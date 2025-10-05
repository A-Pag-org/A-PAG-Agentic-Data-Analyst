-- Initialize pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create initial schema (will be managed by Alembic later)
CREATE SCHEMA IF NOT EXISTS public;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE rag_data_analyst TO postgres;
GRANT ALL PRIVILEGES ON SCHEMA public TO postgres;