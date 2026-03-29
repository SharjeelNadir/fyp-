# final_folder/frontend_connected/utils/parser.py
import spacy
import PyPDF2
import docx
from PIL import Image
import pytesseract

class SimpleResumeParser:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            import os
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")

    def extract_text(self, filepath: str):
        ext = filepath.split(".")[-1].lower()
        if ext == "pdf":
            reader = PyPDF2.PdfReader(filepath)
            return "".join(page.extract_text() or "" for page in reader.pages)
        if ext == "docx":
            d = docx.Document(filepath)
            return "\n".join(p.text for p in d.paragraphs)
        if ext in ("jpg", "jpeg", "png"):
            return pytesseract.image_to_string(Image.open(filepath))
        return ""

    def extract_skills(self, text: str):
        # Professional technical skill list
        TECH = ["python", "javascript", "java", "react", "node", "sql", "django", "flask", "pandas", "numpy", "tensorflow", "pytorch", "mongodb"]
        doc = self.nlp(text.lower())
        found = [t.text.capitalize() for t in doc if t.text in TECH]
        return list(dict.fromkeys(found))