import sqlite3
from datetime import datetime

def check_database_timestamps():
    """Controlla i timestamp nel database per trovare valori hardcoded"""
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    print("🔍 Controllo timestamp nel database...")
    print("=" * 50)
    
    # Controlla la tabella compliance_assessments
    print("\n📋 Tabella compliance_assessments:")
    cursor.execute("SELECT id, requirement_id, assessed_at, assessed_by FROM compliance_assessments LIMIT 10")
    assessments = cursor.fetchall()
    
    for assessment in assessments:
        print(f"ID: {assessment[0]}, Requirement: {assessment[1]}, Assessed at: {assessment[2]}, By: {assessment[3]}")
    
    # Controlla se ci sono timestamp con "10:10:10"
    print("\n🔍 Cerca timestamp con '10:10:10':")
    cursor.execute("SELECT * FROM compliance_assessments WHERE assessed_at LIKE '%10:10:10%'")
    hardcoded_times = cursor.fetchall()
    
    if hardcoded_times:
        print(f"❌ Trovati {len(hardcoded_times)} record con timestamp hardcoded:")
        for record in hardcoded_times:
            print(f"  - ID: {record[0]}, Assessed at: {record[4]}")
    else:
        print("✅ Nessun timestamp hardcoded trovato in compliance_assessments")
    
    # Controlla altre tabelle che potrebbero avere timestamp
    print("\n📋 Controllo altre tabelle:")
    
    # Companies
    cursor.execute("SELECT id, name, created_at FROM companies LIMIT 5")
    companies = cursor.fetchall()
    print("\n🏢 Companies:")
    for company in companies:
        print(f"  ID: {company[0]}, Name: {company[1]}, Created: {company[2]}")
    
    # Suppliers
    cursor.execute("SELECT id, company_name, created_at FROM suppliers LIMIT 5")
    suppliers = cursor.fetchall()
    print("\n🏭 Suppliers:")
    for supplier in suppliers:
        print(f"  ID: {supplier[0]}, Name: {supplier[1]}, Created: {supplier[2]}")
    
    # Assessments
    cursor.execute("SELECT id, supplier_id, completed_at FROM assessments LIMIT 5")
    assessments = cursor.fetchall()
    print("\n📊 Assessments:")
    for assessment in assessments:
        print(f"  ID: {assessment[0]}, Supplier: {assessment[1]}, Completed: {assessment[2]}")
    
    conn.close()
    
    print("\n" + "=" * 50)
    print("✅ Controllo completato!")

if __name__ == "__main__":
    check_database_timestamps()
