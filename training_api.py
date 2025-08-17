from fastapi import APIRouter, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from training_module import TrainingModule
import json
import sqlite3
from typing import Optional

# Configurazione JWT (stessa del file principale)
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"

# Inizializza il modulo training
training = TrainingModule()

# Router per le API di training
training_router = APIRouter(prefix="/training", tags=["Training"])

# Templates
templates = Jinja2Templates(directory="templates")

# Funzione helper per ottenere l'utente corrente
async def get_current_user(request: Request):
    """Ottiene l'utente corrente dai cookie"""
    token = request.cookies.get("access_token")
    if not token:
        print("❌ Debug: Nessun token trovato nei cookie")
        return None
    
    try:
        # Decodifica il token JWT
        import jwt
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"✅ Debug: Token decodificato - {payload}")
        return payload
    except Exception as e:
        print(f"❌ Debug: Errore decodifica token - {e}")
        return None

# ==================== AUTENTICAZIONE DIPENDENTI ====================

@training_router.get("/employee-login")
async def employee_login_page(request: Request):
    """Pagina di login per i dipendenti"""
    return templates.TemplateResponse("training_employee_login.html", {
        "request": request
    })

@training_router.post("/employee-login")
async def employee_login(request: Request, email: str = Form(...), password: str = Form(...)):
    """Login per i dipendenti"""
    print(f"🔍 Debug: Login dipendente - email: {email}, password: {password}")
    
    try:
        # Verifica credenziali dipendente
        print("🔍 Debug: Chiamata authenticate_employee...")
        employee = training.authenticate_employee(email, password)
        print(f"🔍 Debug: Risultato authenticate_employee - {employee}")
        
        if employee:
            print("✅ Debug: Autenticazione riuscita, creo token...")
            # Crea token JWT per il dipendente
            import jwt
            from datetime import datetime, timedelta
            
            payload = {
                "sub": employee['email'],
                "role": "employee",
                "employee_id": employee['id'],
                "employee_name": employee['name'],
                "company_id": employee['company_id'],
                "exp": datetime.utcnow() + timedelta(hours=24)
            }
            
            token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
            print(f"✅ Debug: Token creato - {token[:50]}...")
            
            print("✅ Debug: Creo RedirectResponse...")
            response = RedirectResponse(url="/training/employee-dashboard", status_code=302)
            print("✅ Debug: Imposto cookie...")
            response.set_cookie(key="employee_token", value=token, httponly=True, max_age=86400)
            print("✅ Debug: Redirect a /training/employee-dashboard")
            print(f"✅ Debug: Response status: {response.status_code}")
            print(f"✅ Debug: Response headers: {response.headers}")
            return response
        else:
            print("❌ Debug: Autenticazione fallita, mostro errore")
            return templates.TemplateResponse("training_employee_login.html", {
                "request": request,
                "error": "Credenziali non valide"
            })
    except Exception as e:
        print(f"❌ Debug: Errore nel login - {e}")
        return templates.TemplateResponse("training_employee_login.html", {
            "request": request,
            "error": f"Errore: {str(e)}"
        })

@training_router.get("/employee-dashboard")
async def employee_dashboard(request: Request):
    """Dashboard del dipendente"""
    employee = await get_current_employee(request)
    if not employee:
        return RedirectResponse(url="/training/employee-login")
    
    try:
        # Ottieni i corsi del dipendente
        enrollments = training.get_employee_enrollments(employee['employee_id'])
        certifications = training.get_employee_certifications(employee['employee_id'])
        notifications = training.get_employee_notifications(employee['employee_id'])
        
        return templates.TemplateResponse("training_employee_dashboard.html", {
            "request": request,
            "employee": employee,
            "enrollments": enrollments,
            "certifications": certifications,
            "notifications": notifications
        })
    except Exception as e:
        return templates.TemplateResponse("training_employee_dashboard.html", {
            "request": request,
            "employee": employee,
            "enrollments": [],
            "certifications": [],
            "notifications": [],
            "error": str(e)
        })

