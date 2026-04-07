from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from database import create_connection, initialize_database
from qr_attendance import scan_qr
import threading
from admin_function import (
    admin_login,
    add_student,
    add_faculty,
    delete_student,
    delete_faculty,
    generate_student_regno,
    generate_faculty_regno
)
from qr_generater import generate_student_qr
import os
from datetime import datetime

app = Flask(__name__)

# Enable CORS for all routes
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Ensure QR_Codes directory exists
if not os.path.exists("QR_Codes"):
    os.makedirs("QR_Codes")


# ==================== ADMIN ROUTES ====================

@app.route('/api/login', methods=['POST'])
def login():
    """Admin login endpoint"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if admin_login(username, password):
            return jsonify({
                'success': True,
                'message': 'Login successful'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            }), 401
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== STUDENT ROUTES ====================

@app.route('/api/students', methods=['GET'])
def get_students():
    """Get all students"""
    try:
        conn = create_connection()
        if not conn:
            return jsonify({
                'success': False,
                'message': 'Database connection failed'
            }), 500

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM students ORDER BY student_id DESC")
        students = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'data': students
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/students', methods=['POST'])
def create_student():
    """Add new student"""
    try:
        data = request.json
        name = data.get('name')
        roll = data.get('roll')
        course = data.get('course')

        if not all([name, roll, course]):
            return jsonify({
                'success': False,
                'message': 'All fields are required'
            }), 400

        conn = create_connection()
        if not conn:
            return jsonify({
                'success': False,
                'message': 'Database connection failed'
            }), 500

        cursor = conn.cursor()

        # Generate registration number
        regno = generate_student_regno()

        if not regno:
            return jsonify({
                'success': False,
                'message': 'Failed to generate registration number'
            }), 500

        # Insert student
        cursor.execute("""
                       INSERT INTO students (registration_no, roll_no, name, course)
                       VALUES (%s, %s, %s, %s)
                       """, (regno, roll, name, course))

        conn.commit()

        # Generate QR code
        try:
            generate_student_qr(regno)
        except Exception as qr_error:
            print(f"Warning: QR generation failed: {qr_error}")

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Student added successfully',
            'registration_no': regno
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/students/<registration_no>', methods=['DELETE'])
def remove_student(registration_no):
    """Delete student"""
    try:
        conn = create_connection()
        if not conn:
            return jsonify({
                'success': False,
                'message': 'Database connection failed'
            }), 500

        cursor = conn.cursor()

        # Check if student exists
        cursor.execute("SELECT * FROM students WHERE registration_no=%s", (registration_no,))
        student = cursor.fetchone()

        if not student:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Student not found'
            }), 404

        # Delete student
        cursor.execute("DELETE FROM students WHERE registration_no=%s", (registration_no,))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Student deleted successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== FACULTY ROUTES ====================

@app.route('/api/faculty', methods=['GET'])
def get_faculty():
    """Get all faculty"""
    try:
        conn = create_connection()
        if not conn:
            return jsonify({
                'success': False,
                'message': 'Database connection failed'
            }), 500

        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM faculty ORDER BY faculty_id DESC")
        faculty = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'data': faculty
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/faculty', methods=['POST'])
def create_faculty():
    """Add new faculty"""
    try:
        data = request.json
        name = data.get('name')
        dept = data.get('department')

        if not all([name, dept]):
            return jsonify({
                'success': False,
                'message': 'All fields are required'
            }), 400

        conn = create_connection()
        if not conn:
            return jsonify({
                'success': False,
                'message': 'Database connection failed'
            }), 500

        cursor = conn.cursor()

        # Generate registration number
        fac_reg = generate_faculty_regno()

        if not fac_reg:
            return jsonify({
                'success': False,
                'message': 'Failed to generate faculty registration number'
            }), 500

        # Insert faculty
        cursor.execute("""
                       INSERT INTO faculty (faculty_regno, faculty_name, department)
                       VALUES (%s, %s, %s)
                       """, (fac_reg, name, dept))

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Faculty added successfully',
            'faculty_regno': fac_reg
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/faculty/<faculty_regno>', methods=['DELETE'])
def remove_faculty(faculty_regno):
    """Delete faculty"""
    try:
        conn = create_connection()
        if not conn:
            return jsonify({
                'success': False,
                'message': 'Database connection failed'
            }), 500

        cursor = conn.cursor()

        # Check if faculty exists
        cursor.execute("SELECT * FROM faculty WHERE faculty_regno=%s", (faculty_regno,))
        faculty = cursor.fetchone()

        if not faculty:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Faculty not found'
            }), 404

        # Delete faculty
        cursor.execute("DELETE FROM faculty WHERE faculty_regno=%s", (faculty_regno,))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Faculty deleted successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== ATTENDANCE ROUTES ====================

@app.route('/api/attendance', methods=['GET'])
def get_attendance():
    """Get all attendance records"""
    try:
        conn = create_connection()
        if not conn:
            return jsonify({
                'success': False,
                'message': 'Database connection failed'
            }), 500

        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
                       SELECT a.id,
                              a.registration_no,
                              COALESCE(s.name, f.faculty_name) AS name,
                              s.roll_no,
                              s.course,
                              f.department,
                              a.date,
                              a.time,
                              a.status
                       FROM attendance a
                                LEFT JOIN students s ON a.registration_no = s.registration_no
                                LEFT JOIN faculty f ON a.registration_no = f.faculty_regno
                       ORDER BY a.date DESC, a.time DESC
                       """)

        attendance = cursor.fetchall()

        # Convert date and time to string
        for record in attendance:
            if record['date']:
                record['date'] = record['date'].strftime('%Y-%m-%d')
            if record['time']:
                # Handle both timedelta and time objects
                if isinstance(record['time'], datetime):
                    record['time'] = record['time'].strftime('%H:%M:%S')
                else:
                    record['time'] = str(record['time'])

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'data': attendance
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/attendance/mark', methods=['POST'])
def mark_attendance():

    try:
        data = request.json
        reg_no = data.get('registration_no')

        if not reg_no:
            return jsonify({
                'success': False,
                'message': 'Registration number required'
            }), 400

        conn = create_connection()
        if not conn:
            return jsonify({
                'success': False,
                'message': 'Database connection failed'
            }), 500

        cursor = conn.cursor()

        # Check if already marked today
        cursor.execute("""
                       SELECT *
                       FROM attendance
                       WHERE registration_no = %s AND date =CURDATE()
                       """, (reg_no,))

        exists = cursor.fetchone()

        if exists:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'message': 'Attendance already marked for today'
            }), 400

        # Mark attendance
        cursor.execute("""
                       INSERT INTO attendance (registration_no, date, time, status)
                       VALUES (%s, CURDATE(), CURTIME(), 'Present')
                       """, (reg_no,))

        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Attendance marked successfully'
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/attendance/export', methods=['GET'])
def export_attendance():
    """Export attendance to Excel"""
    try:
        from openpyxl import Workbook

        conn = create_connection()
        if not conn:
            return jsonify({
                'success': False,
                'message': 'Database connection failed'
            }), 500

        cursor = conn.cursor()

        cursor.execute("""
                       SELECT a.registration_no,
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
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'message': 'No attendance data found'
            }), 404

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

        # Save file
        today = datetime.today().strftime("%Y-%m-%d")
        filename = f"Attendance_Report_{today}.xlsx"
        wb.save(filename)

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Attendance exported successfully',
            'filename': filename
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== STATS ROUTES ====================

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    try:
        conn = create_connection()
        if not conn:
            return jsonify({
                'success': False,
                'message': 'Database connection failed'
            }), 500

        cursor = conn.cursor()

        # Count students
        cursor.execute("SELECT COUNT(*) FROM students")
        student_count = cursor.fetchone()[0]

        # Count faculty
        cursor.execute("SELECT COUNT(*) FROM faculty")
        faculty_count = cursor.fetchone()[0]

        # Count today's attendance
        cursor.execute("SELECT COUNT(*) FROM attendance WHERE date=CURDATE()")
        today_attendance = cursor.fetchone()[0]

        # Count total attendance records
        cursor.execute("SELECT COUNT(*) FROM attendance")
        total_attendance = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'students': student_count,
                'faculty': faculty_count,
                'today_attendance': today_attendance,
                'total_attendance': total_attendance
            }
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== QR CODE ROUTES ====================

@app.route('/api/qr/<registration_no>', methods=['GET'])
def get_qr_code(registration_no):
    """Get QR code image for a registration number"""
    try:
        qr_path = f"QR_Codes/{registration_no}.png"

        if not os.path.exists(qr_path):
            return jsonify({
                'success': False,
                'message': 'QR code not found'
            }), 404

        return send_file(qr_path, mimetype='image/png')
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'message': 'Endpoint not found'
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500

# ------------- Qr Scanner --------- #

@app.route('/api/scanner/start', methods=['POST'])
def start_scanner():
        """Start QR code scanner"""
        try:
            # Start scanner in separate thread
            scanner_thread = threading.Thread(target=scan_qr)
            scanner_thread.daemon = True
            scanner_thread.start()

            return jsonify({
                'success': True,
                'message': 'Scanner started. Press Q to quit.'
            }), 200

        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500

# ==================== MAIN ====================

if __name__ == '__main__':
    print("=" * 50)
    print("QR Attendance System API Server")
    print("=" * 50)
    print("Server running on: http://localhost:5000")
    print("API Documentation:")
    print("  POST   /api/login              - Admin login")
    print("  GET    /api/students           - Get all students")
    print("  POST   /api/students           - Add new student")
    print("  DELETE /api/students/<regno>   - Delete student")
    print("  GET    /api/faculty            - Get all faculty")
    print("  POST   /api/faculty            - Add new faculty")
    print("  DELETE /api/faculty/<regno>    - Delete faculty")
    print("  GET    /api/attendance         - Get attendance records")
    print("  POST   /api/attendance/mark    - Mark attendance")
    print("  GET    /api/attendance/export  - Export to Excel")
    print("  GET    /api/stats              - Get statistics")
    print("  GET    /api/qr/<regno>         - Get QR code image")
    print("=" * 50)

    app.run(host="0.0.0.0", port=5000, debug=True)
