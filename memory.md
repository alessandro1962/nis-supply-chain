# Memoria del Progetto - Piattaforma di Valutazione Fornitori NIS2

## Scopo del Progetto
Realizzare una piattaforma web COMPLETA per aziende soggette alla Direttiva NIS2 (soggetti essenziali o importanti) per:
- Gestione anagrafica aziendale e fornitori
- Invio questionario personalizzato NIS2 ai fornitori
- Ricezione risposte e calcolo conformità secondo manifest JSON
- Generazione PDF Passaporto Digitale Fornitore NIS2 (positivo) o PDF Richiamo (negativo)
- QR code nei PDF per verifica pubblica online

## IMPORTANTE: NON DEMO - PIATTAFORMA COMPLETA
L'utente NON vuole una demo o un prototipo, ma la PIATTAFORMA COMPLETA e FUNZIONANTE con:
- Frontend Vue.js completo con interfaccia utente
- Backend FastAPI completo con tutte le API
- Database MySQL/MariaDB con tutti i dati
- Sistema di autenticazione completo
- Generazione PDF completa
- QR code funzionanti
- Tutte le funzionalità operative

## Stack Tecnologico Scelto
- **Frontend**: Vue.js con TailwindCSS
- **Backend**: Python FastAPI
- **Database**: MySQL/MariaDB
- **Hosting**: Server Ubuntu DigitalOcean
- **PDF generation**: WeasyPrint/ReportLab
- **QR code**: libreria qrcode Python

## Architettura Ruoli

### Amministratore
- Login e gestione piattaforma
- Creazione anagrafica aziende clienti (ragione sociale, indirizzo, città, email, tipo soggetto NIS2)
- Generazione credenziali per accesso azienda (username/password)
- Visualizzazione globale aziende e fornitori

### Azienda Cliente
- Login con credenziali fornite
- Gestione anagrafica fornitori
- Generazione link univoco questionario per fornitore
- Ricezione notifiche compilazione questionario
- Visione valutazioni fornitore
- Download PDF (Passaporto o Richiamo)

### Fornitore
- Accesso tramite link univoco (no registrazione)
- Compilazione questionario (SÌ/NO/Parziale)
- Domanda extra ISO/IEC 27001 (se SÌ → algoritmo preimposta 90% risposte)
- Invio risposte → salvataggio DB

## Flusso Operativo
1. Admin crea azienda → genera credenziali
2. Azienda accede → inserisce fornitori
3. Azienda genera questionario → sistema crea link univoco (UUIDv4/SHA256)
4. Fornitore riceve link → compila → submit → dati salvati
5. Piattaforma elabora con questmio_RULES_MANIFEST.json:
   - Calcola punteggio (threshold default: 0,80)
   - Genera PDF PASS (positivo) o Richiamo (negativo)
   - Include QR code per verifica pubblica
6. Azienda scarica PDF o visualizza online

## Logica di Valutazione

### Algoritmo di Calcolo
```python
def calcola_esito(risposte, manifest):
    punteggio_totale = 0
    punteggio_massimo = 0
    essenziali_soddisfatte = true
    
    for topic in manifest.topics:
        for domanda in topic.questions:
            peso = domanda.weight
            punteggio_massimo += peso
            risposta = risposte[domanda.id]
            
            if risposta == "SI":
                punteggio_totale += peso
            elif risposta == "PARZIALE":
                punteggio_totale += peso * 0.5
                
            if domanda.essential and risposta != "SI":
                essenziali_soddisfatte = false
                
    punteggio_finale = punteggio_totale / punteggio_massimo
    
    if essenziali_soddisfatte == false:
        esito = "NEGATIVO"
    else if punteggio_finale >= manifest.scoring_defaults.threshold:
        esito = "POSITIVO"
    else:
        esito = "NEGATIVO"
        
    return esito, punteggio_finale, essenziali_ok, miglioramenti
```

