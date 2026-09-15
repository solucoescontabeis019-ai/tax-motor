"""
Configuração da aplicação - Etapa 2: Motor de Decisão Tributária
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configurações da aplicação"""

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/tax_motor"

    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Motor de Decisão Tributária"
    PROJECT_VERSION: str = "0.2.0"

    # CNPJ Lookup
    CNPJ_API_ENABLED: bool = True
    CNPJ_API_TIMEOUT: int = 5

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
