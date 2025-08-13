import json

def generate_questionnaire_html():
    # Carica il questionario JSON
    with open('questionario_nis2.json', 'r', encoding='utf-8') as f:
        questions = json.load(f)
    
    # Raggruppa le domande per sezione
    sections = {}
    for question in questions:
        codice = question['codice_argomento']
        if codice not in sections:
            sections[codice] = {
                'titolo': question['titolo_argomento'],
                'questions': []
            }
        sections[codice]['questions'].append(question)
    
    # Genera l'HTML per ogni sezione
    html_sections = []
    
    for codice, section_data in sections.items():
        # Header della sezione
        section_html = f'''
            <!-- {codice} - {section_data['titolo']} -->
            <div class="section-header">
                <div class="section-title">{codice} - {section_data['titolo']}</div>
                <div class="section-description">Valutazione conformità {section_data['titolo'].lower()}</div>
            </div>
        '''
        
        # Domande della sezione
        for question in section_data['questions']:
            question_num = question['numero_domanda']
            question_text = question['testo_domanda']
            field_name = f"q_{codice}_{question_num}"
            
            question_html = f'''
            <div class="question-group">
                <div class="question-title">{question_num}. {question_text}</div>
                <div class="options">
                    <label class="option">
                        <input type="radio" name="{field_name}" value="si" required>
                        <span class="option-label">Sì</span>
                    </label>
                    <label class="option">
                        <input type="radio" name="{field_name}" value="no" required>
                        <span class="option-label">No</span>
                    </label>
                    <label class="option">
                        <input type="radio" name="{field_name}" value="na" required>
                        <span class="option-label">Non Applicabile</span>
                    </label>
                </div>
            </div>
            '''
            section_html += question_html
        
        html_sections.append(section_html)
    
    return '\n'.join(html_sections)

if __name__ == "__main__":
    html_content = generate_questionnaire_html()
    print("Questionario HTML generato con successo!")
    print(f"Numero totale di sezioni: {len(html_content.split('section-header')) - 1}")
    
    # Salva in un file temporaneo per copiare nel template
    with open('questionnaire_sections.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("Sezioni salvate in questionnaire_sections.html")
