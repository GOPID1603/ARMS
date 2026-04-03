from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sqlite3
import random
import json
import os

app = Flask(__name__)
CORS(app)
DB_PATH = 'database.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        with open('database_schema.sql', 'r') as f:
            conn.executescript(f.read())
        
        # Seed students if empty
        r = conn.execute("SELECT Count(*) as c FROM students").fetchone()
        if r['c'] == 0:
            print("Seeding database...")
            students = [
                ('202611001', 'Arjun Krishnan', 'CSE', 'AI & ML', '2026', 'arjun@student.edu', '9876543210', 8.7, 6, 120, 1, 0, 82),
                ('202611002', 'Priya Nair', 'CSE', 'Cybersecurity', '2026', 'priya@student.edu', '9876543211', 9.1, 6, 128, 1, 1, 91),
                ('202624001', 'Rahul Mehta', 'AIDS', 'Data Science', '2026', 'rahul@student.edu', '9876543212', 7.9, 6, 112, 1, 0, 79),
                ('202625001', 'Sneha Iyer', 'AIML', 'Deep Learning', '2026', 'sneha@student.edu', '9876543213', 8.4, 6, 118, 1, 2, 74),
                ('202611003', 'Karthik Rajan', 'CSE', 'IoT', '2026', 'karthik@student.edu', '9876543214', 6.8, 6, 100, 1, 0, 68),
                ('202625002', 'Ananya Sharma', 'AIML', 'NLP', '2026', 'ananya@student.edu', '9876543215', 9.3, 6, 130, 1, 0, 95)
            ]
            
            # Generate random students 
            depts = ['CSE', 'AIDS', 'AIML']
            specs = {'CSE': ['AI & ML', 'Cybersecurity', 'IoT'], 'AIDS': ['Data Science', 'Big Data'], 'AIML': ['Deep Learning', 'NLP']}
            fnames = ['Vikram', 'Divya', 'Rohan', 'Lakshmi', 'Amit', 'Neha', 'Sanjay', 'Pooja', 'Vivek', 'Kavita']
            lnames = ['Singh', 'Murthy', 'Nambiar', 'Patel', 'Kumar', 'Reddy', 'Gowda', 'Menon', 'Pillai', 'Rao']
            
            for i in range(11, 220):
                dept = random.choice(depts)
                spec = random.choice(specs[dept])
                reg = f"2026{'11' if dept=='CSE' else '24' if dept=='AIDS' else '25'}{i:04d}"
                name = f"{random.choice(fnames)} {random.choice(lnames)}"
                students.append((reg, name, dept, spec, '2026', f"{name.split(' ')[0].lower()}@student.edu", f"9{random.randint(10000000, 99999999)}", round(random.uniform(6.0, 9.9), 1), 6, random.randint(110, 130), 1, 0, random.randint(65, 99)))
                
            conn.executemany("INSERT INTO students VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", students)
            
            # Seed Faculty
            faculties = [
                ('DG11001', 'Dr. Deepa Gopal', 'CSE', 'Associate Professor', 'deepa@college.edu', '9876540001', 3),
                ('DG24001', 'Prof. Anand Kumar', 'AIDS', 'Assistant Professor', 'anand@college.edu', '9876540002', 2),
                ('DG25001', 'Dr. Ramya Suresh', 'AIML', 'Professor', 'ramya@college.edu', '9876540003', 3)
            ]
            conn.executemany("INSERT INTO faculty VALUES(?,?,?,?,?,?,?)", faculties)
            
            # Seed Courses
            courses = [
                ('CS601', 'Machine Learning', 4, 'CSE', 6, 'DG11001', 42, 70, 'A', 'Mon/Wed 10:30', 'Room 204'),
                ('CS602', 'Cloud Computing', 3, 'CSE', 6, 'DG11001', 38, 55, 'B+', 'Tue/Thu 9:00', 'Lab 3'),
                ('AI601', 'Deep Learning', 4, 'AIML', 6, 'DG25001', 35, 80, 'A+', 'Mon/Fri 11:00', 'Lab 1'),
                ('DS601', 'Data Analytics', 3, 'AIDS', 6, 'DG24001', 40, 65, 'A', 'Wed/Fri 2:00', 'Room 102'),
                ('CS603', 'Blockchain Tech', 2, 'CSE', 6, 'DG11001', 30, 45, 'B', 'Fri 1:00', 'Room 101')
            ]
            conn.executemany("INSERT INTO courses VALUES(?,?,?,?,?,?,?,?,?,?,?)", courses)
            
            # Seed Notifications
            notifs = [
                ('Assignment Due Soon', 'ML Assignment 3 due on March 20 — submit via portal', 'Mar 13', 'warning', 0),
                ('Internal Assessment 2', 'IA2 starts April 1. Syllabus coverage: Units 3-5', 'Mar 12', 'danger', 0),
                ('Fee Payment Reminder', 'Last date for semester fee payment is March 31', 'Mar 11', 'info', 1)
            ]
            conn.executemany("INSERT INTO notifications (title, msg, date, priority, read) VALUES(?,?,?,?,?)", notifs)
            
            # Seed Disciplinary
            discs = [
                ('202611002', 'Priya Nair', 'Minor', 'Late submission of assignment', '2026-02-15', 'DG11001', 'First occurrence. Warning issued.'),
                ('202625001', 'Sneha Iyer', 'Serious', 'Plagiarism detected in project', '2026-02-20', 'DG25001', 'Academic integrity violation. Re-submission required.'),
                ('202611003', 'Karthik Rajan', 'Minor', 'Dress code violation', '2026-03-01', 'DG11001', 'Verbal warning given.')
            ]
            conn.executemany("INSERT INTO disciplinary (student, name, severity, reason, date, faculty, notes) VALUES (?,?,?,?,?,?,?)", discs)
            
            conn.commit()

