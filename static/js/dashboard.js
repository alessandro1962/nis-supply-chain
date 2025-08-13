// Dashboard JavaScript per NIS2 Supply Chain Platform

let complianceChart = null;
let trendChart = null;
let riskChart = null;

// Funzione per creare il grafico a torta della conformità
function createComplianceChart(conformi, nonConformi) {
    const ctx = document.getElementById('complianceChart').getContext('2d');
    
    if (complianceChart) {
        complianceChart.destroy();
    }
    
    complianceChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Conformi NIS2', 'Non Conformi'],
            datasets: [{
                data: [conformi, nonConformi],
                backgroundColor: [
                    'rgba(34, 197, 94, 0.8)',
                    'rgba(239, 68, 68, 0.8)'
                ],
                borderColor: [
                    'rgba(34, 197, 94, 1)',
                    'rgba(239, 68, 68, 1)'
                ],
                borderWidth: 2,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: ${context.parsed} (${percentage}%)`;
                        }
                    }
                }
            },
            animation: {
                animateRotate: true,
                duration: 2000
            }
        }
    });
}

// Funzione per creare il grafico del trend temporale
function createTrendChart() {
    const ctx = document.getElementById('trendChart').getContext('2d');
    
    if (trendChart) {
        trendChart.destroy();
    }
    
    // Genera dati di esempio per gli ultimi 30 giorni
    const labels = [];
    const data = [];
    const today = new Date();
    
    for (let i = 29; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('it-IT', { day: '2-digit', month: '2-digit' }));
        
        // Simula dati realistici con trend crescente
        const baseValue = Math.random() * 3 + 1;
        const trend = Math.sin(i * 0.2) * 0.5 + 1;
        data.push(Math.round(baseValue * trend));
    }
    
    trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Assessment Completati',
                data: data,
                borderColor: 'rgba(59, 130, 246, 1)',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: 'rgba(59, 130, 246, 1)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#fff',
                    bodyColor: '#fff',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    borderWidth: 1
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    ticks: {
                        stepSize: 1
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Funzione per creare il grafico dei rischi
function createRiskChart() {
    const ctx = document.getElementById('riskChart').getContext('2d');
    
    if (riskChart) {
        riskChart.destroy();
    }
    
    // Usa i dati reali se disponibili, altrimenti usa dati di esempio
    const riskData = window.riskData || {'Basso': 0, 'Medio': 0, 'Alto': 0, 'Critico': 0};
    
    riskChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Basso', 'Medio', 'Alto', 'Critico'],
            datasets: [{
                label: 'Fornitori per Livello di Rischio',
                data: [riskData['Basso'], riskData['Medio'], riskData['Alto'], riskData['Critico']],
                backgroundColor: [
                    'rgba(34, 197, 94, 0.8)',
                    'rgba(251, 191, 36, 0.8)',
                    'rgba(249, 115, 22, 0.8)',
                    'rgba(239, 68, 68, 0.8)'
                ],
                borderColor: [
                    'rgba(34, 197, 94, 1)',
                    'rgba(251, 191, 36, 1)',
                    'rgba(249, 115, 22, 1)',
                    'rgba(239, 68, 68, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Inizializzazione dei grafici
document.addEventListener('DOMContentLoaded', function() {
    // Ottieni i dati reali dai contatori
    const totalSuppliers = parseInt(document.querySelector('[data-target]').getAttribute('data-target')) || 0;
    const conformi = parseInt(document.querySelectorAll('[data-target]')[1].getAttribute('data-target')) || 0;
    const nonConformi = parseInt(document.querySelectorAll('[data-target]')[2].getAttribute('data-target')) || 0;
    
    // Crea i grafici con dati reali
    createComplianceChart(conformi, nonConformi);
    createTrendChart();
    createRiskChart();
    
    // Aggiorna i contatori una sola volta
    updateCounters();
});

    // Funzione per aggiornare i contatori
    function updateCounters() {
        const counters = document.querySelectorAll('.counter');
        counters.forEach(counter => {
            const target = parseInt(counter.getAttribute('data-target'));
            counter.textContent = target;
        });
    }

// Funzione per aprire il modal del certificato
function openCertificateModal(supplierId) {
    const modal = document.getElementById('certificateModal');
    modal.classList.remove('hidden');
    
    // Carica i dati del certificato
    loadCertificateData(supplierId);
}

// Funzione per chiudere il modal
function closeCertificateModal() {
    const modal = document.getElementById('certificateModal');
    modal.classList.add('hidden');
}

// Funzione per caricare i dati del certificato
function loadCertificateData(supplierId) {
    // Simula il caricamento dei dati
    const certificateData = {
        supplierName: 'Fornitore ' + supplierId,
        complianceScore: 85,
        assessmentDate: new Date().toLocaleDateString('it-IT'),
        validUntil: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toLocaleDateString('it-IT')
    };
    
    document.getElementById('certificateSupplierName').textContent = certificateData.supplierName;
    document.getElementById('certificateScore').textContent = certificateData.complianceScore + '%';
    document.getElementById('certificateDate').textContent = certificateData.assessmentDate;
    document.getElementById('certificateValidUntil').textContent = certificateData.validUntil;
}
