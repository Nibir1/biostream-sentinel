from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import setup_logging, CorrelationIdMiddleware
from app.api.v1 import ingestion
from app.services.detector import detector # Import detector

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    
    # Train the AI model on startup
    detector.train_baseline()
    
    print(f"Starting {settings.PROJECT_NAME}...")
    yield
    print("Shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(CorrelationIdMiddleware)
app.include_router(ingestion.router, prefix=settings.API_PREFIX, tags=["Ingestion"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "model_ready": detector.is_ready}