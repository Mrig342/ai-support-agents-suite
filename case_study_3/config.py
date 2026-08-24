"""Configuration for Enterprise Support Agent"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    openai_api_key: Optional[str] = None
    google_project_id: Optional[str] = None
    google_credentials_path: Optional[str] = None
    langchain_api_key: Optional[str] = None
    
    # Database
    database_url: Optional[str] = None
    knowledge_base_index: str = "enterprise-support"
    
    # Application Settings
    app_name: str = "Enterprise Support Agent"
    debug: bool = False
    log_level: str = "INFO"
    
    # LLM Settings
    model_name: str = "gpt-4"
    temperature: float = 0.5
    max_tokens: int = 2000
    max_concurrent_sessions: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
