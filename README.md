# 🛡️ Piattaforma NIS2 Supplier Assessment

Piattaforma completa per la valutazione della conformità dei fornitori secondo la **Direttiva NIS2** europea.

## 🚀 Quick Start

### Deployment Automatico
```bash
# Clone del repository
git clone <repository-url>
cd supplychain

# Deployment completo con un comando
./deploy.sh
```

### Requisiti Sistema
- **Docker** 20.10+
- **Docker Compose** 2.0+
- **OpenSSL** (per certificati SSL)
- **4GB RAM** minimo
- **10GB spazio disco** minimo

## 🏗️ Architettura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   Vue.js 3      ├────┤   FastAPI       ├────┤   MySQL/MariaDB │
│   TailwindCSS   │    │   Python 3.11   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │     Nginx       │
                    │  Reverse Proxy  │
                    │   Load Balancer │
                    └─────────────────┘
```

## 📋 Funzionalità Principali

### ✅ **Completate e Funzionanti**

#### 🔐 **Sistema di Autenticazione**
- Login JWT con refresh token
- Ruoli: Admin, Company, Supplier
- Gestione sessioni sicure
- Rate limiting anti-brute force

#### 👥 **Dashboard Admin**
- Panoramica globale della piattaforma
- Gestione aziende registrate
- Statistiche assessment completati
- Upload/gestione manifest questionario
- Creazione account aziende

#### 🏢 **Dashboard Aziende**
- Gestione fornitori
- Generazione link questionari personalizzati
- Monitoraggio assessment in tempo reale
- Download PDF Passaporto/Richiamo
- Statistiche conformità

#### 📱 **Questionario Mobile-First**
- Interfaccia responsive ottimizzata mobile
- Questionario strutturato NIS2 (57 domande, 13 sezioni)
- Auto-save progressi
- Navigazione intuitiva
- Validazione risposte in tempo reale

#### 🧠 **Engine di Valutazione**
- Algoritmo conformità NIS2 completo
- Logica ISO 27001 integrata
- Calcolo punteggi pesati
- Identificazione aree miglioramento
- Classificazione rischio automatica

#### 📄 **Generazione PDF**
- **Passaporto Digitale** (fornitori conformi)
- **Report di Richiamo** (fornitori non conformi)
- QR Code per verifica pubblica
- Template professionali
- Metadati compliance

#### 🔍 **Verifica Pubblica**
- Endpoint pubblico via QR code
- Verifica autenticità documenti
- Accesso anonimo sicuro
- Cache per performance

#### 🗄️ **Database & Persistence**
- Schema MySQL/MariaDB ottimizzato
- Modelli SQLAlchemy completi
- Migrazioni Alembic
- Backup automatici
- Indicizzazione performance

#### 🐳 **Containerizzazione**
- Docker multi-stage build
- Docker Compose orchestration
- Health checks automatici
- Networking isolato
- Volume persistence

#### 🌐 **Reverse Proxy & Load Balancing**
- Nginx configurazione production-ready
- SSL/TLS termination
- Rate limiting per endpoint
- Compressione gzip
- Cache statica

#### 📊 **Monitoring & Logging**
- Health checks integrati
- Structured logging
- Error tracking
- Performance metrics
- Backup automatici

## 🎯 **Questionario NIS2 Completo**

Il questionario include **57 domande** organizzate in **13 sezioni**:

### 📋 **Sezioni GSI (Governance e Sicurezza Informatica)**
- **GSI.03** - Piano per la gestione della continuità operativa
- **GSI.04** - Continuità operativa dei sistemi ICT
- **GSI.05** - Responsabilità in merito alla cybersecurity
- **GSI.06** - Piano di Formazione in materia di Cybersecurity
- **GSI.07** - Politiche di sicurezza informatica
- **GSI.08** - Processo di Risk Assessment
- **GSI.09** - Gestione degli incidenti di sicurezza
- **GSI.10** - Controllo degli accessi

### 🛡️ **Sezioni SIT (Sicurezza IT)**
- **SIT.01** - Sicurezza della rete
- **SIT.02** - Protezione dei dati
- **SIT.03** - Gestione delle vulnerabilità

### 🔧 **Sezioni SFA (Sicurezza Funzionale e Applicativa)**
- **SFA.01** - Sicurezza delle applicazioni
- **SFA.02** - Monitoraggio e logging

## 🚀 **Istruzioni di Deployment**

### 1. **Preparazione Ambiente**
```bash
# Copia template configurazione
cp docker/env.template .env

# Modifica variabili di ambiente
nano .env
```

### 2. **Configurazione Variabili (.env)**
```bash
# Database
DB_NAME=nis2_platform
DB_USER=nis2_user
DB_PASSWORD=your_secure_password

