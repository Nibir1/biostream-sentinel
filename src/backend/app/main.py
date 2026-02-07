from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging, CorrelationIdMiddleware
from app.services.detector import detector
from app.services.storage import storage
# Import all routers
from app.api.v1 import ingestion, analytics, assistant

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Configure Logging
    setup_logging()
    
    # 2. Connect to Infrastructure (Postgres & MinIO)
    await storage.connect()

    # 3. Train the AI model (Isolation Forest) on startup
    detector.train_baseline()
    
    print(f"🚀 Starting {settings.PROJECT_NAME}...")
    yield
    
    # 4. Graceful Shutdown
    await storage.close()
    print("🛑 Shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Middleware: CORS (Allow Frontend)
# UPDATED: Added localhost:3000 to fix the CORS error
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Docker Frontend (Nginx/Production build)
        "http://localhost:5173",  # Local Dev Frontend (Vite)
        "http://localhost:8000",  # Backend itself
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware: Correlation IDs (Tracing)
app.add_middleware(CorrelationIdMiddleware)

# Register Routers
app.include_router(ingestion.router, prefix=settings.API_PREFIX, tags=["Ingestion"])
app.include_router(analytics.router, prefix=settings.API_PREFIX, tags=["Analytics"])
app.include_router(assistant.router, prefix=settings.API_PREFIX, tags=["AI Assistant"]) # New Feature

@app.get("/health")
async def health_check():
    return {
        "status": "ok", 
        "version": settings.VERSION,
        "model_ready": detector.is_ready,
        "db_connected": storage.pool is not None
    }