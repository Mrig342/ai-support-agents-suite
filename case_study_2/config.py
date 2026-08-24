"""Configuration for Banking Support Agent"""

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    openai_api_key: Optional[str] = None
    github_copilot_enabled: bool = True
    
    # Database
    database_url: Optional[str] = None
    encryption_key: Optional[str] = None
    
    # Security & Compliance
    compliance_mode: str = "strict"
    mfa_required: bool = True
    pci_dss_enabled: bool = True
    gdpr_enabled: bool = True
    
    # Application Settings
    app_name: str = "Banking Support Agent"
    debug: bool = False
    log_level: str = "INFO"
    
    # LLM Settings
    model_name: str = "gpt-4"
    temperature: float = 0.3  # Lower temperature for banking (more deterministic)
    max_tokens: int = 500
    
    # Risk Assessment
    max_risk_threshold: str = "medium"
    fraud_detection_enabled: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
