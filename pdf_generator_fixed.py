import os
import json
import sqlite3
import qrcode
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

class NIS2PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
    
    def setup_custom_styles(self):
        """Configura stili personalizzati per i PDF"""
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1e40af')
        )
        
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.HexColor('#374151')
        )
        
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            textColor=colors.HexColor('#1f2937')
        )
        
        self.alert_style = ParagraphStyle(
            'AlertStyle',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            textColor=colors.HexColor('#dc2626'),
            backColor=colors.HexColor('#fef2f2')
        )
    
    def generate_qr_code(self, data, filename):
        """Genera un QR code con i dati specificati"""
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filename)
        return filename
    
    def generate_passport_pdf(self, assessment_data, supplier_data, company_data, output_path):
        """Genera il Passaporto Digitale per valutazioni positive"""
        doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        story = []
        
        # Header con logo e titolo
        story.append(Paragraph("PASSAPORTO DIGITALE NIS2", self.title_style))
        story.append(Spacer(1, 20))
        
        # Informazioni fornitore
        story.append(Paragraph("INFORMAZIONI FORNITORE", self.subtitle_style))
        supplier_info = [
            ["Nome Azienda:", supplier_data['company_name']],
            ["Email:", supplier_data['email']],
            ["Settore:", supplier_data['sector']],
            ["Paese:", supplier_data['country']],
            ["Data Valutazione:", assessment_data['completed_at']]
        ]
        
        supplier_table = Table(supplier_info, colWidths=[3*cm, 10*cm])
        supplier_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#374151')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db'))
        ]))
        story.append(supplier_table)
        story.append(Spacer(1, 20))
        
        # Risultato valutazione
        evaluation_result = json.loads(assessment_data['evaluation_result'])
        score = evaluation_result.get('final_percentage', 0) * 100
        
        story.append(Paragraph("RISULTATO VALUTAZIONE", self.subtitle_style))
        story.append(Paragraph(f"<b>ESITO: CONFORME</b>", self.body_style))
        story.append(Paragraph(f"<b>Punteggio: {score:.1f}%</b>", self.body_style))
        story.append(Paragraph(f"<b>Motivazione: {evaluation_result.get('reason', 'N/A')}</b>", self.body_style))
        story.append(Spacer(1, 20))
        
        # Barra punteggio
        score_bar = self.create_score_bar(score)
        story.append(score_bar)
        story.append(Spacer(1, 20))
        
        # Punti di forza
        if 'strengths' in evaluation_result and evaluation_result['strengths']:
            story.append(Paragraph("PUNTI DI FORZA", self.subtitle_style))
            for strength in evaluation_result['strengths']:
                story.append(Paragraph(f"• {strength}", self.body_style))
            story.append(Spacer(1, 20))
        
        # Aree di miglioramento
        if 'improvement_areas' in evaluation_result and evaluation_result['improvement_areas']:
            story.append(Paragraph("AREE DI MIGLIORAMENTO", self.subtitle_style))
            for area in evaluation_result['improvement_areas']:
                story.append(Paragraph(f"• {area}", self.body_style))
            story.append(Spacer(1, 20))
        
        # Validità e note
        story.append(Paragraph("VALIDITÀ E NOTE", self.subtitle_style))
        story.append(Paragraph("Questo passaporto digitale attesta la conformità del fornitore alle normative NIS2. La validità è di 12 mesi dalla data di emissione.", self.body_style))
        story.append(Paragraph("Il QR code permette di verificare l'autenticità del documento.", self.body_style))
        
        # Genera QR code
        qr_data = f"NIS2_PASSPORT|{assessment_data['id']}|{supplier_data['company_name']}|{assessment_data['completed_at']}"
        qr_filename = f"qr_passport_{assessment_data['id']}.png"
        self.generate_qr_code(qr_data, qr_filename)
        
        # Aggiungi QR code al PDF
        if os.path.exists(qr_filename):
            qr_img = Image(qr_filename, width=2*cm, height=2*cm)
            story.append(Spacer(1, 20))
            story.append(qr_img)
        
        # Costruisci il PDF
        doc.build(story)
        
        # Pulisci il file QR code dopo aver costruito il PDF
        if os.path.exists(qr_filename):
            os.remove(qr_filename)
        
        return output_path
    
    def generate_recall_pdf(self, assessment_data, supplier_data, company_data, output_path):
        """Genera il Report di Richiamo per valutazioni negative"""
        doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
        story = []
        
        # Header con logo e titolo
        story.append(Paragraph("REPORT DI RICHIAMO NIS2", self.title_style))
        story.append(Spacer(1, 20))
        
        # Alert importante
        alert_text = "ATTENZIONE: Questo report indica non conformità alle normative NIS2. È richiesto un intervento immediato."
        story.append(Paragraph(alert_text, self.alert_style))
        story.append(Spacer(1, 20))
        
        # Informazioni fornitore
        story.append(Paragraph("INFORMAZIONI FORNITORE", self.subtitle_style))
        supplier_info = [
            ["Nome Azienda:", supplier_data['company_name']],
            ["Email:", supplier_data['email']],
            ["Settore:", supplier_data['sector']],
            ["Paese:", supplier_data['country']],
            ["Data Valutazione:", assessment_data['completed_at']]
        ]
        
        supplier_table = Table(supplier_info, colWidths=[3*cm, 10*cm])
        supplier_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fef2f2')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#991b1b')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#fecaca'))
        ]))
        story.append(supplier_table)
        story.append(Spacer(1, 20))
        
        # Risultato valutazione
        evaluation_result = json.loads(assessment_data['evaluation_result'])
        score = evaluation_result.get('final_percentage', 0) * 100
        
        story.append(Paragraph("RISULTATO VALUTAZIONE", self.subtitle_style))
        story.append(Paragraph(f"<b>ESITO: NON CONFORME</b>", self.body_style))
        story.append(Paragraph(f"<b>Punteggio: {score:.1f}%</b>", self.body_style))
        story.append(Paragraph(f"<b>Motivazione: {evaluation_result.get('reason', 'N/A')}</b>", self.body_style))
        story.append(Spacer(1, 20))
        
        # Azioni correttive richieste
        story.append(Paragraph("AZIONI CORRETTIVE RICHIESTE", self.subtitle_style))
        if 'improvement_areas' in evaluation_result and evaluation_result['improvement_areas']:
            for i, area in enumerate(evaluation_result['improvement_areas'], 1):
                story.append(Paragraph(f"{i}. {area}", self.body_style))
        else:
            story.append(Paragraph("Sono richiesti interventi generali per migliorare la conformità NIS2.", self.body_style))
        story.append(Spacer(1, 20))
        
        # Ultimatum
        deadline_date = datetime.now() + timedelta(days=60)
        story.append(Paragraph("ULTIMATUM", self.subtitle_style))
        ultimatum_text = f"""
        <b>ATTENZIONE:</b> In caso di mancato miglioramento entro il {deadline_date.strftime('%d/%m/%Y')}, 
        potrebbe essere compromesso l'accordo di fornitura con {company_data.get('name', 'l\'azienda cliente')}.
        
        È obbligatorio completare un nuovo assessment entro 60 giorni dalla data di emissione di questo report.
        """
        story.append(Paragraph(ultimatum_text, self.alert_style))
        story.append(Spacer(1, 20))
        
        # Prossimi passi
        story.append(Paragraph("PROSSIMI PASSI", self.subtitle_style))
        steps = [
            "1. Analizzare le aree di non conformità identificate",
            "2. Implementare le azioni correttive necessarie",
            "3. Completare un nuovo assessment entro 60 giorni",
            "4. Inviare il nuovo report alla società cliente",
            "5. Mantenere aggiornate le procedure di sicurezza"
        ]
        for step in steps:
            story.append(Paragraph(step, self.body_style))
        
        # Genera QR code
        qr_data = f"NIS2_RECALL|{assessment_data['id']}|{supplier_data['company_name']}|{assessment_data['completed_at']}"
        qr_filename = f"qr_recall_{assessment_data['id']}.png"
        self.generate_qr_code(qr_data, qr_filename)
        
        # Aggiungi QR code al PDF
        if os.path.exists(qr_filename):
            qr_img = Image(qr_filename, width=2*cm, height=2*cm)
            story.append(Spacer(1, 20))
            story.append(qr_img)
        
        # Costruisci il PDF
        doc.build(story)
        
        # Pulisci il file QR code dopo aver costruito il PDF
        if os.path.exists(qr_filename):
            os.remove(qr_filename)
        
        return output_path
    
    def create_score_bar(self, score):
        """Crea una barra visiva del punteggio"""
        if score >= 80:
            status = "Eccellente"
        elif score >= 60:
            status = "Buono"
        else:
            status = "Da migliorare"
        
        return Paragraph(f"<b>Punteggio: {score:.1f}% ({status})</b>", self.body_style)

