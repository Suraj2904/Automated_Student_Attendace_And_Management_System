// ============================================
// QR ATTENDANCE SYSTEM - JAVASCRIPT
// ============================================

// API Configuration
const API_URL = 'http://localhost:5000/api';



// Global State
let currentView = 'dashboard';

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Show alert message
 * @param {string} message - Message to display
 * @param {string} type - 'success' or 'error'
 */
function showAlert(message, type = 'success') {
    const alert = document.getElementById('alert');
    const alertMessage = document.getElementById('alertMessage');
    const alertIcon = document.getElementById('alertIcon');

    alert.className = `alert alert-${type} show`;
    alertMessage.textContent = message;
    alertIcon.textContent = type === 'success' ? '✓' : '✕';

    // Auto hide after 5 seconds
    setTimeout(() => {
        alert.classList.remove('show');
    }, 5000);
}

/**
 * API call helper function
 * @param {string} endpoint - API endpoint
 * @param {object} options - Fetch options
 * @returns {Promise} Response data
 */
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_URL}${endpoint}`, options);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API Error:', error);
        showAlert('Connection error. Make sure Flask server is running on port 5000', 'error');
        return { success: false, message: 'Connection error' };
    }
}

/**
 * Set button loading state
 * @param {string} btnTextId - Button text element ID
 * @param {boolean} loading - Loading state
 * @param {string} text - Button text
 */
function setButtonLoading(btnTextId, loading, text = '') {
    const btnText = document.getElementById(btnTextId);
    if (loading) {
        btnText.innerHTML = '<span class="loader"></span>Loading...';
    } else {
        btnText.textContent = text;
    }
}

// ============================================
// AUTHENTICATION
// ============================================

/**
 * Login function
 */
async function login(){
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // Validation
    if (!username || !password) {
        showAlert('Please enter username and password', 'error');
        return;
    }

    setButtonLoading('loginBtnText', true);

    // API call
    const data = await apiCall('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
    });

    setButtonLoading('loginBtnText', false, 'Login');

    // Handle response
    if (data.success) {
        showAlert('Login successful!');
        document.getElementById('loginScreen').style.display = 'none';
        document.getElementById('dashboard').classList.add('active');
        loadDashboard();
    } else {
        showAlert(data.message || 'Invalid credentials', 'error');
    }
}

/**
 * Logout function
 */
function logout() {
    document.getElementById('loginScreen').style.display = 'flex';
    document.getElementById('dashboard').classList.remove('active');
    document.getElementById('username').value = '';
    document.getElementById('password').value = '';
}

// ============================================
// NAVIGATION
// ============================================

/**
 * Show specific view
 * @param {string} view - View name to show
 */
function showView(view) {
    // Hide all views
    document.querySelectorAll('.content-card').forEach(card => {
        card.classList.add('hidden');
    });

    // Remove active class from nav cards
    document.querySelectorAll('.nav-card').forEach(card => {
        card.classList.remove('active');
    });

    // Update current view
    currentView = view;

    // View mapping
    const viewMap = {
        'dashboard': 'dashboardView',
        'addStudent': 'addStudentView',
        'addFaculty': 'addFacultyView',
        'viewStudents': 'viewStudentsView',
        'viewFaculty': 'viewFacultyView',
        'attendance': 'attendanceView',
        'scanner': 'scannerView'
    };

    // Show selected view
    const viewElement = document.getElementById(viewMap[view]);
    if (viewElement) {
        viewElement.classList.remove('hidden');
    }

    // Load data for specific views
    if (view === 'dashboard') loadDashboard();
    else if (view === 'viewStudents') loadStudents();
    else if (view === 'viewFaculty') loadFaculty();
    else if (view === 'attendance') loadAttendance();
}

// ============================================
// DASHBOARD
// ============================================

/**
 * Load dashboard data
 */
async function loadDashboard() {
    // Load statistics
    const stats = await apiCall('/stats');
    if (stats.success) {
        document.getElementById('statStudents').textContent = stats.data.students;
        document.getElementById('statFaculty').textContent = stats.data.faculty;
        document.getElementById('statAttendance').textContent = stats.data.today_attendance;
    }

    // Load recent attendance
    const attendance = await apiCall('/attendance');
    if (attendance.success && attendance.data.length > 0) {
        const tbody = document.getElementById('recentAttendanceTable');
        tbody.innerHTML = attendance.data.slice(0, 5).map(record => `
            <tr>
                <td>${record.registration_no}</td>
                <td>${record.name || 'N/A'}</td>
                <td>${record.date}</td>
                <td>${record.time}</td>
                <td><span class="badge badge-success">${record.status}</span></td>
            </tr>
        `).join('');
    }
}

// ============================================
// STUDENT MANAGEMENT
// ============================================

/**
 * Add new student
 */
async function addStudent() {
    const name = document.getElementById('studentName').value;
    const roll = document.getElementById('studentRoll').value;
    const course = document.getElementById('studentCourse').value;

    // Validation
    if (!name || !roll || !course) {
        showAlert('All fields are required', 'error');
        return;
    }

    setButtonLoading('addStudentBtnText', true);

    // API call
    const data = await apiCall('/students', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, roll, course })
    });

    setButtonLoading('addStudentBtnText', false, 'Add Student');

    // Handle response
    if (data.success) {
        showAlert(`Student added! Registration: ${data.registration_no}`);
        // Clear form
        document.getElementById('studentName').value = '';
        document.getElementById('studentRoll').value = '';
        document.getElementById('studentCourse').value = '';
    } else {
        showAlert(data.message, 'error');
    }
}

/**
 * Load all students
 */
async function loadStudents() {
    const data = await apiCall('/students');

    if (data.success) {
        document.getElementById('studentCount').textContent = data.data.length;
        const tbody = document.getElementById('studentsTable');

        if (data.data.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="empty-state">
                        <div class="empty-state-icon">Student Icon</div>
                        <div>No students found</div>
                    </td>
                </tr>
            `;
        } else {
            tbody.innerHTML = data.data.map(student => `
                <tr>
                    <td>${student.registration_no}</td>
                    <td>${student.roll_no}</td>
                    <td>${student.name}</td>
                    <td>${student.course}</td>
                    <td>
                        <button class="btn-delete" onclick="deleteStudent('${student.registration_no}')">
                            Delete
                        </button>
                    </td>
                </tr>
            `).join('');
        }
    }
}

