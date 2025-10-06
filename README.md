# Getting Started

This is a full-stack application with a FastAPI backend and Next.js frontend.

## Quick Start

### Option 1: Run Everything (Recommended)

```bash
# Install frontend dependencies
npm install

# Run the frontend development server
npm run dev
```

The frontend will be available at [http://localhost:3000](http://localhost:3000)

### Option 2: Run Backend and Frontend Separately

#### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend API will be available at [http://localhost:8000](http://localhost:8000)
- API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

Frontend will be available at [http://localhost:3000](http://localhost:3000)

## Environment Variables

You'll need to set up environment variables for:
- Supabase configuration
- OpenAI API keys
- Any other service credentials

Create a `.env.local` file in the `frontend` directory and a `.env` file in the `backend` directory with the necessary credentials.

## Project Structure

- `backend/` - FastAPI backend with AI agents and data processing
- `frontend/` - Next.js frontend with Chakra UI
- `supabase/` - Database migrations

## Tech Stack

**Backend:**
- FastAPI
- LlamaIndex & LangChain
- OpenAI
- PostgreSQL (via Supabase)
- ChromaDB

**Frontend:**
- Next.js 15
- React 19
- Chakra UI
- TypeScript
