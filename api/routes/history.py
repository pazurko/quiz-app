"""
api/routes/history.py — Endpoints for quiz history.
"""

from fastapi import APIRouter, Header, Query
from db import get_supabase
import jwt

router = APIRouter()


def get_user_id(authorization: str) -> str:
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload["sub"]
    except Exception:
        from fastapi import HTTPException
        raise HTTPException(status_code=401, detail="Invalid or missing auth token")


@router.get("/")
def get_history(
    authorization: str = Header(...),
    limit: int = Query(20, le=100),
    offset: int = Query(0),
):
    """Return the user's quiz history, most recent first."""
    user_id = get_user_id(authorization)
    sb = get_supabase()

    result = sb.table("quiz_sessions") \
        .select("*, subjects(name)") \
        .eq("user_id", user_id) \
        .not_.is_("completed_at", "null") \
        .order("completed_at", desc=True) \
        .range(offset, offset + limit - 1) \
        .execute()

    return result.data


@router.get("/{session_id}")
def get_session_detail(
    session_id: str,
    authorization: str = Header(...),
):
    """Return detailed results for a specific quiz session."""
    user_id = get_user_id(authorization)
    sb = get_supabase()

    session = sb.table("quiz_sessions") \
        .select("*") \
        .eq("id", session_id) \
        .eq("user_id", user_id) \
        .single() \
        .execute()

    answers = sb.table("quiz_answers") \
        .select("*, questions(question_text, options, correct_options, type)") \
        .eq("session_id", session_id) \
        .execute()

    return {
        "session": session.data,
        "answers": answers.data,
    }

@router.delete("/")
def clear_history(authorization: str = Header(...)):
    """Delete all quiz sessions for the current user."""
    user_id = get_user_id(authorization)
    sb = get_supabase()
    sb.table("quiz_sessions").delete().eq("user_id", user_id).execute()
    return {"cleared": True}