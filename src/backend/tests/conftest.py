import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app

@pytest.fixture(scope="module")
def client():
    # Mock the lifespan context manager (DB connection/AI training)
    # This prevents tests from trying to connect to real Postgres/MinIO
    with patch("app.services.storage.storage.connect", new_callable=AsyncMock), \
         patch("app.services.storage.storage.close", new_callable=AsyncMock), \
         patch("app.services.detector.detector.train_baseline", return_value=None):
        
        with TestClient(app) as c:
            yield c