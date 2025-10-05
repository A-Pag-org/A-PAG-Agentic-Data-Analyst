# API Documentation

Base URL: `http://localhost:8000` (development)

API Version: `v1`

All endpoints are prefixed with `/api/v1`

## Authentication

For the single-user demo, authentication is handled via:
- HTTP Bearer token in `Authorization` header
- Or API key in environment variables

```bash
Authorization: Bearer <token>
```

## Endpoints

### Health Check

#### GET /health

Check API health and service status.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "0.1.0",
  "services": {
    "api": "operational",
    "vector_store": "operational",
    "database": "operational"
  }
}
```

---

### Chat

#### POST /api/v1/chat

Send a message and get RAG-powered response.

**Request**:
```json
{
  "message": "What are the trends in my sales data?",
  "context": [
    {
      "role": "user",
      "content": "Previous message"
    }
  ],
  "data_source_ids": ["uuid-1", "uuid-2"]
}
```

**Response**:
```json
{
  "response": "Based on your sales data, I observe...",
  "sources": [
    {
      "content": "Relevant data excerpt",
      "score": 0.85,
      "metadata": {
        "source_id": "uuid-1",
        "chunk_id": "chunk-1"
      }
    }
  ],
  "metadata": {
    "tokens_used": 1500,
    "processing_time": 2.3
  }
}
```

---

### Data Management

#### POST /api/v1/data/upload

Upload a data file (CSV, Excel, JSON).

**Request**: `multipart/form-data`
- `file`: File to upload

**Response**:
```json
{
  "data_source_id": "uuid",
  "filename": "sales_data.csv",
  "status": "processing",
  "message": "File uploaded successfully"
}
```

#### GET /api/v1/data/sources

List all uploaded data sources.

**Response**:
```json
[
  {
    "id": "uuid",
    "name": "sales_data.csv",
    "type": "csv",
    "status": "ready",
    "created_at": "2024-01-01T00:00:00Z",
    "row_count": 1000,
    "column_count": 10
  }
]
```

#### DELETE /api/v1/data/sources/{source_id}

Delete a data source and its embeddings.

**Response**: 204 No Content

---

### Analysis

#### POST /api/v1/analysis/forecast

Generate time series forecast.

**Request**:
```json
{
  "data_source_id": "uuid",
  "date_column": "date",
  "value_column": "sales",
  "periods": 30,
  "model": "prophet"
}
```

**Response**:
```json
{
  "predictions": [
    {
      "date": "2024-02-01",
      "value": 1250.5,
      "lower_bound": 1100.2,
      "upper_bound": 1400.8
    }
  ],
  "metrics": {
    "mae": 45.2,
    "rmse": 67.8,
    "mape": 3.6,
    "r2_score": 0.92
  },
  "model_info": {
    "model": "prophet",
    "seasonality": "yearly",
    "trend": "linear"
  }
}
```

#### POST /api/v1/analysis/analyze

Perform general data analysis.

**Request**:
```json
{
  "data_source_id": "uuid",
  "analysis_type": "descriptive",
  "columns": ["sales", "quantity", "price"],
  "parameters": {
    "include_correlations": true
  }
}
```

**Response**:
```json
{
  "results": {
    "sales": {
      "mean": 1250.5,
      "std": 234.6,
      "min": 500,
      "max": 2000
    }
  },
  "visualizations": [
    {
      "type": "histogram",
      "data": [...],
      "config": {...}
    }
  ],
  "insights": [
    "Sales show strong positive trend",
    "High correlation between quantity and sales"
  ]
}
```

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message",
  "code": "ERROR_CODE",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Common Error Codes

- `400` Bad Request - Invalid input
- `401` Unauthorized - Missing/invalid authentication
- `404` Not Found - Resource not found
- `422` Unprocessable Entity - Validation error
- `429` Too Many Requests - Rate limit exceeded
- `500` Internal Server Error - Server error

---

## Rate Limits

Current limits (subject to change):

- General API: 100 requests/minute
- File uploads: 10 requests/minute
- LLM calls: 20 requests/minute

---

## Interactive Documentation

When running the API locally, visit:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

---

## SDK / Client Examples

### Python

```python
import httpx

API_URL = "http://localhost:8000/api/v1"

async with httpx.AsyncClient() as client:
    response = await client.post(
        f"{API_URL}/chat",
        json={
            "message": "Analyze my sales trends",
            "data_source_ids": ["uuid"]
        }
    )
    data = response.json()
    print(data["response"])
```

### TypeScript

```typescript
const response = await fetch('http://localhost:8000/api/v1/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: 'Analyze my sales trends',
    data_source_ids: ['uuid'],
  }),
});

const data = await response.json();
console.log(data.response);
```

---

## Webhooks (Future)

Webhooks for long-running tasks:

- Analysis completion
- Forecast generation
- Data processing status

---

## Changelog

### v0.1.0 (Current)
- Initial API release
- Basic RAG chat
- File upload
- Forecast generation
- Descriptive analytics