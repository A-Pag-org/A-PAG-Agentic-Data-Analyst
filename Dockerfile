FROM node:20-alpine AS fe
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build && npx next export -o /app/frontend/out

FROM python:3.11-slim AS be
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    CMDSTANPY_CACHE=/cache/cmdstan
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential g++ make git curl \
  && rm -rf /var/lib/apt/lists/*
COPY backend/ /app/backend/
RUN pip install --upgrade pip && pip install -r /app/backend/requirements.txt
RUN mkdir -p /app/backend/public
COPY --from=fe /app/frontend/out/ /app/backend/public/
WORKDIR /app/backend
ENV PORT=10000 \
    HOST=0.0.0.0 \
    ENVIRONMENT=production
EXPOSE 10000
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT

