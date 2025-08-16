import sqlite3
from datetime import datetime, timedelta

def populate_compliance_requirements():
    """Popola le tabelle con i requisiti NIS2"""
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    # Requisiti NIS2 per Governance
    governance_requirements = [
        ("Governance", "GOV-001", "Nomina del CISO", 
         "Designazione di un Chief Information Security Officer responsabile della sicurezza informatica", 
         "Art. 20", "CRITICAL", 1),
        ("Governance", "GOV-002", "Comitato di Sicurezza", 
         "Istituzione di un comitato di sicurezza aziendale con rappresentanti del board", 
         "Art. 20", "HIGH", 1),
        ("Governance", "GOV-003", "Policy di Sicurezza", 
         "Sviluppo e approvazione di policy di sicurezza aziendali complete", 
         "Art. 21", "HIGH", 1),
        ("Governance", "GOV-004", "Risk Management Framework", 
         "Implementazione di un framework strutturato per la gestione del rischio", 
         "Art. 21", "HIGH", 2),
        ("Governance", "GOV-005", "Reporting al Board", 
         "Reporting regolare al board sui rischi di sicurezza e stato di compliance", 
         "Art. 20", "MEDIUM", 2)
    ]
    
    # Requisiti per Risk Management
    risk_requirements = [
        ("Risk Management", "RISK-001", "Risk Assessment", 
         "Valutazione completa e documentata dei rischi di sicurezza informatica", 
         "Art. 21", "CRITICAL", 1),
        ("Risk Management", "RISK-002", "Risk Register", 
         "Mantenimento di un registro dei rischi con piani di mitigazione", 
         "Art. 21", "HIGH", 1),
        ("Risk Management", "RISK-003", "Risk Monitoring", 
         "Monitoraggio continuo dei rischi e aggiornamento delle valutazioni", 
         "Art. 21", "MEDIUM", 2),
        ("Risk Management", "RISK-004", "Third Party Risk", 
         "Valutazione dei rischi legati ai fornitori e partner esterni", 
         "Art. 22", "HIGH", 1),
        ("Risk Management", "RISK-005", "Risk Metrics", 
         "Definizione e monitoraggio di metriche di rischio quantificabili", 
         "Art. 21", "MEDIUM", 3)
    ]
    
    # Requisiti per Incident Response
    incident_requirements = [
        ("Incident Response", "IR-001", "Incident Response Plan", 
         "Piano di risposta agli incidenti di sicurezza documentato e testato", 
         "Art. 23", "CRITICAL", 1),
        ("Incident Response", "IR-002", "CSIRT Team", 
         "Team dedicato per la risposta agli incidenti di sicurezza", 
         "Art. 23", "HIGH", 1),
        ("Incident Response", "IR-003", "Incident Detection", 
         "Sistemi e procedure per la rilevazione tempestiva di incidenti", 
         "Art. 23", "HIGH", 1),
        ("Incident Response", "IR-004", "Communication Plan", 
         "Piano di comunicazione per incidenti con autorità e stakeholder", 
         "Art. 23", "MEDIUM", 2),
        ("Incident Response", "IR-005", "Lessons Learned", 
         "Processo di analisi post-incidente e miglioramento continuo", 
         "Art. 23", "MEDIUM", 3)
    ]
    
    # Requisiti per Business Continuity
    bc_requirements = [
        ("Business Continuity", "BC-001", "Business Continuity Plan", 
         "Piano di continuità aziendale per servizi critici", 
         "Art. 24", "CRITICAL", 1),
        ("Business Continuity", "BC-002", "Disaster Recovery Plan", 
         "Piano di disaster recovery per sistemi e dati critici", 
         "Art. 24", "HIGH", 1),
        ("Business Continuity", "BC-003", "Backup Strategy", 
         "Strategia di backup e recovery testata regolarmente", 
         "Art. 24", "HIGH", 1),
        ("Business Continuity", "BC-004", "RTO/RPO Definition", 
         "Definizione di Recovery Time Objective e Recovery Point Objective", 
         "Art. 24", "MEDIUM", 2),
        ("Business Continuity", "BC-005", "Testing Schedule", 
         "Programma di test regolari per piani di continuità", 
         "Art. 24", "MEDIUM", 2)
    ]
    
    # Requisiti per Data Protection
    data_requirements = [
        ("Data Protection", "DP-001", "Data Classification", 
         "Sistema di classificazione dei dati per livello di sensibilità", 
         "Art. 25", "HIGH", 1),
        ("Data Protection", "DP-002", "Encryption Policy", 
         "Policy di crittografia per dati in transito e a riposo", 
         "Art. 25", "HIGH", 1),
        ("Data Protection", "DP-003", "Access Controls", 
         "Controlli di accesso basati su principio del minimo privilegio", 
         "Art. 25", "HIGH", 1),
        ("Data Protection", "DP-004", "Data Loss Prevention", 
         "Sistemi di prevenzione della perdita di dati", 
         "Art. 25", "MEDIUM", 2),
        ("Data Protection", "DP-005", "Privacy by Design", 
         "Implementazione di principi di privacy by design", 
         "Art. 25", "MEDIUM", 3)
    ]
    
    # Requisiti per Access Control
    access_requirements = [
        ("Access Control", "AC-001", "Identity Management", 
         "Sistema di gestione delle identità e accessi centralizzato", 
         "Art. 26", "HIGH", 1),
        ("Access Control", "AC-002", "Multi-Factor Authentication", 
         "Implementazione di autenticazione multi-fattore per accessi critici", 
         "Art. 26", "HIGH", 1),
        ("Access Control", "AC-003", "Privileged Access Management", 
         "Gestione degli accessi privilegiati con controlli rigorosi", 
         "Art. 26", "HIGH", 1),
        ("Access Control", "AC-004", "Access Reviews", 
         "Review periodiche degli accessi e rimozione di privilegi non necessari", 
         "Art. 26", "MEDIUM", 2),
        ("Access Control", "AC-005", "Session Management", 
         "Gestione delle sessioni con timeout e controlli di sicurezza", 
         "Art. 26", "MEDIUM", 2)
    ]
    
    all_requirements = (governance_requirements + risk_requirements + 
                       incident_requirements + bc_requirements + 
                       data_requirements + access_requirements)
    
    for req in all_requirements:
        cursor.execute('''
            INSERT OR IGNORE INTO compliance_requirements 
            (category, requirement_code, title, description, nis2_article, risk_level, implementation_priority)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', req)
    
    conn.commit()
    print(f"✅ Popolati {len(all_requirements)} requisiti di compliance NIS2")
    conn.close()

if __name__ == "__main__":
    populate_compliance_requirements()
