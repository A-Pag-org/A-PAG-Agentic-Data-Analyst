# AI Data Analytics Platform 📊

AI-powered data analytics platform with natural language queries and intelligent visualizations.

## ✨ Features

- 🤖 **Natural Language Queries** - Ask questions in plain English
- 📊 **Automatic Visualizations** - AI generates appropriate charts and graphs
- 🔮 **Forecasting** - Predict future trends from your data
- 📁 **Multiple Data Formats** - Support for CSV, Excel, and JSON
- 💡 **Smart Insights** - AI discovers patterns and anomalies
- 📤 **Export Results** - Download charts and reports

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- Supabase account ([Sign up free](https://supabase.com/))
- OpenAI API key ([Get your key](https://platform.openai.com/api-keys))

### 1. Install Dependencies

```bash
# Frontend
cd frontend
npm install

# Backend
cd ../backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Backend - Copy and edit .env
cp .env.example .env
# Add your Supabase and OpenAI credentials

# Frontend - Copy and edit .env.local  
cp frontend/.env.local.example frontend/.env.local
# Add your Supabase URL and keys
```

### 3. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 4. Access the App

Open [http://localhost:3000](http://localhost:3000) in your browser 🎉

**📖 For detailed setup instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md)**

## 📖 How to Use

### Step 1: Upload Your Data
1. Go to the **"Upload Data"** tab
2. Select a CSV, Excel, or JSON file
3. Click "Upload Data"

### Step 2: Ask Questions
1. Go to the **"Analyze Data"** tab  
2. Type your question (e.g., "What are the top 5 products by revenue?")
3. Enable visualizations and forecasting (optional)
4. Click "Analyze Data"

### Step 3: Get Insights
- View AI-generated answers
- Explore interactive visualizations
- Review discovered insights
- Export results

## 💬 Example Queries

```
✅ What are my top selling products this month?
✅ Show me sales trends over the last year
✅ Which customers have the highest lifetime value?
✅ Compare Q1 and Q2 performance
✅ Predict next quarter's revenue
✅ Find anomalies in the transaction data
```

## 📁 Project Structure

```
.
├── backend/          # FastAPI backend with AI agents
├── frontend/         # Next.js frontend with Chakra UI
├── supabase/         # Database migrations
├── .env.example      # Backend environment template
└── SETUP_GUIDE.md    # Detailed setup instructions
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

### Required Environment Variables

#### Backend (.env)
Copy `.env.example` to `.env` in the root directory and configure:

**Required:**
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_ANON_KEY` - Supabase anonymous key
- `SUPABASE_SERVICE_ROLE_KEY` - Supabase service role key
- `OPENAI_API_KEY` - Your OpenAI API key
- `DATABASE_URL` - Supabase Postgres connection string

**Optional:**
- `REDIS_URL` - Redis cache URL (for production caching)
- `COHERE_API_KEY` - If using Cohere reranker
- See `.env.example` for all configuration options

#### Frontend (.env.local)
Copy `frontend/.env.local.example` to `frontend/.env.local` and configure:

**Required:**
- `NEXT_PUBLIC_SUPABASE_URL` - Your Supabase project URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Supabase anonymous key

### Deployment (Vercel)
When deploying to Vercel, set these environment variables in your project settings:
- All frontend variables (NEXT_PUBLIC_*)
- Backend variables are typically set separately if using a separate backend deployment

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
