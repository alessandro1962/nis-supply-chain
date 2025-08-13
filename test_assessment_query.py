import sqlite3

def test_assessment_query():
    token = "9dc41bda-54ec-409a-b476-df397f4bb345"
    
    conn = sqlite3.connect("nis2_platform.db")
    cursor = conn.cursor()
    
    try:
        print(f"=== TEST QUERY ASSESSMENT ===")
        print(f"Token da cercare: {token}")
        
        # Test 1: Verifica se la tabella assessments esiste
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assessments'")
        table_exists = cursor.fetchone()
        print(f"Tabella assessments esiste: {table_exists is not None}")
        
        # Test 2: Conta tutti gli assessment
        cursor.execute("SELECT COUNT(*) FROM assessments")
        total_count = cursor.fetchone()[0]
        print(f"Totale assessment nel database: {total_count}")
        
        # Test 3: Verifica se esiste l'assessment con quel token
        cursor.execute("SELECT COUNT(*) FROM assessments WHERE assessment_token = ?", (token,))
        count = cursor.fetchone()[0]
        print(f"Assessment con token {token}: {count}")
        
        # Test 4: Mostra tutti gli assessment
        cursor.execute("SELECT id, assessment_token, status FROM assessments")
        all_assessments = cursor.fetchall()
        print(f"Tutti gli assessment:")
        for assessment in all_assessments:
            print(f"  ID: {assessment[0]}, Token: {assessment[1]}, Status: {assessment[2]}")
        
        # Test 5: Prova la query completa del server
        cursor.execute("""
            SELECT a.id, a.status, s.company_name, s.email, c.name as company_name
            FROM assessments a
            JOIN suppliers s ON a.supplier_id = s.id
            JOIN companies c ON a.company_id = c.id
            WHERE a.assessment_token = ?
        """, (token,))
        
        result = cursor.fetchone()
        print(f"Risultato query completa: {result}")
        
        # Test 6: Verifica se esistono le tabelle suppliers e companies
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='suppliers'")
        suppliers_exists = cursor.fetchone()
        print(f"Tabella suppliers esiste: {suppliers_exists is not None}")
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='companies'")
        companies_exists = cursor.fetchone()
        print(f"Tabella companies esiste: {companies_exists is not None}")
        
        # Test 7: Verifica i dati nelle tabelle correlate
        if suppliers_exists:
            cursor.execute("SELECT id, company_name FROM suppliers WHERE id = 1")
            supplier = cursor.fetchone()
            print(f"Supplier ID 1: {supplier}")
        
        if companies_exists:
            cursor.execute("SELECT id, name FROM companies WHERE id = 1")
            company = cursor.fetchone()
            print(f"Company ID 1: {company}")
        
    except Exception as e:
        print(f"Errore: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    test_assessment_query()
