#!/usr/bin/env python3
"""
Script per aggiungere dipendenti per l'azienda ID 2
"""
import sqlite3
from datetime import datetime

def add_employees_company2():
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    print("👥 Aggiunta dipendenti per l'azienda ID 2...")
    
    # Dipendenti per l'azienda ID 2
    employees = [
        ("Marco Neri", "marco.neri@network.it", "Manager", "IT", "2024-01-15"),
        ("Sara Rossi", "sara.rossi@network.it", "Analyst", "Compliance", "2024-02-01"),
        ("Giuseppe Bianchi", "giuseppe.bianchi@network.it", "Developer", "IT", "2024-03-10"),
        ("Laura Verdi", "laura.verdi@network.it", "Consultant", "Security", "2024-04-05")
    ]
    
    for name, email, role, department, hire_date in employees:
        cursor.execute("""
            INSERT INTO training_employees (name, email, role, department, hire_date, company_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, email, role, department, hire_date, 2))
    
    conn.commit()
    print(f"✅ Aggiunti {len(employees)} dipendenti per l'azienda ID 2")
    
    # Mostra i dipendenti dell'azienda 2
    cursor.execute("SELECT id, name, email, role FROM training_employees WHERE company_id = 2")
    employees_company2 = cursor.fetchall()
    
    print("\n📋 Dipendenti azienda ID 2:")
    for emp in employees_company2:
        print(f"  - ID: {emp[0]}, Nome: {emp[1]}, Email: {emp[2]}, Ruolo: {emp[3]}")
    
    conn.close()

if __name__ == "__main__":
    add_employees_company2()
