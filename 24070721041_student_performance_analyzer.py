import mysql.connector
import csv
import hashlib
import datetime
import getpass

# =========================================
# DATABASE CONFIGURATION
# =========================================

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "mysql",   # CHANGE IF NEEDED
    "database": "spa_enhanced_db"
}

# =========================================
# GLOBAL SESSION
# =========================================

current_user = {
    "id": None,
    "username": None,
    "role": None
}

# =========================================
# DATABASE CONNECTION
# =========================================

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

# =========================================
# PASSWORD HASH FUNCTION
# =========================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# =========================================
# AUDIT LOG FUNCTION
# =========================================

def log_audit(action, details=""):

    try:

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO audit_log(user_id, action, details)
        VALUES(%s,%s,%s)
        """

        cursor.execute(query, (
            current_user["id"],
            action,
            details
        ))

        conn.commit()

    except:
        pass

# =========================================
# LOGIN SYSTEM
# =========================================

def login():

    print("\n========== LOGIN ==========\n")

    username = input("Enter Username: ")

    password = getpass.getpass("Enter Password: ")

    hashed = hash_password(password)

    try:

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        SELECT id, username, role
        FROM users
        WHERE username=%s
        AND password_hash=%s
        AND is_active=1
        """

        cursor.execute(query, (username, hashed))

        user = cursor.fetchone()

        if user:

            current_user["id"] = user[0]
            current_user["username"] = user[1]
            current_user["role"] = user[2]

            print("\nLogin Successful\n")

            log_audit("LOGIN SUCCESS", username)

            return True

        else:

            print("\nInvalid Credentials\n")

            log_audit("LOGIN FAILED", username)

            return False

    except Exception as e:
        print("Error:", e)
        return False

# =========================================
# CREATE USER
# =========================================

def create_user():

    try:

        username = input("Enter Username: ")

        password = getpass.getpass("Enter Password: ")

        role = input("Enter Role(admin/faculty/student): ").lower()

        hashed = hash_password(password)

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO users(username,password_hash,role)
        VALUES(%s,%s,%s)
        """

        cursor.execute(query, (
            username,
            hashed,
            role
        ))

        conn.commit()

        user_id = cursor.lastrowid

        print("\nUser Created Successfully")
        print("Generated User ID :", user_id)

        # AUTO INSERT INTO STUDENTS TABLE
        if role == "student":

            print("\nEnter Student Details\n")

            name = input("Enter Student Name: ")

            dept = input("Enter Department: ")

            marks = float(input("Enter Marks: "))

            student_query = """
            INSERT INTO students(name, department, marks, user_id)
            VALUES(%s,%s,%s,%s)
            """

            cursor.execute(student_query, (
                name,
                dept,
                marks,
                user_id
            ))

            conn.commit()

            print("\nStudent Record Linked Successfully")

        log_audit("CREATE USER", username)

    except Exception as e:
        print("Error:", e)

# =========================================
# ADD STUDENT
# =========================================

def add_student():

    try:

        name = input("Enter Student Name: ")

        dept = input("Enter Department: ")

        marks = float(input("Enter Marks: "))

        user_id = int(input("Enter User ID: "))

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO students(name, department, marks, user_id)
        VALUES(%s,%s,%s,%s)
        """

        cursor.execute(query, (
            name,
            dept,
            marks,
            user_id
        ))

        conn.commit()

        print("\nStudent Added Successfully\n")

        log_audit("ADD STUDENT", name)

    except Exception as e:
        print("Error:", e)

# =========================================
# VIEW ALL STUDENTS
# =========================================

def add_student():

    try:

        print("\n===== ADD STUDENT =====\n")

        username = input("Enter Username: ")

        password = getpass.getpass("Enter Password: ")

        hashed = hash_password(password)

        role = "student"

        conn = get_connection()
        cursor = conn.cursor()

        # CREATE USER FIRST
        user_query = """
        INSERT INTO users(username,password_hash,role)
        VALUES(%s,%s,%s)
        """

        cursor.execute(user_query, (
            username,
            hashed,
            role
        ))

        conn.commit()

        # GET USER ID
        user_id = cursor.lastrowid

        print("Generated User ID:", user_id)

        # STUDENT DETAILS
        name = input("Enter Student Name: ")

        dept = input("Enter Department: ")

        marks = float(input("Enter Marks: "))

        # INSERT STUDENT
        student_query = """
        INSERT INTO students(name, department, marks, user_id)
        VALUES(%s,%s,%s,%s)
        """

        cursor.execute(student_query, (
            name,
            dept,
            marks,
            user_id
        ))

        conn.commit()

        print("\nStudent Added Successfully\n")

        log_audit("ADD STUDENT", name)

    except Exception as e:
        print("Error:", e)

