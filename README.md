# Resume Analyzer

Django app that lets users register/login, upload a resume (PDF), paste a job
description, and get back a match score, extracted/missing skills, an ATS
compatibility score, and improvement suggestions.

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download the spaCy English model (required for skill extraction)
python -m spacy download en_core_web_sm

# 4. Configure environment variables
cp .env.example .env
# edit .env and set a real SECRET_KEY

# 5. Run migrations
python manage.py makemigrations
python manage.py migrate

# 6. Create an admin user (optional, for /admin/)
python manage.py createsuperuser

# 7. Run the dev server
python manage.py runserver
```

Visit http://127.0.0.1:8000/

## Project structure

```
resume_analyzer/
├── manage.py
├── requirements.txt
├── resume_analyzer/        # project settings, urls, wsgi/asgi
├── core/                   # the app
│   ├── models.py           # Resume, Analysis
│   ├── forms.py            # Register, ResumeUpload, JobDescription
│   ├── views.py            # auth, dashboard, upload, analyze, results
│   ├── urls.py
│   ├── admin.py
│   ├── utils/
│   │   ├── pdf_reader.py       # pdfplumber text extraction
│   │   ├── skills_data.py      # curated skills taxonomy
│   │   ├── skill_extractor.py  # spaCy PhraseMatcher skill extraction
│   │   ├── scoring.py          # TF-IDF + cosine similarity scoring
│   │   ├── ats_checker.py      # rule-based ATS compatibility rubric
│   │   └── suggestions.py      # rule-based suggestion generation
│   ├── templates/core/
│   └── templates/registration/
└── templates/base.html     # shared Bootstrap layout
```

## How scoring works

- **Similarity score**: TF-IDF vectorizes resume text and job description
  text, then cosine similarity between the two vectors gives a 0-100 score.
- **Skill extraction**: a curated taxonomy (`utils/skills_data.py`) is matched
  against text using spaCy's `PhraseMatcher`. This is more reliable for this
  use case than generic NER, which doesn't have a built-in "skill" concept.
- **ATS score**: a deterministic rubric checking for section headers,
  contact info, text density (catches scanned/image PDFs), page count, and
  signs of multi-column layouts that break ATS parsers.
- **Overall score**: a weighted blend (40% similarity, 40% skill overlap,
  20% ATS score) — tune weights in `utils/scoring.py`.

## Extending

- Add more entries to `TECH_SKILLS` / `SOFT_SKILLS` in `skills_data.py` as
  you find gaps.
- Swap SQLite for PostgreSQL by setting `USE_POSTGRES=True` in `.env` and
  filling in the `DB_*` variables (`psycopg2-binary` needed — not yet in
  requirements.txt, add it when you switch).
- The scanned-PDF case (image-only resumes) isn't OCR'd yet; `pdf_reader.py`
  would need a Tesseract/`pytesseract` fallback for that.
