from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Customer Support AI Agent"
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    MODEL_NAME: str = "distilbert-base-uncased"  # used on Day 3
    FAQ_MATCH_THRESHOLD: float = 0.55            # used on Day 2+
    QA_MIN_SCORE: float = 0.28                   # used on Day 3
    DB_URL: str = "sqlite:///./support.db"       # SQLite file in backend/

settings = Settings()
