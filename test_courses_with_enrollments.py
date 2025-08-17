#!/usr/bin/env python3
"""
Script per testare il metodo get_courses con conteggio iscritti
"""
from training_module import TrainingModule

def test_courses_with_enrollments():
    training = TrainingModule()
    
    print("🔍 Test metodo get_courses con conteggio iscritti...")
    
    courses = training.get_courses()
    
    print(f"📚 Corsi trovati: {len(courses)}")
    print("\n📋 Dettagli corsi:")
    for course in courses:
        print(f"  - {course['title']} (ID: {course['id']})")
        print(f"    Categoria: {course['category']}")
        print(f"    Difficoltà: {course['difficulty_level']}")
        print(f"    Durata: {course['duration_minutes']} minuti")
        print(f"    Iscritti: {course['enrolled_students']}")
        print()

if __name__ == "__main__":
    test_courses_with_enrollments()
