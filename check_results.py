import sqlite3
import json

def check_assessment_results():
    conn = sqlite3.connect('nis2_platform.db')
    cursor = conn.cursor()
    
    try:
        print("=== RISULTATI ASSESSMENT COMPLETATI ===")
        cursor.execute("""
            SELECT a.id, a.supplier_id, s.company_name, a.evaluation_result, a.completed_at
            FROM assessments a
            JOIN suppliers s ON a.supplier_id = s.id
            WHERE a.status = 'completed'
        """)
        
        assessments = cursor.fetchall()
        
        for assessment in assessments:
            assessment_id, supplier_id, supplier_name, evaluation_result, completed_at = assessment
            print(f"\nAssessment ID: {assessment_id}")
            print(f"Fornitore: {supplier_name} (ID: {supplier_id})")
            print(f"Completato il: {completed_at}")
            
            if evaluation_result:
                try:
                    result = json.loads(evaluation_result)
                    print(f"Risultato: {result.get('outcome', 'N/A')}")
                    print(f"Punteggio: {result.get('final_score', 'N/A')}%")
                    print(f"Motivo: {result.get('reason', 'N/A')}")
                    
                    if 'improvement_areas' in result:
                        print("Aree di miglioramento:")
                        for area in result['improvement_areas']:
                            print(f"  - {area}")
                except:
                    print(f"Risultato (raw): {evaluation_result[:200]}...")
            else:
                print("Nessun risultato disponibile")
            
            print("-" * 50)
        
    except Exception as e:
        print(f"Errore: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_assessment_results()
