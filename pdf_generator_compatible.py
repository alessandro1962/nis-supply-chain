import os
import json
import sqlite3
import qrcode
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO

class DigitalOceanCompatiblePDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_styles()
    
    def setup_styles(self):
        """Configura stili per i PDF"""
        self.title_style = ParagraphStyle(
            'Title',
            parent=self.styles['Heading1'],
            fontSize=20,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1e40af'),
            fontName='Helvetica-Bold'
        )
        
        self.subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=15,
            textColor=colors.HexColor('#374151'),
            fontName='Helvetica-Bold'
        )
        
        self.body_style = ParagraphStyle(
            'Body',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=8,
            textColor=colors.HexColor('#1f2937'),
            fontName='Helvetica'
        )
        
        self.alert_style = ParagraphStyle(
            'Alert',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=10,
            textColor=colors.HexColor('#dc2626'),
            backColor=colors.HexColor('#fef2f2'),
            fontName='Helvetica-Bold'
        )
        
        self.success_style = ParagraphStyle(
            'Success',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=10,
            textColor=colors.HexColor('#059669'),
            backColor=colors.HexColor('#f0fdf4'),
            fontName='Helvetica-Bold'
        )
    
    def generate_qr_code(self, data, filename):
        """Genera un QR code e restituisce il percorso"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Usa tempfile per compatibilità cross-platform
            import tempfile
            qr_path = os.path.join(tempfile.gettempdir(), f"{filename}.png")
            qr_img.save(qr_path)
            return qr_path
        except Exception as e:
            print(f"Errore generazione QR: {e}")
            return None
    
    def generate_passport_pdf(self, assessment_data, supplier_data, company_data, output_path):
        """Genera il Passaporto Digitale per fornitori conformi"""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        story = []
        
        # Header
        story.append(Paragraph("🏆 PASSAPORTO DIGITALE NIS2", self.title_style))
        story.append(Spacer(1, 20))
        
        # Messaggio di successo
        success_text = f"""
        <b>CONGRATULAZIONI!</b><br/>
        {supplier_data.get('company_name', 'Il fornitore')} ha superato con successo 
        la valutazione di conformità NIS2 per {company_data.get('name', 'l\'azienda cliente')}.
        """
        story.append(Paragraph(success_text, self.success_style))
        story.append(Spacer(1, 20))
        
        # Informazioni fornitore
        story.append(Paragraph("INFORMAZIONI FORNITORE", self.subtitle_style))
        
        supplier_info = [
            ["🏢 Nome Azienda", supplier_data.get('company_name', 'N/A')],
            ["📧 Email", supplier_data.get('email', 'N/A')],
            ["🏭 Settore", supplier_data.get('sector', 'N/A')],
            ["🌍 Paese", supplier_data.get('country', 'N/A')],
            ["📅 Data Valutazione", assessment_data.get('completed_at', 'N/A')],
            ["🆔 ID Assessment", f"NIS2-{assessment_data.get('id', '000000'):06d}"]
        ]
        
        supplier_table = Table(supplier_info, colWidths=[4*cm, 10*cm])
        supplier_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#374151')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffffff')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db'))
        ]))
        story.append(supplier_table)
        story.append(Spacer(1, 20))
        
        # Risultati valutazione
        if 'evaluation_result' in assessment_data:
            try:
                eval_result = json.loads(assessment_data['evaluation_result'])
                story.append(Paragraph("RISULTATI VALUTAZIONE", self.subtitle_style))
                
                score = eval_result.get('compliance_score', 0)
                story.append(Paragraph(f"<b>Punteggio di Conformità: {score:.1f}%</b>", self.body_style))
                
                if 'section_scores' in eval_result:
                    story.append(Spacer(1, 10))
                    story.append(Paragraph("Dettaglio per Sezioni:", self.body_style))
                    
                    section_data = [["Sezione", "Punteggio"]]
                    for section, score in eval_result['section_scores'].items():
                        section_data.append([section, f"{score:.1f}%"])
                    
                    section_table = Table(section_data, colWidths=[8*cm, 4*cm])
                    section_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f3f4f6')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#374151')),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db'))
                    ]))
                    story.append(section_table)
            except:
                pass
        
        story.append(Spacer(1, 20))
        
        # QR Code per verifica
        story.append(Paragraph("VERIFICA PUBBLICA", self.subtitle_style))
        story.append(Paragraph("Scansiona il QR code per verificare l'autenticità del documento.", self.body_style))
        
        # Genera QR code
        qr_data = f"NIS2_PASSPORT|{assessment_data.get('id', '0')}|{supplier_data.get('company_name', '')}|{assessment_data.get('completed_at', '')}"
        qr_filename = f"qr_passport_{assessment_data.get('id', '0')}"
        qr_path = self.generate_qr_code(qr_data, qr_filename)
        
        if qr_path and os.path.exists(qr_path):
            try:
                qr_img = Image(qr_path, width=3*cm, height=3*cm)
                story.append(Spacer(1, 10))
                story.append(qr_img)
            except Exception as e:
                print(f"Errore aggiunta QR code: {e}")
                # Aggiungi testo alternativo
                story.append(Paragraph(f"QR Code: {qr_data}", self.body_style))
            
            # Pulisci il file temporaneo
            try:
                os.remove(qr_path)
            except:
                pass
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(Paragraph(f"Generato il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}", self.body_style))
        story.append(Paragraph("Piattaforma NIS2 Supply Chain Assessment", self.body_style))
        
        # Costruisci il PDF
        doc.build(story)
        return output_path
    
    def generate_recall_pdf(self, assessment_data, supplier_data, company_data, output_path):
        """Genera il Report di Richiamo per fornitori non conformi"""
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        story = []
        
        # Header
        story.append(Paragraph("⚠️ REPORT DI RICHIAMO NIS2", self.title_style))
        story.append(Spacer(1, 20))
        
        # Alert critico
        alert_text = f"""
        <b>ATTENZIONE CRITICA</b><br/>
        Questo report indica <b>NON CONFORMITÀ</b> alle normative NIS2. 
        È richiesto un <b>intervento immediato</b> per ripristinare la conformità 
        e mantenere l'accordo di fornitura con <b>{company_data.get('name', 'l\'azienda cliente')}</b>.
        """
        story.append(Paragraph(alert_text, self.alert_style))
        story.append(Spacer(1, 20))
        
        # Informazioni fornitore
        story.append(Paragraph("INFORMAZIONI FORNITORE", self.subtitle_style))
        
        supplier_info = [
            ["🏢 Nome Azienda", supplier_data.get('company_name', 'N/A')],
            ["📧 Email", supplier_data.get('email', 'N/A')],
            ["🏭 Settore", supplier_data.get('sector', 'N/A')],
            ["🌍 Paese", supplier_data.get('country', 'N/A')],
            ["📅 Data Valutazione", assessment_data.get('completed_at', 'N/A')],
            ["🆔 ID Assessment", f"NIS2-{assessment_data.get('id', '000000'):06d}"]
        ]
        
        supplier_table = Table(supplier_info, colWidths=[4*cm, 10*cm])
        supplier_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fef2f2')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffffff')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#fecaca'))
        ]))
        story.append(supplier_table)
        story.append(Spacer(1, 20))
        
        # Risultati valutazione
        if 'evaluation_result' in assessment_data:
            try:
                eval_result = json.loads(assessment_data['evaluation_result'])
                story.append(Paragraph("RISULTATI VALUTAZIONE", self.subtitle_style))
                
                score = eval_result.get('compliance_score', 0)
                story.append(Paragraph(f"<b>Punteggio di Conformità: {score:.1f}%</b>", self.alert_style))
                
                if 'section_scores' in eval_result:
                    story.append(Spacer(1, 10))
                    story.append(Paragraph("Aree che richiedono miglioramento:", self.body_style))
                    
                    section_data = [["Sezione", "Punteggio", "Stato"]]
                    for section, score in eval_result['section_scores'].items():
                        status = "✅ Conforme" if score >= 70 else "❌ Non Conforme"
                        section_data.append([section, f"{score:.1f}%", status])
                    
                    section_table = Table(section_data, colWidths=[6*cm, 3*cm, 3*cm])
                    section_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fef2f2')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#fecaca'))
                    ]))
                    story.append(section_table)
            except:
                pass
        
        story.append(Spacer(1, 20))
        
        # Azioni richieste
        story.append(Paragraph("AZIONI RICHIESTE", self.subtitle_style))
        actions_text = """
        <b>Per ripristinare la conformità, è necessario:</b><br/>
        • Implementare le misure di sicurezza mancanti<br/>
        • Aggiornare le policy aziendali<br/>
        • Formare il personale sulle normative NIS2<br/>
        • Effettuare audit di sicurezza regolari<br/>
        • Documentare tutti i processi di sicurezza<br/>
        <br/>
        <b>Timeline:</b> 30 giorni per implementare le correzioni
        """
        story.append(Paragraph(actions_text, self.body_style))
        
        # QR Code per verifica
        story.append(Spacer(1, 20))
        story.append(Paragraph("VERIFICA PUBBLICA", self.subtitle_style))
        story.append(Paragraph("Scansiona il QR code per verificare l'autenticità del documento.", self.body_style))
        
        # Genera QR code
        qr_data = f"NIS2_RECALL|{assessment_data.get('id', '0')}|{supplier_data.get('company_name', '')}|{assessment_data.get('completed_at', '')}"
        qr_filename = f"qr_recall_{assessment_data.get('id', '0')}"
        qr_path = self.generate_qr_code(qr_data, qr_filename)
        
        if qr_path and os.path.exists(qr_path):
            try:
                qr_img = Image(qr_path, width=3*cm, height=3*cm)
                story.append(Spacer(1, 10))
                story.append(qr_img)
            except Exception as e:
                print(f"Errore aggiunta QR code: {e}")
                # Aggiungi testo alternativo
                story.append(Paragraph(f"QR Code: {qr_data}", self.body_style))
            
            # Pulisci il file temporaneo
            try:
                os.remove(qr_path)
            except:
                pass
        
        # Footer
        story.append(Spacer(1, 30))
        story.append(Paragraph(f"Generato il {datetime.now().strftime('%d/%m/%Y alle %H:%M')}", self.body_style))
        story.append(Paragraph("Piattaforma NIS2 Supply Chain Assessment", self.body_style))
        
        # Costruisci il PDF
        doc.build(story)
        return output_path

def generate_assessment_pdf(assessment_id, output_dir="pdfs"):
    """Genera il PDF appropriato per un assessment"""
    # Crea directory se non esiste
    os.makedirs(output_dir, exist_ok=True)
    
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    try:
        # Ottieni dati assessment
        cursor.execute("""
            SELECT a.id, a.status, a.evaluation_result, a.completed_at,
                   s.name, s.email, s.address, s.city,
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
            'address': result[6],
            'city': result[7]
        }
        
        company_data = {
            'name': result[8]
        }
        
        # Determina tipo di PDF da generare
        evaluation_result = json.loads(assessment_data['evaluation_result'])
        outcome = evaluation_result.get('outcome', 'NEGATIVO')
        
        generator = DigitalOceanCompatiblePDFGenerator()
        
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
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM assessments WHERE status = 'completed'")
    assessments = cursor.fetchall()
    
    for (assessment_id,) in assessments:
        try:
            result = generate_assessment_pdf(assessment_id)
            if result:
                print(f"✅ PDF generato per assessment {assessment_id}")
            else:
                print(f"❌ Errore per assessment {assessment_id}")
        except Exception as e:
            print(f"❌ Errore per assessment {assessment_id}: {e}")
    
    conn.close()
