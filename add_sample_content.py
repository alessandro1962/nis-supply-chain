#!/usr/bin/env python3
"""
Script per aggiungere contenuti di esempio ai corsi di training
"""

import sqlite3
import json
from datetime import datetime

def add_sample_content():
    """Aggiunge contenuti di esempio ai corsi"""
    
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    # Contenuti di esempio per il corso "Cybersecurity Fundamentals NIS2"
    cybersecurity_content = [
        {
            'title': 'Introduzione alla Cybersecurity NIS2',
            'content_type': 'VIDEO',
            'order_index': 1,
            'duration_minutes': 15,
            'video_url': 'https://youtube.com/watch?v=dQw4w9WgXcQ',  # Esempio YouTube
            'content': '''<h3>🎥 Video: Introduzione alla Cybersecurity NIS2</h3>

<p><strong>Video:</strong> <a href="https://youtube.com/watch?v=dQw4w9WgXcQ" target="_blank">Guarda il video su YouTube</a></p>

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
<p>Immagina di essere responsabile della sicurezza IT di un'azienda energetica. Un attacco ransomware potrebbe paralizzare l'intera rete, causando blackout e danni economici ingenti. La compliance NIS2 ti aiuta a implementare le misure di protezione necessarie.</p>'''
        },
        {
            'title': 'Gestione del Rischio Cybersecurity',
            'content_type': 'VIDEO',
            'order_index': 2,
            'duration_minutes': 20,
            'video_url': 'https://vimeo.com/123456789',  # Esempio Vimeo
            'content': '''<h3>🎥 Video: Gestione del Rischio Cybersecurity</h3>

<p><strong>Video:</strong> <a href="https://vimeo.com/123456789" target="_blank">Guarda il video su Vimeo</a></p>

<h4>📝 Trascrizione del Video:</h4>
<p>In questa lezione approfondiremo la gestione del rischio cybersecurity, un aspetto fondamentale per la compliance NIS2.</p>

<h4>🎯 Obiettivi della Lezione:</h4>
<ul>
<li>Comprendere il processo di valutazione del rischio</li>
<li>Identificare le minacce e vulnerabilità</li>
<li>Implementare misure di mitigazione</li>
<li>Monitorare e rivedere i rischi</li>
</ul>

<h4>📋 Processo di Gestione del Rischio:</h4>
<p><strong>1. Identificazione del Rischio:</strong> Analisi sistematica per identificare potenziali minacce e vulnerabilità.</p>

<p><strong>2. Valutazione del Rischio:</strong> Determinazione della probabilità e dell'impatto di ciascun rischio.</p>

<p><strong>3. Trattamento del Rischio:</strong> Implementazione di strategie per ridurre, trasferire o accettare i rischi.</p>

<p><strong>4. Monitoraggio:</strong> Controllo continuo dell'efficacia delle misure implementate.</p>

<h4>💡 Esempio Pratico:</h4>
<p>Considera un'azienda che gestisce dati sensibili dei clienti. Un rischio identificato potrebbe essere un attacco di phishing che porta a una violazione dei dati. La valutazione potrebbe determinare una probabilità media e un impatto alto, richiedendo misure di mitigazione come formazione del personale e sistemi di rilevamento avanzati.</p>'''
        },
        {
            'title': 'Requisiti di Sicurezza NIS2',
            'content_type': 'LESSON',
            'order_index': 3,
            'duration_minutes': 30,
            'content': '''<h3>📚 Lezione: Requisiti di Sicurezza NIS2</h3>

<h4>🎯 Obiettivi della Lezione:</h4>
<p>In questa lezione analizzeremo i requisiti di sicurezza specifici della direttiva NIS2 e come implementarli nella pratica.</p>

<h4>📋 Requisiti Principali:</h4>

<p><strong>1. Gestione del Rischio:</strong></p>
<ul>
<li>Valutazione regolare dei rischi di sicurezza</li>
<li>Implementazione di misure di mitigazione appropriate</li>
<li>Monitoraggio continuo dell'efficacia</li>
</ul>

<p><strong>2. Sicurezza delle Reti e Sistemi:</strong></p>
<ul>
<li>Protezione contro accessi non autorizzati</li>
<li>Crittografia dei dati sensibili</li>
<li>Backup e disaster recovery</li>
</ul>

<p><strong>3. Gestione degli Incidenti:</strong></p>
<ul>
<li>Procedure di rilevamento e risposta</li>
<li>Notifica tempestiva alle autorità competenti</li>
<li>Analisi post-incidente</li>
</ul>

<p><strong>4. Conformità e Audit:</strong></p>
<ul>
<li>Documentazione delle misure implementate</li>
<li>Audit regolari di conformità</li>
<li>Aggiornamento delle procedure</li>
</ul>

<h4>💡 Esempio Pratico:</h4>
<p>Un'azienda energetica deve implementare un sistema di monitoraggio 24/7 per rilevare tentativi di intrusione. In caso di incidente, deve notificare l'autorità nazionale entro 24 ore e fornire un rapporto dettagliato entro 72 ore.</p>'''
        },
        {
            'title': 'Best Practices per la Sicurezza',
            'content_type': 'MODULE',
            'order_index': 4,
            'duration_minutes': 25,
            'content': '''<h3>📦 Modulo: Best Practices per la Sicurezza</h3>

<h4>🎯 Obiettivi del Modulo:</h4>
<p>Questo modulo presenta le migliori pratiche per implementare un programma di sicurezza informatica efficace e conforme alla direttiva NIS2.</p>

<h4>📋 Contenuti del Modulo:</h4>

<p><strong>1. Formazione del Personale:</strong></p>
<ul>
<li>Programmi di awareness sulla cybersecurity</li>
<li>Simulazioni di phishing</li>
<li>Aggiornamenti regolari sulle minacce</li>
</ul>

<p><strong>2. Controlli Tecnici:</strong></p>
<ul>
<li>Firewall e sistemi di rilevamento intrusioni</li>
<li>Antivirus e antimalware</li>
<li>Controllo degli accessi e autenticazione multi-fattore</li>
</ul>

<p><strong>3. Procedure Operative:</strong></p>
<ul>
<li>Gestione delle password</li>
<li>Backup e ripristino</li>
<li>Gestione delle patch di sicurezza</li>
</ul>

<p><strong>4. Monitoraggio e Reporting:</strong></p>
<ul>
<li>Log di sicurezza centralizzati</li>
<li>Analisi degli eventi di sicurezza</li>
<li>Reporting periodico alla direzione</li>
</ul>

<h4>💡 Esempio Pratico:</h4>
<p>Implementa un sistema di backup automatico che esegue backup incrementali ogni ora e backup completi ogni giorno. I backup devono essere crittografati e conservati in una posizione fisica separata per garantire la continuità operativa in caso di incidente.</p>'''
        }
    ]
    
    # Contenuti di esempio per il corso "Business Continuity Management"
    business_continuity_content = [
        {
            'title': 'Introduzione al Business Continuity',
            'content_type': 'VIDEO',
            'order_index': 1,
            'duration_minutes': 18,
            'video_url': 'https://youtube.com/watch?v=9bZkp7q19f0',  # Esempio YouTube
            'content': '''<h3>🎥 Video: Introduzione al Business Continuity</h3>

<p><strong>Video:</strong> <a href="https://youtube.com/watch?v=9bZkp7q19f0" target="_blank">Guarda il video su YouTube</a></p>

<h4>📝 Trascrizione del Video:</h4>
<p>Benvenuti al corso di Business Continuity Management. In questa lezione introduttiva parleremo dei concetti fondamentali della continuità aziendale e della sua importanza strategica.</p>

<h4>🎯 Obiettivi della Lezione:</h4>
<ul>
<li>Comprendere il concetto di business continuity</li>
<li>Identificare i rischi che minacciano la continuità operativa</li>
<li>Conoscere i framework di riferimento</li>
</ul>

<h4>📋 Concetti Chiave:</h4>
<p><strong>1. Business Continuity:</strong> Capacità di un'organizzazione di continuare a fornire prodotti e servizi a livelli predefiniti accettabili dopo un incidente.</p>

<p><strong>2. Disaster Recovery:</strong> Processo di ripristino delle funzioni IT critiche dopo un'interruzione.</p>

<p><strong>3. Risk Assessment:</strong> Identificazione e valutazione dei rischi che potrebbero interrompere le operazioni aziendali.</p>

<h4>💡 Esempio Pratico:</h4>
<p>Un'azienda di e-commerce deve garantire che il sito web rimanga operativo anche in caso di attacco DDoS. Il piano di business continuity prevede server di backup e un sistema di bilanciamento del carico per mantenere la continuità del servizio.</p>'''
        },
        {
            'title': 'Analisi dell\'Impatto sul Business',
            'content_type': 'LESSON',
            'order_index': 2,
            'duration_minutes': 35,
            'content': '''<h3>📚 Lezione: Analisi dell'Impatto sul Business</h3>

<h4>🎯 Obiettivi della Lezione:</h4>
<p>In questa lezione impareremo a condurre un'analisi dell'impatto sul business (BIA) per identificare le funzioni critiche e le risorse necessarie per la continuità operativa.</p>

<h4>📋 Processo BIA:</h4>

<p><strong>1. Identificazione delle Funzioni Critiche:</strong></p>
<ul>
<li>Mappatura dei processi aziendali</li>
<li>Valutazione della criticità</li>
<li>Identificazione delle dipendenze</li>
</ul>

<p><strong>2. Analisi dell'Impatto:</strong></p>
<ul>
<li>Valutazione dell'impatto finanziario</li>
<li>Analisi dell'impatto operativo</li>
<li>Valutazione dell'impatto reputazionale</li>
</ul>

<p><strong>3. Definizione dei Tempi di Recupero:</strong></p>
<ul>
<li>Recovery Time Objective (RTO)</li>
<li>Recovery Point Objective (RPO)</li>
<li>Maximum Tolerable Downtime (MTD)</li>
</ul>

<h4>💡 Esempio Pratico:</h4>
<p>Per un'azienda bancaria, il sistema di pagamenti online ha un RTO di 4 ore e un RPO di 15 minuti. Questo significa che il sistema deve essere ripristinato entro 4 ore e può perdere al massimo 15 minuti di dati.</p>'''
        },
        {
            'title': 'Strategie di Business Continuity',
            'content_type': 'MODULE',
            'order_index': 3,
            'duration_minutes': 40,
            'content': '''<h3>📦 Modulo: Strategie di Business Continuity</h3>

<h4>🎯 Obiettivi del Modulo:</h4>
<p>Questo modulo presenta le strategie e le tecniche per sviluppare e implementare un piano di business continuity efficace.</p>

<h4>📋 Strategie Principali:</h4>

<p><strong>1. Ridondanza:</strong></p>
<ul>
<li>Sistemi di backup</li>
<li>Siti di disaster recovery</li>
<li>Fornitori alternativi</li>
</ul>

<p><strong>2. Resilienza:</strong></p>
<ul>
<li>Design di sistemi fault-tolerant</li>
<li>Distribuzione geografica</li>
<li>Architetture cloud-native</li>
</ul>

<p><strong>3. Ripristino Rapido:</strong></p>
<ul>
<li>Procedure di escalation</li>
<li>Team di risposta agli incidenti</li>
<li>Comunicazione di crisi</li>
</ul>

<p><strong>4. Test e Validazione:</strong></p>
<ul>
<li>Esercitazioni regolari</li>
<li>Simulazioni di scenari</li>
<li>Revisione e aggiornamento dei piani</li>
</ul>

<h4>💡 Esempio Pratico:</h4>
<p>Un'azienda manifatturiera implementa un sistema di produzione parallelo in un sito di backup. In caso di interruzione del sito principale, può trasferire la produzione al sito di backup entro 2 ore, garantendo la continuità operativa.</p>'''
        }
    ]
    
    try:
        # Ottieni i corsi esistenti
        cursor.execute("SELECT id, title FROM training_courses")
        courses = cursor.fetchall()
        
        print(f"Trovati {len(courses)} corsi:")
        for course_id, title in courses:
            print(f"- ID {course_id}: {title}")
        
        # Aggiungi contenuti per ogni corso
        for course_id, title in courses:
            print(f"\nAggiungendo contenuti per: {title}")
            
            # Scegli i contenuti appropriati
            if "cybersecurity" in title.lower() or "nis2" in title.lower():
                content_list = cybersecurity_content
            elif "business continuity" in title.lower():
                content_list = business_continuity_content
            else:
                # Contenuto generico per altri corsi
                content_list = [
                    {
                        'title': 'Introduzione al Corso',
                        'content_type': 'LESSON',
                        'order_index': 1,
                        'duration_minutes': 20,
                        'content': f'<h3>📚 Introduzione al Corso: {title}</h3><p>Benvenuti al corso {title}. In questa lezione introduttiva parleremo dei concetti fondamentali.</p>'
                    }
                ]
            
            # Inserisci i contenuti
            for content in content_list:
                cursor.execute("""
                    INSERT INTO training_course_content 
                    (course_id, title, content_type, order_index, duration_minutes, video_url, content, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    course_id,
                    content['title'],
                    content['content_type'],
                    content['order_index'],
                    content['duration_minutes'],
                    content.get('video_url'),
                    content['content'],
                    datetime.now().isoformat()
                ))
                print(f"  ✅ Aggiunto: {content['title']}")
        
        conn.commit()
        print(f"\n✅ Contenuti aggiunti con successo!")
        
    except Exception as e:
        print(f"❌ Errore: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    add_sample_content()
