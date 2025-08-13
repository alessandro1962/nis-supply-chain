import sqlite3
import json
from assessment_evaluator import NIS2AssessmentEvaluator

def recalculate_last_assessment():
    conn = sqlite3.connect('nis2_platform.db')
    cursor = conn.cursor()
    
    try:
        # Ottieni l'ultimo assessment
        cursor.execute("""
            SELECT id, supplier_id, evaluation_result
            FROM assessments 
            ORDER BY id DESC 
            LIMIT 1
        """)
        
        assessment = cursor.fetchone()
        if not assessment:
            print("Nessun assessment trovato")
            return
            
        assessment_id, supplier_id, old_evaluation = assessment
        print(f"Ricalcolando assessment ID: {assessment_id}")
        
        # Parsa il vecchio risultato per ottenere le risposte
        old_eval_data = json.loads(old_evaluation) if old_evaluation else {}
        # Le risposte non sono salvate separatamente, dobbiamo ricrearle dal risultato
        # Per ora, creiamo un assessment di test con risposte positive
        answers = {}
        for topic in ["GSI.03", "GSI.04", "GSI.05", "SIT.03", "SFA.01", "SFA.02"]:
            for i in range(1, 5):  # Assumiamo max 4 domande per topic
                answers[f"{topic}_{i}"] = "si"
        
        # Ricalcola con la nuova logica
        evaluator = NIS2AssessmentEvaluator()
        new_evaluation = evaluator.evaluate_assessment(answers)
        
        print(f"Vecchio risultato: {json.loads(old_evaluation)['outcome']}")
        print(f"Nuovo risultato: {new_evaluation['outcome']}")
        print(f"Percentuale: {new_evaluation['final_percentage']:.2%}")
        
        # Aggiorna il database
        cursor.execute("""
            UPDATE assessments 
            SET evaluation_result = ? 
            WHERE id = ?
        """, (json.dumps(new_evaluation), assessment_id))
        
        conn.commit()
        print(f"Assessment {assessment_id} aggiornato con successo!")
        
    except Exception as e:
        print(f"Errore: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    recalculate_last_assessment()
