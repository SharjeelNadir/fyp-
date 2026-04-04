from typing import Dict, Any, List, Tuple
from utils.career_profiles import CAREER_PROFILES

# ==========================================
# MODEL CONFIGURATION
# ==========================================

DEFAULT_WEIGHTS = {

    # Slightly more balanced: give personality a bit more weight
    "technical":0.55,
    "personality":0.30,
    "claimed":0.15

}

READINESS_THRESHOLD=0.30


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


# ==========================================
# SKILL NORMALIZATION
# ==========================================

def normalize_user_skills(skill_summary):

    if not skill_summary:

        return {}

    accuracies=[

        v.get("accuracy",0)

        for v in skill_summary.values()

    ]

    max_acc=max(accuracies) if accuracies else 0

    if max_acc<=0:

        return {}

    normalized={}

    for skill,data in skill_summary.items():

        key=SKILL_SYNONYMS.get(skill,skill)

        normalized[key]=data.get("accuracy",0)/max_acc

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

    return _clamp(score,0,1),contributions,coverage


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

def personality_fit(target,user):

    if not user:

        return 0.5

    traits=[

        "openness",
        "conscientiousness",
        "extraversion",
        "agreeableness",
        "neuroticism"

    ]

    dist=0

    for t in traits:

        tv=int(target.get(t,3))

        uv=int(user.get(t,3))

        dist+=abs(tv-uv)

    max_dist=4*len(traits)

    similarity=1-(dist/max_dist)

    return _clamp(similarity,0,1)


# ==========================================
# SKILL GAP DETECTION
# ==========================================

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

def calculate_confidence(coverage,technical):

    confidence=(coverage*0.6)+(technical*0.4)

    if confidence>=0.75:

        return "High"

    if confidence>=0.50:

        return "Medium"

    return "Low"


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


# ==========================================
# MAIN RECOMMENDER
# ==========================================

def recommend_careers(

    skill_summary,
    claimed_skills,
    personality,
    top_k=3,
    weights=None

):

    if weights is None:

        weights=DEFAULT_WEIGHTS

    user_norm=normalize_user_skills(skill_summary)

    results=[]

    for profile in CAREER_PROFILES:

        tech_score,contrib,coverage=technical_fit(

            profile["skill_weights"],
            user_norm
        )

        personality_score=personality_fit(

            profile["personality_target"],
            personality or {}

        )

        claimed_score=claimed_alignment(

            profile["skill_weights"],
            claimed_skills or []

        )

        final=(

            weights["technical"]*tech_score+

            weights["personality"]*personality_score+

            weights["claimed"]*claimed_score

        )

        # Add domain intelligence
        final+=domain_bonus(profile,user_norm)

        # Filter weak careers
        if final<READINESS_THRESHOLD:

            continue

        gaps=detect_skill_gaps(

            profile["skill_weights"],
            user_norm

        )

        confidence=calculate_confidence(

            coverage,
            tech_score

        )

        strongest=sorted(

            user_norm.items(),

            key=lambda x:x[1],

            reverse=True

        )[:3]

        strengths=[s[0] for s in strongest]

        reason=(

            f"Recommended due to strength in "

            f"{', '.join(strengths[:2])}. "

            f"Technical match {round(tech_score*100)}%. "

            f"Personality compatibility "

            f"{round(personality_score*100)}%. "

            f"Skill coverage {round(coverage*100)}%."

        )

        results.append({

            "career_id":profile["id"],

            "title":profile["title"],

            "final_score":round(final*100,1),

            "technical_fit":round(tech_score*100,1),

            "personality_fit":round(personality_score*100,1),

            "claimed_alignment":round(claimed_score*100,1),

            "confidence":confidence,

            "reason":reason,

            "improvement_areas":gaps,

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

    results.sort(

        key=lambda x:x["final_score"],

        reverse=True

    )

    return results[:top_k]