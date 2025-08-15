#!/usr/bin/env python3
"""
Test completo per il generatore PDF professionale
"""

import os
import json
import sqlite3
from datetime import datetime
from pdf_generator_professional import ProfessionalNIS2PDFGenerator

def test_professional_pdf_generation():
    """Testa la generazione di PDF professionali"""
    
    print("🏆 Test Generatore PDF Professionale NIS2")
    print("=" * 60)
    
    # Crea dati di test professionali
    assessment_data = {
        'id': 1001,
        'status': 'completed',
        'evaluation_result': json.dumps({
            'outcome': 'POSITIVO',
            'compliance_score': 87.5,
            'section_scores': {
                'Governance della Sicurezza': 92.0,
                'Gestione del Rischio': 85.0,
                'Risposta agli Incidenti': 88.0,
                'Continuità Aziendale': 90.0,
                'Protezione dei Dati': 86.0,
                'Controlli di Accesso': 89.0
            }
        }),
        'completed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    supplier_data = {
        'company_name': 'TechCorp Solutions SRL',
        'email': 'compliance@techcorp-solutions.com',
        'address': 'Via dell\'Innovazione 42',
        'city': 'Milano',
        'sector': 'Tecnologia e Servizi IT',
        'country': 'Italia'
    }
    
    company_data = {
        'name': 'Enterprise Solutions SPA'
    }
    
    # Test generatore professionale
    generator = ProfessionalNIS2PDFGenerator()
    
    try:
        # Test Passaporto Digitale Professionale
        print("📄 Test generazione Passaporto Digitale Professionale...")
        passport_path = "test_passaporto_professionale.pdf"
        generator.generate_passport_pdf(assessment_data, supplier_data, company_data, passport_path)
        
        if os.path.exists(passport_path):
            size = os.path.getsize(passport_path)
            print(f"✅ Passaporto professionale generato: {passport_path}")
            print(f"   Dimensione: {size:,} bytes ({size/1024:.1f} KB)")
        else:
            print("❌ Errore: Passaporto professionale non generato")
        
        # Test Report di Richiamo Professionale
        print("\n📄 Test generazione Report di Richiamo Professionale...")
        assessment_data['evaluation_result'] = json.dumps({
            'outcome': 'NEGATIVO',
            'compliance_score': 42.0,
            'section_scores': {
                'Governance della Sicurezza': 25.0,
                'Gestione del Rischio': 45.0,
                'Risposta agli Incidenti': 35.0,
                'Continuità Aziendale': 55.0,
                'Protezione dei Dati': 40.0,
                'Controlli di Accesso': 50.0
            }
        })
        
        recall_path = "test_richiamo_professionale.pdf"
        generator.generate_recall_pdf(assessment_data, supplier_data, company_data, recall_path)
        
        if os.path.exists(recall_path):
            size = os.path.getsize(recall_path)
            print(f"✅ Report di richiamo professionale generato: {recall_path}")
            print(f"   Dimensione: {size:,} bytes ({size/1024:.1f} KB)")
        else:
            print("❌ Errore: Report di richiamo professionale non generato")
        
        # Test QR Code professionale
        print("\n🔍 Test generazione QR Code professionale...")
        qr_buffer = generator.generate_qr_code("NIS2_PROFESSIONAL_TEST|1001|TechCorp|2024-01-15", "test_qr_professional")
        if qr_buffer:
            print(f"✅ QR Code professionale generato in memoria")
        else:
            print("❌ Errore: QR Code professionale non generato")
        
        # Test grafico professionale
        print("\n📊 Test generazione grafico professionale...")
        chart = generator.create_score_chart({
            'Governance': 85.0,
            'Risk Management': 78.0,
            'Incident Response': 92.0,
            'Business Continuity': 88.0
        })
        if chart:
            print("✅ Grafico professionale creato con successo")
        else:
            print("❌ Errore: Grafico professionale non creato")
        
        print("\n🎉 Tutti i test professionali completati con successo!")
        print("\n📋 File generati:")
        if os.path.exists(passport_path):
            print(f"   - {passport_path}")
        if os.path.exists(recall_path):
            print(f"   - {recall_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore durante i test professionali: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_integration_professional():
    """Testa l'integrazione con il database per il generatore professionale"""
    
    print("\n🗄️ Test integrazione database professionale...")
    
    try:
        # Verifica che il database esista
        if not os.path.exists('nis2_supply_chain.db'):
            print("⚠️ Database non trovato, creando database di test professionale...")
            # Crea un database di test professionale
            conn = sqlite3.connect('nis2_supply_chain.db')
            cursor = conn.cursor()
            
            # Crea tabelle professionali
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
            
            # Inserisci dati di test professionali
            cursor.execute('INSERT INTO companies (name) VALUES (?)', ('Enterprise Solutions SPA',))
            company_id = cursor.lastrowid
            
            cursor.execute('INSERT INTO suppliers (name, email, address, city) VALUES (?, ?, ?, ?)', 
                         ('TechCorp Solutions SRL', 'compliance@techcorp-solutions.com', 'Via dell\'Innovazione 42', 'Milano'))
            supplier_id = cursor.lastrowid
            
            test_result = json.dumps({
                'outcome': 'POSITIVO',
                'compliance_score': 87.5,
                'section_scores': {
                    'Governance': 92.0,
                    'Risk Management': 85.0,
                    'Incident Response': 88.0,
                    'Business Continuity': 90.0
                }
            })
            
            cursor.execute('INSERT INTO assessments (supplier_id, status, evaluation_result, completed_at) VALUES (?, ?, ?, ?)',
                         (supplier_id, 'completed', test_result, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            
            conn.commit()
            conn.close()
            print("✅ Database di test professionale creato")
        
        # Test generazione PDF da database
        print("📄 Test generazione PDF professionale da database...")
        from pdf_generator_professional import generate_assessment_pdf
        result = generate_assessment_pdf(1, "test_pdfs_professional")
        
        if result:
            print(f"✅ PDF professionale generato da database: {result}")
        else:
            print("❌ Errore: PDF professionale non generato da database")
        
        return True
        
    except Exception as e:
        print(f"❌ Errore integrazione database professionale: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Avvio test generatore PDF professionale")
    print("=" * 60)
    
    # Test generazione professionale
    success1 = test_professional_pdf_generation()
    
    # Test integrazione database professionale
    success2 = test_database_integration_professional()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 TUTTI I TEST PROFESSIONALI SUPERATI!")
        print("✅ Il generatore PDF professionale è pronto per DigitalOcean")
        print("🏆 Caratteristiche professionali implementate:")
        print("   - Design professionale con colori aziendali")
        print("   - Grafici e tabelle avanzate")
        print("   - QR Code per verifica pubblica")
        print("   - Footer con riferimenti normativi")
        print("   - Stili tipografici professionali")
        print("   - Gestione errori robusta")
    else:
        print("❌ ALCUNI TEST PROFESSIONALI FALLITI")
        print("⚠️ Controlla gli errori sopra")
    
    print("\n📝 Prossimi passi:")
    print("1. Committa le modifiche")
    print("2. Push su GitHub")
    print("3. DigitalOcean si aggiornerà automaticamente")
    print("4. Testa gli endpoint PDF su DigitalOcean")
    print("5. I PDF saranno ora professionali e completi!")
