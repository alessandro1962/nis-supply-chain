#!/usr/bin/env python3
"""
Test per verificare il PDF su localhost
"""

import requests
import json

def test_localhost_pdf():
    print("🔍 Testando PDF su localhost...")
    
    # Login
    session = requests.Session()
    
    try:
        # Login
        login_data = {
            'email': 'admin@company.com',
            'password': 'admin'
        }
        
        response = session.post('http://localhost:8000/api/auth/company-login', data=login_data, allow_redirects=False)
        
        if response.status_code == 302:
            print("✅ Login effettuato")
            
            # Test generazione PDF per Datamatic (supplier_id = 10)
            pdf_response = session.get('http://localhost:8000/certificate/10')
            
            if pdf_response.status_code == 200:
                print("✅ PDF generato con successo")
                
                # Salva il PDF per verificare
                with open('test_localhost_datamatic.pdf', 'wb') as f:
                    f.write(pdf_response.content)
                
                print("📄 PDF salvato come: test_localhost_datamatic.pdf")
                print("📋 Controlla il file per verificare che sia professionale")
                
            else:
                print(f"❌ Errore generazione PDF: {pdf_response.status_code}")
                print(f"Response: {pdf_response.text}")
                
        else:
            print(f"❌ Errore login: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Errore: {e}")

if __name__ == "__main__":
    test_localhost_pdf()
