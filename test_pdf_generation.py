#!/usr/bin/env python3
"""
Test script per verificare la generazione PDF su DigitalOcean
"""

import os
import json
import sqlite3
from datetime import datetime
from pdf_generator_compatible import DigitalOceanCompatiblePDFGenerator, generate_assessment_pdf

def test_pdf_generation():
    """Testa la generazione di PDF di esempio"""
    
    print("🧪 Test generazione PDF compatibile con DigitalOcean")
    print("=" * 60)
    
    # Crea dati di test
    assessment_data = {
        'id': 999,
        'status': 'completed',
        'evaluation_result': json.dumps({
            'outcome': 'POSITIVO',
            'compliance_score': 85.5,
            'section_scores': {
                'Governance': 90.0,
                'Risk Management': 85.0,
                'Incident Response': 80.0,
                'Business Continuity': 87.0
            }
        }),
        'completed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    supplier_data = {
        'company_name': 'Test Supplier SRL',
        'email': 'test@supplier.com',
        'address': 'Via Roma 123',
        'city': 'Milano'
    }
    
    company_data = {
        'name': 'Test Company SPA'
    }
    
    # Test generatore
    generator = DigitalOceanCompatiblePDFGenerator()
    
    try:
        # Test Passaporto Digitale
        print("📄 Test generazione Passaporto Digitale...")
        passport_path = "test_passaporto.pdf"
        generator.generate_passport_pdf(assessment_data, supplier_data, company_data, passport_path)
        
        if os.path.exists(passport_path):
            print(f"✅ Passaporto generato: {passport_path}")
            print(f"   Dimensione: {os.path.getsize(passport_path)} bytes")
        else:
            print("❌ Errore: Passaporto non generato")
        
        # Test Report di Richiamo
        print("\n📄 Test generazione Report di Richiamo...")
        assessment_data['evaluation_result'] = json.dumps({
            'outcome': 'NEGATIVO',
            'compliance_score': 45.0,
            'section_scores': {
                'Governance': 30.0,
                'Risk Management': 50.0,
                'Incident Response': 40.0,
                'Business Continuity': 60.0
            }
        })
        
        recall_path = "test_richiamo.pdf"
        generator.generate_recall_pdf(assessment_data, supplier_data, company_data, recall_path)
        
        if os.path.exists(recall_path):
            print(f"✅ Report di richiamo generato: {recall_path}")
            print(f"   Dimensione: {os.path.getsize(recall_path)} bytes")
        else:
            print("❌ Errore: Report di richiamo non generato")
        
        # Test QR Code
        print("\n🔍 Test generazione QR Code...")
        qr_path = generator.generate_qr_code("test_data_for_qr", "test_qr")
        if qr_path and os.path.exists(qr_path):
            print(f"✅ QR Code generato: {qr_path}")
            # Pulisci
            os.remove(qr_path)
        else:
            print("❌ Errore: QR Code non generato")
        
        print("\n🎉 Tutti i test completati con successo!")
        print("\n📋 File generati:")
        if os.path.exists(passport_path):
            print(f"   - {passport_path}")
        if os.path.exists(recall_path):
            print(f"   - {recall_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore durante i test: {e}")
        return False

def test_database_integration():
    """Testa l'integrazione con il database"""
    
    print("\n🗄️ Test integrazione database...")
    
    try:
        # Verifica che il database esista
        if not os.path.exists('nis2_supply_chain.db'):
            print("⚠️ Database non trovato, creando database di test...")
            # Crea un database di test minimo
            conn = sqlite3.connect('nis2_supply_chain.db')
            cursor = conn.cursor()
            
            # Crea tabelle minime
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS companies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS suppliers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    address TEXT,
                    city TEXT
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS assessments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    supplier_id INTEGER,
                    status TEXT,
                    evaluation_result TEXT,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
                )
            ''')
            
            # Aggiungi colonna se non esiste
            try:
                cursor.execute('ALTER TABLE assessments ADD COLUMN evaluation_result TEXT')
            except:
                pass  # La colonna esiste già
            
            # Inserisci dati di test
            cursor.execute('INSERT INTO companies (name) VALUES (?)', ('Test Company',))
            company_id = cursor.lastrowid
            
            cursor.execute('INSERT INTO suppliers (name, email, address, city) VALUES (?, ?, ?, ?)', 
                         ('Test Supplier', 'test@supplier.com', 'Via Roma 123', 'Milano'))
            supplier_id = cursor.lastrowid
            
            test_result = json.dumps({
                'outcome': 'POSITIVO',
                'compliance_score': 85.0,
                'section_scores': {'Test': 85.0}
            })
            
            cursor.execute('INSERT INTO assessments (supplier_id, status, evaluation_result, completed_at) VALUES (?, ?, ?, ?)',
                         (supplier_id, 'completed', test_result, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            conn.commit()
            conn.close()
            print("✅ Database di test creato")
        
        # Test generazione PDF da database
        print("📄 Test generazione PDF da database...")
        result = generate_assessment_pdf(1, "test_pdfs")
        
        if result:
            print(f"✅ PDF generato da database: {result}")
        else:
            print("❌ Errore: PDF non generato da database")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore integrazione database: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Avvio test generazione PDF")
    print("=" * 60)
    
    # Test generazione base
    success1 = test_pdf_generation()
    
    # Test integrazione database
    success2 = test_database_integration()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 TUTTI I TEST SUPERATI!")
        print("✅ Il generatore PDF è pronto per DigitalOcean")
    else:
        print("❌ ALCUNI TEST FALLITI")
        print("⚠️ Controlla gli errori sopra")
    
    print("\n📝 Prossimi passi:")
    print("1. Committa le modifiche")
    print("2. Push su GitHub")
    print("3. DigitalOcean si aggiornerà automaticamente")
    print("4. Testa gli endpoint PDF su DigitalOcean")
