import os
import json
import sqlite3
import qrcode
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics import renderPDF
from io import BytesIO
import tempfile

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
            textColor=colors.HexColor('#1e40af'),
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
        
        # Stile corpo testo
        self.body_style = ParagraphStyle(
            'Body',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=10,
            textColor=colors.HexColor('#1f2937'),
            fontName='Helvetica',
            leading=14
        )
        
        # Stile successo
        self.success_style = ParagraphStyle(
            'Success',
            parent=self.styles['Normal'],
            fontSize=14,
            spaceAfter=15,
            textColor=colors.HexColor('#059669'),
            backColor=colors.HexColor('#f0fdf4'),
            fontName='Helvetica-Bold',
            leading=18,
            borderWidth=1,
            borderColor=colors.HexColor('#bbf7d0'),
            borderPadding=12,
            alignment=TA_CENTER
        )
        
        # Stile tabella header
        self.table_header_style = ParagraphStyle(
            'TableHeader',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.white,
            fontName='Helvetica-Bold',
            alignment=TA_CENTER
        )
        
        # Stile tabella corpo
        self.table_body_style = ParagraphStyle(
            'TableBody',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#1f2937'),
            fontName='Helvetica',
            alignment=TA_LEFT
        )
        
        # Stile footer
        self.footer_style = ParagraphStyle(
            'Footer',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#6b7280'),
            fontName='Helvetica',
            alignment=TA_CENTER,
            spaceBefore=20
        )

    def create_header_logo(self):
        """Crea un header con logo e design professionale"""
        # Disegno per il logo/header
        drawing = Drawing(400, 80)
        
        # Rettangolo di sfondo blu
        drawing.add(String(200, 60, "NIS2 SUPPLY CHAIN", 
                          fontSize=24, fillColor=colors.HexColor('#1e40af'), 
                          fontName='Helvetica-Bold', textAnchor='middle'))
        drawing.add(String(200, 40, "ASSESSMENT PLATFORM", 
                          fontSize=14, fillColor=colors.HexColor('#6b7280'), 
                          fontName='Helvetica', textAnchor='middle'))
        drawing.add(String(200, 20, "Certificazione Conformità", 
                          fontSize=12, fillColor=colors.HexColor('#9ca3af'), 
                          fontName='Helvetica', textAnchor='middle'))
        
        return drawing

    def create_score_chart(self, section_scores):
        """Crea un grafico professionale dei punteggi"""
        try:
            drawing = Drawing(400, 250)
            
            # Crea grafico a barre orizzontali
            chart = HorizontalLineChart()
            chart.x = 80
            chart.y = 50
            chart.height = 150
            chart.width = 280
            
            # Prepara i dati
            labels = list(section_scores.keys())
            data = [list(section_scores.values())]
            
            chart.data = data
            chart.categoryAxis.categoryNames = labels
            chart.valueAxis.valueMin = 0
            chart.valueAxis.valueMax = 100
            chart.valueAxis.valueStep = 20
            
            # Stili del grafico professionali
            chart.bars[0].fillColor = colors.HexColor('#3b82f6')
            chart.bars[0].strokeColor = colors.HexColor('#1d4ed8')
            chart.bars[0].strokeWidth = 1
            
            # Aggiungi titolo al grafico
            drawing.add(String(200, 220, "Punteggi per Sezione", 
                              fontSize=14, fillColor=colors.HexColor('#1e40af'), 
                              fontName='Helvetica-Bold', textAnchor='middle'))
            
            drawing.add(chart)
            return drawing
        except Exception as e:
            print(f"Errore creazione grafico: {e}")
            return None

    def create_compliance_indicator(self, score):
        """Crea un indicatore visivo del livello di conformità"""
        drawing = Drawing(200, 60)
        
        # Colore basato sul punteggio
        if score >= 90:
            color = colors.HexColor('#059669')  # Verde scuro
            level = "ECCELLENTE"
        elif score >= 80:
            color = colors.HexColor('#10b981')  # Verde
            level = "OTTIMI"
        elif score >= 70:
            color = colors.HexColor('#3b82f6')  # Blu
            level = "BUONI"
        elif score >= 50:
            color = colors.HexColor('#f59e0b')  # Giallo
            level = "SUFFICIENTI"
        else:
            color = colors.HexColor('#dc2626')  # Rosso
            level = "INSUFFICIENTI"
        
        # Cerchio indicatore
        drawing.add(String(100, 35, f"{score:.0f}%", 
                          fontSize=16, fillColor=color, 
                          fontName='Helvetica-Bold', textAnchor='middle'))
        drawing.add(String(100, 15, level, 
                          fontSize=10, fillColor=colors.HexColor('#6b7280'), 
                          fontName='Helvetica', textAnchor='middle'))
        
        return drawing

    def create_risk_matrix(self, section_scores):
        """Crea una matrice di rischio professionale"""
        try:
            drawing = Drawing(400, 200)
            
            # Titolo
            drawing.add(String(200, 180, "Matrice di Rischio per Sezione", 
                              fontSize=14, fillColor=colors.HexColor('#1e40af'), 
                              fontName='Helvetica-Bold', textAnchor='middle'))
            
            y_pos = 150
            for section, score in section_scores.items():
                # Colore basato sul rischio
                if score >= 70:
                    color = colors.HexColor('#059669')
                    risk = "BASSO"
                elif score >= 50:
                    color = colors.HexColor('#f59e0b')
                    risk = "MEDIO"
                else:
                    color = colors.HexColor('#dc2626')
                    risk = "ALTO"
                
                # Nome sezione
                drawing.add(String(50, y_pos, section[:25] + "..." if len(section) > 25 else section, 
                                  fontSize=9, fillColor=colors.HexColor('#374151'), 
                                  fontName='Helvetica', textAnchor='start'))
                
                # Punteggio
                drawing.add(String(250, y_pos, f"{score:.0f}%", 
                                  fontSize=9, fillColor=color, 
                                  fontName='Helvetica-Bold', textAnchor='middle'))
                
                # Livello rischio
                drawing.add(String(320, y_pos, risk, 
                                  fontSize=9, fillColor=color, 
                                  fontName='Helvetica', textAnchor='middle'))
                
                y_pos -= 20
                if y_pos < 50:
                    break
            
            return drawing
        except Exception as e:
            print(f"Errore creazione matrice rischio: {e}")
            return None

    def analyze_specific_actions(self, assessment_data):
        """Analizza le risposte specifiche del questionario e genera azioni concrete"""
        try:
            eval_result = json.loads(assessment_data.get('evaluation_result', '{}'))
            section_scores = eval_result.get('section_scores', {})
            
            specific_actions = []
            
            # Analizza ogni sezione e genera azioni specifiche
            for section, score in section_scores.items():
                if score < 70:  # Sezione non conforme
                    if section == "Governance della Sicurezza":
                        if score < 50:
                            specific_actions.append("• <b>Governance Critica:</b> Nominare un CISO e implementare un comitato di sicurezza aziendale")
                            specific_actions.append("• <b>Policy:</b> Creare policy di sicurezza aziendali complete e approvate dal board")
                        else:
                            specific_actions.append("• <b>Governance:</b> Rafforzare il framework di governance della sicurezza esistente")
                    
                    elif section == "Gestione del Rischio":
                        if score < 50:
                            specific_actions.append("• <b>Risk Assessment:</b> Eseguire una valutazione completa dei rischi di sicurezza")
                            specific_actions.append("• <b>Risk Register:</b> Creare un registro dei rischi con piani di mitigazione")
                        else:
                            specific_actions.append("• <b>Risk Management:</b> Aggiornare i processi di gestione del rischio")
                    
                    elif section == "Risposta agli Incidenti":
                        if score < 50:
                            specific_actions.append("• <b>Incident Response Plan:</b> Sviluppare un piano di risposta agli incidenti completo")
                            specific_actions.append("• <b>CSIRT:</b> Creare un team di risposta agli incidenti di sicurezza")
                        else:
                            specific_actions.append("• <b>Incident Response:</b> Migliorare le procedure di risposta agli incidenti esistenti")
                    
                    elif section == "Continuità Aziendale":
                        if score < 50:
                            specific_actions.append("• <b>BCP:</b> Sviluppare un piano di continuità aziendale dettagliato")
                            specific_actions.append("• <b>DRP:</b> Creare un piano di disaster recovery per i sistemi critici")
                        else:
                            specific_actions.append("• <b>Business Continuity:</b> Aggiornare i piani di continuità esistenti")
                    
                    elif section == "Protezione dei Dati":
                        if score < 50:
                            specific_actions.append("• <b>Data Classification:</b> Implementare un sistema di classificazione dei dati")
                            specific_actions.append("• <b>Encryption:</b> Crittografare i dati sensibili in transito e a riposo")
                        else:
                            specific_actions.append("• <b>Data Protection:</b> Rafforzare le misure di protezione dati esistenti")
                    
                    elif section == "Controlli di Accesso":
                        if score < 50:
                            specific_actions.append("• <b>IAM:</b> Implementare un sistema di gestione identità e accessi")
                            specific_actions.append("• <b>MFA:</b> Attivare l'autenticazione multi-fattore per tutti gli utenti")
                        else:
                            specific_actions.append("• <b>Access Control:</b> Migliorare i controlli di accesso esistenti")
            
            # Se non ci sono azioni specifiche, aggiungi azioni generali ma concrete
            if not specific_actions:
                specific_actions = [
                    "• <b>Assessment Completo:</b> Eseguire una valutazione dettagliata delle lacune di sicurezza",
                    "• <b>Roadmap:</b> Sviluppare una roadmap di implementazione delle misure NIS2",
                    "• <b>Budget:</b> Allocare budget specifico per le iniziative di sicurezza",
                    "• <b>Timeline:</b> Stabilire scadenze concrete per ogni misura da implementare"
                ]
            
            return specific_actions
            
        except Exception as e:
            print(f"Errore analisi azioni specifiche: {e}")
            return [
                "• <b>Assessment Completo:</b> Eseguire una valutazione dettagliata delle lacune di sicurezza",
                "• <b>Roadmap:</b> Sviluppare una roadmap di implementazione delle misure NIS2"
            ]

    def generate_improvement_recommendations(self, section_scores):
        """Genera raccomandazioni specifiche per il miglioramento continuo"""
        recommendations = []
        
        for section, score in section_scores.items():
            if score >= 90:
                # Eccellente - raccomandazioni per mantenere l'eccellenza
                if section == "Governance della Sicurezza":
                    recommendations.append("• <b>Governance Eccellente:</b> Considerare l'implementazione di framework avanzati come ISO 27001 o NIST Cybersecurity Framework")
                elif section == "Gestione del Rischio":
                    recommendations.append("• <b>Risk Management Avanzato:</b> Implementare analisi predittive e machine learning per la gestione del rischio")
                elif section == "Risposta agli Incidenti":
                    recommendations.append("• <b>Incident Response Avanzato:</b> Sviluppare capacità di threat hunting e intelligence sharing")
                elif section == "Continuità Aziendale":
                    recommendations.append("• <b>Business Continuity Avanzato:</b> Implementare test di disaster recovery automatizzati e simulazioni avanzate")
                elif section == "Protezione dei Dati":
                    recommendations.append("• <b>Data Protection Avanzato:</b> Considerare l'implementazione di DLP (Data Loss Prevention) e zero-trust architecture")
                elif section == "Controlli di Accesso":
                    recommendations.append("• <b>Access Control Avanzato:</b> Implementare soluzioni di behavioral analytics e adaptive authentication")
            
            elif score >= 80:
                # Ottimo - raccomandazioni per raggiungere l'eccellenza
                if section == "Governance della Sicurezza":
                    recommendations.append("• <b>Governance:</b> Rafforzare il framework di governance con metriche avanzate e reporting automatizzato")
                elif section == "Gestione del Rischio":
                    recommendations.append("• <b>Risk Management:</b> Implementare dashboard di risk monitoring in tempo reale")
                elif section == "Risposta agli Incidenti":
                    recommendations.append("• <b>Incident Response:</b> Sviluppare playbook avanzati e integrazione con SIEM")
                elif section == "Continuità Aziendale":
                    recommendations.append("• <b>Business Continuity:</b> Implementare test di recovery automatizzati e metriche di RTO/RPO")
                elif section == "Protezione dei Dati":
                    recommendations.append("• <b>Data Protection:</b> Implementare data classification automatizzata e encryption avanzata")
                elif section == "Controlli di Accesso":
                    recommendations.append("• <b>Access Control:</b> Implementare single sign-on e privileged access management")
            
            elif score >= 70:
                # Buono - raccomandazioni per migliorare
                if section == "Governance della Sicurezza":
                    recommendations.append("• <b>Governance:</b> Implementare un framework di governance strutturato con responsabilità chiare")
                elif section == "Gestione del Rischio":
                    recommendations.append("• <b>Risk Management:</b> Sviluppare un processo di risk assessment quantitativo")
                elif section == "Risposta agli Incidenti":
                    recommendations.append("• <b>Incident Response:</b> Creare un team CSIRT dedicato e procedure standardizzate")
                elif section == "Continuità Aziendale":
                    recommendations.append("• <b>Business Continuity:</b> Sviluppare piani di continuità dettagliati con test regolari")
                elif section == "Protezione dei Dati":
                    recommendations.append("• <b>Data Protection:</b> Implementare data classification e encryption end-to-end")
                elif section == "Controlli di Accesso":
                    recommendations.append("• <b>Access Control:</b> Implementare MFA e gestione centralizzata degli accessi")
        
        # Aggiungi raccomandazioni generali
        if not recommendations:
            recommendations = [
                "• <b>Miglioramento Continuo:</b> Implementare un programma di miglioramento continuo della sicurezza",
                "• <b>Formazione:</b> Sviluppare programmi di formazione avanzati per il personale",
                "• <b>Innovazione:</b> Esplorare tecnologie emergenti come AI e blockchain per la sicurezza"
            ]
        
        return recommendations

    def generate_improvement_recommendations(self, section_scores):
        """Genera raccomandazioni specifiche per il miglioramento continuo"""
        recommendations = []
        
        for section, score in section_scores.items():
            if score >= 90:
                # Eccellente - raccomandazioni per mantenere l'eccellenza
                if section == "Governance della Sicurezza":
                    recommendations.append("• <b>Governance Eccellente:</b> Considerare l'implementazione di framework avanzati come ISO 27001 o NIST Cybersecurity Framework")
                elif section == "Gestione del Rischio":
                    recommendations.append("• <b>Risk Management Avanzato:</b> Implementare analisi predittive e machine learning per la gestione del rischio")
                elif section == "Risposta agli Incidenti":
                    recommendations.append("• <b>Incident Response Avanzato:</b> Sviluppare capacità di threat hunting e intelligence sharing")
                elif section == "Continuità Aziendale":
                    recommendations.append("• <b>Business Continuity Avanzato:</b> Implementare test di disaster recovery automatizzati e simulazioni avanzate")
                elif section == "Protezione dei Dati":
                    recommendations.append("• <b>Data Protection Avanzato:</b> Considerare l'implementazione di DLP (Data Loss Prevention) e zero-trust architecture")
                elif section == "Controlli di Accesso":
                    recommendations.append("• <b>Access Control Avanzato:</b> Implementare soluzioni di behavioral analytics e adaptive authentication")
            
            elif score >= 80:
                # Ottimo - raccomandazioni per raggiungere l'eccellenza
                if section == "Governance della Sicurezza":
                    recommendations.append("• <b>Governance:</b> Rafforzare il framework di governance con metriche avanzate e reporting automatizzato")
                elif section == "Gestione del Rischio":
                    recommendations.append("• <b>Risk Management:</b> Implementare dashboard di risk monitoring in tempo reale")
                elif section == "Risposta agli Incidenti":
                    recommendations.append("• <b>Incident Response:</b> Sviluppare playbook avanzati e integrazione con SIEM")
                elif section == "Continuità Aziendale":
                    recommendations.append("• <b>Business Continuity:</b> Implementare test di recovery automatizzati e metriche di RTO/RPO")
                elif section == "Protezione dei Dati":
                    recommendations.append("• <b>Data Protection:</b> Implementare data classification automatizzata e encryption avanzata")
                elif section == "Controlli di Accesso":
                    recommendations.append("• <b>Access Control:</b> Implementare single sign-on e privileged access management")
            
            elif score >= 70:
                # Buono - raccomandazioni per migliorare
                if section == "Governance della Sicurezza":
                    recommendations.append("• <b>Governance:</b> Implementare un framework di governance strutturato con responsabilità chiare")
                elif section == "Gestione del Rischio":
                    recommendations.append("• <b>Risk Management:</b> Sviluppare un processo di risk assessment quantitativo")
                elif section == "Risposta agli Incidenti":
                    recommendations.append("• <b>Incident Response:</b> Creare un team CSIRT dedicato e procedure standardizzate")
                elif section == "Continuità Aziendale":
                    recommendations.append("• <b>Business Continuity:</b> Sviluppare piani di continuità dettagliati con test regolari")
                elif section == "Protezione dei Dati":
                    recommendations.append("• <b>Data Protection:</b> Implementare data classification e encryption end-to-end")
                elif section == "Controlli di Accesso":
                    recommendations.append("• <b>Access Control:</b> Implementare MFA e gestione centralizzata degli accessi")
        
        # Aggiungi raccomandazioni generali
        if not recommendations:
            recommendations = [
                "• <b>Miglioramento Continuo:</b> Implementare un programma di miglioramento continuo della sicurezza",
                "• <b>Formazione:</b> Sviluppare programmi di formazione avanzati per il personale",
                "• <b>Innovazione:</b> Esplorare tecnologie emergenti come AI e blockchain per la sicurezza"
            ]
        
        return recommendations

    def generate_passport_pdf(self, assessment_data, supplier_data, company_data, output_path):
        """Genera PDF del passaporto di conformità NIS2"""
        doc = SimpleDocTemplate(output_path, pagesize=A4, 
                              rightMargin=2*cm, leftMargin=2*cm, 
                              topMargin=2*cm, bottomMargin=2*cm)
        
        story = []
        
        # Header con logo
        story.append(self.create_header_logo())
        story.append(Spacer(1, 30))
        
        # Titolo principale
        story.append(Paragraph("PASSAPORTO DIGITALE NIS2", self.main_title_style))
        story.append(Paragraph("Certificato di Conformità alla Direttiva NIS2", self.subtitle_style))
        story.append(Spacer(1, 30))
        
        # Messaggio di congratulazioni
        congrats_text = f"""
        <b>CONGRATULAZIONI!</b><br/><br/>
        {supplier_data.get('company_name', 'N/A')} ha superato con successo la valutazione di conformità NIS2 
        per {company_data.get('name', 'N/A')}.<br/><br/>
        Questo certificato attesta la conformità alle normative europee sulla sicurezza delle reti 
        e dei sistemi informativi.
        """
        story.append(Paragraph(congrats_text, self.success_style))
        story.append(Spacer(1, 30))
        
        # Informazioni fornitore
        story.append(Paragraph("INFORMAZIONI FORNITORE", self.subtitle_style))
        
        supplier_info = [
            ["Nome Azienda", supplier_data.get('company_name', 'N/A')],
            ["Email", supplier_data.get('email', 'N/A')],
            ["Settore", supplier_data.get('sector', 'N/A')],
            ["Paese", supplier_data.get('country', 'N/A')],
            ["Data Valutazione", assessment_data.get('completed_at', 'N/A')],
            ["ID Assessment", f"NIS2-{assessment_data.get('id', '000000'):06d}"]
        ]
        
        supplier_table = Table(supplier_info, colWidths=[4*cm, 10*cm])
        supplier_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(supplier_table)
        story.append(Spacer(1, 25))
        
        # Risultati valutazione
        eval_result = json.loads(assessment_data.get('evaluation_result', '{}'))
        compliance_score = eval_result.get('compliance_score', 0)
        
        story.append(Paragraph("RISULTATI VALUTAZIONE", self.subtitle_style))
        
        # Indicatore di conformità
        indicator = self.create_compliance_indicator(compliance_score)
        if indicator:
            story.append(indicator)
            story.append(Spacer(1, 15))
        
        # Punteggio principale
        score_text = f"""
        <b>Punteggio di Conformità:</b> {compliance_score:.1f}%<br/>
        <b>Livello di conformità:</b> {'Eccellente' if compliance_score >= 90 else 'Ottimo' if compliance_score >= 80 else 'Buono' if compliance_score >= 70 else 'Sufficiente'}
        """
        story.append(Paragraph(score_text, self.body_style))
        story.append(Spacer(1, 20))
        
        # Dettaglio per sezioni
        story.append(Paragraph("Dettaglio per Sezioni:", self.body_style))
        
        section_data = [["Sezione", "Punteggio", "Stato"]]
        for section, score in eval_result.get('section_scores', {}).items():
            status = "Conforme" if score >= 70 else "Parzialmente Conforme" if score >= 50 else "Non Conforme"
            section_data.append([section, f"{score:.1f}%", status])
        
        section_table = Table(section_data, colWidths=[8*cm, 3*cm, 3*cm])
        section_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(section_table)
        story.append(Spacer(1, 25))
        
        # Grafico dei punteggi
        if eval_result.get('section_scores'):
            chart = self.create_score_chart(eval_result['section_scores'])
            if chart:
                story.append(chart)
                story.append(Spacer(1, 20))
        
        # Matrice di rischio
        if eval_result.get('section_scores'):
            risk_matrix = self.create_risk_matrix(eval_result['section_scores'])
            if risk_matrix:
                story.append(risk_matrix)
                story.append(Spacer(1, 25))
        
        # Raccomandazioni per il miglioramento continuo
        story.append(Paragraph("RACCOMANDAZIONI PER IL MIGLIORAMENTO CONTINUO", self.subtitle_style))
        
        # Genera raccomandazioni specifiche basate sui punteggi
        recommendations = self.generate_improvement_recommendations(eval_result.get('section_scores', {}))
        
        for rec in recommendations:
            story.append(Paragraph(rec, self.body_style))
            story.append(Spacer(1, 8))
        
        story.append(Spacer(1, 20))
        
        # Validità del certificato
        story.append(Paragraph("VALIDITÀ DEL CERTIFICATO", self.subtitle_style))
        
        validity_text = """
        <b>Durata:</b> 12 mesi dalla data di emissione<br/>
        <b>Rinnovo:</b> Richiesto assessment annuale per mantenere la conformità<br/>
        <b>Verifica:</b> Possibile in qualsiasi momento tramite ID certificato
        """
        story.append(Paragraph(validity_text, self.body_style))
        
        # Verifica pubblica
        story.append(Spacer(1, 25))
        story.append(Paragraph("VERIFICA PUBBLICA", self.subtitle_style))
        verification_text = f"""
        <b>ID Certificato:</b> NIS2-{assessment_data.get('id', '000000'):06d}<br/>
        <b>Piattaforma:</b> NIS2 Supply Chain Assessment<br/>
        <b>Fornitore:</b> {supplier_data.get('company_name', 'N/A')}<br/>
        <b>Data Emissione:</b> {assessment_data.get('completed_at', 'N/A')}<br/>
        <b>Stato:</b> CONFORME ALLA DIRETTIVA NIS2<br/><br/>
        <i>Per verificare l'autenticità di questo certificato, visita la piattaforma NIS2 Supply Chain Assessment 
        e inserisci l'ID certificato sopra indicato.</i>
        """
        story.append(Paragraph(verification_text, self.body_style))
        
        # Footer
        story.append(Spacer(1, 40))
        footer_text = f"""
        ____________________________________________________________________________<br/>
        Generato il {datetime.now().strftime('%d/%m/%Y alle %H:%M')} | Piattaforma NIS2 Supply Chain Assessment<br/>
        Certificato conforme alla Direttiva (UE) 2022/2555 del Parlamento Europeo
        """
        story.append(Paragraph(footer_text, self.footer_style))
        
        doc.build(story)

    def generate_recall_pdf(self, assessment_data, supplier_data, company_data, output_path):
        """Genera PDF di richiamo per fornitori non conformi"""
        doc = SimpleDocTemplate(output_path, pagesize=A4, 
                              rightMargin=2*cm, leftMargin=2*cm, 
                              topMargin=2*cm, bottomMargin=2*cm)
        
        story = []
        
        # Header con logo
        story.append(self.create_header_logo())
        story.append(Spacer(1, 30))
        
        # Titolo principale
        story.append(Paragraph("REPORT DI RICHIAMO NIS2", self.main_title_style))
        story.append(Paragraph("Notifica di Non Conformità alla Direttiva NIS2", self.subtitle_style))
        story.append(Spacer(1, 30))
        
        # Alert critico
        company_name = company_data.get('name', "l'azienda cliente")
        alert_text = f"""
        <b>ATTENZIONE CRITICA</b><br/>
        Questo report indica <b>NON CONFORMITÀ</b> alle normative NIS2. 
        È richiesto un <b>intervento immediato</b> per ripristinare la conformità 
        e mantenere l'accordo di fornitura con <b>{company_name}</b>.
        <br/><br/>
        <b>Conseguenze:</b> Possibile sospensione o terminazione del contratto di fornitura.
        """
        story.append(Paragraph(alert_text, self.success_style))
        story.append(Spacer(1, 25))
        
        # Informazioni fornitore
        story.append(Paragraph("INFORMAZIONI FORNITORE", self.subtitle_style))
        
        supplier_info = [
            ["Nome Azienda", supplier_data.get('company_name', 'N/A')],
            ["Email", supplier_data.get('email', 'N/A')],
            ["Settore", supplier_data.get('sector', 'N/A')],
            ["Paese", supplier_data.get('country', 'N/A')],
            ["Data Valutazione", assessment_data.get('completed_at', 'N/A')],
            ["ID Assessment", f"NIS2-{assessment_data.get('id', '000000'):06d}"]
        ]
        
        supplier_table = Table(supplier_info, colWidths=[4*cm, 10*cm])
        supplier_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#dc2626')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(supplier_table)
        story.append(Spacer(1, 25))
        
        # Risultati valutazione
        eval_result = json.loads(assessment_data.get('evaluation_result', '{}'))
        compliance_score = eval_result.get('compliance_score', 0)
        section_scores = eval_result.get('section_scores', {})
        
        story.append(Paragraph("RISULTATI VALUTAZIONE", self.subtitle_style))
        
        score_text = f"""
        <b>Punteggio di Conformità: {compliance_score:.1f}%</b><br/>
        <i>Livello di rischio: {'Critico' if compliance_score < 30 else 'Alto' if compliance_score < 50 else 'Medio' if compliance_score < 70 else 'Basso'}</i>
        """
        story.append(Paragraph(score_text, self.success_style))
        story.append(Spacer(1, 20))
        
        # Analizza le sezioni problematiche e genera azioni specifiche
        problematic_sections = []
        specific_actions = []
        
        for section, score in section_scores.items():
            if score < 70:
                problematic_sections.append([section, f"{score:.1f}%", "Non Conforme", "ALTA" if score < 30 else "MEDIA" if score < 50 else "BASSA"])
                
                # Genera azioni specifiche per ogni sezione problematica
                if section == "Governance della Sicurezza":
                    if score < 50:
                        specific_actions.append("• <b>Governance Critica:</b> Nominare un CISO e implementare un comitato di sicurezza aziendale")
                        specific_actions.append("• <b>Policy:</b> Creare policy di sicurezza aziendali complete e approvate dal board")
                    else:
                        specific_actions.append("• <b>Governance:</b> Rafforzare il framework di governance della sicurezza esistente")
                
                elif section == "Gestione del Rischio":
                    if score < 50:
                        specific_actions.append("• <b>Risk Assessment:</b> Eseguire una valutazione completa dei rischi di sicurezza")
                        specific_actions.append("• <b>Risk Register:</b> Creare un registro dei rischi con piani di mitigazione")
                    else:
                        specific_actions.append("• <b>Risk Management:</b> Aggiornare i processi di gestione del rischio")
                
                elif section == "Risposta agli Incidenti":
                    if score < 50:
                        specific_actions.append("• <b>Incident Response Plan:</b> Sviluppare un piano di risposta agli incidenti completo")
                        specific_actions.append("• <b>CSIRT:</b> Creare un team di risposta agli incidenti di sicurezza")
                    else:
                        specific_actions.append("• <b>Incident Response:</b> Migliorare le procedure di risposta agli incidenti esistenti")
                
                elif section == "Continuità Aziendale":
                    if score < 50:
                        specific_actions.append("• <b>BCP:</b> Sviluppare un piano di continuità aziendale dettagliato")
                        specific_actions.append("• <b>DRP:</b> Creare un piano di disaster recovery per i sistemi critici")
                    else:
                        specific_actions.append("• <b>Business Continuity:</b> Aggiornare i piani di continuità esistenti")
                
                elif section == "Protezione dei Dati":
                    if score < 50:
                        specific_actions.append("• <b>Data Classification:</b> Implementare un sistema di classificazione dei dati")
                        specific_actions.append("• <b>Encryption:</b> Crittografare i dati sensibili in transito e a riposo")
                    else:
                        specific_actions.append("• <b>Data Protection:</b> Rafforzare le misure di protezione dati esistenti")
                
                elif section == "Controlli di Accesso":
                    if score < 50:
                        specific_actions.append("• <b>IAM:</b> Implementare un sistema di gestione identità e accessi")
                        specific_actions.append("• <b>MFA:</b> Attivare l'autenticazione multi-fattore per tutti gli utenti")
                    else:
                        specific_actions.append("• <b>Access Control:</b> Migliorare i controlli di accesso esistenti")
        
        # Mostra le sezioni problematiche
        if problematic_sections:
            story.append(Paragraph("Aree che richiedono miglioramento:", self.body_style))
            
            section_data = [["Sezione", "Punteggio", "Stato", "Priorità"]] + problematic_sections
            section_table = Table(section_data, colWidths=[6*cm, 2.5*cm, 3*cm, 2.5*cm])
            section_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc2626')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(section_table)
            story.append(Spacer(1, 25))
        
        # Azioni specifiche basate sulle sezioni problematiche
        story.append(Paragraph("AZIONI SPECIFICHE RICHIESTE", self.subtitle_style))
        
        if specific_actions:
            actions_text = "<b>Basandosi sui risultati della valutazione, sono necessarie le seguenti azioni concrete:</b><br/><br/>"
            actions_text += "<br/>".join(specific_actions)
        else:
            actions_text = """
            <b>Per ripristinare la conformità, è necessario implementare le seguenti misure:</b><br/><br/>
            • <b>Governance:</b> Implementare framework di governance della sicurezza<br/>
            • <b>Risk Management:</b> Sviluppare processi di gestione del rischio<br/>
            • <b>Incident Response:</b> Creare procedure di risposta agli incidenti<br/>
            • <b>Business Continuity:</b> Implementare piani di continuità aziendale<br/>
            • <b>Training:</b> Formare il personale sulle normative NIS2<br/>
            • <b>Documentation:</b> Documentare tutti i processi di sicurezza
            """
        
        actions_text += "<br/><br/><b>Timeline:</b> 30 giorni per implementare le correzioni critiche<br/>"
        actions_text += "<b>Follow-up:</b> Assessment di verifica dopo 60 giorni"
        
        story.append(Paragraph(actions_text, self.body_style))
        
        # Verifica pubblica
        story.append(Spacer(1, 25))
        story.append(Paragraph("VERIFICA PUBBLICA", self.subtitle_style))
        verification_text = f"""
        <b>ID Report:</b> NIS2-{assessment_data.get('id', '000000'):06d}<br/>
        <b>Fornitore:</b> {supplier_data.get('company_name', 'N/A')}<br/>
        <b>Data Valutazione:</b> {assessment_data.get('completed_at', 'N/A')}<br/>
        <b>Stato:</b> NON CONFORME - RICHIESTE AZIONI CORRETTIVE<br/><br/>
        <i>Per verificare l'autenticità di questo report, visita la piattaforma NIS2 Supply Chain Assessment 
        e inserisci l'ID report sopra indicato.</i>
        """
        story.append(Paragraph(verification_text, self.body_style))
        
        # Footer
        story.append(Spacer(1, 40))
        footer_text = f"""
        ____________________________________________________________________________<br/>
        Generato il {datetime.now().strftime('%d/%m/%Y alle %H:%M')} | Piattaforma NIS2 Supply Chain Assessment<br/>
        Report conforme alla Direttiva (UE) 2022/2555 del Parlamento Europeo
        """
        story.append(Paragraph(footer_text, self.footer_style))
        
        doc.build(story)

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
        
        generator = ProfessionalNIS2PDFGenerator()
        
        if outcome == 'POSITIVO':
            filename = f"passaporto_nis2_{assessment_id}.pdf"
            output_path = os.path.join(output_dir, filename)
            generator.generate_passport_pdf(assessment_data, supplier_data, company_data, output_path)
            print(f"✅ Generato passaporto digitale professionale: {output_path}")
        else:
            filename = f"richiamo_nis2_{assessment_id}.pdf"
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
