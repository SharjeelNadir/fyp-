from utils.parser import SimpleResumeParser
import re

parser = SimpleResumeParser()

file = "uploads/Sharjeel-AI-Resume .pdf"

text = parser.extract_text(file)

print("\n===== RAW TEXT =====\n")
print(text[:1500])


# =====================
# TECHNOLOGY EXTRACTION
# =====================

TECH_KEYWORDS=[

# programming
"python","java","c++","javascript","r",

# backend
"flask","django","node","express",

# frontend
"react","vue","angular",

# data
"pandas","numpy","scikit","pytorch",
"tensorflow","spark","hadoop","kafka",

# db
"mongodb","mysql","postgresql","sql",

# ai
"nlp","transformers","openai","llama",

# creative
"lightroom","capcut","davinci",
"canva","premiere","after effects"

]

def extract_technologies(text):

    found=[]

    text_lower=text.lower()

    for tech in TECH_KEYWORDS:

        if tech in text_lower:

            found.append(tech.capitalize())

    return sorted(list(set(found)))


# =====================
# SKILLS
# =====================

print("\n===== SKILLS =====\n")

techs = extract_technologies(text)

skills = list(set(
parser.extract_skills(text) + techs
))

print(sorted(skills))


# =====================
# SECTION DETECTOR
# =====================

SECTION_HEADERS=[
"projects",
"personal projects",
"portfolio",
"experience",
"work experience",
"employment",
"skills",
"technical skills",
"education"
]

def get_section(text,section_names):

    text_lower=text.lower()

    for name in section_names:

        pattern=name+r'([\s\S]*?)(projects|experience|skills|education|$)'

        match=re.search(pattern,text_lower)

        if match:

            return match.group(1)

    return ""


# =====================
# PROJECT EXTRACTION
# =====================

def extract_projects(text):

    section=get_section(text,[
        "personal projects",
        "projects",
        "portfolio"
    ])

    if not section:
        return []

    projects=[]

    numbered=re.findall(
        r'\d+\.\s*([A-Za-z0-9 &]+)',
        section
    )

    bullets=re.findall(
        r'•\s*([A-Za-z0-9 &]+)',
        section
    )

    colon=re.findall(
        r'([A-Za-z0-9 ]+):',
        section
    )

    projects=numbered+bullets+colon

    ignore_words=[
        "handled",
        "focused",
        "worked",
        "developed",
        "built",
        "using"
    ]

    clean=[]

    for p in projects:

        p=p.strip()

        if len(p)<4:
            continue

        if any(w in p.lower() for w in ignore_words):
            continue

        clean.append(p.title())

    return sorted(list(set(clean)))


print("\n===== PROJECTS =====\n")

projects=extract_projects(text)

for p in projects:

    print("-",p)


# =====================
# EXPERIENCE EXTRACTION
# =====================

def extract_experience(text):

    section=get_section(text,[
        "experience",
        "work experience",
        "employment"
    ])

    roles=[]

    if section:

        roles=re.findall(
            r'([A-Za-z ]+intern)',
            section.lower()
        )

        roles=[r.title() for r in roles]

    years=re.findall(
        r'\d+\s+years',
        text.lower()
    )

    if years:

        roles.append(years[0]+" experience")

    if "freelance" in text.lower():

        roles.append("Freelance Experience")

    return sorted(list(set(roles)))


print("\n===== EXPERIENCE =====\n")

exp=extract_experience(text)

for e in exp:

    print("-",e)


# =====================
# TECHNOLOGIES
# =====================

print("\n===== TECHNOLOGIES =====\n")

print(techs)


# =====================
# PROFILE DETECTION
# =====================

def detect_profile(techs,projects):

    text=" ".join(techs+projects).lower()

    ai_keywords=[
        "nlp","machine learning","deep learning",
        "transformers","pytorch","tensorflow"
    ]

    data_keywords=[
        "spark","hadoop","kafka"
    ]

    dev_keywords=[
        "react","flask","node","express"
    ]

    creative_keywords=[
        "lightroom","capcut","davinci",
        "canva","premiere"
    ]

    if any(x in text for x in ai_keywords):
        return "AI / ML"

    if any(x in text for x in data_keywords):
        return "Data Engineering"

    if any(x in text for x in dev_keywords):
        return "Software Development"

    if any(x in text for x in creative_keywords):
        return "Creative / Media"

    return "General Tech"


print("\n===== PROFILE TYPE =====\n")

profile=detect_profile(techs,projects)

print(profile)