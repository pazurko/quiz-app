# Quiz App — Claude Code Instructions

## Project Overview
A personal quiz web app for studying exam questions (currently: Biology for LF UPJS Košice entrance exam).
Users can register, review questions topic by topic, run custom timed quizzes, and track their history.

## Stack
- **Frontend:** Vue 3 + Vite (in `/frontend/`)
- **Backend:** Python FastAPI (in `/api/`)
- **Database:** Supabase (PostgreSQL + Auth)
- **Deployment:** Vercel
- **Domain:** quiz-app.mazur.page

## Project Structure
```
quiz-app/
├── CLAUDE.md              ← you are here
├── vercel.json            ← routing config
├── frontend/              ← Vue 3 app
│   ├── src/
│   │   ├── views/         ← page-level components
│   │   ├── components/    ← reusable UI pieces
│   │   ├── stores/        ← Pinia state management
│   │   ├── lib/
│   │   │   ├── supabase.js  ← Supabase client
│   │   │   └── api.js       ← API helper functions
│   │   ├── router/        ← Vue Router
│   │   └── App.vue
│   ├── index.html
│   └── vite.config.js
├── api/                   ← FastAPI (Vercel serverless)
│   ├── index.py           ← main FastAPI app entry
│   ├── routes/
│   │   ├── questions.py
│   │   ├── quiz.py
│   │   └── history.py
│   ├── models.py          ← Pydantic models
│   └── db.py              ← Supabase client for Python
├── data/
│   ├── questions_biology.json
│   └── answers_biology.json
└── scripts/
    └── seed_db.py         ← one-time DB seeding script
```

## Coding Rules — READ BEFORE DOING ANYTHING
- **NEVER** run `git commit`, `git push`, `git pull`, or any git command — Michal handles all git via PyCharm
- **NEVER** run `npm install` or `pip install` without asking first
- **NEVER** modify `.env` or `.env.local` files
- **NEVER** delete any files
- **NEVER** push secrets, API keys, or passwords to any file
- **DO** explain every non-obvious change you make and why
- **DO** ask before making changes to database schema
- **DO** suggest code in small, reviewable chunks

## Environment Variables
Frontend (`.env.local` in `/frontend/`):
```
VITE_SUPABASE_URL=...
VITE_SUPABASE_ANON_KEY=...
VITE_API_BASE_URL=...
```

Backend (`.env` in `/api/`):
```
SUPABASE_URL=...
SUPABASE_SERVICE_KEY=...
```

## Data Model Summary
- **subjects** — e.g. "Biológia" (user-created or seeded)
- **categories** — subcategories within a subject (e.g. "Genetika", questions 901–1250)
- **questions** — question text, multiple choice options (a–h), subject + category FK
- **answers** — correct option(s) for each question
- **quiz_sessions** — a quiz attempt: user, settings, score, timestamp
- **quiz_answers** — per-question response within a session

## Auth
Using Supabase Auth. Email + password only. No social login.
Row Level Security (RLS) is enabled — users can only see their own quiz history.
Questions and answers are public (readable by all authenticated users).

## Key Behaviors
- Questions support both `multiple_choice` (pick one) and `multiple_correct` (pick all correct) types
- Categories are derived from question number ranges in the source data
- Users can add their own subjects and questions (stored with their user_id)
- Seeded content has `user_id = NULL` (public/system content)
