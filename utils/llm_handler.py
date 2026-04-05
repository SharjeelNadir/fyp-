# frontend_connect/llm_handler.py
import json
import re
import time
import random
import requests
LLM_PROVIDER = "lmstudio"
LMSTUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"
MODEL_NAME = "meta-llama-3.1-8b-instruct-hf"


from database.db_manager import (
    db_get_bank_questions,
    db_save_question_bank
)
# ======================================================
# HARD QUESTION BANK
# ======================================================

HARD_QUESTION_BANK = {
    "OOP": [
        {
            "question": "In C++ multiple inheritance, which statement about object layout is correct?",
            "options": {
                "A": "Only one vptr exists",
                "B": "Each polymorphic base typically has its own vptr",
                "C": "No vptr if overridden",
                "D": "Virtual inheritance is automatic"
            },
            "answer": "B"
        }
    ]
}

# ======================================================
# CORE LLM CALL
# ======================================================

def run_hf_llama(prompt: str, max_tokens: int = 1400) -> str:
    """
    max_tokens bumped to 1400 by default.
    Callers can override (e.g. counsellor chat needs less).
    """
    try:
        start = time.time()

        print("\n================ LLM REQUEST ================")
        print(prompt[:600])
        print("============================================")
        
        # Allow LM Studio to handle its own concurrency; no global lock
        response = requests.post(
            LMSTUDIO_URL,
            json={
                "model": MODEL_NAME,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "top_p": 0.9,
                "presence_penalty":0,
                "frequency_penalty":0,
                "max_tokens": max_tokens,
                "stream": False
            },
            timeout=45                   # batch calls need more time
        )

        response.raise_for_status()
        data = response.json()
        result = data["choices"][0]["message"]["content"].strip()

        elapsed = round(time.time() - start, 2)
        print("\n================ LLM RESPONSE ================")
        print(result[:600])
        print(f"⏱ {elapsed}s | prompt={len(prompt)} chars")
        print("============================================")

        return result

    except requests.exceptions.Timeout:
        print("⚠️ LLM Timeout")
    except requests.exceptions.ConnectionError:
        print("⚠️ LM Studio not running")
    except Exception as e:
        print("⚠️ LM Studio Error:", e)

    return ""

# ======================================================
# SAFE JSON EXTRACTION
# ======================================================

def extract_json(text):

    if not text:
        return None

    try:

        text=text.replace("```json","")
        text=text.replace("```","")
        text=text.strip()

        # find first json start
        match=re.search(r'[\{\[]',text)

        if not match:
            return None

        cleaned=text[match.start():]

        decoder=json.JSONDecoder()

        try:
            obj,_=decoder.raw_decode(cleaned)

        except json.JSONDecodeError:

            cleaned=_escape_control_chars_in_strings(cleaned)

            obj,_=decoder.raw_decode(cleaned)

        return obj

    except Exception as e:

        print("JSON parse failed:",e)

    return None


# ======================================================
# BATCH MCQ GENERATION  ← KEY CHANGE
# ======================================================

def generate_mcqs_batch(skills:list,count_per_skill:int=3):

    results={}

    # ===== STEP 1 : TRY BANK FIRST =====

    missing_skills=[]

    for skill in skills:

        bank=db_get_bank_questions(skill,count_per_skill)

        if len(bank)>=count_per_skill:

            results[skill]=bank

            print("✓ bank used:",skill)

        else:

            results[skill]=bank
            missing_skills.append(skill)


    # ===== STEP 2 : LLM GENERATION =====

    if missing_skills:

        prompt=f"""
Generate {count_per_skill} HARD technical MCQs for EACH skill:

{missing_skills}

IMPORTANT:

Skill refers ONLY to programming technology.
NOT animals.
NOT general meaning.

Example:
Pandas = Python data analysis library
NOT panda animal.

Rules:

Questions must be UNIQUE.
No repeated concepts.
No beginner questions.
Focus on:

• debugging
• edge cases
• code output
• performance
• real production problems

Return ONLY JSON:

{{
"<skill>":[
{{"question":"...","options":{{"A":"...","B":"...","C":"...","D":"..."}}, "answer":"A"}}
]
}}
"""
        raw=run_hf_llama(prompt,1400)

        js=extract_json(raw)

        if isinstance(js,dict):

            new_bank=[]

            for skill in missing_skills:

                skill_questions=js.get(skill,[])

                valid=_validate_questions(
                    skill_questions,
                    skill,
                    count_per_skill
                )

                results[skill]+=valid

                new_bank+=valid


            # save new questions globally
            if new_bank:

                db_save_question_bank(new_bank)


    # ===== STEP 3 : GUARANTEE COUNTS =====

    for skill in skills:

        while len(results[skill])<count_per_skill:

            extra=generate_mcqs(skill,1)[0]

            results[skill].append(extra)

            db_save_question_bank([extra])


    return results

