from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime
from typing import Optional

class TelemetryPayload(BaseModel):
    """
    Represents raw telemetry data from a wearable device.
    Strict validation ensures no physically impossible data enters the system.
    """
    device_id: str = Field(..., min_length=3, max_length=50, description="Unique hardware identifier")
    patient_id: str = Field(..., min_length=3, max_length=50, description="Patient identifier (will be hashed)")
    timestamp: datetime = Field(default_factory=datetime.now, description="ISO 8601 timestamp")
    
    # Validation Rules (Biological Constraints)
    heart_rate: int = Field(..., ge=0, le=300, description="BPM. Must be realistic (0-300).")
    spo2: float = Field(..., ge=0.0, le=100.0, description="Oxygen saturation percentage (0-100).")
    battery_level: float = Field(..., ge=0.0, le=100.0, description="Device battery percentage.")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "device_id": "WEARABLE-001",
                "patient_id": "PATIENT-X",
                "timestamp": "2023-10-27T10:00:00Z",
                "heart_rate": 72,
                "spo2": 98.5,
                "battery_level": 85.0
            }
        }
    )

    @field_validator('heart_rate')
    @classmethod
    def check_physiological_limits(cls, v: int) -> int:
        """
        Reject values that are technically possible (0-300) but indicate 
        likely sensor error or severe medical emergency requiring different protocol.
        Here we treat extreme outliers as 'dirty data' for the purpose of the assignment.
        """
        if v < 30 or v > 250:
            raise ValueError(f"Heart rate {v} is outside physiological tracking limits (30-250)")
        return v

class IngestionResponse(BaseModel):
    status: str
    message: str
    correlation_id: str
    risk_assessment: Optional[str] = "PROCESSING"