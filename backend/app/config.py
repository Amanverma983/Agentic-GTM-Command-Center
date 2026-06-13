import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    sqlite_db_path: str = os.getenv("SQLITE_DB_PATH", "gtm_center.db")
    chroma_db_path: str = os.getenv("CHROMA_DB_PATH", "chroma_db")
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", 8000))
    environment: str = os.getenv("ENVIRONMENT", "development")
    # Gmail SMTP for email sending
    smtp_email: str = os.getenv("SMTP_EMAIL", "")
    smtp_app_password: str = os.getenv("SMTP_APP_PASSWORD", "")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
