from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Enum, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
import os
from dotenv import load_dotenv
import enum

load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost/nis2_platform")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enums
class UserRole(enum.Enum):
    ADMIN = "admin"
    COMPANY = "company"

class CompanyType(enum.Enum):
    ESSENTIAL = "essenziale"
    IMPORTANT = "importante"
    UNKNOWN = "non_so"

class AssessmentStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    EXPIRED = "expired"

class ComplianceResult(enum.Enum):
    POSITIVE = "positivo"
    NEGATIVE = "negativo"

# Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    email = Column(String(255), unique=True, index=True)
    hashed_password = Column(String(255))
    role = Column(Enum(UserRole))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="user", uselist=False)

class Company(Base):
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    ragione_sociale = Column(String(255), nullable=False)
    indirizzo = Column(String(500))
    citta = Column(String(100))
    email = Column(String(255))
    tipo_soggetto = Column(Enum(CompanyType))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="company")
    suppliers = relationship("Supplier", back_populates="company")

class Supplier(Base):
    __tablename__ = "suppliers"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    ragione_sociale = Column(String(255), nullable=False)
    indirizzo = Column(String(500))
    citta = Column(String(100))
    email = Column(String(255))
    certifications = Column(JSON)  # Certificazioni ISO etc
    risk_level = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="suppliers")
    assessments = relationship("Assessment", back_populates="supplier")

class Assessment(Base):
    __tablename__ = "assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    unique_hash = Column(String(255), unique=True, index=True)  # Hash per link univoco
    status = Column(Enum(AssessmentStatus), default=AssessmentStatus.PENDING)
    
    # Dati questionario
    has_iso27001 = Column(Boolean, default=False)
    responses = Column(JSON)  # Risposte del fornitore
    
    # Risultati valutazione
    compliance_result = Column(Enum(ComplianceResult))
    total_score = Column(Float)
    max_score = Column(Float)
    score_percentage = Column(Float)
    essential_questions_passed = Column(Boolean)
    improvement_areas = Column(JSON)
    strengths = Column(JSON)
    
    # Tracking temporale
    questionnaire_sent_at = Column(DateTime(timezone=True))
    questionnaire_completed_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))  # 14 giorni validità
    
    # File generati
    pdf_passport_path = Column(String(500))
    pdf_recall_path = Column(String(500))
    qr_code_path = Column(String(500))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    supplier = relationship("Supplier", back_populates="assessments")

class QuestionnaireManifest(Base):
    __tablename__ = "questionnaire_manifest"
    
    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(50), nullable=False)
    manifest_data = Column(JSON, nullable=False)  # Contenuto questmio_RULES_MANIFEST.json
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(255))
    details = Column(JSON)
    ip_address = Column(String(45))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Dependency per database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 