#!/usr/bin/env python3
"""
Script per testare l'accesso alla pagina del corso
"""
import requests
import json

def test_course_access():
    base_url = "http://localhost:8000"
    
    print("🧪 Test accesso pagina corso...")
    
    # Prima facciamo login
    login_data = {
        "email": "ale@nwk.it",
        "password": "password123"
    }
    
    session = requests.Session()
    
    # Login
    print("🔐 Tentativo login...")
    login_response = session.post(f"{base_url}/company-login", data=login_data)
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        print("✅ Login riuscito")
        
        # Test accesso alla pagina del corso
        print("📚 Test accesso corso...")
        course_response = session.get(f"{base_url}/training/course/5")
        print(f"Corso status: {course_response.status_code}")
        
        if course_response.status_code == 200:
            print("✅ Accesso corso riuscito")
            print("📄 Contenuto pagina:")
            print(course_response.text[:500] + "...")
        else:
            print("❌ Errore accesso corso")
            print(f"Response: {course_response.text}")
    else:
        print("❌ Errore login")
        print(f"Response: {login_response.text}")

if __name__ == "__main__":
    test_course_access()
