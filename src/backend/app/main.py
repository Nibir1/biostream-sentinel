from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import setup_logging, CorrelationIdMiddleware
from app.api.v1 import ingestion
from app.services.detector import detector # Import detector
from app.services.storage import storage # Import storage
from fastapi.middleware.cors import CORSMiddleware # Import this for CORS
from app.api.v1 import ingestion, analytics

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

# Allow Frontend to communicate with Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(CorrelationIdMiddleware)
app.include_router(ingestion.router, prefix=settings.API_PREFIX, tags=["Ingestion"])
app.include_router(analytics.router, prefix=settings.API_PREFIX, tags=["Analytics"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "model_ready": detector.is_ready}