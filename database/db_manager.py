# /frontend/src/database/db_manager.py
"""
GuideMe – Database Manager (SQLite)

Single Source of Truth for all persistent data.

Responsibilities:
- Users (auth)
- Resume skills (CLAIMED skills)
- Personality profiles (OCEAN)
- Technical assessments (VERIFIED skills)
- Pre-generated MCQs (quiz cache)
- Career recommendations (cached)

Design Philosophy:
1) Resume skills = claimed
2) Quiz verifies skills
3) MCQs generated once & stored
4) Career recommendations generated once & cached
5) Latest records = active profile
"""

import sqlite3
import json
import os
from typing import List, Dict, Optional, Any, Tuple

DB_PATH = "career_app.db"

# ======================================================
# CONNECTION HELPERS
# ======================================================

def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def _to_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False)


def _from_json(data: Optional[str], default):
    if not data:
        return default
    try:
        return json.loads(data)
    except:
        return default


# ======================================================
# DATABASE INITIALIZATION
# ======================================================

def init_db():
    conn = _connect()
    cursor = conn.cursor()

    # USERS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # RESUMES (CLAIMED SKILLS)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    file_name TEXT,

    extracted_skills TEXT,
    projects TEXT,
    experience TEXT,
    profile_type TEXT,
    resume_text TEXT,

    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
    """)

    # PERSONALITY
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personality_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            openness INTEGER,
            conscientiousness INTEGER,
            extraversion INTEGER,
            agreeableness INTEGER,
            neuroticism INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # ASSESSMENTS (MASTER)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            total_score INTEGER,
            total_questions INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # QUESTION ATTEMPTS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS question_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id INTEGER NOT NULL,
            skill_name TEXT NOT NULL,
            is_correct INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (assessment_id) REFERENCES assessments(id) ON DELETE CASCADE
        )
    """)



        # GLOBAL QUESTION BANK
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS question_bank (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_name TEXT NOT NULL,
            question_text TEXT NOT NULL,
            options_json TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_bank_question
        ON question_bank (skill_name, question_text)
    """)

    # GENERATED MCQs (QUIZ CACHE)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS generated_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            skill_name TEXT NOT NULL,
            question_text TEXT NOT NULL,
            options_json TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # CAREER RECOMMENDATIONS CACHE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS career_recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            recommendations_json TEXT NOT NULL,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # ---- DEDUPE EXISTING ROWS THEN ADD UNIQUE INDEX ----
    cursor.execute("""
        DELETE FROM generated_questions
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM generated_questions
            GROUP BY user_id, skill_name, question_text
        )
    """)

    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS uq_generated_question
        ON generated_questions (user_id, skill_name, question_text)
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully.")


# ======================================================
# AUTHENTICATION
# ======================================================

def db_signup(email: str, password: str) -> Tuple[bool, str]:
    conn = _connect()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, password)
        )
        conn.commit()
        return True, "Account created successfully"
    except sqlite3.IntegrityError:
        return False, "Email already registered"
    finally:
        conn.close()


def db_login(email: str, password: str) -> Optional[int]:
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM users WHERE email = ? AND password = ?",
        (email, password)
    )
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


# ======================================================
# RESUME (CLAIMED SKILLS)
# ======================================================

def db_save_resume_data(
    user_id: int,
    file_name: str,
    skills: List[str],
    projects: List[str],
    experience: List[str],
    profile: str,
    resume_text: str
) -> bool:

    try:

        conn = _connect()
        cursor = conn.cursor()

        cursor.execute("""

        INSERT INTO resumes (

            user_id,
            file_name,

            extracted_skills,
            projects,
            experience,
            profile_type,
            resume_text

        )

        VALUES (?,?,?,?,?,?,?)

        """,(

            user_id,

            file_name,

            _to_json(skills),

            _to_json(projects),

            _to_json(experience),

            profile,

            resume_text[:8000]   # prevent huge storage

        ))

        conn.commit()

        return True

    except Exception as e:

        print("db_save_resume_data error:", e)

        return False

    finally:

        conn.close()

def db_get_latest_resume(user_id:int):

    conn=_connect()

    conn.row_factory=sqlite3.Row

    cursor=conn.cursor()

    cursor.execute("""

    SELECT *

    FROM resumes

    WHERE user_id=?

    ORDER BY uploaded_at DESC

    LIMIT 1

    """,(user_id,))

    row=cursor.fetchone()

    conn.close()

    if not row:

        return None

    return {

        "skills":_from_json(row["extracted_skills"],[]),

        "projects":_from_json(row["projects"],[]),

        "experience":_from_json(row["experience"],[]),

        "profile":row["profile_type"],

        "resume_text":row["resume_text"]

    }

def db_get_latest_resume_skills(user_id:int):

    resume=db_get_latest_resume(user_id)

    if not resume:

        return []

    return resume.get("skills",[])
# ======================================================
# GENERATED QUESTIONS (MCQ CACHE)
# ======================================================

def db_delete_generated_questions(user_id: int):
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM generated_questions WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def db_save_generated_questions(user_id: int, questions: List[Dict]) -> bool:
    """
    Inserts quiz questions; duplicates are blocked by UNIQUE INDEX + INSERT OR IGNORE.
    """
    try:
        conn = _connect()
        cursor = conn.cursor()

        for q in questions:
            cursor.execute("""
                INSERT OR IGNORE INTO generated_questions
                (user_id, skill_name, question_text, options_json, correct_answer)
                VALUES (?, ?, ?, ?, ?)
            """, (
                user_id,
                q["skill"],
                q["question"],
                _to_json(q["options"]),
                q["answer"]
            ))

        conn.commit()
        return True
    except Exception as e:
        print("db_save_generated_questions error:", e)
        return False
    finally:
        conn.close()


def db_get_generated_questions(user_id: int) -> List[Dict]:
    conn = _connect()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT skill_name, question_text, options_json, correct_answer
        FROM generated_questions
        WHERE user_id = ?
        ORDER BY id ASC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "skill": r["skill_name"],
            "question": r["question_text"],
            "options": _from_json(r["options_json"], []),
            "answer": r["correct_answer"]
        }
        for r in rows
    ]

def db_save_question_bank(questions: List[Dict]):

    conn = _connect()
    cursor = conn.cursor()

    try:

        for q in questions:

            cursor.execute("""
                INSERT OR IGNORE INTO question_bank
                (skill_name, question_text, options_json, correct_answer)
                VALUES (?, ?, ?, ?)
            """,(
                q["skill"],
                q["question"],
                _to_json(q["options"]),
                q["answer"]
            ))

        conn.commit()

    except Exception as e:

        print("bank save error:",e)

    finally:

        conn.close()

def db_get_bank_questions(skill:str,count:int):

    conn=_connect()
    conn.row_factory=sqlite3.Row
    cursor=conn.cursor()

    cursor.execute("""
        SELECT skill_name,question_text,options_json,correct_answer
        FROM question_bank
        WHERE skill_name=?
        ORDER BY RANDOM()
        LIMIT ?
    """,(skill,count))

    rows=cursor.fetchall()

    conn.close()

    return [

        {
            "skill":r["skill_name"],
            "question":r["question_text"],
            "options":_from_json(r["options_json"],{}),
            "answer":r["correct_answer"]
        }

        for r in rows
    ]

# ======================================================
# SAVE FULL ASSESSMENT
# ======================================================

def db_save_full_assessment(
    user_id: int,
    total_score: int,
    total_questions: int,
    personality_dict: Dict[str, int],
    skill_breakdown: List[List]
) -> bool:

    conn = _connect()
    cursor = conn.cursor()

    try:
        # Save personality snapshot
        if personality_dict:
            cursor.execute("""
                INSERT INTO personality_profiles
                (user_id, openness, conscientiousness, extraversion, agreeableness, neuroticism)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                personality_dict.get("openness"),
                personality_dict.get("conscientiousness"),
                personality_dict.get("extraversion"),
                personality_dict.get("agreeableness"),
                personality_dict.get("neuroticism")
            ))

        # Create master assessment
        cursor.execute("""
            INSERT INTO assessments (user_id, total_score, total_questions)
            VALUES (?, ?, ?)
        """, (user_id, total_score, total_questions))

        assessment_id = cursor.lastrowid

        # Store each attempt
        for skill, is_correct in skill_breakdown:
            cursor.execute("""
                INSERT INTO question_attempts
                (assessment_id, skill_name, is_correct)
                VALUES (?, ?, ?)
            """, (assessment_id, skill, int(is_correct)))

        conn.commit()
        return True

    except Exception as e:
        print("db_save_full_assessment error:", e)
        conn.rollback()
        return False
    finally:
        conn.close()


