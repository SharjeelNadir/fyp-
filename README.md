# GuideMe AI Career Advisor

## Setup

Create environment:

conda create -n fyp python=3.10
conda activate fyp

Install dependencies:

pip install -r requirements.txt

Install spacy model:

python -m spacy download en_core_web_sm

Run backend:

uvicorn app:app --reload

Run frontend:

cd react_frontend
npm install
npm start