# Funzione di utilità per generare PDF
def generate_assessment_pdf(assessment_id, output_dir="pdfs"):
    """Genera il PDF appropriato per un assessment"""
    # Crea directory se non esiste
    os.makedirs(output_dir, exist_ok=True)
    
    conn = sqlite3.connect('nis2_platform.db')
    cursor = conn.cursor()
    
    try:
        # Ottieni dati assessment
        cursor.execute("""
            SELECT a.id, a.status, a.evaluation_result, a.completed_at,
                   s.company_name, s.email, s.sector, s.country,
                   c.name as company_name
            FROM assessments a
            JOIN suppliers s ON a.supplier_id = s.id
            JOIN companies c ON s.company_id = c.id
            WHERE a.id = ?
        """, (assessment_id,))
        
        result = cursor.fetchone()
        if not result:
            raise Exception(f"Assessment {assessment_id} non trovato")
        
        assessment_data = {
            'id': result[0],
            'status': result[1],
            'evaluation_result': result[2],
            'completed_at': result[3]
        }
        
        supplier_data = {
            'company_name': result[4],
            'email': result[5],
            'sector': result[6],
            'country': result[7]
        }
        
        company_data = {
            'name': result[8]
        }
        
        # Determina tipo di PDF da generare
        evaluation_result = json.loads(assessment_data['evaluation_result'])
        outcome = evaluation_result.get('outcome', 'NEGATIVO')
        
        generator = NIS2PDFGenerator()
        
        if outcome == 'POSITIVO':
            filename = f"passaporto_nis2_{assessment_id}.pdf"
            output_path = os.path.join(output_dir, filename)
            generator.generate_passport_pdf(assessment_data, supplier_data, company_data, output_path)
            print(f"✅ Generato passaporto digitale: {output_path}")
        else:
            filename = f"richiamo_nis2_{assessment_id}.pdf"
            output_path = os.path.join(output_dir, filename)
            generator.generate_recall_pdf(assessment_data, supplier_data, company_data, output_path)
            print(f"✅ Generato report di richiamo: {output_path}")
        
        return output_path
        
    except Exception as e:
        print(f"❌ Errore generazione PDF: {e}")
        return None
    finally:
        conn.close()

if __name__ == "__main__":
    # Test: genera PDF per tutti gli assessment completati
    conn = sqlite3.connect('nis2_platform.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM assessments WHERE status = 'completed'")
    assessment_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    print(f"Generando PDF per {len(assessment_ids)} assessment...")
    for assessment_id in assessment_ids:
        generate_assessment_pdf(assessment_id)
