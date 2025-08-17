#!/usr/bin/env python3
"""
Script per aggiungere iscrizioni di test al database
"""
import sqlite3
from datetime import datetime

def add_test_enrollments():
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    print("📚 Aggiunta iscrizioni di test...")
    
    # Ottieni dipendenti della company_id = 2
    cursor.execute("SELECT id FROM training_employees WHERE company_id = 2")
    employees = cursor.fetchall()
    
    # Ottieni corsi disponibili
    cursor.execute("SELECT id FROM training_courses WHERE is_active = 1")
    courses = cursor.fetchall()
    
    if not employees:
        print("❌ Nessun dipendente trovato per company_id = 2")
        return
    
    if not courses:
        print("❌ Nessun corso trovato")
        return
    
    print(f"👥 Dipendenti trovati: {len(employees)}")
    print(f"📖 Corsi trovati: {len(courses)}")
    
    # Aggiungi iscrizioni di test
    test_enrollments = [
        (employees[0][0], courses[0][0], 'ENROLLED'),  # Primo dipendente, primo corso
        (employees[0][0], courses[1][0], 'IN_PROGRESS'),  # Primo dipendente, secondo corso
        (employees[1][0], courses[0][0], 'COMPLETED'),  # Secondo dipendente, primo corso
        (employees[2][0], courses[2][0], 'ENROLLED'),  # Terzo dipendente, terzo corso
    ]
    
    for employee_id, course_id, status in test_enrollments:
        try:
            cursor.execute("""
                INSERT INTO training_enrollments (employee_id, course_id, status, enrollment_date)
                VALUES (?, ?, ?, ?)
            """, (employee_id, course_id, status, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            print(f"✅ Iscrizione aggiunta: Dipendente {employee_id} -> Corso {course_id} ({status})")
        except sqlite3.IntegrityError as e:
            print(f"⚠️ Iscrizione già esistente: Dipendente {employee_id} -> Corso {course_id}")
    
    conn.commit()
    conn.close()
    print("\n✅ Iscrizioni di test aggiunte con successo!")

if __name__ == "__main__":
    add_test_enrollments()