@app.route('/api/data', methods=['GET'])
def get_all_data():
    with get_db() as conn:
        students = [dict(row) for row in conn.execute('SELECT * FROM students').fetchall()]
        faculty = [dict(row) for row in conn.execute('SELECT * FROM faculty').fetchall()]
        courses = [dict(row) for row in conn.execute('SELECT * FROM courses').fetchall()]
        notifications = [dict(row) for row in conn.execute('SELECT * FROM notifications ORDER BY id DESC').fetchall()]
        disciplinary = [dict(row) for row in conn.execute('SELECT * FROM disciplinary ORDER BY id DESC').fetchall()]
        odRequests = [dict(row) for row in conn.execute('SELECT * FROM od_requests ORDER BY id DESC').fetchall()]
        attendance_records = [dict(row) for row in conn.execute('SELECT * FROM attendance_records').fetchall()]
        student_courses = [dict(row) for row in conn.execute('SELECT * FROM student_courses').fetchall()]
        
        return jsonify({
            'students': students,
            'faculty': faculty,
            'courses': courses,
            'notifications': notifications,
            'disciplinary': disciplinary,
            'odRequests': odRequests,
            'attendance_records': attendance_records,
            'student_courses': student_courses,
            'semesterGrades': [
                { 'sem': 'Sem 1', 'gpa': 8.2 }, { 'sem': 'Sem 2', 'gpa': 8.5 }, { 'sem': 'Sem 3', 'gpa': 8.9 }, { 'sem': 'Sem 4', 'gpa': 9.0 }, { 'sem': 'Sem 5', 'gpa': 8.7 }, { 'sem': 'Sem 6', 'gpa': 8.7 }
            ],
            'completedCourses': [
                { 'code': 'CS501', 'name': 'Operating Systems', 'credits': 4, 'grade': 'A', 'gp': 9, 'sem': 5 },
                { 'code': 'CS502', 'name': 'Computer Networks', 'credits': 3, 'grade': 'B+', 'gp': 8, 'sem': 5 },
                { 'code': 'CS401', 'name': 'Data Structures & Algorithms', 'credits': 4, 'grade': 'O', 'gp': 10, 'sem': 4 },
                { 'code': 'CS402', 'name': 'Database Management Systems', 'credits': 3, 'grade': 'A+', 'gp': 9, 'sem': 4 }
            ],
            'attendance': {
                'overall': 82, 
                'subjects': [
                    { 'code': 'CS601', 'name': 'Machine Learning', 'present': 34, 'total': 42, 'pct': 81 },
                    { 'code': 'CS602', 'name': 'Cloud Computing', 'present': 28, 'total': 32, 'pct': 87 }
                ],
                'records': [
                  { 'date': '2026-03-13', 'course': 'CS601', 'status': 'Present' },
                  { 'date': '2026-03-12', 'course': 'CS602', 'status': 'Absent' }
                ]
            },
            'fees': {
                'total': 75000, 'paid': 50000, 'due': 25000, 'dueDate': '2026-03-31', 
                'history': [ { 'date': '2026-01-05', 'desc': 'Tuition Fee – Semester I', 'amount': 25000, 'status': 'Paid' } ]
            },
            'placements': []
        })

