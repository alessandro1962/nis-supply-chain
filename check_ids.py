import sqlite3

def check_ids():
    conn = sqlite3.connect('nis2_platform.db')
    cursor = conn.cursor()
    
    try:
        print("=== ID COMPANIES ===")
        cursor.execute("SELECT id, name FROM companies")
        companies = cursor.fetchall()
        for company in companies:
            print(f"ID: {company[0]}, Nome: {company[1]}")
        
        print("\n=== ID SUPPLIERS ===")
        cursor.execute("SELECT id, company_name, company_id FROM suppliers")
        suppliers = cursor.fetchall()
        for supplier in suppliers:
            print(f"ID: {supplier[0]}, Nome: {supplier[1]}, Company ID: {supplier[2]}")
        
    except Exception as e:
        print(f"Errore: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_ids()
