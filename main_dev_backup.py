from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import sqlite3
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
import jwt
from pydantic import BaseModel

app = FastAPI(title="NIS2 Supply Chain Platform", version="1.0.0")

# Configurazione JWT
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Modelli Pydantic
class User(BaseModel):
    id: int
    username: str
    email: str
    role: str

class Company(BaseModel):
    id: int
    name: str
    admin_email: str
    sector: str

class Supplier(BaseModel):
    id: int
    name: str
    email: str
    company_id: int
    compliance_score: Optional[int] = None
    risk_level: Optional[str] = None

# Configurazione database
def init_db():
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    # Tabella aziende
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            admin_email TEXT UNIQUE NOT NULL,
            sector TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabella fornitori
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            company_id INTEGER NOT NULL,
            compliance_score INTEGER,
            risk_level TEXT,
            assessment_date TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    ''')
    
    # Tabella assessment
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supplier_id INTEGER NOT NULL,
            questionnaire_data TEXT NOT NULL,
            score INTEGER NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
        )
    ''')
    
    # Inserisci dati di esempio
    cursor.execute('SELECT COUNT(*) FROM companies')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO companies (name, admin_email, sector) 
            VALUES ('Azienda Demo', 'admin@company.com', 'Tecnologia')
        ''')
        
        # Inserisci fornitori di esempio
        suppliers_data = [
            ('ABC Tech Solutions', 'info@abctech.com', 1, 85, 'Basso'),
            ('XYZ Systems', 'contact@xyzsystems.com', 1, 72, 'Medio'),
            ('DEF Innovations', 'hello@definnovations.com', 1, 45, 'Alto'),
            ('GHI Digital', 'info@ghidigital.com', 1, 92, 'Basso'),
            ('JKL Software', 'contact@jklsoftware.com', 1, 68, 'Medio')
        ]
        
        for supplier in suppliers_data:
            cursor.execute('''
                INSERT INTO suppliers (name, email, company_id, compliance_score, risk_level)
                VALUES (?, ?, ?, ?, ?)
            ''', supplier)
    
    conn.commit()
    conn.close()

# Inizializza il database
init_db()

# Configurazione template e static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Funzioni JWT
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.PyJWTError:
        return None

# Funzione per ottenere l'utente corrente
async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    payload = verify_token(token)
    if not payload:
        return None
    return payload

# Routes
@app.get("/")
async def root():
    return RedirectResponse(url="/company-login")

@app.get("/company-login")
async def company_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/api/auth/company-login")
async def company_login(email: str = Form(...), password: str = Form(...)):
    # Credenziali semplificate per il demo
    if (email == "admin@company.com" and password == "admin") or \
       (email == "demo@company.com" and password == "demo"):
        access_token = create_access_token(data={
            "sub": email, 
            "role": "company", 
            "company_name": "Azienda Demo"
        })
        response = RedirectResponse(url="/company-dashboard/1", status_code=302)
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        return response
    else:
        return RedirectResponse(url="/company-login?error=invalid", status_code=302)

@app.get("/company-dashboard/{company_id}")
async def company_dashboard(request: Request, company_id: int):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/company-login")
    
    # Ottieni dati dell'azienda
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT name, admin_email FROM companies WHERE id = ?', (company_id,))
    company = cursor.fetchone()
    
    if not company:
        conn.close()
        raise HTTPException(status_code=404, detail="Azienda non trovata")
    
    # Ottieni statistiche fornitori
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN compliance_score >= 70 THEN 1 ELSE 0 END) as conformi,
            SUM(CASE WHEN compliance_score < 70 THEN 1 ELSE 0 END) as non_conformi
        FROM suppliers WHERE company_id = ?
    ''', (company_id,))
    
    stats = cursor.fetchone()
    total_suppliers, conformi, non_conformi = stats
    
    # Ottieni distribuzione livelli di rischio
    cursor.execute('''
        SELECT 
            risk_level,
            COUNT(*) as count
        FROM suppliers 
        WHERE company_id = ? AND risk_level IS NOT NULL
        GROUP BY risk_level
    ''', (company_id,))
    
    risk_distribution = cursor.fetchall()
    risk_data = {'Basso': 0, 'Medio': 0, 'Alto': 0, 'Critico': 0}
    for risk_level, count in risk_distribution:
        risk_data[risk_level] = count
    
    # Ottieni attività recenti
    cursor.execute('''
        SELECT s.name, s.compliance_score, s.assessment_date
        FROM suppliers s
        WHERE s.company_id = ?
        ORDER BY s.assessment_date DESC
        LIMIT 5
    ''', (company_id,))
    
    recent_activities = cursor.fetchall()
    conn.close()
    
    context = {
        "request": request,
        "company_id": company_id,
        "company_name": company[0],
        "admin_name": user.get("sub", "Admin"),
        "total_suppliers": total_suppliers,
        "conformi": conformi,
        "non_conformi": non_conformi,
        "risk_data": risk_data,
        "recent_activities": recent_activities
    }
    
    return templates.TemplateResponse("dashboard.html", context)

