import sqlite3
import json
from assessment_evaluator import NIS2AssessmentEvaluator

def evaluate_existing_assessments():
    """Valuta gli assessment esistenti che non hanno ancora evaluation_result"""
    conn = sqlite3.connect('nis2_platform.db')
    cursor = conn.cursor()
    
    try:
        # Trova assessment completati senza evaluation_result
        cursor.execute("""
            SELECT a.id, a.assessment_token, a.supplier_id, s.company_name
            FROM assessments a
            JOIN suppliers s ON a.supplier_id = s.id
            WHERE a.status = 'completed' AND a.evaluation_result IS NULL
        """)
        
        assessments_to_evaluate = cursor.fetchall()
        print(f"Trovati {len(assessments_to_evaluate)} assessment da valutare")
        
        if not assessments_to_evaluate:
            print("Nessun assessment da valutare!")
            return
        
        evaluator = NIS2AssessmentEvaluator()
        
        for assessment_id, token, supplier_id, company_name in assessments_to_evaluate:
            print(f"\nValutando assessment {assessment_id} per {company_name}...")
            
            # Raccogli le risposte dell'assessment
            cursor.execute("""
                SELECT codice_argomento, numero_domanda, risposta
                FROM assessment_answers
                WHERE assessment_id = ?
                ORDER BY codice_argomento, numero_domanda
            """, (assessment_id,))
            
            answers = {}
            for row in cursor.fetchall():
                codice_argomento, numero_domanda, risposta = row
                question_id = f"{codice_argomento}_{numero_domanda}"
                answers[question_id] = risposta
            
            print(f"Trovate {len(answers)} risposte")
            
            if answers:
                # Valuta l'assessment
                evaluation_result = evaluator.evaluate_assessment(answers, has_iso27001=False)
                
                # Salva il risultato
                cursor.execute("""
                    UPDATE assessments 
                    SET evaluation_result = ?
                    WHERE id = ?
                """, (json.dumps(evaluation_result), assessment_id))
                
                print(f"✅ Assessment {assessment_id} valutato: {evaluation_result['outcome']} - Punteggio: {evaluation_result.get('final_score', 'N/A')}%")
            else:
                print(f"❌ Assessment {assessment_id} non ha risposte!")
        
        conn.commit()
        print(f"\n✅ Valutazione completata per {len(assessments_to_evaluate)} assessment")
        
    except Exception as e:
        print(f"❌ Errore durante la valutazione: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    evaluate_existing_assessments()
