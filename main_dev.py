from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
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
import qrcode
import base64
from io import BytesIO
import tempfile
import os

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
    
    # Tabella admin
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabella aziende
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            admin_email TEXT UNIQUE NOT NULL,
            admin_password TEXT NOT NULL,
            sector TEXT NOT NULL,
            address TEXT,
            city TEXT,
            postal_code TEXT,
            country TEXT DEFAULT 'Italia',
            phone TEXT,
            piva TEXT,
            cf TEXT,
            website TEXT,
            description TEXT,
            status TEXT DEFAULT 'active',
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
            assessment_token TEXT,
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
            evaluation_result TEXT,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
        )
    ''')
    
    # Aggiungi colonna evaluation_result se non esiste
    try:
        cursor.execute('ALTER TABLE assessments ADD COLUMN evaluation_result TEXT')
    except sqlite3.OperationalError:
        pass  # La colonna esiste già
    
    # Aggiungi colonna completed_at se non esiste
    try:
        cursor.execute('ALTER TABLE assessments ADD COLUMN completed_at TIMESTAMP')
    except sqlite3.OperationalError:
        pass  # La colonna esiste già
    
    # Inserisci admin di default
    cursor.execute('SELECT COUNT(*) FROM admins')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO admins (username, email, password_hash) 
            VALUES ('admin', 'admin@nis2platform.com', 'admin123')
        ''')
    
    # Inserisci azienda demo
    cursor.execute('SELECT COUNT(*) FROM companies')
    if cursor.fetchone()[0] == 0:
        cursor.execute('''
            INSERT INTO companies (name, admin_email, admin_password, sector, address, city, postal_code, phone, piva, cf, website, description) 
            VALUES ('Azienda Demo', 'admin@company.com', 'admin', 'Tecnologia', 'Via Roma 123', 'Milano', '20100', '+39 02 1234567', '12345678901', 'ABCDEF12G34H567I', 'https://www.aziendademo.com', 'Azienda leader nel settore tecnologico specializzata in soluzioni digitali innovative')
        ''')
        
        # Inserisci fornitori di esempio SENZA punteggi
        suppliers_data = [
            ('ABC Tech Solutions', 'info@abctech.com', 1),
            ('XYZ Systems', 'contact@xyzsystems.com', 1),
            ('DEF Innovations', 'hello@definnovations.com', 1),
            ('GHI Digital', 'info@ghidigital.com', 1),
            ('JKL Software', 'contact@jklsoftware.com', 1)
        ]
        
        for supplier in suppliers_data:
            cursor.execute('''
                INSERT INTO suppliers (name, email, company_id)
                VALUES (?, ?, ?)
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

# Funzione per generare QR code
def generate_qr_code(data: str) -> str:
    """Genera un QR code e lo restituisce come base64"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Converti in base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

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
    return RedirectResponse(url="/admin-login")

@app.get("/admin-login")
async def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

@app.post("/api/auth/admin-login")
async def admin_login(email: str = Form(...), password: str = Form(...)):
    # Credenziali admin
    if email == "admin@nis2platform.com" and password == "admin123":
        access_token = create_access_token(data={
            "sub": email, 
            "role": "admin", 
            "username": "admin"
        })
        response = RedirectResponse(url="/admin-dashboard", status_code=302)
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        return response
    else:
        return RedirectResponse(url="/admin-login?error=invalid", status_code=302)

@app.get("/admin-dashboard")
async def admin_dashboard(request: Request):
    user = await get_current_user(request)
    if not user or user.get("role") != "admin":
        return RedirectResponse(url="/admin-login")
    
    try:
        # Inizializza il database se non esiste
        init_db()
        
        conn = sqlite3.connect('nis2_supply_chain.db')
        cursor = conn.cursor()
        
        # Ottieni statistiche generali
        cursor.execute('SELECT COUNT(*) FROM companies')
        total_companies = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM suppliers')
        total_suppliers = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM suppliers WHERE compliance_score IS NOT NULL')
        completed_assessments = cursor.fetchone()[0]
        
        # Ottieni lista aziende
        cursor.execute('''
            SELECT id, name, admin_email, sector, status, created_at, city, phone, piva,
                   (SELECT COUNT(*) FROM suppliers WHERE company_id = companies.id) as supplier_count
            FROM companies
            ORDER BY created_at DESC
        ''')
        
        companies = cursor.fetchall()
        conn.close()
        
        context = {
            "request": request,
            "total_companies": total_companies,
            "total_suppliers": total_suppliers,
            "completed_assessments": completed_assessments,
            "companies": companies
        }
        
        return templates.TemplateResponse("admin_dashboard.html", context)
    except Exception as e:
        print(f"Errore nel dashboard admin: {e}")
        return templates.TemplateResponse("admin_dashboard.html", {
            "request": request,
            "total_companies": 0,
            "total_suppliers": 0,
            "completed_assessments": 0,
            "companies": [],
            "error": str(e)
        })

@app.get("/admin/companies")
async def admin_companies_page(request: Request):
    user = await get_current_user(request)
    if not user or user.get("role") != "admin":
        return RedirectResponse(url="/admin-login")
    
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, admin_email, sector, status, created_at, city, phone, piva,
               (SELECT COUNT(*) FROM suppliers WHERE company_id = companies.id) as supplier_count
        FROM companies
        ORDER BY created_at DESC
    ''')
    
    companies = cursor.fetchall()
    conn.close()
    
    context = {
        "request": request,
        "companies": companies
    }
    
    return templates.TemplateResponse("admin_companies.html", context)