@training_router.get("/employee-courses")
async def employee_courses_page(request: Request):
    """Pagina corsi del dipendente"""
    employee = await get_current_employee(request)
    if not employee:
        return RedirectResponse(url="/training/employee-login")
    
    try:
        # Ottieni i corsi del dipendente
        enrollments = training.get_employee_enrollments(employee['employee_id'])
        certifications = training.get_employee_certifications(employee['employee_id'])
        
        return templates.TemplateResponse("training_employee_courses.html", {
            "request": request,
            "employee": employee,
            "enrollments": enrollments,
            "certifications": certifications
        })
    except Exception as e:
        return templates.TemplateResponse("training_employee_courses.html", {
            "request": request,
            "employee": employee,
            "enrollments": [],
            "certifications": [],
            "error": str(e)
        })

# Funzione helper per ottenere il dipendente corrente
async def get_current_employee(request: Request):
    """Ottiene il dipendente corrente dai cookies"""
    token = request.cookies.get("employee_token")
    if not token:
        return None
    
    try:
        # Decodifica il token JWT
        import jwt
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception as e:
        return None

# ==================== PAGINE PRINCIPALI ====================

@training_router.get("/dashboard")
async def training_dashboard(request: Request):
    """Dashboard principale del modulo training"""
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/company-login")
    
    company_id = user.get("company_id", 1)
    
    try:
        # Ottieni statistiche training
        stats = training.get_training_stats(company_id)
        
        # Ottieni dipendenti
        employees = training.get_employees(company_id)
        
        # Ottieni corsi disponibili
        courses = training.get_courses()
        
        return templates.TemplateResponse("training_dashboard.html", {
            "request": request,
            "user": user,
            "stats": stats,
            "employees": employees,
            "courses": courses
        })
    except Exception as e:
        return templates.TemplateResponse("training_dashboard.html", {
            "request": request,
            "user": user,
            "stats": {},
            "employees": [],
            "courses": [],
            "error": str(e)
        })

@training_router.get("/employees")
async def training_employees_page(request: Request):
    """Pagina gestione dipendenti"""
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/company-login")
    
    company_id = user.get("company_id")
    if not company_id:
        return RedirectResponse(url="/company-login")
    
    try:
        employees = training.get_employees(company_id)
        return templates.TemplateResponse("training_employees.html", {
            "request": request,
            "user": user,
            "employees": employees
        })
    except Exception as e:
        return templates.TemplateResponse("training_employees.html", {
            "request": request,
            "user": user,
            "employees": [],
            "error": str(e)
        })

@training_router.get("/courses")
async def training_courses_page(request: Request):
    """Pagina corsi disponibili"""
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/company-login")
    
    try:
        courses = training.get_courses()
        employees = training.get_employees(user.get("company_id", 1))
        stats = training.get_training_stats(user.get("company_id", 1))
        
        return templates.TemplateResponse("training_courses.html", {
            "request": request,
            "user": user,
            "courses": courses,
            "employees": employees,
            "stats": stats
        })
    except Exception as e:
        return templates.TemplateResponse("training_courses.html", {
            "request": request,
            "user": user,
            "courses": [],
            "employees": [],
            "stats": {},
            "error": str(e)
        })

@training_router.get("/employee/{employee_id}")
async def employee_training_page(request: Request, employee_id: int):
    """Pagina dettaglio dipendente con i suoi corsi"""
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/company-login")
    
    try:
        # Ottieni dipendente
        employees = training.get_employees(user.get("company_id"))
        employee = next((e for e in employees if e['id'] == employee_id), None)
        
        if not employee:
            raise HTTPException(status_code=404, detail="Dipendente non trovato")
        
        # Ottieni iscrizioni
        enrollments = training.get_employee_enrollments(employee_id)
        
        # Ottieni certificazioni
        certifications = training.get_employee_certifications(employee_id)
        
        # Ottieni notifiche
        notifications = training.get_employee_notifications(employee_id)
        
        return templates.TemplateResponse("training_employee_detail.html", {
            "request": request,
            "user": user,
            "employee": employee,
            "enrollments": enrollments,
            "certifications": certifications,
            "notifications": notifications
        })
    except Exception as e:
        return templates.TemplateResponse("training_employee_detail.html", {
            "request": request,
            "user": user,
            "employee": None,
            "enrollments": [],
            "certifications": [],
            "notifications": [],
            "error": str(e)
        })

