#!/bin/bash

# Script di deployment per DigitalOcean Ubuntu
# Esegui come root o con sudo

set -e

echo "🚀 Iniziando deployment NIS2 Supply Chain Platform su DigitalOcean..."

# Aggiorna il sistema
echo "📦 Aggiornando il sistema..."
apt-get update && apt-get upgrade -y

# Installa dipendenze di sistema
echo "🔧 Installando dipendenze di sistema..."
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    software-properties-common \
    git \
    unzip \
    wget

# Installa Docker
echo "🐳 Installando Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Installa Docker Compose
echo "📋 Installando Docker Compose..."
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Crea directory per l'applicazione
echo "📁 Creando directory per l'applicazione..."
mkdir -p /opt/nis2-platform
cd /opt/nis2-platform

# Clona il repository (sostituisci con il tuo repository)
echo "📥 Clonando il repository..."
# git clone https://github.com/tuousername/nis2-platform.git .
# Oppure copia i file manualmente

# Crea directory per i dati persistenti
mkdir -p data logs ssl

# Crea file .env per le variabili d'ambiente
echo "⚙️ Configurando variabili d'ambiente..."
cat > .env << EOF
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///data/nis2_supply_chain.db
ENVIRONMENT=production
EOF

# Configura firewall
echo "🔥 Configurando firewall..."
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Installa Certbot per SSL
echo "🔒 Installando Certbot per SSL..."
apt-get install -y certbot python3-certbot-nginx

# Avvia l'applicazione
echo "🚀 Avviando l'applicazione..."
docker-compose up -d

# Configura SSL con Let's Encrypt (da eseguire dopo aver configurato il dominio)
echo "🔐 Per configurare SSL, esegui:"
echo "certbot --nginx -d tuodominio.com"

# Configura backup automatico
echo "💾 Configurando backup automatico..."
cat > /etc/cron.daily/nis2-backup << 'EOF'
#!/bin/bash
cd /opt/nis2-platform
tar -czf /backup/nis2-backup-$(date +%Y%m%d).tar.gz data/
find /backup -name "nis2-backup-*.tar.gz" -mtime +7 -delete
EOF
chmod +x /etc/cron.daily/nis2-backup

# Configura log rotation
echo "📝 Configurando log rotation..."
cat > /etc/logrotate.d/nis2-platform << EOF
/opt/nis2-platform/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 root root
}
EOF

echo "✅ Deployment completato!"
echo "🌐 L'applicazione è disponibile su: http://$(curl -s ifconfig.me)"
echo "📊 Per monitorare i log: docker-compose logs -f"
echo "🔄 Per aggiornare: cd /opt/nis2-platform && docker-compose pull && docker-compose up -d" 