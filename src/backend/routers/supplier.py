from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime
import json

from database import get_db, Assessment, AssessmentStatus, QuestionnaireManifest
from services.evaluation_engine import EvaluationEngine
from config import settings

router = APIRouter()

def get_db():
    from database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/questionnaire/{hash}", response_model=dict)
async def get_questionnaire(
    hash: str,
    db: Session = Depends(get_db)
):
    """
    Accesso al questionario tramite hash univoco (no autenticazione richiesta)
    """
    # Trova assessment tramite hash
    assessment = db.query(Assessment).filter(
        Assessment.unique_hash == hash
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Questionario non trovato o link non valido"
        )
    
    # Controlla scadenza
    if assessment.expires_at and datetime.utcnow() > assessment.expires_at:
        assessment.status = AssessmentStatus.EXPIRED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Questionario scaduto"
        )
    
    # Controlla se già completato
    if assessment.status == AssessmentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Questionario già completato"
        )
    
    # Aggiorna status a IN_PROGRESS se era PENDING
    if assessment.status == AssessmentStatus.PENDING:
        assessment.status = AssessmentStatus.IN_PROGRESS
        db.commit()
    
    # Carica manifest questionario
    manifest = db.query(QuestionnaireManifest).filter(
        QuestionnaireManifest.is_active == True
    ).first()
    
    if not manifest:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Manifest questionario non configurato"
        )
    
    # Prepara dati fornitore e azienda (solo info necessarie)
    supplier = assessment.supplier
    company = supplier.company
    
    return {
        "assessment_id": assessment.id,
        "hash": assessment.unique_hash,
        "status": assessment.status.value,
        "expires_at": assessment.expires_at,
        "supplier": {
            "ragione_sociale": supplier.ragione_sociale,
            "email": supplier.email,
            "citta": supplier.citta
        },
        "client_company": {
            "ragione_sociale": company.ragione_sociale,
            "citta": company.citta
        },
        "questionnaire": manifest.manifest_data,
        "responses": assessment.responses if assessment.responses else {},
        "has_iso27001": assessment.has_iso27001
    }

@router.post("/submit", response_model=dict)
async def submit_questionnaire(
    submission_data: dict,
    db: Session = Depends(get_db)
):
    """
    Invio risposte del questionario
    Expected format:
    {
        "hash": "assessment_hash",
        "has_iso27001": true/false,
        "responses": {
            "GSI.03.Q1": "SI",
            "GSI.03.Q2": "NO",
            ...
        }
    }
    """
    try:
        hash_value = submission_data.get("hash")
        has_iso27001 = submission_data.get("has_iso27001", False)
        responses = submission_data.get("responses", {})
        
        # Trova assessment
        assessment = db.query(Assessment).filter(
            Assessment.unique_hash == hash_value
        ).first()
        
        if not assessment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment non trovato"
            )
        
        # Controlla scadenza
        if assessment.expires_at and datetime.utcnow() > assessment.expires_at:
            assessment.status = AssessmentStatus.EXPIRED
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Questionario scaduto"
            )
        
        # Controlla se già completato
        if assessment.status == AssessmentStatus.COMPLETED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Questionario già completato"
            )
        
        # Carica manifest
        manifest = db.query(QuestionnaireManifest).filter(
            QuestionnaireManifest.is_active == True
        ).first()
        
        if not manifest:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Manifest questionario non configurato"
            )
        
        # Applica algoritmo ISO 27001 se necessario
        if has_iso27001:
            responses = apply_iso27001_algorithm(responses, manifest.manifest_data)
        
        # Calcola valutazione
        evaluation_engine = EvaluationEngine()
        evaluation_result = evaluation_engine.calculate_compliance(
            responses, 
            manifest.manifest_data
        )
        
        # Aggiorna assessment
        assessment.has_iso27001 = has_iso27001
        assessment.responses = responses
        assessment.compliance_result = evaluation_result["compliance_result"]
        assessment.total_score = evaluation_result["total_score"]
        assessment.max_score = evaluation_result["max_score"]
        assessment.score_percentage = evaluation_result["score_percentage"]
        assessment.essential_questions_passed = evaluation_result["essential_questions_passed"]
        assessment.improvement_areas = evaluation_result["improvement_areas"]
        assessment.strengths = evaluation_result["strengths"]
        assessment.status = AssessmentStatus.COMPLETED
        assessment.questionnaire_completed_at = datetime.utcnow()
        
        db.commit()
        
        # Genera PDF e QR code (asincrono)
        from services.pdf_generator import PDFGenerator
        pdf_generator = PDFGenerator()
        
        if evaluation_result["compliance_result"] == "positivo":
            pdf_path = await pdf_generator.generate_passport_pdf(assessment, db)
        else:
            pdf_path = await pdf_generator.generate_recall_pdf(assessment, db)
        
        qr_path = await pdf_generator.generate_qr_code(assessment.unique_hash)
        
        # Aggiorna paths
        if evaluation_result["compliance_result"] == "positivo":
            assessment.pdf_passport_path = pdf_path
        else:
            assessment.pdf_recall_path = pdf_path
        assessment.qr_code_path = qr_path
        
        db.commit()
        
        return {
            "success": True,
            "message": "Questionario completato con successo",
            "assessment_id": assessment.id,
            "compliance_result": evaluation_result["compliance_result"],
            "score_percentage": evaluation_result["score_percentage"],
            "essential_questions_passed": evaluation_result["essential_questions_passed"],
            "verification_url": f"{settings.QR_BASE_URL}/{assessment.unique_hash}",
            "completed_at": assessment.questionnaire_completed_at
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Errore nel salvataggio del questionario: {str(e)}"
        )

def apply_iso27001_algorithm(responses: Dict[str, str], manifest: Dict[str, Any]) -> Dict[str, str]:
    """
    Applica l'algoritmo ISO 27001 che preimposta il 90% delle risposte a SÌ
    """
    iso_questions = manifest.get("iso27001_coverage", {}).get("applicable_questions", [])
    
    # Crea una copia delle risposte
    updated_responses = responses.copy()
    
    # Preimposta a SÌ tutte le domande coperte da ISO 27001
    for question_id in iso_questions:
        updated_responses[question_id] = "SI"
    
    return updated_responses

@router.get("/status/{hash}", response_model=dict)
async def get_assessment_status(
    hash: str,
    db: Session = Depends(get_db)
):
    """
    Ottiene lo status di un assessment tramite hash
    """
    assessment = db.query(Assessment).filter(
        Assessment.unique_hash == hash
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment non trovato"
        )
    
    return {
        "hash": assessment.unique_hash,
        "status": assessment.status.value,
        "compliance_result": assessment.compliance_result.value if assessment.compliance_result else None,
        "score_percentage": assessment.score_percentage,
        "expires_at": assessment.expires_at,
        "completed_at": assessment.questionnaire_completed_at,
        "supplier_name": assessment.supplier.ragione_sociale
    } 