# =========================================
# SEARCH BY DEPARTMENT
# =========================================

def search_by_dept():

    try:

        dept = input("Enter Department: ")

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        SELECT id, name, department, marks, user_id
        FROM students
        WHERE LOWER(department)=LOWER(%s)
        """

        cursor.execute(query, (dept,))

        rows = cursor.fetchall()

        print("\n========== SEARCH RESULT ==========\n")

        for row in rows:
            print(row)

    except Exception as e:
        print("Error:", e)

# =========================================
# UPDATE STUDENT
# =========================================

def update_student():

    try:

        sid = int(input("Enter Student ID: "))

        marks = float(input("Enter New Marks: "))

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        UPDATE students
        SET marks=%s
        WHERE id=%s
        """

        cursor.execute(query, (marks, sid))

        conn.commit()

        print("\nStudent Updated Successfully\n")

        log_audit("UPDATE STUDENT", sid)

    except Exception as e:
        print("Error:", e)

# =========================================
# DELETE STUDENT
# =========================================

def delete_student():

    try:

        sid = int(input("Enter Student ID: "))

        confirm = input("Are you sure? (y/n): ")

        if confirm.lower() != 'y':
            return

        conn = get_connection()
        cursor = conn.cursor()

        query = "DELETE FROM students WHERE id=%s"

        cursor.execute(query, (sid,))

        conn.commit()

        print("\nStudent Deleted Successfully\n")

        log_audit("DELETE STUDENT", sid)

    except Exception as e:
        print("Error:", e)

# =========================================
# VIEW OWN RECORD
# =========================================

def view_own_record():

    try:

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        SELECT id, name, department, marks, user_id
        FROM students
        WHERE user_id=%s
        """

        cursor.execute(query, (current_user["id"],))

        row = cursor.fetchone()

        print("\n========== YOUR RECORD ==========\n")

        if row:
            print(row)
        else:
            print("No Record Found")

    except Exception as e:
        print("Error:", e)

# =========================================
# DASHBOARD
# =========================================

def dashboard():

    try:

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        SELECT
        COUNT(*),
        AVG(marks),
        MAX(marks),
        MIN(marks)
        FROM students
        """

        cursor.execute(query)

        result = cursor.fetchone()

        print("\n========== DASHBOARD ==========\n")

        print("Total Students :", result[0])
        print("Average Marks  :", result[1])
        print("Highest Marks  :", result[2])
        print("Lowest Marks   :", result[3])

    except Exception as e:
        print("Error:", e)

# =========================================
# MARKS DISTRIBUTION
# =========================================

def marks_distribution():

    try:

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        SELECT
        SUM(CASE WHEN marks >=90 THEN 1 ELSE 0 END),
        SUM(CASE WHEN marks BETWEEN 75 AND 89 THEN 1 ELSE 0 END),
        SUM(CASE WHEN marks BETWEEN 60 AND 74 THEN 1 ELSE 0 END),
        SUM(CASE WHEN marks BETWEEN 40 AND 59 THEN 1 ELSE 0 END),
        SUM(CASE WHEN marks <40 THEN 1 ELSE 0 END)
        FROM students
        """

        cursor.execute(query)

        row = cursor.fetchone()

        print("\n========== GRADE DISTRIBUTION ==========\n")

        print("A Grade :", row[0])
        print("B Grade :", row[1])
        print("C Grade :", row[2])
        print("D Grade :", row[3])
        print("F Grade :", row[4])

    except Exception as e:
        print("Error:", e)

# =========================================
# TOP PERFORMERS
# =========================================

def show_top_performers():

    try:

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        SELECT name, department, marks
        FROM students
        ORDER BY marks DESC
        LIMIT 3
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        print("\n========== TOP PERFORMERS ==========\n")

        for row in rows:
            print(row)

    except Exception as e:
        print("Error:", e)

# =========================================
# DEPARTMENT LEADERBOARD
# =========================================

def dept_leaderboard():

    try:

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        SELECT department, AVG(marks)
        FROM students
        GROUP BY department
        ORDER BY AVG(marks) DESC
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        print("\n========== DEPARTMENT LEADERBOARD ==========\n")

        for row in rows:
            print(row)

    except Exception as e:
        print("Error:", e)

# =========================================
# BONUS MARKS
# =========================================

def add_bonus_marks():

    try:

        dept = input("Enter Department: ")

        bonus = float(input("Enter Bonus Marks: "))

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        UPDATE students
        SET marks = LEAST(marks + %s, 100)
        WHERE department=%s
        """

        cursor.execute(query, (bonus, dept))

        conn.commit()

        print("\nBonus Marks Added\n")

        log_audit("BONUS MARKS", dept)

    except Exception as e:
        print("Error:", e)

