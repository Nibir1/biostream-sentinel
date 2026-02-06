from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import setup_logging, CorrelationIdMiddleware
from app.api.v1 import ingestion

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    setup_logging()
    print(f"Starting {settings.PROJECT_NAME}...")
    yield
    # Shutdown logic
    print("Shutting down...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# Middleware
app.add_middleware(CorrelationIdMiddleware)

# Routers
app.include_router(ingestion.router, prefix=settings.API_PREFIX, tags=["Ingestion"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.VERSION}