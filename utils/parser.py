# final_folder/frontend_connected/utils/parser.py

import spacy
import PyPDF2
import docx
from PIL import Image
import pytesseract
import re


class SimpleResumeParser:

    def __init__(self):

        try:
            self.nlp = spacy.load("en_core_web_sm")

        except:

            import os

            os.system("python -m spacy download en_core_web_sm")

            self.nlp = spacy.load("en_core_web_sm")


    # =========================================
    # TEXT EXTRACTION
    # =========================================

    def extract_text(self, filepath:str):

        ext = filepath.split(".")[-1].lower()

        if ext == "pdf":

            reader = PyPDF2.PdfReader(filepath)

            return "".join(
                page.extract_text() or ""
                for page in reader.pages
            )

        if ext == "docx":

            d = docx.Document(filepath)

            return "\n".join(
                p.text for p in d.paragraphs
            )

        if ext in ("jpg","jpeg","png"):

            return pytesseract.image_to_string(
                Image.open(filepath)
            )

        return ""


    # =========================================
    # SKILLS
    # =========================================

    def extract_skills(self,text:str):

        TECH=[

            "python","javascript","java",

            "react","node","sql",

            "django","flask",

            "pandas","numpy",

            "tensorflow","pytorch",

            "mongodb"

        ]

        doc=self.nlp(text.lower())

        found=[

            t.text.capitalize()

            for t in doc

            if t.text in TECH

        ]

        return list(dict.fromkeys(found))


    # =========================================
    # SECTION FINDER
    # =========================================

    def _get_section(self,text,headers):

        text_lower=text.lower()

        for h in headers:

            pattern = h+r'([\s\S]*?)(projects|experience|skills|education|$)'

            match=re.search(pattern,text_lower)

            if match:

                return match.group(1)

        return ""


    # =========================================
    # PROJECTS
    # =========================================

    def extract_projects(self,text):

        section=self._get_section(

            text,

            [

                "personal projects",

                "projects",

                "portfolio"

            ]

        )

        if not section:

            return []


        numbered=re.findall(

            r'\d+\.\s*([A-Za-z0-9 \-&]+)',

            section

        )


        bullets=re.findall(

            r'•\s*([A-Za-z0-9 \-&]+)',

            section

        )


        colon=re.findall(

            r'([A-Za-z0-9 \-&]+):',

            section

        )


        projects=numbered+bullets+colon


        clean=[]

        for p in projects:

            p=p.strip()

            if len(p)<4:

                continue

            clean.append(p.title())


        return sorted(

            list(set(clean))

        )[:5]


    # =========================================
    # EXPERIENCE
    # =========================================

    def extract_experience(self,text):

        section=self._get_section(

            text,

            [

                "experience",

                "work experience",

                "employment"

            ]

        )

        roles=[]


        if section:

            found=re.findall(

                r'([A-Za-z ]+intern)',

                section.lower()

            )

            roles=[r.title() for r in found]


        if "freelance" in text.lower():

            roles.append(

                "Freelance Experience"

            )


        years=re.findall(

            r'\d+\s+years',

            text.lower()

        )

        if years:

            roles.append(

                years[0]+" experience"

            )


        return sorted(

            list(set(roles))

        )[:5]


    # =========================================
    # PROFILE TYPE
    # =========================================

    def detect_profile_type(

        self,

        text

    ):

        text=text.lower()


        if any(x in text for x in [

            "machine learning",

            "deep learning",

            "nlp",

            "pytorch",

            "tensorflow"

        ]):

            return "AI/ML"


        if any(x in text for x in [

            "react",

            "flask",

            "node",

            "api",

            "backend"

        ]):

            return "Software Development"


        if any(x in text for x in [

            "spark",

            "hadoop",

            "etl",

            "pipeline"

        ]):

            return "Data Engineering"


        if any(x in text for x in [

            "photoshop",

            "premiere",

            "after effects"

        ]):

            return "Creative Tech"


        return "General Tech"