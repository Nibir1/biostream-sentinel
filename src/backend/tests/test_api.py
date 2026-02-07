import pytest
from unittest.mock import patch, AsyncMock  # <-- ADDED THIS IMPORT
from app.core.config import settings

# 1. Test The Quality Gate (Phase 2 Requirement)
def test_reject_impossible_heart_rate(client):
    """
    Ensure the system rejects physically impossible data (HR > 250).
    Expected: 422 Unprocessable Entity
    """
    payload = {
        "device_id": "TEST-001",
        "patient_id": "PATIENT-TEST",
        "timestamp": "2026-02-07T12:00:00Z",
        "heart_rate": 300, # IMPOSSIBLE VALUE
        "spo2": 98.0,
        "battery_level": 50.0
    }
    response = client.post(f"{settings.API_PREFIX}/telemetry", json=payload)
    assert response.status_code == 422
    assert "physiological tracking limits" in response.text

# 2. Test Valid Data Ingestion
def test_accept_valid_telemetry(client):
    """
    Ensure valid data is accepted and passed to processing.
    Expected: 202 Accepted
    """
    payload = {
        "device_id": "TEST-002",
        "patient_id": "PATIENT-TEST",
        "timestamp": "2026-02-07T12:00:00Z",
        "heart_rate": 80, # Normal
        "spo2": 99.0,
        "battery_level": 75.0
    }
    
    # Mock the storage store_telemetry method to avoid DB errors
    with patch("app.services.storage.storage.store_telemetry", new_callable=AsyncMock) as mock_store:
        response = client.post(f"{settings.API_PREFIX}/telemetry", json=payload)
        
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "accepted"
        assert "risk_assessment" in data

# 3. Test Health Check
def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"