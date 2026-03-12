"""
api/index.py — FastAPI entry point for Vercel serverless deployment.

Vercel will run this file as a Python serverless function.
All routes are prefixed with /api.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import questions, quiz, history

app = FastAPI(title="Quiz App API", version="1.0.0")

# Allow requests from the Vue frontend (adjust origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "https://quiz-app.mazur.page",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(questions.router, prefix="/api/questions", tags=["questions"])
app.include_router(quiz.router, prefix="/api/quiz", tags=["quiz"])
app.include_router(history.router, prefix="/api/history", tags=["history"])


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
