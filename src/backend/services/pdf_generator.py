import os
import qrcode
import base64
from io import BytesIO
from datetime import datetime
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader
from PIL import Image

class PDFGenerator:
    def __init__(self):
        self.template_env = Environment(loader=FileSystemLoader('templates'))
        self.static_dir = 'static'
        self.ensure_directories()
    
    def ensure_directories(self):
        """Crea le directory necessarie se non esistono"""
        os.makedirs(self.static_dir, exist_ok=True)
        os.makedirs('templates', exist_ok=True)
        os.makedirs(os.path.join(self.static_dir, 'pdfs'), exist_ok=True)
        os.makedirs(os.path.join(self.static_dir, 'qr_codes'), exist_ok=True)
    
    def generate_qr_code(self, data: str, filename: str) -> str:
        """Genera un QR code e restituisce il percorso del file"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Crea l'immagine QR
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Salva il QR code
        qr_path = os.path.join(self.static_dir, 'qr_codes', f'{filename}.png')
        qr_img.save(qr_path)
        
        return qr_path
    
    def generate_passaporto_digitale(self, supplier_data: dict, assessment_data: dict, 
                                   verification_url: str) -> str:
        """Genera il PDF del Passaporto Digitale per fornitori conformi"""
        
        # Genera QR code per la verifica pubblica
        qr_filename = f"passport_{assessment_data['id']}_{datetime.now().strftime('%Y%m%d')}"
        qr_path = self.generate_qr_code(verification_url, qr_filename)
        
        # Prepara i dati per il template
        template_data = {
            'supplier': supplier_data,
            'assessment': assessment_data,
            'verification_url': verification_url,
            'qr_code_path': qr_path,
            'generated_date': datetime.now().strftime('%d/%m/%Y'),
            'generated_time': datetime.now().strftime('%H:%M:%S'),
            'document_type': 'PASSAPORTO DIGITALE NIS2',
            'compliance_status': 'CONFORME',
            'validity_period': '12 mesi dalla data di emissione'
        }
        
        # Carica e renderizza il template
        template = self.template_env.get_template('passaporto_template.html')
        html_content = template.render(**template_data)
        
        # Genera il PDF
        pdf_filename = f"passaporto_{supplier_data['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(self.static_dir, 'pdfs', pdf_filename)
        
        HTML(string=html_content).write_pdf(
            pdf_path,
            stylesheets=[CSS(string=self._get_pdf_styles())]
        )
        
        return pdf_path
    
    def generate_richiamo_report(self, supplier_data: dict, assessment_data: dict, 
                               verification_url: str) -> str:
        """Genera il PDF del Report di Richiamo per fornitori non conformi"""
        
        # Genera QR code per la verifica pubblica
        qr_filename = f"recall_{assessment_data['id']}_{datetime.now().strftime('%Y%m%d')}"
        qr_path = self.generate_qr_code(verification_url, qr_filename)
        
        # Prepara i dati per il template
        template_data = {
            'supplier': supplier_data,
            'assessment': assessment_data,
            'verification_url': verification_url,
            'qr_code_path': qr_path,
            'generated_date': datetime.now().strftime('%d/%m/%Y'),
            'generated_time': datetime.now().strftime('%H:%M:%S'),
            'document_type': 'REPORT DI RICHIAMO NIS2',
            'compliance_status': 'NON CONFORME',
            'action_required': 'Implementazione misure correttive richieste'
        }
        
        # Carica e renderizza il template
        template = self.template_env.get_template('richiamo_template.html')
        html_content = template.render(**template_data)
        
        # Genera il PDF
        pdf_filename = f"richiamo_{supplier_data['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_path = os.path.join(self.static_dir, 'pdfs', pdf_filename)
        
        HTML(string=html_content).write_pdf(
            pdf_path,
            stylesheets=[CSS(string=self._get_pdf_styles())]
        )
        
        return pdf_path
    
    def _get_pdf_styles(self) -> str:
        """Restituisce gli stili CSS per i PDF"""
        return """
        @page {
            size: A4;
            margin: 2cm;
            @top-center {
                content: "Piattaforma NIS2 Supplier Assessment";
                font-size: 10px;
                color: #666;
            }
            @bottom-center {
                content: "Pagina " counter(page) " di " counter(pages);
                font-size: 10px;
                color: #666;
            }
        }
        
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
        }
        
        .header {
            text-align: center;
            border-bottom: 3px solid #2563eb;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        
        .header h1 {
            color: #2563eb;
            font-size: 24px;
            margin: 0;
            font-weight: bold;
        }
        
        .header .subtitle {
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }
        
        .status-badge {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: bold;
            font-size: 16px;
            margin: 20px 0;
        }
        
        .status-conforme {
            background-color: #22c55e;
            color: white;
        }
        
        .status-non-conforme {
            background-color: #ef4444;
            color: white;
        }
        
        .info-section {
            background-color: #f8fafc;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #2563eb;
        }
        
        .info-section h3 {
            color: #2563eb;
            margin-top: 0;
            font-size: 18px;
        }
        
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        
        .data-table th,
        .data-table td {
            border: 1px solid #e5e7eb;
            padding: 12px;
            text-align: left;
        }
        
        .data-table th {
            background-color: #f3f4f6;
            font-weight: bold;
            color: #374151;
        }
        
        .qr-section {
            text-align: center;
            margin: 30px 0;
            padding: 20px;
            background-color: #f9fafb;
            border-radius: 8px;
        }
        
        .qr-code {
            margin: 20px auto;
            display: block;
        }
        
        .verification-url {
            font-family: 'Courier New', monospace;
            font-size: 12px;
            color: #6b7280;
            word-break: break-all;
            margin-top: 10px;
        }
        
        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
            font-size: 12px;
            color: #6b7280;
            text-align: center;
        }
        
        .improvement-areas {
            background-color: #fef2f2;
            border-left: 4px solid #ef4444;
            padding: 15px;
            margin: 20px 0;
        }
        
        .improvement-areas h4 {
            color: #dc2626;
            margin-top: 0;
        }
        
        .improvement-areas ul {
            margin: 0;
            padding-left: 20px;
        }
        
        .improvement-areas li {
            margin-bottom: 5px;
        }
        
        .strengths {
            background-color: #f0fdf4;
            border-left: 4px solid #22c55e;
            padding: 15px;
            margin: 20px 0;
        }
        
        .strengths h4 {
            color: #16a34a;
            margin-top: 0;
        }
        """ 