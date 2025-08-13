import json
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

class NIS2AssessmentEvaluator:
    """Valutatore assessment NIS2 con algoritmo di calcolo conformità"""
    
    def __init__(self, manifest_path: str = "questionario_rules_manifest.json"):
        """Inizializza il valutatore con il manifest delle regole"""
        with open(manifest_path, 'r', encoding='utf-8') as f:
            self.manifest = json.load(f)
        
        self.threshold = self.manifest['scoring_defaults']['threshold']
        self.partial_weight = self.manifest['scoring_defaults']['partial_weight']
        self.iso27001_auto_percentage = self.manifest['scoring_defaults']['iso27001_auto_percentage']
    
    def evaluate_assessment(self, answers: Dict[str, str], has_iso27001: bool = False) -> Dict:
        """
        Valuta un assessment e restituisce il risultato
        
        Args:
            answers: Dizionario con risposte (es: {"GSI.03_1": "si", "GSI.03_2": "no"})
            has_iso27001: Se il fornitore ha certificazione ISO 27001
        
        Returns:
            Dizionario con risultati della valutazione
        """
        # Applica regole ISO 27001 se necessario
        if has_iso27001:
            answers = self._apply_iso27001_rules(answers)
        
        # Calcola punteggi
        total_score = 0
        max_score = 0
        essential_violations = []
        topic_scores = {}
        
        for topic in self.manifest['topics']:
            topic_code = topic['code']
            topic_score = 0
            topic_max = 0
            topic_essential_violations = []
            
            for question in topic['questions']:
                question_id = question['id']
                weight = question['weight']
                is_essential = question['essential']
                
                topic_max += weight
                max_score += weight
                
                answer = answers.get(question_id, 'no')
                
                # Calcola punteggio per questa domanda
                if answer == 'si':
                    question_score = weight
                    topic_score += weight
                elif answer == 'na':
                    question_score = weight * self.partial_weight
                    topic_score += weight * self.partial_weight
                else:  # 'no'
                    question_score = 0
                    if is_essential:
                        topic_essential_violations.append(question_id)
                        essential_violations.append(question_id)
                
                total_score += question_score
            
            topic_scores[topic_code] = {
                'score': topic_score,
                'max_score': topic_max,
                'percentage': topic_score / topic_max if topic_max > 0 else 0,
                'essential_violations': topic_essential_violations
            }
        
        # Calcola punteggio finale
        final_percentage = total_score / max_score if max_score > 0 else 0
        
        # Determina esito con logica più sofisticata
        if final_percentage >= self.threshold:
            if len(essential_violations) <= 3:  # Permette fino a 3 violazioni essenziali se il punteggio è alto
                outcome = "POSITIVO"
                reason = "Punteggio sufficiente con violazioni essenziali limitate"
            elif final_percentage >= 0.90:  # Se punteggio molto alto, permette più violazioni
                outcome = "POSITIVO"
                reason = "Punteggio molto alto compensa violazioni essenziali"
            else:
                outcome = "NEGATIVO"
                reason = f"Troppe violazioni essenziali ({len(essential_violations)}) nonostante punteggio sufficiente"
        else:
            outcome = "NEGATIVO"
            reason = "Punteggio insufficiente"
        
        # Genera hash per verifica pubblica
        verification_hash = self._generate_verification_hash(answers, outcome, final_percentage)
        
        return {
            'outcome': outcome,
            'reason': reason,
            'final_percentage': final_percentage,
            'threshold': self.threshold,
            'total_score': total_score,
            'max_score': max_score,
            'essential_violations': essential_violations,
            'topic_scores': topic_scores,
            'verification_hash': verification_hash,
            'evaluated_at': datetime.now().isoformat(),
            'has_iso27001': has_iso27001
        }
    
    def _apply_iso27001_rules(self, answers: Dict[str, str]) -> Dict[str, str]:
        """Applica le regole automatiche per certificazione ISO 27001"""
        auto_questions = self.manifest['iso27001_rules']['auto_questions']
        
        for question_id in auto_questions:
            if question_id not in answers:
                answers[question_id] = 'si'
        
        return answers
    
    def _generate_verification_hash(self, answers: Dict[str, str], outcome: str, percentage: float) -> str:
        """Genera hash per verifica pubblica"""
        # Crea stringa unica per questo assessment
        unique_string = f"{json.dumps(answers, sort_keys=True)}{outcome}{percentage}{datetime.now().isoformat()}"
        return hashlib.sha256(unique_string.encode()).hexdigest()[:16]
    
    def generate_report_data(self, evaluation_result: Dict, supplier_data: Dict, company_data: Dict) -> Dict:
        """Genera dati per il report PDF"""
        is_positive = evaluation_result['outcome'] == 'POSITIVO'
        
        # Trova punti di forza e debolezza
        strengths = []
        weaknesses = []
        
        for topic_code, topic_data in evaluation_result['topic_scores'].items():
            topic_name = next(t['name'] for t in self.manifest['topics'] if t['code'] == topic_code)
            
            if topic_data['percentage'] >= 0.8:
                strengths.append({
                    'topic': topic_code,
                    'name': topic_name,
                    'percentage': topic_data['percentage']
                })
            elif topic_data['percentage'] < 0.5:
                weaknesses.append({
                    'topic': topic_code,
                    'name': topic_name,
                    'percentage': topic_data['percentage'],
                    'essential_violations': topic_data['essential_violations']
                })
        
        return {
            'supplier': supplier_data,
            'company': company_data,
            'evaluation': evaluation_result,
            'report_type': 'passport' if is_positive else 'recall',
            'template': self.manifest['report_templates']['passport' if is_positive else 'recall'],
            'strengths': strengths,
            'weaknesses': weaknesses,
            'generated_at': datetime.now().isoformat(),
            'valid_until': (datetime.now() + timedelta(days=14)).isoformat()
        }
    
    def get_public_verification_data(self, verification_hash: str, evaluation_result: Dict) -> Dict:
        """Genera dati per verifica pubblica via QR code"""
        return {
            'hash': verification_hash,
            'outcome': evaluation_result['outcome'],
            'percentage': evaluation_result['final_percentage'],
            'evaluated_at': evaluation_result['evaluated_at'],
            'valid_until': (datetime.now() + timedelta(days=14)).isoformat(),
            'status': 'VALID' if datetime.now() < datetime.fromisoformat(evaluation_result['evaluated_at']) + timedelta(days=14) else 'EXPIRED'
        }

