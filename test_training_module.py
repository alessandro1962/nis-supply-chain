from training_module import TrainingModule

def test_training_module():
    """Test completo del modulo training"""
    print("🧪 Test del Modulo Training")
    print("=" * 50)
    
    # Inizializza il modulo
    training = TrainingModule()
    
    # Test 1: Aggiungi dipendenti
    print("\n1️⃣ Test aggiunta dipendenti...")
    try:
        employee1_id = training.add_employee(1, "Mario Rossi", "mario.rossi@company.com", "IT Manager", "IT", "2024-01-15")
        employee2_id = training.add_employee(1, "Anna Bianchi", "anna.bianchi@company.com", "Security Officer", "Security", "2024-02-01")
        employee3_id = training.add_employee(1, "Luca Verdi", "luca.verdi@company.com", "Compliance Manager", "Legal", "2024-03-01")
        print(f"✅ Dipendenti aggiunti: {employee1_id}, {employee2_id}, {employee3_id}")
    except Exception as e:
        print(f"❌ Errore aggiunta dipendenti: {e}")
    
    # Test 2: Ottieni dipendenti
    print("\n2️⃣ Test recupero dipendenti...")
    try:
        employees = training.get_employees(1)
        print(f"✅ Dipendenti trovati: {len(employees)}")
        for emp in employees:
            print(f"   - {emp['name']} ({emp['role']})")
    except Exception as e:
        print(f"❌ Errore recupero dipendenti: {e}")
    
    # Test 3: Ottieni corsi
    print("\n3️⃣ Test recupero corsi...")
    try:
        courses = training.get_courses()
        print(f"✅ Corsi trovati: {len(courses)}")
        for course in courses:
            print(f"   - {course['title']} ({course['category']})")
    except Exception as e:
        print(f"❌ Errore recupero corsi: {e}")
    
    # Test 4: Iscrizioni
    print("\n4️⃣ Test iscrizioni...")
    try:
        if employees and courses:
            enrollment1 = training.enroll_employee(employees[0]['id'], courses[0]['id'])
            enrollment2 = training.enroll_employee(employees[1]['id'], courses[1]['id'])
            print(f"✅ Iscrizioni create: {enrollment1}, {enrollment2}")
    except Exception as e:
        print(f"❌ Errore iscrizioni: {e}")
    
    # Test 5: Quiz
    print("\n5️⃣ Test quiz...")
    try:
        if courses:
            quiz = training.get_course_quiz(courses[0]['id'])
            if quiz:
                print(f"✅ Quiz trovato: {quiz['title']} con {len(quiz['questions'])} domande")
            else:
                print("⚠️ Nessun quiz trovato per questo corso")
    except Exception as e:
        print(f"❌ Errore quiz: {e}")
    
    # Test 6: Statistiche
    print("\n6️⃣ Test statistiche...")
    try:
        stats = training.get_training_stats(1)
        print(f"✅ Statistiche: {stats}")
    except Exception as e:
        print(f"❌ Errore statistiche: {e}")
    
    # Test 7: Notifiche
    print("\n7️⃣ Test notifiche...")
    try:
        if employees:
            training.create_notification(employees[0]['id'], "COURSE_DUE", "Corso in Scadenza", "Il corso Fondamenti NIS2 scade tra 7 giorni")
            notifications = training.get_employee_notifications(employees[0]['id'])
            print(f"✅ Notifiche create: {len(notifications)}")
    except Exception as e:
        print(f"❌ Errore notifiche: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Test completato!")

if __name__ == "__main__":
    test_training_module()
