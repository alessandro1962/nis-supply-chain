import json

def generate_complete_manifest():
    """Genera il manifest completo basato sul questionario NIS2 originale"""
    
    # Carica il questionario originale
    with open("questionario_nis2.json", "r", encoding="utf-8") as f:
        questions = json.load(f)
    
    # Raggruppa le domande per argomento
    topics = {}
    for question in questions:
        codice = question["codice_argomento"]
        if codice not in topics:
            topics[codice] = {
                "name": question["titolo_argomento"],
                "questions": []
            }
        
        topics[codice]["questions"].append({
            "id": f"{codice}_{question['numero_domanda']}",
            "text": question["testo_domanda"],
            "weight": 1.0,  # Peso standard
            "essential": True  # Tutte le domande sono essenziali per ora
        })
    
    # Crea il manifest
    manifest = {
        "version": "1.0",
        "name": "NIS2 Supplier Assessment Rules - Complete",
        "description": "Regole di valutazione conformità NIS2 per fornitori - Questionario completo",
        "scoring_defaults": {
            "threshold": 0.80,
            "partial_weight": 0.5,
            "iso27001_auto_percentage": 0.90
        },
        "topics": []
    }
    
    # Aggiungi i topic al manifest
    for codice, topic_data in topics.items():
        manifest["topics"].append({
            "code": codice,
            "name": topic_data["name"],
            "essential": True,
            "questions": topic_data["questions"]
        })
    
    # Regole ISO 27001 (per ora vuote, da configurare manualmente)
    manifest["iso27001_rules"] = {
        "enabled": True,
        "auto_questions": []
    }
    
    # Template per i report
    manifest["report_templates"] = {
        "passport": {
            "title": "Passaporto Digitale Fornitore NIS2",
            "subtitle": "Certificazione di Conformità",
            "color": "#22c55e",
            "icon": "✅"
        },
        "recall": {
            "title": "Richiamo Conformità NIS2",
            "subtitle": "Azioni Correttive Necessarie",
            "color": "#ef4444",
            "icon": "⚠️"
        }
    }
    
    # Salva il manifest completo
    with open("questionario_rules_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Manifest generato con {len(questions)} domande in {len(topics)} sezioni")
    print("📁 File salvato: questionario_rules_manifest.json")

if __name__ == "__main__":
    generate_complete_manifest()
