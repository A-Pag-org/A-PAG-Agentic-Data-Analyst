# Architecture Overview

## System Architecture

The RAG Data Analyst platform is built as a modern, serverless-first application with clear separation between frontend, backend, and shared components.

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│                  Next.js 14 + Chakra UI                      │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │  Dashboard   │  │  Chat UI     │  │  Visualizations │   │
│  │  & Upload    │  │  & RAG       │  │  & Analytics    │   │
│  └──────────────┘  └──────────────┘  └─────────────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │ REST API
                          │
┌─────────────────────────┴───────────────────────────────────┐
│                      Backend API                             │
│                     FastAPI + Python                         │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐   │
│  │   RAG        │  │   Agent      │  │   Analytics     │   │
│  │   Pipeline   │  │   Workflows  │  │   & Forecast    │   │
│  └──────┬───────┘  └──────┬───────┘  └────────┬────────┘   │
│         │                 │                    │            │
└─────────┼─────────────────┼────────────────────┼────────────┘
          │                 │                    │
    ┌─────┴─────┐     ┌────┴─────┐        ┌────┴────┐
    │  Vector   │     │   LLM    │        │  Data   │
    │  Stores   │     │  (GPT-4) │        │ Process │
    └───────────┘     └──────────┘        └─────────┘
         │
    ┌────┴────┐
    │ChromaDB │
    │pgvector │
    └─────────┘
```

## Technology Stack

### Frontend Layer

**Framework**: Next.js 14 with App Router
- Server-side rendering (SSR)
- API routes for BFF pattern
- Optimized for Vercel deployment
- Static optimization where possible

**UI/UX**:
- Chakra UI v2 for component library
- Framer Motion for animations
- React Icons for iconography
- Light/Dark mode support

**State Management**:
- Zustand for global state
- SWR for data fetching and caching
- React Context for theme/auth

**Data Visualization**:
- Recharts for standard charts
- D3.js for custom visualizations
- React-Leaflet for GIS mapping

### Backend Layer

**Framework**: FastAPI
- Async/await for high performance
- Automatic OpenAPI documentation
- Type safety with Pydantic
- WebSocket support for real-time updates

**RAG Pipeline**:
- **LlamaIndex**: Primary RAG framework
  - Document loading and parsing
  - Text chunking and preprocessing
  - Query engine and retrieval
  - Response synthesis

- **LangChain**: Agentic workflows
  - Multi-step reasoning
  - Tool integration
  - Chain-of-thought prompting
  - Memory management

**Vector Storage**:
- **ChromaDB**: Fast vector similarity search
- **Supabase pgvector**: Persistent PostgreSQL storage
- Hybrid search (vector + keyword)

**LLM Integration**:
- OpenAI GPT-4o for generation
- OpenAI text-embedding-3-large for embeddings
- Fallback mechanisms for rate limits

**Analytics**:
- Prophet for time series forecasting
- scikit-learn for ML tasks
- Pandas/NumPy for data processing
- GeoPandas for spatial analysis

### Data Layer

**Primary Database**: Supabase (PostgreSQL)
- User data (single user for demo)
- Data source metadata
- Query history
- Vector embeddings (via pgvector)

**Vector Storage**:
- ChromaDB for development
- pgvector for production
- Hybrid approach for optimal performance

**File Storage**: Supabase Storage
- Uploaded datasets (CSV, Excel)
- Generated reports
- ChromaDB persistence

## Key Components

### 1. RAG Pipeline

```
User Query
    ↓
Query Processing (LlamaIndex)
    ↓
Vector Retrieval (ChromaDB/pgvector)
    ↓
Context Assembly
    ↓
LLM Generation (GPT-4)
    ↓
Response + Sources
```

**Features**:
- Semantic search with embeddings
- Keyword fallback
- Re-ranking results
- Source attribution
- Streaming responses

### 2. Agentic Workflows (LangChain)

Multi-step analysis tasks:
1. **Planning**: Break down complex queries
2. **Tool Selection**: Choose appropriate tools
3. **Execution**: Run analysis steps
4. **Synthesis**: Combine results
5. **Validation**: Verify outputs

**Available Tools**:
- Data querying (SQL, Pandas)
- Statistical analysis
- Visualization generation
- Forecasting models
- Web search (future)

### 3. Data Processing Pipeline

```
Upload → Validate → Parse → Transform → Embed → Store
```

**Supported Formats**:
- CSV/Excel: Pandas processing
- JSON: Direct parsing
- PDF: Text extraction (future)
- APIs: Scheduled fetching (future)

### 4. Analytics Engine

**Descriptive Statistics**:
- Summary statistics
- Distribution analysis
- Correlation matrices
- Missing data analysis

**Predictive Analytics**:
- Time series forecasting (Prophet)
- Regression analysis
- Classification
- Clustering

**Visualization**:
- Automatic chart selection
- Interactive dashboards
- Geospatial mapping
- Export capabilities

## Data Flow

### Upload Flow
```
1. User uploads file → Frontend
2. File validation → Backend
3. Parsing (Pandas) → Backend
4. Chunking → Backend
5. Embedding generation → OpenAI
6. Storage → ChromaDB + PostgreSQL
7. Confirmation → Frontend
```

### Query Flow
```
1. User asks question → Frontend
2. Query processing → Backend
3. Vector search → ChromaDB
4. Context retrieval → Backend
5. LLM completion → OpenAI
6. Response formatting → Backend
7. Display with sources → Frontend
```

### Analysis Flow
```
1. User requests analysis → Frontend
2. Data fetching → Backend
3. Processing (Pandas/Prophet) → Backend
4. Visualization generation → Backend
5. Insights extraction (LLM) → OpenAI
6. Results display → Frontend
```

## Security Considerations

### Single-User Model
- Simple password authentication
- Environment-based secrets
- No complex user management

### API Security
- API key authentication
- Rate limiting
- CORS configuration
- Input validation

### Data Privacy
- No data leaves the system (except OpenAI API)
- Secure storage in Supabase
- Encrypted connections (HTTPS)

## Scalability

### Current (Single User)
- Optimized for demo/testing
- Local ChromaDB
- Minimal caching

### Future (Multi-User)
- User isolation
- Distributed vector stores
- CDN for static assets
- Horizontal backend scaling
- Connection pooling

## Deployment

### Vercel (Frontend)
- Automatic deployments
- Edge functions
- Global CDN
- Preview deployments

### Railway/Fly.io (Backend)
- Containerized deployment
- Auto-scaling
- Managed PostgreSQL
- Persistent volumes for ChromaDB

### Supabase (Data)
- Managed PostgreSQL
- Real-time subscriptions
- Authentication (future)
- File storage

## Monitoring

### Application
- Health check endpoints
- Performance metrics
- Error tracking (Sentry)
- Usage analytics

### Infrastructure
- Uptime monitoring
- Resource utilization
- Database performance
- API latency

## Next Steps

- [Setup Guide](./SETUP.md)
- [API Documentation](./API.md)
- [Development Guide](./DEVELOPMENT.md)