def _validate_questions(questions: list, skill: str, count: int) -> list:
    """Validate and normalize a list of raw MCQ dicts."""

    valid=[]
    seen=set()

    for q in questions:

        if not (
            isinstance(q, dict)
            and "question" in q
            and "options" in q
            and "answer" in q
            and isinstance(q["options"], dict)
            and set(q["options"].keys()) == {"A","B","C","D"}
            and q["answer"] in {"A","B","C","D"}
        ):
            continue


        # ===== NORMALIZE QUESTION TEXT =====

        normalized=re.sub(
            r'\s+',
            ' ',
            q["question"].strip().lower()
        )


        # ===== DUPLICATE FILTER =====

        if normalized in seen:
            continue


        seen.add(normalized)


        valid.append({

            "question":q["question"].strip(),

            "options":q["options"],

            "answer":q["answer"],

            "skill":skill

        })


        if len(valid)==count:
            break


    return valid

def _escape_control_chars_in_strings(text: str) -> str:
    """
    Escape raw control chars that appear inside JSON strings.
    Keeps structure outside strings unchanged.
    """
    out = []
    in_string = False
    escaped = False

    for ch in text:
        if escaped:
            out.append(ch)
            escaped = False
            continue

        if ch == "\\":
            out.append(ch)
            escaped = True
            continue

        if ch == '"':
            out.append(ch)
            in_string = not in_string
            continue

        if in_string and ch == "\n":
            out.append("\\n")
            continue
        if in_string and ch == "\r":
            out.append("\\r")
            continue
        if in_string and ch == "\t":
            out.append("\\t")
            continue

        out.append(ch)

    return "".join(out)

def _fallback_questions(skill: str, count: int) -> list:
    return [
        {
            "question": f"In advanced usage of {skill}, which statement is most accurate?",
            "options": {
                "A": "Depends on implementation",
                "B": "Depends on runtime",
                "C": "Depends on edge cases",
                "D": "All of the above"
            },
            "answer": "D",
            "skill": skill
        }
        for _ in range(count)
    ]


def repair_mcq(text):

    try:

        q_match = re.search(r'"question"\s*:\s*"([^"]+)"',text)

        a = re.search(r'"A"\s*:\s*"([^"]+)"',text)
        b = re.search(r'"B"\s*:\s*"([^"]+)"',text)
        c = re.search(r'"C"\s*:\s*"([^"]+)"',text)
        d = re.search(r'"D"\s*:\s*"([^"]+)"',text)

        ans = re.search(r'"answer"\s*:\s*"([ABCD])"',text)

        if not (q_match and a and b and c and d and ans):
            return None


        return {

            "question": q_match.group(1),

            "options":{

                "A":a.group(1),
                "B":b.group(1),
                "C":c.group(1),
                "D":d.group(1)

            },

            "answer":ans.group(1)

        }

    except:

        return None