@app.post("/api/admin/companies")
async def create_company(request: Request, name: str = Form(...), admin_email: str = Form(...), 
                        admin_password: str = Form(...), sector: str = Form(...), address: str = Form(None),
                        city: str = Form(None), postal_code: str = Form(None), country: str = Form("Italia"),
                        phone: str = Form(None), piva: str = Form(None), cf: str = Form(None),
                        website: str = Form(None), description: str = Form(None)):
    user = await get_current_user(request)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Non autorizzato")
    
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO companies (name, admin_email, admin_password, sector, address, city, postal_code, 
                                 country, phone, piva, cf, website, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, admin_email, admin_password, sector, address, city, postal_code, 
              country, phone, piva, cf, website, description))
        
        conn.commit()
        conn.close()
        
        return RedirectResponse(url="/admin/companies?success=created", status_code=302)
    except sqlite3.IntegrityError:
        conn.close()
        return RedirectResponse(url="/admin/companies?error=duplicate", status_code=302)

@app.delete("/api/admin/companies/{company_id}")
async def delete_company(request: Request, company_id: int):
    user = await get_current_user(request)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Non autorizzato")
    
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    # Elimina prima i fornitori associati
    cursor.execute('DELETE FROM suppliers WHERE company_id = ?', (company_id,))
    
    # Poi elimina l'azienda
    cursor.execute('DELETE FROM companies WHERE id = ?', (company_id,))
    
    conn.commit()
    conn.close()
    
    return {"success": True, "message": "Azienda eliminata con successo"}

@app.get("/admin/companies/{company_id}/edit")
async def edit_company_page(request: Request, company_id: int):
    """Pagina per modificare un'azienda"""
    user = await get_current_user(request)
    if not user or user.get("role") != "admin":
        return RedirectResponse(url="/admin-login")
    
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name, admin_email, sector, status, address, city, postal_code, country, phone, piva, cf, website, description FROM companies WHERE id = ?', (company_id,))
    company = cursor.fetchone()
    conn.close()
    
    if not company:
        raise HTTPException(status_code=404, detail="Azienda non trovata")
    
    context = {
        "request": request,
        "company": {
            "id": company[0],
            "name": company[1],
            "admin_email": company[2],
            "sector": company[3],
            "status": company[4],
            "address": company[5],
            "city": company[6],
            "postal_code": company[7],
            "country": company[8],
            "phone": company[9],
            "piva": company[10],
            "cf": company[11],
            "website": company[12],
            "description": company[13]
        }
    }
    
    return templates.TemplateResponse("edit_company.html", context)

