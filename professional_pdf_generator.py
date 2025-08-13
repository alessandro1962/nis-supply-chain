import os
import json
import sqlite3
import qrcode
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.units import mm
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF

class ProfessionalNIS2PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_professional_styles()
    
    def setup_professional_styles(self):
        """Configura stili professionali per i PDF"""
        # Stile titolo principale
        self.main_title_style = ParagraphStyle(
            'MainTitle',
            parent=self.styles['Heading1'],
            fontSize=28,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1e3a8a'),
            fontName='Helvetica-Bold',
            leading=32
        )
        
        # Stile sottotitolo
        self.subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceAfter=20,
            textColor=colors.HexColor('#374151'),
            fontName='Helvetica-Bold',
            leading=22
        )
        
        # Stile sezione
        self.section_style = ParagraphStyle(
            'Section',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=15,
            textColor=colors.HexColor('#1f2937'),
            fontName='Helvetica-Bold',
            leading=18
        )
        
        # Stile corpo testo
        self.body_style = ParagraphStyle(
            'Body',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            textColor=colors.HexColor('#374151'),
            fontName='Helvetica',
            leading=14,
            alignment=TA_JUSTIFY
        )
        
        # Stile alert importante
        self.alert_style = ParagraphStyle(
            'Alert',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            textColor=colors.HexColor('#dc2626'),
            fontName='Helvetica-Bold',
            leading=16,
            backColor=colors.HexColor('#fef2f2'),
            leftIndent=10,
            rightIndent=10,
            borderWidth=1,
            borderColor=colors.HexColor('#fecaca'),
            borderPadding=8
        )
        
        # Stile successo
        self.success_style = ParagraphStyle(
            'Success',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            textColor=colors.HexColor('#059669'),
            fontName='Helvetica-Bold',
            leading=16,
            backColor=colors.HexColor('#f0fdf4'),
            leftIndent=10,
            rightIndent=10,
            borderWidth=1,
            borderColor=colors.HexColor('#bbf7d0'),
            borderPadding=8
        )
        
        # Stile lista
        self.list_style = ParagraphStyle(
            'List',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            textColor=colors.HexColor('#374151'),
            fontName='Helvetica',
            leading=14,
            leftIndent=20
        )
    
    def generate_qr_code(self, data, filename):
        """Genera un QR code professionale"""
        qr = qrcode.QRCode(
            version=1, 
            box_size=12, 
            border=6,
            error_correction=qrcode.constants.ERROR_CORRECT_H
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filename)
        return filename
    
    def create_header_footer(self, canvas, doc, title, is_passport=True):
        """Crea header e footer professionali"""
        # Header
        canvas.saveState()
        canvas.setFillColor(colors.HexColor('#1e3a8a'))
        canvas.rect(0, A4[1]-2*cm, A4[0], 2*cm, fill=1)
        
        # Logo/titolo nel header
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 16)
        canvas.drawCentredString(A4[0]/2, A4[1]-1.2*cm, "NIS2 COMPLIANCE PLATFORM")
        
        canvas.setFont("Helvetica", 10)
        canvas.drawCentredString(A4[0]/2, A4[1]-1.6*cm, title)
        
        # Footer
        canvas.setFillColor(colors.HexColor('#6b7280'))
        canvas.rect(0, 0, A4[0], 1.5*cm, fill=1)
        
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica", 8)
        canvas.drawCentredString(A4[0]/2, 0.8*cm, "Documento generato automaticamente - Piattaforma NIS2 Compliance")
        canvas.drawCentredString(A4[0]/2, 0.4*cm, f"Data emissione: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        canvas.restoreState()
    
    def create_score_chart(self, score):
        """Crea un grafico professionale del punteggio"""
        drawing = Drawing(400, 200)
        
        # Barra del punteggio
        chart = HorizontalLineChart()
        chart.x = 50
        chart.y = 50
        chart.height = 100
        chart.width = 300
        chart.data = [[score]]
        chart.categoryAxis.categoryNames = ['Punteggio NIS2']
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = 100
        chart.valueAxis.valueStep = 20
        chart.lines[0].strokeColor = colors.HexColor('#3b82f6')
        chart.lines[0].strokeWidth = 20
        
        drawing.add(chart)
        return drawing
    
    def generate_passport_pdf(self, assessment_data, supplier_data, company_data, output_path):
        """Genera un Passaporto Digitale professionale per valutazioni positive"""
        doc = SimpleDocTemplate(
            output_path, 
            pagesize=A4, 
            rightMargin=2*cm, 
            leftMargin=2*cm, 
            topMargin=3*cm, 
            bottomMargin=2.5*cm
        )
        story = []
        
        # Titolo principale
        story.append(Paragraph("🏆 PASSAPORTO DIGITALE NIS2", self.main_title_style))
        story.append(Spacer(1, 20))
        
        # Certificazione di conformità
        certification_text = f"""
        <b>ATTESTAZIONE DI CONFORMITÀ</b><br/>
        La presente certifica che <b>{supplier_data['company_name']}</b> ha superato con successo 
        la valutazione di conformità alle normative NIS2 (Network and Information Security 2) 
        richiesta da <b>{company_data.get('name', 'l\'azienda cliente')}</b>.
        """
        story.append(Paragraph(certification_text, self.success_style))
        story.append(Spacer(1, 30))
        
        # Informazioni fornitore con design professionale
        story.append(Paragraph("INFORMAZIONI FORNITORE", self.subtitle_style))
        
        supplier_info = [
            ["🏢 Nome Azienda", supplier_data['company_name']],
            ["📧 Email", supplier_data['email']],
            ["🏭 Settore", supplier_data['sector']],
            ["🌍 Paese", supplier_data['country']],
            ["📅 Data Valutazione", assessment_data['completed_at']],
            ["🆔 ID Assessment", f"NIS2-{assessment_data['id']:06d}"]
        ]
        
        supplier_table = Table(supplier_info, colWidths=[4*cm, 10*cm])
        supplier_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8fafc')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1e3a8a')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
        ]))
        story.append(supplier_table)
        story.append(Spacer(1, 30))
        
        # Risultato valutazione
        evaluation_result = json.loads(assessment_data['evaluation_result'])
        score = evaluation_result.get('final_percentage', 0) * 100
        
        story.append(Paragraph("RISULTATO VALUTAZIONE", self.subtitle_style))
        
        result_text = f"""
        <b>✅ ESITO: CONFORME ALLE NORMATIVE NIS2</b><br/>
        <b>🎯 Punteggio Finale: {score:.1f}%</b><br/>
        <b>📋 Motivazione: {evaluation_result.get('reason', 'N/A')}</b>
        """
        story.append(Paragraph(result_text, self.success_style))
        story.append(Spacer(1, 20))
        
        # Grafico del punteggio
        if score > 0:
            chart = self.create_score_chart(score)
            story.append(chart)
            story.append(Spacer(1, 20))
        
        # Punti di forza
        if 'strengths' in evaluation_result and evaluation_result['strengths']:
            story.append(Paragraph("🏆 PUNTI DI FORZA", self.section_style))
            for i, strength in enumerate(evaluation_result['strengths'], 1):
                story.append(Paragraph(f"• {strength}", self.list_style))
            story.append(Spacer(1, 20))
        
        # Aree di miglioramento
        if 'improvement_areas' in evaluation_result and evaluation_result['improvement_areas']:
            story.append(Paragraph("📈 AREE DI MIGLIORAMENTO", self.section_style))
            for i, area in enumerate(evaluation_result['improvement_areas'], 1):
                story.append(Paragraph(f"• {area}", self.list_style))
            story.append(Spacer(1, 20))
        
        # Raccomandazioni specifiche
        story.append(Paragraph("💡 RACCOMANDAZIONI PER MIGLIORAMENTO", self.section_style))
        recommendations = [
            "Implementare controlli di sicurezza aggiuntivi per rafforzare la conformità",
            "Sviluppare procedure di risposta agli incidenti più robuste",
            "Migliorare la formazione del personale sulla sicurezza informatica",
            "Aggiornare regolarmente le policy di sicurezza aziendali",
            "Conductare audit di sicurezza periodici per mantenere la conformità"
        ]
        for rec in recommendations:
            story.append(Paragraph(f"• {rec}", self.list_style))
        story.append(Spacer(1, 30))
        
        # Validità e note legali
        story.append(Paragraph("📋 VALIDITÀ E NOTE LEGALI", self.section_style))
        validity_text = f"""
        <b>Validità del Documento:</b> Questo passaporto digitale è valido per 12 mesi dalla data di emissione.<br/>
        <b>Rinnovo:</b> È consigliabile completare un nuovo assessment prima della scadenza.<br/>
        <b>Verifica Autenticità:</b> Il QR code permette di verificare l'autenticità del documento.<br/>
        <b>Conformità Normativa:</b> Questo documento attesta la conformità alle normative NIS2 vigenti.
        """
        story.append(Paragraph(validity_text, self.body_style))
        story.append(Spacer(1, 30))
        
        # Genera QR code
        qr_data = f"NIS2_PASSPORT|{assessment_data['id']}|{supplier_data['company_name']}|{assessment_data['completed_at']}|{score:.1f}"
        qr_filename = f"qr_passport_{assessment_data['id']}.png"
        self.generate_qr_code(qr_data, qr_filename)
        
        # Aggiungi QR code con design professionale
        if os.path.exists(qr_filename):
            story.append(Paragraph("🔍 VERIFICA AUTENTICITÀ", self.section_style))
            story.append(Paragraph("Scansiona il QR code per verificare l'autenticità di questo documento:", self.body_style))
            
            qr_img = Image(qr_filename, width=3*cm, height=3*cm)
            story.append(qr_img)
            story.append(Spacer(1, 20))
        
        # Costruisci il PDF con header/footer
        def header_footer(canvas, doc):
            self.create_header_footer(canvas, doc, "PASSAPORTO DIGITALE NIS2", True)
        
        doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
        
        # Pulisci il file QR code
        if os.path.exists(qr_filename):
            os.remove(qr_filename)
        
        return output_path
    
    def generate_recall_pdf(self, assessment_data, supplier_data, company_data, output_path):
        """Genera un Report di Richiamo professionale per valutazioni negative"""
        doc = SimpleDocTemplate(
            output_path, 
            pagesize=A4, 
            rightMargin=2*cm, 
            leftMargin=2*cm, 
            topMargin=3*cm, 
            bottomMargin=2.5*cm
        )
        story = []
        
        # Titolo principale
        story.append(Paragraph("⚠️ REPORT DI RICHIAMO NIS2", self.main_title_style))
        story.append(Spacer(1, 20))
        
        # Alert critico
        alert_text = f"""
        <b>ATTENZIONE CRITICA</b><br/>
        Questo report indica <b>NON CONFORMITÀ</b> alle normative NIS2. 
        È richiesto un <b>intervento immediato</b> per ripristinare la conformità 
        e mantenere l'accordo di fornitura con <b>{company_data.get('name', 'l\'azienda cliente')}</b>.
        """
        story.append(Paragraph(alert_text, self.alert_style))
        story.append(Spacer(1, 30))
        
        # Informazioni fornitore
        story.append(Paragraph("INFORMAZIONI FORNITORE", self.subtitle_style))
        
        supplier_info = [
            ["🏢 Nome Azienda", supplier_data['company_name']],
            ["📧 Email", supplier_data['email']],
            ["🏭 Settore", supplier_data['sector']],
            ["🌍 Paese", supplier_data['country']],
            ["📅 Data Valutazione", assessment_data['completed_at']],
            ["🆔 ID Assessment", f"NIS2-{assessment_data['id']:06d}"]
        ]
        
        supplier_table = Table(supplier_info, colWidths=[4*cm, 10*cm])
        supplier_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fef2f2')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#991b1b')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#fecaca')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#fef2f2')])
        ]))
        story.append(supplier_table)
        story.append(Spacer(1, 30))
        
        # Risultato valutazione
        evaluation_result = json.loads(assessment_data['evaluation_result'])
        score = evaluation_result.get('final_percentage', 0) * 100
        
        story.append(Paragraph("RISULTATO VALUTAZIONE", self.subtitle_style))
        
        result_text = f"""
        <b>❌ ESITO: NON CONFORME ALLE NORMATIVE NIS2</b><br/>
        <b>🎯 Punteggio Finale: {score:.1f}%</b><br/>
        <b>📋 Motivazione: {evaluation_result.get('reason', 'N/A')}</b>
        """
        story.append(Paragraph(result_text, self.alert_style))
        story.append(Spacer(1, 20))
        
        # Grafico del punteggio
        if score > 0:
            chart = self.create_score_chart(score)
            story.append(chart)
            story.append(Spacer(1, 20))
        
        # AZIONI CORRETTIVE DETTAGLIATE
        story.append(Paragraph("🔧 AZIONI CORRETTIVE RICHIESTE", self.subtitle_style))
        
        # Azioni correttive specifiche per NIS2
        corrective_actions = [
            {
                "area": "Governance e Leadership",
                "actions": [
                    "Nominare un responsabile della sicurezza informatica (CISO)",
                    "Implementare un framework di governance della sicurezza",
                    "Definire policy di sicurezza aziendali complete",
                    "Stabilire un comitato di sicurezza con riunioni regolari"
                ]
            },
            {
                "area": "Gestione del Rischio",
                "actions": [
                    "Conductare una valutazione completa dei rischi informatici",
                    "Implementare un sistema di gestione dei rischi",
                    "Definire procedure di escalation per incidenti critici",
                    "Stabilire metriche di monitoraggio del rischio"
                ]
            },
            {
                "area": "Sicurezza delle Operazioni",
                "actions": [
                    "Implementare controlli di accesso robusti (MFA)",
                    "Aggiornare regolarmente sistemi e software",
                    "Implementare backup e disaster recovery",
                    "Definire procedure di gestione delle vulnerabilità"
                ]
            },
            {
                "area": "Business Continuity",
                "actions": [
                    "Sviluppare un piano di business continuity",
                    "Testare regolarmente i piani di disaster recovery",
                    "Implementare ridondanza dei sistemi critici",
                    "Definire procedure di comunicazione in emergenza"
                ]
            },
            {
                "area": "Conformità e Audit",
                "actions": [
                    "Implementare controlli di conformità automatizzati",
                    "Conductare audit di sicurezza interni regolari",
                    "Mantenere documentazione completa delle procedure",
                    "Implementare monitoraggio continuo della conformità"
                ]
            }
        ]
        
        for area in corrective_actions:
            story.append(Paragraph(f"📋 {area['area']}", self.section_style))
            for action in area['actions']:
                story.append(Paragraph(f"• {action}", self.list_style))
            story.append(Spacer(1, 15))
        
        # Aree di miglioramento specifiche dall'assessment
        if 'improvement_areas' in evaluation_result and evaluation_result['improvement_areas']:
            story.append(Paragraph("🎯 AREE SPECIFICHE DI MIGLIORAMENTO", self.section_style))
            for i, area in enumerate(evaluation_result['improvement_areas'], 1):
                story.append(Paragraph(f"{i}. {area}", self.list_style))
            story.append(Spacer(1, 20))
        
        # TIMELINE E ULTIMATUM
        deadline_date = datetime.now() + timedelta(days=60)
        story.append(Paragraph("⏰ TIMELINE E ULTIMATUM", self.subtitle_style))
        
        timeline_text = f"""
        <b>📅 Scadenza Critica: {deadline_date.strftime('%d/%m/%Y')}</b><br/>
        <b>⚠️ CONSEGUENZE DEL MANCATO RISPETTO:</b><br/>
        • Possibile sospensione dell'accordo di fornitura<br/>
        • Rischio di violazione contrattuale<br/>
        • Potenziali sanzioni normative<br/>
        • Danno alla reputazione aziendale<br/><br/>
        <b>✅ AZIONI IMMEDIATE RICHIESTE:</b><br/>
        1. Iniziare implementazione azioni correttive entro 7 giorni<br/>
        2. Nominare un responsabile del progetto di compliance<br/>
        3. Completare nuovo assessment entro 60 giorni<br/>
        4. Fornire aggiornamenti settimanali sui progressi
        """
        story.append(Paragraph(timeline_text, self.alert_style))
        story.append(Spacer(1, 30))
        
        # PROSSIMI PASSI DETTAGLIATI
        story.append(Paragraph("🚀 PIANO D'AZIONE DETTAGLIATO", self.subtitle_style))
        
        action_plan = [
            {
                "step": "1. Analisi e Pianificazione (Settimana 1-2)",
                "actions": [
                    "Conductare gap analysis completa",
                    "Definire roadmap di implementazione",
                    "Assegnare responsabilità e budget",
                    "Stabilire KPI di progresso"
                ]
            },
            {
                "step": "2. Implementazione Prioritaria (Settimana 3-6)",
                "actions": [
                    "Implementare controlli di sicurezza critici",
                    "Aggiornare policy e procedure",
                    "Formare il personale chiave",
                    "Implementare monitoraggio base"
                ]
            },
            {
                "step": "3. Consolidamento (Settimana 7-8)",
                "actions": [
                    "Testare e validare implementazioni",
                    "Documentare procedure e controlli",
                    "Conductare audit interno",
                    "Preparare per assessment finale"
                ]
            },
            {
                "step": "4. Assessment Finale (Settimana 9-10)",
                "actions": [
                    "Completare nuovo assessment NIS2",
                    "Verificare conformità completa",
                    "Ottenere certificazione finale",
                    "Mantenere conformità continua"
                ]
            }
        ]
        
        for step in action_plan:
            story.append(Paragraph(f"<b>{step['step']}</b>", self.section_style))
            for action in step['actions']:
                story.append(Paragraph(f"• {action}", self.list_style))
            story.append(Spacer(1, 15))
        
        # Genera QR code
        qr_data = f"NIS2_RECALL|{assessment_data['id']}|{supplier_data['company_name']}|{assessment_data['completed_at']}|{score:.1f}"
        qr_filename = f"qr_recall_{assessment_data['id']}.png"
        self.generate_qr_code(qr_data, qr_filename)
        
        # Aggiungi QR code
        if os.path.exists(qr_filename):
            story.append(Paragraph("🔍 VERIFICA AUTENTICITÀ", self.section_style))
            story.append(Paragraph("Scansiona il QR code per verificare l'autenticità di questo documento:", self.body_style))
            
            qr_img = Image(qr_filename, width=3*cm, height=3*cm)
            story.append(qr_img)
            story.append(Spacer(1, 20))
        
        # Costruisci il PDF con header/footer
        def header_footer(canvas, doc):
            self.create_header_footer(canvas, doc, "REPORT DI RICHIAMO NIS2", False)
        
        doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
        
        # Pulisci il file QR code
        if os.path.exists(qr_filename):
            os.remove(qr_filename)
        
        return output_path

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
        
        generator = ProfessionalNIS2PDFGenerator()
        
        if outcome == 'POSITIVO':
            filename = f"passaporto_nis2_professionale_{assessment_id}.pdf"
            output_path = os.path.join(output_dir, filename)
            generator.generate_passport_pdf(assessment_data, supplier_data, company_data, output_path)
            print(f"✅ Generato passaporto digitale professionale: {output_path}")
        else:
            filename = f"richiamo_nis2_professionale_{assessment_id}.pdf"
            output_path = os.path.join(output_dir, filename)
            generator.generate_recall_pdf(assessment_data, supplier_data, company_data, output_path)
            print(f"✅ Generato report di richiamo professionale: {output_path}")
        
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
    
    print(f"Generando PDF professionali per {len(assessment_ids)} assessment...")
    for assessment_id in assessment_ids:
        generate_assessment_pdf(assessment_id)
