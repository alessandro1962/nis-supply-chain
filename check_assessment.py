import sqlite3

def check_assessment():
    conn = sqlite3.connect('nis2_platform.db')
    cursor = conn.cursor()
    
    try:
        print("=== ASSESSMENTS NEL DATABASE ===")
        cursor.execute("SELECT id, company_id, supplier_id, assessment_token, status FROM assessments")
        assessments = cursor.fetchall()
        
        if assessments:
            for assessment in assessments:
                print(f"ID: {assessment[0]}, Company: {assessment[1]}, Supplier: {assessment[2]}, Token: {assessment[3]}, Status: {assessment[4]}")
        else:
            print("Nessun assessment trovato nel database")
        
        print("\n=== VERIFICA TOKEN SPECIFICO ===")
        token = "9dc41bda-54ec-409a-b476-df397f4bb345"
        cursor.execute("SELECT * FROM assessments WHERE assessment_token = ?", (token,))
        assessment = cursor.fetchone()
        
        if assessment:
            print(f"Assessment trovato: {assessment}")
        else:
            print(f"Assessment con token {token} NON TROVATO")
            
    except Exception as e:
        print(f"Errore: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_assessment()
