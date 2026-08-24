"""Configuration for E-Commerce Support Agent"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Vector Database
    pinecone_api_key: Optional[str] = None
    pinecone_index_name: str = "ecommerce-orders"
    
    # Database
    database_url: Optional[str] = None
    
    # Application Settings
    app_name: str = "E-Commerce Support Agent"
    debug: bool = False
    log_level: str = "INFO"
    
    # RAG Settings
    chunk_size: int = 1000
    chunk_overlap: int = 200
    retrieval_top_k: int = 5
    
    # LLM Settings
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 500
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
