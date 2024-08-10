# ai-job-scraper

**AI-Based Job Scraper & Dashboard (Flask + MongoDB + AI classification)**

A portfolio-ready project that ingests public job posts from open APIs (no HTML scraping), classifies them with an optional AI provider (OpenAI), tags skills, and displays results in a clean dashboard.

- **Stack:** Python (Flask), MongoDB (Atlas or local), Requests
- **AI:** OpenAI (Claude). If no API key is provided, a rule-based fallback is used.
- **Deploy:** Render (free tier) or Docker
- **Live Demo (self-hosted):** Deploy to Render and add your URL here

> Sources used are **public JSON APIs**:
> - Arbeitnow Job Board API (EU): https://www.arbeitnow.com/api/job-board-api
> - RemoteOK API (global): https://remoteok.com/api

> Always check and comply with each provider's Terms of Service before large-scale use.

---

## Features
- Fetch jobs from public APIs
- Store normalized data in MongoDB
- AI classification of role types (Backend, Frontend, Full-Stack, Data/ML, DevOps, Other)
- Skill extraction (Python, JS/TS, React, Node, Docker, SQL, NoSQL, etc.)
- Web dashboard with filters + charts
- One-click refresh to re-ingest latest jobs

---

## Quickstart (Local)

1) **Create and activate a virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

2) **Install dependencies**
```bash
pip install -r requirements.txt
```

3) **Copy env and set variables**
```bash
cp .env.example .env
# Edit .env to set MONGO_URI (Atlas or local), DB_NAME, and optionally AI keys
```

4) **Run the app**
```bash
python app.py
# Visit http://127.0.0.1:8000
```

If `MONGO_URI` is not set, the app will fall back to an in-memory mocked MongoDB (via `mongomock`) so you can run immediately.

---

## Deploy to Render

1) **Create a new Web Service** on Render and connect your GitHub repo.
2) Set **Build Command**: `pip install -r requirements.txt`
3) Set **Start Command**: `gunicorn -w 2 -b 0.0.0.0:$PORT app:app`
4) Set **Environment** (Render Dashboard → Environment):
   - `PYTHON_VERSION=3.11`
   - `FLASK_ENV=production`
   - `PORT=10000` (Render will inject PORT, but having this variable set is fine)
   - `MONGO_URI=...` (MongoDB Atlas connection string)
   - `DB_NAME=ai_job_scraper`
   - Optional: `OPENAI_API_KEY=...`
5) **Deploy.**

Alternatively, use the provided `render.yaml` for Infrastructure as Code (Blueprints).

---

## Project Structure
```
ai-job-scraper/
├── app.py
├── db.py
├── scraper/
│   ├── __init__.py
│   ├── job_sources.py
│   └── ai_classifier.py
├── templates/
│   ├── base.html
│   ├── index.html
│   └── job_detail.html
├── static/
│   ├── styles.css
│   └── app.js
├── requirements.txt
├── Procfile
├── render.yaml
├── Dockerfile
├── .env.example
├── LICENSE
└── README.md
```

---

## Environment Variables
- `FLASK_ENV` (default: `development`)
- `PORT` (default: `8000`)
- `MONGO_URI` (e.g., Atlas connection string; if missing, uses in-memory DB via mongomock)
- `DB_NAME` (default: `ai_job_scraper`)
- `OPENAI_API_KEY` (optional)

---

## Data Model
Jobs are stored as documents like:
```json
{
  "_id": "...",
  "source": "arbeitnow",
  "source_id": "12345",
  "title": "Data Scientist",
  "company": "Acme GmbH",
  "location": "Berlin, Germany",
  "remote": true,
  "url": "https://...",
  "description": "...",
  "published_at": "2025-08-01T10:00:00Z",
  "tags": ["Python", "ML", "Docker"],
  "ai_class": "Data/ML",
  "ai_reasoning": "Likely Data/ML due to keywords ...",
  "ingested_at": "2025-08-15T00:00:00Z"
}
```

---

## Notes
- Keep API calls reasonable. Cache results in MongoDB.
- Extend `scraper/job_sources.py` to add more providers.
- Swap the AI backend in `scraper/ai_classifier.py` as you prefer.
- For a stronger portfolio, add small tests and GitHub Actions CI later.