def generate_mcqs(skill: str, count: int = 1):

    """
    Guaranteed MCQ generation:
    - Never loses questions
    - Repairs bad JSON
    - Removes duplicates
    - Forces programming context
    """

    if skill in HARD_QUESTION_BANK:

        q=random.choice(HARD_QUESTION_BANK[skill]).copy()

        q["skill"]=skill

        return [q]


    # ===== SKILL CONTEXT FIX (prevents Pandas animal issue) =====

    skill_context = {

        "Pandas":"Pandas Python data analysis library",
        "Numpy":"NumPy Python numerical computing library",
        "Flask":"Flask Python backend web framework",
        "Javascript":"JavaScript programming language",
        "Java":"Java programming language",
        "MongoDB":"MongoDB NoSQL database",
        "DBMS":"Database Management Systems",
        "OOP":"Object Oriented Programming",
        "Operating Systems":"Computer Operating Systems"
    }

    skill_desc = skill_context.get(skill, skill)


    # ===== IMPROVED PROMPT =====

    prompt = f"""
Generate ONE HARD technical MCQ for programming skill:

{skill_desc}

IMPORTANT:

Skill refers ONLY to software technology.
NOT animals.
NOT general meaning.

Example:

Pandas means Python data analysis library.
NOT panda animal.

Difficulty:

Final year Computer Science level.

Question style:

• Code output prediction
• Debugging scenarios
• Time/space complexity
• Framework internals
• Edge cases
• Production issues

Rules:

Question must be UNIQUE.
Avoid textbook questions.
Avoid definitions.

Return ONLY JSON:

{{
"question":"text",
"options":{{"A":"opt","B":"opt","C":"opt","D":"opt"}},
"answer":"A"
}}

Rules:

4 options only
Answer must be A/B/C/D
No explanations
JSON only
"""


    seen=set()

    for attempt in range(3):

        try:

            raw = run_hf_llama(
                prompt,
                max_tokens=400
            )

            js = extract_json(raw)
            print("LLM parsed JSON:",js)

            # ===== JSON FAILED → TRY REPAIR =====

            if not js:

                repaired = repair_mcq(raw)

                if repaired:

                    key=re.sub(r'\s+',' ',repaired["question"].lower())

                    if key not in seen:

                        seen.add(key)

                        repaired["skill"]=skill

                        return [repaired]

                continue


            valid = _validate_questions(

                [js] if isinstance(js,dict) else js,

                skill,

                1
            )


            if valid:

                key=re.sub(
                    r'\s+',
                    ' ',
                    valid[0]["question"].lower()
                )

                if key not in seen:

                    seen.add(key)

                    return valid


            # validation failed → still try repair

            repaired = repair_mcq(raw)

            if repaired:

                key=re.sub(
                    r'\s+',
                    ' ',
                    repaired["question"].lower()
                )

                if key not in seen:

                    seen.add(key)

                    repaired["skill"]=skill

                    return [repaired]


        except Exception as e:

            print(skill,"error:",e)


    # ===== FINAL GUARANTEE =====

    return _fallback_questions(skill,1)




# ======================================================
# PERSONALITY QUESTIONS
# ======================================================

def generate_personality_questions():
    prompt = "Return a JSON array of exactly 5 OCEAN personality statements. Double quotes only. Return only JSON.\n[{\"trait\":\"Openness\",\"question\":\"...\"}]"

    raw = run_hf_llama(prompt, max_tokens=400)
    js = extract_json(raw)

    if isinstance(js, list) and len(js) == 5:
        return js

    return [
        {"trait": "Openness",          "question": "I have a vivid imagination."},
        {"trait": "Conscientiousness", "question": "I am always prepared."},
        {"trait": "Extraversion",      "question": "I feel comfortable around people."},
        {"trait": "Agreeableness",     "question": "I am interested in people."},
        {"trait": "Neuroticism",       "question": "I get upset easily."}
    ]

# ======================================================
# LLM CAREER ENHANCEMENT
# ======================================================

