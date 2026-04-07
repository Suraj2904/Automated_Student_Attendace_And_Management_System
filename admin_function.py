from database import create_connection
from qr_generater import generate_student_qr
from datetime import datetime


# ============= REGISTRATION NUMBER GENERATORS =============

def generate_student_regno():
    """Generate unique student registration number"""
    year = datetime.now().year
    prefix = f"STU{year}"

    conn = create_connection()
    if not conn:
        return None

    cursor = conn.cursor()

    try:
        # Ensure students table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id INT AUTO_INCREMENT PRIMARY KEY,
                registration_no VARCHAR(20) UNIQUE,
                roll_no VARCHAR(50),
                name VARCHAR(100),
                course VARCHAR(100)
            )
        """)

        # Count existing students
        cursor.execute("SELECT COUNT(*) FROM students")
        count = cursor.fetchone()[0] + 1

        regno = prefix + str(count).zfill(4)

        cursor.close()
        conn.close()

        return regno
    except Exception as e:
        print(f"Error generating registration number: {e}")
        cursor.close()
        conn.close()
        return None


def generate_faculty_regno():
    """Generate unique faculty registration number"""
    year = datetime.now().year
    prefix = f"FAC{year}"

    conn = create_connection()
    if not conn:
        return None

    cursor = conn.cursor()

    try:
        # Ensure faculty table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS faculty (
                faculty_id INT AUTO_INCREMENT PRIMARY KEY,
                faculty_regno VARCHAR(20) UNIQUE,
                faculty_name VARCHAR(100),
                department VARCHAR(100)
            )
        """)

        # Count existing faculty
        cursor.execute("SELECT COUNT(*) FROM faculty")
        count = cursor.fetchone()[0] + 1

        regno = prefix + str(count).zfill(4)

        cursor.close()
        conn.close()

        return regno
    except Exception as e:
        print(f"Error generating faculty registration number: {e}")
        cursor.close()
        conn.close()
        return None


# ============= ADMIN AUTHENTICATION =============

def admin_login(username, password):
    """Verify admin credentials"""
    conn = create_connection()
    if not conn:
        return False

    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT * FROM admin WHERE username=%s AND password=%s",
            (username, password)
        )

        result = cursor.fetchone()
        cursor.close()
        conn.close()

        return result is not None
    except Exception as e:
        print(f"Login error: {e}")
        cursor.close()
        conn.close()
        return False


# ============= STUDENT MANAGEMENT =============

