import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost/nis2_platform")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "fallback-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Email Configuration
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "")
    
    # File Storage
    STATIC_FILES_DIR: str = os.getenv("STATIC_FILES_DIR", "static")
    PDF_OUTPUT_DIR: str = os.getenv("PDF_OUTPUT_DIR", "static/pdf")
    QR_CODES_DIR: str = os.getenv("QR_CODES_DIR", "static/qr")
    
    # Application Settings
    APP_NAME: str = os.getenv("APP_NAME", "NIS2 Supplier Assessment Platform")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    DOMAIN: str = os.getenv("DOMAIN", "localhost:8000")
    
    # QR Code Settings
    QR_BASE_URL: str = os.getenv("QR_BASE_URL", "http://localhost:8000/v/passport")
    
    # PDF Settings
    PDF_LOGO_PATH: str = os.getenv("PDF_LOGO_PATH", "static/images/logo.png")
    PDF_COMPANY_NAME: str = os.getenv("PDF_COMPANY_NAME", "Your Company Name")
    
    # Security Settings
    BCRYPT_ROUNDS: int = int(os.getenv("BCRYPT_ROUNDS", "12"))
    QUESTIONNAIRE_EXPIRY_DAYS: int = int(os.getenv("QUESTIONNAIRE_EXPIRY_DAYS", "14"))

settings = Settings() 