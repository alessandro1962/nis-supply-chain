#!/usr/bin/env python3
"""
Script per testare l'iscrizione ai corsi
"""
from training_module import TrainingModule

def test_enrollment():
    training = TrainingModule()
    
    print("🔍 Test iscrizione ai corsi...")
    
    # Controlla dipendenti disponibili
    employees = training.get_employees(1)
    print(f"👥 Dipendenti disponibili: {len(employees)}")
    for emp in employees:
        print(f"  - ID: {emp['id']}, Nome: {emp['name']}, Email: {emp['email']}")
    
    # Controlla corsi disponibili
    courses = training.get_courses()
    print(f"\n📚 Corsi disponibili: {len(courses)}")
    for course in courses:
        print(f"  - ID: {course['id']}, Titolo: {course['title']}")
    
    # Test iscrizione
    if employees and courses:
        employee_id = employees[0]['id']
        course_id = courses[0]['id']
        
        print(f"\n🧪 Test iscrizione: Dipendente {employee_id} al corso {course_id}")
        
        try:
            enrollment_id = training.enroll_employee(employee_id, course_id)
            print(f"✅ Iscrizione riuscita! ID: {enrollment_id}")
        except ValueError as e:
            print(f"❌ Errore di validazione: {e}")
        except Exception as e:
            print(f"❌ Errore generico: {e}")
    
    # Controlla iscrizioni esistenti
    print(f"\n📊 Iscrizioni esistenti:")
    for emp in employees:
        enrollments = training.get_employee_enrollments(emp['id'])
        print(f"  - {emp['name']}: {len(enrollments)} iscrizioni")
        for enrollment in enrollments:
            print(f"    * {enrollment['course_title']} - {enrollment['status']}")

if __name__ == "__main__":
    test_enrollment()
