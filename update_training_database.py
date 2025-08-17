#!/usr/bin/env python3
"""
Script per aggiornare il database del training con le nuove colonne
"""
import sqlite3

def update_database():
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    print("🔧 Aggiornamento database training...")
    
    try:
        # Aggiungi colonna progress_data a training_enrollments se non esiste
        cursor.execute("PRAGMA table_info(training_enrollments)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'progress_data' not in columns:
            print("➕ Aggiungo colonna progress_data a training_enrollments...")
            cursor.execute("ALTER TABLE training_enrollments ADD COLUMN progress_data TEXT")
            print("✅ Colonna progress_data aggiunta")
        else:
            print("✅ Colonna progress_data già presente")
        
        # Aggiungi colonna explanation a training_questions se non esiste
        cursor.execute("PRAGMA table_info(training_questions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'explanation' not in columns:
            print("➕ Aggiungo colonna explanation a training_questions...")
            cursor.execute("ALTER TABLE training_questions ADD COLUMN explanation TEXT")
            print("✅ Colonna explanation aggiunta")
        else:
            print("✅ Colonna explanation già presente")
        
        # Crea tabella training_course_content se non esiste
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS training_course_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content_type TEXT NOT NULL,
                content TEXT NOT NULL,
                order_index INTEGER NOT NULL,
                duration_minutes INTEGER,
                FOREIGN KEY (course_id) REFERENCES training_courses (id)
            )
        """)
        print("✅ Tabella training_course_content verificata/creata")
        
        conn.commit()
        print("🎉 Database aggiornato con successo!")
        
    except Exception as e:
        print(f"❌ Errore nell'aggiornamento: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_database()
