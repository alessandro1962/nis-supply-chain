import sqlite3

def check_assessments():
    conn = sqlite3.connect('nis2_platform.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, supplier_id, status, evaluation_result FROM assessments")
        results = cursor.fetchall()
        
        print("=== ASSESSMENT NEL DATABASE ===")
        for row in results:
            assessment_id, supplier_id, status, evaluation_result = row
            has_result = "Presente" if evaluation_result else "NULL"
            print(f"ID: {assessment_id}, Supplier: {supplier_id}, Status: {status}, Result: {has_result}")
            
            if evaluation_result:
                print(f"  Contenuto: {evaluation_result[:100]}...")
        
        print(f"\nTotale assessment: {len(results)}")
        
    except Exception as e:
        print(f"Errore: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_assessments()
