# Makefile for GroundedCV
# Common development commands for the project

.PHONY: help setup setup-backend setup-frontend dev dev-backend dev-frontend \
        test test-backend test-frontend lint lint-fix typecheck build \
        docker-build docker-up docker-down docker-logs clean

# Default target
help:
	@echo "GroundedCV Development Commands"
	@echo "================================"
	@echo ""
	@echo "Setup:"
	@echo "  make setup          - Install all dependencies and pre-commit hooks"
	@echo "  make setup-backend  - Install backend dependencies only"
	@echo "  make setup-frontend - Install frontend dependencies only"
	@echo ""
	@echo "Development:"
	@echo "  make dev            - Start both backend and frontend dev servers"
	@echo "  make dev-backend    - Start backend dev server only"
	@echo "  make dev-frontend   - Start frontend dev server only"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Run all tests"
	@echo "  make test-backend   - Run backend tests with coverage"
	@echo "  make test-frontend  - Run frontend tests with coverage"
	@echo ""
	@echo "Quality:"
	@echo "  make lint           - Run all linters"
	@echo "  make lint-fix       - Run linters with auto-fix"
	@echo "  make typecheck      - Run type checkers"
	@echo ""
	@echo "Build:"
	@echo "  make build          - Build production assets"
	@echo "  make docker-build   - Build Docker images locally"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up      - Start Docker Compose services"
	@echo "  make docker-down    - Stop Docker Compose services"
	@echo "  make docker-logs    - View Docker Compose logs"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean          - Clean build artifacts"

# ============================================================================
# Setup
# ============================================================================

setup: setup-backend setup-frontend
	@echo "Installing pre-commit hooks..."
	pip install pre-commit
	pre-commit install
	@echo ""
	@echo "Setup complete! Run 'make dev' to start development servers."

setup-backend:
	@echo "Setting up backend..."
	cd backend && python -m venv .venv
	cd backend && .venv/Scripts/activate && pip install --upgrade pip
	cd backend && .venv/Scripts/activate && pip install -e ".[dev]"

setup-frontend:
	@echo "Setting up frontend..."
	cd frontend && npm ci

# ============================================================================
# Development
# ============================================================================

dev:
	@echo "Starting development servers..."
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:5173"
	@echo ""
	@echo "Press Ctrl+C to stop"
	$(MAKE) -j2 dev-backend dev-frontend

dev-backend:
	cd backend && .venv/Scripts/activate && uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

# ============================================================================
# Testing
# ============================================================================

test: test-backend test-frontend

test-backend:
	@echo "Running backend tests..."
	cd backend && .venv/Scripts/activate && pytest tests/ -v --cov=app --cov-report=term-missing

test-frontend:
	@echo "Running frontend tests..."
	cd frontend && npm run test:coverage

# ============================================================================
# Quality
# ============================================================================

lint: lint-backend lint-frontend

lint-backend:
	@echo "Linting backend..."
	cd backend && .venv/Scripts/activate && ruff check app/
	cd backend && .venv/Scripts/activate && ruff format --check app/

lint-frontend:
	@echo "Linting frontend..."
	cd frontend && npm run lint

lint-fix:
	@echo "Fixing lint issues..."
	cd backend && .venv/Scripts/activate && ruff check --fix app/
	cd backend && .venv/Scripts/activate && ruff format app/
	cd frontend && npm run lint -- --fix
	cd frontend && npx prettier --write "src/**/*.{ts,tsx,css,json}"

typecheck: typecheck-backend typecheck-frontend

typecheck-backend:
	@echo "Type checking backend..."
	cd backend && .venv/Scripts/activate && mypy app/

typecheck-frontend:
	@echo "Type checking frontend..."
	cd frontend && npx tsc --noEmit

# ============================================================================
# Build
# ============================================================================

build: build-frontend

build-frontend:
	@echo "Building frontend..."
	cd frontend && npm run build

docker-build:
	@echo "Building Docker images..."
	docker build -t grounded-cv-backend:dev ./backend
	docker build -t grounded-cv-frontend:dev ./frontend

# ============================================================================
# Docker
# ============================================================================

docker-up:
	@echo "Starting Docker Compose services..."
	docker-compose up -d

docker-down:
	@echo "Stopping Docker Compose services..."
	docker-compose down

docker-logs:
	docker-compose logs -f

# ============================================================================
# Cleanup
# ============================================================================

clean:
	@echo "Cleaning build artifacts..."
	rm -rf frontend/dist
	rm -rf frontend/node_modules/.cache
	rm -rf backend/.venv
	rm -rf backend/__pycache__
	rm -rf backend/app/__pycache__
	rm -rf backend/.pytest_cache
	rm -rf backend/.mypy_cache
	rm -rf backend/.ruff_cache
	rm -rf backend/htmlcov
	rm -rf backend/.coverage
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Clean complete!"
