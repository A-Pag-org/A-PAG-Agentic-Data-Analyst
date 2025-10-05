from typing import Optional
from supabase import create_client, Client
from ..core.config import settings

_supabase_client: Optional[Client] = None
_supabase_service_client: Optional[Client] = None

def get_supabase_client() -> Client:
    global _supabase_client
    if _supabase_client is None:
        if not settings.supabase_url or not settings.supabase_key:
            raise RuntimeError("Supabase not configured. Set SUPABASE_URL and SUPABASE_ANON_KEY.")
        _supabase_client = create_client(settings.supabase_url, settings.supabase_key)
    return _supabase_client

def get_supabase_service_client() -> Client:
    """Returns a Supabase client using the service role key for server-side tasks.

    Falls back to anon key if service key is not provided.
    """
    global _supabase_service_client
    if _supabase_service_client is None:
        key = settings.supabase_service_key or settings.supabase_key
        if not settings.supabase_url or not key:
            raise RuntimeError(
                "Supabase not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_ANON_KEY)."
            )
        _supabase_service_client = create_client(settings.supabase_url, key)
    return _supabase_service_client
