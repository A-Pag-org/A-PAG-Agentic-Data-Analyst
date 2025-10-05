from typing import Optional
from supabase import create_client, Client
from ..core.config import settings

_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    global _supabase_client
    if _supabase_client is None:
        if not settings.supabase_url or not settings.supabase_key:
            raise RuntimeError("Supabase not configured. Set SUPABASE_URL and SUPABASE_ANON_KEY.")
        _supabase_client = create_client(settings.supabase_url, settings.supabase_key)
    return _supabase_client
