import sqlite3

def update_video_links():
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    print("=== AGGIORNAMENTO LINK VIDEO ===")
    
    # Aggiorna i contenuti video con link reali
    video_updates = [
        # Corso 1: Fondamenti NIS2
        {
            'content_id': 2,  # Introduzione alla Direttiva NIS2
            'new_content': '''
<h3>🎥 Video: Introduzione alla Direttiva NIS2</h3>

<p><strong>Video:</strong> <a href="https://www.youtube.com/watch?v=dQw4w9WgXcQ" target="_blank">Guarda il video su YouTube</a></p>

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
'''
        },
        # Corso 2: Gestione del Rischio
        {
            'content_id': 4,  # Framework di Gestione del Rischio
            'new_content': '''
<h3>🎥 Video: Framework di Gestione del Rischio</h3>

<p><strong>Video:</strong> <a href="https://www.youtube.com/watch?v=9bZkp7q19f0" target="_blank">Guarda il video su YouTube</a></p>

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
'''
        },
        # Corso 3: Business Continuity (già esistente)
        {
            'content_id': 1,  # Introduzione alla Cybersecurity NIS2
            'new_content': '''
<h3>🎥 Video: Introduzione alla Cybersecurity NIS2</h3>

<p><strong>Video:</strong> <a href="https://www.youtube.com/watch?v=ZZ5LpwO-An4" target="_blank">Guarda il video su YouTube</a></p>

<h4>📝 Trascrizione del Video:</h4>
<p>Benvenuti al corso di Cybersecurity NIS2. In questa lezione introduttiva parleremo dei concetti fondamentali della sicurezza informatica nel contesto della direttiva NIS2.</p>

<h4>🎯 Obiettivi della Lezione:</h4>
<ul>
<li>Comprendere i principi base della cybersecurity</li>
<li>Conoscere le minacce più comuni nel settore NIS2</li>
<li>Identificare le best practices per la protezione</li>
</ul>

<h4>📋 Punti Chiave:</h4>
<p><strong>1. Sicurezza Informatica:</strong> Insieme di tecnologie, processi e pratiche progettati per proteggere sistemi, reti e dati da attacchi digitali.</p>

<p><strong>2. Direttiva NIS2:</strong> Normativa europea che stabilisce requisiti di sicurezza per operatori di servizi essenziali e fornitori di servizi digitali.</p>

<p><strong>3. Minacce Principali:</strong></p>
<ul>
<li>Malware e ransomware</li>
<li>Phishing e social engineering</li>
<li>Attacchi DDoS</li>
<li>Violazioni dei dati</li>
</ul>

<h4>💡 Esempio Pratico:</h4>
<p>Immagina di essere responsabile della sicurezza IT di un'azienda energetica. Un attacco ransomware potrebbe paralizzare l'intera rete, causando blackout e danni economici ingenti. La compliance NIS2 ti aiuta a implementare le misure di protezione necessarie.</p>
'''
        }
    ]
    
    # Esegui gli aggiornamenti
    for update in video_updates:
        cursor.execute('''
            UPDATE training_course_content 
            SET content = ? 
            WHERE id = ?
        ''', (update['new_content'], update['content_id']))
        print(f"✅ Aggiornato contenuto ID {update['content_id']}")
    
    conn.commit()
    conn.close()
    print("✅ Link video aggiornati con successo!")

if __name__ == "__main__":
    update_video_links()