@app.get("/suppliers")
async def suppliers_page(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/company-login")
    
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, email, compliance_score, risk_level, assessment_date
        FROM suppliers
        ORDER BY name
    ''')
    
    suppliers = cursor.fetchall()
    conn.close()
    
    context = {
        "request": request,
        "suppliers": suppliers
    }
    
    return templates.TemplateResponse("suppliers.html", context)

@app.post("/api/suppliers")
async def add_supplier(request: Request, name: str = Form(...), email: str = Form(...)):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Non autorizzato")
    
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO suppliers (name, email, company_id)
        VALUES (?, ?, 1)
    ''', (name, email))
    
    conn.commit()
    conn.close()
    
    return RedirectResponse(url="/suppliers", status_code=302)

@app.get("/assessment/{supplier_id}")
async def view_assessment(request: Request, supplier_id: int):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/company-login")
    
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.name, s.email, s.compliance_score, s.risk_level, s.assessment_date
        FROM suppliers s
        WHERE s.id = ?
    ''', (supplier_id,))
    
    supplier = cursor.fetchone()
    conn.close()
    
    if not supplier:
        raise HTTPException(status_code=404, detail="Fornitore non trovato")
    
    context = {
        "request": request,
        "supplier": supplier,
        "supplier_id": supplier_id
    }
    
    return templates.TemplateResponse("assessment.html", context)

@app.post("/api/send-assessment/{supplier_id}")
async def send_assessment(request: Request, supplier_id: int):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Non autorizzato")
    
    # Simula l'invio dell'assessment
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    # Aggiorna il fornitore con un punteggio simulato
    import random
    score = random.randint(45, 95)
    risk_level = "Basso" if score >= 70 else "Medio" if score >= 50 else "Alto"
    
    cursor.execute('''
        UPDATE suppliers 
        SET compliance_score = ?, risk_level = ?, assessment_date = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (score, risk_level, supplier_id))
    
    conn.commit()
    conn.close()
    
    return {"success": True, "message": "Assessment inviato con successo"}

@app.delete("/api/suppliers/{supplier_id}")
async def delete_supplier(request: Request, supplier_id: int):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Non autorizzato")
    
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM suppliers WHERE id = ?', (supplier_id,))
    conn.commit()
    conn.close()
    
    return {"success": True, "message": "Fornitore eliminato con successo"}

@app.get("/certificate/{supplier_id}")
async def generate_certificate_pdf(request: Request, supplier_id: int):
    """Genera PDF di certificazione per fornitori conformi"""
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/company-login")
    
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.name, s.compliance_score, s.assessment_date, c.name as company_name
        FROM suppliers s
        JOIN companies c ON s.company_id = c.id
        WHERE s.id = ?
    ''', (supplier_id,))
    
    supplier_data = cursor.fetchone()
    conn.close()
    
    if not supplier_data:
        raise HTTPException(status_code=404, detail="Fornitore non trovato")
    
    supplier_name, compliance_score, assessment_date, company_name = supplier_data
    
    # Verifica che il fornitore sia conforme (≥70%)
    if compliance_score < 70:
        raise HTTPException(status_code=400, detail="Il fornitore non è conforme per generare un certificato")
    
    context = {
        "request": request,
        "supplier_name": supplier_name,
        "compliance_score": compliance_score,
        "assessment_date": assessment_date,
        "company_name": company_name,
        "supplier_id": supplier_id
    }
    
    return templates.TemplateResponse("certificate_pdf.html", context)

@app.get("/warning/{supplier_id}")
async def generate_warning_pdf(request: Request, supplier_id: int):
    """Genera PDF di richiamo per fornitori non conformi"""
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/company-login")
    
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.name, s.compliance_score, s.assessment_date, c.name as company_name
        FROM suppliers s
        JOIN companies c ON s.company_id = c.id
        WHERE s.id = ?
    ''', (supplier_id,))
    
    supplier_data = cursor.fetchone()
    conn.close()
    
    if not supplier_data:
        raise HTTPException(status_code=404, detail="Fornitore non trovato")
    
    supplier_name, compliance_score, assessment_date, company_name = supplier_data
    
    # Verifica che il fornitore NON sia conforme (<70%)
    if compliance_score >= 70:
        raise HTTPException(status_code=400, detail="Il fornitore è conforme, non è necessario un richiamo")
    
    context = {
        "request": request,
        "supplier_name": supplier_name,
        "compliance_score": compliance_score,
        "assessment_date": assessment_date,
        "company_name": company_name,
        "supplier_id": supplier_id
    }
    
    return templates.TemplateResponse("warning_pdf.html", context)

