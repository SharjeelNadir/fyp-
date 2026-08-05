# GuideMe AI Career Advisor

GuideMe is an AI-powered career guidance platform designed to help university students and fresh graduates make informed career decisions through intelligent resume analysis, personality assessment, technical evaluation, and personalized career roadmaps.

Unlike traditional career assessment platforms that rely only on personality quizzes, GuideMe combines multiple sources of information including resume content, technical skills, personality traits, and assessment performance to generate explainable career recommendations.

---

## Features

### Resume Analysis
- Upload PDF, DOCX or image resumes
- Automatic skill extraction
- Project detection
- Technology identification
- Experience parsing
- OCR support for image resumes

---

### Personality Assessment
- AI-generated personality questions
- Trait-based evaluation
- Work style analysis
- Career compatibility scoring

---

### Technical Assessment
- Automatically extracts technical skills from resumes
- Generates advanced MCQs using Llama 3
- Evaluates candidate proficiency
- Scores technical competency

---

### AI Career Recommendation
GuideMe combines:

- Resume skills
- Technical assessment score
- Personality profile
- Verified competencies

to recommend the most suitable career paths.

Recommendations include:

- Why the role matches
- Required skills
- Missing skills
- Career confidence score

---

### Career Roadmaps

Each recommended career includes:

- Learning roadmap
- Required technologies
- Recommended certifications
- Suggested projects
- Interview preparation
- Career progression path

---

### Job Fit Analyzer

Optimize resumes for specific job roles by:

- Comparing resume with target role
- Identifying missing skills
- ATS-friendly optimization
- Resume improvement suggestions

---

### AI Career Chatbot

Students can ask career-related questions such as:

- Which career suits me?
- What should I learn next?
- Which projects should I build?
- Which certification should I pursue?

The chatbot uses the user's profile and assessment results to provide contextual guidance.

---

## Tech Stack

### Frontend

- React
- React Router
- Axios
- Tailwind CSS

### Backend

- FastAPI
- Python
- Uvicorn

### AI / NLP

- Meta Llama 3 (8B)
- Ollama
- spaCy
- PyPDF2
- pytesseract
- FAISS

### Database

- SQLite

---

## System Workflow

```
Signup/Login
        │
        ▼
Upload Resume
        │
        ▼
Resume Parsing
        │
        ▼
Personality Assessment
        │
        ▼
Technical Assessment
        │
        ▼
Career Recommendation Engine
        │
        ▼
Career Roadmap
        │
        ▼
Job Fit Analysis
        │
        ▼
AI Career Chatbot
```

---

## Project Structure

```
GuideMe
│
├── app.py
├── database/
├── utils/
│   ├── parser.py
│   ├── career_recommender.py
│   ├── llm_handler.py
│   └── ...
│
├── react_frontend/
├── requirements.txt
└── README.md
```

---

## Installation

### Create Environment

```bash
conda create -n fyp python=3.10
conda activate fyp
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Install spaCy Model

```bash
python -m spacy download en_core_web_sm
```

### Start Ollama

Ensure Ollama is installed and running.

Pull the required model:

```bash
ollama pull llama3:8b
```

---

## Run Backend

```bash
uvicorn app:app --reload
```

---

## Run Frontend

```bash
cd react_frontend
npm install
npm start
```

---

## Core Technologies

- FastAPI
- React
- Python
- SQLite
- Meta Llama 3 (Ollama)
- spaCy
- FAISS
- PyPDF2
- OCR
- REST APIs

---

## Future Enhancements

- GitHub portfolio analysis
- AI project recommendations
- Personalized portfolio roadmap
- Internship recommendations
- Interview simulator
- Recruiter dashboard
- Learning progress tracking
- Cloud deployment
- Vector database integration