def add_student(name, roll, course):
    """Add new student to database"""
    conn = create_connection()
    if not conn:
        return False

    cursor = conn.cursor()

    try:
        # Ensure table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id INT AUTO_INCREMENT PRIMARY KEY,
                registration_no VARCHAR(20) UNIQUE,
                roll_no VARCHAR(50),
                name VARCHAR(100),
                course VARCHAR(100)
            )
        """)

        # Generate unique registration number
        regno = generate_student_regno()
        if not regno:
            print("❌ Failed to generate registration number")
            cursor.close()
            conn.close()
            return False

        # Insert student
        cursor.execute("""
            INSERT INTO students (registration_no, roll_no, name, course)
            VALUES (%s, %s, %s, %s)
        """, (regno, roll, name, course))

        conn.commit()

        print(f"✓ Student added successfully! Registration No: {regno}")

        # Auto-generate QR Code
        try:
            generate_student_qr(regno)
            print(f"📸 QR Code generated for {regno}")
        except Exception as e:
            print(f"⚠ Warning: QR code generation failed: {e}")

        cursor.close()
        conn.close()

        return True
    except Exception as e:
        print(f"❌ Error adding student: {e}")
        conn.rollback()
        cursor.close()
        conn.close()
        return False


def view_students():
    """Retrieve all students"""
    conn = create_connection()
    if not conn:
        return []

    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM students ORDER BY student_id DESC")
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        return results
    except Exception as e:
        print(f"Error fetching students: {e}")
        cursor.close()
        conn.close()
        return []


def delete_student(registration_no):
    """Delete student by registration number"""
    conn = create_connection()
    if not conn:
        return False

    cursor = conn.cursor()

    try:
        # Check if student exists
        cursor.execute("SELECT * FROM students WHERE registration_no=%s", (registration_no,))
        result = cursor.fetchone()

        if not result:
            print("❌ Student not found!")
            cursor.close()
            conn.close()
            return False

        # Delete student
        cursor.execute("DELETE FROM students WHERE registration_no=%s", (registration_no,))
        conn.commit()

        print(f"✓ Student {registration_no} deleted successfully!")

        cursor.close()
        conn.close()

        return True
    except Exception as e:
        print(f"❌ Error deleting student: {e}")
        conn.rollback()
        cursor.close()
        conn.close()
        return False


# ============= FACULTY MANAGEMENT =============

def add_faculty(name, dept):
    """Add new faculty to database"""
    conn = create_connection()
    if not conn:
        return False

    cursor = conn.cursor()

    try:
        # Ensure table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS faculty (
                faculty_id INT AUTO_INCREMENT PRIMARY KEY,
                faculty_regno VARCHAR(20) UNIQUE,
                faculty_name VARCHAR(100),
                department VARCHAR(100)
            )
        """)

        # Generate unique registration number
        fac_reg = generate_faculty_regno()
        if not fac_reg:
            print("❌ Failed to generate faculty registration number")
            cursor.close()
            conn.close()
            return False

        # Insert faculty
        cursor.execute("""
            INSERT INTO faculty (faculty_regno, faculty_name, department)
            VALUES (%s, %s, %s)
        """, (fac_reg, name, dept))

        conn.commit()

        print(f"✓ Faculty added successfully! Faculty ID: {fac_reg}")

        cursor.close()
        conn.close()

        return True
    except Exception as e:
        print(f"❌ Error adding faculty: {e}")
        conn.rollback()
        cursor.close()
        conn.close()
        return False


def view_faculty():
    """Retrieve all faculty"""
    conn = create_connection()
    if not conn:
        return []

    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT * FROM faculty ORDER BY faculty_id DESC")
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        return results
    except Exception as e:
        print(f"Error fetching faculty: {e}")
        cursor.close()
        conn.close()
        return []


def delete_faculty(faculty_regno):
    """Delete faculty by registration number"""
    conn = create_connection()
    if not conn:
        return False

    cursor = conn.cursor()

    try:
        # Check if faculty exists
        cursor.execute("SELECT * FROM faculty WHERE faculty_regno=%s", (faculty_regno,))
        result = cursor.fetchone()

        if not result:
            print("❌ Faculty not found!")
            cursor.close()
            conn.close()
            return False

        # Delete faculty
        cursor.execute("DELETE FROM faculty WHERE faculty_regno=%s", (faculty_regno,))
        conn.commit()

        print(f"✓ Faculty {faculty_regno} deleted successfully!")

        cursor.close()
        conn.close()

        return True
    except Exception as e:
        print(f"❌ Error deleting faculty: {e}")
        conn.rollback()
        cursor.close()
        conn.close()
        return False


# ============= ATTENDANCE MANAGEMENT =============

