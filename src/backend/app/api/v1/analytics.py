from fastapi import APIRouter
from app.services.storage import storage

router = APIRouter()

@router.get("/anomalies")
async def get_anomalies():
    """Returns the latest high-risk alerts."""
    data = await storage.get_recent_anomalies()
    return {"data": data}