"""
api/routes/quiz.py — Endpoints for creating and submitting quiz sessions.
"""

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from typing import Optional
from db import get_supabase
import jwt  # PyJWT — to decode Supabase JWT and get user_id

router = APIRouter()


def get_user_id(authorization: str) -> str:
    """Extract user_id from Supabase JWT token in Authorization header."""
    try:
        token = authorization.replace("Bearer ", "")
        # Decode without verification (Supabase already verified it)
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or missing auth token")


# ── Pydantic models (define the shape of request bodies) ─────────────────────

class CreateSessionRequest(BaseModel):
    subject_id: str
    mode: str                          # "review" or "custom_quiz"
    category_ids: Optional[list[str]] = None
    question_count: Optional[int] = 20
    time_limit_seconds: Optional[int] = None


class SubmitAnswerRequest(BaseModel):
    question_id: str
    selected_options: list[str]


class CompleteSessionRequest(BaseModel):
    time_spent_secs: Optional[int] = None


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post("/sessions")
def create_session(
    body: CreateSessionRequest,
    authorization: str = Header(...),
):
    """Create a new quiz session and return the question set."""
    user_id = get_user_id(authorization)
    sb = get_supabase()

    settings = {
        "question_count": body.question_count,
        "time_limit_seconds": body.time_limit_seconds,
        "category_ids": body.category_ids,
    }

    # Create the session row
    session = sb.table("quiz_sessions").insert({
        "user_id": user_id,
        "subject_id": body.subject_id,
        "settings": settings,
        "mode": body.mode,
    }).execute()

    session_id = session.data[0]["id"]

    # Fetch questions for this session
    query = sb.table("questions").select(
        "id, question_number, question_text, type, options, category_id"
    ).eq("subject_id", body.subject_id)

    if body.category_ids:
        query = query.in_("category_id", body.category_ids)

    result = query.execute()
    questions = result.data

    # Shuffle and limit
    import random
    random.shuffle(questions)
    questions = questions[:body.question_count]

    return {
        "session_id": session_id,
        "questions": questions,
        "settings": settings,
    }


@router.post("/sessions/{session_id}/answers")
def submit_answer(
    session_id: str,
    body: SubmitAnswerRequest,
    authorization: str = Header(...),
):
    """Record a single answer and return whether it was correct."""
    user_id = get_user_id(authorization)
    sb = get_supabase()

    # Verify session belongs to user
    session = sb.table("quiz_sessions") \
        .select("id, user_id") \
        .eq("id", session_id) \
        .single() \
        .execute()

    if not session.data or session.data["user_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not your session")

    # Get correct answer
    question = sb.table("questions") \
        .select("correct_options, type") \
        .eq("id", body.question_id) \
        .single() \
        .execute()

    if not question.data:
        raise HTTPException(status_code=404, detail="Question not found")

    correct = set(question.data["correct_options"])
    selected = set(body.selected_options)
    is_correct = (correct == selected)

    # Save the answer
    sb.table("quiz_answers").insert({
        "session_id": session_id,
        "question_id": body.question_id,
        "selected_options": body.selected_options,
        "is_correct": is_correct,
    }).execute()

    return {
        "is_correct": is_correct,
        "correct_options": question.data["correct_options"],
    }


@router.post("/sessions/{session_id}/complete")
def complete_session(
    session_id: str,
    body: CompleteSessionRequest,
    authorization: str = Header(...),
):
    """Mark session as complete and calculate final score."""
    user_id = get_user_id(authorization)
    sb = get_supabase()

    # Count correct answers for this session
    answers = sb.table("quiz_answers") \
        .select("is_correct") \
        .eq("session_id", session_id) \
        .execute()

    total = len(answers.data)
    score = sum(1 for a in answers.data if a["is_correct"])

    from datetime import datetime, timezone
    sb.table("quiz_sessions").update({
        "score": score,
        "total_questions": total,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "time_spent_secs": body.time_spent_secs,
    }).eq("id", session_id).eq("user_id", user_id).execute()

    return {"score": score, "total_questions": total}
