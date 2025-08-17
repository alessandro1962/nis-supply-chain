#!/usr/bin/env python3
"""
Script per aggiungere password ai dipendenti esistenti
"""
import sqlite3

def add_employee_passwords():
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    print("🔐 Aggiunta password ai dipendenti...")
    
    # Controlla se esiste la colonna password
    cursor.execute("PRAGMA table_info(training_employees)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'password' not in columns:
        print("➕ Aggiungendo colonna password...")
        cursor.execute("ALTER TABLE training_employees ADD COLUMN password TEXT DEFAULT 'password123'")
        print("✅ Colonna password aggiunta!")
    
    # Aggiorna password per tutti i dipendenti
    cursor.execute("UPDATE training_employees SET password = 'password123' WHERE password IS NULL")
    
    # Mostra i dipendenti con le loro credenziali
    cursor.execute("SELECT id, name, email, password FROM training_employees")
    employees = cursor.fetchall()
    
    print(f"\n📋 Credenziali dipendenti:")
    for emp in employees:
        print(f"  - {emp[1]} ({emp[2]}) - Password: {emp[3]}")
    
    conn.commit()
    conn.close()
    print("\n✅ Password aggiunte con successo!")

if __name__ == "__main__":
    add_employee_passwords()
