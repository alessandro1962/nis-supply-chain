# Piattaforma NIS2 Supplier Assessment - Script di Deployment Windows

Write-Host "🚀 Deployment Piattaforma NIS2 Supplier Assessment" -ForegroundColor Blue
Write-Host "==================================================" -ForegroundColor Blue

# Controllo Docker
Write-Host "[INFO] Controllo prerequisiti..." -ForegroundColor Blue
try {
    docker --version | Out-Null
    Write-Host "[SUCCESS] Docker trovato" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Docker non installato!" -ForegroundColor Red
    exit 1
}

# Setup environment
Write-Host "[INFO] Setup variabili di ambiente..." -ForegroundColor Blue
if (-not (Test-Path ".env")) {
    if (Test-Path "docker/env.template") {
        Copy-Item "docker/env.template" ".env"
        Write-Host "[WARNING] File .env creato da template. Modificalo se necessario!" -ForegroundColor Yellow
    }
}

# Crea directory
Write-Host "[INFO] Creazione directory..." -ForegroundColor Blue
New-Item -ItemType Directory -Force -Path "docker/ssl" | Out-Null
New-Item -ItemType Directory -Force -Path "logs" | Out-Null
New-Item -ItemType Directory -Force -Path "backups" | Out-Null

# Certificati dummy
"dummy cert" | Out-File -FilePath "docker/ssl/cert.pem"
"dummy key" | Out-File -FilePath "docker/ssl/key.pem"

# Deployment
Write-Host "[INFO] Avvio deployment Docker..." -ForegroundColor Blue
docker-compose down --remove-orphans 2>$null
docker-compose build --no-cache
docker-compose up -d

Write-Host "[INFO] Attendendo avvio servizi..." -ForegroundColor Blue
Start-Sleep -Seconds 45

# Test servizi
Write-Host "[INFO] Test servizi..." -ForegroundColor Blue
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 10
    Write-Host "[SUCCESS] Backend: OK" -ForegroundColor Green
}
catch {
    Write-Host "[WARNING] Backend: potrebbe non essere ancora pronto" -ForegroundColor Yellow
}

try {
    $response = Invoke-WebRequest -Uri "http://localhost/" -TimeoutSec 10
    Write-Host "[SUCCESS] Frontend: OK" -ForegroundColor Green
}
catch {
    Write-Host "[WARNING] Frontend: potrebbe non essere ancora pronto" -ForegroundColor Yellow
}

# Informazioni finali
Write-Host ""
Write-Host "[SUCCESS] Deployment completato!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 ACCESSO ALLA PIATTAFORMA:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost" -ForegroundColor White
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   Documentazione API: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "📊 COMANDI UTILI:" -ForegroundColor Cyan
Write-Host "   Status: docker-compose ps" -ForegroundColor White
Write-Host "   Logs: docker-compose logs -f" -ForegroundColor White
Write-Host "   Stop: docker-compose down" -ForegroundColor White
Write-Host ""
Write-Host "[WARNING] PRIMA CONFIGURAZIONE:" -ForegroundColor Yellow
Write-Host "1. Accedi come admin al backend" -ForegroundColor Yellow
Write-Host "2. Carica il manifest del questionario" -ForegroundColor Yellow
Write-Host "3. Crea la prima azienda" -ForegroundColor Yellow 