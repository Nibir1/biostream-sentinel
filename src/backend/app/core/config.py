import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "BioStream Sentinel"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api/v1"
    
    # Infrastructure - Defaults match docker-compose
    POSTGRES_USER: str = "biostream_user"
    POSTGRES_PASSWORD: str = "biostream_secure_pass"
    POSTGRES_HOST: str = "localhost" # 'postgres' when in docker
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "biostream_db"
    
    # Security
    PII_SALT: str = "default_unsafe_salt_for_dev"

    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000" # Use 'minio:9000' in docker, 'localhost' for local dev
    MINIO_ROOT_USER: str = "minio_admin"
    MINIO_ROOT_PASSWORD: str = "minio_secure_pass"
    MINIO_BUCKET_RAW: str = "telemetry-raw"

    # Directs Pydantic to look for .env in the infra folder if running locally
    model_config = SettingsConfigDict(
        env_file="../../../infra/.env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()