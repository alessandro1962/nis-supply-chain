#!/usr/bin/env python3
"""
Script per aggiungere iscrizioni per i dipendenti dell'azienda ID 2
"""
import sqlite3
from datetime import datetime

def add_enrollments_company2():
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    print("📚 Aggiunta iscrizioni per l'azienda ID 2...")
    
    # Ottieni i dipendenti dell'azienda 2
    cursor.execute("SELECT id FROM training_employees WHERE company_id = 2")
    employees = [row[0] for row in cursor.fetchall()]
    
    # Ottieni i corsi disponibili
    cursor.execute("SELECT id FROM training_courses WHERE is_active = 1")
    courses = [row[0] for row in cursor.fetchall()]
    
    print(f"👥 Dipendenti trovati: {employees}")
    print(f"📚 Corsi trovati: {courses}")
    
    # Crea alcune iscrizioni
    enrollments = [
        (employees[0], courses[0]),  # Marco Neri -> Fondamenti NIS2
        (employees[1], courses[1]),  # Sara Rossi -> Gestione del Rischio
        (employees[2], courses[2]),  # Giuseppe Bianchi -> Cybersecurity
        (employees[3], courses[0]),  # Laura Verdi -> Fondamenti NIS2
    ]
    
    for employee_id, course_id in enrollments:
        try:
            cursor.execute("""
                INSERT INTO training_enrollments (employee_id, course_id, enrollment_date, status)
                VALUES (?, ?, ?, ?)
            """, (employee_id, course_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'ENROLLED'))
            print(f"✅ Iscrizione: Dipendente {employee_id} -> Corso {course_id}")
        except Exception as e:
            print(f"❌ Errore iscrizione {employee_id} -> {course_id}: {e}")
    
    conn.commit()
    
    # Mostra le iscrizioni create
    cursor.execute("""
        SELECT e.id, te.name, c.title, e.enrollment_date
        FROM training_enrollments e
        JOIN training_employees te ON e.employee_id = te.id
        JOIN training_courses c ON e.course_id = c.id
        WHERE te.company_id = 2
        ORDER BY e.id DESC
        LIMIT 10
    """)
    
    enrollments_company2 = cursor.fetchall()
    print(f"\n📋 Iscrizioni azienda ID 2:")
    for enrollment in enrollments_company2:
        print(f"  - ID: {enrollment[0]}, Dipendente: {enrollment[1]}, Corso: {enrollment[2]}, Data: {enrollment[3]}")
    
    conn.close()

if __name__ == "__main__":
    add_enrollments_company2()
