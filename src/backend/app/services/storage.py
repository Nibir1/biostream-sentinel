import hashlib
import io
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any

import asyncpg
import polars as pl
from minio import Minio
from app.core.config import settings
from app.domain.schemas import TelemetryPayload

logger = logging.getLogger(__name__)

class StorageService:
    def __init__(self):
        self.pool = None
        self.minio_client = None
        # Batch buffer for Cold Storage (Parquet)
        self.buffer: List[Dict[str, Any]] = []
        self.BATCH_SIZE = 50 # Flush to MinIO every 50 records

    async def connect(self):
        """Initialize DB Pool and MinIO Client."""
        logger.info("STORAGE: Connecting to Postgres...")
        self.pool = await asyncpg.create_pool(
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            database=settings.POSTGRES_DB,
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT
        )
        
        logger.info("STORAGE: Connecting to MinIO...")
        self.minio_client = Minio(
            settings.MINIO_ENDPOINT.replace("http://", ""), # Strip protocol if present
            access_key=settings.MINIO_ROOT_USER,
            secret_key=settings.MINIO_ROOT_PASSWORD,
            secure=False # Dev mode (No SSL)
        )

    async def close(self):
        if self.pool:
            await self.pool.close()

    def hash_pii(self, patient_id: str) -> str:
        """SHA-256 Hashing for HIPAA Compliance."""
        salted = f"{patient_id}{settings.PII_SALT}"
        return hashlib.sha256(salted.encode()).hexdigest()

    async def store_telemetry(self, payload: TelemetryPayload, risk: str, score: float):
        """
        Dual-write strategy:
        1. Insert into Postgres (Hot)
        2. Buffer for MinIO Parquet (Cold)
        """
        pii_hash = self.hash_pii(payload.patient_id)
        
        # 1. Hot Storage (Postgres)
        async with self.pool.acquire() as conn:
            # Insert Telemetry
            row_id = await conn.fetchval('''
                INSERT INTO device_telemetry 
                (device_id, patient_id_hash, timestamp, heart_rate, spo2, battery_level)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
            ''', payload.device_id, pii_hash, payload.timestamp, 
                 payload.heart_rate, payload.spo2, payload.battery_level)

            # Insert Anomaly Alert if High Risk
            if risk == "HIGH":
                await conn.execute('''
                    INSERT INTO anomalies (telemetry_id, device_id, anomaly_score, risk_level)
                    VALUES ($1, $2, $3, $4)
                ''', row_id, payload.device_id, score, risk)

        # 2. Cold Storage Buffering
        self.buffer.append({
            "device_id": payload.device_id,
            "patient_id_hash": pii_hash,
            "timestamp": payload.timestamp,
            "heart_rate": payload.heart_rate,
            "spo2": payload.spo2,
            "risk_level": risk
        })

        if len(self.buffer) >= self.BATCH_SIZE:
            self._flush_to_minio()

    def _flush_to_minio(self):
        """Writes the buffer to a Parquet file and uploads to MinIO."""
        try:
            # Create DataFrame
            df = pl.DataFrame(self.buffer)
            
            # Write to in-memory buffer
            parquet_buffer = io.BytesIO()
            df.write_parquet(parquet_buffer)
            parquet_buffer.seek(0)
            
            # Upload to MinIO
            filename = f"telemetry_batch_{uuid.uuid4()}.parquet"
            # Hardcoded bucket name from docker-compose logic
            bucket_name = "telemetry-raw" 
            
            # Check if bucket exists (idempotency)
            if not self.minio_client.bucket_exists(bucket_name):
                 self.minio_client.make_bucket(bucket_name)

            self.minio_client.put_object(
                bucket_name,
                filename,
                parquet_buffer,
                length=parquet_buffer.getbuffer().nbytes,
                content_type="application/octet-stream"
            )
            
            logger.info(f"ARCHIVE: Flushed {len(self.buffer)} records to MinIO/{filename}")
            self.buffer.clear() # Reset buffer
            
        except Exception as e:
            logger.error(f"ARCHIVE ERROR: Failed to flush to MinIO: {e}")

# Singleton
storage = StorageService()