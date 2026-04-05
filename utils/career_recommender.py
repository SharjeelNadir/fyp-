from typing import Dict, Any, List, Tuple
from utils.career_profiles import CAREER_PROFILES
DEBUG=True
# ==========================================
# MODEL CONFIGURATION
# ==========================================

DEFAULT_WEIGHTS={

    "technical":0.65,
    "personality":0.25,
    "claimed":0.10

}

READINESS_THRESHOLD=0.20


# Skill synonym normalization improves matching accuracy
SKILL_SYNONYMS={

"MongoDB":"DBMS",
"MySQL":"DBMS",
"PostgreSQL":"DBMS",

"Pandas":"Python",
"Numpy":"Python",
"Pytorch":"Python",
"Tensorflow":"Python",

"Javascript":"JavaScript",
"Node":"JavaScript",

}


# ==========================================
# HELPERS
# ==========================================

def _clamp(v,lo,hi):

    return max(lo,min(hi,v))

def debug_print(*args):

    if DEBUG:

        print(*args)
# ==========================================
# SKILL NORMALIZATION
# ==========================================

def normalize_user_skills(skill_summary):

    if not skill_summary:
        return {}

    normalized={}

    for skill,data in skill_summary.items():

        key=SKILL_SYNONYMS.get(skill,skill)

        value=data.get("accuracy",0)/100


        if key in normalized:

            normalized[key]=max(normalized[key],value)

        else:

            normalized[key]=value

    return normalized

# ==========================================
# TECHNICAL MATCH
# ==========================================

def technical_fit(profile_skills,user_norm):

    score=0

    contributions={}

    matched=0

    for skill,weight in profile_skills.items():

        if skill in user_norm:

            value=user_norm[skill]

            matched+=1

        else:

            # Neutral instead of zero (prevents unfair penalty)
            value=0.30

        contrib=weight*value

        contributions[skill]=contrib

        score+=contrib

    coverage=matched/max(1,len(profile_skills))

    score=_clamp(score,0,1)

    debug_print("\n--- TECHNICAL FIT ---")
    debug_print("Score:",round(score*100,1))
    debug_print("Coverage:",round(coverage*100,1))
    debug_print("Contributions:",contributions)

    return score,contributions,coverage


# ==========================================
# CLAIMED SKILL MATCH
# ==========================================

def claimed_alignment(profile_skills,claimed):

    if not profile_skills:

        return 0

    required=set(profile_skills.keys())

    claimed=set(claimed or [])

    overlap=len(required.intersection(claimed))

    return overlap/max(1,len(required))


# ==========================================
# PERSONALITY MATCH
# ==========================================

def personality_fit(user,career):

    TRAIT_WEIGHTS={

        "openness":0.25,
        "conscientiousness":0.30,
        "extraversion":0.15,
        "agreeableness":0.10,
        "neuroticism":0.20

    }

    diff=0

    for trait,weight in TRAIT_WEIGHTS.items():

        user_val=user.get(trait,3)

        career_val=career.get(trait,3)

        diff += abs(user_val-career_val) * weight

    # max possible difference:
    # 4 difference per trait * weight sum (1.0)
    max_diff = 4

    score = 1 - (diff/max_diff)

    score=_clamp(score,0,1)

    debug_print("\n--- PERSONALITY FIT ---")
    debug_print("Score:",round(score*100,1))

    return score
# ==========================================
# PERSONALITY REASONING
# ==========================================

def personality_reason(user):

    if not user:

        return []

    insights=[]

    if user.get("conscientiousness",3)>=4:

        insights.append(
        "strong discipline and structured thinking"
        )

    if user.get("openness",3)>=4:

        insights.append(
        "curiosity and learning ability"
        )

    if user.get("openness",3)<=2:

        insights.append(
        "preference for structured environments"
        )

    if user.get("extraversion",3)<=2:

        insights.append(
        "ability to work independently"
        )

    if user.get("agreeableness",3)>=4:

        insights.append(
        "good collaboration ability"
        )

    if user.get("neuroticism",3)<=2:

        insights.append(
        "good emotional stability"
        )

    if user.get("neuroticism",3)>=4:

        insights.append(
        "awareness of pressure and risk"
        )

    return insights[:3]

