// JavaScript per la gestione dei fornitori

// Funzione per aprire il modal di aggiunta fornitore
function openAddSupplierModal() {
    document.getElementById('addSupplierModal').classList.remove('hidden');
}

// Funzione per chiudere il modal di aggiunta fornitore
function closeAddSupplierModal() {
    document.getElementById('addSupplierModal').classList.add('hidden');
    document.getElementById('addSupplierForm').reset();
}

// Funzione per inviare assessment
async function sendAssessment(supplierId) {
    const btn = document.querySelector(`[onclick="sendAssessment(${supplierId})"]`);
    const originalText = btn.textContent;
    
    btn.disabled = true;
    btn.textContent = 'Invio in corso...';
    
    try {
        const response = await fetch(`/api/send-assessment/${supplierId}`, {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Mostra il link generato
            const linkContainer = document.getElementById(`link-${supplierId}`);
            const linkText = linkContainer.querySelector('.link-text');
            linkText.textContent = result.assessment_link;
            linkContainer.style.display = 'block';
            
            // Disabilita il bottone
            btn.textContent = '✅ Inviato';
            btn.disabled = true;
            btn.className = 'action-btn btn-success';
            
        } else {
            alert('Errore durante l\'invio dell\'assessment');
        }
    } catch (error) {
        alert('Errore di connessione');
    } finally {
        if (!btn.disabled) {
            btn.textContent = originalText;
            btn.disabled = false;
        }
    }
}

// Funzione per eliminare fornitore
function deleteSupplier(supplierId) {
    if (confirm('Sei sicuro di voler eliminare questo fornitore?')) {
        fetch(`/api/suppliers/${supplierId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Errore nell\'eliminazione del fornitore');
            }
        })
        .catch(error => {
            console.error('Errore:', error);
            alert('Errore nell\'eliminazione del fornitore');
        });
    }
}

// Gestione del form di aggiunta fornitore
document.addEventListener('DOMContentLoaded', function() {
    const addSupplierForm = document.getElementById('addSupplierForm');
    if (addSupplierForm) {
        addSupplierForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(addSupplierForm);
            
            try {
                const response = await fetch('/api/suppliers', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    alert('Fornitore aggiunto con successo!');
                    location.reload();
                } else {
                    alert('Errore nell\'aggiunta del fornitore');
                }
            } catch (error) {
                console.error('Errore:', error);
                alert('Errore nell\'aggiunta del fornitore');
            }
        });
    }
    
    // Chiudi modal cliccando fuori
    const modal = document.getElementById('addSupplierModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                closeAddSupplierModal();
            }
        });
    }
});

// Funzione per filtrare fornitori
function filterSuppliers(filter) {
    const supplierCards = document.querySelectorAll('.supplier-card');
    
    supplierCards.forEach(card => {
        const complianceScore = card.querySelector('.score-badge');
        const riskLevel = card.querySelector('.risk-badge');
        
        let show = true;
        
        if (filter === 'conformi') {
            const score = parseInt(complianceScore.textContent);
            show = score >= 70;
        } else if (filter === 'non-conformi') {
            const score = parseInt(complianceScore.textContent);
            show = score < 70;
        } else if (filter === 'rischio-alto') {
            show = riskLevel.textContent.includes('Alto') || riskLevel.textContent.includes('Critico');
        }
        
        card.style.display = show ? 'block' : 'none';
    });
}

// Funzione per cercare fornitori
function searchSuppliers(query) {
    const supplierCards = document.querySelectorAll('.supplier-card');
    const searchTerm = query.toLowerCase();
    
    supplierCards.forEach(card => {
        const supplierName = card.querySelector('.supplier-name').textContent.toLowerCase();
        const supplierEmail = card.querySelector('.supplier-email').textContent.toLowerCase();
        
        const matches = supplierName.includes(searchTerm) || supplierEmail.includes(searchTerm);
        card.style.display = matches ? 'block' : 'none';
    });
}

function copyLink(supplierId) {
    const linkText = document.querySelector(`#link-${supplierId} .link-text`).textContent;
    navigator.clipboard.writeText(linkText).then(() => {
        const copyBtn = document.querySelector(`#link-${supplierId} .copy-btn`);
        const originalText = copyBtn.textContent;
        copyBtn.textContent = '✅ Copiato!';
        setTimeout(() => {
            copyBtn.textContent = originalText;
        }, 2000);
    });
}
