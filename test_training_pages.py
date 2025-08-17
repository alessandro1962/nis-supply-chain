#!/usr/bin/env python3
"""
Test per verificare il funzionamento di tutte le pagine del Modulo Training
"""

import requests
import json
from datetime import datetime

def test_training_pages():
    """Test delle pagine del training module"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Test Pagine Modulo Training")
    print("=" * 50)
    
    # Lista delle pagine da testare
    pages = [
        {
            "name": "Dashboard Training",
            "url": "/training/dashboard",
            "expected_status": 200
        },
        {
            "name": "Gestione Dipendenti",
            "url": "/training/employees", 
            "expected_status": 200
        },
        {
            "name": "Gestione Corsi",
            "url": "/training/courses",
            "expected_status": 200
        },
        {
            "name": "Quiz e Certificazioni",
            "url": "/training/quiz/1",
            "expected_status": 200
        },
        {
            "name": "Report e Statistiche",
            "url": "/training/reports",
            "expected_status": 200
        },
        {
            "name": "Gestione Notifiche",
            "url": "/training/notifications",
            "expected_status": 200
        }
    ]
    
    # Test delle pagine
    for page in pages:
        try:
            print(f"\n📄 Testando: {page['name']}")
            print(f"   URL: {page['url']}")
            
            response = requests.get(f"{base_url}{page['url']}", allow_redirects=False)
            
            if response.status_code == page['expected_status']:
                print(f"   ✅ Status: {response.status_code} - OK")
            elif response.status_code == 302:  # Redirect (probabilmente al login)
                print(f"   ⚠️  Status: {response.status_code} - Redirect (login richiesto)")
            else:
                print(f"   ❌ Status: {response.status_code} - Errore")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Errore di connessione - Server non raggiungibile")
        except Exception as e:
            print(f"   ❌ Errore: {str(e)}")
    
    # Test delle API
    print(f"\n🔌 Test API Endpoints")
    print("-" * 30)
    
    api_endpoints = [
        {
            "name": "Health Check",
            "url": "/training/api/health",
            "method": "GET"
        },
        {
            "name": "Statistiche Training",
            "url": "/training/api/stats/1",
            "method": "GET"
        },
        {
            "name": "Corsi Disponibili",
            "url": "/training/api/courses",
            "method": "GET"
        }
    ]
    
    for api in api_endpoints:
        try:
            print(f"\n🔌 Testando API: {api['name']}")
            print(f"   URL: {api['url']}")
            print(f"   Method: {api['method']}")
            
            if api['method'] == 'GET':
                response = requests.get(f"{base_url}{api['url']}")
            else:
                response = requests.post(f"{base_url}{api['url']}")
            
            if response.status_code == 200:
                print(f"   ✅ Status: {response.status_code} - OK")
                try:
                    data = response.json()
                    print(f"   📊 Risposta: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"   📊 Risposta: {response.text[:200]}...")
            else:
                print(f"   ❌ Status: {response.status_code} - Errore")
                print(f"   📊 Risposta: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print(f"   ❌ Errore di connessione - Server non raggiungibile")
        except Exception as e:
            print(f"   ❌ Errore: {str(e)}")
    
    print(f"\n" + "=" * 50)
    print("✅ Test completato!")
    print("\n📋 Note:")
    print("- Se vedi redirect (302), significa che il login è richiesto")
    print("- Le pagine HTML dovrebbero essere accessibili dopo il login")
    print("- Le API dovrebbero funzionare indipendentemente dal login")
    print("- Verifica che il server sia in esecuzione su http://localhost:8000")

def test_training_functionality():
    """Test delle funzionalità del training module"""
    
    base_url = "http://localhost:8000"
    
    print(f"\n🔧 Test Funzionalità Training")
    print("=" * 50)
    
    # Test aggiunta dipendente
    print(f"\n👤 Test Aggiunta Dipendente")
    try:
        employee_data = {
            "name": "Test User",
            "email": "test@example.com",
            "role": "Security Officer",
            "department": "IT",
            "hire_date": "2024-01-01"
        }
        
        response = requests.post(f"{base_url}/training/api/employees", data=employee_data)
        
        if response.status_code in [200, 201]:
            print(f"   ✅ Dipendente aggiunto con successo")
            try:
                data = response.json()
                print(f"   📊 Risposta: {json.dumps(data, indent=2)}")
            except:
                print(f"   📊 Risposta: {response.text}")
        else:
            print(f"   ❌ Errore nell'aggiunta dipendente: {response.status_code}")
            print(f"   📊 Risposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Errore: {str(e)}")
    
    # Test iscrizione corso
    print(f"\n📚 Test Iscrizione Corso")
    try:
        enrollment_data = {
            "employee_id": 1,
            "course_id": 1
        }
        
        response = requests.post(f"{base_url}/training/api/enroll", data=enrollment_data)
        
        if response.status_code in [200, 201]:
            print(f"   ✅ Iscrizione effettuata con successo")
            try:
                data = response.json()
                print(f"   📊 Risposta: {json.dumps(data, indent=2)}")
            except:
                print(f"   📊 Risposta: {response.text}")
        else:
            print(f"   ❌ Errore nell'iscrizione: {response.status_code}")
            print(f"   📊 Risposta: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Errore: {str(e)}")

if __name__ == "__main__":
    print("🚀 Avvio test del Modulo Training")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test delle pagine
    test_training_pages()
    
    # Test delle funzionalità
    test_training_functionality()
    
    print(f"\n🎉 Test completato alle {datetime.now().strftime('%H:%M:%S')}")
    print("\n📝 Prossimi passi:")
    print("1. Verifica che il server sia in esecuzione")
    print("2. Accedi al sistema tramite login")
    print("3. Naviga alle pagine del training module")
    print("4. Testa le funzionalità interattive")
