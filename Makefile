.PHONY: help install dev build clean docker-up docker-down lint format test

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	@echo "📦 Installing dependencies..."
	pnpm install
	cd backend && poetry install

dev: ## Start development servers
	@echo "🚀 Starting development servers..."
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	pnpm dev

build: ## Build all packages
	@echo "🔨 Building packages..."
	pnpm build

clean: ## Clean build artifacts and dependencies
	@echo "🧹 Cleaning..."
	pnpm clean
	cd backend && rm -rf .venv __pycache__ .pytest_cache .ruff_cache
	rm -rf node_modules

docker-up: ## Start Docker services (PostgreSQL, ChromaDB)
	@echo "🐳 Starting Docker services..."
	docker-compose up -d
	@echo "✅ Services started:"
	@echo "  - PostgreSQL: localhost:5432"
	@echo "  - ChromaDB: localhost:8001"

docker-down: ## Stop Docker services
	@echo "🐳 Stopping Docker services..."
	docker-compose down

docker-logs: ## Show Docker logs
	docker-compose logs -f

lint: ## Lint code
	@echo "🔍 Linting..."
	pnpm lint
	cd backend && poetry run ruff check app/

format: ## Format code
	@echo "✨ Formatting..."
	pnpm format
	cd backend && poetry run black app/

test: ## Run tests
	@echo "🧪 Running tests..."
	pnpm test
	cd backend && poetry run pytest

type-check: ## Type check code
	@echo "🔍 Type checking..."
	pnpm type-check
	cd backend && poetry run mypy app/

setup: install docker-up ## Complete setup (install + docker)
	@echo "✅ Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Copy .env.example files and configure"
	@echo "  2. Run 'make dev' to start development servers"

.DEFAULT_GOAL := help