def detect_skill_gaps(profile_skills,user_norm):

    gaps=[]

    for skill in profile_skills:

        if skill not in user_norm:

            gaps.append(skill)

        elif user_norm[skill]<0.5:

            gaps.append(skill)

    return gaps[:5]


# ==========================================
# CONFIDENCE MODEL
# ==========================================

def calculate_confidence(coverage,technical,personality):

    confidence=(

        coverage*0.5+

        technical*0.3+

        personality*0.2

    )

    if confidence>=0.75:

        return "High"

    if confidence>=0.50:

        return "Medium"

    return "Low"

# ==========================================
# READINESS SCORE
# ==========================================

def readiness_score(coverage,technical):

    readiness=(coverage*0.7)+(technical*0.3)

    return round(readiness*100,1)


# ==========================================
# DOMAIN BOOST (INTELLIGENCE LAYER)
# ==========================================

def domain_bonus(profile,user_norm):

    data_skills=[

        "Python",
        "Pandas",
        "Numpy",
        "Pytorch"

    ]

    matches=sum(

        1 for s in data_skills

        if s in user_norm

    )

    if matches>=2:

        if "data" in profile["id"] or "ml" in profile["id"]:

            return 0.05

    return 0


def project_domain_bonus(profile,projects):

    if not projects:

        return 0

    text=" ".join(projects).lower()

    ai_words=[

        "ml",
        "ai",
        "nlp",
        "model",
        "prediction",
        "classification"

    ]

    backend_words=[

        "api",
        "backend",
        "server",
        "database"

    ]

    web_words=[

        "react",
        "frontend",
        "web",
        "ui"

    ]

    if any(w in text for w in ai_words):

        if "ml" in profile["id"]:

            return 0.07

    if any(w in text for w in backend_words):

        if "backend" in profile["id"]:

            return 0.05

    if any(w in text for w in web_words):

        if "frontend" in profile["id"]:

            return 0.05

    return 0

def experience_bonus(experience):

    if not experience:

        return 0

    text=" ".join(experience).lower()

    if "intern" in text:

        return 0.03

    if "freelance" in text:

        return 0.04

    if "year" in text:

        return 0.05

    return 0

def profile_bonus(profile,career):

    if not profile:

        return 0

    profile=profile.lower()

    if "ai" in profile and "ml" in career["id"]:

        return 0.05

    if "software" in profile and "backend" in career["id"]:

        return 0.04

    if "data" in profile and "data" in career["id"]:

        return 0.05

    return 0
# ==========================================
# MAIN RECOMMENDER
# ==========================================

