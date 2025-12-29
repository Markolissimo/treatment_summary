from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "BiteSoft AI Document Generation System"
    app_version: str = "0.2.0"
    debug: bool = False
    environment: str = "development"  # development, staging, production

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    
    # LLM Seeds for reproducibility
    treatment_summary_seed: int = 42
    insurance_summary_seed: int = 42
    progress_notes_seed: int = 42

    # Database
    # database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/bitesoft_ai"
    database_url: str = "sqlite+aiosqlite:///./bitesoft_ai.db"  # For local development

    # JWT Authentication
    secret_key: str = "CHANGE_ME_IN_PRODUCTION"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    jwt_issuer: str = ""  # Expected JWT issuer (e.g., portal domain)
    jwt_audience: str = ""  # Expected JWT audience
    jwt_public_key: str = ""  # Public key for JWT verification (if using RS256)
    enable_auth_bypass: bool = True  # Allow unauthenticated requests in dev mode
    
    # CORS Configuration
    cors_origins: str = "*"  # Comma-separated list of allowed origins
    
    # PHI and Data Retention
    store_full_audit_data: bool = True  # Store full input/output in audit logs
    redact_phi_fields: bool = False  # Redact PHI fields before storing
    phi_fields_to_redact: str = "patient_name,practice_name"  # Comma-separated field names

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
    
    @property
    def phi_fields_list(self) -> list[str]:
        """Parse PHI fields from comma-separated string."""
        return [field.strip() for field in self.phi_fields_to_redact.split(",") if field.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
