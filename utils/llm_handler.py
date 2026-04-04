# frontend_connect/llm_handler.py
import json
import re
import time
import random
import requests
LLM_PROVIDER = "lmstudio"
LMSTUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"
MODEL_NAME = "meta-llama-3.1-8b-instruct-hf"

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

        # remove markdown junk
        text=text.replace("```json","")
        text=text.replace("```","")
        # Parse the first JSON value (object OR array) even if extra text exists.
        # This fixes cases where the LLM outputs JSON + trailing tokens.
        start_candidates = [i for i in [text.find("{"), text.find("[")] if i != -1]
        if not start_candidates:
            return None

        start = min(start_candidates)
        cleaned = text[start:]

        decoder = json.JSONDecoder()
        try:
            obj, _idx = decoder.raw_decode(cleaned)
        except json.JSONDecodeError:
            # Common LLM issue: raw newlines/tabs inside quoted strings
            cleaned = _escape_control_chars_in_strings(cleaned)
            obj, _idx = decoder.raw_decode(cleaned)
        return obj

    except Exception as e:

        print("JSON parse failed:",e)

    return None



# ======================================================
# BATCH MCQ GENERATION  ← KEY CHANGE
# ======================================================

def generate_mcqs_batch(skills: list, count_per_skill: int = 3) -> dict:
    """
    ONE LLM call for ALL skills.
    Returns dict: { skill_name: [questions] }
    Falls back to empty dict on failure.
    """
    # Skills already covered by hard bank — skip from LLM call
    llm_skills = [s for s in skills if s not in HARD_QUESTION_BANK]

    if not llm_skills:
        return {}

    # Compact prompt — fewer tokens, strict schema
    prompt = f"""
Generate {count_per_skill} VERY HARD MCQs for EACH skill:

{llm_skills}

These are COMPUTER SCIENCE SKILLS.

Requirements:

• Advanced questions only
• Code tracing
• Debugging
• Complexity
• Framework behavior
• Performance issues

At least one code question per skill. Put code inside the question text using triple backticks.

Return ONLY JSON object:

{{
"<skill>":[
  {{"question":"...","options":{{"A":"...","B":"...","C":"...","D":"..."}}, "answer":"A"}},
  ...
]
}}

No text.
No markdown.
JSON only.
"""
    raw = run_hf_llama(prompt, max_tokens=1400)
    js = extract_json(raw)
    

    if not isinstance(js, dict):
        print("⚠️ Batch generation failed — will fallback per-skill")
        return {}

    return js


def _validate_questions(questions: list, skill: str, count: int) -> list:
    """Validate and normalize a list of raw MCQ dicts."""
    valid = []
    for q in questions:
        if (
            isinstance(q, dict)
            and "question" in q
            and "options" in q
            and "answer" in q
            and isinstance(q["options"], dict)
            and set(q["options"].keys()) == {"A", "B", "C", "D"}
            and q["answer"] in {"A", "B", "C", "D"}
        ):
            valid.append({
                "question": q["question"].strip(),
                "options": q["options"],
                "answer": q["answer"],
                "skill": skill
            })
        if len(valid) == count:
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
    - Always returns count
    """

    if skill in HARD_QUESTION_BANK:

        return [random.choice(HARD_QUESTION_BANK[skill])]


    prompt = f"""
Generate ONE HARD MCQ for skill:

{skill}

Return ONLY JSON:

{{
"question":"text",
"options":{{"A":"opt","B":"opt","C":"opt","D":"opt"}},
"answer":"A"
}}

Rules:
4 options only
Answer A/B/C/D
No explanation
JSON only
"""


    for attempt in range(3):

        try:

            raw = run_hf_llama(
                prompt,
                max_tokens=400
            )

            js = extract_json(raw)

            # ===== JSON failed → try repair =====

            if not js:

                repaired = repair_mcq(raw)

                if repaired:
                    return [repaired]

                continue


            valid = _validate_questions(
                [js] if isinstance(js,dict) else js,
                skill,
                1
            )

            if valid:

                return valid


            # validation failed → still try repair
            repaired = repair_mcq(raw)

            if repaired:
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
    if not isinstance(output, dict):
        return None

    recs = output.get("recommendations")
    if not isinstance(recs, list) or len(recs) != top_k:
        return None

    # reason is optional (backend can fall back to deterministic reason)
    required = {"career_id", "title", "final_score", "technical_fit",
                "personality_fit", "claimed_alignment"}

    for r in recs:
        if not isinstance(r, dict) or not required.issubset(r.keys()):
            return None
        if not isinstance(r["final_score"], (int, float)):
            return None
        if not (0 <= float(r["final_score"]) <= 100):
            return None

    return recs


def enhance_career_recommendations_llm(
    claimed_skills, verified_skills, personality, deterministic_recs, top_k=3
):
    # Compact prompt
    prompt = f"""Return exactly {top_k} career recommendations as JSON. No markdown.

CLAIMED: {claimed_skills}
VERIFIED: {verified_skills}
PERSONALITY: {personality}
DETERMINISTIC: {deterministic_recs}

Return ONLY:
{{"recommendations":[
  {{"career_id":"...","title":"...","final_score":70,"technical_fit":65,"personality_fit":75,"claimed_alignment":80,"reason":"1-2 sentences"}}
]}}

No other text.
"""

    raw = run_hf_llama(prompt, max_tokens=1400)
    js = extract_json(raw)

    if not js:
        return None

    validated = validate_llm_recommendations(js, top_k)
    if validated:
        return {"recommendations": validated}

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