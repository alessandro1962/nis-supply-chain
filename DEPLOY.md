# Deploy su DigitalOcean

## Opzione 1: DigitalOcean App Platform (Raccomandato)

### 1. Preparazione
1. Crea un repository GitHub con il codice
2. Assicurati che tutti i file siano committati

### 2. Deploy su DigitalOcean
1. Vai su [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
2. Clicca "Create App"
3. Connetti il tuo repository GitHub
4. Seleziona il branch `main`
5. DigitalOcean rileverà automaticamente che è un'app Python

### 3. Configurazione
- **Build Command**: `pip install -r requirements.txt`
- **Run Command**: `uvicorn main_dev:app --host 0.0.0.0 --port $PORT`
- **Environment**: Python

### 4. Variabili d'ambiente
Aggiungi queste variabili d'ambiente:
- `SECRET_KEY`: Una chiave segreta sicura per JWT
- `DATABASE_URL`: `sqlite:///./nis2_supply_chain.db`

## Opzione 2: DigitalOcean Droplet con Docker

### 1. Crea un Droplet
1. Vai su DigitalOcean Droplets
2. Crea un nuovo Droplet con Ubuntu
3. Seleziona "Docker" come image

### 2. Deploy con Docker
```bash
# SSH nel droplet
ssh root@YOUR_DROPLET_IP

# Clona il repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO

# Build e run del container
docker build -t nis2-supply-chain .
docker run -d -p 80:8000 --name nis2-app nis2-supply-chain
```

### 3. Configurazione Nginx (Opzionale)
```bash
# Installa Nginx
apt update
apt install nginx

# Configura il reverse proxy
cat > /etc/nginx/sites-available/nis2 << EOF
server {
    listen 80;
    server_name YOUR_DOMAIN.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

# Abilita il sito
ln -s /etc/nginx/sites-available/nis2 /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

## Note importanti

1. **Database**: L'app usa SQLite locale. Per produzione, considera PostgreSQL
2. **SSL**: Configura HTTPS con Let's Encrypt
3. **Backup**: Configura backup automatici del database
4. **Monitoring**: Aggiungi monitoring per uptime e performance

## Troubleshooting

- **Porta non accessibile**: Verifica che il firewall permetta la porta 80/443
- **Database errori**: Controlla i permessi del file SQLite
- **Static files**: Verifica che la directory `static/` sia presente
