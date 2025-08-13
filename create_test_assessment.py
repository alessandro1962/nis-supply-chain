import sqlite3
import uuid
from datetime import datetime

def create_test_assessment():
    conn = sqlite3.connect('nis2_platform.db')
    cursor = conn.cursor()
    
    try:
        # Verifica le tabelle esistenti
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("Tabelle trovate:", [table[0] for table in tables])
        
        # Verifica che esistano azienda e fornitore
        cursor.execute("SELECT id, name FROM companies WHERE id = 1")
        company = cursor.fetchone()
        print("Azienda trovata:", company)
        
        cursor.execute("SELECT id, company_name FROM suppliers WHERE id = 1")
        supplier = cursor.fetchone()
        print("Fornitore trovato:", supplier)
        
        if not company or not supplier:
            print("Errore: Azienda o fornitore non trovati")
            return
        
        # Verifica se la tabella assessments esiste
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assessments'")
        assessments_table = cursor.fetchone()
        print("Tabella assessments esiste:", assessments_table is not None)
        
        if not assessments_table:
            print("Creazione tabella assessments...")
            cursor.execute("""
                CREATE TABLE assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_id INTEGER NOT NULL,
                    supplier_id INTEGER NOT NULL,
                    assessment_token TEXT UNIQUE NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TEXT,
                    completed_at TEXT,
                    evaluation_result TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies (id),
                    FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
                )
            """)
            conn.commit()
            print("Tabella assessments creata!")
        
        # Crea un assessment di test
        assessment_token = str(uuid.uuid4())
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute("""
            INSERT INTO assessments (company_id, supplier_id, assessment_token, status, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (1, 1, assessment_token, 'pending', created_at))
        
        conn.commit()
        
        print(f"Assessment di test creato con successo!")
        print(f"Token: {assessment_token}")
        print(f"URL: http://localhost:8000/assessment/{assessment_token}")
        
    except Exception as e:
        print(f"Errore: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    create_test_assessment()