@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.json
    try:
        with get_db() as conn:
            conn.execute('''INSERT INTO students (reg, name, dept, spec, batch, email, phone, cgpa, sem, credits, pass, disc, att)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                         (data['reg'], data['name'], data['dept'], data.get('spec', ''), data['batch'], data['email'], 
                          data['phone'], data['cgpa'], data['sem'], data.get('credits', 0), int(data['pass']==True), 0, 100))
            conn.commit()
            return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/students/<reg>', methods=['DELETE'])
def delete_student(reg):
    with get_db() as conn:
        conn.execute('DELETE FROM disciplinary WHERE student=?', (reg,))
        conn.execute('DELETE FROM students WHERE reg=?', (reg,))
        conn.commit()
    return jsonify({'success': True})

@app.route('/api/notifications', methods=['POST'])
def add_notification():
    data = request.json
    with get_db() as conn:
        conn.execute('INSERT INTO notifications (title, msg, date, priority, read) VALUES (?, ?, ?, ?, 0)',
                     (data['title'], data['msg'], data.get('date', 'Today'), data['priority']))
        conn.commit()
    return jsonify({'success': True})

@app.route('/api/disciplinary', methods=['POST'])
def add_disc():
    data = request.json
    with get_db() as conn:
        conn.execute('INSERT INTO disciplinary (student, name, severity, reason, date, faculty, notes) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (data['student'], data['name'], data['severity'], data['reason'], data['date'], data['faculty'], data.get('notes', '')))
        conn.commit()
    return jsonify({'success': True})

@app.route('/api/od', methods=['POST'])
def request_od():
    data = request.json
    with get_db() as conn:
        conn.execute('INSERT INTO od_requests (date, course, reason, student_reg, faculty_status, admin_status) VALUES (?, ?, ?, ?, "Pending", "Pending")',
                     (data['date'], data['course'], data['reason'], data.get('student_reg', 'UNKNOWN')))
        conn.commit()
    return jsonify({'success': True})

@app.route('/api/od/<int:id>', methods=['PUT'])
def update_od(id):
    data = request.json
    role = data.get('role')
    status = data.get('status')
    with get_db() as conn:
        if role == 'faculty':
            conn.execute('UPDATE od_requests SET faculty_status = ? WHERE id = ?', (status, id))
        elif role == 'admin':
            conn.execute('UPDATE od_requests SET admin_status = ? WHERE id = ?', (status, id))
        conn.commit()
    return jsonify({'success': True})

@app.route('/api/courses', methods=['POST'])
def create_course():
    data = request.json
    with get_db() as conn:
        conn.execute('INSERT INTO courses (code, name, credits, dept, sem, faculty, students, progress, grade, schedule, room) VALUES (?, ?, ?, ?, ?, ?, 0, 0, "", ?, "")',
                     (data['code'], data['name'], data['credits'], data['dept'], data['sem'], data['faculty'], data['schedule']))
        conn.commit()
    return jsonify({'success': True})

@app.route('/api/enroll', methods=['POST'])
def enroll_student():
    data = request.json
    with get_db() as conn:
        cur = conn.execute('SELECT * FROM student_courses WHERE student_reg=? AND course_code=?', (data['student_reg'], data['course_code'])).fetchone()
        if not cur:
            conn.execute('INSERT INTO student_courses (student_reg, course_code) VALUES (?, ?)', (data['student_reg'], data['course_code']))
            conn.execute('UPDATE courses SET students = students + 1 WHERE code = ?', (data['course_code'],))
            conn.commit()
    return jsonify({'success': True})

@app.route('/api/attendance', methods=['POST'])
def submit_bulk_attendance():
    records = request.json.get('records', [])
    with get_db() as conn:
        for r in records:
            conn.execute('INSERT INTO attendance_records (date, course, status, student_reg) VALUES (?, ?, ?, ?)',
                         (r['date'], r['course'], r['status'], r['student_reg']))
        conn.commit()
    return jsonify({'success': True})

@app.route('/')
def index():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'student360_enhanced.html')
    return send_file(html_path)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
