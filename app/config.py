import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "WeatherPulse"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Scraping Settings
    request_timeout: int = 30
    max_retries: int = 3
    
    # CORS Settings
    allowed_origins: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        env_file = ".env"

settings = Settings()
