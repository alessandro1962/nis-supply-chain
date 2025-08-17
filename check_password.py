#!/usr/bin/env python3
"""
Script per controllare la password del dipendente ale@nwk.it
"""
import sqlite3

def check_password():
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    print("🔍 Controllo password dipendente ale@nwk.it...")
    
    cursor.execute("SELECT id, name, email, password FROM training_employees WHERE email = 'ale@nwk.it'")
    row = cursor.fetchone()
    
    if row:
        print(f"✅ Dipendente trovato:")
        print(f"   ID: {row[0]}")
        print(f"   Nome: {row[1]}")
        print(f"   Email: {row[2]}")
        print(f"   Password: '{row[3]}'")
        
        # Test con password123
        if row[3] == 'password123':
            print("✅ Password corretta: password123")
        else:
            print("❌ Password NON è 'password123'")
            print("   La password nel database è diversa!")
    else:
        print("❌ Dipendente non trovato")
    
    conn.close()

if __name__ == "__main__":
    check_password()
