from fastapi import APIRouter, Depends, Request
from app.domain.schemas import TelemetryPayload, IngestionResponse
from app.services.detector import detector # Import the singleton
from app.services.storage import storage # Import storage
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/telemetry", response_model=IngestionResponse, status_code=202)
async def ingest_telemetry(payload: TelemetryPayload, request: Request):
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    
    # 1. AI Analysis
    # We run this synchronously here for simplicity. 
    # In high-scale production, this would be offloaded to a background worker.
    analysis = detector.predict(
        payload.heart_rate, 
        payload.spo2, 
        payload.battery_level
    )
    
    risk_level = analysis["risk_level"]
    score = float(analysis["anomaly_score"]) # Ensure float for DB
    
    # 2. Logging with Context
    log_payload = {
        "correlation_id": correlation_id,
        "device_id": payload.device_id,
        "risk": risk_level,
        "score": f"{analysis['anomaly_score']:.4f}"
    }
    
    # 3. Persistence (Async)
    # In a real app, use BackgroundTasks. Here we await to ensure data safety for the demo.
    await storage.store_telemetry(payload, risk_level, score)

    # FORCE PRINT TO CONSOLE FOR DEMO PURPOSES
    if risk_level == "HIGH":
        print(f"🚨 [ALERT] High Risk Detected! Device: {payload.device_id} | HR: {payload.heart_rate} | Score: {log_payload['score']}")
        logger.warning(f"ANOMALY DETECTED: {payload.device_id}", extra=log_payload)
    else:
        logger.info(f"Telemetry Accepted", extra=log_payload)
    
    return IngestionResponse(
        status="accepted",
        message="Telemetry processed",
        correlation_id=correlation_id,
        risk_assessment=risk_level
    )