# Funzione di utilità per test
def test_evaluator():
    """Test del valutatore"""
    evaluator = NIS2AssessmentEvaluator()
    
    # Test con risposte positive
    positive_answers = {
        "GSI.03_1": "si", "GSI.03_2": "si", "GSI.03_3": "si", "GSI.03_4": "si",
        "GSI.04_1": "si", "GSI.04_2": "si", "GSI.04_3": "si", "GSI.04_4": "si",
        "GSI.05_1": "si", "GSI.05_2": "si", "GSI.05_3": "si",
        "SIT.03_1": "si", "SIT.03_2": "si", "SIT.03_3": "si",
        "SFA.01_1": "si", "SFA.01_2": "si",
        "SFA.02_1": "si", "SFA.02_2": "si"
    }
    
    result = evaluator.evaluate_assessment(positive_answers)
    print("Test positivo:", result['outcome'], f"({result['final_percentage']:.2%})")
    
    # Test con risposte negative
    negative_answers = {
        "GSI.03_1": "no", "GSI.03_2": "no", "GSI.03_3": "no", "GSI.03_4": "no",
        "GSI.04_1": "no", "GSI.04_2": "no", "GSI.04_3": "no", "GSI.04_4": "no",
        "GSI.05_1": "no", "GSI.05_2": "no", "GSI.05_3": "no",
        "SIT.03_1": "no", "SIT.03_2": "no", "SIT.03_3": "no",
        "SFA.01_1": "no", "SFA.01_2": "no",
        "SFA.02_1": "no", "SFA.02_2": "no"
    }
    
    result = evaluator.evaluate_assessment(negative_answers)
    print("Test negativo:", result['outcome'], f"({result['final_percentage']:.2%})")

if __name__ == "__main__":
    test_evaluator()
