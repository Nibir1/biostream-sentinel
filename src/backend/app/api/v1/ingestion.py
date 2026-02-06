from fastapi import APIRouter, Depends, HTTPException, Request
from app.domain.schemas import TelemetryPayload, IngestionResponse
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/telemetry", response_model=IngestionResponse, status_code=202)
async def ingest_telemetry(payload: TelemetryPayload, request: Request):
    """
    Ingests wearable telemetry data.
    
    - **Validation**: Enforced by Pydantic. Invalid data returns 422.
    - **Processing**: (Future) Async dispatch to Kafka/Queue.
    """
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    
    # In Phase 4, we will pass this payload to the Anomaly Detector
    logger.info(f"Received valid telemetry from {payload.device_id}", extra={"correlation_id": correlation_id})
    
    return IngestionResponse(
        status="accepted",
        message="Telemetry queued for processing",
        correlation_id=correlation_id
    )