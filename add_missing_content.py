import sqlite3
from datetime import datetime

def add_missing_content():
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    print("=== AGGIUNTA CONTENUTI MANCANTI ===")
    
    # Contenuti per il corso 1: Fondamenti NIS2
    course1_contents = [
        {
            'title': 'Introduzione alla Direttiva NIS2',
            'type': 'VIDEO',
            'content': '''
<h3>🎥 Video: Introduzione alla Direttiva NIS2</h3>

<p><strong>Video:</strong> <a href="https://youtube.com/watch?v=NIS2_INTRO" target="_blank">Guarda il video su YouTube</a></p>

<h4>📝 Trascrizione del Video:</h4>
<p>La Direttiva NIS2 (Network and Information Security 2) è la normativa europea che stabilisce requisiti di sicurezza per operatori di servizi essenziali e fornitori di servizi digitali.</p>

<h4>🎯 Obiettivi della Lezione:</h4>
<ul>
<li>Comprendere il contesto e gli obiettivi della NIS2</li>
<li>Identificare le entità soggette alla normativa</li>
<li>Conoscere i requisiti di compliance</li>
</ul>

<h4>📋 Punti Chiave:</h4>
<p><strong>1. Ambito di Applicazione:</strong> La NIS2 si applica a:</p>
<ul>
<li>Operatori di servizi essenziali (energia, trasporti, sanità, ecc.)</li>
<li>Fornitori di servizi digitali (cloud, e-commerce, motori di ricerca)</li>
<li>Enti pubblici e amministrazioni</li>
</ul>

<p><strong>2. Requisiti Principali:</strong></p>
<ul>
<li>Gestione del rischio di sicurezza</li>
<li>Notifica degli incidenti</li>
<li>Misurazioni di sicurezza</li>
<li>Audit e certificazioni</li>
</ul>
''',
            'order': 1,
            'duration': 20
        },
        {
            'title': 'Classificazione delle Entità NIS2',
            'type': 'DOCUMENT',
            'content': '''
<h3>📄 Documento: Classificazione delle Entità NIS2</h3>

<h4>🏢 Entità di Importanza Essenziale (OES):</h4>
<ul>
<li><strong>Settore Energia:</strong> Operatori di reti elettriche, gas, petrolio</li>
<li><strong>Settore Trasporti:</strong> Operatori ferroviari, aerei, marittimi</li>
<li><strong>Settore Bancario:</strong> Istituzioni finanziarie, sistemi di pagamento</li>
<li><strong>Settore Sanitario:</strong> Ospedali, laboratori, farmacie</li>
<li><strong>Settore Acqua:</strong> Operatori di distribuzione idrica</li>
<li><strong>Settore Digitale:</strong> Infrastrutture cloud, DNS, IXP</li>
</ul>

<h4>💻 Fornitori di Servizi Digitali (DSP):</h4>
<ul>
<li><strong>Servizi Cloud:</strong> IaaS, PaaS, SaaS</li>
<li><strong>E-commerce:</strong> Piattaforme online</li>
<li><strong>Motori di Ricerca:</strong> Servizi di indicizzazione</li>
<li><strong>Social Media:</strong> Piattaforme di comunicazione</li>
</ul>

<h4>📊 Criteri di Classificazione:</h4>
<p>Le entità sono classificate in base a:</p>
<ul>
<li>Numero di utenti serviti</li>
<li>Volume di fatturato</li>
<li>Impatto potenziale di un incidente</li>
<li>Interdipendenze con altri settori</li>
</ul>
''',
            'order': 2,
            'duration': 15
        }
    ]
    
    # Contenuti per il corso 2: Gestione del Rischio
    course2_contents = [
        {
            'title': 'Framework di Gestione del Rischio',
            'type': 'VIDEO',
            'content': '''
<h3>🎥 Video: Framework di Gestione del Rischio</h3>

<p><strong>Video:</strong> <a href="https://youtube.com/watch?v=RISK_MGMT" target="_blank">Guarda il video su YouTube</a></p>

<h4>📝 Trascrizione del Video:</h4>
<p>La gestione del rischio è un processo sistematico per identificare, valutare e mitigare i rischi che potrebbero compromettere la sicurezza delle informazioni e dei sistemi.</p>

<h4>🎯 Obiettivi della Lezione:</h4>
<ul>
<li>Comprendere il ciclo di gestione del rischio</li>
<li>Identificare le metodologie di valutazione</li>
<li>Implementare strategie di mitigazione</li>
</ul>

<h4>📋 Framework ISO 27005:</h4>
<p><strong>1. Contesto:</strong> Definire il contesto organizzativo e i criteri di rischio</p>
<p><strong>2. Identificazione:</strong> Identificare asset, minacce e vulnerabilità</p>
<p><strong>3. Valutazione:</strong> Analizzare probabilità e impatto</p>
<p><strong>4. Trattamento:</strong> Implementare controlli di mitigazione</p>
<p><strong>5. Monitoraggio:</strong> Controllare e rivedere continuamente</p>

<h4>💡 Esempio Pratico:</h4>
<p>In un'azienda energetica, un rischio potrebbe essere un attacco ransomware che paralizza i sistemi SCADA. La probabilità è media, ma l'impatto è critico. Le mitigazioni includono backup offline, segmentazione di rete e formazione del personale.</p>
''',
            'order': 1,
            'duration': 25
        },
        {
            'title': 'Matrice di Valutazione del Rischio',
            'type': 'INTERACTIVE',
            'content': '''
<h3>🔄 Esercizio Interattivo: Matrice di Valutazione del Rischio</h3>

<h4>📊 Matrice 5x5:</h4>
<table border="1" style="width:100%; border-collapse: collapse;">
<tr>
<th>Probabilità/Impatto</th>
<th>Molto Basso (1)</th>
<th>Basso (2)</th>
<th>Medio (3)</th>
<th>Alto (4)</th>
<th>Molto Alto (5)</th>
</tr>
<tr>
<td><strong>Molto Alta (5)</strong></td>
<td style="background-color: #ffeb3b;">5</td>
<td style="background-color: #ff9800;">10</td>
<td style="background-color: #f44336;">15</td>
<td style="background-color: #d32f2f;">20</td>
<td style="background-color: #b71c1c;">25</td>
</tr>
<tr>
<td><strong>Alta (4)</strong></td>
<td style="background-color: #4caf50;">4</td>
<td style="background-color: #ffeb3b;">8</td>
<td style="background-color: #ff9800;">12</td>
<td style="background-color: #f44336;">16</td>
<td style="background-color: #d32f2f;">20</td>
</tr>
<tr>
<td><strong>Media (3)</strong></td>
<td style="background-color: #4caf50;">3</td>
<td style="background-color: #4caf50;">6</td>
<td style="background-color: #ffeb3b;">9</td>
<td style="background-color: #ff9800;">12</td>
<td style="background-color: #f44336;">15</td>
</tr>
<tr>
<td><strong>Bassa (2)</strong></td>
<td style="background-color: #4caf50;">2</td>
<td style="background-color: #4caf50;">4</td>
<td style="background-color: #4caf50;">6</td>
<td style="background-color: #ffeb3b;">8</td>
<td style="background-color: #ff9800;">10</td>
</tr>
<tr>
<td><strong>Molto Bassa (1)</strong></td>
<td style="background-color: #4caf50;">1</td>
<td style="background-color: #4caf50;">2</td>
<td style="background-color: #4caf50;">3</td>
<td style="background-color: #4caf50;">4</td>
<td style="background-color: #ffeb3b;">5</td>
</tr>
</table>

<h4>🎨 Legenda Colori:</h4>
<ul>
<li><span style="color: #4caf50;">🟢 Verde:</span> Rischio Accettabile (1-6)</li>
<li><span style="color: #ffeb3b;">🟡 Giallo:</span> Rischio Moderato (7-12)</li>
<li><span style="color: #ff9800;">🟠 Arancione:</span> Rischio Alto (13-18)</li>
<li><span style="color: #f44336;">🔴 Rosso:</span> Rischio Critico (19-25)</li>
</ul>

<h4>📝 Esercizio:</h4>
<p>Valuta i seguenti rischi per la tua organizzazione:</p>
<ol>
<li>Phishing email ai dipendenti (Probabilità: Alta, Impatto: Medio)</li>
<li>Guasto hardware server critico (Probabilità: Bassa, Impatto: Alto)</li>
<li>Violazione dati personali (Probabilità: Media, Impatto: Molto Alto)</li>
</ol>
''',
            'order': 2,
            'duration': 30
        }
    ]
    
    # Inserimento contenuti per corso 1
    for content in course1_contents:
        cursor.execute('''
            INSERT INTO training_course_content (course_id, title, content_type, content, order_index, duration_minutes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (1, content['title'], content['type'], content['content'], content['order'], content['duration']))
        print(f"✅ Aggiunto contenuto '{content['title']}' al corso 1")
    
    # Inserimento contenuti per corso 2
    for content in course2_contents:
        cursor.execute('''
            INSERT INTO training_course_content (course_id, title, content_type, content, order_index, duration_minutes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (2, content['title'], content['type'], content['content'], content['order'], content['duration']))
        print(f"✅ Aggiunto contenuto '{content['title']}' al corso 2")
    
    conn.commit()
    conn.close()
    print("✅ Contenuti aggiunti con successo!")

if __name__ == "__main__":
    add_missing_content()
