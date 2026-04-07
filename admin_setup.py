from database import create_connection


# Create Admin Table Defaut Admin

def setup_admin():
    conn = create_connection()
    if conn is None:
        return 

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            admin_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            fullname VARCHAR(100)
        )
    """)
    print("✔ Admin table created!")

    cursor.execute("""
        INSERT IGNORE INTO admin (username, password, fullname)
        VALUES ('suraj', 'admin123', 'System Administrator')
    """)

    conn.commit()
    cursor.close()
    conn.close()

    print("✔ Default admin added!")


# Create attendance table

def create_attendance_table():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            registration_no VARCHAR(20),
            date DATE,
            time TIME,
            status VARCHAR(20)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


if __name__ == "__main__":
    setup_admin()
    create_attendance_table()


