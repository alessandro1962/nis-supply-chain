import sqlite3
import os

def create_assessment_answers_table(cursor):
    """Crea la tabella per le risposte degli assessment"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessment_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id INTEGER NOT NULL,
            codice_argomento TEXT NOT NULL,
            numero_domanda INTEGER NOT NULL,
            risposta TEXT NOT NULL CHECK (risposta IN ('si', 'no', 'na')),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (assessment_id) REFERENCES assessments (id) ON DELETE CASCADE,
            UNIQUE(assessment_id, codice_argomento, numero_domanda)
        )
    """)
    print("✅ Tabella assessment_answers creata/aggiornata")

def create_assessments_table(cursor):
    """Crea la tabella per gli assessment"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            supplier_id INTEGER NOT NULL,
            assessment_token TEXT UNIQUE NOT NULL,
            status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'completed', 'expired')),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            completed_at DATETIME,
            evaluation_result TEXT,
            FOREIGN KEY (company_id) REFERENCES companies (id) ON DELETE CASCADE,
            FOREIGN KEY (supplier_id) REFERENCES suppliers (id) ON DELETE CASCADE
        )
    """)
    print("✅ Tabella assessments creata/aggiornata")

def create_companies_table(cursor):
    """Crea la tabella companies"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            admin_email TEXT UNIQUE NOT NULL,
            sector TEXT,
            vat_number TEXT,
            fiscal_code TEXT,
            address TEXT,
            city TEXT,
            postal_code TEXT,
            country TEXT,
            phone TEXT,
            website TEXT,
            contact_person TEXT,
            contact_phone TEXT,
            contact_email TEXT,
            company_size TEXT,
            industry TEXT,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("✅ Tabella companies creata/aggiornata")

def create_suppliers_table(cursor):
    """Crea la tabella suppliers"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            company_name TEXT NOT NULL,
            email TEXT NOT NULL,
            sector TEXT,
            country TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies (id) ON DELETE CASCADE
        )
    """)
    print("✅ Tabella suppliers creata/aggiornata")

def update_suppliers_table(cursor):
    """Aggiunge la colonna company_id alla tabella suppliers esistente"""
    try:
        cursor.execute("ALTER TABLE suppliers ADD COLUMN company_id INTEGER")
        cursor.execute("UPDATE suppliers SET company_id = 1 WHERE company_id IS NULL")
        print("✅ Colonna company_id aggiunta alla tabella suppliers")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("ℹ️ Colonna company_id già presente")
        else:
            print(f"⚠️ Errore nell'aggiunta della colonna company_id: {e}")

def update_database():
    """Aggiorna il database con le nuove tabelle e colonne"""
    db_path = "nis2_platform.db"
    
    # Crea il database se non esiste
    if not os.path.exists(db_path):
        print(f"📁 Creazione nuovo database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🔄 Aggiornamento database...")
        
        # Crea le tabelle
        create_companies_table(cursor)
        create_suppliers_table(cursor)
        create_assessments_table(cursor)
        create_assessment_answers_table(cursor)
        
        # Aggiorna la tabella suppliers se esiste
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='suppliers'")
        if cursor.fetchone():
            update_suppliers_table(cursor)
        
        # Verifica se la colonna evaluation_result esiste
        cursor.execute("PRAGMA table_info(assessments)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'evaluation_result' not in columns:
            print("Aggiungendo colonna evaluation_result alla tabella assessments...")
            cursor.execute("ALTER TABLE assessments ADD COLUMN evaluation_result TEXT")
            print("Colonna evaluation_result aggiunta con successo!")
        else:
            print("Colonna evaluation_result già presente")
        
        # Verifica se la tabella assessment_answers esiste
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='assessment_answers'")
        if not cursor.fetchone():
            print("Creando tabella assessment_answers...")
            cursor.execute("""
                CREATE TABLE assessment_answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    assessment_id INTEGER NOT NULL,
                    question_code TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    created_at TEXT,
                    FOREIGN KEY (assessment_id) REFERENCES assessments (id)
                )
            """)
            print("Tabella assessment_answers creata con successo!")
        else:
            print("Tabella assessment_answers già presente")
        
        conn.commit()
        print("✅ Database aggiornato con successo!")
        
    except Exception as e:
        print(f"❌ Errore nell'aggiornamento del database: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_database()
