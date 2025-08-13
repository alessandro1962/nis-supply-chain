console.log('=== SCRIPT ASSESSMENT CARICATO ===');

const container = document.getElementById('questionsContainer');
console.log('Container trovato:', container);

if (!container) {
    console.error('ERRORE: Container questionsContainer non trovato!');
} else {
    console.log('Inizio fetch del questionario...');
    fetch('/questionario')
        .then(response => {
            console.log('Response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('=== DATI RICEVUTI ===');
            console.log('Data:', data);
            
            if (data.full_questionnaire && data.full_questionnaire.length > 0) {
                const questions = data.full_questionnaire;
                console.log('Numero totale domande:', questions.length);
                
                let html = '';
                const sections = [...new Set(questions.map(q => q.codice_argomento))];
                console.log('Sezioni trovate:', sections);
                
                sections.forEach(sectionCode => {
                    const sectionQuestions = questions.filter(q => q.codice_argomento === sectionCode);
                    console.log('Domande per sezione ' + sectionCode + ':', sectionQuestions.length);
                    
                    html += '<div class="bg-blue-50 p-6 rounded-lg mb-8">';
                    html += '<h2 class="text-xl font-semibold text-blue-900 mb-4">' + sectionCode + '</h2>';
                    html += '<p class="text-blue-700 mb-6">' + (sectionQuestions[0].titolo_argomento || 'Sezione di valutazione') + '</p>';
                    
                    sectionQuestions.forEach(question => {
                        html += '<div class="mb-6 p-4 bg-white rounded border">';
                        html += '<h3 class="font-semibold text-gray-900 mb-2">' + question.testo_domanda + '</h3>';
                        html += '<div class="space-y-2">';
                        html += '<label class="flex items-center"><input type="radio" name="q_' + question.codice_argomento + '_' + question.numero_domanda + '" value="si" class="mr-2"><span>Si</span></label>';
                        html += '<label class="flex items-center"><input type="radio" name="q_' + question.codice_argomento + '_' + question.numero_domanda + '" value="no" class="mr-2"><span>No</span></label>';
                        html += '<label class="flex items-center"><input type="radio" name="q_' + question.codice_argomento + '_' + question.numero_domanda + '" value="na" class="mr-2"><span>Non Applicabile</span></label>';
                        html += '</div>';
                        html += '</div>';
                    });
                    
                    html += '</div>';
                });
                
                console.log('HTML generato, lunghezza:', html.length);
                container.innerHTML = html;
                console.log('=== QUESTIONARIO CARICATO CON SUCCESSO ===');
            } else {
                console.error('ERRORE: Nessuna domanda trovata nel questionario');
                container.innerHTML = '<p class="text-red-500">Errore: Nessuna domanda trovata nel questionario</p>';
            }
        })
        .catch(error => {
            console.error('=== ERRORE CARICAMENTO QUESTIONARIO ===');
            console.error('Errore:', error);
            container.innerHTML = '<p class="text-red-500">Errore nel caricamento del questionario: ' + error.message + '</p>';
        });
}

function saveProgress() {
    console.log('Funzione saveProgress chiamata');
    alert('Progresso salvato!');
}

document.getElementById('assessmentForm').addEventListener('submit', function(e) {
    console.log('=== SUBMIT FORM ===');
    e.preventDefault();
    
    const formData = new FormData();
    formData.append('token', document.getElementById('assessmentToken').value);
    
    const selectedAnswers = document.querySelectorAll('input[type="radio"]:checked');
    console.log('Risposte selezionate:', selectedAnswers.length);
    selectedAnswers.forEach(input => {
        formData.append(input.name, input.value);
    });
    
    fetch('/api/assessment/submit', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log('Risposta submit:', data);
        if (data.success) {
            alert('Assessment completato con successo!');
            window.location.href = '/assessment-completed/' + document.getElementById('assessmentToken').value;
        } else {
            alert('Errore: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Errore submit:', error);
        alert('Errore nell\'invio dell\'assessment');
    });
});

console.log('=== SCRIPT ASSESSMENT COMPLETATO ===');
