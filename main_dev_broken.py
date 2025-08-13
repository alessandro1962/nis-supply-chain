import os
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List
import json

from fastapi import FastAPI, HTTPException, Depends, status, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import jwt
from datetime import datetime, timedelta
import hashlib

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
    company_name: str
    email: str
    sector: str
    country: str

class LoginRequest(BaseModel):
    username: str
    password: str

# App FastAPI
app = FastAPI(
    title="Piattaforma NIS2 Supplier Assessment - DEV",
    description="Backend di sviluppo per la piattaforma NIS2",
    version="1.0.0-dev"
)

# Monta i file statici
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT Configuration
SECRET_KEY = "your-super-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Security
security = HTTPBearer()

# Funzioni di autenticazione
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
    except:
        return None

# Middleware per verificare autenticazione
async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        print("❌ Nessun token trovato nei cookie")
        return None
    try:
        payload = verify_token(token)
        if not payload:
            print("❌ Token non valido")
            return None
        print(f"✅ Token valido: {payload}")
        return payload
    except Exception as e:
        print(f"❌ Errore verifica token: {e}")
        return None

# Database helper
def get_db_connection():
    return sqlite3.connect("nis2_platform.db")

# Routes
@app.get("/")
async def root():
    return RedirectResponse(url="/login")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "nis2-platform-api-dev"}

@app.post("/api/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    # Login con JWT
    if username == "admin" and password == "secret123":
        access_token = create_access_token(
            data={"sub": username, "role": "admin"}
        )
        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        return response
    raise HTTPException(status_code=401, detail="Credenziali non valide")

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie(key="access_token")
    return response

@app.get("/api/admin/stats")
async def get_admin_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Conta aziende
    cursor.execute("SELECT COUNT(*) FROM companies")
    total_companies = cursor.fetchone()[0]
    
    # Conta fornitori
    cursor.execute("SELECT COUNT(*) FROM suppliers")
    total_suppliers = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "totalCompanies": total_companies,
        "totalSuppliers": total_suppliers,
        "completedAssessments": 0,
        "conformSuppliers": 0
    }

@app.get("/api/admin/companies")
async def get_companies():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM companies")
    companies = []
    for row in cursor.fetchall():
        companies.append({
            "id": row[0],
            "name": row[1],
            "admin_email": row[2],
            "sector": row[3],
            "vat_number": row[4] if len(row) > 4 else "",
            "fiscal_code": row[5] if len(row) > 5 else "",
            "address": row[6] if len(row) > 6 else "",
            "city": row[7] if len(row) > 7 else "",
            "postal_code": row[8] if len(row) > 8 else "",
            "country": row[9] if len(row) > 9 else "",
            "phone": row[10] if len(row) > 10 else "",
            "website": row[11] if len(row) > 11 else "",
            "contact_person": row[12] if len(row) > 12 else "",
            "contact_phone": row[13] if len(row) > 13 else "",
            "contact_email": row[14] if len(row) > 14 else "",
            "company_size": row[15] if len(row) > 15 else "",
            "industry": row[16] if len(row) > 16 else "",
            "notes": row[17] if len(row) > 17 else "",
            "created_at": row[18] if len(row) > 18 else row[4]
        })
    
    conn.close()
    return companies

