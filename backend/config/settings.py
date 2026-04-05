"""Application settings using Pydantic Settings v2."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Global application settings loaded from environment variables."""

    # App
    APP_NAME: str = "SMDPIS - Social Media Intelligence"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security
    SECRET_KEY: str = "smdpis-secret-key-change-in-production-2025"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # MongoDB (optional for Phase 2)
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB: str = "smdpis"

    # Elasticsearch (optional for Phase 2)
    ELASTICSEARCH_URL: str = "http://localhost:9200"

    # Neo4j (optional for Phase 2)
    NEO4J_URL: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"

    # Kafka (optional for Phase 2)
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
