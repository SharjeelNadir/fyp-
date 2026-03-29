# frontend/utils/career_recommender.py
from typing import Dict, Any, List, Tuple
from utils.career_profiles import CAREER_PROFILES


# ======================================================
# DEFAULT MODEL WEIGHTS (ACADEMIC CONFIG)
# ======================================================

DEFAULT_WEIGHTS = {
    "technical": 0.60,
    "personality": 0.25,
    "claimed": 0.15
}

def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def normalize_user_skills(skill_summary: Dict[str, Dict[str, int]]) -> Dict[str, float]:
    """
    skill_summary example:
    {
      "Python": {"correct": 2, "total": 3, "accuracy": 67},
      ...
    }

    Returns normalized [0..1] per skill using user's max accuracy as denominator.
    """
    if not skill_summary:
        return {}

    accuracies = [v.get("accuracy", 0) for v in skill_summary.values()]
    max_acc = max(accuracies) if accuracies else 0
    if max_acc <= 0:
        # user attempted but got 0 everywhere
        return {k: 0.0 for k in skill_summary.keys()}

    return {k: (v.get("accuracy", 0) / max_acc) for k, v in skill_summary.items()}


def technical_fit(profile_skill_weights: Dict[str, float], user_norm: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
    """
    Weighted sum of normalized skill strength for skills in the career profile.
    Missing skill => 0.
    """
    contrib = {}
    score = 0.0
    for skill, w in profile_skill_weights.items():
        v = user_norm.get(skill, 0.0)
        c = w * v
        contrib[skill] = c
        score += c
    return _clamp(score, 0.0, 1.0), contrib


def claimed_alignment(profile_skill_weights: Dict[str, float], claimed_skills: List[str]) -> float:
    """
    Simple deterministic boost: how many required skills are claimed.
    """
    if not profile_skill_weights:
        return 0.0
    required = set(profile_skill_weights.keys())
    claimed = set(claimed_skills or [])
    overlap = len(required.intersection(claimed))
    return overlap / max(1, len(required))  # [0..1]


def personality_fit(target: Dict[str, int], user: Dict[str, int]) -> float:
    """
    Deterministic similarity score in [0..1] using distance over 1..5 scale.
    If user personality missing -> neutral 0.5
    """
    if not user:
        return 0.5
    traits = ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]

    # max distance per trait is 4 (1..5)
    total_dist = 0.0
    for t in traits:
        tv = int(target.get(t, 3))
        uv = int(user.get(t, 3))
        total_dist += abs(tv - uv)

    max_dist = 4 * len(traits)
    similarity = 1.0 - (total_dist / max_dist)
    return _clamp(similarity, 0.0, 1.0)


def recommend_careers(
    skill_summary: Dict[str, Dict[str, int]],
    claimed_skills: List[str],
    personality: Dict[str, int],
    top_k: int = 3,
    weights: Dict[str, float] = None
) -> List[Dict[str, Any]]:
    """
    Final = wt * Technical + wp * Personality + wc * Claimed
    Default weights: 0.60, 0.25, 0.15
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS

    user_norm = normalize_user_skills(skill_summary)

    results = []
    for prof in CAREER_PROFILES:
        t_score, t_contrib = technical_fit(prof["skill_weights"], user_norm)
        p_score = personality_fit(prof["personality_target"], personality or {})
        c_score = claimed_alignment(prof["skill_weights"], claimed_skills or [])

        final = (
            weights["technical"] * t_score
            + weights["personality"] * p_score
            + weights["claimed"] * c_score
        )

        results.append({
    "career_id": prof["id"],
    "title": prof["title"],
    "final_score": round(final * 100, 1),
    "technical_fit": round(t_score * 100, 1),
    "personality_fit": round(p_score * 100, 1),
    "claimed_alignment": round(c_score * 100, 1),
    "model_weights": weights,
    "top_skill_contributions": sorted(
        [{"skill": k, "contribution": round(v * 100, 2)} for k, v in t_contrib.items()],
        key=lambda x: x["contribution"],
        reverse=True
    )[:5],
})


    results.sort(key=lambda r: r["final_score"], reverse=True)
    return results[:top_k]
