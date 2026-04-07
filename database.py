import mysql.connector
from mysql.connector import Error

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'sun',  # CHANGE THIS to your MySQL password
    'database': 'attendance_system'
}


def create_database_if_not_exists():
    """Create the database if it doesn't exist"""
    try:
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
            
        )

        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        print(f" Database '{DB_CONFIG['database']}' is ready!")

        cursor.close()
        conn.close()
        return True

    except Error as err:
        print(f" Error creating database: {err}")
        return False


def create_connection():
    """Create and return a MySQL database connection"""
    try:
        create_database_if_not_exists()

        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database']
        )
        return conn

    except Error as err:
        print(f" Database Connection Error: {err}")
        return None


def initialize_database():
    """Complete database initialization"""
    print("=" * 60)
    print("DATABASE INITIALIZATION")
    print("=" * 60)

    if not create_database_if_not_exists():
        print(" Failed to create database!")
        return False

    conn = create_connection()
    if not conn:
        print(" Failed to connect to database!")
        return False

    cursor = conn.cursor()

    try:
        # Create admin table
        print("\n Creating admin table...")
        
        cursor.execute(""" CREATE TABLE IF NOT EXISTS admin (admin_id INT AUTO_INCREMENT PRIMARY KEY,username VARCHAR(50) UNIQUE NOT NULL, password VARCHAR (255) NOT NULL, fullname VARCHAR (100) NOT NULL)""")

        print(" Admin table created!")

        # Insert default admin
        cursor.execute(""" INSERT IGNORE INTO admin (username, password, fullname) VALUES ('suraj', 'admin123', 'System Administrator')
                       """)
        print(" Default admin added (username: suraj, password: admin123)")

        # Create students table
        print("\n Creating students table...")
        cursor.execute(""" CREATE TABLE IF NOT EXISTS students
                            (student_id INT AUTO_INCREMENT PRIMARY KEY,registration_no VARCHAR(20) UNIQUE,roll_no VARCHAR(50),name VARCHAR(100),course VARCHAR(100))""")
        print(" Students table created!")

        # Create faculty table
        print("\n Creating faculty table...")
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS faculty
                            (faculty_id INT AUTO_INCREMENT PRIMARY KEY, faculty_regno VARCHAR(20) UNIQUE, faculty_name VARCHAR(100),department VARCHAR(100))""")
        print(" Faculty table created!")

        # Create attendance table
        print("\n Creating attendance table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                registration_no VARCHAR(20),
                date DATE,
                time TIME,
                status VARCHAR(20),
                INDEX idx_reg_date (registration_no, date)
            )
        """)
        print(" Attendance table created!")

        conn.commit()
        cursor.close()
        conn.close()

        print("\n" + "=" * 60)
        print(" DATABASE INITIALIZATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nYou can now:")
        print("1. Start the backend: python app.py")
        print("2. Open index.html in your browser")
        print("3. Login with: username=suraj, password=admin123")
        print("=" * 60)

        return True

    except Error as err:
        print(f" Error creating tables: {err}")
        conn.rollback()
        cursor.close()
        conn.close()
        return False


def test_connection():
    """Test database connection"""
    print("Testing database connection...")
    conn = create_connection()
    if conn:
        print(" Database connection successful!")

        cursor = conn.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        if tables:
            print(f"\n Found {len(tables)} tables:")
            for table in tables:
                print(f"  - {table[0]}")
        else:
            print("\n️  No tables found. Run 'python database.py init' to create them.")

        cursor.close()
        conn.close()
        return True
    else:
        print(" Database connection failed!")
        return False


if __name__ == "__main__":
    import sys

    print("\n" + "=" * 60)
    print("QR ATTENDANCE SYSTEM - DATABASE SETUP")
    print("=" * 60)

    if len(sys.argv) > 1 and sys.argv[1] == "init":
        initialize_database()
    else:
        test_connection()
        print("\n Tip: Run 'python database.py init' for complete setup")