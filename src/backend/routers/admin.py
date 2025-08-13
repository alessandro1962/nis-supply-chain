from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import secrets
import hashlib
from passlib.context import CryptContext

from database import get_db, User, Company, Supplier, Assessment, UserRole, CompanyType
from auth import get_current_admin_user
from schemas import CompanyCreate, CompanyResponse, UserCreate, GlobalStatsResponse
from config import settings

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_db():
    from database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def generate_password() -> str:
    """Genera una password sicura per le aziende"""
    return secrets.token_urlsafe(12)

@router.post("/create-company", response_model=dict)
async def create_company(
    company_data: dict,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Crea una nuova azienda cliente con credenziali di accesso
    """
    try:
        # Genera username e password
        username = f"company_{company_data['ragione_sociale'].lower().replace(' ', '_')}"
        password = generate_password()
        
        # Crea utente
        user = User(
            username=username,
            email=company_data['email'],
            hashed_password=hash_password(password),
            role=UserRole.COMPANY,
            is_active=True
        )
        db.add(user)
        db.flush()
        
        # Crea azienda
        company = Company(
            user_id=user.id,
            ragione_sociale=company_data['ragione_sociale'],
            indirizzo=company_data.get('indirizzo'),
            citta=company_data.get('citta'),
            email=company_data['email'],
            tipo_soggetto=CompanyType(company_data['tipo_soggetto'])
        )
        db.add(company)
        db.commit()
        
        return {
            "success": True,
            "message": "Azienda creata con successo",
            "company_id": company.id,
            "credentials": {
                "username": username,
                "password": password,
                "email": company_data['email']
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Errore nella creazione dell'azienda: {str(e)}"
        )

@router.get("/companies", response_model=List[dict])
async def get_all_companies(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Visualizza tutte le aziende registrate
    """
    companies = db.query(Company).join(User).all()
    
    result = []
    for company in companies:
        # Conta fornitori e assessment
        suppliers_count = db.query(Supplier).filter(Supplier.company_id == company.id).count()
        assessments_count = db.query(Assessment).join(Supplier).filter(
            Supplier.company_id == company.id
        ).count()
        
        result.append({
            "id": company.id,
            "ragione_sociale": company.ragione_sociale,
            "email": company.email,
            "citta": company.citta,
            "tipo_soggetto": company.tipo_soggetto.value,
            "username": company.user.username,
            "is_active": company.user.is_active,
            "created_at": company.created_at,
            "suppliers_count": suppliers_count,
            "assessments_count": assessments_count
        })
    
    return result

@router.get("/suppliers", response_model=List[dict])
async def get_all_suppliers(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Visualizza tutti i fornitori di tutte le aziende
    """
    suppliers = db.query(Supplier).join(Company).all()
    
    result = []
    for supplier in suppliers:
        # Ultimo assessment
        last_assessment = db.query(Assessment).filter(
            Assessment.supplier_id == supplier.id
        ).order_by(Assessment.created_at.desc()).first()
        
        result.append({
            "id": supplier.id,
            "ragione_sociale": supplier.ragione_sociale,
            "email": supplier.email,
            "citta": supplier.citta,
            "company_name": supplier.company.ragione_sociale,
            "risk_level": supplier.risk_level,
            "certifications": supplier.certifications,
            "last_assessment": {
                "status": last_assessment.status.value if last_assessment else None,
                "compliance_result": last_assessment.compliance_result.value if last_assessment and last_assessment.compliance_result else None,
                "score_percentage": last_assessment.score_percentage if last_assessment else None,
                "completed_at": last_assessment.questionnaire_completed_at if last_assessment else None
            } if last_assessment else None,
            "created_at": supplier.created_at
        })
    
    return result

@router.get("/stats", response_model=dict)
async def get_global_stats(
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Statistiche globali della piattaforma
    """
    companies_count = db.query(Company).count()
    suppliers_count = db.query(Supplier).count()
    assessments_count = db.query(Assessment).count()
    
    # Assessment completati
    completed_assessments = db.query(Assessment).filter(
        Assessment.status == "completed"
    ).count()
    
    # Compliance rate
    positive_assessments = db.query(Assessment).filter(
        Assessment.compliance_result == "positivo"
    ).count()
    
    compliance_rate = (positive_assessments / completed_assessments * 100) if completed_assessments > 0 else 0
    
    return {
        "companies_count": companies_count,
        "suppliers_count": suppliers_count,
        "assessments_count": assessments_count,
        "completed_assessments": completed_assessments,
        "compliance_rate": round(compliance_rate, 2),
        "platform_stats": {
            "positive_assessments": positive_assessments,
            "negative_assessments": completed_assessments - positive_assessments,
            "pending_assessments": assessments_count - completed_assessments
        }
    }

@router.post("/upload-manifest")
async def upload_manifest(
    manifest_data: dict,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Carica/aggiorna il manifest del questionario
    """
    try:
        from database import QuestionnaireManifest
        
        # Disattiva manifest precedenti
        db.query(QuestionnaireManifest).update({"is_active": False})
        
        # Crea nuovo manifest
        manifest = QuestionnaireManifest(
            version=manifest_data.get("version", "1.0.0"),
            manifest_data=manifest_data,
            is_active=True
        )
        db.add(manifest)
        db.commit()
        
        return {
            "success": True,
            "message": "Manifest aggiornato con successo",
            "version": manifest.version
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Errore nell'upload del manifest: {str(e)}"
        ) 