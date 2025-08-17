#!/usr/bin/env python3
"""
Sistema di Login Unificato per NIS2 Supply Chain
Gestisce l'accesso per Admin, Azienda e Dipendenti
"""
from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import sqlite3
import jwt
from datetime import datetime, timedelta
from typing import Optional

# Configurazione
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"

# Router e templates
unified_router = APIRouter()
templates = Jinja2Templates(directory="templates")

@unified_router.get("/unified-login")
async def unified_login_page(request: Request):
    """Pagina di login unificata"""
    return templates.TemplateResponse("unified_login.html", {
        "request": request
    })

@unified_router.post("/unified-login")
async def unified_login(
    request: Request,
    user_type: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    """Gestisce il login per tutti i tipi di utente"""
    
    try:
        if user_type == "admin":
            return await handle_admin_login(request, email, password)
        elif user_type == "company":
            return await handle_company_login(request, email, password)
        elif user_type == "employee":
            return await handle_employee_login(request, email, password)
        else:
            return templates.TemplateResponse("unified_login.html", {
                "request": request,
                "error": "Tipo di utente non valido"
            })
    except Exception as e:
        return templates.TemplateResponse("unified_login.html", {
            "request": request,
            "error": f"Errore durante il login: {str(e)}"
        })

async def handle_admin_login(request: Request, email: str, password: str):
    """Gestisce il login per gli amministratori"""
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, name, email, role 
            FROM admins 
            WHERE email = ? AND password = ?
        """, (email, password))
        
        admin = cursor.fetchone()
        if admin:
            # Crea token JWT per admin
            payload = {
                "sub": admin[2],
                "role": "admin",
                "admin_id": admin[0],
                "admin_name": admin[1],
                "exp": datetime.utcnow() + timedelta(hours=24)
            }
            
            token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
            
            response = RedirectResponse(url="/admin-dashboard", status_code=302)
            response.set_cookie(key="admin_token", value=token, httponly=True, max_age=86400)
            return response
        else:
            return templates.TemplateResponse("unified_login.html", {
                "request": request,
                "error": "Credenziali amministratore non valide"
            })
    finally:
        conn.close()

async def handle_company_login(request: Request, email: str, password: str):
    """Gestisce il login per le aziende"""
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, name, email, contact_person 
            FROM companies 
            WHERE email = ? AND password = ?
        """, (email, password))
        
        company = cursor.fetchone()
        if company:
            # Crea token JWT per azienda
            payload = {
                "sub": company[2],
                "role": "company",
                "company_id": company[0],
                "company_name": company[1],
                "contact_person": company[3],
                "exp": datetime.utcnow() + timedelta(hours=24)
            }
            
            token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
            
            response = RedirectResponse(url="/company-dashboard", status_code=302)
            response.set_cookie(key="access_token", value=token, httponly=True, max_age=86400)
            return response
        else:
            return templates.TemplateResponse("unified_login.html", {
                "request": request,
                "error": "Credenziali azienda non valide"
            })
    finally:
        conn.close()

async def handle_employee_login(request: Request, email: str, password: str):
    """Gestisce il login per i dipendenti"""
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, name, email, role, department, company_id
            FROM training_employees 
            WHERE email = ? AND password = ?
        """, (email, password))
        
        employee = cursor.fetchone()
        if employee:
            # Crea token JWT per dipendente
            payload = {
                "sub": employee[2],
                "role": "employee",
                "employee_id": employee[0],
                "employee_name": employee[1],
                "employee_role": employee[3],
                "department": employee[4],
                "company_id": employee[5],
                "exp": datetime.utcnow() + timedelta(hours=24)
            }
            
            token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
            
            response = RedirectResponse(url="/training/employee-dashboard", status_code=302)
            response.set_cookie(key="employee_token", value=token, httponly=True, max_age=86400)
            return response
        else:
            return templates.TemplateResponse("unified_login.html", {
                "request": request,
                "error": "Credenziali dipendente non valide"
            })
    finally:
        conn.close()

# Funzioni helper per verificare l'autenticazione
def get_current_admin(request: Request) -> Optional[dict]:
    """Ottiene l'amministratore corrente dai cookies"""
    token = request.cookies.get("admin_token")
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        return None

def get_current_company(request: Request) -> Optional[dict]:
    """Ottiene l'azienda corrente dai cookies"""
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        return None

def get_current_employee(request: Request) -> Optional[dict]:
    """Ottiene il dipendente corrente dai cookies"""
    token = request.cookies.get("employee_token")
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        return None

@unified_router.get("/logout")
async def logout(request: Request):
    """Logout per tutti i tipi di utente"""
    response = RedirectResponse(url="/unified-login", status_code=302)
    
    # Rimuovi tutti i possibili cookie di autenticazione
    response.delete_cookie("admin_token")
    response.delete_cookie("access_token")
    response.delete_cookie("employee_token")
    
    return response
