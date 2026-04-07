import qrcode
import os
from database import create_connection

# Create folder
if not os.path.exists("QR_Codes"):
    os.makedirs("QR_Codes")

def generate_student_qr(reg_no):
    img = qrcode.make(reg_no)
    img.save(f"QR_Codes/{reg_no}.png")
    print(f"✔ QR Code generated: {reg_no}.png")


# Generate QR for all students

def generate_all_qr():
    conn = create_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT registration_no FROM students")
    data = cursor.fetchall()

    for row in data:
        generate_student_qr(row[0])
    print('done')
    cursor.close()
    conn.close()

if __name__ == '__main__':
    generate_all_qr()