@training_router.get("/course/{enrollment_id}")
async def course_view_page(request: Request, enrollment_id: int):
    """Pagina per visualizzare un corso in corso"""
    # Prova prima l'autenticazione admin dal sistema unificato
    from unified_login import get_current_admin
    admin_user = get_current_admin(request)
    
    # Prova l'autenticazione azienda
    user = await get_current_user(request)
    
    # Prova l'autenticazione dipendente
    employee = await get_current_employee(request)
    
    # Determina quale tipo di utente è
    current_user = None
    if admin_user:
        current_user = admin_user
    elif user:
        current_user = user
    elif employee:
        current_user = employee
    else:
        return RedirectResponse(url="/unified-login")
    
    try:
        # Ottieni dettagli iscrizione
        conn = sqlite3.connect('nis2_supply_chain.db')
        cursor = conn.cursor()
        
        # Determina il company_id
        company_id = None
        if admin_user:
            # Admin può vedere tutto, usa company_id 1 di default
            company_id = 1
        elif user:
            company_id = user.get("company_id", 1)
        elif employee:
            company_id = employee.get("company_id", 1)
        
        cursor.execute("""
            SELECT e.id, e.enrollment_date, e.completion_date, e.status, e.score,
                   c.id as course_id, c.title, c.description, c.category, c.duration_minutes, c.difficulty_level,
                   te.id as employee_id, te.name as employee_name
            FROM training_enrollments e
            JOIN training_courses c ON e.course_id = c.id
            JOIN training_employees te ON e.employee_id = te.id
            WHERE e.id = ? AND te.company_id = ?
        """, (enrollment_id, company_id))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Iscrizione non trovata")
        
        enrollment = {
            'enrollment_id': row[0],
            'enrollment_date': row[1],
            'completion_date': row[2],
            'status': row[3],
            'score': row[4]
        }
        
        course = {
            'id': row[5],
            'title': row[6],
            'description': row[7],
            'category': row[8],
            'duration_minutes': row[9],
            'difficulty_level': row[10]
        }
        
        # Ottieni quiz del corso
        quiz = training.get_course_quiz(course['id'])
        
        # Ottieni contenuti del corso
        course_contents = training.get_course_content(course['id'])
        
        # Calcola progresso reale
        total_modules = len(course_contents) if course_contents else 0
        completed_modules = 0
        
        # Per ora, considera completati i primi 2 moduli (in futuro si userà il progress_data)
        if total_modules > 0:
            completed_modules = min(2, total_modules)
        
        progress = int((completed_modules / total_modules) * 100) if total_modules > 0 else 0
        
        conn.close()
        
        # Scegli il template in base al tipo di utente
        template_name = "training_employee_course_view.html" if employee else "training_course_view.html"
        
        return templates.TemplateResponse(template_name, {
            "request": request,
            "user": current_user,
            "employee": employee,  # Aggiungi employee per il template dipendente
            "enrollment": enrollment,
            "course": course,
            "quiz": quiz,
            "course_contents": course_contents,
            "progress": progress,
            "completed_modules": completed_modules,
            "total_modules": total_modules
        })
    except Exception as e:
        return templates.TemplateResponse("training_course_view.html", {
            "request": request,
            "user": current_user,
            "enrollment": None,
            "course": None,
            "quiz": None,
            "progress": 0,
            "completed_modules": 0,
            "total_modules": 0,
            "error": str(e)
        })

# ==================== API ENDPOINTS ====================