/**
 * Delete student
 * @param {string} regno - Registration number
 */
async function deleteStudent(regno) {
    if (!confirm('Are you sure you want to delete this student?')) return;

    const data = await apiCall(`/students/${regno}`, { method: 'DELETE' });

    if (data.success) {
        showAlert('Student deleted successfully');
        loadStudents();
    } else {
        showAlert(data.message, 'error');
    }
}

// ============================================
// FACULTY MANAGEMENT
// ============================================

/**
 * Add new faculty
 */
async function addFaculty() {
    const name = document.getElementById('facultyName').value;
    const department = document.getElementById('facultyDept').value;

    // Validation
    if (!name || !department) {
        showAlert('All fields are required', 'error');
        return;
    }

    setButtonLoading('addFacultyBtnText', true);

    // API call
    const data = await apiCall('/faculty', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, department })
    });

    setButtonLoading('addFacultyBtnText', false, 'Add Faculty');

    // Handle response
    if (data.success) {
        showAlert(`Faculty added! Registration: ${data.faculty_regno}`);
        // Clear form
        document.getElementById('facultyName').value = '';
        document.getElementById('facultyDept').value = '';
    } else {
        showAlert(data.message, 'error');
    }
}

/**
 * Load all faculty
 */
async function loadFaculty() {
    const data = await apiCall('/faculty');

    if (data.success) {
        document.getElementById('facultyCount').textContent = data.data.length;
        const tbody = document.getElementById('facultyTable');

        if (data.data.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="4" class="empty-state">
                        <div class="empty-state-icon">Faculty Icon</div>
                        <div>No faculty found</div>
                    </td>
                </tr>
            `;
        } else {
            tbody.innerHTML = data.data.map(fac => `
                <tr>
                    <td>${fac.faculty_regno}</td>
                    <td>${fac.faculty_name}</td>
                    <td>${fac.department}</td>
                    <td>
                        <button class="btn-delete" onclick="deleteFaculty('${fac.faculty_regno}')">
                            Delete
                        </button>
                    </td>
                </tr>
            `).join('');
        }
    }
}

/**
 * Delete faculty
 * @param {string} regno - Registration number
 */
async function deleteFaculty(regno) {
    if (!confirm('Are you sure you want to delete this faculty?')) return;

    const data = await apiCall(`/faculty/${regno}`, { method: 'DELETE' });

    if (data.success) {
        showAlert('Faculty deleted successfully');
        loadFaculty();
    } else {
        showAlert(data.message, 'error');
    }
}

// ============================================
// ATTENDANCE MANAGEMENT
// ============================================

/**
 * Load all attendance records
 */
async function loadAttendance() {
    const data = await apiCall('/attendance');

    if (data.success) {
        const tbody = document.getElementById('attendanceTable');

        if (data.data.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="empty-state">
                        <div class="empty-state-icon">Attendance Icon</div>
                        <div>No attendance records</div>
                    </td>
                </tr>
            `;
        } else {
            tbody.innerHTML = data.data.map(record => `
                <tr>
                    <td>${record.registration_no}</td>
                    <td>${record.name || 'N/A'}</td>
                    <td>${record.roll_no || record.department || 'N/A'}</td>
                    <td>${record.date}</td>
                    <td>${record.time}</td>
                    <td><span class="badge badge-success">${record.status}</span></td>
                </tr>
            `).join('');
        }
    }
}