# =========================================
# EXPORT HIGH PERFORMERS
# =========================================

def export_high_performers():

    try:

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        SELECT *
        FROM students
        WHERE marks >
        (SELECT AVG(marks) FROM students)
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        filename = "high_performers_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".csv"

        with open(filename, "w", newline="") as file:

            writer = csv.writer(file)

            writer.writerow([
                "ID",
                "NAME",
                "DEPARTMENT",
                "MARKS",
                "USER_ID",
                "ENROLLED_AT"
            ])

            writer.writerows(rows)

        print("\nCSV Exported Successfully\n")

    except Exception as e:
        print("Error:", e)

# =========================================
# LIST USERS
# =========================================

def list_users():

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT id, username, role,
               is_active, created_at
        FROM users
        """)

        rows = cursor.fetchall()

        print("\n========== USERS ==========\n")

        for row in rows:
            print(row)

    except Exception as e:
        print("Error:", e)

# =========================================
# TOGGLE USER
# =========================================

def toggle_user():

    try:

        uid = int(input("Enter User ID: "))

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        UPDATE users
        SET is_active = NOT is_active
        WHERE id=%s
        """

        cursor.execute(query, (uid,))

        conn.commit()

        print("\nUser Status Changed\n")

    except Exception as e:
        print("Error:", e)

# =========================================
# VIEW AUDIT LOG
# =========================================

def view_audit_log():

    try:

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        SELECT *
        FROM audit_log
        ORDER BY timestamp DESC
        LIMIT 20
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        print("\n========== AUDIT LOG ==========\n")

        for row in rows:
            print(row)

    except Exception as e:
        print("Error:", e)

# =========================================
# ADMIN MENU
# =========================================

def menu_admin():

    while True:

        print("""
========== ADMIN MENU ==========

1. Add Student
2. View Students
3. Search By Department
4. Update Student
5. Delete Student
6. Dashboard
7. Marks Distribution
8. Top Performers
9. Department Leaderboard
10. Add Bonus Marks
11. Export CSV
12. Create User
13. List Users
14. Toggle User
15. View Audit Log
16. Exit
""")

        choice = input("Enter Choice: ")

        if choice == '1':
            add_student()

        elif choice == '2':
            view_students()

        elif choice == '3':
            search_by_dept()

        elif choice == '4':
            update_student()

        elif choice == '5':
            delete_student()

        elif choice == '6':
            dashboard()

        elif choice == '7':
            marks_distribution()

        elif choice == '8':
            show_top_performers()

        elif choice == '9':
            dept_leaderboard()

        elif choice == '10':
            add_bonus_marks()

        elif choice == '11':
            export_high_performers()

        elif choice == '12':
            create_user()

        elif choice == '13':
            list_users()

        elif choice == '14':
            toggle_user()

        elif choice == '15':
            view_audit_log()

        elif choice == '16':
            break

        else:
            print("Invalid Choice")

# =========================================
# FACULTY MENU
# =========================================

def menu_faculty():

    while True:

        print("""
========== FACULTY MENU ==========

1. Add Student
2. View Students
3. Search By Department
4. Update Student
5. Dashboard
6. Marks Distribution
7. Top Performers
8. Department Leaderboard
9. Add Bonus Marks
10. Export CSV
11. Exit
""")

        choice = input("Enter Choice: ")

        if choice == '1':
            add_student()

        elif choice == '2':
            view_students()

        elif choice == '3':
            search_by_dept()

        elif choice == '4':
            update_student()

        elif choice == '5':
            dashboard()

        elif choice == '6':
            marks_distribution()

        elif choice == '7':
            show_top_performers()

        elif choice == '8':
            dept_leaderboard()

        elif choice == '9':
            add_bonus_marks()

        elif choice == '10':
            export_high_performers()

        elif choice == '11':
            break

        else:
            print("Invalid Choice")

# =========================================
# STUDENT MENU
# =========================================

def menu_student():

    while True:

        print("""
========== STUDENT MENU ==========

1. View Own Record
2. Dashboard
3. Top Performers
4. Exit
""")

        choice = input("Enter Choice: ")

        if choice == '1':
            view_own_record()

        elif choice == '2':
            dashboard()

        elif choice == '3':
            show_top_performers()

        elif choice == '4':
            break

        else:
            print("Invalid Choice")

# =========================================
# MAIN FUNCTION
# =========================================

def main():

    if not login():
        return

    role = current_user["role"]

    if role == "admin":
        menu_admin()

    elif role == "faculty":
        menu_faculty()

    elif role == "student":
        menu_student()

# =========================================
# RUN APPLICATION
# =========================================

if __name__ == "__main__":
    main()