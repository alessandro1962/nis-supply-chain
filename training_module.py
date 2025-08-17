import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

class TrainingModule:
    def __init__(self, db_path: str = 'nis2_supply_chain.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inizializza le tabelle del database per il training"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabella dipendenti/utenti training
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL,
                department TEXT,
                hire_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies (id)
            )
        """)
        
        # Tabella corsi di formazione
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT NOT NULL,
                duration_minutes INTEGER DEFAULT 60,
                difficulty_level TEXT DEFAULT 'BEGINNER',
                nis2_requirements TEXT, -- JSON array dei requisiti NIS2 coperti
                content_url TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabella iscrizioni ai corsi
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completion_date TIMESTAMP,
                status TEXT DEFAULT 'ENROLLED', -- ENROLLED, IN_PROGRESS, COMPLETED, EXPIRED
                score INTEGER, -- Punteggio finale (0-100)
                certificate_url TEXT,
                progress_data TEXT, -- JSON con dati di progresso
                FOREIGN KEY (employee_id) REFERENCES training_employees (id),
                FOREIGN KEY (course_id) REFERENCES training_courses (id)
            )
        """)
        
        # Tabella quiz e test
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                passing_score INTEGER DEFAULT 70,
                time_limit_minutes INTEGER DEFAULT 30,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (course_id) REFERENCES training_courses (id)
            )
        """)
        
        # Tabella domande quiz
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_id INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                question_type TEXT DEFAULT 'MULTIPLE_CHOICE', -- MULTIPLE_CHOICE, TRUE_FALSE, TEXT
                options TEXT, -- JSON array per multiple choice
                correct_answer TEXT,
                points INTEGER DEFAULT 1,
                explanation TEXT, -- Spiegazione della risposta corretta
                FOREIGN KEY (quiz_id) REFERENCES training_quizzes (id)
            )
        """)
        
        # Tabella risposte quiz
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_quiz_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                enrollment_id INTEGER NOT NULL,
                quiz_id INTEGER NOT NULL,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                score INTEGER,
                passed BOOLEAN,
                answers TEXT, -- JSON con le risposte date
                FOREIGN KEY (enrollment_id) REFERENCES training_enrollments (id),
                FOREIGN KEY (quiz_id) REFERENCES training_quizzes (id)
            )
        """)
        
        # Tabella certificazioni
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_certifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                certification_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expiry_date TIMESTAMP,
                certificate_number TEXT UNIQUE,
                status TEXT DEFAULT 'ACTIVE', -- ACTIVE, EXPIRED, REVOKED
                certificate_url TEXT,
                FOREIGN KEY (employee_id) REFERENCES training_employees (id),
                FOREIGN KEY (course_id) REFERENCES training_courses (id)
            )
        """)
        
        # Tabella notifiche training
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                type TEXT NOT NULL, -- COURSE_DUE, CERTIFICATION_EXPIRING, REMINDER
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (employee_id) REFERENCES training_employees (id)
            )
        """)
        
        # Tabella contenuti dei corsi
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_course_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content_type TEXT NOT NULL, -- MODULE, LESSON, VIDEO, DOCUMENT
                content TEXT NOT NULL,
                order_index INTEGER NOT NULL,
                duration_minutes INTEGER,
                FOREIGN KEY (course_id) REFERENCES training_courses (id)
            )
        """)
        
        conn.commit()
        conn.close()
        
        # Popola con dati di esempio se le tabelle sono vuote
        self.populate_sample_data()
    
    def populate_sample_data(self):
        """Popola il database con dati di esempio per il training"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Controlla se ci sono già corsi
        cursor.execute("SELECT COUNT(*) FROM training_courses")
        if cursor.fetchone()[0] == 0:
            # Inserisci corsi di esempio
            sample_courses = [
                ("Fondamenti NIS2", "Corso base sui requisiti della direttiva NIS2", "COMPLIANCE", 120, "BEGINNER", 
                 json.dumps(["AC-001", "AC-002", "BC-001"]), None),
                ("Gestione del Rischio", "Metodologie di risk assessment e mitigazione", "RISK_MANAGEMENT", 90, "INTERMEDIATE",
                 json.dumps(["RM-001", "RM-002", "RM-003"]), None),
                ("Business Continuity", "Pianificazione e implementazione della continuità aziendale", "BUSINESS_CONTINUITY", 150, "ADVANCED",
                 json.dumps(["BC-001", "BC-002", "BC-003", "BC-004", "BC-005"]), None),
                ("Cybersecurity Avanzata", "Misure di sicurezza informatica avanzate", "CYBERSECURITY", 180, "ADVANCED",
                 json.dumps(["CS-001", "CS-002", "CS-003", "CS-004"]), None),
                ("Supply Chain Security", "Sicurezza della catena di approvvigionamento", "SUPPLY_CHAIN", 120, "INTERMEDIATE",
                 json.dumps(["SC-001", "SC-002", "SC-003"]), None)
            ]
            
            cursor.executemany("""
                INSERT INTO training_courses (title, description, category, duration_minutes, difficulty_level, nis2_requirements, content_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, sample_courses)
            
            # Inserisci quiz di esempio per il primo corso
            cursor.execute("SELECT id FROM training_courses WHERE title = 'Fondamenti NIS2'")
            course_id = cursor.fetchone()[0]
            
            cursor.execute("""
                INSERT INTO training_quizzes (course_id, title, description, passing_score, time_limit_minutes)
                VALUES (?, 'Quiz Fondamenti NIS2', 'Test di valutazione sui fondamenti NIS2', 70, 30)
            """, (course_id,))
            
            quiz_id = cursor.lastrowid
            
            # Inserisci domande di esempio
            sample_questions = [
                (quiz_id, "Cosa significa NIS2?", "MULTIPLE_CHOICE", 
                 json.dumps(["Network and Information Security 2", "National Information System 2", "Network Infrastructure Security 2", "Nessuna delle precedenti"]),
                 "Network and Information Security 2", 2),
                (quiz_id, "Quale è l'obiettivo principale della direttiva NIS2?", "MULTIPLE_CHOICE",
                 json.dumps(["Aumentare i costi IT", "Migliorare la sicurezza delle reti e dei sistemi informativi", "Ridurre la produttività", "Limitare l'innovazione"]),
                 "Migliorare la sicurezza delle reti e dei sistemi informativi", 3),
                (quiz_id, "La direttiva NIS2 si applica solo alle grandi aziende", "TRUE_FALSE",
                 None, "FALSE", 1)
            ]
            
            cursor.executemany("""
                INSERT INTO training_questions (quiz_id, question_text, question_type, options, correct_answer, points)
                VALUES (?, ?, ?, ?, ?, ?)
            """, sample_questions)
        
        conn.commit()
        conn.close()
    
    # METODI PER GESTIONE DIPENDENTI
    def add_employee(self, company_id: int, name: str, email: str, role: str, department: str = None, hire_date: str = None) -> int:
        """Aggiunge un nuovo dipendente al sistema di training"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO training_employees (company_id, name, email, role, department, hire_date)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (company_id, name, email, role, department, hire_date))
            
            employee_id = cursor.lastrowid
            conn.commit()
            return employee_id
        except sqlite3.IntegrityError:
            raise ValueError("Email già esistente nel sistema")
        finally:
            conn.close()
    
    def add_employee_with_password(self, company_id: int, name: str, email: str, password: str, role: str, department: str = None, hire_date: str = None) -> int:
        """Aggiunge un nuovo dipendente con password al sistema di training"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO training_employees (company_id, name, email, password, role, department, hire_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (company_id, name, email, password, role, department, hire_date))
            
            employee_id = cursor.lastrowid
            conn.commit()
            return employee_id
        except sqlite3.IntegrityError:
            raise ValueError("Email già esistente nel sistema")
        finally:
            conn.close()
    
    def update_employee_with_password(self, employee_id: int, company_id: int, name: str, email: str, password: str = None, role: str = None, department: str = None, hire_date: str = None) -> bool:
        """Aggiorna un dipendente esistente, opzionalmente con nuova password"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Verifica che il dipendente appartenga all'azienda
            cursor.execute("SELECT id FROM training_employees WHERE id = ? AND company_id = ?", (employee_id, company_id))
            if not cursor.fetchone():
                raise ValueError("Dipendente non trovato o non autorizzato")
            
            # Costruisci la query di aggiornamento
            update_fields = []
            params = []
            
            if name:
                update_fields.append("name = ?")
                params.append(name)
            if email:
                update_fields.append("email = ?")
                params.append(email)
            if password:
                update_fields.append("password = ?")
                params.append(password)
            if role:
                update_fields.append("role = ?")
                params.append(role)
            if department is not None:
                update_fields.append("department = ?")
                params.append(department)
            if hire_date is not None:
                update_fields.append("hire_date = ?")
                params.append(hire_date)
            
            if not update_fields:
                raise ValueError("Nessun campo da aggiornare")
            
            params.append(employee_id)
            params.append(company_id)
            
            query = f"UPDATE training_employees SET {', '.join(update_fields)} WHERE id = ? AND company_id = ?"
            cursor.execute(query, params)
            
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            raise ValueError("Email già esistente nel sistema")
        finally:
            conn.close()
    
    def get_employees(self, company_id: int) -> List[Dict]:
        """Ottiene la lista dei dipendenti di un'azienda"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, email, role, department, hire_date, created_at
            FROM training_employees 
            WHERE company_id = ?
            ORDER BY name
        """, (company_id,))
        
        employees = []
        for row in cursor.fetchall():
            employees.append({
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'role': row[3],
                'department': row[4],
                'hire_date': row[5],
                'created_at': row[6]
            })
        
        conn.close()
        return employees
    
    def get_employee_by_id(self, employee_id: int, company_id: int) -> Optional[Dict]:
        """Ottiene i dati di un dipendente specifico"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, email, role, department, hire_date, created_at, password
            FROM training_employees 
            WHERE id = ? AND company_id = ?
        """, (employee_id, company_id))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        
        employee = {
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'role': row[3],
            'department': row[4],
            'hire_date': row[5],
            'created_at': row[6],
            'password': row[7] if row[7] else None
        }
        
        conn.close()
        return employee
    
    # METODI PER GESTIONE CORSI
    def get_courses(self, category: str = None) -> List[Dict]:
        """Ottiene la lista dei corsi disponibili con numero di iscritti"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if category:
            cursor.execute("""
                SELECT c.id, c.title, c.description, c.category, c.duration_minutes, c.difficulty_level, c.nis2_requirements,
                       COUNT(e.id) as enrolled_count
                FROM training_courses c
                LEFT JOIN training_enrollments e ON c.id = e.course_id AND e.status != 'EXPIRED'
                WHERE c.category = ? AND c.is_active = 1
                GROUP BY c.id
                ORDER BY c.title
            """, (category,))
        else:
            cursor.execute("""
                SELECT c.id, c.title, c.description, c.category, c.duration_minutes, c.difficulty_level, c.nis2_requirements,
                       COUNT(e.id) as enrolled_count
                FROM training_courses c
                LEFT JOIN training_enrollments e ON c.id = e.course_id AND e.status != 'EXPIRED'
                WHERE c.is_active = 1
                GROUP BY c.id
                ORDER BY c.category, c.title
            """)
        
        courses = []
        for row in cursor.fetchall():
            courses.append({
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'category': row[3],
                'duration_minutes': row[4],
                'difficulty_level': row[5],
                'nis2_requirements': json.loads(row[6]) if row[6] else [],
                'enrolled_students': row[7]
            })
        
        conn.close()
        return courses
    
    # METODI PER ISCRIZIONI
    def enroll_employee(self, employee_id: int, course_id: int) -> int:
        """Iscrive un dipendente a un corso"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Controlla se già iscritto
        cursor.execute("""
            SELECT id FROM training_enrollments 
            WHERE employee_id = ? AND course_id = ? AND status != 'EXPIRED'
        """, (employee_id, course_id))
        
        if cursor.fetchone():
            conn.close()
            raise ValueError("Dipendente già iscritto a questo corso")
        
        cursor.execute("""
            INSERT INTO training_enrollments (employee_id, course_id, status)
            VALUES (?, ?, 'ENROLLED')
        """, (employee_id, course_id))
        
        enrollment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return enrollment_id
    
    def get_employee_enrollments(self, employee_id: int) -> List[Dict]:
        """Ottiene le iscrizioni di un dipendente"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT e.id, e.enrollment_date, e.completion_date, e.status, e.score,
                   c.title, c.description, c.category, c.duration_minutes
            FROM training_enrollments e
            JOIN training_courses c ON e.course_id = c.id
            WHERE e.employee_id = ?
            ORDER BY e.enrollment_date DESC
        """, (employee_id,))
        
        enrollments = []
        for row in cursor.fetchall():
            enrollments.append({
                'enrollment_id': row[0],
                'enrollment_date': row[1],
                'completion_date': row[2],
                'status': row[3],
                'score': row[4],
                'course_title': row[5],
                'course_description': row[6],
                'course_category': row[7],
                'course_duration': row[8]
            })
        
        conn.close()
        return enrollments
    
    # METODI PER QUIZ
    def get_course_quiz(self, course_id: int) -> Optional[Dict]:
        """Ottiene il quiz di un corso"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, description, passing_score, time_limit_minutes
            FROM training_quizzes 
            WHERE course_id = ? AND is_active = 1
        """, (course_id,))
        
        quiz_row = cursor.fetchone()
        if not quiz_row:
            conn.close()
            return None
        
        quiz = {
            'id': quiz_row[0],
            'title': quiz_row[1],
            'description': quiz_row[2],
            'passing_score': quiz_row[3],
            'time_limit_minutes': quiz_row[4],
            'questions': []
        }
        
        # Ottieni le domande
        cursor.execute("""
            SELECT id, question_text, question_type, options, points
            FROM training_questions 
            WHERE quiz_id = ?
            ORDER BY id
        """, (quiz_row[0],))
        
        for question_row in cursor.fetchall():
            quiz['questions'].append({
                'id': question_row[0],
                'question_text': question_row[1],
                'question_type': question_row[2],
                'options': json.loads(question_row[3]) if question_row[3] else None,
                'points': question_row[4]
            })
        
        conn.close()
        return quiz
    
    def submit_quiz_attempt(self, enrollment_id: int, quiz_id: int, answers: Dict, score: int) -> int:
        """Sottomette un tentativo di quiz"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Ottieni il passing score
        cursor.execute("SELECT passing_score FROM training_quizzes WHERE id = ?", (quiz_id,))
        passing_score = cursor.fetchone()[0]
        
        passed = score >= passing_score
        
        cursor.execute("""
            INSERT INTO training_quiz_attempts (enrollment_id, quiz_id, end_time, score, passed, answers)
            VALUES (?, ?, CURRENT_TIMESTAMP, ?, ?, ?)
        """, (enrollment_id, quiz_id, score, passed, json.dumps(answers)))
        
        attempt_id = cursor.lastrowid
        
        # Aggiorna lo stato dell'iscrizione se il quiz è superato
        if passed:
            cursor.execute("""
                UPDATE training_enrollments 
                SET status = 'COMPLETED', completion_date = CURRENT_TIMESTAMP, score = ?
                WHERE id = ?
            """, (score, enrollment_id))
            
            # Crea certificazione
            cursor.execute("""
                SELECT employee_id, course_id FROM training_enrollments WHERE id = ?
            """, (enrollment_id,))
            employee_id, course_id = cursor.fetchone()
            
            # Calcola data di scadenza (1 anno)
            expiry_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d %H:%M:%S')
            certificate_number = f"CERT-{employee_id:04d}-{course_id:04d}-{datetime.now().strftime('%Y%m%d')}"
            
            cursor.execute("""
                INSERT INTO training_certifications (employee_id, course_id, expiry_date, certificate_number)
                VALUES (?, ?, ?, ?)
            """, (employee_id, course_id, expiry_date, certificate_number))
        
        conn.commit()
        conn.close()
        
        return attempt_id
    
    # METODI PER CERTIFICAZIONI
    def get_employee_certifications(self, employee_id: int) -> List[Dict]:
        """Ottiene le certificazioni di un dipendente"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.id, c.certification_date, c.expiry_date, c.certificate_number, c.status,
                   co.title, co.category
            FROM training_certifications c
            JOIN training_courses co ON c.course_id = co.id
            WHERE c.employee_id = ?
            ORDER BY c.certification_date DESC
        """, (employee_id,))
        
        certifications = []
        for row in cursor.fetchall():
            certifications.append({
                'id': row[0],
                'certification_date': row[1],
                'expiry_date': row[2],
                'certificate_number': row[3],
                'status': row[4],
                'course_title': row[5],
                'course_category': row[6]
            })
        
        conn.close()
        return certifications
    
    # METODI PER NOTIFICHE
    def create_notification(self, employee_id: int, type: str, title: str, message: str):
        """Crea una notifica per un dipendente"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO training_notifications (employee_id, type, title, message)
            VALUES (?, ?, ?, ?)
        """, (employee_id, type, title, message))
        
        conn.commit()
        conn.close()
    
    def get_employee_notifications(self, employee_id: int, unread_only: bool = False) -> List[Dict]:
        """Ottiene le notifiche di un dipendente"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if unread_only:
            cursor.execute("""
                SELECT id, type, title, message, created_at
                FROM training_notifications 
                WHERE employee_id = ? AND is_read = 0
                ORDER BY created_at DESC
            """, (employee_id,))
        else:
            cursor.execute("""
                SELECT id, type, title, message, is_read, created_at
                FROM training_notifications 
                WHERE employee_id = ?
                ORDER BY created_at DESC
                LIMIT 50
            """, (employee_id,))
        
        notifications = []
        for row in cursor.fetchall():
            notifications.append({
                'id': row[0],
                'type': row[1],
                'title': row[2],
                'message': row[3],
                'is_read': row[4] if len(row) > 4 else False,
                'created_at': row[5] if len(row) > 5 else row[4]
            })
        
        conn.close()
        return notifications
    
    # METODI PER REPORT E STATISTICHE
    def get_training_stats(self, company_id: int) -> Dict:
        """Ottiene statistiche del training per un'azienda"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Totale dipendenti
        cursor.execute("SELECT COUNT(*) FROM training_employees WHERE company_id = ?", (company_id,))
        total_employees = cursor.fetchone()[0]
        
        # Dipendenti con corsi completati
        cursor.execute("""
            SELECT COUNT(DISTINCT te.id) 
            FROM training_employees te
            JOIN training_enrollments e ON te.id = e.employee_id
            WHERE te.company_id = ? AND e.status = 'COMPLETED'
        """, (company_id,))
        employees_with_courses = cursor.fetchone()[0]
        
        # Corsi completati totali
        cursor.execute("""
            SELECT COUNT(*) 
            FROM training_employees te
            JOIN training_enrollments e ON te.id = e.employee_id
            WHERE te.company_id = ? AND e.status = 'COMPLETED'
        """, (company_id,))
        total_completed_courses = cursor.fetchone()[0]
        
        # Certificazioni attive
        cursor.execute("""
            SELECT COUNT(*) 
            FROM training_employees te
            JOIN training_certifications c ON te.id = c.employee_id
            WHERE te.company_id = ? AND c.status = 'ACTIVE' AND c.expiry_date > datetime('now')
        """, (company_id,))
        active_certifications = cursor.fetchone()[0]
        
        # Certificazioni in scadenza (30 giorni)
        cursor.execute("""
            SELECT COUNT(*) 
            FROM training_employees te
            JOIN training_certifications c ON te.id = c.employee_id
            WHERE te.company_id = ? AND c.status = 'ACTIVE' 
            AND c.expiry_date BETWEEN datetime('now') AND datetime('now', '+30 days')
        """, (company_id,))
        expiring_certifications = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_employees': total_employees,
            'employees_with_courses': employees_with_courses,
            'total_completed_courses': total_completed_courses,
            'active_certifications': active_certifications,
            'expiring_certifications': expiring_certifications,
            'completion_rate': (employees_with_courses / total_employees * 100) if total_employees > 0 else 0
        }
    
    def authenticate_employee(self, email: str, password: str) -> Optional[Dict]:
        """Autentica un dipendente"""
        print(f"🔍 Debug: Tentativo autenticazione - email: {email}, password: {password}")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Per ora, password semplice (in produzione usare hash)
            cursor.execute("""
                SELECT id, name, email, role, department, company_id
                FROM training_employees 
                WHERE email = ? AND password = ?
            """, (email, password))
            
            row = cursor.fetchone()
            print(f"🔍 Debug: Risultato query - {row}")
            
            if row:
                result = {
                    'id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'role': row[3],
                    'department': row[4],
                    'company_id': row[5]
                }
                print(f"✅ Debug: Autenticazione riuscita - {result}")
                return result
            else:
                print("❌ Debug: Autenticazione fallita - nessun risultato")
                return None
        except Exception as e:
            print(f"❌ Debug: Errore autenticazione - {e}")
            return None
        finally:
            conn.close()
    
    # METODI PER GESTIONE CORSI
    def add_course(self, title: str, description: str, category: str, duration_minutes: int, 
                   difficulty_level: str, nis2_requirements: List[str] = None, content_url: str = None) -> int:
        """Aggiunge un nuovo corso di formazione"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO training_courses (title, description, category, duration_minutes, 
                                            difficulty_level, nis2_requirements, content_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (title, description, category, duration_minutes, difficulty_level, 
                  json.dumps(nis2_requirements) if nis2_requirements else None, content_url))
            
            course_id = cursor.lastrowid
            conn.commit()
            return course_id
        finally:
            conn.close()
    
    def update_course(self, course_id: int, title: str, description: str, category: str, 
                     duration_minutes: int, difficulty_level: str, nis2_requirements: List[str] = None, 
                     content_url: str = None) -> bool:
        """Aggiorna un corso esistente"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE training_courses 
                SET title = ?, description = ?, category = ?, duration_minutes = ?, 
                    difficulty_level = ?, nis2_requirements = ?, content_url = ?
                WHERE id = ?
            """, (title, description, category, duration_minutes, difficulty_level,
                  json.dumps(nis2_requirements) if nis2_requirements else None, content_url, course_id))
            
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def delete_course(self, course_id: int) -> bool:
        """Elimina un corso (soft delete - imposta is_active = 0)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE training_courses 
                SET is_active = 0 
                WHERE id = ?
            """, (course_id,))
            
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def get_course_by_id(self, course_id: int) -> Optional[Dict]:
        """Ottiene i dettagli di un corso specifico"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, description, category, duration_minutes, difficulty_level, 
                   nis2_requirements, content_url, is_active, created_at
            FROM training_courses 
            WHERE id = ?
        """, (course_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        
        course = {
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'category': row[3],
            'duration_minutes': row[4],
            'difficulty_level': row[5],
            'nis2_requirements': json.loads(row[6]) if row[6] else [],
            'content_url': row[7],
            'is_active': bool(row[8]),
            'created_at': row[9]
        }
        
        conn.close()
        return course
    
    def get_course_stats(self, course_id: int) -> Dict:
        """Ottiene le statistiche di un corso specifico"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Totale iscritti
        cursor.execute("""
            SELECT COUNT(*) FROM training_enrollments 
            WHERE course_id = ? AND status != 'EXPIRED'
        """, (course_id,))
        total_enrolled = cursor.fetchone()[0]
        
        # Completati
        cursor.execute("""
            SELECT COUNT(*) FROM training_enrollments 
            WHERE course_id = ? AND status = 'COMPLETED'
        """, (course_id,))
        completed = cursor.fetchone()[0]
        
        # In corso
        cursor.execute("""
            SELECT COUNT(*) FROM training_enrollments 
            WHERE course_id = ? AND status = 'IN_PROGRESS'
        """, (course_id,))
        in_progress = cursor.fetchone()[0]
        
        # Punteggio medio
        cursor.execute("""
            SELECT AVG(score) FROM training_enrollments 
            WHERE course_id = ? AND status = 'COMPLETED' AND score IS NOT NULL
        """, (course_id,))
        avg_score = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_enrolled': total_enrolled,
            'completed': completed,
            'in_progress': in_progress,
            'avg_score': round(avg_score, 1),
            'completion_rate': (completed / total_enrolled * 100) if total_enrolled > 0 else 0
        }

    # ==================== GESTIONE CONTENUTI CORSI ====================
    
    def add_course_content(self, course_id: int, title: str, content_type: str, content: str, 
                          order_index: int, duration_minutes: int = None) -> int:
        """Aggiunge contenuto a un corso (moduli, lezioni, etc.)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO training_course_content (course_id, title, content_type, content, 
                                                   order_index, duration_minutes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (course_id, title, content_type, content, order_index, duration_minutes))
            
            content_id = cursor.lastrowid
            conn.commit()
            return content_id
        finally:
            conn.close()
    
    def get_course_content(self, course_id: int) -> List[Dict]:
        """Ottiene tutti i contenuti di un corso ordinati per indice"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, content_type, content, order_index, duration_minutes
            FROM training_course_content 
            WHERE course_id = ?
            ORDER BY order_index
        """, (course_id,))
        
        content = []
        for row in cursor.fetchall():
            content.append({
                'id': row[0],
                'title': row[1],
                'content_type': row[2],
                'content': row[3],
                'order_index': row[4],
                'duration_minutes': row[5]
            })
        
        conn.close()
        return content
    
    def update_course_content(self, content_id: int, title: str, content: str, 
                            order_index: int, duration_minutes: int = None) -> bool:
        """Aggiorna contenuto di un corso"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE training_course_content 
                SET title = ?, content = ?, order_index = ?, duration_minutes = ?
                WHERE id = ?
            """, (title, content, order_index, duration_minutes, content_id))
            
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def delete_course_content(self, content_id: int) -> bool:
        """Elimina contenuto di un corso"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM training_course_content WHERE id = ?", (content_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    # ==================== GESTIONE QUIZ AVANZATA ====================
    
    def create_quiz_for_course(self, course_id: int, title: str, description: str, 
                              passing_score: int = 70, time_limit_minutes: int = 30) -> int:
        """Crea un quiz per un corso"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO training_quizzes (course_id, title, description, passing_score, time_limit_minutes)
                VALUES (?, ?, ?, ?, ?)
            """, (course_id, title, description, passing_score, time_limit_minutes))
            
            quiz_id = cursor.lastrowid
            conn.commit()
            return quiz_id
        finally:
            conn.close()
    
    def add_quiz_question(self, quiz_id: int, question_text: str, question_type: str, 
                         options: List[str] = None, correct_answer: str = None, 
                         points: int = 1, explanation: str = None) -> int:
        """Aggiunge una domanda a un quiz"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO training_questions (quiz_id, question_text, question_type, options, 
                                              correct_answer, points, explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (quiz_id, question_text, question_type, 
                  json.dumps(options) if options else None, 
                  correct_answer, points, explanation))
            
            question_id = cursor.lastrowid
            conn.commit()
            return question_id
        finally:
            conn.close()
    
    def get_quiz_with_questions(self, quiz_id: int) -> Optional[Dict]:
        """Ottiene un quiz completo con tutte le domande"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Ottieni il quiz
        cursor.execute("""
            SELECT id, course_id, title, description, passing_score, time_limit_minutes
            FROM training_quizzes 
            WHERE id = ? AND is_active = 1
        """, (quiz_id,))
        
        quiz_row = cursor.fetchone()
        if not quiz_row:
            conn.close()
            return None
        
        quiz = {
            'id': quiz_row[0],
            'course_id': quiz_row[1],
            'title': quiz_row[2],
            'description': quiz_row[3],
            'passing_score': quiz_row[4],
            'time_limit_minutes': quiz_row[5],
            'questions': []
        }
        
        # Ottieni le domande
        cursor.execute("""
            SELECT id, question_text, question_type, options, correct_answer, points, explanation
            FROM training_questions 
            WHERE quiz_id = ?
            ORDER BY id
        """, (quiz_id,))
        
        for question_row in cursor.fetchall():
            quiz['questions'].append({
                'id': question_row[0],
                'question_text': question_row[1],
                'question_type': question_row[2],
                'options': json.loads(question_row[3]) if question_row[3] else None,
                'correct_answer': question_row[4],
                'points': question_row[5],
                'explanation': question_row[6]
            })
        
        conn.close()
        return quiz
    
    def update_quiz_question(self, question_id: int, question_text: str, question_type: str,
                           options: List[str] = None, correct_answer: str = None,
                           points: int = 1, explanation: str = None) -> bool:
        """Aggiorna una domanda di quiz"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                UPDATE training_questions 
                SET question_text = ?, question_type = ?, options = ?, 
                    correct_answer = ?, points = ?, explanation = ?
                WHERE id = ?
            """, (question_text, question_type, 
                  json.dumps(options) if options else None,
                  correct_answer, points, explanation, question_id))
            
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def delete_quiz_question(self, question_id: int) -> bool:
        """Elimina una domanda di quiz"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM training_questions WHERE id = ?", (question_id,))
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    # ==================== TRACKING PROGRESSO ====================
    
    def update_enrollment_progress(self, enrollment_id: int, completed_content_ids: List[int], 
                                 current_content_id: int = None) -> bool:
        """Aggiorna il progresso di un'iscrizione"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Aggiorna lo stato a IN_PROGRESS se non è già COMPLETED
            cursor.execute("""
                UPDATE training_enrollments 
                SET status = 'IN_PROGRESS', 
                    progress_data = ?
                WHERE id = ? AND status != 'COMPLETED'
            """, (json.dumps({
                'completed_content_ids': completed_content_ids,
                'current_content_id': current_content_id,
                'last_updated': datetime.now().isoformat()
            }), enrollment_id))
            
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()
    
    def get_enrollment_progress(self, enrollment_id: int) -> Dict:
        """Ottiene il progresso di un'iscrizione"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT progress_data FROM training_enrollments WHERE id = ?
        """, (enrollment_id,))
        
        row = cursor.fetchone()
        if not row or not row[0]:
            conn.close()
            return {
                'completed_content_ids': [],
                'current_content_id': None,
                'progress_percentage': 0
            }
        
        progress_data = json.loads(row[0])
        conn.close()
        
        # Calcola percentuale di completamento
        if progress_data.get('completed_content_ids'):
            # Ottieni totale contenuti del corso
            cursor.execute("""
                SELECT COUNT(*) FROM training_course_content tc
                JOIN training_enrollments e ON tc.course_id = e.course_id
                WHERE e.id = ?
            """, (enrollment_id,))
            total_content = cursor.fetchone()[0] or 1
            progress_percentage = (len(progress_data['completed_content_ids']) / total_content) * 100
        else:
            progress_percentage = 0
        
        progress_data['progress_percentage'] = round(progress_percentage, 1)
        return progress_data

# Test del modulo
if __name__ == "__main__":
    training = TrainingModule()
    print("✅ Modulo di Training inizializzato con successo!")
    
    # Test statistiche
    stats = training.get_training_stats(1)
    print(f"📊 Statistiche Training: {stats}")
