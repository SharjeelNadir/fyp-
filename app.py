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
    db_get_user_recommendations,
    db_save_user_recommendations,
    db_delete_generated_questions,
    db_save_generated_questions,
    db_get_generated_questions
)

from utils.parser import SimpleResumeParser
from utils.career_recommender import recommend_careers
from utils.llm_handler import (
    generate_mcq,
    generate_personality_questions,
    run_hf_llama,
    enhance_career_recommendations_llm
)

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
#  RESUME UPLOAD (CLAIMED SKILLS) + GENERATE QUIZ ONCE
# ======================================================

@app.post("/api/upload")
async def api_upload_resume(
    file: UploadFile = File(...),
    user_id: int = Depends(get_user_id)
):
    """
    Upload resume:
    - Extract skills
    - Generate MCQs (3 per skill) with retry + dedupe
    - Store questions in DB
    """
    try:
        safe_name = file.filename.replace("/", "_").replace("\\", "_")
        file_path = os.path.join(UPLOAD_DIR, safe_name)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract skills
        text = parser.extract_text(file_path)
        extracted_skills = parser.extract_skills(text) or []
        final_skills = sorted(list(set(CORE_SKILLS + extracted_skills)))

        # Save resume skills
        db_save_resume_skills(user_id, safe_name, final_skills)

        print("\n📄 Resume uploaded. Generating MCQs...")

        # Always regenerate on upload (fresh quiz)
        db_delete_generated_questions(user_id)

        TARGET_PER_SKILL = 3
        MAX_ATTEMPTS = 12

        all_questions: List[Dict] = []
        seen = set()

        for skill in final_skills:
            collected = 0
            tries = 0

            while collected < TARGET_PER_SKILL and tries < MAX_ATTEMPTS:
                tries += 1

                raw = generate_mcq(skill)
                q = None

                if isinstance(raw, dict):
                    q = raw
                elif isinstance(raw, str):
                    try:
                        parsed = json.loads(clean_llm_json(raw))
                        if isinstance(parsed, list) and parsed:
                            q = parsed[0]
                        elif isinstance(parsed, dict):
                            q = parsed
                    except:
                        q = None

                if not q:
                    continue

                question_text = q.get("question")
                options = q.get("options")
                answer = q.get("answer")

                if not question_text or options is None or not answer:
                    continue

                key = (skill, _normalize_q(question_text))
                if key in seen:
                    continue

                seen.add(key)
                q["skill"] = skill
                all_questions.append(q)
                collected += 1

            if collected < TARGET_PER_SKILL:
                print(f"⚠️ Only generated {collected}/{TARGET_PER_SKILL} for {skill}")

        db_save_generated_questions(user_id, all_questions)

        print(f"\n✅ Stored {len(all_questions)} questions in database.")
        print("=" * 60)

        return {
            "success": True,
            "skills": final_skills,
            "total_questions_generated": len(all_questions)
        }

    except Exception as e:
        print("❌ Resume upload error:", e)
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": "Resume processing failed"}
        )


# ======================================================
#  FETCH QUIZ FROM DB (FRONTEND MUST USE THIS)
# ======================================================

@app.get("/api/quiz")
async def api_get_quiz(user_id: int = Depends(get_user_id)):

    questions = db_get_generated_questions(user_id)

    return questions

# ======================================================
#  PERSONALITY QUESTIONS
# ======================================================

@app.get("/api/personality-questions")
async def api_personality_questions():
    questions = generate_personality_questions()
    print(f"✅ Generated {len(questions)} personality questions")
    return questions


# ======================================================
# CAREER RECOMMENDATION
# ======================================================

@app.get("/api/recommend-careers")
async def api_recommend_careers(user_id: int = Depends(get_user_id)):

    cached = db_get_user_recommendations(user_id)
    if cached:
        print("✅ Returning cached career recommendations")
        return {"recommendations": cached.get("recommendations", []), "cached": True}

    stats = db_get_user_stats(user_id)
    if not stats:
        raise HTTPException(status_code=400, detail="Complete assessment first.")

    skill_summary = stats.get("skill_summary", {})
    claimed_skills = stats.get("claimed_skills", [])
    personality = stats.get("personality", {})

    deterministic_recs = recommend_careers(
        skill_summary=skill_summary,
        claimed_skills=claimed_skills,
        personality=personality,
        top_k=5
    )

    final_recs = deterministic_recs[:3]

    llm_output = enhance_career_recommendations_llm(
        claimed_skills=claimed_skills,
        verified_skills=skill_summary,
        personality=personality,
        deterministic_recs=deterministic_recs,
        top_k=3
    )

    if llm_output and isinstance(llm_output.get("recommendations"), list):
        recs = llm_output["recommendations"]
        required_keys = {
            "career_id", "title", "final_score",
            "technical_fit", "personality_fit",
            "claimed_alignment", "reason"
        }

        valid = True
        if len(recs) != 3:
            valid = False
        else:
            for r in recs:
                if not isinstance(r, dict) or not required_keys.issubset(r.keys()):
                    valid = False
                    break
                for field in ["final_score", "technical_fit", "personality_fit", "claimed_alignment"]:
                    if not isinstance(r[field], (int, float)) or not (0 <= float(r[field]) <= 100):
                        valid = False
                        break

        if valid:
            print("🤖 LLM enhancement accepted")
            final_recs = recs
        else:
            print("⚠️ LLM output invalid → using deterministic fallback")
    else:
        print("⚠️ LLM returned nothing → using deterministic fallback")

    result = {"recommendations": final_recs}
    db_save_user_recommendations(user_id, result)

    print("💾 Career recommendations generated & cached")

    return {"recommendations": final_recs, "cached": False}


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
        raw_output = generate_mcq(skill)
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