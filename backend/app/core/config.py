from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173"
    ]
    DEFAULT_ALGORITHM: str = "genetic"
    DEFAULT_ITERATIONS: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 