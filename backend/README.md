# RAG Data Analyst - Backend

FastAPI backend for the RAG-powered data analysis platform.

## Setup

### Prerequisites

- Python 3.12+
- Poetry
- PostgreSQL with pgvector extension
- ChromaDB (optional for development)

### Installation

1. Install dependencies:
```bash
poetry install
```

2. Copy environment variables:
```bash
cp .env.example .env
```

3. Edit `.env` with your configuration (OpenAI API key, database URL, etc.)

4. Run database migrations (coming soon):
```bash
poetry run alembic upgrade head
```

### Development

Run the development server:
```bash
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or use the convenience script:
```bash
poetry run python -m app.main
```

Access the API documentation:
- Swagger UI: http://localhost:8000/api/v1/docs
- ReDoc: http://localhost:8000/api/v1/redoc

### Code Quality

Format code:
```bash
poetry run black app/
```

Lint code:
```bash
poetry run ruff check app/
```

Type check:
```bash
poetry run mypy app/
```

### Testing

Run tests:
```bash
poetry run pytest
```

With coverage:
```bash
poetry run pytest --cov=app --cov-report=html
```

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── core/                # Core functionality
│   │   ├── config.py        # Settings and configuration
│   │   └── security.py      # Authentication (coming soon)
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/   # API endpoints
│   │       └── __init__.py
│   ├── services/            # Business logic (coming soon)
│   │   ├── rag/             # RAG pipeline
│   │   ├── agent/           # Agentic workflows
│   │   └── analytics/       # Data analytics
│   ├── models/              # Database models (coming soon)
│   └── schemas/             # Pydantic schemas (coming soon)
├── tests/                   # Test suite
├── alembic/                 # Database migrations
├── pyproject.toml           # Poetry configuration
└── README.md
```

## API Endpoints

### Health
- `GET /health` - Health check

### Data
- `POST /api/v1/data/upload` - Upload data files
- `GET /api/v1/data/sources` - List data sources
- `DELETE /api/v1/data/sources/{id}` - Delete data source

### Chat
- `POST /api/v1/chat` - RAG-powered chat

### Analysis
- `POST /api/v1/analysis/forecast` - Time series forecasting
- `POST /api/v1/analysis/analyze` - General data analysis

## Next Steps

- [ ] Implement RAG pipeline with LlamaIndex
- [ ] Set up vector store (ChromaDB + pgvector)
- [ ] Implement agentic workflows with LangChain
- [ ] Add authentication middleware
- [ ] Implement data processing pipeline
- [ ] Add forecasting with Prophet
- [ ] Create database models and migrations