### Regole Questionario
- Campi risposta: SI, NO, PARZIALE (parziale = 0,5 punti)
- Domande Essenziali: tutte SÌ per esito positivo
- Threshold punteggio: 0,80 (80% del massimo)
- Certificazione ISO 27001: imposta automaticamente SÌ a 90% domande

## QR Code e Verifica Pubblica
- URL: `https://<dominio>/v/passport/<hash>`
- Mostra: Stato fornitore, sintesi risposte, punteggio, data emissione/scadenza
- Validità: 14 giorni
- Nessun dato sensibile extra rispetto al PDF

## API Endpoints
- `POST /admin/create-company`
- `POST /company/create-supplier`
- `POST /company/generate-questionnaire`
- `GET /supplier/questionnaire/{hash}`
- `POST /supplier/submit`
- `GET /company/report/{supplier_id}`
- `GET /v/passport/{hash}` (pubblico)
- `POST /admin/upload-manifest`

## Output
- **PDF PASSAPORTO** (positivo): Dati fornitore/azienda, esito, punti di forza, suggerimenti, QR code
- **PDF RICHIAMO** (negativo): Dati fornitore/azienda, punti da correggere, QR code
- **Pagina web pubblica** per QR code
- **Dashboard** con stato fornitori

## Design/UI
- TailwindCSS interfaccia moderna
- Mobile-first per modulo fornitore
- Colori personalizzabili
- Indicatori stato (verde → conforme, rosso → non conforme)

## Sicurezza
- Hash univoco randomico per ogni passaporto
- Token scadono dopo 14 giorni
- HTTPS obbligatorio
- Ruoli e permessi isolati
- Prevenzione CSRF/XSS
- Backup DB giornaliero

## Sezioni Questionario Dettagliate

### GSI (Gestione Sicurezza Informazioni)
- GSI.03: Piano gestione continuità operativa
- GSI.04: Continuità operativa sistemi ICT
- GSI.05: Responsabilità cybersecurity
- GSI.06: Responsabilità protezione dati personali
- GSI.07: Azioni formazione e consapevolezza
- GSI.08: Inventari beni aziendali
- GSI.09: Contratti terze parti
- GSI.10: Rischio cybersecurity
- GSI.11: Verifica conformità gestione
- GSI.12: Processo sviluppo sicuro software
- GSI.13: Budget cybersecurity
- GSI.15: Screening del personale
- GSI.16: Certificazioni sicurezza informazioni

### SIT (Sistemi Informativi e Tecnologie)
- SIT.01: Dispositivi protezione traffico rete
- SIT.02: Reti wireless
- SIT.03: Backup
- SIT.04: Accessi logici utenti
- SIT.05: Accessi logici amministratori
- SIT.06: Accessi logici da remoto
- SIT.07: Utenti sistema operativo
- SIT.08: Patch di sicurezza
- SIT.09: Vulnerability assessment
- SIT.10: Penetration test
- SIT.11: Gestione log
- SIT.12: Dati memorizzati (data at rest)
- SIT.13: Dati scambiati (data in transit)
- SIT.14: Protezione endpoint
- SIT.15: Sistemi protezione locali
- SIT.16: Sistemi protezione rete
- SIT.18: Gestione incidenti cybersecurity
- SIT.19: Notifica incidenti
- SIT.20: Cancellazione sicura dati
- SIT.21: Trattamento dati personali
- SIT.22: Cambiamenti sistemi informativi
- SIT.23: Configurazione sistemi operativi
- SIT.24: Sistemi monitoraggio
- SIT.25: Architettura applicativa

### SFA (Sicurezza Fisica e Ambientale)
- SFA.01: Accesso perimetro organizzazione
- SFA.02: Accesso locali server
- SFA.03: Controllo temperatura/umidità
- SFA.04: Continuità alimentazione elettrica
- SFA.05: Protezione antincendio
- SFA.06: Archivi cartacei

## Note Implementative
- Ogni sezione ha regole di conformità specifiche
- Algoritmo ISO 27001 preimposta risposte per certificati
- Sistema di pesatura domande con punteggi differenziati
- Gestione domande essenziali vs opzionali
- Tracking temporale per scadenze e validità 