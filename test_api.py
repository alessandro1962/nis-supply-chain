import requests
import json

def test_api():
    try:
        # Test API suppliers
        response = requests.get("http://localhost:8000/api/company/1/suppliers")
        print("=== API SUPPLIERS ===")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Numero fornitori: {len(data)}")
            for supplier in data:
                print(f"ID: {supplier.get('id')}, Nome: {supplier.get('company_name')}")
                print(f"  Assessment Status: {supplier.get('assessment_status')}")
                print(f"  Evaluation Result: {supplier.get('evaluation_result')}")
                print("---")
        else:
            print(f"Errore: {response.text}")
        
        # Test API dashboard stats
        response = requests.get("http://localhost:8000/api/company/dashboard")
        print("\n=== API DASHBOARD STATS ===")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
        else:
            print(f"Errore: {response.text}")
            
    except Exception as e:
        print(f"Errore nella connessione: {e}")

if __name__ == "__main__":
    test_api()
