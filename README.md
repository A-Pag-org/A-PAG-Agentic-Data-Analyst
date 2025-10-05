# RAG Data Analyst

> Advanced RAG-powered data analysis platform with agentic AI workflows for comprehensive insights, visualizations, and forecasting.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Frontend CI](https://github.com/yourusername/rag-data-analyst/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/yourusername/rag-data-analyst/actions/workflows/frontend-ci.yml)
[![Backend CI](https://github.com/yourusername/rag-data-analyst/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/yourusername/rag-data-analyst/actions/workflows/backend-ci.yml)

## ✨ Features

- 🤖 **Advanced RAG**: Hybrid search combining vector and keyword capabilities
- 🔄 **Agentic AI**: Multi-step analysis with intelligent workflows powered by LangChain
- 📊 **Analytics & Forecasting**: Time series forecasting with Prophet and scikit-learn
- 🗺️ **GIS Mapping**: Interactive geospatial visualizations with React-Leaflet
- 📈 **Rich Visualizations**: Beautiful charts with Recharts and D3.js
- 🎨 **Modern UI**: Responsive design with Chakra UI and dark mode support
- ⚡ **High Performance**: Built on Next.js 14 and FastAPI with serverless deployment
- 🔒 **Single-User Demo**: Optimized for testing and demonstration

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ & pnpm 8+
- Python 3.12+
- Docker & Docker Compose
- OpenAI API key

### Installation

1. **Clone and setup**:
```bash
git clone <repository-url>
cd rag-data-analyst
```

2. **Start infrastructure**:
```bash
docker-compose up -d
```

3. **Configure environment**:
```bash
# Frontend
cp frontend/.env.example frontend/.env
# Add your settings

# Backend
cp backend/.env.example backend/.env
# Add your OPENAI_API_KEY
```

4. **Install dependencies**:
```bash
pnpm install
cd backend && poetry install && cd ..
```

5. **Start development servers**:
```bash
# Frontend (http://localhost:3000)
pnpm --filter @rag-data-analyst/frontend dev

# Backend (http://localhost:8000)
cd backend && poetry run uvicorn app.main:app --reload
```

6. **Visit the app**:
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/api/v1/docs

For detailed setup instructions, see [docs/SETUP.md](./docs/SETUP.md)

## 📁 Project Structure

```
rag-data-analyst/
├── frontend/             # Next.js 14 application
│   ├── src/
│   │   ├── app/         # App router pages
│   │   ├── components/  # React components
│   │   ├── lib/         # Utilities and API client
│   │   ├── hooks/       # Custom React hooks
│   │   ├── store/       # Zustand state management
│   │   └── styles/      # Chakra UI theme
│   └── package.json
│
├── backend/             # FastAPI application
│   ├── app/
│   │   ├── main.py      # Application entry
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Core configuration
│   │   ├── services/    # Business logic (Phase 2)
│   │   │   ├── rag/     # RAG pipeline
│   │   │   ├── agent/   # Agentic workflows
│   │   │   └── analytics/ # Data analytics
│   │   └── models/      # Database models (Phase 2)
│   └── pyproject.toml
│
├── shared/              # Shared TypeScript types
│   ├── src/
│   │   ├── types/       # Common types
│   │   ├── api/         # API schemas
│   │   └── constants/   # Shared constants
│   └── package.json
│
├── docker/              # Docker configurations
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── init-scripts/
│
├── .github/
│   └── workflows/       # CI/CD pipelines
│       ├── frontend-ci.yml
│       ├── backend-ci.yml
│       ├── deploy-staging.yml
│       └── deploy-production.yml
│
├── docs/                # Documentation
│   ├── SETUP.md        # Detailed setup guide
│   ├── ARCHITECTURE.md # System architecture
│   └── API.md          # API documentation
│
├── docker-compose.yml   # Local development services
├── turbo.json          # Turborepo configuration
└── package.json        # Root package.json
```

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **UI**: Chakra UI v2, Framer Motion
- **State**: Zustand, SWR
- **Charts**: Recharts, D3.js
- **Maps**: React-Leaflet

### Backend
- **Framework**: FastAPI (Python 3.12)
- **RAG**: LlamaIndex, LangChain
- **LLM**: OpenAI GPT-4o
- **Embeddings**: OpenAI text-embedding-3-large
- **Vector DB**: ChromaDB, Supabase pgvector
- **Analytics**: Prophet, scikit-learn, Pandas

### Infrastructure
- **Database**: PostgreSQL with pgvector
- **Storage**: Supabase Storage
- **Deployment**: Vercel (Frontend), Railway (Backend)
- **CI/CD**: GitHub Actions

## 📚 Documentation

- [Setup Guide](./docs/SETUP.md) - Detailed installation and setup
- [Architecture](./docs/ARCHITECTURE.md) - System design and data flow
- [API Reference](./docs/API.md) - Complete API documentation

## 🧪 Development

### Code Quality

```bash
# Lint and format
pnpm lint
pnpm format

# Type check
pnpm type-check

# Run tests
pnpm test
```

### Pre-commit Hooks

Pre-commit hooks are set up with Husky to:
- Lint and format code automatically
- Type check TypeScript
- Validate commit messages (Conventional Commits)

## 🚢 Deployment

### Vercel (Frontend)

This project is configured for Vercel deployment with `vercel.json`. To deploy:

1. **Connect your repository to Vercel**:
   - Import your project on [vercel.com](https://vercel.com)
   - Vercel will auto-detect the Next.js framework

2. **Configure environment variables** in Vercel dashboard:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-api.com
   NEXT_PUBLIC_APP_NAME=RAG Data Analyst
   NEXT_PUBLIC_APP_VERSION=0.1.0
   NEXT_PUBLIC_ENABLE_GIS=true
   NEXT_PUBLIC_ENABLE_FORECASTING=true
   ```

3. **Build settings** (handled by vercel.json):
   - Build Command: `pnpm turbo run build --filter=@rag-data-analyst/frontend`
   - Output Directory: `frontend/.next`
   - Install Command: `pnpm install`

### Railway (Backend)

Deploy the backend separately on Railway or your preferred platform.

### CI/CD

- **Staging**: Automatically deployed on push to `develop` branch
- **Production**: Deployed on push to `main` branch or version tags

See [docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md) for details.

## 📊 Roadmap

### Phase 1: Foundation ✅ (Current)
- [x] Project setup and repository structure
- [x] Frontend with Next.js and Chakra UI
- [x] Backend with FastAPI
- [x] Docker development environment
- [x] CI/CD pipelines

### Phase 2: Core Features (Weeks 2-3)
- [ ] RAG pipeline with LlamaIndex
- [ ] Vector store integration (ChromaDB + pgvector)
- [ ] File upload and processing
- [ ] Basic chat interface
- [ ] Data visualization components

### Phase 3: Advanced Features (Weeks 4-5)
- [ ] Agentic workflows with LangChain
- [ ] Time series forecasting
- [ ] Advanced analytics
- [ ] GIS mapping
- [ ] Export capabilities

### Phase 4: Polish & Deploy (Week 6)
- [ ] Performance optimization
- [ ] Error handling and validation
- [ ] User documentation
- [ ] Production deployment
- [ ] Monitoring and logging

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](./docs/CONTRIBUTING.md) first.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 🙏 Acknowledgments

- [LlamaIndex](https://www.llamaindex.ai/) for RAG capabilities
- [LangChain](https://www.langchain.com/) for agentic workflows
- [OpenAI](https://openai.com/) for LLM and embeddings
- [Supabase](https://supabase.com/) for backend infrastructure
- [Vercel](https://vercel.com/) for frontend hosting

---

Built with ❤️ using Next.js, FastAPI, and AI