# ======================================================
# UNIFIED USER STATS
# ======================================================

def db_get_user_stats(user_id: int) -> Optional[Dict[str, Any]]:

    conn = _connect()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM assessments
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    """, (user_id,))
    assessment = cursor.fetchone()

    if not assessment:
        conn.close()
        return None

    assessment_id = assessment["id"]

    cursor.execute("""
        SELECT skill_name, is_correct
        FROM question_attempts
        WHERE assessment_id = ?
    """, (assessment_id,))
    attempts = cursor.fetchall()

    skill_summary: Dict[str, Dict[str, int]] = {}

    for row in attempts:
        skill = row["skill_name"]
        correct = row["is_correct"]

        if skill not in skill_summary:
            skill_summary[skill] = {"correct": 0, "total": 0, "accuracy": 0}

        skill_summary[skill]["total"] += 1
        skill_summary[skill]["correct"] += int(correct)

    for skill, data in skill_summary.items():
        data["accuracy"] = round((data["correct"] / data["total"]) * 100) if data["total"] else 0

    conn.close()

    return {
        "master": dict(assessment),
        "breakdown": [
            {"skill_name": r["skill_name"], "is_correct": r["is_correct"]}
            for r in attempts
        ],
        "skill_summary": skill_summary,
        "claimed_skills": db_get_latest_resume_skills(user_id),
    }


# ======================================================
# CAREER RECOMMENDATION CACHE
# ======================================================

def db_save_user_recommendations(user_id: int, recommendations: Dict) -> bool:
    try:
        conn = _connect()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO career_recommendations
            (user_id, recommendations_json)
            VALUES (?, ?)
        """, (user_id, _to_json(recommendations)))
        conn.commit()
        return True
    except Exception as e:
        print("db_save_user_recommendations error:", e)
        return False
    finally:
        conn.close()


def db_get_user_recommendations(user_id: int) -> Optional[Dict]:
    conn = _connect()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT recommendations_json
        FROM career_recommendations
        WHERE user_id = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    return _from_json(row[0], None) if row else None


# ======================================================
# DEV RESET
# ======================================================

def db_reset_all():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()