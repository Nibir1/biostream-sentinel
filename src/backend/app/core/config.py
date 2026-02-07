import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "BioStream Sentinel"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api/v1"

    # OpenAI (Required for Chatbot)
    OPENAI_API_KEY: str 
    
    # Infrastructure - Defaults are set for LOCAL development (localhost)
    # Docker will override these via environment variables
    POSTGRES_USER: str = "biostream_user"
    POSTGRES_PASSWORD: str = "biostream_secure_pass"
    POSTGRES_HOST: str = "localhost" 
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "biostream_db"
    
    # Security
    PII_SALT: str = "default_unsafe_salt_for_dev"

    # MinIO
    # Default is localhost:9000 for local dev.
    # Docker Compose sets this to 'minio:9000'.
    MINIO_ENDPOINT: str = "localhost:9000" 
    MINIO_ROOT_USER: str = "minio_admin"
    MINIO_ROOT_PASSWORD: str = "minio_secure_pass"
    MINIO_BUCKET_RAW: str = "telemetry-raw"

    # Directs Pydantic to look for .env in the PROJECT ROOT if running locally
    # Path is relative to where this python command is run, or absolute.
    # We look 2 levels up from src/backend if running from there, or just .env
    model_config = SettingsConfigDict(
        env_file=[".env", "../../.env"], 
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()