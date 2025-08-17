#!/usr/bin/env python3
"""
Script per controllare la struttura della tabella admins
"""
import sqlite3

def check_admin_structure():
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    print("🔍 Controllo struttura tabella admins...")
    
    # Controlla le colonne della tabella admins
    cursor.execute("PRAGMA table_info(admins)")
    columns = cursor.fetchall()
    
    print("📋 Colonne della tabella admins:")
    for column in columns:
        print(f"   - {column[1]} ({column[2]})")
    
    # Controlla se ci sono dati nella tabella
    cursor.execute("SELECT COUNT(*) FROM admins")
    count = cursor.fetchone()[0]
    print(f"\n📊 Numero di admin nel database: {count}")
    
    if count > 0:
        print("\n👥 Tutti gli admin:")
        cursor.execute("SELECT * FROM admins")
        admins = cursor.fetchall()
        
        for admin in admins:
            print(f"   - {admin}")
    
    # Controlla anche la tabella companies per admin
    print("\n🔍 Controllo tabella companies per admin...")
    cursor.execute("SELECT id, name, email FROM companies WHERE email LIKE '%admin%' OR name LIKE '%admin%'")
    company_admins = cursor.fetchall()
    
    if company_admins:
        print("👥 Admin trovati nella tabella companies:")
        for admin in company_admins:
            print(f"   - ID: {admin[0]}, Nome: {admin[1]}, Email: {admin[2]}")
    else:
        print("❌ Nessun admin trovato nella tabella companies")
    
    conn.close()

if __name__ == "__main__":
    check_admin_structure()
