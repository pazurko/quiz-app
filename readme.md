# BioQuiz — quiz-app.mazur.page

Personal quiz app for studying LF UPJŠ Košice entrance exam questions.
Built with Vue 3, FastAPI, and Supabase.

## Structure
- `frontend/` — Vue 3 + Vite app
- `api/` — FastAPI backend (Vercel serverless)
- `data/` — Source JSON files (questions + answers)
- `scripts/` — One-time utility scripts
- `home-page/` — home.mazur.page landing page

## Setup

### 1. Supabase
- Run `supabase_schema.sql` in Supabase SQL Editor

### 2. Backend
```bash
cd api
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in your Supabase keys
uvicorn index:app --reload --port 8000
```

### 3. Seed the database
```bash
cd scripts
python seed_db.py
```

### 4. Frontend
```bash
cd frontend
npm install
cp .env.example .env.local   # fill in your Supabase keys
npm run dev
```

## Deploy to Vercel
1. Push repo to GitHub
2. Import in Vercel dashboard
3. Set environment variables (SUPABASE_URL, SUPABASE_SERVICE_KEY, VITE_SUPABASE_URL, VITE_SUPABASE_ANON_KEY)
4. Add domain `quiz-app.mazur.page` in Vercel → Domains

## Claude Code usage
Run `claude` in PyCharm terminal. See `CLAUDE.md` for instructions.
