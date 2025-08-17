#!/usr/bin/env python3
"""
Script per testare direttamente il metodo authenticate_employee
"""
from training_module import TrainingModule

def test_auth():
    print("🔍 Test autenticazione dipendente...")
    
    training = TrainingModule()
    
    # Test con password corretta
    print("\n1. Test con password corretta (Somiwo123):")
    employee = training.authenticate_employee('ale@nwk.it', 'Somiwo123')
    print(f"Risultato: {employee}")
    
    # Test con password sbagliata
    print("\n2. Test con password sbagliata (password123):")
    employee = training.authenticate_employee('ale@nwk.it', 'password123')
    print(f"Risultato: {employee}")
    
    # Test con email inesistente
    print("\n3. Test con email inesistente:")
    employee = training.authenticate_employee('nonexistent@example.com', 'Somiwo123')
    print(f"Risultato: {employee}")

if __name__ == "__main__":
    test_auth()
