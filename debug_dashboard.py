import sqlite3
import json

def debug_dashboard():
    conn = sqlite3.connect('nis2_platform.db')
    cursor = conn.cursor()
    
    try:
        # Verifica fornitori dell'azienda 1
        print("=== FORNITORI AZIENDA 1 ===")
        cursor.execute("""
            SELECT id, company_name, email, sector, country, created_at
            FROM suppliers 
            WHERE company_id = 1
            ORDER BY created_at DESC
        """)
        suppliers = cursor.fetchall()
        print(f"Numero fornitori trovati: {len(suppliers)}")
        for supplier in suppliers:
            print(f"ID: {supplier[0]}, Nome: {supplier[1]}, Email: {supplier[2]}")
        
        # Verifica assessment per ogni fornitore
        print("\n=== ASSESSMENT PER FORNITORE ===")
        for supplier in suppliers:
            supplier_id = supplier[0]
            print(f"\nFornitore {supplier_id} ({supplier[1]}):")
            
            cursor.execute("""
                SELECT id, status, evaluation_result, completed_at
                FROM assessments 
                WHERE supplier_id = ?
                ORDER BY id DESC
            """, (supplier_id,))
            
            assessments = cursor.fetchall()
            if assessments:
                latest = assessments[0]
                print(f"  Ultimo assessment ID: {latest[0]}")
                print(f"  Status: {latest[1]}")
                print(f"  Completed at: {latest[3]}")
                if latest[2]:  # evaluation_result
                    try:
                        eval_data = json.loads(latest[2])
                        print(f"  Risultato: {eval_data.get('outcome', 'N/A')}")
                        print(f"  Percentuale: {eval_data.get('final_percentage', 'N/A')}")
                    except:
                        print(f"  Risultato: Errore parsing JSON")
            else:
                print("  Nessun assessment trovato")
        
        # Test query esatta dell'API
        print("\n=== TEST QUERY API ===")
        cursor.execute("""
            SELECT 
                s.id, 
                s.company_name, 
                s.email, 
                s.sector, 
                s.country, 
                s.created_at,
                COALESCE(a.status, 'pending') as assessment_status,
                a.evaluation_result,
                a.completed_at
            FROM suppliers s
            LEFT JOIN (
                SELECT DISTINCT supplier_id, status, evaluation_result, completed_at
                FROM assessments 
                WHERE id IN (
                    SELECT MAX(id) 
                    FROM assessments 
                    GROUP BY supplier_id
                )
            ) a ON s.id = a.supplier_id
            WHERE s.company_id = 1
            ORDER BY s.created_at DESC
        """)
        
        results = cursor.fetchall()
        print(f"Risultati query API: {len(results)}")
        for row in results:
            print(f"Fornitore: {row[1]} (ID: {row[0]})")
            print(f"  Assessment Status: {row[6]}")
            print(f"  Evaluation Result: {row[7]}")
            print(f"  Completed At: {row[8]}")
            print("---")
            
    except Exception as e:
        print(f"Errore: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    debug_dashboard()
