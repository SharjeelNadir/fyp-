import json

def build_user_context(stats: dict) -> str:
    skill_summary = stats["skill_summary"]
    personality = json.loads(stats["master"]["personality"])

    strong_skills = [s for s, d in skill_summary.items() if d["accuracy"] >= 70]
    weak_skills = [s for s, d in skill_summary.items() if d["accuracy"] < 70]

    context = f"""
User Profile:
Strong: {', '.join(strong_skills)}
Weak: {', '.join(weak_skills)}
Personality: {personality}
"""
    return context.strip()