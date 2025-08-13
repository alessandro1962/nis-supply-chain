from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db, Assessment, AssessmentStatus
from config import settings

router = APIRouter()

def get_db():
    from database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/passport/{hash}", response_class=HTMLResponse)
async def verify_passport(
    hash: str,
    db: Session = Depends(get_db)
):
    """
    Pagina pubblica di verifica per QR code (accessibile senza autenticazione)
    """
    # Trova assessment tramite hash
    assessment = db.query(Assessment).filter(
        Assessment.unique_hash == hash
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Passaporto non trovato"
        )
    
    # Controlla se completato
    if assessment.status != AssessmentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment non completato"
        )
    
    # Controlla validità (14 giorni)
    if assessment.expires_at and datetime.utcnow() > assessment.expires_at:
        status_message = "SCADUTO"
        status_class = "expired"
    else:
        status_message = "VALIDO"
        status_class = "valid"
    
    # Dati per la pagina
    supplier = assessment.supplier
    company = supplier.company
    
    compliance_status = assessment.compliance_result.value if assessment.compliance_result else "Non determinato"
    compliance_class = "positive" if compliance_status == "positivo" else "negative"
    
    # Template HTML responsive
    html_template = f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Verifica Passaporto Digitale NIS2 - {supplier.ragione_sociale}</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                line-height: 1.6;
                color: #333;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            
            .container {{
                max-width: 800px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            
            .header {{
                background: linear-gradient(45deg, #2c3e50, #3498db);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            
            .header h1 {{
                font-size: 2rem;
                margin-bottom: 10px;
            }}
            
            .header p {{
                opacity: 0.9;
                font-size: 1.1rem;
            }}
            
            .content {{
                padding: 40px;
            }}
            
            .status-badge {{
                display: inline-block;
                padding: 12px 24px;
                border-radius: 25px;
                font-weight: bold;
                font-size: 1.1rem;
                margin-bottom: 30px;
            }}
            
            .status-badge.positive {{
                background: #d4edda;
                color: #155724;
                border: 2px solid #c3e6cb;
            }}
            
            .status-badge.negative {{
                background: #f8d7da;
                color: #721c24;
                border: 2px solid #f5c6cb;
            }}
            
            .status-badge.valid {{
                background: #d1ecf1;
                color: #0c5460;
                border: 2px solid #bee5eb;
            }}
            
            .status-badge.expired {{
                background: #f8d7da;
                color: #721c24;
                border: 2px solid #f5c6cb;
            }}
            
            .info-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 30px;
                margin: 30px 0;
            }}
            
            .info-card {{
                background: #f8f9fa;
                padding: 25px;
                border-radius: 10px;
                border-left: 4px solid #3498db;
            }}
            
            .info-card h3 {{
                color: #2c3e50;
                margin-bottom: 15px;
                font-size: 1.3rem;
            }}
            
            .info-item {{
                margin-bottom: 10px;
            }}
            
            .info-label {{
                font-weight: 600;
                color: #555;
            }}
            
            .info-value {{
                color: #333;
                margin-left: 10px;
            }}
            
            .score-section {{
                background: linear-gradient(45deg, #f39c12, #e67e22);
                color: white;
                padding: 25px;
                border-radius: 10px;
                text-align: center;
                margin: 30px 0;
            }}
            
            .score-value {{
                font-size: 3rem;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            
            .footer {{
                background: #2c3e50;
                color: white;
                padding: 25px;
                text-align: center;
            }}
            
            .footer p {{
                opacity: 0.8;
                margin-bottom: 5px;
            }}
            
            @media (max-width: 768px) {{
                .container {{
                    margin: 10px;
                    border-radius: 10px;
                }}
                
                .header {{
                    padding: 20px;
                }}
                
                .header h1 {{
                    font-size: 1.5rem;
                }}
                
                .content {{
                    padding: 25px;
                }}
                
                .info-grid {{
                    grid-template-columns: 1fr;
                    gap: 20px;
                }}
                
                .score-value {{
                    font-size: 2rem;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛡️ Passaporto Digitale NIS2</h1>
                <p>Verifica Conformità Fornitori alla Direttiva NIS2</p>
            </div>
            
            <div class="content">
                <div style="text-align: center;">
                    <span class="status-badge {compliance_class}">
                        {'✅ CONFORME' if compliance_status == 'positivo' else '❌ NON CONFORME'}
                    </span>
                    <span class="status-badge {status_class}">
                        {'🟢 ' + status_message if status_class == 'valid' else '🔴 ' + status_message}
                    </span>
                </div>
                
                <div class="info-grid">
                    <div class="info-card">
                        <h3>📋 Fornitore</h3>
                        <div class="info-item">
                            <span class="info-label">Ragione Sociale:</span>
                            <span class="info-value">{supplier.ragione_sociale}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Email:</span>
                            <span class="info-value">{supplier.email}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Città:</span>
                            <span class="info-value">{supplier.citta}</span>
                        </div>
                    </div>
                    
                    <div class="info-card">
                        <h3>🏢 Azienda Cliente</h3>
                        <div class="info-item">
                            <span class="info-label">Ragione Sociale:</span>
                            <span class="info-value">{company.ragione_sociale}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Città:</span>
                            <span class="info-value">{company.citta}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Tipo Soggetto:</span>
                            <span class="info-value">{company.tipo_soggetto.value.title()}</span>
                        </div>
                    </div>
                </div>
                
                <div class="score-section">
                    <div class="score-value">{assessment.score_percentage:.1f}%</div>
                    <h3>Punteggio di Conformità</h3>
                    <p>Soglia minima richiesta: 80%</p>
                </div>
                
                <div class="info-grid">
                    <div class="info-card">
                        <h3>📊 Dettagli Assessment</h3>
                        <div class="info-item">
                            <span class="info-label">Certificazione ISO 27001:</span>
                            <span class="info-value">{'✅ Sì' if assessment.has_iso27001 else '❌ No'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Domande Essenziali:</span>
                            <span class="info-value">{'✅ Soddisfatte' if assessment.essential_questions_passed else '❌ Non Soddisfatte'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Data Completamento:</span>
                            <span class="info-value">{assessment.questionnaire_completed_at.strftime('%d/%m/%Y %H:%M') if assessment.questionnaire_completed_at else 'N/A'}</span>
                        </div>
                    </div>
                    
                    <div class="info-card">
                        <h3>⏰ Validità</h3>
                        <div class="info-item">
                            <span class="info-label">Data Scadenza:</span>
                            <span class="info-value">{assessment.expires_at.strftime('%d/%m/%Y %H:%M') if assessment.expires_at else 'N/A'}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">Hash Verifica:</span>
                            <span class="info-value" style="font-family: monospace; font-size: 0.9rem;">{assessment.unique_hash[:16]}...</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <p><strong>Piattaforma NIS2 Supplier Assessment</strong></p>
                <p>Questo documento è stato generato automaticamente e ha valore di certificazione digitale</p>
                <p>Verificato il: {datetime.utcnow().strftime('%d/%m/%Y %H:%M UTC')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_template

@router.get("/api/passport/{hash}", response_model=dict)
async def verify_passport_api(
    hash: str,
    db: Session = Depends(get_db)
):
    """
    API endpoint per verifica programmatica del passaporto
    """
    assessment = db.query(Assessment).filter(
        Assessment.unique_hash == hash
    ).first()
    
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Passaporto non trovato"
        )
    
    if assessment.status != AssessmentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assessment non completato"
        )
    
    # Controlla validità
    is_valid = True
    if assessment.expires_at and datetime.utcnow() > assessment.expires_at:
        is_valid = False
    
    supplier = assessment.supplier
    company = supplier.company
    
    return {
        "hash": assessment.unique_hash,
        "is_valid": is_valid,
        "compliance_result": assessment.compliance_result.value if assessment.compliance_result else None,
        "score_percentage": assessment.score_percentage,
        "essential_questions_passed": assessment.essential_questions_passed,
        "has_iso27001": assessment.has_iso27001,
        "supplier": {
            "ragione_sociale": supplier.ragione_sociale,
            "email": supplier.email,
            "citta": supplier.citta
        },
        "client_company": {
            "ragione_sociale": company.ragione_sociale,
            "citta": company.citta,
            "tipo_soggetto": company.tipo_soggetto.value
        },
        "completed_at": assessment.questionnaire_completed_at,
        "expires_at": assessment.expires_at
    } 