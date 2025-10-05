# Setup Guide

This guide will help you set up the RAG Data Analyst platform for local development.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** 18+ and **pnpm** 8+
- **Python** 3.12+
- **Poetry** 1.7+
- **Docker** and **Docker Compose** (for local services)
- **Git**

### Optional Tools
- **pyenv** or **asdf** (for Python version management)
- **nvm** (for Node version management)

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd rag-data-analyst
```

### 2. Set Up Environment Variables

#### Root Level
```bash
cp .env.example .env
```

#### Frontend
```bash
cp frontend/.env.example frontend/.env
```

Edit `frontend/.env`:
- Set `NEXT_PUBLIC_API_URL` to your backend URL (default: `http://localhost:8000`)
- Set `DEMO_PASSWORD` for single-user authentication

#### Backend
```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:
- **Required**: Set your `OPENAI_API_KEY`
- Set `DEMO_PASSWORD` (must match frontend)
- Configure `DATABASE_URL` if not using Docker
- Configure `SUPABASE_*` variables for production

### 3. Start Infrastructure Services

Start PostgreSQL (with pgvector) and ChromaDB:

```bash
docker-compose up -d
```

Verify services are running:
```bash
docker-compose ps
```

You should see:
- `rag_postgres` on port 5432
- `rag_chromadb` on port 8001

### 4. Install Dependencies

#### Install all dependencies (recommended)
```bash
pnpm install
```

This will install dependencies for frontend and shared packages using the monorepo workspace configuration.

#### Backend dependencies
```bash
cd backend
poetry install
cd ..
```

### 5. Build Shared Package

The shared package contains TypeScript types used by the frontend:

```bash
pnpm --filter @rag-data-analyst/shared build
```

### 6. Run Database Migrations

```bash
cd backend
poetry run alembic upgrade head
cd ..
```

*Note: Database migrations coming soon in Phase 2*

### 7. Start Development Servers

#### Option A: Start all services with Turbo
```bash
pnpm dev
```

This will start:
- Frontend on `http://localhost:3000`
- Backend needs to be started separately (see below)

#### Option B: Start services individually

**Frontend:**
```bash
pnpm --filter @rag-data-analyst/frontend dev
```

**Backend:**
```bash
cd backend
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 8. Verify Installation

- Frontend: http://localhost:3000
- Backend API Docs: http://localhost:8000/api/v1/docs
- Backend Health: http://localhost:8000/health

## Development Workflow

### Code Quality

Run linting and formatting:

```bash
# Frontend
pnpm --filter @rag-data-analyst/frontend lint
pnpm --filter @rag-data-analyst/frontend format

# Backend
cd backend
poetry run ruff check app/
poetry run black app/
poetry run mypy app/
```

### Pre-commit Hooks

Pre-commit hooks are automatically installed via Husky. They will:
- Lint and format code
- Type check TypeScript
- Validate commit messages

To skip hooks (not recommended):
```bash
git commit --no-verify
```

### Testing

```bash
# Frontend tests (coming soon)
pnpm --filter @rag-data-analyst/frontend test

# Backend tests
cd backend
poetry run pytest
```

## Docker Development

If you prefer to run everything in Docker:

1. Uncomment the `backend` and `frontend` services in `docker-compose.yml`
2. Run:
```bash
docker-compose up
```

## Troubleshooting

### Port Already in Use

If ports 3000, 8000, 5432, or 8001 are in use:

**Find and kill the process:**
```bash
# On macOS/Linux
lsof -ti:3000 | xargs kill -9

# Or change the ports in your configuration
```

### Database Connection Issues

Ensure PostgreSQL is running:
```bash
docker-compose logs postgres
```

Test connection:
```bash
docker-compose exec postgres psql -U postgres -d rag_data_analyst -c "SELECT version();"
```

### ChromaDB Connection Issues

Check ChromaDB logs:
```bash
docker-compose logs chromadb
```

Test connection:
```bash
curl http://localhost:8001/api/v1/heartbeat
```

### Poetry/pnpm Installation Issues

**Poetry:**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**pnpm:**
```bash
npm install -g pnpm
```

### OpenAI API Issues

Verify your API key:
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

## Next Steps

- [Architecture Overview](./ARCHITECTURE.md)
- [API Documentation](./API.md)
- [Contributing Guide](./CONTRIBUTING.md)
- [Deployment Guide](./DEPLOYMENT.md)