@app.post("/api/admin/companies/{company_id}/edit")
async def edit_company(request: Request, company_id: int, name: str = Form(...), 
                      admin_email: str = Form(...), sector: str = Form(...), 
                      status: str = Form(...), address: str = Form(None),
                      city: str = Form(None), postal_code: str = Form(None), country: str = Form("Italia"),
                      phone: str = Form(None), piva: str = Form(None), cf: str = Form(None),
                      website: str = Form(None), description: str = Form(None)):
    """Modifica un'azienda esistente"""
    user = await get_current_user(request)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=401, detail="Non autorizzato")
    
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE companies 
            SET name = ?, admin_email = ?, sector = ?, status = ?, address = ?, city = ?, postal_code = ?,
                country = ?, phone = ?, piva = ?, cf = ?, website = ?, description = ?
            WHERE id = ?
        ''', (name, admin_email, sector, status, address, city, postal_code, 
              country, phone, piva, cf, website, description, company_id))
        
        conn.commit()
        conn.close()
        
        return RedirectResponse(url="/admin/companies?success=updated", status_code=302)
    except sqlite3.IntegrityError:
        conn.close()
        return RedirectResponse(url=f"/admin/companies/{company_id}/edit?error=duplicate", status_code=302)
    except Exception as e:
        conn.close()
        return RedirectResponse(url=f"/admin/companies/{company_id}/edit?error=unknown", status_code=302)

@app.get("/company-login")
async def company_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/api/auth/company-login")
async def company_login(email: str = Form(...), password: str = Form(...)):
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    # Cerca l'azienda nel database
    cursor.execute('SELECT id, name, admin_email, admin_password FROM companies WHERE admin_email = ? AND status = "active"', (email,))
    company = cursor.fetchone()
    conn.close()
    
    if company and company[3] == password:  # company[3] è admin_password
        company_id, company_name = company[0], company[1]
        access_token = create_access_token(data={
            "sub": email, 
            "role": "company", 
            "company_name": company_name,
            "company_id": company_id
        })
        response = RedirectResponse(url=f"/company-dashboard/{company_id}", status_code=302)
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
    
    cursor.execute('SELECT name, admin_email, address, city, postal_code, country, phone, piva, cf, website, description FROM companies WHERE id = ?', (company_id,))
    company = cursor.fetchone()
    
    if not company:
        conn.close()
        raise HTTPException(status_code=404, detail="Azienda non trovata")
    
    # Ottieni statistiche fornitori
    cursor.execute('''
        SELECT 
            COUNT(*) as total,
            COALESCE(SUM(CASE WHEN compliance_score >= 70 THEN 1 ELSE 0 END), 0) as conformi,
            COALESCE(SUM(CASE WHEN compliance_score < 70 THEN 1 ELSE 0 END), 0) as non_conformi
        FROM suppliers WHERE company_id = ?
    ''', (company_id,))
    
    stats = cursor.fetchone()
    total_suppliers, conformi, non_conformi = stats
    
    # Calcola tasso di conformità
    compliance_rate = (conformi / total_suppliers * 100) if total_suppliers > 0 else 0
    
    # Ottieni fornitori recenti
    cursor.execute('''
        SELECT id, name, email, compliance_score, risk_level, assessment_date
        FROM suppliers 
        WHERE company_id = ?
        ORDER BY assessment_date DESC NULLS LAST, created_at DESC
        LIMIT 10
    ''', (company_id,))
    
    recent_suppliers = []
    for row in cursor.fetchall():
        supplier_id, name, email, compliance_score, risk_level, assessment_date = row
        recent_suppliers.append({
            'id': supplier_id,
            'name': name,
            'email': email,
            'sector': 'N/A',  # Non disponibile nella tabella
            'compliance_score': compliance_score or 0,
            'last_assessment_date': assessment_date
        })
    
    # Ottieni notifiche recenti (simulate per ora)
    recent_notifications = [
        {
            'type': 'success',
            'title': 'Assessment Completato',
            'message': 'TechCorp ha completato la valutazione NIS2',
            'timestamp': datetime.now()
        },
        {
            'type': 'warning',
            'title': 'Scadenza Imminente',
            'message': '3 fornitori hanno assessment in scadenza',
            'timestamp': datetime.now()
        },
        {
            'type': 'info',
            'title': 'Nuovo Fornitore',
            'message': 'Digital Solutions è stato aggiunto alla piattaforma',
            'timestamp': datetime.now()
        }
    ]
    
    conn.close()
    
    # Prepara statistiche per il template professionale
    stats_data = {
        'compliant_count': conformi,
        'non_compliant_count': non_conformi,
        'total_assessments': total_suppliers,
        'compliance_rate': compliance_rate,
        'total_suppliers': total_suppliers
    }
    
    context = {
        "request": request,
        "company_id": company_id,
        "company_name": company[0],
        "company_email": company[1],
        "company_address": company[2] or "N/A",
        "company_city": company[3] or "N/A",
        "company_postal_code": company[4] or "N/A",
        "company_country": company[5] or "N/A",
        "company_phone": company[6] or "N/A",
        "company_piva": company[7] or "N/A",
        "company_cf": company[8] or "N/A",
        "company_website": company[9] or "N/A",
        "company_description": company[10] or "N/A",
        "admin_name": user.get("sub", "Admin"),
        "stats": stats_data,
        "recent_suppliers": recent_suppliers,
        "recent_notifications": recent_notifications
    }
    
    return templates.TemplateResponse("professional_dashboard.html", context)

@app.get("/suppliers")
async def suppliers_page(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/company-login")
    
    # Ottieni l'ID dell'azienda dall'utente loggato
    company_id = user.get("company_id")
    if not company_id:
        return RedirectResponse(url="/company-login")
    
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, email, compliance_score, risk_level, assessment_date
        FROM suppliers
        WHERE company_id = ?
        ORDER BY name
    ''', (company_id,))
    
    suppliers = cursor.fetchall()
    conn.close()
    
    context = {
        "request": request,
        "suppliers": suppliers,
        "user": user
    }
    
    return templates.TemplateResponse("suppliers.html", context)