def recommend_careers(

    skill_summary,
    claimed_skills,
    personality,

    projects=None,
    experience=None,
    profile=None,

    top_k=3,
    weights=None
):

    debug_print("\n========== CAREER RECOMMENDER START ==========")

    if weights is None:
        weights=DEFAULT_WEIGHTS

    debug_print("Weights:",weights)

    user_norm=normalize_user_skills(skill_summary)

    debug_print("Normalized skills:",user_norm)

    results=[]


    for career in CAREER_PROFILES:

        debug_print("\n============================")
        debug_print("Evaluating:",career["title"])


        # ===== TECHNICAL =====

        tech_score,contrib,coverage=technical_fit(

            career["skill_weights"],
            user_norm
        )


        # ===== PERSONALITY =====

        personality_score=personality_fit(

            personality or {},
            career["personality_target"]

        )


        # ===== CLAIMED =====

        claimed_score=claimed_alignment(

            career["skill_weights"],
            claimed_skills or []

        )


        # ===== BASE SCORE =====

        final=(

            weights["technical"]*tech_score+

            weights["personality"]*personality_score+

            weights["claimed"]*claimed_score

        )

        debug_print("Technical:",round(tech_score*100,1))
        debug_print("Personality:",round(personality_score*100,1))
        debug_print("Claimed:",round(claimed_score*100,1))

        debug_print("Base score:",round(final*100,1))


        # ===== BONUSES =====

        domain=domain_bonus(career,user_norm)

        project=project_domain_bonus(career,projects)

        exp=experience_bonus(experience)*0.5

        prof=profile_bonus(profile,career)


        final+=domain
        final+=project
        final+=exp
        final+=prof


        debug_print("Domain bonus:",round(domain*100,2))
        debug_print("Project bonus:",round(project*100,2))
        debug_print("Experience bonus:",round(exp*100,2))
        debug_print("Profile bonus:",round(prof*100,2))


        # ===== FINAL SCORE =====

        final=_clamp(final,0,1)

        debug_print("Final score:",round(final*100,1))


        # ===== FILTER WEAK CAREERS =====

        if final<READINESS_THRESHOLD:

            debug_print("Rejected (below threshold)")
            continue


        # ===== SKILL GAPS =====

        gaps=detect_skill_gaps(

            career["skill_weights"],
            user_norm

        )


        # ===== CONFIDENCE =====

        confidence=calculate_confidence(

            coverage,
            tech_score,
            personality_score

        )


        # ===== USER STRENGTHS =====

        strongest=sorted(

            user_norm.items(),

            key=lambda x:x[1],

            reverse=True

        )[:3]

        strengths=[s[0] for s in strongest]


        # ===== PERSONALITY INSIGHTS =====

        personality_insights=personality_reason(

            personality or {}

        )


        # ===== READINESS =====

        readiness=readiness_score(

            coverage,
            tech_score

        )


        # ===== OPTIONAL TEXT =====

        project_text=""

        if projects:

            project_text=f" Projects such as {projects[0]} show practical exposure."


        exp_text=""

        if experience:

            exp_text=f" Your experience ({experience[0]}) strengthens this path."


        # ===== REASON =====

        reason=(

            f"Recommended due to strength in "

            f"{', '.join(strengths[:2])}. "

            f"Your personality indicates "

            f"{', '.join(personality_insights) if personality_insights else 'balanced traits'}. "

            f"Technical match {round(tech_score*100)}%. "

            f"Career readiness {readiness}%."

            f"{project_text}"

            f"{exp_text}"

        )


        debug_print("Accepted:",career["title"])
        debug_print("Confidence:",confidence)
        debug_print("Readiness:",readiness)
        debug_print("Skill gaps:",gaps)


        # ===== RESULT OBJECT =====

        results.append({

            "career_id":career["id"],

            "title":career["title"],

            "final_score":round(final*100,1),

            "technical_fit":round(tech_score*100,1),

            "personality_fit":round(personality_score*100,1),

            "claimed_alignment":round(claimed_score*100,1),

            "confidence":confidence,

            "readiness":readiness,

            "reason":reason,

            "improvement_areas":gaps,

            "gap_reason":

            f"Improving {', '.join(gaps[:3])} "

            f"would significantly increase readiness.",

            "skill_coverage":round(coverage*100),

            "top_skill_contributions":sorted(

                [

                    {

                        "skill":k,

                        "contribution":round(v*100,2)

                    }

                    for k,v in contrib.items()

                ],

                key=lambda x:x["contribution"],

                reverse=True

            )[:5]

        })


    # ===== FINAL SORT =====

    results.sort(

        key=lambda x:x["final_score"],

        reverse=True

    )


    debug_print("\n========== FINAL RANKING ==========")

    for r in results:

        debug_print(
            r["title"],
            "Score:",
            r["final_score"]
        )


    debug_print("========== END ==========\n")


    return results[:top_k]

