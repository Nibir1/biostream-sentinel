.PHONY: help up down logs build infra-up infra-down run-backend run-frontend run-simulator install install-frontend test clean db-shell minio-ui

# ==============================================================================
# Configuration & Paths
# ==============================================================================
# Main Production Compose File (Root)
COMPOSE_FILE := docker-compose.yml
# Legacy/Local Dev Infra Only File
INFRA_COMPOSE := infra/docker-compose.yml

BACKEND_DIR  := src/backend
FRONTEND_DIR := src/frontend
SIM_DIR      := src/simulator
PYTHON       := python

# ==============================================================================
# Main Commands
# ==============================================================================

help:
	@echo "BioStream Sentinel - Engineer's Control Plane"
	@echo "===================================================================="
	@echo "PRODUCTION (Docker - Recommended):"
	@echo "  make up            : Start FULL System (Backend, Frontend, Simulator, DB)"
	@echo "  make down          : Stop all containers"
	@echo "  make build         : Rebuild all images (no cache)"
	@echo "  make logs          : View live logs from all services"
	@echo ""
	@echo "LOCAL DEVELOPMENT (Hybrid):"
	@echo "  make infra-up      : Start ONLY Infra (Postgres & MinIO)"
	@echo "  make run-backend   : Start FastAPI Server Locally (Port 8000)"
	@echo "  make run-frontend  : Start React Dashboard Locally (Port 5173)"
	@echo "  make run-simulator : Start Go Device Simulator Locally"
	@echo "  make install       : Install ALL dependencies (Python, Go, Node)"
	@echo "  make test          : Run Python Unit Tests"
	@echo ""
	@echo "DEBUGGING:"
	@echo "  make clean         : NUCLEAR option (Stop + Remove Volumes/Data)"
	@echo "  make db-shell      : Open PSQL terminal inside Postgres container"
	@echo "  make minio-ui      : Print MinIO Console URL"

# ==============================================================================
# Production / Full Docker Support
# ==============================================================================

up:
	@echo "Launching BioStream Sentinel (Full Stack)..."
	docker-compose -f $(COMPOSE_FILE) build --no-cache
	docker-compose -f $(COMPOSE_FILE) up -d
	@echo "System is UP."
	@echo "  - Frontend:  http://localhost:3000"
	@echo "  - Backend:   http://localhost:8000/docs"
	@echo "  - MinIO UI:  http://localhost:9001"

down:
	docker-compose -f $(COMPOSE_FILE) down

build:
	docker-compose -f $(COMPOSE_FILE) build --no-cache

logs:
	docker-compose -f $(COMPOSE_FILE) logs -f

# ==============================================================================
# Local Development (Hybrid Mode)
# ==============================================================================

# Uses the infra-only compose file if you want to run code on host
infra-up:
	docker-compose -f $(INFRA_COMPOSE) up -d
	@echo "Infrastructure (DB Only) is UP."

infra-down:
	docker-compose -f $(INFRA_COMPOSE) down

install: install-frontend
	@echo "Syncing Python Dependencies (uv)..."
	cd $(BACKEND_DIR) && uv pip compile pyproject.toml --extra test -o uv.lock && uv pip sync uv.lock
	@echo "Tidy Go Modules..."
	cd $(SIM_DIR) && go mod tidy
	@echo "All Dependencies Installed."

install-frontend:
	@echo "Installing Frontend Dependencies..."
	cd $(FRONTEND_DIR) && npm install

run-backend:
	@echo "Starting FastAPI Backend (Local)..."
	@echo "Ensure 'make infra-up' was run first!"
	cd $(BACKEND_DIR) && $(PYTHON) -m uvicorn app.main:app --reload --port 8000

run-frontend:
	@echo "Starting React Dashboard (Local)..."
	cd $(FRONTEND_DIR) && npm run dev

run-simulator:
	@echo "Starting Go Device Simulator (Local)..."
	cd $(SIM_DIR) && go run .

test: test-backend test-frontend

test-backend:
	@echo "🧪 Running Backend Tests..."
	cd $(BACKEND_DIR) && pytest

test-frontend:
	@echo "🧪 Running Frontend Tests..."
	cd $(FRONTEND_DIR) && npm test -- --run

# ==============================================================================
# Maintenance & Debugging
# ==============================================================================

clean:
	@echo "⚠️  Cleaning up ALL Docker resources..."
	docker-compose -f $(COMPOSE_FILE) down -v --remove-orphans
	docker-compose -f $(INFRA_COMPOSE) down -v --remove-orphans
	docker system prune -f
	@echo "🧹 Cleaning Python cache..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	@echo "🧹 Cleaning Node modules..."
	rm -rf $(FRONTEND_DIR)/node_modules
	@echo "✨ Clean complete."

db-shell:
	@echo "Entering Postgres Shell..."
	docker exec -it biostream-postgres psql -U biostream_user -d biostream_db

minio-ui:
	@echo "MinIO Console: http://localhost:9001"
	@echo "  User: minio_admin"
	@echo "  Pass: minio_secure_pass"