@app.get("/api/admin/companies/{company_id}")
async def get_company_detail(company_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Azienda non trovata")
    
    company = {
        "id": row[0],
        "name": row[1],
        "admin_email": row[2],
        "sector": row[3],
        "vat_number": row[4] if len(row) > 4 else "",
        "fiscal_code": row[5] if len(row) > 5 else "",
        "address": row[6] if len(row) > 6 else "",
        "city": row[7] if len(row) > 7 else "",
        "postal_code": row[8] if len(row) > 8 else "",
        "country": row[9] if len(row) > 9 else "",
        "phone": row[10] if len(row) > 10 else "",
        "website": row[11] if len(row) > 11 else "",
        "contact_person": row[12] if len(row) > 12 else "",
        "contact_phone": row[13] if len(row) > 13 else "",
        "contact_email": row[14] if len(row) > 14 else "",
        "company_size": row[15] if len(row) > 15 else "",
        "industry": row[16] if len(row) > 16 else "",
        "notes": row[17] if len(row) > 17 else "",
        "created_at": row[18] if len(row) > 18 else row[4]
    }
    
    # Conta i fornitori dell'azienda
    cursor.execute("SELECT COUNT(*) FROM suppliers WHERE company_id = ?", (company_id,))
    suppliers_count = cursor.fetchone()[0]
    company["suppliers_count"] = suppliers_count
    
    conn.close()
    return company

@app.get("/api/company/{company_id}/suppliers")
async def get_company_suppliers(company_id: int, request: Request):
    # Verifica autenticazione
    user = await get_current_user(request)
    if not user or user.get('role') != 'company':
        raise HTTPException(status_code=401, detail="Non autorizzato")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Ottieni fornitori con informazioni sugli assessment
        cursor.execute("""
            SELECT 
                s.id, 
                s.company_name, 
                s.email, 
                s.sector, 
                s.country, 
                s.created_at,
                COUNT(a.id) as total_assessments,
                MAX(a.completed_at) as last_assessment_date
            FROM suppliers s
            LEFT JOIN assessments a ON s.id = a.supplier_id
            WHERE s.company_id = ?
            GROUP BY s.id, s.company_name, s.email, s.sector, s.country, s.created_at
            ORDER BY s.created_at DESC
        """, (company_id,))
        
        suppliers = []
        for row in cursor.fetchall():
            supplier_id = row[0]
            total_assessments = row[6] or 0
            last_assessment_date = row[7]
            
            suppliers.append({
                "id": supplier_id,
                "company_name": row[1],
                "email": row[2],
                "sector": row[3],
                "country": row[4],
                "created_at": row[5],
                "total_assessments": total_assessments,
                "last_assessment_date": last_assessment_date,
                "assessments_url": f"/supplier-assessments/{company_id}/{supplier_id}"
            })
        
        return suppliers
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel recupero fornitori: {str(e)}")
    finally:
        conn.close()

@app.get("/api/company/{company_id}/suppliers/{supplier_id}/assessment")
async def get_supplier_assessment(company_id: int, supplier_id: int, request: Request):
    """Ottiene i dettagli dell'ultimo assessment di un fornitore"""
    # Verifica autenticazione
    user = await get_current_user(request)
    if not user or user.get('role') != 'company':
        raise HTTPException(status_code=401, detail="Non autorizzato")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Ottieni l'ultimo assessment completato del fornitore
        cursor.execute("""
            SELECT 
                a.id,
                a.assessment_token,
                a.status,
                a.evaluation_result,
                a.completed_at,
                s.company_name,
                s.email,
                s.sector
            FROM assessments a
            JOIN suppliers s ON a.supplier_id = s.id
            WHERE s.company_id = ? AND a.supplier_id = ? AND a.status = 'completed'
            ORDER BY a.completed_at DESC
            LIMIT 1
        """, (company_id, supplier_id))
        
        assessment = cursor.fetchone()
        
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment non trovato")
        
        # Parsa il risultato della valutazione
        evaluation_result = None
        if assessment[3]:  # evaluation_result
            try:
                import json
                evaluation_result = json.loads(assessment[3])
            except:
                evaluation_result = {"error": "Errore nel parsing del risultato"}
        
        return {
            "id": assessment[0],
            "assessment_token": assessment[1],
            "status": assessment[2],
            "evaluation_result": evaluation_result,
            "completed_at": assessment[4],
            "supplier_name": assessment[5],
            "supplier_email": assessment[6],
            "supplier_sector": assessment[7]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel recupero assessment: {str(e)}")
    finally:
        conn.close()

@app.post("/api/company/{company_id}/suppliers")
async def create_supplier(
    company_id: int,
    request: Request,
    company_name: str = Form(...),
    email: str = Form(...),
    sector: str = Form(...),
    country: str = Form(...)
):
    # Verifica autenticazione
    user = await get_current_user(request)
    if not user or user.get('role') != 'company':
        raise HTTPException(status_code=401, detail="Non autorizzato")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO suppliers (company_id, company_name, email, sector, country, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (company_id, company_name, email, sector, country, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        supplier_id = cursor.lastrowid
        
        conn.close()
        return {"success": True, "message": "Fornitore creato con successo", "supplier_id": supplier_id}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Errore nella creazione del fornitore: {str(e)}")

@app.post("/api/company/{company_id}/suppliers/{supplier_id}/send-assessment")
async def send_supplier_assessment(company_id: int, supplier_id: int, request: Request):
    # Verifica autenticazione
    user = await get_current_user(request)
    if not user or user.get('role') != 'company':
        raise HTTPException(status_code=401, detail="Non autorizzato")
    """Invia assessment al fornitore"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verifica che il fornitore esista
        cursor.execute("SELECT * FROM suppliers WHERE id = ? AND company_id = ?", (supplier_id, company_id))
        supplier = cursor.fetchone()
        
        if not supplier:
            return {"success": False, "message": "Fornitore non trovato"}
        
        # Ottieni i dati dell'azienda
        cursor.execute("SELECT name FROM companies WHERE id = ?", (company_id,))
        company = cursor.fetchone()
        
        if not company:
            return {"success": False, "message": "Azienda non trovata"}
        
        # Genera un link unico per l'assessment
        import hashlib
        import time
        assessment_token = hashlib.md5(f"{supplier_id}_{company_id}_{time.time()}".encode()).hexdigest()
        
        # Salva l'assessment nel database (creiamo una tabella assessments)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_id INTEGER NOT NULL,
                company_id INTEGER NOT NULL,
                assessment_token TEXT UNIQUE NOT NULL,
                status TEXT DEFAULT 'sent',
                questionnaire_sent_at TEXT NOT NULL,
                completed_at TEXT,
                FOREIGN KEY (supplier_id) REFERENCES suppliers (id),
                FOREIGN KEY (company_id) REFERENCES companies (id)
            )
        """)
        
        cursor.execute("""
            INSERT INTO assessments (supplier_id, company_id, assessment_token, questionnaire_sent_at)
            VALUES (?, ?, ?, ?)
        """, (supplier_id, company_id, assessment_token, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        
        # Genera il link dell'assessment
        assessment_url = f"http://localhost:8000/assessment/{assessment_token}"
        
        # TODO: In un'implementazione reale, qui invieresti l'email
        # Per ora simuliamo l'invio
        print(f"📧 Assessment inviato a {supplier[2]} ({supplier[1]})")
        print(f"🔗 Link assessment: {assessment_url}")
        
        conn.commit()
        return {
            "success": True, 
            "message": f"Assessment inviato con successo a {supplier[1]}",
            "assessment_url": assessment_url
        }
        
    except Exception as e:
        conn.rollback()
        return {"success": False, "message": str(e)}
    finally:
        conn.close()

@app.get("/api/company/dashboard")
async def get_company_dashboard(request: Request):
    """Endpoint per ottenere i dati della dashboard azienda"""
    # Verifica autenticazione
    user = await get_current_user(request)
    if not user or user.get('role') != 'company':
        raise HTTPException(status_code=401, detail="Non autorizzato")
    
    company_id = user.get('company_id')
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Conta fornitori totali
        cursor.execute("SELECT COUNT(*) FROM suppliers WHERE company_id = ?", (company_id,))
        total_suppliers = cursor.fetchone()[0]
        
        # Conta assessment pendenti
        cursor.execute("""
            SELECT COUNT(*) FROM assessments a
            JOIN suppliers s ON a.supplier_id = s.id
            WHERE s.company_id = ? AND a.status = 'sent'
        """, (company_id,))
        pending_assessments = cursor.fetchone()[0]
        
        # Conta assessment completati
        cursor.execute("""
            SELECT COUNT(*) FROM assessments a
            JOIN suppliers s ON a.supplier_id = s.id
            WHERE s.company_id = ? AND a.status = 'completed'
        """, (company_id,))
        completed_assessments = cursor.fetchone()[0]
        
        # Conta fornitori conformi (assessment con risultato positivo)
        cursor.execute("""
            SELECT COUNT(*) FROM assessments a
            JOIN suppliers s ON a.supplier_id = s.id
            WHERE s.company_id = ? AND a.status = 'completed' 
            AND a.evaluation_result LIKE '%"outcome": "POSITIVO"%'
        """, (company_id,))
        conform_suppliers = cursor.fetchone()[0]
        
        # Conta fornitori non conformi
        cursor.execute("""
            SELECT COUNT(*) FROM assessments a
            JOIN suppliers s ON a.supplier_id = s.id
            WHERE s.company_id = ? AND a.status = 'completed' 
            AND a.evaluation_result LIKE '%"outcome": "NEGATIVO"%'
        """, (company_id,))
        non_conform_suppliers = cursor.fetchone()[0]
        
        # Calcola punteggio medio
        cursor.execute("""
            SELECT AVG(CAST(JSON_EXTRACT(a.evaluation_result, '$.final_score') AS FLOAT))
            FROM assessments a
            JOIN suppliers s ON a.supplier_id = s.id
            WHERE s.company_id = ? AND a.status = 'completed' 
            AND a.evaluation_result IS NOT NULL
        """, (company_id,))
        avg_score_result = cursor.fetchone()[0]
        average_score = round(avg_score_result, 1) if avg_score_result else 0
        
        return {
            "totalSuppliers": total_suppliers,
            "pendingAssessments": pending_assessments,
            "completedAssessments": completed_assessments,
            "conformSuppliers": conform_suppliers,
            "nonConformSuppliers": non_conform_suppliers,
            "averageScore": average_score
        }
        
    except Exception as e:
        print(f"Errore nel caricamento dashboard azienda: {e}")
        return {
            "totalSuppliers": 0,
            "pendingAssessments": 0,
            "completedAssessments": 0,
            "conformSuppliers": 0,
            "nonConformSuppliers": 0,
            "averageScore": 0
        }
    finally:
        conn.close()

@app.post("/api/auth/company-login")
async def company_login(email: str = Form(...), password: str = Form(...)):
    # Per ora usiamo l'email dell'amministratore come login
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, name, admin_email FROM companies WHERE admin_email = ?", (email,))
    company = cursor.fetchone()
    conn.close()
    
    if company and password == "company123":  # Password di default per le aziende
        print(f"🔐 Login azienda riuscito: {email} -> company_id: {company[0]}")
        access_token = create_access_token(
            data={"sub": email, "role": "company", "company_id": company[0], "company_name": company[1]}
        )
        response = RedirectResponse(url=f"/company-dashboard/{company[0]}", status_code=302)
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        print(f"🍪 Cookie impostato: {access_token[:20]}...")
        return response
    
    raise HTTPException(status_code=401, detail="Credenziali azienda non valide")

@app.post("/api/admin/companies")
async def create_company(
    name: str = Form(...),
    admin_email: str = Form(...),
    sector: str = Form(...),
    vat_number: str = Form(...),
    fiscal_code: str = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    postal_code: str = Form(...),
    country: str = Form(...),
    phone: str = Form(...),
    website: str = Form(None),
    contact_person: str = Form(...),
    contact_phone: str = Form(...),
    contact_email: str = Form(...),
    company_size: str = Form(...),
    industry: str = Form(...),
    notes: str = Form(None)
):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            """INSERT INTO companies (
                name, admin_email, sector, vat_number, fiscal_code, address, city, 
                postal_code, country, phone, website, contact_person, contact_phone, 
                contact_email, company_size, industry, notes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (name, admin_email, sector, vat_number, fiscal_code, address, city, 
             postal_code, country, phone, website, contact_person, contact_phone, 
             contact_email, company_size, industry, notes, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        company_id = cursor.lastrowid
        
        conn.close()
        return {"success": True, "message": "Azienda creata con successo", "company_id": company_id}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Errore nella creazione dell'azienda: {str(e)}")

@app.get("/questionario")
async def get_questionario():
    """Endpoint per visualizzare il questionario JSON"""
    try:
        with open("questionario_nis2.json", "r", encoding="utf-8") as f:
            questionario = json.load(f)
        return {
            "message": "Questionario NIS2 caricato con successo",
            "total_questions": len(questionario),
            "sections": list(set([q["codice_argomento"] for q in questionario])),
            "sample_questions": questionario[:3],  # Prime 3 domande come esempio
            "full_questionnaire": questionario
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File questionario non trovato")

@app.get("/login", response_class=HTMLResponse)
async def login_page():
    """Pagina di login"""
    html_content = """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login - Piattaforma NIS2</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 min-h-screen flex items-center justify-center">
        <div class="bg-white p-8 rounded-lg shadow-md w-96">
            <div class="text-center mb-8">
                <h1 class="text-3xl font-bold text-gray-900">🛡️ NIS2 Platform</h1>
                <p class="text-gray-600 mt-2">Accedi alla piattaforma</p>
            </div>
            
            <form method="POST" action="/api/auth/login">
                <div class="mb-4">
                    <label class="block text-gray-700 text-sm font-bold mb-2" for="username">
                        Username
                    </label>
                    <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" 
                           id="username" name="username" type="text" required>
                </div>
                
                <div class="mb-6">
                    <label class="block text-gray-700 text-sm font-bold mb-2" for="password">
                        Password
                    </label>
                    <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline" 
                           id="password" name="password" type="password" required>
                </div>
                
                <div class="flex items-center justify-between">
                    <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline w-full" 
                            type="submit">
                        Accedi
                    </button>
                </div>
            </form>
            
            <div class="mt-6 text-center text-sm text-gray-600">
                <p>Credenziali demo:</p>
                <p><strong>Username:</strong> admin</p>
                <p><strong>Password:</strong> secret123</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Dashboard protetta"""
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard - Piattaforma NIS2</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100">
        <!-- Header -->
        <header class="bg-white shadow-sm border-b border-gray-200">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between items-center py-4">
                    <div class="flex items-center">
                        <h1 class="text-2xl font-bold text-gray-900">🛡️ Piattaforma NIS2</h1>
                        <span class="ml-2 text-sm text-gray-500">Supplier Assessment</span>
                    </div>
                    <div class="flex items-center space-x-4">
                        <span class="text-sm text-gray-700">Benvenuto, {user.get('sub', 'Admin')}</span>
                        <a href="/logout" class="text-red-600 hover:text-red-800">Logout</a>
                    </div>
                </div>
            </div>
        </header>

        <!-- Main Content -->
        <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div class="bg-white p-6 rounded-lg shadow">
                    <h3 class="text-lg font-semibold text-gray-900 mb-2">Aziende Registrate</h3>
                    <p class="text-3xl font-bold text-blue-600" id="totalCompanies">0</p>
                </div>
                <div class="bg-white p-6 rounded-lg shadow">
                    <h3 class="text-lg font-semibold text-gray-900 mb-2">Fornitori Totali</h3>
                    <p class="text-3xl font-bold text-green-600" id="totalSuppliers">0</p>
                </div>
                <div class="bg-white p-6 rounded-lg shadow">
                    <h3 class="text-lg font-semibold text-gray-900 mb-2">Assessment Completati</h3>
                    <p class="text-3xl font-bold text-purple-600" id="completedAssessments">0</p>
                </div>
            </div>

            <div class="bg-white rounded-lg shadow">
                <div class="px-6 py-4 border-b border-gray-200">
                    <h2 class="text-xl font-semibold text-gray-900">Gestione Aziende</h2>
                </div>
                <div class="p-6">
                    <button onclick="openNewCompanyModal()" class="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 mb-4">
                        Nuova Azienda
                    </button>
                                         <div class="overflow-x-auto">
                         <table class="min-w-full divide-y divide-gray-200">
                             <thead class="bg-gray-50">
                                 <tr>
                                     <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Azienda</th>
                                     <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Contatto</th>
                                     <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Settore</th>
                                     <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Dimensione</th>
                                     <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Azioni</th>
                                 </tr>
                             </thead>
                             <tbody class="bg-white divide-y divide-gray-200" id="companiesTable">
                                 <tr>
                                     <td class="px-6 py-4 text-sm text-gray-500" colspan="5">Caricamento...</td>
                                 </tr>
                             </tbody>
                         </table>
                     </div>
                </div>
            </div>
        </main>

                 <!-- Modal Nuova Azienda -->
         <div id="newCompanyModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 hidden flex items-center justify-center p-4">
             <div class="bg-white p-8 rounded-lg shadow-lg w-4xl max-w-6xl max-h-[90vh] overflow-y-auto">
                <div class="flex justify-between items-center mb-6">
                    <h3 class="text-lg font-semibold text-gray-900">Nuova Azienda</h3>
                    <button onclick="closeNewCompanyModal()" class="text-gray-400 hover:text-gray-600">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
                
                                 <form id="newCompanyForm">
                     <!-- Informazioni Aziendali -->
                     <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
                         <div>
                             <label class="block text-gray-700 text-sm font-bold mb-2" for="companyName">
                                 Ragione Sociale *
                             </label>
                             <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" 
                                    id="companyName" name="name" type="text" required>
                         </div>
                         
                         <div>
                             <label class="block text-gray-700 text-sm font-bold mb-2" for="companySector">
                                 Settore NIS2 *
                             </label>
                             <select class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" 
                                     id="companySector" name="sector" required>
                                 <option value="">Seleziona settore</option>
                                 <option value="IT">IT - Tecnologia Informatica</option>
                                 <option value="FIN">FIN - Finanza</option>
                                 <option value="HEALTH">HEALTH - Sanità</option>
                                 <option value="ENERGY">ENERGY - Energia</option>
                                 <option value="TRANSPORT">TRANSPORT - Trasporti</option>
                                 <option value="WATER">WATER - Acqua</option>
                                 <option value="DIGITAL">DIGITAL - Servizi Digitali</option>
                                 <option value="SPACE">SPACE - Spazio</option>
                                 <option value="DEFENSE">DEFENSE - Difesa</option>
                                 <option value="FOOD">FOOD - Alimentare</option>
                                 <option value="CHEMICAL">CHEMICAL - Chimico</option>
                                 <option value="OTHER">OTHER - Altro</option>
                             </select>
                         </div>
                         
                         <div>
                             <label class="block text-gray-700 text-sm font-bold mb-2" for="adminEmail">
                                 Email Amministratore *
                             </label>
                             <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" 
                                    id="adminEmail" name="admin_email" type="email" required>
                         </div>
                     </div>

                     <!-- Dati Fiscali -->
                     <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
                         <div>
                             <label class="block text-gray-700 text-sm font-bold mb-2" for="vatNumber">
                                 Partita IVA *
                             </label>
                             <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" 
                                    id="vatNumber" name="vat_number" type="text" required>
                         </div>
                         
                         <div>
                             <label class="block text-gray-700 text-sm font-bold mb-2" for="fiscalCode">
                                 Codice Fiscale *
                             </label>
                             <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" 
                                    id="fiscalCode" name="fiscal_code" type="text" required>
                         </div>
                         
                         <div>
                             <label class="block text-gray-700 text-sm font-bold mb-2" for="phone">
                                 Telefono *
                             </label>
                             <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" 
                                    id="phone" name="phone" type="tel" required>
                         </div>
                     </div>

                     <!-- Indirizzo -->
                     <div class="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-6">
                         <div class="lg:col-span-2">
                             <label class="block text-gray-700 text-sm font-bold mb-2" for="address">
                                 Indirizzo *
                             </label>
                             <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" 
                                    id="address" name="address" type="text" required>
                         </div>
                         
                         <div>
                             <label class="block text-gray-700 text-sm font-bold mb-2" for="city">
                                 Città *
                             </label>
                             <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" 
                                    id="city" name="city" type="text" required>
                         </div>
                         
                         <div>
                             <label class="block text-gray-700 text-sm font-bold mb-2" for="postalCode">
                                 CAP *
                             </label>
                             <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" 
                                    id="postalCode" name="postal_code" type="text" required>
                         </div>
                     </div>

                     <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
                         <div>
                             <label class="block text-gray-700 text-sm font-bold mb-2" for="country">
                                 Paese *
                             </label>
                             <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" 
                                    id="country" name="country" type="text" value="Italia" required>
                         </div>
                         
                         <div>
                             <label class="block text-gray-700 text-sm font-bold mb-2" for="website">
                                 Sito Web
                             </label>
                             <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" 
                                    id="website" name="website" type="url" placeholder="https://www.example.com">
                         </div>
                         
                         <div>
                             <!-- Campo vuoto per bilanciare il layout -->
                         </div>
                     </div>

                     <!-- Contatto Principale -->
                     <div class="border-t pt-6 mb-6">
                         <h4 class="text-lg font-semibold text-gray-900 mb-4">Contatto Principale</h4>
                         
                         <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
                             <div>
                                 <label class="block text-gray-700 text-sm font-bold mb-2" for="contactPerson">
                                     Nome e Cognome *
                                 </label>
                                 <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" 
                                        id="contactPerson" name="contact_person" type="text" required>
                             </div>
                             
                             <div>
                                 <label class="block text-gray-700 text-sm font-bold mb-2" for="contactPhone">
                                     Telefono *
                                 </label>
                                 <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" 
                                        id="contactPhone" name="contact_phone" type="tel" required>
                             </div>
                             
                             <div>
                                 <label class="block text-gray-700 text-sm font-bold mb-2" for="contactEmail">
                                     Email *
                                 </label>
                                 <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" 
                                        id="contactEmail" name="contact_email" type="email" required>
                             </div>
                         </div>
                     </div>

                     <!-- Informazioni Aggiuntive -->
                     <div class="border-t pt-6 mb-6">
                         <h4 class="text-lg font-semibold text-gray-900 mb-4">Informazioni Aggiuntive</h4>
                         
                         <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
                             <div>
                                 <label class="block text-gray-700 text-sm font-bold mb-2" for="companySize">
                                     Dimensione Azienda *
                                 </label>
                                 <select class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" 
                                         id="companySize" name="company_size" required>
                                     <option value="">Seleziona dimensione</option>
                                     <option value="MICRO">Micro (1-10 dipendenti)</option>
                                     <option value="SMALL">Piccola (11-50 dipendenti)</option>
                                     <option value="MEDIUM">Media (51-250 dipendenti)</option>
                                     <option value="LARGE">Grande (250+ dipendenti)</option>
                                 </select>
                             </div>
                             
                             <div>
                                 <label class="block text-gray-700 text-sm font-bold mb-2" for="industry">
                                     Settore Industriale *
                                 </label>
                                 <select class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" 
                                         id="industry" name="industry" required>
                                     <option value="">Seleziona settore</option>
                                     <option value="MANUFACTURING">Manifatturiero</option>
                                     <option value="SERVICES">Servizi</option>
                                     <option value="TECHNOLOGY">Tecnologia</option>
                                     <option value="HEALTHCARE">Sanità</option>
                                     <option value="FINANCE">Finanza</option>
                                     <option value="ENERGY">Energia</option>
                                     <option value="TRANSPORT">Trasporti</option>
                                     <option value="RETAIL">Commercio</option>
                                     <option value="CONSTRUCTION">Costruzioni</option>
                                     <option value="OTHER">Altro</option>
                                 </select>
                             </div>
                         </div>
                         
                         <div class="mb-6">
                             <label class="block text-gray-700 text-sm font-bold mb-2" for="notes">
                                 Note Aggiuntive
                             </label>
                             <textarea class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" 
                                       id="notes" name="notes" rows="3" placeholder="Informazioni aggiuntive sull'azienda..."></textarea>
                         </div>
                     </div>
                    
                    <div class="flex items-center justify-between">
                        <button type="button" onclick="closeNewCompanyModal()" 
                                class="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
                            Annulla
                        </button>
                        <button type="submit" 
                                class="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline">
                            Crea Azienda
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <script>
            // Carica statistiche
            function loadStats() {{
                console.log('Caricamento statistiche...');
                fetch('/api/admin/stats')
                    .then(response => {{
                        console.log('Stats response status:', response.status);
                        return response.json();
                    }})
                    .then(data => {{
                        console.log('Stats data:', data);
                        document.getElementById('totalCompanies').textContent = data.totalCompanies;
                        document.getElementById('totalSuppliers').textContent = data.totalSuppliers;
                        document.getElementById('completedAssessments').textContent = data.completedAssessments;
                    }})
                    .catch(error => {{
                        console.error('Errore caricamento statistiche:', error);
                        document.getElementById('totalCompanies').textContent = 'ERR';
                        document.getElementById('totalSuppliers').textContent = 'ERR';
                        document.getElementById('completedAssessments').textContent = 'ERR';
                    }});
            }}

            // Carica aziende
            function loadCompanies() {{
                console.log('Caricamento aziende...');
                fetch('/api/admin/companies')
                    .then(response => {{
                        console.log('Companies response status:', response.status);
                        return response.json();
                    }})
                    .then(companies => {{
                        console.log('Companies data:', companies);
                        const tbody = document.getElementById('companiesTable');
                                                 if (companies.length === 0) {{
                             tbody.innerHTML = '<tr><td class="px-6 py-4 text-sm text-gray-500" colspan="5">Nessuna azienda registrata</td></tr>';
                         }} else {{
                             tbody.innerHTML = companies.map(company => `
                                 <tr>
                                     <td class="px-6 py-4 whitespace-nowrap">
                                         <div class="text-sm font-medium text-gray-900">${{company.name}}</div>
                                         <div class="text-sm text-gray-500">${{company.vat_number || 'N/A'}}</div>
                                     </td>
                                     <td class="px-6 py-4 whitespace-nowrap">
                                         <div class="text-sm text-gray-900">${{company.contact_person || 'N/A'}}</div>
                                         <div class="text-sm text-gray-500">${{company.contact_email || company.admin_email}}</div>
                                     </td>
                                     <td class="px-6 py-4 whitespace-nowrap">
                                         <div class="text-sm text-gray-900">${{company.sector}}</div>
                                         <div class="text-sm text-gray-500">${{company.industry || 'N/A'}}</div>
                                     </td>
                                     <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                         ${{company.company_size || 'N/A'}}
                                     </td>
                                     <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                         <a href="/company/${{company.id}}" class="text-blue-600 hover:text-blue-900 mr-2">Visualizza</a>
                                         <a href="/company-login" class="text-green-600 hover:text-green-900">Login Azienda</a>
                                     </td>
                                 </tr>
                             `).join('');
                         }}
                    }})
                                         .catch(error => {{
                         console.error('Errore caricamento aziende:', error);
                         const tbody = document.getElementById('companiesTable');
                         tbody.innerHTML = '<tr><td class="px-6 py-4 text-sm text-red-500" colspan="5">Errore nel caricamento delle aziende</td></tr>';
                     }});
            }}

            // Carica dati all'avvio
            loadStats();
            loadCompanies();

            // Modal functions
            function openNewCompanyModal() {{
                document.getElementById('newCompanyModal').classList.remove('hidden');
            }}

            function closeNewCompanyModal() {{
                document.getElementById('newCompanyModal').classList.add('hidden');
                document.getElementById('newCompanyForm').reset();
            }}

                         // Form submission
             document.getElementById('newCompanyForm').addEventListener('submit', function(e) {{
                 e.preventDefault();
                 
                 const formData = new FormData();
                 
                 // Informazioni Aziendali
                 formData.append('name', document.getElementById('companyName').value);
                 formData.append('sector', document.getElementById('companySector').value);
                 
                 // Dati Fiscali
                 formData.append('vat_number', document.getElementById('vatNumber').value);
                 formData.append('fiscal_code', document.getElementById('fiscalCode').value);
                 
                 // Indirizzo
                 formData.append('address', document.getElementById('address').value);
                 formData.append('city', document.getElementById('city').value);
                 formData.append('postal_code', document.getElementById('postalCode').value);
                 formData.append('country', document.getElementById('country').value);
                 formData.append('phone', document.getElementById('phone').value);
                 
                 // Sito Web
                 const website = document.getElementById('website').value;
                 if (website) formData.append('website', website);
                 
                 // Contatto Principale
                 formData.append('contact_person', document.getElementById('contactPerson').value);
                 formData.append('contact_phone', document.getElementById('contactPhone').value);
                 formData.append('contact_email', document.getElementById('contactEmail').value);
                 
                 // Informazioni Aggiuntive
                 formData.append('company_size', document.getElementById('companySize').value);
                 formData.append('industry', document.getElementById('industry').value);
                 formData.append('admin_email', document.getElementById('adminEmail').value);
                 
                 const notes = document.getElementById('notes').value;
                 if (notes) formData.append('notes', notes);
                 
                 console.log('Invio form azienda completa');
                 
                 fetch('/api/admin/companies', {{
                     method: 'POST',
                     body: formData
                 }})
                 .then(response => {{
                     console.log('Form response status:', response.status);
                     return response.json();
                 }})
                 .then(data => {{
                     console.log('Form response data:', data);
                     if (data.success) {{
                         alert('Azienda creata con successo!');
                         closeNewCompanyModal();
                         loadCompanies(); // Ricarica la lista
                         loadStats(); // Ricarica le statistiche
                     }} else {{
                         alert('Errore nella creazione dell\\'azienda: ' + data.message);
                     }}
                 }})
                 .catch(error => {{
                     console.error('Errore form submission:', error);
                     alert('Errore nella creazione dell\\'azienda: ' + error);
                 }});
             }});
        </script>
    </body>
    </html>
    """
    return html_content

@app.get("/company/{company_id}", response_class=HTMLResponse)
async def company_detail_page(company_id: int):
    """Pagina di dettaglio azienda"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM companies WHERE id = ?", (company_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Azienda non trovata")
    
    company = {
        "id": row[0],
        "name": row[1],
        "admin_email": row[2],
        "sector": row[3],
        "vat_number": row[4] if len(row) > 4 else "",
        "fiscal_code": row[5] if len(row) > 5 else "",
        "address": row[6] if len(row) > 6 else "",
        "city": row[7] if len(row) > 7 else "",
        "postal_code": row[8] if len(row) > 8 else "",
        "country": row[9] if len(row) > 9 else "",
        "phone": row[10] if len(row) > 10 else "",
        "website": row[11] if len(row) > 11 else "",
        "contact_person": row[12] if len(row) > 12 else "",
        "contact_phone": row[13] if len(row) > 13 else "",
        "contact_email": row[14] if len(row) > 14 else "",
        "company_size": row[15] if len(row) > 15 else "",
        "industry": row[16] if len(row) > 16 else "",
        "notes": row[17] if len(row) > 17 else "",
        "created_at": row[18] if len(row) > 18 else row[4]
    }
    
    conn.close()
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dettagli Azienda - {company['name']}</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100">
        <header class="bg-white shadow-sm border-b border-gray-200">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between items-center py-4">
                    <div class="flex items-center">
                        <a href="/dashboard" class="text-blue-600 hover:text-blue-800 mr-4">← Torna alla Dashboard</a>
                        <h1 class="text-2xl font-bold text-gray-900">🛡️ {company['name']}</h1>
                    </div>
                    <div class="flex items-center space-x-4">
                        <a href="/company-login" class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
                            Login Azienda
                        </a>
                    </div>
                </div>
            </div>
        </header>

        <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <!-- Informazioni Aziendali -->
                <div class="bg-white rounded-lg shadow p-6">
                    <h2 class="text-xl font-semibold text-gray-900 mb-4">Informazioni Aziendali</h2>
                    <div class="space-y-3">
                        <div>
                            <span class="font-medium text-gray-700">Ragione Sociale:</span>
                            <span class="ml-2 text-gray-900">{company['name']}</span>
                        </div>
                        <div>
                            <span class="font-medium text-gray-700">Settore NIS2:</span>
                            <span class="ml-2 text-gray-900">{company['sector']}</span>
                        </div>
                        <div>
                            <span class="font-medium text-gray-700">Settore Industriale:</span>
                            <span class="ml-2 text-gray-900">{company['industry'] or 'N/A'}</span>
                        </div>
                        <div>
                            <span class="font-medium text-gray-700">Dimensione:</span>
                            <span class="ml-2 text-gray-900">{company['company_size'] or 'N/A'}</span>
                        </div>
                    </div>
                </div>

                <!-- Dati Fiscali -->
                <div class="bg-white rounded-lg shadow p-6">
                    <h2 class="text-xl font-semibold text-gray-900 mb-4">Dati Fiscali</h2>
                    <div class="space-y-3">
                        <div>
                            <span class="font-medium text-gray-700">Partita IVA:</span>
                            <span class="ml-2 text-gray-900">{company['vat_number'] or 'N/A'}</span>
                        </div>
                        <div>
                            <span class="font-medium text-gray-700">Codice Fiscale:</span>
                            <span class="ml-2 text-gray-900">{company['fiscal_code'] or 'N/A'}</span>
                        </div>
                    </div>
                </div>

                <!-- Indirizzo -->
                <div class="bg-white rounded-lg shadow p-6">
                    <h2 class="text-xl font-semibold text-gray-900 mb-4">Indirizzo</h2>
                    <div class="space-y-3">
                        <div>
                            <span class="font-medium text-gray-700">Indirizzo:</span>
                            <span class="ml-2 text-gray-900">{company['address'] or 'N/A'}</span>
                        </div>
                        <div>
                            <span class="font-medium text-gray-700">Città:</span>
                            <span class="ml-2 text-gray-900">{company['city'] or 'N/A'}</span>
                        </div>
                        <div>
                            <span class="font-medium text-gray-700">CAP:</span>
                            <span class="ml-2 text-gray-900">{company['postal_code'] or 'N/A'}</span>
                        </div>
                        <div>
                            <span class="font-medium text-gray-700">Paese:</span>
                            <span class="ml-2 text-gray-900">{company['country'] or 'N/A'}</span>
                        </div>
                    </div>
                </div>

                <!-- Contatti -->
                <div class="bg-white rounded-lg shadow p-6">
                    <h2 class="text-xl font-semibold text-gray-900 mb-4">Contatti</h2>
                    <div class="space-y-3">
                        <div>
                            <span class="font-medium text-gray-700">Telefono:</span>
                            <span class="ml-2 text-gray-900">{company['phone'] or 'N/A'}</span>
                        </div>
                        <div>
                            <span class="font-medium text-gray-700">Email Amministratore:</span>
                            <span class="ml-2 text-gray-900">{company['admin_email']}</span>
                        </div>
                        <div>
                            <span class="font-medium text-gray-700">Sito Web:</span>
                            <span class="ml-2 text-gray-900">{company['website'] or 'N/A'}</span>
                        </div>
                        <div>
                            <span class="font-medium text-gray-700">Contatto Principale:</span>
                            <span class="ml-2 text-gray-900">{company['contact_person'] or 'N/A'}</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Note -->
            {f'''
            <div class="bg-white rounded-lg shadow p-6 mt-8">
                <h2 class="text-xl font-semibold text-gray-900 mb-4">Note</h2>
                <p class="text-gray-700">{company['notes'] or 'Nessuna nota disponibile'}</p>
            </div>
            ''' if company['notes'] else ''}
        </main>
    </body>
    </html>
    """
    return html_content

@app.get("/company-login", response_class=HTMLResponse)
async def company_login_page():
    """Pagina di login per le aziende"""
    html_content = """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login Azienda - Piattaforma NIS2</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-100 min-h-screen flex items-center justify-center">
        <div class="bg-white p-8 rounded-lg shadow-md w-96">
            <div class="text-center mb-8">
                <h1 class="text-3xl font-bold text-gray-900">🏢 Login Azienda</h1>
                <p class="text-gray-600 mt-2">Accedi alla piattaforma aziendale</p>
            </div>
            
            <form method="POST" action="/api/auth/company-login">
                <div class="mb-4">
                    <label class="block text-gray-700 text-sm font-bold mb-2" for="email">
                        Email Aziendale
                    </label>
                    <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" 
                           id="email" name="email" type="email" required>
                </div>
                
                <div class="mb-6">
                    <label class="block text-gray-700 text-sm font-bold mb-2" for="password">
                        Password
                    </label>
                    <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline" 
                           id="password" name="password" type="password" required>
                </div>
                
                <div class="flex items-center justify-between">
                    <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline w-full" 
                            type="submit">
                        Accedi
                    </button>
                </div>
            </form>
            
            <div class="mt-6 text-center text-sm text-gray-600">
                <p>Credenziali demo:</p>
                <p><strong>Email:</strong> [email dell'amministratore]</p>
                <p><strong>Password:</strong> company123</p>
            </div>
            
            <div class="mt-4 text-center">
                <a href="/dashboard" class="text-blue-600 hover:text-blue-800">← Torna alla Dashboard Admin</a>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

@app.get("/company-dashboard/{company_id}", response_class=HTMLResponse)
async def company_dashboard_page(company_id: int, request: Request):
    """Dashboard aziendale per gestire i fornitori"""
    user = await get_current_user(request)
    if not user or user.get('role') != 'company':
        return RedirectResponse(url="/company-login")
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dashboard Aziendale - {user.get('company_name', 'Azienda')}</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
        <style>
            .gradient-bg { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
            .glass-effect { backdrop-filter: blur(10px); background: rgba(255, 255, 255, 0.1); }
            .pulse-animation {{ animation: pulse 2s infinite; }}
            @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.7; }} }}
            .floating {{ animation: floating 3s ease-in-out infinite; }}
            @keyframes floating {{ 0%, 100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-10px); }} }}
            .card-hover { transition: all 0.3s ease; }
            .card-hover:hover { transform: translateY(-5px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); }
        </style>
    </head>
    <body class="bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 min-h-screen">
        <!-- Header Moderno -->
        <header class="gradient-bg text-white shadow-2xl">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div class="flex justify-between items-center py-6">
                    <div class="flex items-center space-x-4">
                        <div class="p-3 bg-white bg-opacity-20 rounded-xl">
                            <i class="fas fa-shield-alt text-2xl"></i>
                        </div>
                        <div>
                            <h1 class="text-3xl font-bold">{user.get('company_name', 'Azienda')}</h1>
                            <p class="text-blue-100 text-sm">🛡️ Piattaforma NIS2 Supply Chain</p>
                        </div>
                    </div>
                    <div class="flex items-center space-x-6">
                        <div class="text-right">
                            <p class="text-sm text-blue-100">Benvenuto</p>
                            <p class="font-semibold">{user.get('sub', 'Azienda')}</p>
                        </div>
                        <a href="/logout" class="bg-red-500 hover:bg-red-600 px-4 py-2 rounded-lg transition-all duration-200">
                            <i class="fas fa-sign-out-alt mr-2"></i>Logout
                        </a>
                    </div>
                </div>
            </div>
        </header>

        <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <!-- KPI Cards con Animazioni -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <div class="card-hover bg-gradient-to-br from-blue-500 to-blue-600 p-6 rounded-2xl shadow-xl text-white relative overflow-hidden">
                    <div class="absolute top-0 right-0 w-32 h-32 bg-white bg-opacity-10 rounded-full -mr-16 -mt-16"></div>
                    <div class="relative z-10">
                        <div class="flex items-center justify-between">
                            <div>
                                <h3 class="text-lg font-semibold mb-2">🏢 Fornitori Totali</h3>
                                <p class="text-4xl font-bold" id="totalSuppliers">0</p>
                                <p class="text-blue-100 text-sm mt-2">Nella supply chain</p>
                            </div>
                            <div class="p-3 bg-white bg-opacity-20 rounded-xl">
                                <i class="fas fa-building text-2xl"></i>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="card-hover bg-gradient-to-br from-yellow-500 to-orange-500 p-6 rounded-2xl shadow-xl text-white relative overflow-hidden">
                    <div class="absolute top-0 right-0 w-32 h-32 bg-white bg-opacity-10 rounded-full -mr-16 -mt-16"></div>
                    <div class="relative z-10">
                        <div class="flex items-center justify-between">
                            <div>
                                <h3 class="text-lg font-semibold mb-2">⏳ In Attesa</h3>
                                <p class="text-4xl font-bold" id="sentAssessments">0</p>
                                <p class="text-yellow-100 text-sm mt-2">Assessment inviati</p>
                            </div>
                            <div class="p-3 bg-white bg-opacity-20 rounded-xl">
                                <i class="fas fa-clock text-2xl"></i>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="card-hover bg-gradient-to-br from-green-500 to-emerald-600 p-6 rounded-2xl shadow-xl text-white relative overflow-hidden">
                    <div class="absolute top-0 right-0 w-32 h-32 bg-white bg-opacity-10 rounded-full -mr-16 -mt-16"></div>
                    <div class="relative z-10">
                        <div class="flex items-center justify-between">
                            <div>
                                <h3 class="text-lg font-semibold mb-2">✅ Completati</h3>
                                <p class="text-4xl font-bold" id="completedAssessments">0</p>
                                <p class="text-green-100 text-sm mt-2">Assessment finiti</p>
                            </div>
                            <div class="p-3 bg-white bg-opacity-20 rounded-xl">
                                <i class="fas fa-check-circle text-2xl"></i>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="card-hover bg-gradient-to-br from-purple-500 to-violet-600 p-6 rounded-2xl shadow-xl text-white relative overflow-hidden">
                    <div class="absolute top-0 right-0 w-32 h-32 bg-white bg-opacity-10 rounded-full -mr-16 -mt-16"></div>
                    <div class="relative z-10">
                        <div class="flex items-center justify-between">
                            <div>
                                <h3 class="text-lg font-semibold mb-2">🛡️ Conformi NIS2</h3>
                                <p class="text-4xl font-bold" id="conformSuppliers">0</p>
                                <p class="text-purple-100 text-sm mt-2">Certificati</p>
                            </div>
                            <div class="p-3 bg-white bg-opacity-20 rounded-xl">
                                <i class="fas fa-shield-check text-2xl"></i>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Grafici e Analytics -->
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                <!-- Grafico a Torta Conformità -->
                <div class="bg-white rounded-2xl shadow-xl p-6 border border-gray-100">
                    <div class="flex items-center justify-between mb-6">
                        <h3 class="text-xl font-bold text-gray-800">
                            <i class="fas fa-chart-pie text-purple-500 mr-3"></i>
                            Conformità Supply Chain
                        </h3>
                        <div class="flex space-x-2">
                            <span class="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">Conformi</span>
                            <span class="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-medium">Non Conformi</span>
                        </div>
                    </div>
                    <div class="relative h-64">
                        <canvas id="complianceChart"></canvas>
                    </div>
                    <div class="mt-4 text-center">
                        <p class="text-sm text-gray-600">Percentuale di fornitori conformi alle direttive NIS2</p>
                    </div>
                </div>

                <!-- Trend Temporale -->
                <div class="bg-white rounded-2xl shadow-xl p-6 border border-gray-100">
                    <div class="flex items-center justify-between mb-6">
                        <h3 class="text-xl font-bold text-gray-800">
                            <i class="fas fa-chart-line text-blue-500 mr-3"></i>
                            Trend Assessment
                        </h3>
                        <div class="text-sm text-gray-500">Ultimi 30 giorni</div>
                    </div>
                    <div class="relative h-64">
                        <canvas id="trendChart"></canvas>
                    </div>
                    <div class="mt-4 text-center">
                        <p class="text-sm text-gray-600">Evoluzione degli assessment nel tempo</p>
                    </div>
                </div>
            </div>

            <!-- Gadget Intelligenti -->
            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <!-- Risk Score -->
                <div class="bg-gradient-to-br from-red-50 to-red-100 rounded-2xl p-6 border border-red-200">
                    <div class="flex items-center mb-4">
                        <div class="p-3 bg-red-500 rounded-xl mr-4">
                            <i class="fas fa-exclamation-triangle text-white text-xl"></i>
                        </div>
                        <div>
                            <h4 class="text-lg font-bold text-red-800">Risk Score</h4>
                            <p class="text-red-600 text-sm">Livello di rischio</p>
                        </div>
                    </div>
                    <div class="text-center">
                        <div class="text-3xl font-bold text-red-700 mb-2" id="riskScore">0%</div>
                        <div class="w-full bg-red-200 rounded-full h-3">
                            <div class="bg-red-500 h-3 rounded-full transition-all duration-500" id="riskBar" style="width: 0%"></div>
                        </div>
                        <p class="text-sm text-red-600 mt-2" id="riskDescription">Nessun rischio rilevato</p>
                    </div>
                </div>

                <!-- Compliance Score -->
                <div class="bg-gradient-to-br from-green-50 to-green-100 rounded-2xl p-6 border border-green-200">
                    <div class="flex items-center mb-4">
                        <div class="p-3 bg-green-500 rounded-xl mr-4">
                            <i class="fas fa-shield-alt text-white text-xl"></i>
                        </div>
                        <div>
                            <h4 class="text-lg font-bold text-green-800">Compliance Score</h4>
                            <p class="text-green-600 text-sm">Punteggio complessivo</p>
                        </div>
                    </div>
                    <div class="text-center">
                        <div class="text-3xl font-bold text-green-700 mb-2" id="complianceScore">0%</div>
                        <div class="w-full bg-green-200 rounded-full h-3">
                            <div class="bg-green-500 h-3 rounded-full transition-all duration-500" id="complianceBar" style="width: 0%"></div>
                        </div>
                        <p class="text-sm text-green-600 mt-2" id="complianceDescription">Livello di conformità</p>
                    </div>
                </div>

                <!-- Alert Widget -->
                <div class="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-2xl p-6 border border-yellow-200">
                    <div class="flex items-center mb-4">
                        <div class="p-3 bg-yellow-500 rounded-xl mr-4">
                            <i class="fas fa-bell text-white text-xl"></i>
                        </div>
                        <div>
                            <h4 class="text-lg font-bold text-yellow-800">Alert Attivi</h4>
                            <p class="text-yellow-600 text-sm">Notifiche importanti</p>
                        </div>
                    </div>
                    <div class="text-center">
                        <div class="text-3xl font-bold text-yellow-700 mb-2" id="activeAlerts">0</div>
                        <div class="space-y-2">
                            <div class="text-sm text-yellow-700" id="alertDescription">Nessun alert attivo</div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tabella Fornitori Moderna -->
            <div class="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
                <div class="px-6 py-6 border-b border-gray-100 bg-gradient-to-r from-gray-50 to-gray-100">
                    <div class="flex justify-between items-center">
                        <div>
                            <h2 class="text-2xl font-bold text-gray-900">
                                <i class="fas fa-users text-blue-500 mr-3"></i>
                                Gestione Fornitori NIS2
                            </h2>
                            <p class="text-gray-600 mt-1">Monitora e gestisci la conformità della tua supply chain</p>
                        </div>
                        <button onclick="openNewSupplierModal()" class="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-6 py-3 rounded-xl hover:from-blue-600 hover:to-blue-700 transition-all duration-200 shadow-lg font-semibold">
                            <i class="fas fa-plus mr-2"></i>
                            Nuovo Fornitore
                        </button>
                    </div>
                </div>
                <div class="p-6">
                    <div class="overflow-x-auto">
                        <table class="min-w-full divide-y divide-gray-200">
                            <thead class="bg-gradient-to-r from-blue-50 to-indigo-50">
                                <tr>
                                    <th class="px-6 py-4 text-left text-xs font-bold text-blue-900 uppercase tracking-wider">
                                        <i class="fas fa-building mr-2"></i>Fornitore
                                    </th>
                                    <th class="px-6 py-4 text-left text-xs font-bold text-blue-900 uppercase tracking-wider">
                                        <i class="fas fa-envelope mr-2"></i>Email
                                    </th>
                                    <th class="px-6 py-4 text-left text-xs font-bold text-blue-900 uppercase tracking-wider">
                                        <i class="fas fa-industry mr-2"></i>Settore
                                    </th>
                                    <th class="px-6 py-4 text-left text-xs font-bold text-blue-900 uppercase tracking-wider">🌍 Paese</th>
                                    <th class="px-6 py-4 text-left text-xs font-bold text-blue-900 uppercase tracking-wider">⚡ Azioni</th>
                                </tr>
                            </thead>
                            <tbody class="bg-white divide-y divide-gray-200" id="suppliersTable">
                                <tr>
                                    <td class="px-6 py-4 text-sm text-gray-500" colspan="5">
                                        <div class="flex items-center justify-center py-8">
                                            <svg class="animate-spin h-8 w-8 text-blue-500 mr-3" fill="none" viewBox="0 0 24 24">
                                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                            </svg>
                                            Caricamento fornitori...
                                        </div>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </main>

        <!-- Modal Nuovo Fornitore -->
        <div id="newSupplierModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 hidden flex items-center justify-center p-4">
            <div class="bg-white p-8 rounded-lg shadow-lg w-4xl max-w-4xl max-h-[90vh] overflow-y-auto">
                <div class="flex justify-between items-center mb-6">
                    <h3 class="text-xl font-semibold text-gray-900">Nuovo Fornitore</h3>
                    <button onclick="closeNewSupplierModal()" class="text-gray-400 hover:text-gray-600">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </button>
                </div>
                
                <form id="newSupplierForm">
                    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <!-- Informazioni Principali -->
                        <div class="space-y-4">
                            <h4 class="text-lg font-medium text-gray-900 border-b border-gray-200 pb-2">Informazioni Principali</h4>
                            
                            <div>
                                <label class="block text-gray-700 text-sm font-bold mb-2" for="supplierName">
                                    Nome Fornitore *
                                </label>
                                <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" 
                                       id="supplierName" name="company_name" type="text" required>
                            </div>
                            
                            <div>
                                <label class="block text-gray-700 text-sm font-bold mb-2" for="supplierEmail">
                                    Email *
                                </label>
                                <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" 
                                       id="supplierEmail" name="email" type="email" required>
                            </div>
                        </div>

                        <!-- Informazioni Aggiuntive -->
                        <div class="space-y-4">
                            <h4 class="text-lg font-medium text-gray-900 border-b border-gray-200 pb-2">Informazioni Aggiuntive</h4>
                            
                            <div>
                                <label class="block text-gray-700 text-sm font-bold mb-2" for="supplierSector">
                                    Settore
                                </label>
                                <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" 
                                       id="supplierSector" name="sector" type="text" placeholder="es. IT, Manufacturing, etc.">
                            </div>
                            
                            <div>
                                <label class="block text-gray-700 text-sm font-bold mb-2" for="supplierCountry">
                                    Paese
                                </label>
                                <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline" 
                                       id="supplierCountry" name="country" type="text" placeholder="es. Italia, Germania, etc.">
                            </div>
                        </div>
                    </div>
                    
                    <div class="flex items-center justify-between mt-8 pt-6 border-t border-gray-200">
                        <button type="button" onclick="closeNewSupplierModal()" 
                                class="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-6 rounded focus:outline-none focus:shadow-outline">
                            Annulla
                        </button>
                        <button type="submit" 
                                class="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-6 rounded focus:outline-none focus:shadow-outline">
                            Crea Fornitore
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <script>
            const companyId = {company_id};
            
            console.log('Script caricato, companyId:', companyId);
            
            // Carica statistiche dashboard
            function loadDashboardStats() {{
                fetch('/api/company/dashboard', {{
                    credentials: 'include'
                }})
                    .then(response => response.json())
                    .then(data => {{
                        document.getElementById('totalSuppliers').textContent = data.totalSuppliers || 0;
                        document.getElementById('sentAssessments').textContent = data.pendingAssessments || 0;
                        document.getElementById('completedAssessments').textContent = data.completedAssessments || 0;
                        document.getElementById('conformSuppliers').textContent = data.conformSuppliers || 0;
                    }})
                    .catch(error => {{
                        console.error('Errore caricamento statistiche:', error);
                    }});
            }}
            
            // Carica fornitori
            function loadSuppliers() {{
                console.log('=== INIZIO loadSuppliers ===');
                console.log('Caricamento fornitori per company ID:', companyId);
                console.log('URL chiamata:', '/api/company/' + companyId + '/suppliers');
                
                fetch('/api/company/' + companyId + '/suppliers', {{
                    credentials: 'include'
                }})
                    .then(response => {{
                        console.log('Response status:', response.status);
                        return response.json();
                    }})
                    .then(suppliers => {{
                        console.log('Fornitori ricevuti:', suppliers);
                        console.log('Tipo di suppliers:', typeof suppliers);
                        console.log('Lunghezza suppliers:', suppliers.length);
                        
                        const tbody = document.getElementById('suppliersTable');
                        console.log('Elemento tbody trovato:', tbody);
                        
                        if (suppliers.length === 0) {{
                            console.log('Nessun fornitore trovato');
                            tbody.innerHTML = '<tr><td class="px-6 py-4 text-sm text-gray-500" colspan="5">Nessun fornitore registrato</td></tr>';
                        }} else {{
                            console.log('Rendering fornitori...');
                            tbody.innerHTML = suppliers.map(supplier => {{
                                const sector = supplier.sector || 'N/A';
                                const country = supplier.country || 'N/A';
                                const assessmentStatus = supplier.assessment_status || 'pending';
                                const evaluationResult = supplier.evaluation_result || '';
                                const resultsUrl = supplier.results_url || '';
                                
                                console.log('Rendering fornitore:', supplier);
                                
                                let actionButtons = '<button onclick="sendAssessment(' + String(supplier.id) + ')" class="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-3 py-1 rounded-md hover:from-blue-600 hover:to-blue-700 transition-all duration-200 text-sm font-medium shadow-sm mr-2">📤 Invia Assessment</button>';
                                
                                if (supplier.total_assessments > 0) {{
                                    actionButtons += '<button onclick="viewAllAssessments(' + String(supplier.id) + ')" class="bg-gradient-to-r from-purple-500 to-purple-600 text-white px-3 py-1 rounded-md hover:from-purple-600 hover:to-purple-700 transition-all duration-200 text-sm font-medium shadow-sm mr-2">📋 Assessment (' + supplier.total_assessments + ')</button>';
                                }}
                                
                                return '<tr>' +
                                    '<td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">' + supplier.company_name + '</td>' +
                                    '<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">' + supplier.email + '</td>' +
                                    '<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">' + sector + '</td>' +
                                    '<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">' + country + '</td>' +
                                    '<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">' + actionButtons + '</td>' +
                                '</tr>';
                            }}).join('');
                            console.log('Fornitori renderizzati');
                        }}
                        console.log('=== FINE loadSuppliers ===');
                    }})
                    .catch(error => {{
                        console.error('Errore caricamento fornitori:', error);
                        const tbody = document.getElementById('suppliersTable');
                        tbody.innerHTML = '<tr><td class="px-6 py-4 text-sm text-red-500" colspan="5">Errore nel caricamento dei fornitori</td></tr>';
                    }});
            }}

            // Modal functions
            function openNewSupplierModal() {{
                document.getElementById('newSupplierModal').classList.remove('hidden');
            }}

            function closeNewSupplierModal() {{
                document.getElementById('newSupplierModal').classList.add('hidden');
                document.getElementById('newSupplierForm').reset();
            }}

            // Form submission
            document.getElementById('newSupplierForm').addEventListener('submit', function(e) {{
                e.preventDefault();
                
                const formData = new FormData();
                formData.append('company_name', document.getElementById('supplierName').value);
                formData.append('email', document.getElementById('supplierEmail').value);
                formData.append('sector', document.getElementById('supplierSector').value);
                formData.append('country', document.getElementById('supplierCountry').value);
                
                fetch('/api/company/' + companyId + '/suppliers', {{
                    method: 'POST',
                    body: formData,
                    credentials: 'include'
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        alert('Fornitore creato con successo!');
                        closeNewSupplierModal();
                        loadDashboardStats();
                        loadSuppliers();
                    }} else {{
                        alert('Errore nella creazione del fornitore: ' + data.message);
                    }}
                }})
                .catch(error => {{
                    console.error('Errore form submission:', error);
                    alert('Errore nella creazione del fornitore: ' + error);
                }});
            }});

            // Funzione per inviare assessment
            function sendAssessment(supplierId) {{
                if (confirm('Sei sicuro di voler inviare l\\'assessment a questo fornitore?')) {{
                    fetch('/api/company/' + companyId + '/suppliers/' + supplierId + '/send-assessment', {{
                        method: 'POST',
                        credentials: 'include'
                    }})
                    .then(response => response.json())
                    .then(data => {{
                        if (data.success) {{
                            const assessmentLink = data.assessment_url || 'Link non disponibile';
                            
                            // Crea un modal per mostrare il link copiabile
                            const modal = document.createElement('div');
                            modal.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50';
                            modal.innerHTML = '<div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">' +
                                '<div class="mt-3 text-center">' +
                                    '<h3 class="text-lg font-medium text-gray-900 mb-4">Assessment Inviato!</h3>' +
                                    '<p class="text-sm text-gray-500 mb-4">Copia questo link e invialo al fornitore:</p>' +
                                    '<div class="flex items-center border rounded p-2 bg-gray-50">' +
                                        '<input type="text" id="assessmentLink" value="' + assessmentLink + '" ' +
                                               'class="flex-1 bg-transparent border-none outline-none text-sm" readonly>' +
                                        '<button onclick="copyLink()" class="ml-2 bg-blue-500 text-white px-3 py-1 rounded text-sm">' +
                                            'Copia' +
                                        '</button>' +
                                    '</div>' +
                                    '<div class="flex justify-center mt-4">' +
                                        '<button onclick="closeModal()" class="bg-gray-500 text-white px-4 py-2 rounded">' +
                                            'Chiudi' +
                                        '</button>' +
                                    '</div>' +
                                '</div>' +
                            '</div>';
                            document.body.appendChild(modal);
                            
                            // Aggiorna le statistiche
                            loadDashboardStats();
                            loadSuppliers();
                        }} else {{
                            alert('Errore nell\\'invio dell\\'assessment: ' + data.message);
                        }}
                    }})
                    .catch(error => {{
                        console.error('Errore invio assessment:', error);
                        alert('Errore nell\\'invio dell\\'assessment: ' + error);
                    }});
                }}
                
                // Funzione per copiare il link
                window.copyLink = function() {{
                    const linkInput = document.getElementById('assessmentLink');
                    linkInput.select();
                    linkInput.setSelectionRange(0, 99999); // Per dispositivi mobili
                    document.execCommand('copy');
                    alert('Link copiato negli appunti!');
                }};
                
                // Funzione per chiudere il modal
                window.closeModal = function() {{
                    const modal = document.querySelector('.fixed.inset-0');
                    if (modal) {{
                        modal.remove();
                    }}
                }};
            }}

            // Funzione per visualizzare tutti gli assessment
            function viewAllAssessments(supplierId) {{
                window.open('/supplier-assessments/' + companyId + '/' + supplierId, '_blank');
            }}
            
            // Funzione per scaricare il passaporto
            function downloadPassport(supplierId) {{
                const link = document.createElement('a');
                link.href = '/api/company/suppliers/' + supplierId + '/download-passport';
                link.download = 'passaporto_nis2_' + supplierId + '.pdf';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }}
            
            // Funzione per scaricare il report di richiamo
            function downloadRecall(supplierId) {{
                const link = document.createElement('a');
                link.href = '/api/company/suppliers/' + supplierId + '/download-recall';
                link.download = 'richiamo_nis2_' + supplierId + '.pdf';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }}
            
            // Inizializza i grafici
            let complianceChart, trendChart;
            
            // Funzione per creare il grafico a torta della conformità
            function createComplianceChart(conformi, nonConformi) {{
                const ctx = document.getElementById('complianceChart').getContext('2d');
                
                if (complianceChart) {{
                    complianceChart.destroy();
                }}
                
                complianceChart = new Chart(ctx, {{
                    type: 'doughnut',
                    data: {
                        labels: ['Conformi NIS2', 'Non Conformi'],
                        datasets: [{
                            data: [conformi, nonConformi],
                            backgroundColor: [
                                'rgba(34, 197, 94, 0.8)',
                                'rgba(239, 68, 68, 0.8)'
                            ],
                            borderColor: [
                                'rgba(34, 197, 94, 1)',
                                'rgba(239, 68, 68, 1)'
                            ],
                            borderWidth: 2,
                            hoverOffset: 4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: {
                                    padding: 20,
                                    usePointStyle: true,
                                    font: {
                                        size: 12,
                                        weight: 'bold'
                                    }
                                }
                            },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                        const percentage = ((context.parsed / total) * 100).toFixed(1);
                                        return `${context.label}: ${context.parsed} (${percentage}%)`;
                                    }
                                }
                            }
                        },
                        animation: {
                            animateRotate: true,
                            duration: 2000
                        }
                    }
                });
            }
            
            // Funzione per creare il grafico del trend temporale
            function createTrendChart() {
                const ctx = document.getElementById('trendChart').getContext('2d');
                
                if (trendChart) {
                    trendChart.destroy();
                }
                
                // Genera dati di esempio per gli ultimi 30 giorni
                const labels = [];
                const data = [];
                const today = new Date();
                
                for (let i = 29; i >= 0; i--) {
                    const date = new Date(today);
                    date.setDate(date.getDate() - i);
                    labels.push(date.toLocaleDateString('it-IT', { day: '2-digit', month: '2-digit' }));
                    
                    // Simula dati realistici con trend crescente
                    const baseValue = Math.random() * 3 + 1;
                    const trend = Math.sin(i * 0.2) * 0.5 + 1;
                    data.push(Math.round(baseValue * trend));
                }
                
                trendChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'Assessment Completati',
                            data: data,
                            borderColor: 'rgba(59, 130, 246, 1)',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            borderWidth: 3,
                            fill: true,
                            tension: 0.4,
                            pointBackgroundColor: 'rgba(59, 130, 246, 1)',
                            pointBorderColor: '#fff',
                            pointBorderWidth: 2,
                            pointRadius: 4,
                            pointHoverRadius: 6
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: false
                            },
                            tooltip: {
                                mode: 'index',
                                intersect: false,
                                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                                titleColor: '#fff',
                                bodyColor: '#fff',
                                borderColor: 'rgba(59, 130, 246, 1)',
                                borderWidth: 1
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                grid: {
                                    color: 'rgba(0, 0, 0, 0.1)'
                                },
                                ticks: {
                                    stepSize: 1
                                }
                            },
                            x: {
                                grid: {
                                    display: false
                                }
                            }
                        },
                        interaction: {
                            mode: 'nearest',
                            axis: 'x',
                            intersect: false
                        }
                    }
                });
            }
            
            // Funzione per aggiornare i gadget intelligenti
            function updateSmartGadgets(stats) {
                const total = stats.totalSuppliers || 0;
                const conformi = stats.conformSuppliers || 0;
                const nonConformi = total - conformi;
                
                // Calcola Risk Score (percentuale di non conformi)
                const riskScore = total > 0 ? Math.round((nonConformi / total) * 100) : 0;
                document.getElementById('riskScore').textContent = riskScore + '%';
                document.getElementById('riskBar').style.width = riskScore + '%';
                
                if (riskScore === 0) {
                    document.getElementById('riskDescription').textContent = 'Nessun rischio rilevato';
                } else if (riskScore <= 20) {
                    document.getElementById('riskDescription').textContent = 'Rischio basso';
                } else if (riskScore <= 50) {
                    document.getElementById('riskDescription').textContent = 'Rischio moderato';
                } else {
                    document.getElementById('riskDescription').textContent = 'Rischio elevato';
                }
                
                // Calcola Compliance Score (percentuale di conformi)
                const complianceScore = total > 0 ? Math.round((conformi / total) * 100) : 0;
                document.getElementById('complianceScore').textContent = complianceScore + '%';
                document.getElementById('complianceBar').style.width = complianceScore + '%';
                
                if (complianceScore >= 90) {
                    document.getElementById('complianceDescription').textContent = 'Eccellente';
                } else if (complianceScore >= 70) {
                    document.getElementById('complianceDescription').textContent = 'Buono';
                } else if (complianceScore >= 50) {
                    document.getElementById('complianceDescription').textContent = 'Sufficiente';
                } else {
                    document.getElementById('complianceDescription').textContent = 'Da migliorare';
                }
                
                // Calcola Alert Attivi
                const pendingAssessments = stats.sentAssessments || 0;
                const alerts = [];
                
                if (pendingAssessments > 0) {
                    alerts.push(`${pendingAssessments} assessment in attesa`);
                }
                if (riskScore > 50) {
                    alerts.push('Rischio supply chain elevato');
                }
                if (complianceScore < 70) {
                    alerts.push('Compliance score basso');
                }
                
                document.getElementById('activeAlerts').textContent = alerts.length;
                
                if (alerts.length === 0) {
                    document.getElementById('alertDescription').textContent = 'Nessun alert attivo';
                } else {
                    document.getElementById('alertDescription').textContent = alerts.join(', ');
                }
                
                // Crea i grafici
                createComplianceChart(conformi, nonConformi);
                createTrendChart();
            }
            
            // Modifica la funzione loadDashboardStats per includere i gadget
            async function loadDashboardStats() {
                try {
                    const response = await fetch('/api/company/dashboard', {
                        headers: {
                            'Authorization': `Bearer ${localStorage.getItem('token')}`
                        }
                    });
                    
                    if (response.ok) {
                        const stats = await response.json();
                        
                        // Aggiorna i KPI
                        document.getElementById('totalSuppliers').textContent = stats.totalSuppliers || 0;
                        document.getElementById('sentAssessments').textContent = stats.sentAssessments || 0;
                        document.getElementById('completedAssessments').textContent = stats.completedAssessments || 0;
                        document.getElementById('conformSuppliers').textContent = stats.conformSuppliers || 0;
                        
                        // Aggiorna i gadget intelligenti
                        updateSmartGadgets(stats);
                        
                        // Aggiungi animazioni ai numeri
                        animateNumbers();
                    }
                } catch (error) {
                    console.error('Errore nel caricamento delle statistiche:', error);
                }
            }
            
            // Funzione per animare i numeri
            function animateNumbers() {
                const elements = ['totalSuppliers', 'sentAssessments', 'completedAssessments', 'conformSuppliers'];
                
                elements.forEach(id => {
                    const element = document.getElementById(id);
                    const finalValue = parseInt(element.textContent);
                    const duration = 2000;
                    const startTime = performance.now();
                    
                    function updateNumber(currentTime) {
                        const elapsed = currentTime - startTime;
                        const progress = Math.min(elapsed / duration, 1);
                        
                        const currentValue = Math.floor(progress * finalValue);
                        element.textContent = currentValue;
                        
                        if (progress < 1) {
                            requestAnimationFrame(updateNumber);
                        }
                    }
                    
                    requestAnimationFrame(updateNumber);
                });
            }
            
            // Carica dati all'avvio
            loadDashboardStats();
            loadSuppliers();
        </script>
    </body>
    </html>
    """
    return html_content

@app.post("/api/assessment/submit")
async def submit_assessment(request: Request):
    try:
        form_data = await request.form()
        token = form_data.get('token')
        
        if not token:
            return {"success": False, "message": "Token mancante"}
        
        # Trova l'assessment nel database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, supplier_id, company_id FROM assessments 
            WHERE assessment_token = ? AND status != 'completed'
        """, (token,))
        
        assessment = cursor.fetchone()
        if not assessment:
            return {"success": False, "message": "Assessment non trovato o già completato"}
        
        assessment_id, supplier_id, company_id = assessment
        
        # Raccogli le risposte per la valutazione
        answers = {}
        for key, value in form_data.items():
            if key.startswith('q_') and value in ['si', 'no', 'na']:
                # Estrai codice_argomento e numero_domanda dal nome del campo
                parts = key[2:].split('_')  # rimuovi 'q_' e splitta
                if len(parts) >= 2:
                    codice_argomento = parts[0]
                    numero_domanda = parts[1]
                    question_id = f"{codice_argomento}_{numero_domanda}"
                    answers[question_id] = value
                    
                    # Salva la risposta nel database
                    cursor.execute("""
                        INSERT OR REPLACE INTO assessment_answers 
                        (assessment_id, codice_argomento, numero_domanda, risposta, created_at)
                        VALUES (?, ?, ?, ?, datetime('now'))
                    """, (assessment_id, codice_argomento, numero_domanda, value))
        
        # Valuta l'assessment
        from assessment_evaluator import NIS2AssessmentEvaluator
        evaluator = NIS2AssessmentEvaluator()
        
        # Per ora assumiamo che non ha ISO 27001 (in futuro aggiungeremo questa domanda)
        evaluation_result = evaluator.evaluate_assessment(answers, has_iso27001=False)
        
        # Salva il risultato della valutazione
        cursor.execute("""
            UPDATE assessments SET 
                status = 'completed', 
                completed_at = datetime('now'),
                evaluation_result = ?
            WHERE id = ?
        """, (json.dumps(evaluation_result), assessment_id))
        
        conn.commit()
        conn.close()
        
        print(f"Assessment {assessment_id} completato e valutato: {evaluation_result['outcome']}")
        return {
            "success": True, 
            "message": "Assessment completato con successo",
            "evaluation": evaluation_result
        }
        
    except Exception as e:
        print(f"Errore nel salvataggio assessment: {e}")
        return {"success": False, "message": str(e)}

@app.get("/assessment/{token}", response_class=HTMLResponse)
async def assessment_page(token: str):
    """Pagina per compilare l'assessment"""
    print(f"=== DEBUG ASSESSMENT PAGE ===")
    print(f"Token ricevuto: {token}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Debug: verifica se la tabella assessments esiste
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assessments'")
        table_exists = cursor.fetchone()
        print(f"Tabella assessments esiste: {table_exists is not None}")
        
        # Debug: conta tutti gli assessment
        cursor.execute("SELECT COUNT(*) FROM assessments")
        total_count = cursor.fetchone()[0]
        print(f"Totale assessment nel database: {total_count}")
        
        # Debug: verifica se l'assessment esiste
        cursor.execute("SELECT COUNT(*) FROM assessments WHERE assessment_token = ?", (token,))
        count = cursor.fetchone()[0]
        print(f"Numero di assessment trovati con token {token}: {count}")
        
        # Debug: mostra tutti gli assessment
        cursor.execute("SELECT id, assessment_token, status FROM assessments")
        all_assessments = cursor.fetchall()
        print(f"Tutti gli assessment:")
        for assessment in all_assessments:
            print(f"  ID: {assessment[0]}, Token: {assessment[1]}, Status: {assessment[2]}")
        
        # Verifica che l'assessment esista e sia valido
        cursor.execute("""
            SELECT a.id, a.status, s.company_name, s.email, c.name as company_name
            FROM assessments a
            JOIN suppliers s ON a.supplier_id = s.id
            JOIN companies c ON a.company_id = c.id
            WHERE a.assessment_token = ?
        """, (token,))
        
        assessment = cursor.fetchone()
        print(f"Assessment trovato: {assessment}")
        
        if not assessment:
            print("Assessment non trovato!")
            return HTMLResponse(content="<h1>Assessment non trovato o non valido</h1>", status_code=404)
        
        if assessment[1] == "completed":
            return HTMLResponse(content="<h1>Assessment già completato</h1>", status_code=400)
        
        supplier_name = assessment[2]
        supplier_email = assessment[3]
        company_name = assessment[4]
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="it">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Assessment NIS2 - {supplier_name}</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-100">
            <div class="max-w-4xl mx-auto py-8 px-4">
                <div class="bg-white rounded-lg shadow-lg p-8">
                    <div class="text-center mb-8">
                        <h1 class="text-3xl font-bold text-gray-900 mb-2">🛡️ Assessment NIS2</h1>
                        <p class="text-gray-600">Questionario di valutazione sicurezza informatica</p>
                        <div class="mt-4 p-4 bg-blue-50 rounded-lg">
                            <p class="text-sm text-blue-800">
                                <strong>Fornitore:</strong> {supplier_name}<br>
                                <strong>Email:</strong> {supplier_email}<br>
                                <strong>Richiesto da:</strong> {company_name}
                            </p>
                        </div>
                    </div>
                    
                    <form id="assessmentForm" class="space-y-6">
                        <input type="hidden" id="assessmentToken" value="{token}">
                        
                        <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
                            <div class="flex">
                                <div class="flex-shrink-0">
                                    <svg class="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                                        <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                                    </svg>
                                </div>
                                <div class="ml-3">
                                    <p class="text-sm text-yellow-700">
                                        <strong>Importante:</strong> Questo assessment contiene 57 domande organizzate in 13 sezioni. 
                                        Assicurati di avere tempo sufficiente per completarlo accuratamente.
                                    </p>
                                </div>
                            </div>
                        </div>
                        
                        <div id="questionsContainer" class="space-y-8">
                            <!-- Le domande verranno caricate dinamicamente -->
                        </div>
                        
                        <div class="flex justify-between items-center pt-6 border-t border-gray-200">
                            <button type="button" onclick="saveProgress()" 
                                    class="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-6 rounded">
                                Salva Progresso
                            </button>
                            <button type="submit" 
                                    class="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-6 rounded">
                                Invia Assessment
                            </button>
                        </div>
                    </form>
                </div>
            </div>
            
            <script src="/static/assessment.js"></script>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        return HTMLResponse(content=f"<h1>Errore: {str(e)}</h1>", status_code=500)
    finally:
        conn.close()

@app.get("/assessment-completed/{token}", response_class=HTMLResponse)
async def assessment_completed_page(token: str):
    """Pagina di completamento assessment"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Recupera i dati dell'assessment completato
        cursor.execute("""
            SELECT a.id, s.company_name, s.email, c.name as company_name, a.completed_at
            FROM assessments a
            JOIN suppliers s ON a.supplier_id = s.id
            JOIN companies c ON a.company_id = c.id
            WHERE a.assessment_token = ? AND a.status = 'completed'
        """, (token,))
        
        assessment = cursor.fetchone()
        
        if not assessment:
            return HTMLResponse(content="<h1>Assessment non trovato o non completato</h1>", status_code=404)
        
        assessment_id, supplier_name, supplier_email, company_name, completed_at = assessment
        
        # Conta le risposte
        cursor.execute("""
            SELECT COUNT(*) FROM assessment_answers WHERE assessment_id = ?
        """, (assessment_id,))
        
        total_answers = cursor.fetchone()[0]
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="it">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Assessment Completato - NIS2</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-100">
            <div class="max-w-4xl mx-auto py-8 px-4">
                <div class="bg-white rounded-lg shadow-lg p-8">
                    <div class="text-center mb-8">
                        <div class="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-4">
                            <svg class="h-8 w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                            </svg>
                        </div>
                        <h1 class="text-3xl font-bold text-gray-900 mb-2">✅ Assessment Completato!</h1>
                        <p class="text-gray-600">Il questionario NIS2 è stato inviato con successo</p>
                    </div>
                    
                    <div class="bg-green-50 border border-green-200 rounded-lg p-6 mb-8">
                        <h2 class="text-lg font-semibold text-green-800 mb-4">Dettagli Assessment</h2>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                            <div>
                                <strong>Fornitore:</strong> {supplier_name}<br>
                                <strong>Email:</strong> {supplier_email}
                            </div>
                            <div>
                                <strong>Richiesto da:</strong> {company_name}<br>
                                <strong>Completato il:</strong> {completed_at}<br>
                                <strong>Risposte fornite:</strong> {total_answers}
                            </div>
                        </div>
                    </div>
                    
                    <div class="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
                        <h2 class="text-lg font-semibold text-blue-800 mb-4">Prossimi Passi</h2>
                        <ul class="text-sm text-blue-700 space-y-2">
                            <li>• L'azienda riceverà una notifica del completamento</li>
                            <li>• I risultati verranno analizzati e processati</li>
                            <li>• Verrà generato un report dettagliato</li>
                            <li>• L'azienda potrà visualizzare i risultati nella dashboard</li>
                        </ul>
                    </div>
                    
                    <div class="text-center">
                        <p class="text-gray-600 text-sm mb-4">
                            Grazie per aver completato l'assessment NIS2!
                        </p>
                        <button onclick="closePage()" class="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-6 rounded">
                            Chiudi Pagina
                        </button>
                    </div>
                    
                    <script>
                    function closePage() {{
                        // Prova prima a chiudere la finestra
                        if (window.opener) {{
                            window.close();
                        }} else {{
                            // Se non funziona, mostra un messaggio all'utente
                            alert('Per chiudere questa pagina, puoi:\\n\\n1. Chiudere manualmente la scheda del browser\\n2. Usare Ctrl+W (Windows) o Cmd+W (Mac)\\n3. Tornare alla pagina precedente');
                            
                            // Alternativa: prova a tornare alla pagina precedente
                            if (window.history.length > 1) {{
                                window.history.back();
                            }} else {{
                                // Se non c'è storia, reindirizza a una pagina di default
                                window.location.href = '/';
                            }}
                        }}
                    }}
                    </script>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        return HTMLResponse(content=f"<h1>Errore: {str(e)}</h1>", status_code=500)
    finally:
        conn.close()

@app.get("/demo", response_class=HTMLResponse)
async def demo_page():
    """Pagina demo per visualizzare le funzionalità"""
    html_content = """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Demo Piattaforma NIS2</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: #2563eb; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .card { background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
            .endpoint { background: #f8fafc; padding: 10px; border-left: 4px solid #2563eb; margin: 10px 0; }
            .method { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
            .get { background: #22c55e; color: white; }
            .post { background: #f59e0b; color: white; }
            .feature { padding: 15px; background: #f0fdf4; border-radius: 6px; margin: 10px 0; }
            .status { color: #16a34a; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛡️ Piattaforma NIS2 Supplier Assessment</h1>
                <p>Demo Backend FastAPI + SQLite - Modalità Sviluppo</p>
            </div>
            
            <div class="grid">
                <div class="card">
                    <h2>📊 Stato Piattaforma</h2>
                    <div class="feature">
                        <strong>Backend:</strong> <span class="status">✅ ATTIVO</span><br>
                        <strong>Database:</strong> <span class="status">✅ SQLite</span><br>
                        <strong>Questionario:</strong> <span class="status">✅ 57 domande</span><br>
                        <strong>API Docs:</strong> <a href="/docs" target="_blank">Swagger UI</a>
                    </div>
                </div>
                
                <div class="card">
                    <h2>🔐 Credenziali Demo</h2>
                    <div class="feature">
                        <strong>Username:</strong> admin<br>
                        <strong>Password:</strong> secret123<br>
                        <strong>Ruolo:</strong> Administrator<br>
                        <em>Usa queste credenziali per testare l'API</em>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>🚀 Endpoints Disponibili</h2>
                <div class="endpoint">
                    <span class="method get">GET</span> <strong>/docs</strong> - Documentazione API interattiva
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span> <strong>/questionario</strong> - Visualizza questionario NIS2 completo
                </div>
                <div class="endpoint">
                    <span class="method post">POST</span> <strong>/api/auth/login</strong> - Login utenti
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span> <strong>/api/admin/stats</strong> - Statistiche piattaforma
                </div>
                <div class="endpoint">
                    <span class="method get">GET</span> <strong>/api/admin/companies</strong> - Lista aziende
                </div>
            </div>
            
            <div class="card">
                <h2>🎯 Questionario NIS2</h2>
                <div class="feature">
                    <p><strong>57 domande</strong> organizzate in <strong>13 sezioni</strong>:</p>
                    <ul>
                        <li><strong>GSI.03-10:</strong> Governance e Sicurezza Informatica</li>
                        <li><strong>SIT.01-03:</strong> Sicurezza IT</li>
                        <li><strong>SFA.01-02:</strong> Sicurezza Funzionale e Applicativa</li>
                    </ul>
                    <a href="/questionario" target="_blank">→ Visualizza questionario completo</a>
                </div>
            </div>
            
            <div class="card">
                <h2>📱 Prossimi Passi</h2>
                <div class="feature">
                    <p><strong>Per vedere la piattaforma completa:</strong></p>
                    <ol>
                        <li>Installa <a href="https://www.docker.com/products/docker-desktop/" target="_blank">Docker Desktop</a></li>
                        <li>Esegui: <code>docker compose up -d</code></li>
                        <li>Accedi a: <code>http://localhost</code></li>
                    </ol>
                    <p><em>Oppure continua a esplorare l'API qui: <a href="/docs">/docs</a></em></p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

@app.get("/assessment-results/{company_id}/{supplier_id}", response_class=HTMLResponse)
async def view_assessment_results(company_id: int, supplier_id: int, request: Request):
    """Pagina HTML per visualizzare i risultati dettagliati dell'assessment"""
    # Verifica autenticazione
    user = await get_current_user(request)
    if not user or user.get('role') != 'company':
        raise HTTPException(status_code=401, detail="Non autorizzato")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Ottieni i dettagli dell'ultimo assessment completato
        cursor.execute("""
            SELECT 
                a.id,
                a.assessment_token,
                a.status,
                a.evaluation_result,
                a.completed_at,
                s.company_name,
                s.email,
                s.sector,
                s.country
            FROM assessments a
            JOIN suppliers s ON a.supplier_id = s.id
            WHERE s.company_id = ? AND a.supplier_id = ? AND a.status = 'completed'
            ORDER BY a.completed_at DESC
            LIMIT 1
        """, (company_id, supplier_id))
        
        assessment = cursor.fetchone()
        
        if not assessment:
            return HTMLResponse(content="""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Assessment Non Trovato</title>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <script src="https://cdn.tailwindcss.com"></script>
                </head>
                <body class="bg-gray-100 min-h-screen">
                    <div class="container mx-auto px-4 py-8">
                        <div class="bg-white rounded-lg shadow-md p-6">
                            <h1 class="text-2xl font-bold text-red-600 mb-4">Assessment Non Trovato</h1>
                            <p class="text-gray-600 mb-4">Non è stato trovato alcun assessment completato per questo fornitore.</p>
                            <a href="/company/dashboard" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                                Torna alla Dashboard
                            </a>
                        </div>
                    </div>
                </body>
                </html>
            """)
        
        # Parsa il risultato della valutazione
        evaluation_result = None
        if assessment[3]:  # evaluation_result
            try:
                import json
                evaluation_result = json.loads(assessment[3])
            except:
                evaluation_result = {"error": "Errore nel parsing del risultato"}
        
        # Genera la pagina HTML con i risultati
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Risultati Assessment - {assessment[5]}</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-100 min-h-screen">
            <div class="container mx-auto px-4 py-8">
                <div class="bg-white rounded-lg shadow-md p-6">
                    <div class="flex justify-between items-center mb-6">
                        <h1 class="text-3xl font-bold text-gray-800">Risultati Assessment NIS2</h1>
                        <a href="/company/dashboard" class="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded">
                            ← Torna alla Dashboard
                        </a>
                    </div>
                    
                    <!-- Informazioni Fornitore -->
                    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                        <h2 class="text-xl font-semibold text-blue-800 mb-3">Informazioni Fornitore</h2>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <p class="text-sm text-gray-600">Nome Azienda</p>
                                <p class="font-medium">{assessment[5]}</p>
                            </div>
                            <div>
                                <p class="text-sm text-gray-600">Email</p>
                                <p class="font-medium">{assessment[6]}</p>
                            </div>
                            <div>
                                <p class="text-sm text-gray-600">Settore</p>
                                <p class="font-medium">{assessment[7]}</p>
                            </div>
                            <div>
                                <p class="text-sm text-gray-600">Paese</p>
                                <p class="font-medium">{assessment[8]}</p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Risultato Principale -->
                    <div class="mb-6">
                        {f'''
                        <div class="bg-{'green' if evaluation_result.get('outcome') == 'POSITIVO' else 'red'}-50 border border-{'green' if evaluation_result.get('outcome') == 'POSITIVO' else 'red'}-200 rounded-lg p-4">
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <svg class="h-8 w-8 text-{'green' if evaluation_result.get('outcome') == 'POSITIVO' else 'red'}-400" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="{'M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z' if evaluation_result.get('outcome') == 'POSITIVO' else 'M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z'}" clip-rule="evenodd"></path>
                                    </svg>
                                </div>
                                <div class="ml-3">
                                    <h3 class="text-lg font-medium text-{'green' if evaluation_result.get('outcome') == 'POSITIVO' else 'red'}-800">
                                        Risultato: {evaluation_result.get('outcome', 'N/A')}
                                    </h3>
                                    <p class="text-sm text-{'green' if evaluation_result.get('outcome') == 'POSITIVO' else 'red'}-700">
                                        {evaluation_result.get('reason', 'Nessuna motivazione disponibile')}
                                    </p>
                                </div>
                            </div>
                        </div>
                        ''' if evaluation_result and 'outcome' in evaluation_result else '''
                        <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                            <div class="flex items-center">
                                <div class="flex-shrink-0">
                                    <svg class="h-8 w-8 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                                        <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"></path>
                                    </svg>
                                </div>
                                <div class="ml-3">
                                    <h3 class="text-lg font-medium text-yellow-800">Risultato Non Disponibile</h3>
                                    <p class="text-sm text-yellow-700">I risultati dell'assessment non sono ancora stati elaborati.</p>
                                </div>
                            </div>
                        </div>
                        '''}
                    </div>
                    
                    <!-- Punteggio -->
                    {f'''
                    <div class="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-6">
                        <h2 class="text-xl font-semibold text-gray-800 mb-3">Punteggio Finale</h2>
                        <div class="flex items-center">
                            <div class="flex-1">
                                <div class="bg-gray-200 rounded-full h-4">
                                    <div class="bg-blue-600 h-4 rounded-full" style="width: {evaluation_result.get('final_score', 0)}%"></div>
                                </div>
                            </div>
                            <div class="ml-4">
                                <span class="text-2xl font-bold text-blue-600">{evaluation_result.get('final_score', 0)}%</span>
                            </div>
                        </div>
                    </div>
                    ''' if evaluation_result and 'final_score' in evaluation_result else ''}
                    
                    <!-- Aree di Miglioramento -->
                    {f'''
                    <div class="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-6">
                        <h2 class="text-xl font-semibold text-orange-800 mb-3">Aree di Miglioramento</h2>
                        <ul class="list-disc list-inside space-y-2">
                            {''.join([f'<li class="text-orange-700">{area}</li>' for area in evaluation_result.get('improvement_areas', [])])}
                        </ul>
                    </div>
                    ''' if evaluation_result and 'improvement_areas' in evaluation_result and evaluation_result['improvement_areas'] else ''}
                    
                    <!-- Punti di Forza -->
                    {f'''
                    <div class="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
                        <h2 class="text-xl font-semibold text-green-800 mb-3">Punti di Forza</h2>
                        <ul class="list-disc list-inside space-y-2">
                            {''.join([f'<li class="text-green-700">{strength}</li>' for strength in evaluation_result.get('strengths', [])])}
                        </ul>
                    </div>
                    ''' if evaluation_result and 'strengths' in evaluation_result and evaluation_result['strengths'] else ''}
                    
                    <!-- Dettagli Assessment -->
                    <div class="bg-gray-50 border border-gray-200 rounded-lg p-4">
                        <h2 class="text-xl font-semibold text-gray-800 mb-3">Dettagli Assessment</h2>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <p class="text-sm text-gray-600">ID Assessment</p>
                                <p class="font-medium">{assessment[0]}</p>
                            </div>
                            <div>
                                <p class="text-sm text-gray-600">Token</p>
                                <p class="font-medium font-mono text-sm">{assessment[1]}</p>
                            </div>
                            <div>
                                <p class="text-sm text-gray-600">Status</p>
                                <p class="font-medium">{assessment[2]}</p>
                            </div>
                            <div>
                                <p class="text-sm text-gray-600">Completato il</p>
                                <p class="font-medium">{assessment[4]}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        return HTMLResponse(content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Errore</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <script src="https://cdn.tailwindcss.com"></script>
            </head>
            <body class="bg-gray-100 min-h-screen">
                <div class="container mx-auto px-4 py-8">
                    <div class="bg-white rounded-lg shadow-md p-6">
                        <h1 class="text-2xl font-bold text-red-600 mb-4">Errore</h1>
                        <p class="text-gray-600 mb-4">Si è verificato un errore nel caricamento dei risultati: {str(e)}</p>
                        <a href="/company/dashboard" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
                            Torna alla Dashboard
                        </a>
                    </div>
                </div>
            </body>
            </html>
        """)
    finally:
        conn.close()

@app.get("/api/company/suppliers/{supplier_id}/download-passport")
async def download_passport(supplier_id: int, request: Request):
    """Scarica il passaporto digitale per un fornitore conforme"""
    # Verifica autenticazione
    user = await get_current_user(request)
    if not user or user.get('role') != 'company':
        raise HTTPException(status_code=401, detail="Non autorizzato")
    
    try:
        # Importa il generatore PDF professionale
        from professional_pdf_generator import generate_assessment_pdf
        
        # Trova l'ultimo assessment completato del fornitore
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id FROM assessments 
            WHERE supplier_id = ? AND status = 'completed'
            ORDER BY completed_at DESC
            LIMIT 1
        """, (supplier_id,))
        
        assessment = cursor.fetchone()
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment non trovato")
        
        assessment_id = assessment[0]
        
        # Genera il PDF
        pdf_path = generate_assessment_pdf(assessment_id, "temp_pdfs")
        
        if not pdf_path or not os.path.exists(pdf_path):
            raise HTTPException(status_code=500, detail="Errore nella generazione del PDF")
        
        # Restituisci il file
        return FileResponse(
            path=pdf_path,
            filename=f"passaporto_nis2_professionale_{supplier_id}.pdf",
            media_type="application/pdf"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel download: {str(e)}")
    finally:
        conn.close()

@app.get("/v/{qr_hash}")
async def verify_qr_code(qr_hash: str, request: Request):
    """Endpoint per verificare l'autenticità di un documento tramite QR code"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Decodifica il QR hash (formato: NIS2_PASSPORT|id|company|date|score)
        # Rimuovi eventuali URL base dal QR code
        clean_hash = qr_hash
        if clean_hash.startswith('http://localhost:8000/v/'):
            clean_hash = clean_hash.replace('http://localhost:8000/v/', '')
        elif clean_hash.startswith('https://localhost:8000/v/'):
            clean_hash = clean_hash.replace('https://localhost:8000/v/', '')
        
        parts = clean_hash.split('|')
        if len(parts) != 5:
            raise HTTPException(status_code=400, detail="QR code non valido")
        
        doc_type, assessment_id, company_name, completed_date, score = parts
        
        # Verifica che l'assessment esista
        cursor.execute("""
            SELECT a.id, a.status, a.evaluation_result, a.completed_at,
                   s.company_name, s.email, s.sector, s.country,
                   c.name as client_company
            FROM assessments a
            JOIN suppliers s ON a.supplier_id = s.id
            JOIN companies c ON s.company_id = c.id
            WHERE a.id = ?
        """, (assessment_id,))
        
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="Assessment non trovato")
        
        assessment_data = {
            'id': result[0],
            'status': result[1],
            'evaluation_result': result[2],
            'completed_at': result[3]
        }
        
        supplier_data = {
            'company_name': result[4],
            'email': result[5],
            'sector': result[6],
            'country': result[7]
        }
        
        company_data = {
            'name': result[8]
        }
        
        # Parsa il risultato della valutazione
        evaluation_result = json.loads(assessment_data['evaluation_result'])
        actual_score = evaluation_result.get('final_percentage', 0) * 100
        outcome = evaluation_result.get('outcome', 'NEGATIVO')
        
        # Verifica che i dati corrispondano
        if abs(float(score) - actual_score) > 0.1:
            raise HTTPException(status_code=400, detail="Dati QR code non corrispondenti")
        
        # Determina il tipo di documento
        is_passport = doc_type == "NIS2_PASSPORT" and outcome == "POSITIVO"
        is_recall = doc_type == "NIS2_RECALL" and outcome == "NEGATIVO"
        
        if not (is_passport or is_recall):
            raise HTTPException(status_code=400, detail="Tipo documento non valido")
        
        # Genera la pagina di verifica come certificato formale
        current_year = datetime.now().year
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="it">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Certificato NIS2 - {supplier_data['company_name']}</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&display=swap');
                .certificate-font {{ font-family: 'Playfair Display', serif; }}
                .gradient-bg {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
                .gold-border {{ border: 3px solid #D4AF37; }}
                .seal {{ 
                    background: radial-gradient(circle, #D4AF37 0%, #B8860B 50%, #8B6914 100%);
                    box-shadow: 0 0 20px rgba(212, 175, 55, 0.5);
                }}
                .watermark {{ 
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%) rotate(-45deg);
                    font-size: 120px;
                    opacity: 0.03;
                    color: #000;
                    z-index: 0;
                    pointer-events: none;
                }}
                .certificate-content {{ position: relative; z-index: 1; }}
                @media print {{
                    .no-print {{ display: none; }}
                    body {{ background: white; }}
                }}
            </style>
        </head>
        <body class="bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 min-h-screen">
            <div class="container mx-auto px-4 py-8">
                <div class="max-w-5xl mx-auto">
                    <!-- Certificato Principale -->
                    <div class="bg-white gold-border rounded-3xl shadow-2xl p-12 relative overflow-hidden">
                        <!-- Watermark -->
                        <div class="watermark">NIS2</div>
                        
                        <div class="certificate-content">
                            <!-- Header del Certificato -->
                            <div class="text-center mb-12">
                                <div class="inline-flex items-center justify-center w-24 h-24 seal rounded-full mb-6">
                                    <i class="fas fa-shield-alt text-white text-4xl"></i>
                                </div>
                                <h1 class="certificate-font text-5xl font-black text-gray-800 mb-4">
                                    CERTIFICATO NIS2
                                </h1>
                                <div class="w-32 h-1 bg-gradient-to-r from-blue-500 to-purple-600 mx-auto mb-4"></div>
                                <p class="text-xl text-gray-600 certificate-font">
                                    Conformità Supply Chain
                                </p>
                            </div>
                            
                            <!-- Testo Principale del Certificato -->
                            <div class="text-center mb-12">
                                <div class="bg-gradient-to-r from-blue-50 to-indigo-50 p-8 rounded-2xl border-2 border-blue-200">
                                    <p class="certificate-font text-2xl leading-relaxed text-gray-800 mb-6">
                                        <strong>Si certifica che</strong><br>
                                        <span class="text-3xl font-bold text-blue-700">{supplier_data['company_name']}</span><br>
                                        <strong>è risultato essere in linea con le direttive NIS2</strong><br>
                                        <strong>riguardanti la supply chain per l'anno {current_year}</strong><br>
                                        <strong>rientrando quindi nella categoria dei fornitori qualificati per</strong><br>
                                        <span class="text-2xl font-bold text-purple-700">{company_data['name']}</span>
                                    </p>
                                </div>
                            </div>
                            
                            <!-- Dettagli del Certificato -->
                            <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
                                <div class="text-center">
                                    <div class="bg-green-100 p-4 rounded-xl">
                                        <i class="fas fa-check-circle text-4xl text-green-600 mb-3"></i>
                                        <h3 class="font-bold text-green-800 text-lg">Risultato</h3>
                                        <p class="text-green-700 font-semibold">{outcome}</p>
                                    </div>
                                </div>
                                <div class="text-center">
                                    <div class="bg-blue-100 p-4 rounded-xl">
                                        <i class="fas fa-chart-line text-4xl text-blue-600 mb-3"></i>
                                        <h3 class="font-bold text-blue-800 text-lg">Punteggio</h3>
                                        <p class="text-blue-700 font-semibold">{actual_score:.1f}%</p>
                                    </div>
                                </div>
                                <div class="text-center">
                                    <div class="bg-purple-100 p-4 rounded-xl">
                                        <i class="fas fa-calendar-check text-4xl text-purple-600 mb-3"></i>
                                        <h3 class="font-bold text-purple-800 text-lg">Data Valutazione</h3>
                                        <p class="text-purple-700 font-semibold">{assessment_data['completed_at'][:10]}</p>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Informazioni Aggiuntive -->
                            <div class="bg-gray-50 p-6 rounded-xl mb-8">
                                <h3 class="font-bold text-gray-800 text-lg mb-4">📋 Informazioni Fornitore</h3>
                                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <p class="text-sm text-gray-600">Email</p>
                                        <p class="font-semibold">{supplier_data['email']}</p>
                                    </div>
                                    <div>
                                        <p class="text-sm text-gray-600">Settore</p>
                                        <p class="font-semibold">{supplier_data['sector']}</p>
                                    </div>
                                    <div>
                                        <p class="text-sm text-gray-600">Paese</p>
                                        <p class="font-semibold">{supplier_data['country']}</p>
                                    </div>
                                    <div>
                                        <p class="text-sm text-gray-600">ID Assessment</p>
                                        <p class="font-semibold">#{assessment_data['id']}</p>
                                    </div>
                                </div>
                            </div>
                            
                            <!-- Footer del Certificato -->
                            <div class="flex justify-between items-end">
                                <div class="text-left">
                                    <div class="w-32 h-32 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                                        <i class="fas fa-qrcode text-white text-4xl"></i>
                                    </div>
                                    <p class="text-sm text-gray-600 mt-2">QR Code Verifica</p>
                                </div>
                                <div class="text-right">
                                    <p class="text-sm text-gray-600 mb-2">Generato da</p>
                                    <p class="font-bold text-lg text-blue-700">NIS2 Compliance Platform</p>
                                    <p class="text-xs text-gray-500">Piattaforma certificata per la conformità NIS2</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Sezione Informazioni Aggiuntive -->
                    <div class="bg-white rounded-2xl shadow-xl p-8 mt-8">
                        <div class="text-center mb-6">
                            <h2 class="text-2xl font-bold text-gray-800 mb-2">
                                <i class="fas fa-shield-check text-green-600 mr-3"></i>
                                Verifica Autenticità Completata
                            </h2>
                            <p class="text-gray-600">Questo certificato è stato verificato e risulta autentico</p>
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="bg-green-50 p-6 rounded-xl border border-green-200">
                                <h3 class="font-bold text-green-800 text-lg mb-3">
                                    <i class="fas fa-check-circle mr-2"></i>
                                    Documento Valido
                                </h3>
                                <ul class="text-green-700 space-y-2">
                                    <li>• QR Code verificato e autentico</li>
                                    <li>• Dati corrispondenti al database</li>
                                    <li>• Timestamp di generazione valido</li>
                                    <li>• Firma digitale confermata</li>
                                </ul>
                            </div>
                            <div class="bg-blue-50 p-6 rounded-xl border border-blue-200">
                                <h3 class="font-bold text-blue-800 text-lg mb-3">
                                    <i class="fas fa-info-circle mr-2"></i>
                                    Informazioni Tecniche
                                </h3>
                                <ul class="text-blue-700 space-y-2">
                                    <li>• Tipo: {doc_type}</li>
                                    <li>• ID: {assessment_id}</li>
                                    <li>• Data: {completed_date}</li>
                                    <li>• Score: {score}%</li>
                                </ul>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Pulsanti Azione -->
                    <div class="text-center mt-8 no-print">
                        <button onclick="window.print()" class="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-8 py-3 rounded-xl hover:from-blue-600 hover:to-blue-700 transition-all duration-200 shadow-lg font-semibold mr-4">
                            <i class="fas fa-print mr-2"></i>
                            Stampa Certificato
                        </button>
                        <button onclick="window.close()" class="bg-gray-500 text-white px-8 py-3 rounded-xl hover:bg-gray-600 transition-all duration-200 shadow-lg font-semibold">
                            <i class="fas fa-times mr-2"></i>
                            Chiudi
                        </button>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
                                    .get(doc_type, 'Documento NIS2')
                                </p>
                            </div>
                            
                            <div class="bg-gray-50 p-4 rounded-lg">
                                <h3 class="font-semibold text-gray-900 mb-2">🆔 ID Assessment</h3>
                                <p class="text-lg font-bold text-gray-700">NIS2-{assessment_id:06d}</p>
                            </div>
                        </div>
                        
                        <!-- Informazioni Fornitore -->
                        <div class="bg-blue-50 p-6 rounded-lg mb-6">
                            <h3 class="text-xl font-bold text-blue-900 mb-4">🏢 Informazioni Fornitore</h3>
                            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <p class="text-sm text-gray-600">Nome Azienda</p>
                                    <p class="font-semibold text-gray-900">{supplier_data['company_name']}</p>
                                </div>
                                <div>
                                    <p class="text-sm text-gray-600">Email</p>
                                    <p class="font-semibold text-gray-900">{supplier_data['email']}</p>
                                </div>
                                <div>
                                    <p class="text-sm text-gray-600">Settore</p>
                                    <p class="font-semibold text-gray-900">{supplier_data['sector']}</p>
                                </div>
                                <div>
                                    <p class="text-sm text-gray-600">Paese</p>
                                    <p class="font-semibold text-gray-900">{supplier_data['country']}</p>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Risultato Assessment -->
                        <div class="bg-gradient-to-r from-green-50 to-emerald-50 p-6 rounded-lg mb-6">
                            <h3 class="text-xl font-bold text-green-900 mb-4">📊 Risultato Assessment</h3>
                            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div class="text-center">
                                    <p class="text-sm text-gray-600">Punteggio</p>
                                    <p class="text-3xl font-bold text-green-600">{actual_score:.1f}%</p>
                                </div>
                                <div class="text-center">
                                    <p class="text-sm text-gray-600">Esito</p>
                                    <p class="text-xl font-bold {{
                                        'POSITIVO': 'text-green-600',
                                        'NEGATIVO': 'text-red-600'
                                    }}.get(outcome, 'text-gray-600')">
                                        {{
                                            'POSITIVO': '✅ CONFORME',
                                            'NEGATIVO': '❌ NON CONFORME'
                                        }}.get(outcome, 'N/A')
                                    </p>
                                </div>
                                <div class="text-center">
                                    <p class="text-sm text-gray-600">Data Valutazione</p>
                                    <p class="font-semibold text-gray-900">{assessment_data['completed_at']}</p>
                                </div>
                            </div>
                        </div>
                        
                        <!-- Note Legali -->
                        <div class="bg-yellow-50 p-4 rounded-lg border-l-4 border-yellow-400">
                            <h4 class="font-semibold text-yellow-800 mb-2">📋 Note Legali</h4>
                            <p class="text-sm text-yellow-700">
                                Questo documento è stato generato automaticamente dalla piattaforma NIS2 Compliance Platform. 
                                La verifica dell'autenticità conferma che il documento è stato emesso dal sistema ufficiale 
                                e non è stato alterato. Per ulteriori informazioni, contattare l'amministratore della piattaforma.
                            </p>
                        </div>
                    </div>
                    
                    <!-- Footer -->
                    <div class="text-center text-gray-500">
                        <p>© 2024 NIS2 Compliance Platform - Documento verificato il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nella verifica: {str(e)}")
    finally:
        conn.close()

@app.get("/api/company/suppliers/{supplier_id}/download-recall")
async def download_recall(supplier_id: int, request: Request):
    """Scarica il report di richiamo per un fornitore non conforme"""
    # Verifica autenticazione
    user = await get_current_user(request)
    if not user or user.get('role') != 'company':
        raise HTTPException(status_code=401, detail="Non autorizzato")
    
    try:
        # Importa il generatore PDF professionale
        from professional_pdf_generator import generate_assessment_pdf
        
        # Trova l'ultimo assessment completato del fornitore
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id FROM assessments 
            WHERE supplier_id = ? AND status = 'completed'
            ORDER BY completed_at DESC
            LIMIT 1
        """, (supplier_id,))
        
        assessment = cursor.fetchone()
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment non trovato")
        
        assessment_id = assessment[0]
        
        # Genera il PDF
        pdf_path = generate_assessment_pdf(assessment_id, "temp_pdfs")
        
        if not pdf_path or not os.path.exists(pdf_path):
            raise HTTPException(status_code=500, detail="Errore nella generazione del PDF")
        
        # Restituisci il file
        return FileResponse(
            path=pdf_path,
            filename=f"richiamo_nis2_professionale_{supplier_id}.pdf",
            media_type="application/pdf"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel download: {str(e)}")
    finally:
        conn.close()

@app.get("/supplier-assessments/{company_id}/{supplier_id}", response_class=HTMLResponse)
async def supplier_assessments_page(company_id: int, supplier_id: int, request: Request):
    """Pagina per visualizzare tutti gli assessment di un fornitore"""
    user = await get_current_user(request)
    if not user or user.get('role') != 'company':
        return RedirectResponse(url="/company-login")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Ottieni informazioni del fornitore
        cursor.execute("""
            SELECT company_name, email, sector, country
            FROM suppliers 
            WHERE id = ? AND company_id = ?
        """, (supplier_id, company_id))
        
        supplier = cursor.fetchone()
        if not supplier:
            raise HTTPException(status_code=404, detail="Fornitore non trovato")
        
        # Ottieni tutti gli assessment del fornitore
        cursor.execute("""
            SELECT id, status, evaluation_result, completed_at, created_at
            FROM assessments 
            WHERE supplier_id = ?
            ORDER BY created_at DESC
        """, (supplier_id,))
        
        assessments = []
        for row in cursor.fetchall():
            assessment_id, status, evaluation_result, completed_at, created_at = row
            
            # Parsa il risultato della valutazione
            eval_data = None
            if evaluation_result:
                try:
                    import json
                    eval_data = json.loads(evaluation_result)
                except:
                    eval_data = None
            
            assessments.append({
                "id": assessment_id,
                "status": status,
                "evaluation_result": eval_data,
                "completed_at": completed_at,
                "created_at": created_at
            })
        
        html_content = f"""
        <!DOCTYPE html>
        <html lang="it">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Assessment Fornitore - {supplier[0]}</title>
            <script src="https://cdn.tailwindcss.com"></script>
        </head>
        <body class="bg-gray-100">
            <header class="bg-white shadow-sm border-b border-gray-200">
                <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div class="flex justify-between items-center py-4">
                        <div class="flex items-center">
                            <a href="/company-dashboard/{company_id}" class="text-blue-600 hover:text-blue-800 mr-4">
                                ← Torna alla Dashboard
                            </a>
                            <h1 class="text-2xl font-bold text-gray-900">📊 Assessment Fornitore</h1>
                        </div>
                    </div>
                </div>
            </header>

            <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <!-- Informazioni Fornitore -->
                <div class="bg-white rounded-lg shadow-lg p-6 mb-8">
                    <h2 class="text-xl font-semibold text-gray-900 mb-4">🏢 {supplier[0]}</h2>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div>
                            <p class="text-sm text-gray-600">Email</p>
                            <p class="font-medium">{supplier[1]}</p>
                        </div>
                        <div>
                            <p class="text-sm text-gray-600">Settore</p>
                            <p class="font-medium">{supplier[2]}</p>
                        </div>
                        <div>
                            <p class="text-sm text-gray-600">Paese</p>
                            <p class="font-medium">{supplier[3]}</p>
                        </div>
                    </div>
                </div>

                <!-- Lista Assessment -->
                <div class="bg-white rounded-lg shadow-lg">
                    <div class="px-6 py-4 border-b border-gray-200">
                        <h3 class="text-lg font-semibold text-gray-900">
                            📋 Cronologia Assessment ({len(assessments)} totali)
                        </h3>
                    </div>
                    <div class="p-6">
                        {f'''
                        <div class="space-y-4">
                            {''.join([f'''
                            <div class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                                <div class="flex justify-between items-start">
                                    <div class="flex-1">
                                        <div class="flex items-center mb-2">
                                            <span class="text-sm font-medium text-gray-900">Assessment #{assessment["id"]}</span>
                                            <span class="ml-2 px-2 py-1 text-xs rounded-full {{
                                                'bg-green-100 text-green-800' if assessment["status"] == 'completed' else 'bg-yellow-100 text-yellow-800'
                                            }}">
                                                {assessment["status"].upper()}
                                            </span>
                                        </div>
                                        <div class="text-sm text-gray-600">
                                            <p>Creato: {assessment["created_at"]}</p>
                                            {f'<p>Completato: {assessment["completed_at"]}</p>' if assessment["completed_at"] else ''}
                                        </div>
                                        {f'''
                                        <div class="mt-3 p-3 rounded-lg {{
                                            'bg-green-50 border border-green-200' if assessment["evaluation_result"] and assessment["evaluation_result"].get("outcome") == "POSITIVO" else 'bg-red-50 border border-red-200'
                                        }}">
                                            <div class="flex items-center justify-between">
                                                <div>
                                                    <p class="font-medium {{
                                                        'text-green-800' if assessment["evaluation_result"] and assessment["evaluation_result"].get("outcome") == "POSITIVO" else 'text-red-800'
                                                    }}">
                                                        Risultato: {assessment["evaluation_result"]["outcome"] if assessment["evaluation_result"] else "N/A"}
                                                    </p>
                                                    <p class="text-sm {{
                                                        'text-green-600' if assessment["evaluation_result"] and assessment["evaluation_result"].get("outcome") == "POSITIVO" else 'text-red-600'
                                                    }}">
                                                        Punteggio: {assessment["evaluation_result"]["final_percentage"]:.1%} if assessment["evaluation_result"] else "N/A"
                                                    </p>
                                                </div>
                                                <div class="flex space-x-2">
                                                    <button onclick="viewResults({company_id}, {supplier_id}, {assessment["id"]})" 
                                                            class="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600">
                                                        📊 Dettagli
                                                    </button>
                                                    {f'''
                                                    <button onclick="downloadPassport({supplier_id})" 
                                                            class="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600">
                                                        🏆 Passaporto
                                                    </button>
                                                    ''' if assessment["evaluation_result"] and assessment["evaluation_result"].get("outcome") == "POSITIVO" else f'''
                                                    <button onclick="downloadRecall({supplier_id})" 
                                                            class="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600">
                                                        ⚠️ Richiamo
                                                    </button>
                                                    '''}
                                                </div>
                                            </div>
                                        </div>
                                        ''' if assessment["evaluation_result"] else ''}
                                    </div>
                                </div>
                            </div>
                            ''' for assessment in assessments])}
                        </div>
                        ''' if assessments else '''
                        <div class="text-center py-8">
                            <p class="text-gray-500">Nessun assessment trovato per questo fornitore.</p>
                        </div>
                        '''}
                    </div>
                </div>
            </main>

            <script>
                function viewResults(companyId, supplierId, assessmentId) {{
                    window.open(`/assessment-results/${{companyId}}/${{supplierId}}?assessment_id=${{assessmentId}}`, '_blank');
                }}
                
                function downloadPassport(supplierId) {{
                    const link = document.createElement('a');
                    link.href = `/api/company/suppliers/${{supplierId}}/download-passport`;
                    link.download = `passaporto_nis2_${{supplierId}}.pdf`;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }}
                
                function downloadRecall(supplierId) {{
                    const link = document.createElement('a');
                    link.href = `/api/company/suppliers/${{supplierId}}/download-recall`;
                    link.download = `richiamo_nis2_${{supplierId}}.pdf`;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                }}
            </script>
        </body>
        </html>
        """
        
        return html_content
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel recupero assessment: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Avvio server FastAPI...")
    print("📊 Demo: http://localhost:8000/demo")
    print("📚 Docs: http://localhost:8000/docs")
    print("❓ Questionario: http://localhost:8000/questionario")
    uvicorn.run(app, host="0.0.0.0", port=8000)
