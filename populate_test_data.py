import sqlite3
from datetime import datetime

def populate_test_data():
    conn = sqlite3.connect('nis2_platform.db')
    cursor = conn.cursor()
    
    try:
        # Crea una azienda di test
        cursor.execute("""
            INSERT INTO companies (
                name, admin_email, sector, vat_number, fiscal_code, 
                address, city, postal_code, country, phone, 
                contact_person, contact_phone, contact_email, 
                company_size, industry, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'Azienda Demo SRL', 'demo@company.com', 'IT', '12345678901', 'DEMO12345678',
            'Via Roma 123', 'Milano', '20100', 'Italia', '+39 02 1234567',
            'Mario Rossi', '+39 333 1234567', 'mario.rossi@company.com',
            'Media', 'Tecnologia', datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        company_id = cursor.lastrowid
        print(f"Azienda creata con ID: {company_id}")
        
        # Crea un fornitore di test
        cursor.execute("""
            INSERT INTO suppliers (
                company_id, company_name, email, sector, country, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            company_id, 'Fornitore Test', 'test@fornitore.com', 'IT', 'Italia',
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))
        
        supplier_id = cursor.lastrowid
        print(f"Fornitore creato con ID: {supplier_id}")
        
        conn.commit()
        print("Dati di test creati con successo!")
        
        return company_id, supplier_id
        
    except Exception as e:
        print(f"Errore: {e}")
        import traceback
        traceback.print_exc()
        return None, None
    finally:
        conn.close()

if __name__ == "__main__":
    populate_test_data()
