#!/usr/bin/env python3
"""
Script per controllare le iscrizioni ai corsi nel database
"""
import sqlite3

def check_enrollments():
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    print("🔍 Controllo iscrizioni ai corsi...")
    
    # Controlla la tabella training_enrollments
    cursor.execute("SELECT * FROM training_enrollments")
    enrollments = cursor.fetchall()
    print(f"📊 Iscrizioni totali: {len(enrollments)}")
    
    if enrollments:
        print("\n📋 Dettagli iscrizioni:")
        for enrollment in enrollments:
            print(f"  - ID: {enrollment[0]}, Dipendente: {enrollment[1]}, Corso: {enrollment[2]}, Data: {enrollment[3]}")
    else:
        print("❌ Nessuna iscrizione trovata")
    
    # Controlla dipendenti
    cursor.execute("SELECT * FROM training_employees")
    employees = cursor.fetchall()
    print(f"\n👥 Dipendenti totali: {len(employees)}")
    
    # Controlla corsi
    cursor.execute("SELECT * FROM training_courses")
    courses = cursor.fetchall()
    print(f"📚 Corsi totali: {len(courses)}")
    
    conn.close()

if __name__ == "__main__":
    check_enrollments()