def validate_llm_recommendations(output, top_k=3):
    # Handle both {"recommendations": [...]} and bare [...]
    if isinstance(output, list):
        recs = output
    elif isinstance(output, dict):
        recs = output.get("recommendations")
        if not isinstance(recs, list):
            return None
    else:
        return None

    fixed = []
    for i, r in enumerate(recs):
        if not isinstance(r, dict):
            continue
        title = r.get("title")
        if not title:
            continue
        try:
            score = float(r.get("final_score", 0))
        except:
            score = 0
        score = max(0, min(score, 100))
        fixed.append({
            "career_id": r.get("career_id", f"llm_{i}"),
            "title": title,
            "final_score": score,
            "technical_fit": float(r.get("technical_fit", 0)),
            "personality_fit": float(r.get("personality_fit", 0)),
            "claimed_alignment": float(r.get("claimed_alignment", 0)),
            "reason": r.get("reason", "Recommended based on profile")
        })

    if len(fixed) < top_k:
        return None

    return fixed[:top_k]


def enhance_career_recommendations_llm(
    claimed_skills,
    verified_skills,
    personality,
    deterministic_recs,
    top_k=3
):

    print("\n===== TRYING LLM CAREER ENHANCEMENT =====")

    # Format verified skills nicely for the prompt
    verified_str = ", ".join([f"{k} ({v}%)" for k, v in verified_skills.items()]) if isinstance(verified_skills, dict) else str(verified_skills)

    prompt = f"""You are a career counselor. Return exactly {top_k} career recommendations as a JSON array. No markdown.

USER PROFILE:
- Verified skills with scores: {verified_str}
- Claimed skills: {claimed_skills}

CAREERS TO RECOMMEND (use these scores exactly):
{deterministic_recs}

For each career write a 2-sentence reason that:
- Mentions 1-2 SPECIFIC skills the user actually has that are relevant
- Mentions 1 key skill they are missing
- Never uses generic phrases like "high technical fit" or "strong personality alignment"

Example of a GOOD reason:
"Your Flask and Python experience make you a strong candidate for backend roles. Strengthening OOP and DBMS would make you job-ready faster."

Example of a BAD reason (do not do this):
"High technical fit and strong personality alignment make this a good match."

Return ONLY this format:
[
  {{"career_id":"...","title":"...","final_score":70,"technical_fit":65,"personality_fit":75,"claimed_alignment":80,"reason":"specific 2-sentence reason here"}}
]

No other text.
"""

    
    
    
    
    raw = run_hf_llama(prompt, max_tokens=1400)
    print("\n===== RAW LLM CAREER OUTPUT =====")
    print(raw)
    print("=================================\n")

    if not raw:

        print("❌ LLM returned empty response")

        return None


    js = extract_json(raw)
    print("\n===== PARSED JSON =====")
    print(js)
    print("======================\n")


    if not js:

        print("❌ JSON extraction failed")

        print("Raw output:",raw[:300])

        return None


    validated = validate_llm_recommendations(js, top_k)


    if validated and len(validated)>0:

        print("✅ LLM recommendations valid")

        return {"recommendations": validated}


    print("❌ LLM validation failed")

    return None

# ======================================================
# RESUME → JOB LATEX OPTIMIZER
# ======================================================

def optimize_resume_latex(resume_text: str, job_title: str, job_description: str) -> str:
    """
    Ask the LLM to rewrite the resume as a job-tailored LaTeX resume.
    Returns raw LaTeX code (no markdown fences).
    """
    prompt = f"""
You are an expert technical resume writer and LaTeX expert.

TASK:
- Rewrite the candidate's resume so it is strongly aligned to the target role
- Keep all content truthful (do NOT invent experience or skills)
- Emphasize impact, metrics, and keywords from the job description
- Use a clean, ATS-friendly one-column LaTeX resume layout

JOB TITLE:
{job_title}

JOB DESCRIPTION:
{job_description}

CURRENT RESUME (PLAIN TEXT):
{resume_text}

Return ONLY valid LaTeX code for a complete resume document.
Do NOT include markdown fences, comments, or explanations.
Just the LaTeX.
"""

    latex = run_hf_llama(prompt, max_tokens=1600) or ""
    return latex.strip()