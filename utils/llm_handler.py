# frontend/src/utils/llm_handler.py
import json
import re
import time
import random
import requests


# ======================================================
# LOCAL LLAMA CONFIG
# ======================================================

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3:8b"


# ======================================================
# HARD QUESTION BANK (Stable for Demo)
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
# LOCAL LLM CALL (REPLACES HF)
# ======================================================

def run_hf_llama(prompt: str) -> str:

    try:

        response = requests.post(

            OLLAMA_URL,

            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,

                "options": {
                    "temperature":0.7,
                    "top_p":0.9,
                    "num_predict":900
                }
            },

            timeout=300
        )

        response.raise_for_status()

        data=response.json()

        return data.get("response","").strip()

    except Exception as e:

        print("⚠️ Local LLM Error:",e)

        return ""


# ======================================================
# SAFE JSON EXTRACTION
# ======================================================

def extract_json(text: str):

    if not text:
        return None

    match=re.search(r"\[\s*\{.*?\}\s*\]",text,re.DOTALL)

    if not match:
        match=re.search(r"\{.*?\}",text,re.DOTALL)

    if not match:
        return None

    cleaned=match.group(0)

    if "'" in cleaned and '"' not in cleaned:
        cleaned=cleaned.replace("'","\"")

    try:
        return json.loads(cleaned)

    except:
        return None


# ======================================================
# MCQ GENERATION
# ======================================================

def generate_mcq(skill:str):

    if skill in HARD_QUESTION_BANK:
        return random.choice(HARD_QUESTION_BANK[skill])


    prompt=f"""
Generate ONE difficult MCQ for skill "{skill}".

Rules:
- 4 options A B C D
- Only one correct answer
- No explanation
- Return ONLY JSON ARRAY
- Use double quotes

Format:

[
 {{
   "question":"text",
   "options":{{
     "A":"opt",
     "B":"opt",
     "C":"opt",
     "D":"opt"
   }},
   "answer":"A"
 }}
]
"""


    for _ in range(3):

        raw=run_hf_llama(prompt)

        js=extract_json(raw)

        if not js:
            continue


        if isinstance(js,list) and len(js)>0:
            q=js[0]

        elif isinstance(js,dict):
            q=js

        else:
            continue


        if (

            isinstance(q,dict)

            and "question" in q
            and "options" in q
            and "answer" in q

            and isinstance(q["options"],dict)

            and set(q["options"].keys())=={"A","B","C","D"}

            and q["answer"] in {"A","B","C","D"}

        ):

            return q


        time.sleep(0.5)


    return {

        "question":f"In advanced usage of {skill}, which statement is most accurate?",

        "options":{

            "A":"It depends on implementation details.",

            "B":"It depends on runtime behavior.",

            "C":"It depends on edge cases.",

            "D":"All of the above."

        },

        "answer":"D"

    }


# ======================================================
# PERSONALITY QUESTIONS
# ======================================================

def generate_personality_questions():

    prompt="""
Return a JSON ARRAY of exactly 5 OCEAN personality statements.
Use double quotes only.
Return only JSON.
"""

    raw=run_hf_llama(prompt)

    js=extract_json(raw)

    if isinstance(js,list) and len(js)==5:
        return js


    return [

        {"trait":"Openness","question":"I have a vivid imagination."},

        {"trait":"Conscientiousness","question":"I am always prepared."},

        {"trait":"Extraversion","question":"I feel comfortable around people."},

        {"trait":"Agreeableness","question":"I am interested in people."},

        {"trait":"Neuroticism","question":"I get upset easily."}

    ]


# ======================================================
# VALIDATION
# ======================================================

def validate_llm_recommendations(output,top_k=3):

    if not isinstance(output,dict):
        return None

    recs=output.get("recommendations")

    if not isinstance(recs,list) or len(recs)!=top_k:
        return None


    required={

        "career_id",
        "title",
        "final_score",
        "technical_fit",
        "personality_fit",
        "claimed_alignment",
        "reason"

    }


    for r in recs:

        if not isinstance(r,dict):
            return None

        if not required.issubset(r.keys()):
            return None

        if not isinstance(r["final_score"],(int,float)):
            return None

        if not (0<=float(r["final_score"])<=100):
            return None


    return recs


# ======================================================
# LLM CAREER ENHANCEMENT
# ======================================================

def enhance_career_recommendations_llm(

    claimed_skills,
    verified_skills,
    personality,
    deterministic_recs,
    top_k=3

):

    prompt=f"""
Return exactly {top_k} career recommendations in STRICT JSON.

CLAIMED_SKILLS: {claimed_skills}
VERIFIED_SKILLS: {verified_skills}
PERSONALITY: {personality}
DETERMINISTIC: {deterministic_recs}

Format:

{{
 "recommendations":[
   {{
     "career_id":"example",
     "title":"Example",
     "final_score":70,
     "technical_fit":65,
     "personality_fit":75,
     "claimed_alignment":80,
     "reason":"short reason"
   }}
 ]
}}
"""

    raw=run_hf_llama(prompt)

    js=extract_json(raw)

    if not js:
        return None


    validated=validate_llm_recommendations(js,top_k)

    if validated:
        return {"recommendations":validated}


    return None