def show_attendance():
    """Display all attendance records"""
    conn = create_connection()
    if not conn:
        return []

    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT 
                a.registration_no,
                COALESCE(s.name, f.faculty_name) AS name,
                s.roll_no,
                f.department,
                a.date,
                a.time,
                a.status
            FROM attendance a
            LEFT JOIN students s ON a.registration_no = s.registration_no
            LEFT JOIN faculty f ON a.registration_no = f.faculty_regno
            ORDER BY a.date DESC, a.time DESC
        """)

        records = cursor.fetchall()

        print("\n========== Attendance Report ==========\n")

        if len(records) == 0:
            print("❌ No attendance records available.")
        else:
            for record in records:
                print(record)

        cursor.close()
        conn.close()

        return records
    except Exception as e:
        print(f"Error fetching attendance: {e}")
        cursor.close()
        conn.close()
        return []


def mark_attendance(reg_no):
    """Mark attendance for a registration number"""
    conn = create_connection()
    if not conn:
        return False

    cursor = conn.cursor()

    try:
        # Check if already marked today
        cursor.execute("""
            SELECT * FROM attendance
            WHERE registration_no=%s AND date=CURDATE()
        """, (reg_no,))

        exists = cursor.fetchone()

        if exists:
            print(f"⚠ Attendance already marked for {reg_no} today")
            cursor.close()
            conn.close()
            return False

        # Mark attendance
        cursor.execute("""
            INSERT INTO attendance (registration_no, date, time, status)
            VALUES (%s, CURDATE(), CURTIME(), 'Present')
        """, (reg_no,))

        conn.commit()

        print(f"✓ Attendance marked for {reg_no}")

        cursor.close()
        conn.close()

        return True
    except Exception as e:
        print(f"❌ Error marking attendance: {e}")
        conn.rollback()
        cursor.close()
        conn.close()
        return False


# ============= EXPORT FUNCTIONS =============

def export_attendance_to_excel():
    """Export attendance records to Excel file"""
    try:
        from openpyxl import Workbook

        conn = create_connection()
        if not conn:
            print("❌ Database connection failed")
            return False

        cursor = conn.cursor()

        # Fetch attendance with student/faculty details
        cursor.execute("""
            SELECT 
                a.registration_no,
                COALESCE(s.name, f.faculty_name) AS name,
                s.roll_no,
                f.department,
                a.date,
                a.time,
                a.status
            FROM attendance a
            LEFT JOIN students s ON a.registration_no = s.registration_no
            LEFT JOIN faculty f ON a.registration_no = f.faculty_regno
            ORDER BY a.date DESC, a.time DESC
        """)

        rows = cursor.fetchall()

        if len(rows) == 0:
            print("\n❌ No attendance data found to export.")
            cursor.close()
            conn.close()
            return False

        # Create Excel workbook
        wb = Workbook()
        sheet = wb.active
        sheet.title = "Attendance Records"

        # Add headers
        sheet.append([
            "Registration No",
            "Name",
            "Roll No",
            "Department",
            "Date",
            "Time",
            "Status"
        ])

        # Add data rows
        for row in rows:
            sheet.append(row)

        # Generate filename with timestamp
        today = datetime.today().strftime("%Y-%m-%d")
        filename = f"Attendance_Report_{today}.xlsx"

        # Save file
        wb.save(filename)

        print(f"\n✓ Attendance exported successfully!")
        print(f"📄 File saved as: {filename}")

        cursor.close()
        conn.close()

        return True
    except Exception as e:
        print(f"❌ Error exporting attendance: {e}")
        return False


# ============= STATISTICS =============

def get_statistics():
    """Get dashboard statistics"""
    conn = create_connection()
    if not conn:
        return None

    cursor = conn.cursor()

    try:
        stats = {}

        # Count students
        cursor.execute("SELECT COUNT(*) FROM students")
        stats['students'] = cursor.fetchone()[0]

        # Count faculty
        cursor.execute("SELECT COUNT(*) FROM faculty")
        stats['faculty'] = cursor.fetchone()[0]

        # Count today's attendance
        cursor.execute("SELECT COUNT(*) FROM attendance WHERE date=CURDATE()")
        stats['today_attendance'] = cursor.fetchone()[0]

        # Count total attendance records
        cursor.execute("SELECT COUNT(*) FROM attendance")
        stats['total_attendance'] = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return stats
    except Exception as e:
        print(f"Error fetching statistics: {e}")
        cursor.close()
        conn.close()
        return None


# ============= MAIN (for testing) =============

if __name__ == "__main__":
    print("Admin Functions Module - Testing")
    print("=" * 50)

    # Test statistics
    stats = get_statistics()
    if stats:
        print("\n📊 Current Statistics:")
        print(f"Students: {stats['students']}")
        print(f"Faculty: {stats['faculty']}")
        print(f"Today's Attendance: {stats['today_attendance']}")
        print(f"Total Attendance: {stats['total_attendance']}")