@app.get("/v/{certificate_hash}")
async def view_certificate(request: Request, certificate_hash: str):
    # Decodifica l'hash per ottenere l'ID del fornitore
    try:
        # Per semplicità, assumiamo che l'hash sia l'ID del fornitore
        supplier_id = int(certificate_hash)
    except ValueError:
        raise HTTPException(status_code=404, detail="Certificato non valido")
    
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    # Cerca il fornitore specifico
    cursor.execute('''
        SELECT s.name, s.compliance_score, s.assessment_date, c.name as company_name
        FROM suppliers s
        JOIN companies c ON s.company_id = c.id
        WHERE s.id = ?
    ''', (supplier_id,))
    
    supplier_data = cursor.fetchone()
    conn.close()
    
    if not supplier_data:
        raise HTTPException(status_code=404, detail="Certificato non trovato")
    
    supplier_name, compliance_score, assessment_date, company_name = supplier_data
    
    context = {
        "request": request,
        "supplier_name": supplier_name,
        "compliance_score": compliance_score,
        "assessment_date": assessment_date,
        "company_name": company_name,
        "certificate_hash": certificate_hash
    }
    
    return templates.TemplateResponse("certificate.html", context)

@app.get("/v/{certificate_hash}")
async def view_certificate(request: Request, certificate_hash: str):
    # Decodifica l'hash per ottenere l'ID del fornitore
    try:
        # Per semplicità, assumiamo che l'hash sia l'ID del fornitore
        supplier_id = int(certificate_hash)
    except ValueError:
        raise HTTPException(status_code=404, detail="Certificato non valido")
    
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    # Cerca il fornitore specifico
    cursor.execute('''
        SELECT s.name, s.compliance_score, s.assessment_date, c.name as company_name
        FROM suppliers s
        JOIN companies c ON s.company_id = c.id
        WHERE s.id = ?
    ''', (supplier_id,))
    
    supplier_data = cursor.fetchone()
    conn.close()
    
    if not supplier_data:
        raise HTTPException(status_code=404, detail="Certificato non trovato")
    
    supplier_name, compliance_score, assessment_date, company_name = supplier_data
    
    context = {
        "request": request,
        "supplier_name": supplier_name,
        "compliance_score": compliance_score,
        "assessment_date": assessment_date,
        "company_name": company_name,
        "certificate_hash": certificate_hash
    }
    
    return templates.TemplateResponse("certificate.html", context)

@app.get("/new-supplier")
async def new_supplier_page(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/company-login")
    
    return templates.TemplateResponse("new_supplier.html", {"request": request})

@app.get("/send-assessment")
async def send_assessment_page(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/company-login")
    
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, email
        FROM suppliers
        WHERE compliance_score IS NULL
        ORDER BY name
    ''')
    
    suppliers = cursor.fetchall()
    conn.close()
    
    context = {
        "request": request,
        "suppliers": suppliers
    }
    
    return templates.TemplateResponse("send_assessment.html", context)

@app.get("/assessments")
async def assessments_page(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/company-login")
    
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, email, compliance_score, risk_level, assessment_date
        FROM suppliers
        WHERE compliance_score IS NOT NULL
        ORDER BY assessment_date DESC
    ''')
    
    assessments = cursor.fetchall()
    conn.close()
    
    context = {
        "request": request,
        "assessments": assessments
    }
    
    return templates.TemplateResponse("assessments.html", context)

@app.get("/company-logout")
async def company_logout():
    response = RedirectResponse(url="/company-login")
    response.delete_cookie("access_token")
    return response

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