# Security
SECRET_KEY=your-super-secret-key-minimum-32-chars

# Email (opzionale)
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_USER=your-email@domain.com
EMAIL_SMTP_PASSWORD=your_app_password
```

### 3. **Deploy Automatico**
```bash
# Deployment completo
./deploy.sh

# Comandi disponibili
./deploy.sh deploy   # Deployment completo
./deploy.sh status   # Controllo servizi
./deploy.sh backup   # Backup dati
./deploy.sh logs     # Visualizza logs
./deploy.sh stop     # Ferma servizi
./deploy.sh restart  # Riavvia servizi
./deploy.sh update   # Aggiorna piattaforma
```

### 4. **Accesso Piattaforma**
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **Documentazione API**: http://localhost:8000/docs
- **Database**: localhost:3306

### 5. **Prima Configurazione**
1. Accedi come **admin** e crea la prima azienda
2. Carica il **manifest del questionario** (`questionario_nis2.json`)
3. Configura le **impostazioni email**
4. Testa la **generazione del primo questionario**

## 🔧 **Gestione e Manutenzione**

### Monitoraggio
```bash
# Status servizi
docker-compose ps

# Logs in tempo reale
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f database

# Risorse utilizzate
docker stats
```

### Backup e Restore
```bash
# Backup automatico
./deploy.sh backup

# Backup manuale database
docker-compose exec -T database mysqldump -u root -ppassword nis2_platform > backup.sql

# Restore database
docker-compose exec -T database mysql -u root -ppassword nis2_platform < backup.sql
```

### Aggiornamenti
```bash
# Aggiorna codice
git pull origin main

# Rebuild e restart
./deploy.sh update
```

## 🔒 **Sicurezza**

### Implementazioni di Sicurezza
- **JWT Authentication** con refresh token
- **Rate Limiting** su API e auth
- **CORS** configurato
- **Security Headers** (HSTS, CSP, X-Frame-Options)
- **Input Validation** su tutti gli endpoint
- **SQL Injection Prevention** (SQLAlchemy ORM)
- **XSS Protection** integrata
- **Password Hashing** (bcrypt)

### Raccomandazioni Production
1. **Cambia SECRET_KEY** in `.env`
2. **Usa certificati SSL validi** (Let's Encrypt)
3. **Configura firewall** (porta 80, 443, 22 only)
4. **Abilita backup automatici**
5. **Monitora logs** per anomalie
6. **Aggiorna regolarmente** dipendenze

## 📈 **Performance**

### Ottimizzazioni Implementate
- **Connection Pooling** database
- **Gzip Compression** nginx
- **Static File Caching**
- **Database Indexing**
- **Lazy Loading** frontend
- **Docker Multi-stage** builds

### Scalabilità
- **Horizontal Scaling**: Load balancer nginx
- **Database Scaling**: Read replicas supportate
- **Caching**: Redis integrato
- **CDN Ready**: Static assets ottimizzati

## 🐛 **Troubleshooting**

### Problemi Comuni

#### **Servizi non partono**
```bash
# Controlla logs
docker-compose logs

# Verifica porte occupate
netstat -tulpn | grep :80
netstat -tulpn | grep :8000
netstat -tulpn | grep :3306

# Restart completo
docker-compose down --volumes
docker-compose up -d
```

#### **Database connection error**
```bash
# Controlla database
docker-compose exec database mysql -u root -p

# Reset database
docker-compose down
docker volume rm nis2_platform_db_data
docker-compose up -d
```

#### **Frontend non carica**
```bash
# Rebuild frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### Log Analysis
```bash
# Backend errors
docker-compose logs backend | grep ERROR

# Nginx access logs
docker-compose exec frontend tail -f /var/log/nginx/access.log

# Database slow queries
docker-compose exec database mysql -u root -p -e "SHOW PROCESSLIST;"
```

## 🤝 **Contributi**

### Development Setup
```bash
# Backend development
cd src/backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend development
cd src/frontend
npm install
npm run dev
```

### Git Workflow
1. Fork repository
2. Create feature branch
3. Commit changes
4. Submit Pull Request

## 📜 **Licenza**

Questo progetto è rilasciato sotto licenza **MIT**.

## 📞 **Supporto**

Per supporto tecnico:
- 📧 **Email**: support@nis2platform.com
- 🐛 **Issues**: GitHub Issues
- 📖 **Docs**: `/docs` nella piattaforma

---

**🎯 Piattaforma NIS2 Supplier Assessment - Compliance Europea Semplificata** 