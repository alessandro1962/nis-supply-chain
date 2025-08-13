#!/usr/bin/env python3
"""
Script per avviare la Piattaforma NIS2 in modalità sviluppo locale
Senza Docker - Solo backend FastAPI con database SQLite
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def print_banner():
    print("🛡️  Piattaforma NIS2 Supplier Assessment - Modalità Sviluppo")
    print("=" * 60)
    print("Backend: FastAPI + SQLite")
    print("Frontend: File statici (senza build)")
    print("=" * 60)

def install_dependencies():
    print("📦 Installazione dipendenze Python...")
    
    # Lista dipendenze essenziali per il backend
    essential_deps = [
        "fastapi",
        "uvicorn[standard]",
        "sqlalchemy",
        "pydantic",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "python-multipart",
        "jinja2",
        "qrcode[pil]",
        "aiofiles"
    ]
    
    for dep in essential_deps:
        print(f"Installando {dep}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            print(f"⚠️  Errore installando {dep}, continuando...")

def create_sqlite_database():
    print("🗄️  Creazione database SQLite...")
    
    # Crea il file database
    db_path = "nis2_dev.db"
    conn = sqlite3.connect(db_path)
    
    # Schema semplificato per demo
    cursor = conn.cursor()
    
    # Tabella users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'company',
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabella companies
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            admin_email TEXT NOT NULL,
            sector TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Tabella suppliers
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            company_name TEXT NOT NULL,
            email TEXT NOT NULL,
            sector TEXT,
            country TEXT,
            questionnaire_hash TEXT UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    """)
    
    # Inserisci utente admin di esempio
    cursor.execute("""
        INSERT OR IGNORE INTO users (username, email, hashed_password, role) 
        VALUES ('admin', 'admin@nis2.local', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', 'admin')
    """)
    # Password: secret123
    
    # Inserisci azienda di esempio
    cursor.execute("""
        INSERT OR IGNORE INTO companies (name, admin_email, sector) 
        VALUES ('Azienda Demo', 'demo@company.com', 'IT')
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ Database creato: {db_path}")

def create_simple_backend():
    print("⚙️  Creazione backend semplificato...")
    
    backend_code = '''
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List
import json

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Database helper
def get_db_connection():
    return sqlite3.connect("nis2_dev.db")

# Routes
@app.get("/")
async def root():
    return {
        "message": "Piattaforma NIS2 Supplier Assessment API",
        "version": "1.0.0-dev",
        "mode": "development",
        "database": "SQLite",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "nis2-platform-api-dev"}

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    # Login semplificato per demo
    if request.username == "admin" and request.password == "secret123":
        return {
            "access_token": "demo-token-admin",
            "token_type": "bearer",
            "user": {
                "id": 1,
                "username": "admin",
                "email": "admin@nis2.local",
                "role": "admin"
            }
        }
    raise HTTPException(status_code=401, detail="Credenziali non valide")

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
            "created_at": row[4]
        })
    
    conn.close()
    return companies

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

if __name__ == "__main__":
    print("🚀 Avvio server FastAPI...")
    print("📊 Demo: http://localhost:8000/demo")
    print("📚 Docs: http://localhost:8000/docs")
    print("❓ Questionario: http://localhost:8000/questionario")
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    with open("main_dev.py", "w", encoding="utf-8") as f:
        f.write(backend_code)
    
    print("✅ Backend semplificato creato: main_dev.py")

def main():
    print_banner()
    
    # Controlla se siamo nella directory giusta
    if not os.path.exists("questionario_nis2.json"):
        print("❌ File questionario_nis2.json non trovato!")
        print("   Assicurati di essere nella directory del progetto")
        return
    
    install_dependencies()
    create_sqlite_database()
    create_simple_backend()
    
    print("\n🎉 Setup completato!")
    print("\n🚀 Per avviare il server:")
    print("   python main_dev.py")
    print("\n📱 Poi apri nel browser:")
    print("   • Demo: http://localhost:8000/demo")
    print("   • API Docs: http://localhost:8000/docs")
    print("   • Questionario: http://localhost:8000/questionario")
    print("\n🔐 Credenziali demo:")
    print("   Username: admin")
    print("   Password: secret123")

if __name__ == "__main__":
    main() 