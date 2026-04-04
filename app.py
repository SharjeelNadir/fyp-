# frontend_connected/app.py

"""
GuideMe – FastAPI Backend (API-only)

Flow supported:
1) Signup -> Login
2) New user: Resume Upload -> Personality Quiz -> Technical Quiz -> Profile
3) Existing user: Login -> Profile
4) AI Counselor: answers ONLY using user stats

Key Notes:
- Uses cookie-based session (user_id cookie)
- React frontend must send: credentials: "include"
- Database is the single source of truth (career_app.db)
"""

import os
import json
import shutil
import re
from typing import List, Dict
from fastapi import BackgroundTasks
from fastapi import (
    FastAPI,
    Request,
    File,
    UploadFile,
    HTTPException,
    Form,
    Depends,
    Query
)
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from database.db_manager import (
    init_db,
    db_signup,
    db_login,
    db_save_full_assessment,
    db_get_user_stats,
    db_save_resume_skills,
    db_get_latest_resume_skills,
    db_get_user_recommendations,
    db_save_user_recommendations,
    db_delete_generated_questions,
    db_save_generated_questions,
    db_get_generated_questions,
    db_reset_all
)

from utils.parser import SimpleResumeParser
from utils.career_recommender import recommend_careers
from utils.llm_handler import (
    generate_mcqs,
    generate_mcqs_batch,
    generate_personality_questions,
    run_hf_llama,
    enhance_career_recommendations_llm,
    optimize_resume_latex,
    _fallback_questions   # ADD THIS
)

from concurrent.futures import ThreadPoolExecutor, as_completed
UPLOAD_DIR = "uploads"
quiz_generation_running=False
quiz_generation_running_by_user: Dict[int, bool] = {}

# Target number of questions per skill
QUIZ_TARGET_PER_SKILL = 3

# Track quiz generation timing per user (dev/simple in-memory)
quiz_generation_started_at: Dict[int, float] = {}
quiz_generation_finished_at: Dict[int, float] = {}
# ======================================================
#  APP SETUP
# ======================================================

