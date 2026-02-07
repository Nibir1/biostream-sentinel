from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import setup_logging, CorrelationIdMiddleware
from app.api.v1 import ingestion
from app.services.detector import detector # Import detector
from app.services.storage import storage # Import storage

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    
    # Connect to DB & MinIO
    await storage.connect()

    # Train the AI model on startup
    detector.train_baseline()
    
    print(f"Starting {settings.PROJECT_NAME}...")
    yield

    # Close connections
    await storage.close()
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