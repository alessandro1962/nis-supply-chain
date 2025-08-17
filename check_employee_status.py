#!/usr/bin/env python3
"""
Script per controllare lo status del dipendente ale@nwk.it
"""
import sqlite3

def check_employee_status():
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    print("🔍 Controllo status dipendente ale@nwk.it...")
    
    # Controlla se ale@nwk.it è un dipendente
    cursor.execute("SELECT id, name, email, company_id FROM training_employees WHERE email = 'ale@nwk.it'")
    employee = cursor.fetchone()
    
    if employee:
        print(f"✅ ale@nwk.it è un dipendente:")
        print(f"   ID: {employee[0]}")
        print(f"   Nome: {employee[1]}")
        print(f"   Email: {employee[2]}")
        print(f"   Company ID: {employee[3]}")
        
        # Controlla le iscrizioni
        cursor.execute("""
            SELECT e.id, e.course_id, e.status, c.title 
            FROM training_enrollments e 
            JOIN training_courses c ON e.course_id = c.id 
            WHERE e.employee_id = ?
        """, (employee[0],))
        
        enrollments = cursor.fetchall()
        print(f"\n📚 Iscrizioni di ale@nwk.it:")
        for enrollment in enrollments:
            print(f"   ID: {enrollment[0]}, Corso: {enrollment[3]}, Status: {enrollment[2]}")
    else:
        print("❌ ale@nwk.it NON è un dipendente")
        print("   Questo spiega perché non può accedere ai corsi!")
        
        # Controlla se è un'azienda
        cursor.execute("SELECT id, name, email FROM companies WHERE email = 'ale@nwk.it'")
        company = cursor.fetchone()
        
        if company:
            print(f"\n🏢 ale@nwk.it è un'azienda:")
            print(f"   ID: {company[0]}")
            print(f"   Nome: {company[1]}")
            print(f"   Email: {company[2]}")
    
    conn.close()

if __name__ == "__main__":
    check_employee_status()