app = FastAPI(title="GuideMe API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB + utilities
init_db()
parser = SimpleResumeParser()

# Store uploads locally
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Always include these baseline CS skills
CORE_SKILLS = [
    "OOP",
    "Data Structures",
    "Algorithms",
    "DBMS",
    "Operating Systems",
    "Computer Networks"
]

# ======================================================
#  HELPERS
# ======================================================

def clean_llm_json(raw_str: str) -> str:
    """
    Tries to extract valid JSON from LLM output by:
    - finding first JSON object/array
    - removing control characters that break JSON parsing
    """
    try:
        match = re.search(r'(\[.*\]|\{.*\})', raw_str, re.DOTALL)
        if match:
            clean = match.group(1)
            clean = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', clean)
            return clean
        return raw_str
    except:
        return raw_str


def get_user_id(request: Request) -> int:
    """
    Cookie-based auth: reads user_id from secure cookie.
    React MUST use credentials: "include"
    """
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not logged in")
    try:
        return int(user_id)
    except:
        raise HTTPException(status_code=401, detail="Invalid session cookie")


def _require_dev_reset_token(request: Request):
    """
    Dev-only guard for destructive endpoints.
    Set env var DEV_RESET_TOKEN and send header: X-Dev-Reset-Token
    """
    expected = os.getenv("DEV_RESET_TOKEN")
    provided = request.headers.get("X-Dev-Reset-Token")
    if not expected or provided != expected:
        raise HTTPException(status_code=403, detail="Forbidden")


def _normalize_q(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


# ======================================================
#  SCHEMAS
# ======================================================

class UserAuth(BaseModel):
    email: str
    password: str


class AssessmentSave(BaseModel):
    total_score: int
    total_questions: int
    personality: Dict[str, int]
    breakdown: List[List]


# ======================================================
#  AUTH ROUTES
# ======================================================

@app.post("/api/signup")
async def api_signup(user: UserAuth):
    success, message = db_signup(user.email, user.password)
    return {"success": success, "message": message}


@app.post("/api/login")
async def api_login(user: UserAuth):
    user_id = db_login(user.email, user.password)
    if not user_id:
        return JSONResponse(
            status_code=401,
            content={"success": False, "message": "Invalid credentials"}
        )

    has_stats = db_get_user_stats(int(user_id)) is not None
    redirect_to = "/profile" if has_stats else "/dashboard"

    response = JSONResponse(content={"success": True, "redirect_to": redirect_to})
    response.set_cookie(
        key="user_id",
        value=str(user_id),
        httponly=True,
        samesite="lax",
        max_age=86400,
    )
    return response


@app.post("/api/logout")
async def api_logout():
    response = JSONResponse(content={"success": True})
    response.delete_cookie("user_id")
    return response


# ======================================================
#  DEV: RESET DB (DESTRUCTIVE)
# ======================================================

@app.post("/api/dev/reset-db")
async def api_dev_reset_db(request: Request):
    """
    Deletes and recreates the SQLite DB (career_app.db).
    Requires header X-Dev-Reset-Token matching env DEV_RESET_TOKEN.
    """
    _require_dev_reset_token(request)
    try:
        db_reset_all()
        return {"success": True, "message": "Database reset successfully"}
    except Exception as e:
        print("❌ DB reset error:", e)
        raise HTTPException(status_code=500, detail="DB reset failed")


# ======================================================
#  RESUME UPLOAD (CLAIMED SKILLS) + GENERATE QUIZ ONCE
# ======================================================
import time
def generate_skill_questions(user_id, skill, TARGET_PER_SKILL, seen):

    print(f"→ Parallel processing {skill}")

    try:

        raw_questions = generate_mcqs(
            skill,
            TARGET_PER_SKILL
        )

    except Exception as e:

        print(f"⚠️ LLM failed for {skill}: {e}")

        raw_questions = _fallback_questions(
            skill,
            TARGET_PER_SKILL
        )

    skill_questions=[]

    for q in raw_questions:

        question_text=q.get("question")

        if not question_text:
            continue

        key=(skill,_normalize_q(question_text))

        if key in seen:
            continue

        seen.add(key)

        q["skill"]=skill

        skill_questions.append(q)


    if len(skill_questions)<TARGET_PER_SKILL:

        missing=TARGET_PER_SKILL-len(skill_questions)

        fallback=_fallback_questions(skill,missing)

        for q in fallback:

            q["skill"]=skill

            skill_questions.append(q)


    skill_questions=skill_questions[:TARGET_PER_SKILL]

    db_save_generated_questions(user_id,skill_questions)

    print(f"✓ {skill} finished")

    return skill_questions
def generate_quiz_background(user_id, final_skills):

    """
    Streaming MCQ generation:
    - Parallel skills
    - Generates 1 question at a time
    - Saves instantly
    - Frontend can show live progress
    """

    global quiz_generation_running

    TARGET_PER_SKILL = QUIZ_TARGET_PER_SKILL

    print("\n⚡ Background MCQ generation started")

    quiz_generation_running = True
    quiz_generation_running_by_user[user_id] = True

    quiz_generation_started_at[user_id] = time.time()
    quiz_generation_finished_at.pop(user_id, None)


    try:

        def process_skill(skill):

            print(f"\n→ Processing {skill}")

            generated = 0

            while generated < TARGET_PER_SKILL:

                try:

                    questions = generate_mcqs(skill,1)

                except Exception as e:

                    print("LLM failed:",skill,e)

                    questions = _fallback_questions(skill,1)


                for q in questions:

                    if not q.get("question"):
                        continue

                    q["skill"]=skill

                    db_save_generated_questions(
                        user_id,
                        [q]
                    )

                    generated += 1

                    print(f"✓ {skill} Q{generated} ready")


            print(f"✅ {skill} finished")


        # Parallel skills
        with ThreadPoolExecutor(max_workers=3) as executor:

            futures=[

                executor.submit(
                    process_skill,
                    skill
                )

                for skill in final_skills

            ]

            for f in as_completed(futures):

                try:
                    f.result()

                except Exception as e:

                    print("Thread failed:",e)


    except Exception as e:

        print("GENERATION ERROR:",e)


    finally:

        quiz_generation_running=False

        quiz_generation_running_by_user[user_id]=False

        quiz_generation_finished_at[user_id]=time.time()

        print("✅ Background MCQ generation finished")
        
@app.post("/api/upload")
async def api_upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    user_id: int = Depends(get_user_id)
):

    """
    Upload resume:
    - Extract skills
    - Start background MCQ generation
    - Return immediately (no waiting)
    """

    global quiz_generation_running

    try:

        start=time.time()

        # ===== SAVE FILE =====

        safe_name=file.filename.replace("/","_").replace("\\","_")

        file_path=os.path.join(UPLOAD_DIR,safe_name)

        with open(file_path,"wb") as buffer:
            shutil.copyfileobj(file.file,buffer)


        # ===== SKILL EXTRACTION =====

        text=parser.extract_text(file_path)

        extracted_skills=parser.extract_skills(text) or []

        final_skills=sorted(list(set(CORE_SKILLS+extracted_skills)))


        print("\n==============================")
        print("📄 Resume uploaded")
        print("Detected skills:",final_skills)
        print(f"Total skills: {len(final_skills)}")
        print("==============================\n")


        # ===== SAVE CLAIMED SKILLS =====

        db_save_resume_skills(
            user_id,
            safe_name,
            final_skills
        )


        # ===== RESET OLD QUESTIONS =====

        db_delete_generated_questions(user_id)


        # ===== MARK GENERATION START =====

        quiz_generation_running=True
        quiz_generation_running_by_user[user_id] = True
        quiz_generation_started_at[user_id] = time.time()
        quiz_generation_finished_at.pop(user_id, None)


        # ===== START BACKGROUND GENERATION =====

        background_tasks.add_task(

            generate_quiz_background,

            user_id,

            final_skills

        )


        end=time.time()

        print("⚡ Quiz generation started in background")
        print(f"⏱ Upload processing time: {round(end-start,2)} sec")


        # ===== RETURN IMMEDIATELY =====

        return {

            "success":True,

            "skills":final_skills,

            "message":"Quiz generation started",

            "total_skills":len(final_skills),

            "generating":True

        }


    except Exception as e:

        print("❌ Resume upload error:",e)

        quiz_generation_running=False

        return JSONResponse(

            status_code=500,

            content={

                "success":False,

                "message":"Resume processing failed"

            }

        )
# ======================================================
#  FETCH QUIZ FROM DB (FRONTEND MUST USE THIS)
# ======================================================

@app.get("/api/quiz")
async def api_get_quiz(user_id: int = Depends(get_user_id)):

    questions=db_get_generated_questions(user_id)
    skills = db_get_latest_resume_skills(user_id) or []
    expected_total = len(skills) * QUIZ_TARGET_PER_SKILL
    generated_total = len(questions)

    started_at = quiz_generation_started_at.get(user_id)
    finished_at = quiz_generation_finished_at.get(user_id)
    now = time.time()
    elapsed_seconds = None
    if started_at:
        elapsed_seconds = round(((finished_at or now) - started_at), 2)

    return {

        "questions":sorted(questions,key=lambda x:x["skill"]),

        "generating":quiz_generation_running_by_user.get(user_id, False),
        "expected_total": expected_total,
        "generated_total": generated_total,
        "skill_count": len(skills),
        "per_skill": QUIZ_TARGET_PER_SKILL,
        "elapsed_seconds": elapsed_seconds

    }
# ======================================================
#  PERSONALITY QUESTIONS
# ======================================================

@app.get("/api/personality-questions")
async def api_personality_questions():
    questions=generate_personality_questions()

    print(f"✅ Generated {len(questions)} personality questions")

    return questions

# ======================================================
# CAREER RECOMMENDATION
# ======================================================

@app.get("/api/clear-careers")

def clear_careers(user_id:int=Depends(get_user_id)):

    import sqlite3

    conn=sqlite3.connect("career_app.db")

    cur=conn.cursor()

    cur.execute(
        "DELETE FROM career_recommendations WHERE user_id=?",
        (user_id,)
    )

    conn.commit()

    conn.close()

    return {"message":"cleared"}


@app.get("/api/recommend-careers")
async def api_recommend_careers(user_id: int = Depends(get_user_id)):

    # ===== LOAD USER STATS =====

    stats = db_get_user_stats(user_id)

    if not stats:
        raise HTTPException(
            status_code=400,
            detail="Complete assessment first."
        )

    # ===== CHECK CACHE =====

    cached = None   # disable cache during testing

    if cached:

        recs = cached.get("recommendations", [])

        if all("improvement_areas" in r for r in recs):

            print("✅ Returning cached career recommendations")

            return {
                "recommendations": recs,
                "cached": True
            }

        else:
            print("♻️ Old cache detected → regenerating")

    # ===== EXTRACT USER DATA =====

    skill_summary = stats.get("skill_summary", {})
    claimed_skills = stats.get("claimed_skills", [])
    personality = stats.get("personality", {})

    # ===== DETERMINISTIC ENGINE =====

    deterministic_recs = recommend_careers(

        skill_summary=skill_summary,

        claimed_skills=claimed_skills,

        personality=personality,

        top_k=3

    )

    # Base recommendations
    final_recs = [

        {
            **r,
            "reason": r.get("reason","Strong skill alignment"),
            "improvement_areas": r.get("improvement_areas",[])
        }

        for r in deterministic_recs

    ]

    # ===== TOKEN SAFE LLM INPUT =====

    lightweight_recs = [

        {
            "title": r["title"],
            "final_score": r["final_score"],
            "technical_fit": r["technical_fit"],
            "personality_fit": r["personality_fit"],
            "claimed_alignment": r["claimed_alignment"]
        }

        for r in deterministic_recs

    ]

    # ===== LLM ENHANCEMENT =====

    llm_output = enhance_career_recommendations_llm(

        claimed_skills = claimed_skills[:10],

        verified_skills = list(skill_summary.keys())[:10],

        personality = personality,

        deterministic_recs = lightweight_recs,

        top_k = 3

    )

    # ===== VALIDATE LLM OUTPUT =====

    if llm_output and isinstance(llm_output.get("recommendations"), list):

        recs = llm_output["recommendations"]

        valid = True

        if len(recs) != 3:

            valid = False

        else:

            for r in recs:

                if not isinstance(r, dict):

                    valid = False
                    break

                # Reason is optional; we can fall back to deterministic explanation

        # ===== MERGE SAFELY =====

        if valid:

            print("🤖 LLM enhancement accepted")

            merged = []

            for i, r in enumerate(recs):

                base = deterministic_recs[i]

                merged.append({

                    # KEEP deterministic scores
                    "career_id": base["career_id"],

                    "title": base["title"],

                    "final_score": base["final_score"],

                    "technical_fit": base["technical_fit"],

                    "personality_fit": base["personality_fit"],

                    "claimed_alignment": base["claimed_alignment"],

                    # Allow LLM only to improve explanation (fallback to deterministic)
                    "reason": r.get("reason", base["reason"]),

                    # Keep roadmap deterministic
                    "improvement_areas":
                    base.get("improvement_areas",[]),

                    "top_skill_contributions":
                    base.get("top_skill_contributions",[])

                })

            final_recs = merged

        else:

            print("⚠️ Invalid LLM output → using deterministic")

    else:

        print("⚠️ LLM failed → using deterministic")

    # ===== SAVE CACHE =====

    result = {

        "recommendations": final_recs

    }

    db_save_user_recommendations(

        user_id,

        result

    )

    print("💾 Career recommendations generated")

    return {

        "recommendations": final_recs,

        "cached": False

    }
# ======================================================
#  OPTIONAL: KEEP THIS ENDPOINT, BUT FRONTEND SHOULD NOT USE IT
# ======================================================

@app.get("/api/generate-mcqs")
async def api_generate_mcqs(skill: str = Query(..., min_length=1)):
    """
    Debug endpoint only.
    Frontend should NOT call this during quiz.
    """
    print(f"\n🧠 [MCQ REQUEST] Generating 3 questions for skill: {skill}")

    questions = []
    for i in range(1, 4):
        raw_output = generate_mcqs(skill,1)
        q = None

        if isinstance(raw_output, str):
            try:
                cleaned = clean_llm_json(raw_output)
                parsed = json.loads(cleaned)
                if isinstance(parsed, list) and parsed:
                    q = parsed[0]
                elif isinstance(parsed, dict):
                    q = parsed
            except Exception as e:
                print(f"❌ JSON parse failed (attempt {i}) for {skill}: {e}")

        elif isinstance(raw_output, dict):
            q = raw_output

        if not q:
            continue

        q["skill"] = skill
        questions.append(q)

    return questions


# ======================================================
#  SAVE FINAL RESULTS
# ======================================================

@app.post("/api/save-results")
async def api_save_results(data: AssessmentSave, user_id: int = Depends(get_user_id)):
    success = db_save_full_assessment(
        user_id=user_id,
        total_score=data.total_score,
        total_questions=data.total_questions,
        personality_dict=data.personality,
        skill_breakdown=data.breakdown
    )
    return {"success": success}


# ======================================================
#  USER STATS (PROFILE PAGE)
# ======================================================

@app.get("/api/user-stats")
async def api_user_stats(user_id: int = Depends(get_user_id)):
    stats = db_get_user_stats(user_id)
    return stats


# ======================================================
#  RESUME LATEX OPTIMIZER
# ======================================================

@app.post("/api/optimize-resume-latex")
async def api_optimize_resume_latex(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    job_title: str = Form(...),
    job_description: str = Form(...),
    user_id: int = Depends(get_user_id)
):
    """
    Upload a resume + job description and return a LaTeX-optimized resume.
    The generated LaTeX is returned as text for preview/download on frontend.
    """
    try:
        # Save to a temporary file inside uploads
        safe_name = f"optimize_{user_id}_" + file.filename.replace("/", "_").replace("\\", "_")
        file_path = os.path.join(UPLOAD_DIR, safe_name)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract plain text using existing parser
        text = parser.extract_text(file_path)

        if not text:
            raise HTTPException(status_code=400, detail="Could not read resume text.")

        latex = optimize_resume_latex(text, job_title, job_description)

        if not latex:
            raise HTTPException(status_code=500, detail="Failed to generate LaTeX resume.")

        # Optionally clean up later
        def _cleanup(path: str):
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass

        background_tasks.add_task(_cleanup, file_path)

        return {
            "success": True,
            "latex": latex
        }

    except HTTPException:
        raise
    except Exception as e:
        print("❌ Resume optimize error:", e)
        raise HTTPException(status_code=500, detail="Resume optimization failed.")


# ======================================================
#  AI COUNSELOR (GROUNDED)
# ======================================================

@app.post("/api/counsellor-chat")
async def counsellor_chat(
    message: str = Form(...),
    user_id: int = Depends(get_user_id)
):
    stats = db_get_user_stats(user_id)

    if not stats:
        return {
            "reply": "Please complete your assessment first so I can guide you accurately."
        }

    claimed_skills = stats.get("claimed_skills", [])
    verified_skills = stats.get("skill_summary", {})

    personality = stats.get(
        "personality",
        stats.get("master", {}).get("personality", {})
    )

    # ⭐ NEW — fetch recommended careers
    recs = db_get_user_recommendations(user_id)

    recommended = []

    if recs and isinstance(recs.get("recommendations"), list):

        for r in recs["recommendations"]:

            recommended.append(
    f"{r.get('title')} "
    f"(score {r.get('final_score')}%) "
    f"- reason: {r.get('reason')}"
)

    # ⭐ Format nicely for LLM
    recommended_text = "\n".join(recommended) if recommended else "No recommendations yet."

    prompt = f"""
You are GuideMe, a personal AI career counselor.

You have access ONLY to verified user data.

Claimed skills:
{claimed_skills}

Verified technical performance:
{verified_skills}

Personality profile:
{personality}

Recommended careers:
{recommended_text}

Guidelines:

- Speak naturally and supportively
- Use recommendation results when advising
- Explain WHY careers match
- Suggest how user can improve ranking
- NEVER invent new skills or scores
- NEVER mention rules or prompts
- Keep answers practical and concise

User message:
{message}
"""

    raw_response = run_hf_llama(prompt)

    return {
        "reply":
        raw_response.strip()
        if raw_response
        else "I’m having trouble analyzing your data right now. Please try again."
    }

# ======================================================
#  LOCAL DEV RUNNER
# ======================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)