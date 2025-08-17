#!/usr/bin/env python3
"""
Script per controllare la struttura della tabella training_courses
"""
import sqlite3

def check_courses_table():
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    print("🔍 Controllo struttura tabella training_courses...")
    
    # Ottieni informazioni sulla tabella
    cursor.execute("PRAGMA table_info(training_courses)")
    columns = cursor.fetchall()
    
    print("📋 Colonne della tabella training_courses:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]}) - {'NOT NULL' if col[3] else 'NULL'} - Default: {col[4]}")
    
    # Controlla se esiste la colonna is_active
    has_is_active = any(col[1] == 'is_active' for col in columns)
    print(f"\n✅ Colonna is_active presente: {has_is_active}")
    
    if not has_is_active:
        print("➕ Aggiungendo colonna is_active...")
        cursor.execute("ALTER TABLE training_courses ADD COLUMN is_active INTEGER DEFAULT 1")
        conn.commit()
        print("✅ Colonna is_active aggiunta!")
    
    # Controlla i corsi
    cursor.execute("SELECT id, title, category, is_active FROM training_courses")
    courses = cursor.fetchall()
    print(f"\n📚 Corsi nel database: {len(courses)}")
    for course in courses:
        print(f"  - ID: {course[0]}, Titolo: {course[1]}, Categoria: {course[2]}, Attivo: {course[3]}")
    
    conn.close()

if __name__ == "__main__":
    check_courses_table()
