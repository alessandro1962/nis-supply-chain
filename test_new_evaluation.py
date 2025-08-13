from assessment_evaluator import NIS2AssessmentEvaluator

def test_new_evaluation():
    evaluator = NIS2AssessmentEvaluator()
    
    # Crea risposte positive (quasi tutti sì)
    positive_answers = {
        "GSI.03_1": "si", "GSI.03_2": "si", "GSI.03_3": "si", "GSI.03_4": "si",
        "GSI.04_1": "si", "GSI.04_2": "si", "GSI.04_3": "si", "GSI.04_4": "si",
        "GSI.05_1": "si", "GSI.05_2": "si", "GSI.05_3": "si",
        "SIT.03_1": "si", "SIT.03_2": "si", "SIT.03_3": "si",
        "SFA.01_1": "si", "SFA.01_2": "si",
        "SFA.02_1": "si", "SFA.02_2": "si"
    }
    
    result = evaluator.evaluate_assessment(positive_answers)
    
    print("=== TEST NUOVA LOGICA DI VALUTAZIONE ===")
    print(f"Risultato: {result['outcome']}")
    print(f"Percentuale: {result['final_percentage']:.2%}")
    print(f"Motivo: {result['reason']}")
    print(f"Violazioni essenziali: {result['essential_violations']}")
    
    # Test con alcune risposte negative (come nel tuo caso)
    mixed_answers = {
        "GSI.03_1": "si", "GSI.03_2": "si", "GSI.03_3": "si", "GSI.03_4": "no",  # Una essenziale negativa
        "GSI.04_1": "no", "GSI.04_2": "no", "GSI.04_3": "si", "GSI.04_4": "si",  # Due essenziali negative
        "GSI.05_1": "si", "GSI.05_2": "si", "GSI.05_3": "si",
        "SIT.03_1": "si", "SIT.03_2": "si", "SIT.03_3": "si",
        "SFA.01_1": "si", "SFA.01_2": "si",
        "SFA.02_1": "si", "SFA.02_2": "si"
    }
    
    result2 = evaluator.evaluate_assessment(mixed_answers)
    
    print("\n=== TEST CON ALCUNE RISPOSTE NEGATIVE ===")
    print(f"Risultato: {result2['outcome']}")
    print(f"Percentuale: {result2['final_percentage']:.2%}")
    print(f"Motivo: {result2['reason']}")
    print(f"Violazioni essenziali: {result2['essential_violations']}")

if __name__ == "__main__":
    test_new_evaluation()
