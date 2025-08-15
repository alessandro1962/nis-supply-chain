#!/usr/bin/env python3
"""
Test finale per verificare il PDF professionale
"""

from pdf_generator_professional import ProfessionalNIS2PDFGenerator
import json

def test_final_pdf():
    print("🔍 Test finale PDF professionale...")
    
    # Dati di test
    assessment_data = {
        'id': 999,
        'status': 'completed',
        'evaluation_result': json.dumps({
            'compliance_score': 85,
            'section_scores': {
                'Governance della Sicurezza': 85,
                'Gestione del Rischio': 85,
                'Risposta agli Incidenti': 85,
                'Continuità Aziendale': 85,
                'Protezione dei Dati': 85,
                'Controlli di Accesso': 85
            }
        }),
        'completed_at': '2025-01-15 10:30:00'
    }
    
    supplier_data = {
        'company_name': 'Test Company SRL',
        'email': 'test@testcompany.com',
        'sector': 'Tecnologia',
        'country': 'Italia'
    }
    
    company_data = {
        'name': 'Test Client SPA'
    }
    
    # Genera PDF
    generator = ProfessionalNIS2PDFGenerator()
    output_path = 'test_final_professional.pdf'
    
    try:
        generator.generate_passport_pdf(assessment_data, supplier_data, company_data, output_path)
        print(f"✅ PDF generato: {output_path}")
        
        # Verifica contenuto
        with open(output_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        if '🏆' in content or '🏢' in content or '📧' in content:
            print("❌ ERRORE: PDF contiene ancora emoji!")
            return False
        elif 'QR code' in content or 'Scansiona il QR' in content:
            print("❌ ERRORE: PDF contiene ancora riferimenti QR code!")
            return False
        else:
            print("✅ PDF professionale senza emoji e QR code!")
            return True
            
    except Exception as e:
        print(f"❌ Errore: {e}")
        return False

if __name__ == "__main__":
    test_final_pdf()