/**
 * Mark attendance
 */
async function markAttendance() {
    const regno = document.getElementById('qrInput').value;

    // Validation
    if (!regno) {
        showAlert('Please enter registration number', 'error');
        return;
    }

    setButtonLoading('markAttendanceBtnText', true);

    // API call
    const data = await apiCall('/attendance/mark', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ registration_no: regno })
    });

    setButtonLoading('markAttendanceBtnText', false, 'Mark Attendance');

    // Handle response
    if (data.success) {
        showAlert('Attendance marked successfully!');
        document.getElementById('qrInput').value = '';
    } else {
        showAlert(data.message, 'error');
    }
}

//-------------- QR Scanner ------------- #

/**
 * Start QR Code Scanner
 * Opens webcam to scan QR codes
 */
async function startQRScanner() {
    const btnText = document.getElementById('scannerBtnText');

    // Update button
    btnText.innerHTML = '<span class="loader"></span>Starting...';

    try {
        const response = await fetch(`${API_URL}/scanner/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        const data = await response.json();

        if (data.success) {
            showAlert('Scanner started! Show QR code. Press Q to quit.', 'success');
            btnText.innerHTML = ' Scanner Running';

            setTimeout(() => {
                btnText.innerHTML = ' Start QR Scanner';
            }, 5000);
        } else {
            showAlert(data.message || 'Failed to start scanner', 'error');
            btnText.innerHTML = ' Start QR Scanner';
        }

    } catch (error) {
        showAlert('Error starting scanner', 'error');
        btnText.innerHTML = ' Start QR Scanner';
    }
}
/**
 * Export attendance to Excel
 */
async function exportAttendance() {
    const data = await apiCall('/attendance/export');

    if (data.success) {
        showAlert(`Attendance exported! File: ${data.filename}`);
    } else {
        showAlert(data.message, 'error');
    }
}

// ============================================
// EVENT LISTENERS
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Enter key on password field triggers login
    const passwordField = document.getElementById('password');
    if (passwordField) {
        passwordField.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') login();
        });
    }

    // Enter key on QR input triggers mark attendance
    const qrInput = document.getElementById('qrInput');
    if (qrInput) {
        qrInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') markAttendance();
        });
    }
});

// ============================================
// CONSOLE INFO
// ============================================

console.log('QR Attendance System - JavaScript Loaded');
console.log('API URL:', API_URL);
console.log('Make sure Flask backend is running on port 5000');