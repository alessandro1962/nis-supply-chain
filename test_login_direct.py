#!/usr/bin/env python3
"""
Script per testare il login direttamente
"""
import requests

def test_login():
    print("🔍 Test login dipendente...")
    
    # Crea una sessione
    session = requests.Session()
    
    # Prima ottieni la pagina di login
    print("1. Ottengo la pagina di login...")
    r = session.get('http://localhost:8000/training/employee-login')
    print(f"   Status: {r.status_code}")
    
    # Poi fai il login
    print("\n2. Faccio il login...")
    login_data = {
        'email': 'ale@nwk.it',
        'password': 'Somiwo123'
    }
    
    r = session.post('http://localhost:8000/training/employee-login', data=login_data)
    print(f"   Status: {r.status_code}")
    print(f"   Headers: {dict(r.headers)}")
    print(f"   Content length: {len(r.text)}")
    
    # Controlla se c'è un redirect
    if r.status_code == 302:
        print(f"   Redirect URL: {r.headers.get('location')}")
    else:
        print("   Nessun redirect")
        print(f"   Content preview: {r.text[:200]}...")
    
    # Controlla i cookie
    print(f"\n3. Cookie ricevuti: {dict(session.cookies)}")
    
    # Prova ad accedere alla dashboard
    print("\n4. Provo ad accedere alla dashboard...")
    r = session.get('http://localhost:8000/training/employee-dashboard')
    print(f"   Status: {r.status_code}")
    print(f"   Content length: {len(r.text)}")

if __name__ == "__main__":
    test_login()
