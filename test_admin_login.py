#!/usr/bin/env python3
"""
Script per testare il login admin direttamente
"""
import requests

def test_admin_login():
    print("🔍 Test login admin...")
    
    # Crea una sessione
    session = requests.Session()
    
    # Prima ottieni la pagina di login
    print("1. Ottengo la pagina di login...")
    r = session.get('http://localhost:8000/unified-login')
    print(f"   Status: {r.status_code}")
    
    # Poi fai il login admin
    print("\n2. Faccio il login admin...")
    login_data = {
        'user_type': 'admin',
        'email': 'admin@nis2platform.com',
        'password': 'admin123'
    }
    
    r = session.post('http://localhost:8000/unified-login', data=login_data)
    print(f"   Status: {r.status_code}")
    print(f"   Headers: {dict(r.headers)}")
    
    # Controlla se c'è un redirect
    if r.status_code == 302:
        print(f"   ✅ Redirect URL: {r.headers.get('location')}")
    else:
        print("   ❌ Nessun redirect")
        print(f"   Content preview: {r.text[:500]}...")
    
    # Controlla i cookie
    print(f"\n3. Cookie ricevuti: {dict(session.cookies)}")
    
    # Prova ad accedere alla dashboard admin
    print("\n4. Provo ad accedere alla dashboard admin...")
    r = session.get('http://localhost:8000/admin-dashboard')
    print(f"   Status: {r.status_code}")
    print(f"   Content length: {len(r.text)}")
    
    if r.status_code == 200:
        print("   ✅ Login admin funziona!")
    else:
        print("   ❌ Login admin non funziona")

if __name__ == "__main__":
    test_admin_login()
