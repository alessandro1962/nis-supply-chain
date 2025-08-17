import sqlite3

def analyze_database():
    conn = sqlite3.connect('nis2_supply_chain.db')
    cursor = conn.cursor()
    
    print("=== ANALISI DATABASE ===")
    
    # Verifica struttura tabelle
    cursor.execute("PRAGMA table_info(training_enrollments)")
    enrollments_structure = cursor.fetchall()
    print(f"Training enrollments structure: {enrollments_structure}")
    
    cursor.execute("PRAGMA table_info(training_employees)")
    employees_structure = cursor.fetchall()
    print(f"Training employees structure: {employees_structure}")
    
    cursor.execute("PRAGMA table_info(training_course_content)")
    content_structure = cursor.fetchall()
    print(f"Training course content structure: {content_structure}")
    
    # Verifica dipendente
    cursor.execute("SELECT * FROM training_employees WHERE email = 'ale@nwk.it'")
    employee = cursor.fetchall()
    print(f"Employee ale@nwk.it: {employee}")
    
    # Verifica iscrizioni (usando la struttura corretta)
    cursor.execute("SELECT * FROM training_enrollments")
    all_enrollments = cursor.fetchall()
    print(f"All enrollments: {all_enrollments}")
    
    # Verifica iscrizioni specifiche per ale@nwk.it (employee_id = 4)
    cursor.execute("SELECT * FROM training_enrollments WHERE employee_id = 4")
    user_enrollments = cursor.fetchall()
    print(f"Enrollments for ale@nwk.it (employee_id=4): {user_enrollments}")
    
    # Verifica corsi
    cursor.execute("SELECT * FROM training_courses")
    courses = cursor.fetchall()
    print(f"All courses: {len(courses)} found")
    for course in courses:
        print(f"  Course ID {course[0]}: {course[1]}")
    
    # Verifica contenuti dei corsi
    cursor.execute("SELECT * FROM training_course_content")
    contents = cursor.fetchall()
    print(f"All course contents: {len(contents)} found")
    
    # Verifica contenuti per i corsi specifici dell'utente
    if user_enrollments:
        for enrollment in user_enrollments:
            course_id = enrollment[2]  # course_id è alla posizione 2
            cursor.execute("SELECT * FROM training_course_content WHERE course_id = ?", (course_id,))
            course_contents = cursor.fetchall()
            print(f"Contents for course {course_id}: {len(course_contents)} found")
            for content in course_contents:
                print(f"  - {content}")
    
    conn.close()

if __name__ == "__main__":
    analyze_database()
