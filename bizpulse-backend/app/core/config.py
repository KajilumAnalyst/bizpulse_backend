import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "BizPulse")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # DB — prefers PostgreSQL, falls back to SQLite
    DATABASE_URL: str = os.getenv("DATABASE_URL") or os.getenv("SQLITE_URL", "sqlite:///./bizpulse_local.db")

    # Fix Railway's postgres:// prefix (SQLAlchemy requires postgresql://)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    # Auth
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 10080))

    # AI
    AI_PROVIDER: str = os.getenv("AI_PROVIDER", "mock")   # openai | ollama | mock
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3")

    # CORS
    ALLOWED_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "http://localhost:5500").split(",")

settings = Settings()
