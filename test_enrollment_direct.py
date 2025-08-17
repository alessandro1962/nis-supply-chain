#!/usr/bin/env python3
"""
Script per testare l'iscrizione direttamente
"""
from training_module import TrainingModule

def test_enrollment_direct():
    training = TrainingModule()
    
    print("🔍 Test iscrizione diretta...")
    
    # Test iscrizione Mario Rossi (ID 1) al corso Gestione del Rischio (ID 2)
    employee_id = 1
    course_id = 2
    
    print(f"🧪 Iscrizione: Dipendente {employee_id} al corso {course_id}")
    
    try:
        enrollment_id = training.enroll_employee(employee_id, course_id)
        print(f"✅ Iscrizione riuscita! ID: {enrollment_id}")
        
        # Verifica che l'iscrizione sia stata registrata
        enrollments = training.get_employee_enrollments(employee_id)
        print(f"📊 Iscrizioni di Mario Rossi: {len(enrollments)}")
        for enrollment in enrollments:
            print(f"  - {enrollment['course_title']} - {enrollment['status']}")
            
    except ValueError as e:
        print(f"❌ Errore di validazione: {e}")
    except Exception as e:
        print(f"❌ Errore generico: {e}")

if __name__ == "__main__":
    test_enrollment_direct()
