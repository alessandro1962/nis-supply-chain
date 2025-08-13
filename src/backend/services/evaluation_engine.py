from typing import Dict, Any, List
from database import ComplianceResult

class EvaluationEngine:
    """
    Motore di valutazione della conformità NIS2
    Implementa l'algoritmo di calcolo specificato nel memory.md
    """
    
    def calculate_compliance(self, responses: Dict[str, str], manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcola l'esito della conformità basato su risposte e manifest
        
        Args:
            responses: Dizionario con risposte del fornitore {question_id: "SI"|"NO"|"PARZIALE"}
            manifest: Dizionario con configurazione questionario
            
        Returns:
            Dict con risultati della valutazione
        """
        punteggio_totale = 0.0
        punteggio_massimo = 0.0
        essenziali_soddisfatte = True
        improvement_areas = []
        strengths = []
        
        # Estrai configurazioni
        threshold = manifest.get("scoring_defaults", {}).get("threshold", 0.80)
        response_values = manifest.get("scoring_defaults", {}).get("response_values", {
            "SI": 1.0,
            "NO": 0.0,
            "PARZIALE": 0.5
        })
        
        # Elabora tutti i topic e sezioni
        for topic in manifest.get("topics", []):
            for section in topic.get("sections", []):
                section_score = 0.0
                section_max = 0.0
                section_essential_passed = True
                
                for question in section.get("questions", []):
                    question_id = question["id"]
                    peso = question.get("weight", 1.0)
                    is_essential = question.get("essential", False)
                    
                    punteggio_massimo += peso
                    section_max += peso
                    
                    # Ottieni risposta (default a "NO" se mancante)
                    risposta = responses.get(question_id, "NO")
                    
                    # Calcola punteggio per questa domanda
                    valore_risposta = response_values.get(risposta, 0.0)
                    punteggio_domanda = peso * valore_risposta
                    
                    punteggio_totale += punteggio_domanda
                    section_score += punteggio_domanda
                    
                    # Controlla domande essenziali
                    if is_essential and risposta != "SI":
                        essenziali_soddisfatte = False
                        section_essential_passed = False
                        
                        # Aggiungi area di miglioramento
                        improvement_areas.append({
                            "question_id": question_id,
                            "question_text": question["text"],
                            "section": section["title"],
                            "response": risposta,
                            "required": "SI",
                            "feedback": question.get("negative_feedback", ""),
                            "is_essential": True
                        })
                    
                    # Aggiungi punti di forza per risposte positive
                    if risposta == "SI":
                        strengths.append({
                            "question_id": question_id,
                            "question_text": question["text"],
                            "section": section["title"],
                            "feedback": question.get("positive_feedback", ""),
                            "weight": peso
                        })
                    elif risposta == "NO":
                        # Aggiungi area di miglioramento per risposte negative
                        improvement_areas.append({
                            "question_id": question_id,
                            "question_text": question["text"],
                            "section": section["title"],
                            "response": risposta,
                            "suggested": "SI",
                            "feedback": question.get("negative_feedback", ""),
                            "is_essential": is_essential
                        })
                
                # Controlla regole di conformità specifiche per sezione
                compliance_rule = section.get("compliance_rule", "")
                if compliance_rule and not self._evaluate_section_compliance(
                    section, responses, compliance_rule
                ):
                    # Sezione non conforme secondo regole specifiche
                    for question in section.get("questions", []):
                        if responses.get(question["id"], "NO") != "SI":
                            improvement_areas.append({
                                "question_id": question["id"],
                                "question_text": question["text"],
                                "section": section["title"],
                                "response": responses.get(question["id"], "NO"),
                                "required": "SI",
                                "feedback": f"Richiesto per conformità sezione: {section['title']}",
                                "is_essential": False,
                                "section_rule": compliance_rule
                            })
        
        # Calcola punteggio finale percentuale
        punteggio_finale = punteggio_totale / punteggio_massimo if punteggio_massimo > 0 else 0
        
        # Determina esito finale
        if not essenziali_soddisfatte:
            esito = ComplianceResult.NEGATIVE
        elif punteggio_finale >= threshold:
            esito = ComplianceResult.POSITIVE
        else:
            esito = ComplianceResult.NEGATIVE
        
        # Ordina aree di miglioramento per priorità (essenziali prima)
        improvement_areas.sort(key=lambda x: (not x.get("is_essential", False), x.get("question_id", "")))
        
        # Ordina punti di forza per peso (più importanti prima)
        strengths.sort(key=lambda x: x.get("weight", 0), reverse=True)
        
        return {
            "compliance_result": esito,
            "total_score": punteggio_totale,
            "max_score": punteggio_massimo,
            "score_percentage": round(punteggio_finale * 100, 2),
            "essential_questions_passed": essenziali_soddisfatte,
            "improvement_areas": improvement_areas[:20],  # Limita a 20 più importanti
            "strengths": strengths[:15],  # Limita a 15 punti di forza principali
            "threshold_met": punteggio_finale >= threshold,
            "evaluation_details": {
                "threshold_used": threshold,
                "total_questions": len([q for topic in manifest.get("topics", []) 
                                     for section in topic.get("sections", []) 
                                     for q in section.get("questions", [])]),
                "answered_questions": len([r for r in responses.values() if r in ["SI", "NO", "PARZIALE"]]),
                "essential_questions_total": len([q for topic in manifest.get("topics", []) 
                                                for section in topic.get("sections", []) 
                                                for q in section.get("questions", []) 
                                                if q.get("essential", False)]),
                "positive_responses": len([r for r in responses.values() if r == "SI"]),
                "negative_responses": len([r for r in responses.values() if r == "NO"]),
                "partial_responses": len([r for r in responses.values() if r == "PARZIALE"])
            }
        }
    
    def _evaluate_section_compliance(self, section: Dict[str, Any], responses: Dict[str, str], rule: str) -> bool:
        """
        Valuta la conformità di una sezione secondo regole specifiche
        
        Args:
            section: Dati della sezione
            responses: Risposte del fornitore
            rule: Regola di conformità (es. "AFFIDABILE se (Q1 == SÌ) AND (Q2 == SÌ)")
            
        Returns:
            bool: True se la sezione è conforme
        """
        try:
            # Parsing semplificato delle regole più comuni
            if "percentuale di SÌ ≥ 70%" in rule:
                return self._evaluate_percentage_rule(section, responses, 0.70)
            elif "percentuale di SÌ ≥ 80%" in rule:
                return self._evaluate_percentage_rule(section, responses, 0.80)
            elif "AND" in rule:
                return self._evaluate_and_rule(section, responses, rule)
            elif "OR" in rule:
                return self._evaluate_or_rule(section, responses, rule)
            else:
                # Default: almeno 80% di risposte positive
                return self._evaluate_percentage_rule(section, responses, 0.80)
                
        except Exception:
            # In caso di errore nel parsing, usa regola default conservativa
            return self._evaluate_percentage_rule(section, responses, 0.80)
    
    def _evaluate_percentage_rule(self, section: Dict[str, Any], responses: Dict[str, str], threshold: float) -> bool:
        """Valuta regola percentuale"""
        questions = section.get("questions", [])
        if not questions:
            return True
            
        positive_count = 0
        total_count = len(questions)
        
        for question in questions:
            question_id = question["id"]
            if responses.get(question_id, "NO") == "SI":
                positive_count += 1
        
        percentage = positive_count / total_count if total_count > 0 else 0
        return percentage >= threshold
    
    def _evaluate_and_rule(self, section: Dict[str, Any], responses: Dict[str, str], rule: str) -> bool:
        """Valuta regola AND (tutte le condizioni devono essere vere)"""
        # Estrai i numeri delle domande dalla regola
        import re
        question_numbers = re.findall(r'Q(\d+)', rule)
        
        for q_num in question_numbers:
            question_id = f"{section['id']}.Q{q_num}"
            if responses.get(question_id, "NO") != "SI":
                return False
        
        return True
    
    def _evaluate_or_rule(self, section: Dict[str, Any], responses: Dict[str, str], rule: str) -> bool:
        """Valuta regola OR (almeno una condizione deve essere vera)"""
        import re
        question_numbers = re.findall(r'Q(\d+)', rule)
        
        for q_num in question_numbers:
            question_id = f"{section['id']}.Q{q_num}"
            if responses.get(question_id, "NO") == "SI":
                return True
        
        return False 