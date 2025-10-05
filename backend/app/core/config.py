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
    # Chroma backend: "memory" (EphemeralClient) or "persistent" (PersistentClient)
    chroma_backend: str = Field(default="memory", alias="CHROMA_BACKEND")
    # Dataset scope for collections: "per_user" or "per_dataset"
    chroma_dataset_scope: str = Field(default="per_user", alias="CHROMA_DATASET_SCOPE")
    # Supabase Storage bucket for persisting collections
    chroma_supabase_bucket: str = Field(default="chroma-collections", alias="CHROMA_SUPABASE_BUCKET")
    # Autosave collections to Supabase after mutations and attempt auto-load on first access
    chroma_autosave: bool = Field(default=True, alias="CHROMA_AUTOSAVE")
    embedding_model: str = Field(default="text-embedding-3-large", alias="EMBEDDING_MODEL")

    # Database (for LlamaIndex Postgres/pgvector)
    database_url: str | None = Field(default=None, alias="DATABASE_URL")
    pgvector_schema: str = Field(default="public", alias="PGVECTOR_SCHEMA")
    pgvector_table: str = Field(default="llamaindex_embeddings", alias="PGVECTOR_TABLE")
    embedding_dim: int = Field(default=3072, alias="EMBEDDING_DIM")

    # Chunking / splitting
    chunk_size: int = Field(default=512, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=50, alias="CHUNK_OVERLAP")
    use_semantic_chunking: bool = Field(default=True, alias="USE_SEMANTIC_CHUNKING")

    # Embedding cache
    embedding_cache_path: str = Field(default="cache/embeddings.sqlite3", alias="EMBEDDING_CACHE_PATH")

    # Retrieval / reranking
    retriever_top_k: int = Field(default=8, alias="RETRIEVER_TOP_K")
    reranker_top_n: int = Field(default=5, alias="RERANKER_TOP_N")
    reranker_model: str = Field(default="cross-encoder/ms-marco-MiniLM-L-6-v2", alias="RERANKER_MODEL")
    # Reranker provider: "local" (SentenceTransformer) or "cohere"
    reranker_provider: str = Field(default="local", alias="RERANKER_PROVIDER")
    # Cohere configuration (used when reranker_provider == "cohere")
    cohere_api_key: str | None = Field(default=None, alias="COHERE_API_KEY")
    cohere_reranker_model: str = Field(default="rerank-3.5", alias="COHERE_RERANKER_MODEL")

    # Query decomposition
    query_decomposition_enabled: bool = Field(default=True, alias="QUERY_DECOMPOSITION_ENABLED")
    query_decomposition_max_sub_queries: int = Field(default=4, alias="QUERY_DECOMPOSITION_MAX_SUB_QUERIES")
    query_decomposition_context_limit: int = Field(default=12, alias="QUERY_DECOMPOSITION_CONTEXT_LIMIT")

    # Conversation history
    conversation_history_limit: int = Field(default=6, alias="CONVERSATION_HISTORY_LIMIT")

settings = Settings()
