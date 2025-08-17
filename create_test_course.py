#!/usr/bin/env python3
"""
Script per creare un corso di test nel database
"""
import sqlite3
import json

def create_test_course():
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    print("🎓 Creazione corso di test...")
    
    # Corso di test
    course_data = {
        'title': 'Cybersecurity Fundamentals NIS2',
        'description': 'Corso base sui principi fondamentali della cybersecurity secondo i requisiti NIS2. Copre i concetti essenziali di sicurezza informatica, minacce comuni e best practices per la protezione dei sistemi.',
        'category': 'Cybersecurity',
        'duration_minutes': 90,
        'difficulty_level': 'BEGINNER',
        'nis2_requirements': ['Gestione del rischio', 'Protezione dei sistemi', 'Incident response'],
        'content_url': 'https://example.com/cybersecurity-fundamentals'
    }
    
    try:
        cursor.execute("""
            INSERT INTO training_courses (title, description, category, duration_minutes, 
                                        difficulty_level, nis2_requirements, content_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            course_data['title'],
            course_data['description'],
            course_data['category'],
            course_data['duration_minutes'],
            course_data['difficulty_level'],
            json.dumps(course_data['nis2_requirements']),
            course_data['content_url']
        ))
        
        course_id = cursor.lastrowid
        conn.commit()
        
        print(f"✅ Corso creato con successo!")
        print(f"   ID: {course_id}")
        print(f"   Titolo: {course_data['title']}")
        print(f"   Categoria: {course_data['category']}")
        print(f"   Durata: {course_data['duration_minutes']} minuti")
        print(f"   Livello: {course_data['difficulty_level']}")
        
        # Crea anche un secondo corso
        course_data2 = {
            'title': 'Business Continuity Management',
            'description': 'Corso avanzato sulla gestione della continuità aziendale secondo i requisiti NIS2. Include pianificazione, test e mantenimento dei piani di business continuity.',
            'category': 'Business Continuity',
            'duration_minutes': 120,
            'difficulty_level': 'INTERMEDIATE',
            'nis2_requirements': ['Business continuity', 'Disaster recovery', 'Pianificazione strategica'],
            'content_url': 'https://example.com/business-continuity'
        }
        
        cursor.execute("""
            INSERT INTO training_courses (title, description, category, duration_minutes, 
                                        difficulty_level, nis2_requirements, content_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            course_data2['title'],
            course_data2['description'],
            course_data2['category'],
            course_data2['duration_minutes'],
            course_data2['difficulty_level'],
            json.dumps(course_data2['nis2_requirements']),
            course_data2['content_url']
        ))
        
        course_id2 = cursor.lastrowid
        conn.commit()
        
        print(f"✅ Secondo corso creato con successo!")
        print(f"   ID: {course_id2}")
        print(f"   Titolo: {course_data2['title']}")
        print(f"   Categoria: {course_data2['category']}")
        print(f"   Durata: {course_data2['duration_minutes']} minuti")
        print(f"   Livello: {course_data2['difficulty_level']}")
        
        # Verifica i corsi nel database
        cursor.execute("SELECT id, title, category, difficulty_level FROM training_courses WHERE is_active = 1")
        courses = cursor.fetchall()
        
        print(f"\n📚 Corsi totali nel database: {len(courses)}")
        for course in courses:
            print(f"   - {course[0]}: {course[1]} ({course[2]}) - {course[3]}")
        
    except Exception as e:
        print(f"❌ Errore nella creazione del corso: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_test_course()
