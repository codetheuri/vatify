from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    PROJECT_NAME: str = "
    DATABASE_URL: str = "sqlite+aiosqlite:///./
    SECRET_KEY: str = "supersecretkey"
    ALGORITHM: str = "HS256"
    
    # KRA Sandbox Config
    GAVA_CONNECT_BASE_URL: str = "https://sbx.kra.go.ke"
    
    # Individual App Credentials
    KRA_PIN_VALIDATION_KEY: Optional[str] = None
    KRA_PIN_VALIDATION_SECRET: Optional[str] = None
    
    KRA_INVOICE_CHECKER_KEY: Optional[str] = None
    KRA_INVOICE_CHECKER_SECRET: Optional[str] = None
    
    KRA_NIL_FILING_KEY: Optional[str] = None
    KRA_NIL_FILING_SECRET: Optional[str] = None

    KRA_OBLIGATIONS_KEY: Optional[str] = None
    KRA_OBLIGATIONS_SECRET: Optional[str] = None

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 # 1 hour
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7 # 7 days

    # SMTP Settings
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 465
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "theurij113@gmail.com"
    SMTP_FROM_NAME: str = ""
    
    DEBUG: bool = False

settings = Settings()
