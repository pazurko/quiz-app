"""
api/routes/questions.py — Endpoints for fetching questions and subjects/categories.
"""

from fastapi import APIRouter, Query, HTTPException, Header
from typing import Optional
from datetime import datetime, timezone
from db import get_supabase
import jwt

router = APIRouter()


def get_user_id(authorization: str) -> str:
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or missing auth token")


@router.get("/subjects")
def list_subjects():
    """Return all subjects (system + user's own — RLS handles filtering)."""
    sb = get_supabase()
    result = sb.table("subjects").select("*, categories(*)").order("created_at").execute()
    return result.data


@router.get("/review-state")
def get_review_state(
    subject_id: str = Query(...),
    authorization: str = Header(...),
):
    user_id = get_user_id(authorization)
    sb = get_supabase()

    # Join via questions table to filter by subject
    result = sb.table("question_review_state") \
        .select("question_id, status, last_reviewed_at, questions!inner(subject_id)") \
        .eq("user_id", user_id) \
        .eq("questions.subject_id", subject_id) \
        .execute()

    return result.data


@router.post("/review-state")
def upsert_review_state(
    body: dict,
    authorization: str = Header(...),
):
    """Upsert a single question's review status."""
    user_id = get_user_id(authorization)
    sb = get_supabase()

    result = sb.table("question_review_state").upsert({
        "user_id": user_id,
        "question_id": body["question_id"],
        "status": body["status"],
        "last_reviewed_at": datetime.now(timezone.utc).isoformat(),
    }, on_conflict="user_id,question_id").execute()

    return result.data


@router.post("/review-state/reset")
def reset_review_state(
    body: dict,
    authorization: str = Header(...),
):
    """Delete review state rows for a subject (optionally filtered by category), resetting to unreviewed."""
    user_id = get_user_id(authorization)
    sb = get_supabase()

    subject_id = body.get("subject_id")
    category_id = body.get("category_id")

    q_query = sb.table("questions").select("id").eq("subject_id", subject_id).limit(5000)
    if category_id:
        q_query = q_query.eq("category_id", category_id)
    q_result = q_query.execute()
    question_ids = [q["id"] for q in q_result.data]

    if question_ids:
        # Delete in batches of 100 to avoid Supabase URL length limits
        batch_size = 100
        for i in range(0, len(question_ids), batch_size):
            batch = question_ids[i:i + batch_size]
            sb.table("question_review_state") \
                .delete() \
                .eq("user_id", user_id) \
                .in_("question_id", batch) \
                .execute()

    return {"reset": len(question_ids)}


@router.get("/")
def list_questions(
    subject_id: Optional[str] = Query(None),
    category_id: Optional[str] = Query(None),
    limit: int = Query(50, le=500),
    offset: int = Query(0),
    random: bool = Query(False),
):
    """
    Fetch questions with optional filters.
    random=true returns a random sample (used for custom quizzes).
    """
    sb = get_supabase()

    query = sb.table("questions").select(
        "id, question_number, question_text, type, options, correct_options, category_id, subject_id"
    )

    if subject_id:
        query = query.eq("subject_id", subject_id)
    if category_id:
        query = query.eq("category_id", category_id)

    if random:
        # Supabase doesn't support ORDER BY RANDOM() directly via client,
        # so we fetch more and shuffle in Python (acceptable for quiz sizes)
        result = query.limit(limit * 3).execute()
        import random as rnd
        data = result.data
        rnd.shuffle(data)
        return data[:limit]

    result = query.range(offset, offset + limit - 1).execute()
    return result.data


@router.get("/{question_id}/answer")
def get_answer(question_id: str):
    """Return the correct options for a question (called after user submits answer)."""
    sb = get_supabase()
    result = sb.table("questions") \
        .select("id, correct_options, type") \
        .eq("id", question_id) \
        .single() \
        .execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Question not found")

    return result.data