@app.post("/api/suppliers")
async def add_supplier(request: Request, name: str = Form(...), email: str = Form(...)):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Non autorizzato")
    
    # Ottieni l'ID dell'azienda dall'utente loggato
    company_id = user.get("company_id")
    if not company_id:
        raise HTTPException(status_code=401, detail="Azienda non trovata")
    
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO suppliers (name, email, company_id)
        VALUES (?, ?, ?)
    ''', (name, email, company_id))
    
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
        "supplier_id": supplier_id,
        "user": user
    }
    
    return templates.TemplateResponse("assessment.html", context)

@app.post("/api/send-assessment/{supplier_id}")
async def send_assessment(request: Request, supplier_id: int):
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Non autorizzato")
    
    # Genera un token unico per l'assessment
    assessment_token = secrets.token_urlsafe(32)
    
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    # Aggiorna il fornitore con il token dell'assessment
    cursor.execute('''
        UPDATE suppliers 
        SET assessment_token = ?
        WHERE id = ?
    ''', (assessment_token, supplier_id))
    
    conn.commit()
    conn.close()
    
    # Genera il link per l'assessment
    assessment_link = f"http://localhost:8000/assessment-form/{assessment_token}"
    
    return {"success": True, "message": "Assessment inviato con successo", "assessment_link": assessment_link}

@app.get("/assessment-form/{token}")
async def assessment_form(request: Request, token: str):
    """Pagina per compilare l'assessment NIS2"""
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    # Trova il fornitore con questo token
    cursor.execute('''
        SELECT s.id, s.name, s.email, c.name as company_name
        FROM suppliers s
        JOIN companies c ON s.company_id = c.id
        WHERE s.assessment_token = ?
    ''', (token,))
    
    supplier = cursor.fetchone()
    conn.close()
    
    if not supplier:
        raise HTTPException(status_code=404, detail="Assessment non trovato o già completato")
    
    context = {
        "request": request,
        "supplier": supplier,
        "token": token
    }
    
    return templates.TemplateResponse("assessment_form.html", context)

@app.post("/api/submit-assessment/{token}")
async def submit_assessment(request: Request, token: str):
    """Riceve e processa l'assessment compilato"""
    try:
        # Leggi i dati JSON
        data = await request.json()
        

        
        conn = sqlite3.connect('nis2_supply_chain.db')
        cursor = conn.cursor()
        
        # Trova il fornitore
        cursor.execute('SELECT id FROM suppliers WHERE assessment_token = ?', (token,))
        supplier = cursor.fetchone()
        
        if not supplier:
            conn.close()
            raise HTTPException(status_code=404, detail="Assessment non trovato")
        
        supplier_id = supplier[0]
        
        # Calcola il punteggio basato sulle risposte NIS2
        total_score = 0
        questions_answered = 0
        
        # Processa tutte le domande NIS2 (formato q_GSI.03_1, q_GSI.03_2, etc.)
        for key, value in data.items():
            if key.startswith('q_') and value in ['si', 'no', 'na']:
                questions_answered += 1
                if value == 'si':
                    total_score += 100
                elif value == 'na':
                    total_score += 50  # Peso parziale per "Non Applicabile"
                # 'no' = 0 punti
        
        if questions_answered == 0:
            conn.close()
            raise HTTPException(status_code=400, detail="Nessuna risposta fornita")
        
        # Calcola il punteggio percentuale
        score = int((total_score / (questions_answered * 100)) * 100)
        risk_level = "Basso" if score >= 70 else "Medio" if score >= 50 else "Alto"
        
        # Aggiorna il fornitore con i risultati
        cursor.execute('''
            UPDATE suppliers 
            SET compliance_score = ?, risk_level = ?, assessment_date = CURRENT_TIMESTAMP, assessment_token = NULL
            WHERE id = ?
        ''', (score, risk_level, supplier_id))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Assessment completato con successo", "score": score}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Errore nel processare l'assessment: {str(e)}")

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
    
    try:
        # Importa il generatore PDF professionale
        from pdf_generator_professional import ProfessionalNIS2PDFGenerator
        
        conn = sqlite3.connect('nis2_supply_chain.db')
        cursor = conn.cursor()
        
        # Ottieni dati del fornitore e dell'azienda
        cursor.execute('''
            SELECT s.id, s.name, s.email, s.address, s.city, s.compliance_score, s.assessment_date,
                   c.name as company_name
            FROM suppliers s
            JOIN companies c ON s.company_id = c.id
            WHERE s.id = ? AND s.compliance_score IS NOT NULL
        ''', (supplier_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Nessun assessment completato trovato per questo fornitore")
        
        # Crea dati assessment compatibili
        assessment_data = {
            'id': result[0],
            'status': 'completed',
            'evaluation_result': json.dumps({
                'outcome': 'POSITIVO' if result[5] >= 70 else 'NEGATIVO',
                'compliance_score': result[5] or 0,
                'section_scores': {
                    'Governance della Sicurezza': result[5] or 0,
                    'Gestione del Rischio': result[5] or 0,
                    'Risposta agli Incidenti': result[5] or 0,
                    'Continuità Aziendale': result[5] or 0,
                    'Protezione dei Dati': result[5] or 0,
                    'Controlli di Accesso': result[5] or 0
                }
            }),
            'completed_at': result[6] or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        supplier_data = {
            'company_name': result[1],
            'email': result[2],
            'address': result[3] or 'N/A',
            'city': result[4] or 'N/A'
        }
        
        company_data = {
            'name': result[7]
        }
        
        # Verifica che il fornitore sia conforme
        if result[5] < 70:
            raise HTTPException(status_code=400, detail="Il fornitore non è conforme per generare un certificato")
        
        # Genera il PDF
        generator = ProfessionalNIS2PDFGenerator()
        output_dir = "static/pdfs"
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"passaporto_nis2_{supplier_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(output_dir, filename)
        
        generator.generate_passport_pdf(assessment_data, supplier_data, company_data, output_path)
        
        # Restituisci il file PDF
        return FileResponse(
            path=output_path,
            filename=filename,
            media_type='application/pdf'
        )
        
    except Exception as e:
        print(f"Errore generazione PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Errore nella generazione del PDF: {str(e)}")

@app.get("/warning/{supplier_id}")
async def generate_warning_pdf(request: Request, supplier_id: int):
    """Genera PDF di richiamo per fornitori non conformi"""
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/company-login")
    
    try:
        # Importa il generatore PDF professionale
        from pdf_generator_professional import ProfessionalNIS2PDFGenerator
        
        conn = sqlite3.connect('nis2_supply_chain.db')
        cursor = conn.cursor()
        
        # Ottieni dati del fornitore e dell'azienda
        cursor.execute('''
            SELECT s.id, s.name, s.email, s.address, s.city, s.compliance_score, s.assessment_date,
                   c.name as company_name
            FROM suppliers s
            JOIN companies c ON s.company_id = c.id
            WHERE s.id = ? AND s.compliance_score IS NOT NULL
        ''', (supplier_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Nessun assessment completato trovato per questo fornitore")
        
        # Crea dati assessment compatibili
        assessment_data = {
            'id': result[0],
            'status': 'completed',
            'evaluation_result': json.dumps({
                'outcome': 'POSITIVO' if result[5] >= 70 else 'NEGATIVO',
                'compliance_score': result[5] or 0,
                'section_scores': {
                    'Governance della Sicurezza': result[5] or 0,
                    'Gestione del Rischio': result[5] or 0,
                    'Risposta agli Incidenti': result[5] or 0,
                    'Continuità Aziendale': result[5] or 0,
                    'Protezione dei Dati': result[5] or 0,
                    'Controlli di Accesso': result[5] or 0
                }
            }),
            'completed_at': result[6] or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        supplier_data = {
            'company_name': result[1],
            'email': result[2],
            'address': result[3] or 'N/A',
            'city': result[4] or 'N/A'
        }
        
        company_data = {
            'name': result[7]
        }
        
        # Verifica che il fornitore NON sia conforme
        if result[5] >= 70:
            raise HTTPException(status_code=400, detail="Il fornitore è conforme, non è necessario un richiamo")
        
        # Genera il PDF
        generator = ProfessionalNIS2PDFGenerator()
        output_dir = "static/pdfs"
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"richiamo_nis2_{supplier_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        output_path = os.path.join(output_dir, filename)
        
        generator.generate_recall_pdf(assessment_data, supplier_data, company_data, output_path)
        
        # Restituisci il file PDF
        return FileResponse(
            path=output_path,
            filename=filename,
            media_type='application/pdf'
        )
        
    except Exception as e:
        print(f"Errore generazione PDF: {e}")
        raise HTTPException(status_code=500, detail=f"Errore nella generazione del PDF: {str(e)}")

@app.get("/verify/{certificate_hash}")
async def verify_certificate(request: Request, certificate_hash: str):
    """Verifica l'autenticità di un certificato tramite QR code"""
    # Decodifica l'hash per ottenere l'ID del fornitore
    try:
        # Per semplicità, assumiamo che l'hash sia l'ID del fornitore
        supplier_id = int(certificate_hash)
    except ValueError:
        context = {
            "request": request,
            "is_valid": False,
            "supplier_data": None,
            "certificate_hash": certificate_hash,
            "verification_date": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        return templates.TemplateResponse("verification.html", context)
    
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
        context = {
            "request": request,
            "is_valid": False,
            "supplier_data": None,
            "certificate_hash": certificate_hash,
            "verification_date": datetime.now().strftime("%d/%m/%Y %H:%M")
        }
        return templates.TemplateResponse("verification.html", context)
    
    supplier_name, compliance_score, assessment_date, company_name = supplier_data
    
    # Verifica che il fornitore sia conforme (≥70%) per considerare valido
    is_valid = compliance_score is not None and compliance_score >= 70
    
    context = {
        "request": request,
        "is_valid": is_valid,
        "supplier_data": supplier_data,
        "certificate_hash": certificate_hash,
        "verification_date": datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    
    return templates.TemplateResponse("verification.html", context)

@app.get("/v/{certificate_hash}")
async def view_certificate(request: Request, certificate_hash: str):
    # Ottieni l'utente corrente
    user = await get_current_user(request)
    
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
    
    # Verifica che il fornitore sia conforme (≥70%) per mostrare il certificato
    if compliance_score is None:
        raise HTTPException(status_code=400, detail="Assessment non ancora completato")
    
    if compliance_score < 70:
        raise HTTPException(status_code=400, detail="Fornitore non conforme - Certificato non disponibile")
    
    # Ottieni i dati completi del fornitore e dell'azienda per il certificato
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.email, s.address, s.city, c.address as company_address, c.city as company_city
        FROM suppliers s
        JOIN companies c ON s.company_id = c.id
        WHERE s.id = ?
    ''', (supplier_id,))
    
    supplier_details = cursor.fetchone()
    conn.close()
    
    if supplier_details:
        supplier_email, supplier_address, supplier_city, company_address, company_city = supplier_details
        
        # Genera testo certificazione per QR code
        certificate_text = f"Questo certificato attesta che il fornitore {supplier_name} ({supplier_address}, {supplier_city}, {supplier_email}) è conforme alla Direttiva NIS2 e rientra nella lista dei fornitori certificati di {company_name}. Certificato N° {supplier_id} - Data: {assessment_date}"
        
        # Genera QR code con il testo della certificazione
        qr_code_data = generate_qr_code(certificate_text)
    else:
        # Fallback se non troviamo i dettagli
        supplier_email = "N/A"
        supplier_address = "N/A"
        supplier_city = "N/A"
        company_address = "N/A"
        company_city = "N/A"
        certificate_text = f"Questo certificato attesta che il fornitore {supplier_name} è conforme alla Direttiva NIS2 e rientra nella lista dei fornitori certificati di {company_name}. Certificato N° {supplier_id} - Data: {assessment_date}"
        qr_code_data = generate_qr_code(certificate_text)
    
    context = {
        "request": request,
        "supplier_name": supplier_name,
        "compliance_score": compliance_score,
        "assessment_date": assessment_date,
        "company_name": company_name,
        "company_address": company_address or "N/A",
        "company_city": company_city or "N/A",
        "supplier_email": supplier_email or "N/A",
        "supplier_address": supplier_address or "N/A",
        "supplier_city": supplier_city or "N/A",
        "company_postal_code": "N/A",
        "company_country": "N/A",
        "company_phone": "N/A",
        "company_piva": "N/A",
        "company_cf": "N/A",
        "company_website": "N/A",
        "company_description": "N/A",
        "certificate_hash": certificate_hash,
        "qr_code": qr_code_data,
        "user": user
    }
    
    return templates.TemplateResponse("certificate.html", context)