@training_router.post("/api/employees")
async def add_employee_api(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    role: str = Form(...),
    department: str = Form(None),
    hire_date: str = Form(None)
):
    """API per aggiungere un nuovo dipendente"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Non autorizzato")
    
    company_id = user.get("company_id")
    if not company_id:
        raise HTTPException(status_code=400, detail="ID azienda mancante")
    
    # Validazione password
    if password != confirm_password:
        raise HTTPException(status_code=400, detail="Le password non coincidono")
    
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="La password deve essere di almeno 6 caratteri")
    
    try:
        employee_id = training.add_employee_with_password(company_id, name, email, password, role, department, hire_date)
        return {"success": True, "employee_id": employee_id, "message": "Dipendente aggiunto con successo"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")

@training_router.put("/api/employees/{employee_id}")
async def update_employee_api(
    request: Request,
    employee_id: int,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(None),
    confirm_password: str = Form(None),
    role: str = Form(...),
    department: str = Form(None),
    hire_date: str = Form(None)
):
    """API per aggiornare un dipendente esistente"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Non autorizzato")
    
    company_id = user.get("company_id")
    if not company_id:
        raise HTTPException(status_code=400, detail="ID azienda mancante")
    
    # Validazione password se fornita
    if password:
        if password != confirm_password:
            raise HTTPException(status_code=400, detail="Le password non coincidono")
        
        if len(password) < 6:
            raise HTTPException(status_code=400, detail="La password deve essere di almeno 6 caratteri")
    
    try:
        training.update_employee_with_password(employee_id, company_id, name, email, password, role, department, hire_date)
        return {"success": True, "message": "Dipendente aggiornato con successo"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")

@training_router.get("/api/employee/{employee_id}")
async def get_employee_api(request: Request, employee_id: int):
    """API per ottenere i dati di un dipendente specifico"""
    print(f"🔍 Debug: Richiesta dipendente ID {employee_id}")
    
    user = await get_current_user(request)
    if not user:
        print("❌ Debug: Utente non autenticato")
        raise HTTPException(status_code=401, detail="Non autorizzato")
    
    print(f"✅ Debug: Utente autenticato - {user}")
    
    company_id = user.get("company_id")
    if not company_id:
        print("❌ Debug: ID azienda mancante")
        raise HTTPException(status_code=400, detail="ID azienda mancante")
    
    print(f"🏢 Debug: Company ID {company_id}")
    
    try:
        employee = training.get_employee_by_id(employee_id, company_id)
        if not employee:
            print(f"❌ Debug: Dipendente {employee_id} non trovato per company {company_id}")
            raise HTTPException(status_code=404, detail="Dipendente non trovato")
        
        print(f"✅ Debug: Dipendente trovato - {employee['name']}")
        return {"success": True, "employee": employee}
    except Exception as e:
        print(f"❌ Debug: Errore interno - {e}")
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")

@training_router.post("/api/enroll")
async def enroll_employee_api(
    request: Request,
    employee_id: int = Form(...),
    course_id: int = Form(...)
):
    """API per iscrivere un dipendente a un corso"""
    print(f"🔍 Debug: Tentativo iscrizione - employee_id: {employee_id}, course_id: {course_id}")
    
    user = await get_current_user(request)
    if not user:
        print("❌ Debug: Utente non autenticato")
        raise HTTPException(status_code=401, detail="Non autorizzato")
    
    print(f"✅ Debug: Utente autenticato - {user}")
    
    try:
        enrollment_id = training.enroll_employee(employee_id, course_id)
        print(f"✅ Debug: Iscrizione riuscita - enrollment_id: {enrollment_id}")
        return {"success": True, "enrollment_id": enrollment_id, "message": "Iscrizione effettuata con successo"}
    except ValueError as e:
        print(f"❌ Debug: Errore di validazione - {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"❌ Debug: Errore generico - {e}")
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")

@training_router.get("/api/courses")
async def get_courses_api(request: Request, category: Optional[str] = None):
    """API per ottenere i corsi disponibili"""
    try:
        courses = training.get_courses(category)
        return {"success": True, "courses": courses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")

@training_router.get("/api/quiz/{course_id}")
async def get_course_quiz_api(request: Request, course_id: int):
    """API per ottenere il quiz di un corso"""
    try:
        quiz = training.get_course_quiz(course_id)
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz non trovato per questo corso")
        return {"success": True, "quiz": quiz}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")

@training_router.post("/api/quiz/submit")
async def submit_quiz_api(
    request: Request,
    enrollment_id: int = Form(...),
    quiz_id: int = Form(...),
    answers: str = Form(...),  # JSON string
    score: int = Form(...)
):
    """API per sottomettere un quiz"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Non autorizzato")
    
    try:
        answers_dict = json.loads(answers)
        attempt_id = training.submit_quiz_attempt(enrollment_id, quiz_id, answers_dict, score)
        return {"success": True, "attempt_id": attempt_id, "message": "Quiz completato con successo"}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Formato risposte non valido")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")

@training_router.get("/api/stats/{company_id}")
async def get_training_stats_api(request: Request, company_id: int):
    """API per ottenere statistiche training"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Non autorizzato")
    
    try:
        stats = training.get_training_stats(company_id)
        return {"success": True, "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")

@training_router.get("/api/notifications/{employee_id}")
async def get_notifications_api(request: Request, employee_id: int, unread_only: bool = False):
    """API per ottenere le notifiche di un dipendente"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Non autorizzato")
    
    try:
        notifications = training.get_employee_notifications(employee_id, unread_only)
        return {"success": True, "notifications": notifications}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")

# ==================== PAGINE QUIZ ====================

@training_router.get("/quiz/{enrollment_id}")
async def take_quiz_page(request: Request, enrollment_id: int):
    """Pagina per sostenere un quiz"""
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/company-login")
    
    try:
        # Ottieni dettagli iscrizione
        # Nota: questo richiederebbe un metodo aggiuntivo nel training module
        # Per ora usiamo un approccio semplificato
        
        return templates.TemplateResponse("training_quiz.html", {
            "request": request,
            "user": user,
            "enrollment_id": enrollment_id
        })
    except Exception as e:
        return templates.TemplateResponse("training_quiz.html", {
            "request": request,
            "user": user,
            "enrollment_id": enrollment_id,
            "error": str(e)
        })

# ==================== PAGINE REPORT ====================

@training_router.get("/reports")
async def training_reports_page(request: Request):
    """Pagina report e statistiche training"""
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/company-login")
    
    company_id = user.get("company_id")
    if not company_id:
        return RedirectResponse(url="/company-login")
    
    try:
        stats = training.get_training_stats(company_id)
        employees = training.get_employees(company_id)
        
        return templates.TemplateResponse("training_reports.html", {
            "request": request,
            "user": user,
            "stats": stats,
            "employees": employees
        })
    except Exception as e:
        return templates.TemplateResponse("training_reports.html", {
            "request": request,
            "user": user,
            "stats": {},
            "employees": [],
            "error": str(e)
        })

# ==================== PAGINA NOTIFICHE ====================

@training_router.get("/notifications")
async def training_notifications_page(request: Request):
    """Pagina gestione notifiche"""
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/company-login")
    
    company_id = user.get("company_id")
    if not company_id:
        return RedirectResponse(url="/company-login")
    
    try:
        # Ottieni tutte le notifiche per l'azienda
        employees = training.get_employees(company_id)
        all_notifications = []
        
        for employee in employees:
            notifications = training.get_employee_notifications(employee['id'])
            all_notifications.extend(notifications)
        
        return templates.TemplateResponse("training_notifications.html", {
            "request": request,
            "user": user,
            "notifications": all_notifications
        })
    except Exception as e:
        return templates.TemplateResponse("training_notifications.html", {
            "request": request,
            "user": user,
            "notifications": [],
            "error": str(e)
        })

# ==================== PAGINA GESTIONE CORSI ====================

@training_router.get("/course-management")
async def course_management_page(request: Request):
    """Pagina gestione corsi di formazione - SOLO ADMIN"""
    # Prova prima l'autenticazione admin dal sistema unificato
    from unified_login import get_current_admin
    user = get_current_admin(request)
    
    # Se non funziona, prova l'autenticazione del training module
    if not user:
        user = await get_current_user(request)
    
    if not user:
        return RedirectResponse(url="/unified-login")
    
    # Verifica che sia admin
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accesso negato. Solo gli amministratori possono gestire i corsi.")
    
    try:
        courses = training.get_courses()
        
        # Aggiungi statistiche per ogni corso
        for course in courses:
            stats = training.get_course_stats(course['id'])
            course['completed_count'] = stats['completed']
        
        return templates.TemplateResponse("training_course_management.html", {
            "request": request,
            "user": user,
            "courses": courses
        })
    except Exception as e:
        return templates.TemplateResponse("training_course_management.html", {
            "request": request,
            "user": user,
            "courses": [],
            "error_message": str(e)
        })

@training_router.get("/course/{course_id}/content")
async def course_content_management_page(request: Request, course_id: int):
    """Pagina gestione contenuti di un corso - SOLO ADMIN"""
    # Prova prima l'autenticazione admin dal sistema unificato
    from unified_login import get_current_admin
    user = get_current_admin(request)
    
    # Se non funziona, prova l'autenticazione del training module
    if not user:
        user = await get_current_user(request)
    
    if not user:
        return RedirectResponse(url="/unified-login")
    
    # Verifica che sia admin
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accesso negato. Solo gli amministratori possono gestire i corsi.")
    
    try:
        course = training.get_course_by_id(course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Corso non trovato")
        
        content = training.get_course_content(course_id)
        quiz = training.get_course_quiz(course_id)
        
        return templates.TemplateResponse("training_course_content.html", {
            "request": request,
            "user": user,
            "course": course,
            "content": content,
            "quiz": quiz
        })
    except Exception as e:
        return templates.TemplateResponse("training_course_content.html", {
            "request": request,
            "user": user,
            "course": None,
            "content": [],
            "quiz": None,
            "error_message": str(e)
        })

@training_router.get("/course/{course_id}/quiz")
async def course_quiz_management_page(request: Request, course_id: int):
    """Pagina gestione quiz di un corso - SOLO ADMIN"""
    # Prova prima l'autenticazione admin dal sistema unificato
    from unified_login import get_current_admin
    user = get_current_admin(request)
    
    # Se non funziona, prova l'autenticazione del training module
    if not user:
        user = await get_current_user(request)
    
    if not user:
        return RedirectResponse(url="/unified-login")
    
    # Verifica che sia admin
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accesso negato. Solo gli amministratori possono gestire i corsi.")
    
    try:
        course = training.get_course_by_id(course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Corso non trovato")
        
        quiz = training.get_course_quiz(course_id)
        if quiz:
            # Ottieni il quiz completo con le domande
            quiz = training.get_quiz_with_questions(quiz['id'])
        
        return templates.TemplateResponse("training_course_quiz.html", {
            "request": request,
            "user": user,
            "course": course,
            "quiz": quiz
        })
    except Exception as e:
        return templates.TemplateResponse("training_course_quiz.html", {
            "request": request,
            "user": user,
            "course": None,
            "quiz": None,
            "error_message": str(e)
        })

# ==================== API GESTIONE CORSI ====================

@training_router.post("/api/courses")
async def add_course_api(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    duration_minutes: int = Form(...),
    difficulty_level: str = Form(...),
    nis2_requirements: str = Form(None),
    content_url: str = Form(None)
):
    """API per aggiungere un nuovo corso - SOLO ADMIN"""
    # Prova prima l'autenticazione admin dal sistema unificato
    from unified_login import get_current_admin
    user = get_current_admin(request)
    
    # Se non funziona, prova l'autenticazione del training module
    if not user:
        user = await get_current_user(request)
    
    if not user:
        raise HTTPException(status_code=401, detail="Non autorizzato")
    
    # Verifica che sia admin
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accesso negato. Solo gli amministratori possono gestire i corsi.")
    
    try:
        # Parsing requisiti NIS2
        requirements_list = None
        if nis2_requirements:
            try:
                requirements_list = json.loads(nis2_requirements)
            except json.JSONDecodeError:
                requirements_list = [req.strip() for req in nis2_requirements.split('\n') if req.strip()]
        
        course_id = training.add_course(
            title=title,
            description=description,
            category=category,
            duration_minutes=duration_minutes,
            difficulty_level=difficulty_level,
            nis2_requirements=requirements_list,
            content_url=content_url
        )
        
        return {"success": True, "course_id": course_id, "message": "Corso creato con successo"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")

@training_router.get("/api/courses/{course_id}")
async def get_course_api(request: Request, course_id: int):
    """API per ottenere i dettagli di un corso specifico"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Non autorizzato")
    
    try:
        course = training.get_course_by_id(course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Corso non trovato")
        
        return {"success": True, "course": course}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")

@training_router.put("/api/courses/{course_id}")
async def update_course_api(
    request: Request,
    course_id: int,
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    duration_minutes: int = Form(...),
    difficulty_level: str = Form(...),
    nis2_requirements: str = Form(None),
    content_url: str = Form(None)
):
    """API per aggiornare un corso esistente"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Non autorizzato")
    
    try:
        # Parsing requisiti NIS2
        requirements_list = None
        if nis2_requirements:
            try:
                requirements_list = json.loads(nis2_requirements)
            except json.JSONDecodeError:
                requirements_list = [req.strip() for req in nis2_requirements.split('\n') if req.strip()]
        
        success = training.update_course(
            course_id=course_id,
            title=title,
            description=description,
            category=category,
            duration_minutes=duration_minutes,
            difficulty_level=difficulty_level,
            nis2_requirements=requirements_list,
            content_url=content_url
        )
        
        if success:
            return {"success": True, "message": "Corso aggiornato con successo"}
        else:
            raise HTTPException(status_code=404, detail="Corso non trovato")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")

@training_router.delete("/api/courses/{course_id}")
async def delete_course_api(request: Request, course_id: int):
    """API per eliminare un corso"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Non autorizzato")
    
    # Verifica che sia admin
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accesso negato. Solo gli amministratori possono gestire i corsi.")
    
    try:
        success = training.delete_course(course_id)
        if success:
            return {"success": True, "message": "Corso eliminato con successo"}
        else:
            raise HTTPException(status_code=404, detail="Corso non trovato")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")

# ==================== API GESTIONE CONTENUTI ====================

@training_router.post("/api/courses/{course_id}/content")
async def add_course_content_api(
    request: Request,
    course_id: int,
    title: str = Form(...),
    content_type: str = Form(...),
    content: str = Form(...),
    order_index: int = Form(...),
    duration_minutes: int = Form(None)
):
    """API per aggiungere contenuto a un corso - SOLO ADMIN"""
    user = await get_current_user(request)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accesso negato. Solo gli amministratori possono gestire i corsi.")
    
    try:
        content_id = training.add_course_content(
            course_id=course_id,
            title=title,
            content_type=content_type,
            content=content,
            order_index=order_index,
            duration_minutes=duration_minutes
        )
        return {"success": True, "content_id": content_id, "message": "Contenuto aggiunto con successo"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")

@training_router.put("/api/content/{content_id}")
async def update_course_content_api(
    request: Request,
    content_id: int,
    title: str = Form(...),
    content: str = Form(...),
    order_index: int = Form(...),
    duration_minutes: int = Form(None)
):
    """API per aggiornare contenuto di un corso - SOLO ADMIN"""
    user = await get_current_user(request)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accesso negato. Solo gli amministratori possono gestire i corsi.")
    
    try:
        success = training.update_course_content(
            content_id=content_id,
            title=title,
            content=content,
            order_index=order_index,
            duration_minutes=duration_minutes
        )
        if success:
            return {"success": True, "message": "Contenuto aggiornato con successo"}
        else:
            raise HTTPException(status_code=404, detail="Contenuto non trovato")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")

@training_router.delete("/api/content/{content_id}")
async def delete_course_content_api(request: Request, content_id: int):
    """API per eliminare contenuto di un corso - SOLO ADMIN"""
    user = await get_current_user(request)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accesso negato. Solo gli amministratori possono gestire i corsi.")
    
    try:
        success = training.delete_course_content(content_id)
        if success:
            return {"success": True, "message": "Contenuto eliminato con successo"}
        else:
            raise HTTPException(status_code=404, detail="Contenuto non trovato")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")

# ==================== API GESTIONE QUIZ ====================

@training_router.post("/api/courses/{course_id}/quiz")
async def create_quiz_api(
    request: Request,
    course_id: int,
    title: str = Form(...),
    description: str = Form(...),
    passing_score: int = Form(70),
    time_limit_minutes: int = Form(30)
):
    """API per creare un quiz per un corso - SOLO ADMIN"""
    user = await get_current_user(request)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accesso negato. Solo gli amministratori possono gestire i corsi.")
    
    try:
        quiz_id = training.create_quiz_for_course(
            course_id=course_id,
            title=title,
            description=description,
            passing_score=passing_score,
            time_limit_minutes=time_limit_minutes
        )
        return {"success": True, "quiz_id": quiz_id, "message": "Quiz creato con successo"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")

@training_router.post("/api/quiz/{quiz_id}/questions")
async def add_quiz_question_api(
    request: Request,
    quiz_id: int,
    question_text: str = Form(...),
    question_type: str = Form(...),
    options: str = Form(None),  # JSON string per multiple choice
    correct_answer: str = Form(...),
    points: int = Form(1),
    explanation: str = Form(None)
):
    """API per aggiungere una domanda a un quiz - SOLO ADMIN"""
    user = await get_current_user(request)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accesso negato. Solo gli amministratori possono gestire i corsi.")
    
    try:
        # Parsing delle opzioni se fornite
        options_list = None
        if options:
            try:
                options_list = json.loads(options)
            except json.JSONDecodeError:
                options_list = [opt.strip() for opt in options.split('\n') if opt.strip()]
        
        question_id = training.add_quiz_question(
            quiz_id=quiz_id,
            question_text=question_text,
            question_type=question_type,
            options=options_list,
            correct_answer=correct_answer,
            points=points,
            explanation=explanation
        )
        return {"success": True, "question_id": question_id, "message": "Domanda aggiunta con successo"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")

@training_router.put("/api/quiz/questions/{question_id}")
async def update_quiz_question_api(
    request: Request,
    question_id: int,
    question_text: str = Form(...),
    question_type: str = Form(...),
    options: str = Form(None),
    correct_answer: str = Form(...),
    points: int = Form(1),
    explanation: str = Form(None)
):
    """API per aggiornare una domanda di quiz - SOLO ADMIN"""
    user = await get_current_user(request)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accesso negato. Solo gli amministratori possono gestire i corsi.")
    
    try:
        # Parsing delle opzioni se fornite
        options_list = None
        if options:
            try:
                options_list = json.loads(options)
            except json.JSONDecodeError:
                options_list = [opt.strip() for opt in options.split('\n') if opt.strip()]
        
        success = training.update_quiz_question(
            question_id=question_id,
            question_text=question_text,
            question_type=question_type,
            options=options_list,
            correct_answer=correct_answer,
            points=points,
            explanation=explanation
        )
        if success:
            return {"success": True, "message": "Domanda aggiornata con successo"}
        else:
            raise HTTPException(status_code=404, detail="Domanda non trovata")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")

@training_router.delete("/api/quiz/questions/{question_id}")
async def delete_quiz_question_api(request: Request, question_id: int):
    """API per eliminare una domanda di quiz - SOLO ADMIN"""
    user = await get_current_user(request)
    if not user or user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Accesso negato. Solo gli amministratori possono gestire i corsi.")
    
    try:
        success = training.delete_quiz_question(question_id)
        if success:
            return {"success": True, "message": "Domanda eliminata con successo"}
        else:
            raise HTTPException(status_code=404, detail="Domanda non trovata")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore interno: {str(e)}")

# ==================== UTILITY ENDPOINTS ====================

@training_router.get("/api/health")
async def training_health_check():
    """Health check per il modulo training"""
    try:
        # Test semplice del database
        stats = training.get_training_stats(1)
        return {"status": "healthy", "module": "training", "timestamp": "2025-01-16T12:00:00"}
    except Exception as e:
        return {"status": "unhealthy", "module": "training", "error": str(e)}
