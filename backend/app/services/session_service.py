from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..core.config import settings
from .supabase_client import get_supabase_service_client


class SessionService:
    """Supabase-backed conversation session storage.

    Stores the rolling conversation in analysis_sessions.artifacts->history
    as a list of {role, content, ...}. Each assistant turn may include sources.
    """

    @staticmethod
    def load_history(*, session_id: Optional[str], limit: Optional[int] = None) -> List[Dict[str, Any]]:
        if not session_id:
            return []
        supabase = get_supabase_service_client()
        resp = (
            supabase
            .table("analysis_sessions")
            .select("id, artifacts")
            .eq("id", session_id)
            .execute()
        )
        data = getattr(resp, "data", None) or []
        if not data:
            return []
        artifacts = data[0].get("artifacts") or {}
        history: List[Dict[str, Any]] = artifacts.get("history") or []
        max_items = limit if limit is not None else int(getattr(settings, "conversation_history_limit", 6))
        if max_items <= 0:
            return []
        return history[-max_items:]

    @staticmethod
    def _truncate_history(history: List[Dict[str, Any]], *, max_items: int) -> List[Dict[str, Any]]:
        if max_items <= 0:
            return []
        if len(history) <= max_items:
            return history
        return history[-max_items:]

    @staticmethod
    def create_session(
        *,
        user_id: str,
        user_turn: Dict[str, Any],
        assistant_turn: Dict[str, Any],
        sources: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        supabase = get_supabase_service_client()
        history: List[Dict[str, Any]] = [user_turn, {**assistant_turn, "sources": sources or []}]
        artifacts: Dict[str, Any] = {
            "history": SessionService._truncate_history(
                history,
                max_items=int(getattr(settings, "conversation_history_limit", 6)),
            )
        }
        resp = (
            supabase
            .table("analysis_sessions")
            .insert({
                "user_id": user_id,
                "query": user_turn.get("content", ""),
                "response": assistant_turn,
                "artifacts": artifacts,
            })
            .execute()
        )
        rows = getattr(resp, "data", None) or []
        if not rows:
            raise RuntimeError("Failed to create analysis session")
        return rows[0]["id"]

    @staticmethod
    def append_turn(
        *,
        session_id: str,
        user_turn: Dict[str, Any],
        assistant_turn: Dict[str, Any],
        sources: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        supabase = get_supabase_service_client()
        # Load existing history
        existing_history = SessionService.load_history(session_id=session_id)
        updated_history = existing_history + [user_turn, {**assistant_turn, "sources": sources or []}]
        truncated = SessionService._truncate_history(
            updated_history,
            max_items=int(getattr(settings, "conversation_history_limit", 6)),
        )
        artifacts: Dict[str, Any] = {"history": truncated}

        (
            supabase
            .table("analysis_sessions")
            .update({
                "query": user_turn.get("content", ""),
                "response": assistant_turn,
                "artifacts": artifacts,
            })
            .eq("id", session_id)
            .execute()
        )