@app.get("/qr/{assessment_id}")
async def generate_qr_image(assessment_id: int):
    """Genera immagine QR per il sito web del fornitore"""
    try:
        conn = sqlite3.connect('nis2_supply_chain.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT a.id, a.status, a.evaluation_result, a.completed_at,
                   s.name, s.email, s.address, s.city,
                   c.name as company_name
            FROM assessments a
            JOIN suppliers s ON a.supplier_id = s.id
            JOIN companies c ON s.company_id = c.id
            WHERE a.id = ?
        """, (assessment_id,))
        
        result = cursor.fetchone()
        if not result:
            return {"error": "Assessment non trovato"}
        
        # Genera QR code con URL della piattaforma
        qr_data = f"https://nis2-supply-chain.ondigitalocean.app/v/{assessment_id}"
        
        import qrcode
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Converti in bytes
        from io import BytesIO
        img_buffer = BytesIO()
        qr_img.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        return Response(
            content=img_buffer.getvalue(),
            media_type="image/png",
            headers={"Content-Disposition": f"attachment; filename=nis2_qr_{assessment_id}.png"}
        )
        
    except Exception as e:
        return {"error": str(e)}
    finally:
        conn.close()

@app.get("/new-supplier")
async def new_supplier_page(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/company-login")
    
    return templates.TemplateResponse("new_supplier.html", {"request": request, "user": user})

@app.get("/send-assessment")
async def send_assessment_page(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/company-login")
    
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    # Ottieni l'ID dell'azienda dall'utente loggato
    company_id = user.get("company_id")
    if not company_id:
        return RedirectResponse(url="/company-login")
    
    cursor.execute('''
        SELECT id, name, email
        FROM suppliers
        WHERE compliance_score IS NULL AND company_id = ?
        ORDER BY name
    ''', (company_id,))
    
    suppliers = cursor.fetchall()
    conn.close()
    
    context = {
        "request": request,
        "suppliers": suppliers,
        "user": user
    }
    
    return templates.TemplateResponse("send_assessment.html", context)

@app.get("/assessments")
async def assessments_page(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/company-login")
    
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    # Ottieni l'ID dell'azienda dall'utente loggato
    company_id = user.get("company_id")
    if not company_id:
        return RedirectResponse(url="/company-login")
    
    cursor.execute('''
        SELECT id, name, email, compliance_score, risk_level, assessment_date
        FROM suppliers
        WHERE compliance_score IS NOT NULL AND company_id = ?
        ORDER BY assessment_date DESC
    ''', (company_id,))
    
    assessments = cursor.fetchall()
    conn.close()
    
    # Prepara i dati per il template professionale
    assessment_list = []
    for row in assessments:
        supplier_id, name, email, compliance_score, risk_level, assessment_date = row
        assessment_list.append({
            'id': supplier_id,
            'name': name,
            'email': email,
            'compliance_score': compliance_score or 0,
            'risk_level': risk_level or 'N/A',
            'assessment_date': assessment_date
        })
    
    context = {
        "request": request,
        "assessments": assessment_list,
        "user": user,
        "company_id": company_id
    }
    
    return templates.TemplateResponse("professional_assessments.html", context)

@app.get("/thank-you/{score}")
async def thank_you_page(request: Request, score: int):
    """Pagina di ringraziamento dopo aver completato l'assessment"""
    context = {
        "request": request,
        "score": score
    }
    
    return templates.TemplateResponse("thank_you.html", context)

@app.get("/admin-logout")
async def admin_logout():
    response = RedirectResponse(url="/admin-login")
    response.delete_cookie("access_token")
    return response

@app.get("/company-logout")
async def company_logout():
    response = RedirectResponse(url="/company-login")
    response.delete_cookie("access_token")
    return response

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/edit-supplier/{supplier_id}")
async def edit_supplier_page(request: Request, supplier_id: int):
    """Pagina per modificare un fornitore"""
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/company-login")
    
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name, email, address, city FROM suppliers WHERE id = ?', (supplier_id,))
    supplier = cursor.fetchone()
    conn.close()
    
    if not supplier:
        raise HTTPException(status_code=404, detail="Fornitore non trovato")
    
    context = {
        "request": request,
        "supplier": {
            "id": supplier[0],
            "name": supplier[1],
            "email": supplier[2],
            "address": supplier[3] or "",
            "city": supplier[4] or ""
        },
        "user": user
    }
    
    return templates.TemplateResponse("edit_supplier.html", context)

@app.post("/api/edit-supplier/{supplier_id}")
async def edit_supplier(request: Request, supplier_id: int, name: str = Form(...), 
                       email: str = Form(...), address: str = Form(None), city: str = Form(None)):
    """Modifica un fornitore esistente"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Non autorizzato")
    
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            UPDATE suppliers 
            SET name = ?, email = ?, address = ?, city = ?
            WHERE id = ?
        ''', (name, email, address, city, supplier_id))
        
        conn.commit()
        conn.close()
        
        return RedirectResponse(url="/suppliers?success=updated", status_code=302)
    except Exception as e:
        conn.close()
        return RedirectResponse(url=f"/edit-supplier/{supplier_id}?error=unknown", status_code=302)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)