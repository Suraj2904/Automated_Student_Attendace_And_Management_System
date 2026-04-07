# 📱 QR Attendance System

A web-based attendance management system that allows admins to manage students and faculty, mark attendance via QR code scanning or manual entry, and export reports to Excel.

---

## 🗂️ Project Structure

```
qr-attendance-system/
│
├── app.py               # Flask backend — all REST API routes
├── database.py          # MySQL connection and database initialization
├── admin_function.py    # Core logic: add/delete students, faculty, attendance
├── admin_setup.py       # One-time setup: admin table + default admin
├── manual_setup.py      # Standalone DB setup script (no Flask needed)
├── qr_generater.py      # Generates QR code images for students
├── qr_attendance.py     # Webcam-based QR scanner for marking attendance
│
├── index.html           # Main frontend UI (Admin Dashboard)
├── style.css            # Stylesheet for the frontend
├── script.js            # Frontend JavaScript (API calls, UI logic)
│
├── test_api.html        # Browser-based API endpoint tester
├── test_db.py           # MySQL connection test script
├── test_qr.py           # QR scanner test script
│
└── QR_Codes/            # Auto-created folder for generated QR images
```

---

## ✨ Features

- **Admin Login** — Secure login portal with default credentials
- **Student Management** — Add, view, and delete students with auto-generated registration numbers (`STU<YEAR><XXXX>`)
- **Faculty Management** — Add, view, and delete faculty with auto-generated IDs (`FAC<YEAR><XXXX>`)
- **QR Code Generation** — Automatically generates a QR code PNG for every new student
- **Attendance Marking** — Mark attendance via webcam QR scan or manual registration number entry
- **Duplicate Prevention** — Blocks marking the same person twice in a single day
- **Dashboard Stats** — Live counts of students, faculty, and today's attendance
- **Excel Export** — Export full attendance records to a timestamped `.xlsx` file

---

## ⚙️ Requirements

**Python 3.8+** and **MySQL 8.0+** are required.

Install all Python dependencies:

```bash
pip install flask flask-cors mysql-connector-python qrcode opencv-python pyzbar openpyxl
```

> **Windows users:** You may also need to install the Visual C++ runtime for `pyzbar`.  
> **Linux users:** `sudo apt-get install libzbar0`

---

## 🚀 Setup & Installation

### Step 1 — Configure Database Password

Open `database.py` and update the password field:

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'YOUR_PASSWORD_HERE',   # ← change this
    'database': 'attendance_system'
}
```

Do the same in `manual_setup.py` (line 9) and `test_db.py`.

### Step 2 — Initialize the Database

**Option A** (recommended):
```bash
python database.py init
```

**Option B** (if Option A fails):
```bash
python manual_setup.py
```

This creates the `attendance_system` database with all required tables and adds a default admin account.

### Step 3 — Start the Backend

```bash
python app.py
```

The API server will start at `http://localhost:5000`.

### Step 4 — Open the Frontend

Open `index.html` in your browser directly (double-click or `File > Open`).

### Step 5 — Login

| Field    | Value      |
|----------|------------|
| Username | `suraj`    |
| Password | `admin123` |

---

## 🌐 API Reference

Base URL: `http://localhost:5000/api`

| Method   | Endpoint                        | Description                  |
|----------|---------------------------------|------------------------------|
| `POST`   | `/login`                        | Admin login                  |
| `GET`    | `/students`                     | List all students            |
| `POST`   | `/students`                     | Add a new student            |
| `DELETE` | `/students/<registration_no>`   | Delete a student             |
| `GET`    | `/faculty`                      | List all faculty             |
| `POST`   | `/faculty`                      | Add a new faculty member     |
| `DELETE` | `/faculty/<faculty_regno>`      | Delete a faculty member      |
| `GET`    | `/attendance`                   | Get all attendance records   |
| `POST`   | `/attendance/mark`              | Mark attendance manually     |
| `GET`    | `/attendance/export`            | Export attendance to Excel   |
| `GET`    | `/stats`                        | Get dashboard statistics     |
| `GET`    | `/qr/<registration_no>`         | Get QR code image            |
| `POST`   | `/scanner/start`                | Start webcam QR scanner      |

---

## 🗄️ Database Schema

**`admin`** — Admin user credentials  
**`students`** — Student records with auto-generated registration numbers  
**`faculty`** — Faculty records with auto-generated IDs  
**`attendance`** — Attendance log linked to students/faculty by registration number  

---

## 🧪 Testing

**Test the database connection:**
```bash
python test_db.py
```

**Test all API endpoints in the browser:**  
Open `test_api.html` in your browser while `app.py` is running, then click "Run All Tests".

---

## 🔧 Troubleshooting

| Problem | Solution |
|---|---|
| `Database Connection Error` | Check MySQL is running and password is correct in `database.py` |
| `Could not open webcam` | Close other apps using the camera; try running as administrator |
| QR codes not generating | Ensure the `QR_Codes/` folder has write permissions |
| CORS errors in browser | Make sure `app.py` is running before opening `index.html` |
| `pyzbar` import error | Linux: `sudo apt-get install libzbar0`; Windows: install VC++ runtime |

---

## 📝 Notes

- Passwords are stored in plain text. For production use, replace with hashed passwords (e.g., `bcrypt`).
- The QR scanner opens a native OpenCV window — it does not run in the browser.
- Registration numbers follow the format `STU<YEAR><4-digit-sequence>` for students and `FAC<YEAR><4-digit-sequence>` for faculty.
- Attendance export files are saved in the project root directory as `Attendance_Report_<YYYY-MM-DD>.xlsx`.
