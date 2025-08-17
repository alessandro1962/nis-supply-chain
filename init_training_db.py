#!/usr/bin/env python3
"""
Script per inizializzare e popolare il database del Training Module
"""

import sqlite3
import json
from datetime import datetime, timedelta
import os

def init_training_database():
    """Inizializza il database del training module"""
    
    db_path = 'nis2_supply_chain.db'
    
    print("🚀 Inizializzazione Database Training Module...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # ===== CREAZIONE TABELLE =====
    
    # Tabella dipendenti training
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS training_employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            role TEXT NOT NULL,
            department TEXT,
            hire_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id)
        )
    ''')
    
    # Tabella corsi
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS training_courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            duration_minutes INTEGER NOT NULL,
            difficulty_level TEXT NOT NULL,
            nis2_requirements TEXT,
            content_url TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabella iscrizioni
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS training_enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completion_date TIMESTAMP,
            status TEXT DEFAULT 'ENROLLED',
            score INTEGER,
            FOREIGN KEY (employee_id) REFERENCES training_employees (id),
            FOREIGN KEY (course_id) REFERENCES training_courses (id)
        )
    ''')
    
    # Tabella quiz
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS training_quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            passing_score INTEGER DEFAULT 70,
            time_limit_minutes INTEGER DEFAULT 30,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES training_courses (id)
        )
    ''')
    
    # Tabella domande quiz
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS training_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            quiz_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            question_type TEXT NOT NULL,
            options TEXT,
            correct_answer TEXT NOT NULL,
            points INTEGER DEFAULT 1,
            FOREIGN KEY (quiz_id) REFERENCES training_quizzes (id)
        )
    ''')
    
    # Tabella tentativi quiz
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS training_quiz_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            enrollment_id INTEGER NOT NULL,
            quiz_id INTEGER NOT NULL,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            score INTEGER,
            passed BOOLEAN,
            answers TEXT,
            FOREIGN KEY (enrollment_id) REFERENCES training_enrollments (id),
            FOREIGN KEY (quiz_id) REFERENCES training_quizzes (id)
        )
    ''')
    
    # Tabella certificazioni
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS training_certifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            certification_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expiry_date TEXT NOT NULL,
            certificate_number TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'ACTIVE',
            FOREIGN KEY (employee_id) REFERENCES training_employees (id),
            FOREIGN KEY (course_id) REFERENCES training_courses (id)
        )
    ''')
    
    # Tabella notifiche
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS training_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            type TEXT NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            is_read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employee_id) REFERENCES training_employees (id)
        )
    ''')
    
    print("✅ Tabelle create con successo!")
    
    # ===== POPOLAMENTO DATI DI ESEMPIO =====
    
    # Controlla se ci sono già corsi
    cursor.execute("SELECT COUNT(*) FROM training_courses")
    if cursor.fetchone()[0] == 0:
        print("📚 Inserimento corsi di esempio...")
        
        # Corsi di esempio
        sample_courses = [
            ("Fondamenti NIS2", "Corso base sui requisiti della direttiva NIS2 e le sue implicazioni per le aziende", "Compliance", 120, "Beginner", 
             json.dumps(["AC-001", "AC-002", "BC-001"]), None),
            ("Gestione del Rischio", "Metodologie di risk assessment e mitigazione dei rischi informatici", "Risk Management", 90, "Intermediate",
             json.dumps(["RM-001", "RM-002", "RM-003"]), None),
            ("Business Continuity", "Pianificazione e implementazione della continuità aziendale", "Business Continuity", 150, "Advanced",
             json.dumps(["BC-001", "BC-002", "BC-003", "BC-004", "BC-005"]), None),
            ("Cybersecurity Avanzata", "Misure di sicurezza informatica avanzate e best practices", "Cybersecurity", 180, "Advanced",
             json.dumps(["CS-001", "CS-002", "CS-003", "CS-004"]), None),
            ("Supply Chain Security", "Sicurezza della catena di approvvigionamento e gestione fornitori", "Supply Chain", 120, "Intermediate",
             json.dumps(["SC-001", "SC-002", "SC-003"]), None),
            ("Data Protection", "Protezione dei dati personali e conformità GDPR", "Data Protection", 100, "Intermediate",
             json.dumps(["DP-001", "DP-002", "DP-003"]), None),
            ("Incident Response", "Gestione degli incidenti di sicurezza e procedure di risposta", "Incident Response", 140, "Advanced",
             json.dumps(["IR-001", "IR-002", "IR-003", "IR-004"]), None),
            ("Security Awareness", "Consapevolezza della sicurezza per tutti i dipendenti", "Awareness", 60, "Beginner",
             json.dumps(["SA-001", "SA-002"]), None)
        ]
        
        cursor.executemany("""
            INSERT INTO training_courses (title, description, category, duration_minutes, difficulty_level, nis2_requirements, content_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, sample_courses)
        
        print(f"✅ Inseriti {len(sample_courses)} corsi di esempio")
        
        # Inserisci quiz di esempio per alcuni corsi
        print("📝 Creazione quiz di esempio...")
        
        # Quiz per Fondamenti NIS2
        cursor.execute("SELECT id FROM training_courses WHERE title = 'Fondamenti NIS2'")
        course_id = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO training_quizzes (course_id, title, description, passing_score, time_limit_minutes)
            VALUES (?, 'Quiz Fondamenti NIS2', 'Test di valutazione sui fondamenti della direttiva NIS2', 70, 30)
        """, (course_id,))
        
        quiz_id = cursor.lastrowid
        
        # Domande per il quiz
        sample_questions = [
            (quiz_id, "Cosa significa NIS2?", "MULTIPLE_CHOICE", 
             json.dumps(["Network and Information Security 2", "National Information System 2", "Network Infrastructure Security 2", "Nessuna delle precedenti"]),
             "Network and Information Security 2", 2),
            (quiz_id, "Quale è l'obiettivo principale della direttiva NIS2?", "MULTIPLE_CHOICE",
             json.dumps(["Aumentare i costi IT", "Migliorare la sicurezza delle reti e dei sistemi informativi", "Ridurre la produttività", "Limitare l'innovazione"]),
             "Migliorare la sicurezza delle reti e dei sistemi informativi", 3),
            (quiz_id, "La direttiva NIS2 si applica solo alle grandi aziende", "TRUE_FALSE",
             None, "FALSE", 1),
            (quiz_id, "Quale delle seguenti NON è una misura di sicurezza richiesta da NIS2?", "MULTIPLE_CHOICE",
             json.dumps(["Access Control", "Incident Response", "Business Continuity", "Marketing Automation"]),
             "Marketing Automation", 2)
        ]
        
        cursor.executemany("""
            INSERT INTO training_questions (quiz_id, question_text, question_type, options, correct_answer, points)
            VALUES (?, ?, ?, ?, ?, ?)
        """, sample_questions)
        
        print("✅ Quiz e domande create con successo")
        
    else:
        print("ℹ️ I corsi sono già presenti nel database")
    
    # Controlla se ci sono dipendenti di esempio
    cursor.execute("SELECT COUNT(*) FROM training_employees")
    if cursor.fetchone()[0] == 0:
        print("👥 Inserimento dipendenti di esempio...")
        
        # Dipendenti di esempio per company_id = 1
        sample_employees = [
            (1, "Mario Rossi", "mario.rossi@azienda.com", "Security Manager", "IT", "2023-01-15"),
            (1, "Laura Bianchi", "laura.bianchi@azienda.com", "Compliance Officer", "Legal", "2023-03-20"),
            (1, "Giuseppe Verdi", "giuseppe.verdi@azienda.com", "IT Administrator", "IT", "2022-11-10"),
            (1, "Anna Neri", "anna.neri@azienda.com", "Risk Analyst", "Risk Management", "2023-06-05"),
            (1, "Marco Gialli", "marco.gialli@azienda.com", "System Engineer", "IT", "2022-09-12")
        ]
        
        cursor.executemany("""
            INSERT INTO training_employees (company_id, name, email, role, department, hire_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, sample_employees)
        
        print(f"✅ Inseriti {len(sample_employees)} dipendenti di esempio")
        
        # Crea alcune iscrizioni di esempio
        print("📚 Creazione iscrizioni di esempio...")
        
        # Iscrizioni di esempio
        sample_enrollments = [
            (1, 1, "2024-01-15 10:00:00", "2024-01-20 15:30:00", "COMPLETED", 85),
            (1, 2, "2024-02-01 09:00:00", None, "IN_PROGRESS", None),
            (2, 1, "2024-01-10 14:00:00", "2024-01-18 11:20:00", "COMPLETED", 92),
            (3, 3, "2024-03-05 16:00:00", None, "ENROLLED", None),
            (4, 2, "2024-02-15 13:00:00", None, "IN_PROGRESS", None)
        ]
        
        cursor.executemany("""
            INSERT INTO training_enrollments (employee_id, course_id, enrollment_date, completion_date, status, score)
            VALUES (?, ?, ?, ?, ?, ?)
        """, sample_enrollments)
        
        print("✅ Iscrizioni di esempio create")
        
    else:
        print("ℹ️ I dipendenti sono già presenti nel database")
    
    conn.commit()
    conn.close()
    
    print("🎉 Database Training Module inizializzato con successo!")
    
    # Test delle funzionalità
    print("\n🧪 Test delle funzionalità...")
    
    # Importa il modulo training per testare
    from training_module import TrainingModule
    
    training = TrainingModule()
    
    # Test statistiche
    stats = training.get_training_stats(1)
    print(f"📊 Statistiche Training: {stats}")
    
    # Test corsi
    courses = training.get_courses()
    print(f"📚 Corsi disponibili: {len(courses)}")
    
    # Test dipendenti
    employees = training.get_employees(1)
    print(f"👥 Dipendenti: {len(employees)}")
    
    print("\n✅ Tutto funziona correttamente!")

if __name__ == "__main__":
    init_training_database()
