import sqlite3
from datetime import datetime

def fix_hardcoded_timestamp():
    """Corregge il timestamp hardcoded nel database"""
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    print("🔧 Correzione timestamp hardcoded...")
    print("=" * 50)
    
    # Trova il record con timestamp hardcoded
    cursor.execute("SELECT id, requirement_id, assessed_at, assessed_by FROM compliance_assessments WHERE assessed_at LIKE '%10:10:10%'")
    hardcoded_record = cursor.fetchone()
    
    if hardcoded_record:
        record_id = hardcoded_record[0]
        requirement_id = hardcoded_record[1]
        old_timestamp = hardcoded_record[2]
        assessed_by = hardcoded_record[3]
        
        print(f"❌ Trovato record con timestamp hardcoded:")
        print(f"  - ID: {record_id}")
        print(f"  - Requirement: {requirement_id}")
        print(f"  - Timestamp attuale: {old_timestamp}")
        print(f"  - Assessed by: {assessed_by}")
        
        # Genera nuovo timestamp corrente
        new_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Aggiorna il record con il timestamp corrente
        cursor.execute("""
            UPDATE compliance_assessments 
            SET assessed_at = ? 
            WHERE id = ?
        """, (new_timestamp, record_id))
        
        conn.commit()
        
        print(f"\n✅ Timestamp corretto:")
        print(f"  - Da: {old_timestamp}")
        print(f"  - A: {new_timestamp}")
        
        # Verifica la correzione
        cursor.execute("SELECT assessed_at FROM compliance_assessments WHERE id = ?", (record_id,))
        updated_record = cursor.fetchone()
        print(f"  - Verifica: {updated_record[0]}")
        
    else:
        print("✅ Nessun timestamp hardcoded trovato da correggere")
    
    conn.close()
    print("\n" + "=" * 50)
    print("✅ Correzione completata!")

if __name__ == "__main__":
    fix_hardcoded_timestamp()
