from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid
import hashlib
from datetime import datetime, timedelta

from database import get_db, User, Company, Supplier, Assessment, AssessmentStatus
from auth import get_current_company_user
from config import settings

router = APIRouter()

def get_db():
    from database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_assessment_hash() -> str:
    """Genera un hash univoco per il questionario"""
    return str(uuid.uuid4())

@router.post("/create-supplier", response_model=dict)
async def create_supplier(
    supplier_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_company_user)
):
    """
    Crea un nuovo fornitore per l'azienda
    """
    try:
        company = db.query(Company).filter(Company.user_id == current_user.id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Azienda non trovata"
            )
        
        supplier = Supplier(
            company_id=company.id,
            ragione_sociale=supplier_data['ragione_sociale'],
            indirizzo=supplier_data.get('indirizzo'),
            citta=supplier_data.get('citta'),
            email=supplier_data['email'],
            certifications=supplier_data.get('certifications', {}),
            risk_level=supplier_data.get('risk_level', 'medium')
        )
        db.add(supplier)
        db.commit()
        
        return {
            "success": True,
            "message": "Fornitore creato con successo",
            "supplier_id": supplier.id,
            "supplier": {
                "id": supplier.id,
                "ragione_sociale": supplier.ragione_sociale,
                "email": supplier.email,
                "citta": supplier.citta,
                "risk_level": supplier.risk_level
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Errore nella creazione del fornitore: {str(e)}"
        )

@router.get("/suppliers", response_model=List[dict])
async def get_suppliers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_company_user)
):
    """
    Lista tutti i fornitori dell'azienda
    """
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Azienda non trovata"
        )
    
    suppliers = db.query(Supplier).filter(Supplier.company_id == company.id).all()
    
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
            "risk_level": supplier.risk_level,
            "certifications": supplier.certifications,
            "last_assessment": {
                "id": last_assessment.id if last_assessment else None,
                "status": last_assessment.status.value if last_assessment else None,
                "compliance_result": last_assessment.compliance_result.value if last_assessment and last_assessment.compliance_result else None,
                "score_percentage": last_assessment.score_percentage if last_assessment else None,
                "completed_at": last_assessment.questionnaire_completed_at if last_assessment else None,
                "expires_at": last_assessment.expires_at if last_assessment else None
            } if last_assessment else None,
            "created_at": supplier.created_at
        })
    
    return result

@router.post("/generate-questionnaire", response_model=dict)
async def generate_questionnaire(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_company_user)
):
    """
    Genera un link univoco per il questionario del fornitore
    """
    try:
        company = db.query(Company).filter(Company.user_id == current_user.id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Azienda non trovata"
            )
        
        supplier = db.query(Supplier).filter(
            Supplier.id == supplier_id,
            Supplier.company_id == company.id
        ).first()
        
        if not supplier:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fornitore non trovato"
            )
        
        # Controlla se esiste già un assessment attivo
        existing_assessment = db.query(Assessment).filter(
            Assessment.supplier_id == supplier_id,
            Assessment.status.in_([AssessmentStatus.PENDING, AssessmentStatus.IN_PROGRESS])
        ).first()
        
        if existing_assessment:
            questionnaire_url = f"{settings.DOMAIN}/supplier/questionnaire/{existing_assessment.unique_hash}"
            return {
                "success": True,
                "message": "Assessment già esistente",
                "assessment_id": existing_assessment.id,
                "questionnaire_url": questionnaire_url,
                "expires_at": existing_assessment.expires_at
            }
        
        # Crea nuovo assessment
        unique_hash = generate_assessment_hash()
        expires_at = datetime.utcnow() + timedelta(days=settings.QUESTIONNAIRE_EXPIRY_DAYS)
        
        assessment = Assessment(
            supplier_id=supplier_id,
            unique_hash=unique_hash,
            status=AssessmentStatus.PENDING,
            questionnaire_sent_at=datetime.utcnow(),
            expires_at=expires_at
        )
        db.add(assessment)
        db.commit()
        
        questionnaire_url = f"{settings.DOMAIN}/supplier/questionnaire/{unique_hash}"
        
        return {
            "success": True,
            "message": "Questionario generato con successo",
            "assessment_id": assessment.id,
            "questionnaire_url": questionnaire_url,
            "unique_hash": unique_hash,
            "expires_at": expires_at
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Errore nella generazione del questionario: {str(e)}"
        )

@router.get("/report/{supplier_id}", response_model=dict)
async def get_supplier_report(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_company_user)
):
    """
    Ottiene il report di valutazione del fornitore
    """
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Azienda non trovata"
        )
    
    supplier = db.query(Supplier).filter(
        Supplier.id == supplier_id,
        Supplier.company_id == company.id
    ).first()
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornitore non trovato"
        )
    
    # Ultimo assessment completato
    assessment = db.query(Assessment).filter(
        Assessment.supplier_id == supplier_id,
        Assessment.status == AssessmentStatus.COMPLETED
    ).order_by(Assessment.questionnaire_completed_at.desc()).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nessun assessment completato trovato per questo fornitore"
        )
    
    return {
        "supplier": {
            "id": supplier.id,
            "ragione_sociale": supplier.ragione_sociale,
            "email": supplier.email,
            "citta": supplier.citta,
            "certifications": supplier.certifications
        },
        "assessment": {
            "id": assessment.id,
            "status": assessment.status.value,
            "compliance_result": assessment.compliance_result.value if assessment.compliance_result else None,
            "total_score": assessment.total_score,
            "max_score": assessment.max_score,
            "score_percentage": assessment.score_percentage,
            "essential_questions_passed": assessment.essential_questions_passed,
            "has_iso27001": assessment.has_iso27001,
            "improvement_areas": assessment.improvement_areas,
            "strengths": assessment.strengths,
            "responses": assessment.responses,
            "completed_at": assessment.questionnaire_completed_at,
            "expires_at": assessment.expires_at
        },
        "files": {
            "pdf_passport_path": assessment.pdf_passport_path,
            "pdf_recall_path": assessment.pdf_recall_path,
            "qr_code_path": assessment.qr_code_path
        }
    }

@router.get("/assessments", response_model=List[dict])
async def get_company_assessments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_company_user)
):
    """
    Lista tutti gli assessment dell'azienda
    """
    company = db.query(Company).filter(Company.user_id == current_user.id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Azienda non trovata"
        )
    
    assessments = db.query(Assessment).join(Supplier).filter(
        Supplier.company_id == company.id
    ).order_by(Assessment.created_at.desc()).all()
    
    result = []
    for assessment in assessments:
        result.append({
            "id": assessment.id,
            "supplier_name": assessment.supplier.ragione_sociale,
            "supplier_id": assessment.supplier_id,
            "status": assessment.status.value,
            "compliance_result": assessment.compliance_result.value if assessment.compliance_result else None,
            "score_percentage": assessment.score_percentage,
            "has_iso27001": assessment.has_iso27001,
            "questionnaire_sent_at": assessment.questionnaire_sent_at,
            "questionnaire_completed_at": assessment.questionnaire_completed_at,
            "expires_at": assessment.expires_at,
            "questionnaire_url": f"{settings.DOMAIN}/supplier/questionnaire/{assessment.unique_hash}" if assessment.status in [AssessmentStatus.PENDING, AssessmentStatus.IN_PROGRESS] else None
        })
    
    return result 