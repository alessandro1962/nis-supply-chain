#!/usr/bin/env python3
"""
Script per controllare la password dell'admin
"""
import sqlite3

def check_admin_password():
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    print("🔍 Controllo password admin...")
    
    # Controlla nella tabella admins
    cursor.execute("SELECT id, username, email, password FROM admins WHERE username = 'admin' OR email = 'admin@example.com'")
    admin_row = cursor.fetchone()
    
    if admin_row:
        print(f"✅ Admin trovato nella tabella admins:")
        print(f"   ID: {admin_row[0]}")
        print(f"   Username: {admin_row[1]}")
        print(f"   Email: {admin_row[2]}")
        print(f"   Password: '{admin_row[3]}'")
    else:
        print("❌ Admin non trovato nella tabella admins")
    
    # Controlla anche nella tabella companies (per compatibilità)
    cursor.execute("SELECT id, name, email, password FROM companies WHERE email = 'admin@example.com' OR name LIKE '%admin%'")
    company_row = cursor.fetchone()
    
    if company_row:
        print(f"\n✅ Admin trovato nella tabella companies:")
        print(f"   ID: {company_row[0]}")
        print(f"   Nome: {company_row[1]}")
        print(f"   Email: {company_row[2]}")
        print(f"   Password: '{company_row[3]}'")
    else:
        print("\n❌ Admin non trovato nella tabella companies")
    
    # Lista tutti gli utenti admin
    print("\n📋 Tutti gli utenti admin nel sistema:")
    cursor.execute("SELECT id, username, email FROM admins")
    admins = cursor.fetchall()
    
    for admin in admins:
        print(f"   - ID: {admin[0]}, Username: {admin[1]}, Email: {admin[2]}")
    
    conn.close()

if __name__ == "__main__":
    check_admin_password()
