from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    environment: str = Field(default="development", alias="ENVIRONMENT")
    api_prefix: str = Field(default="/api/v1", alias="API_PREFIX")
    secret_key: str = Field(default="change-me", alias="SECRET_KEY")

    # Auth
    auth_bearer_token: str | None = Field(default=None, alias="AUTH_BEARER_TOKEN")

    # Supabase
    supabase_url: str | None = Field(default=None, alias="SUPABASE_URL")
    supabase_key: str | None = Field(default=None, alias="SUPABASE_ANON_KEY")
    supabase_service_key: str | None = Field(default=None, alias="SUPABASE_SERVICE_ROLE_KEY")

    # OpenAI
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")

    # Vector DB / Embeddings
    chroma_persist_dir: str = Field(default="chroma_index", alias="CHROMA_PERSIST_DIR")
    embedding_model: str = Field(default="text-embedding-3-large", alias="EMBEDDING_MODEL")

settings = Settings()
