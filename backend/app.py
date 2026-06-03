from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from supabase import create_client, Client
import random
import json
import os
import sqlite3
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__, static_folder='..', static_url_path='')
CORS(app)

# =========================================================
# CHATBOT AI CONFIGURATION
# =========================================================
CHATBOT_API_KEY = "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"
CHATBOT_PROVIDER = "groq"

# =========================================================
# SUPABASE CONFIGURATION & DUAL DB SETUP
# =========================================================
SUPABASE_URL = "https://mihwjfgwjdkraxyceamj.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1paHdqZmd3amRrcmF4eWNlYW1qIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3ODU2NzgyNiwiZXhwIjoyMDk0MTQzODI2fQ.IGa0ajGxa1yR2KCDKUMkqCx-0SUnTHSvkHb5cdUZJNw"

use_sqlite = False
supabase: Client = None

if SUPABASE_URL != "YOUR_SUPABASE_URL":
    try:
        import urllib.request
        from urllib.parse import urlparse
        import socket
        parsed_url = urlparse(SUPABASE_URL)
        socket.setdefaulttimeout(3)
        socket.gethostbyname(parsed_url.hostname)
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        # Attempt a quick check
        supabase.table('students').select('count', count='exact').limit(1).execute()
        print("Connected to Supabase successfully.")
    except Exception as e:
        print(f"Supabase connection failed ({e}). Falling back to local SQLite database.")
        use_sqlite = True
else:
    use_sqlite = True

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Helper for SQLite auto-increment IDs if needed
def get_next_id_sqlite(conn, table):
    try:
        row = conn.execute(f"SELECT MAX(id) as max_id FROM {table}").fetchone()
        return (row['max_id'] or 0) + 1
    except Exception:
        import time
        return int(time.time() * 1000) % 1000000

# Helper for Supabase auto-increment IDs
def get_next_id_supabase(table):
    try:
        res = supabase.table(table).select('id').order('id', desc=True).limit(1).execute().data
        return res[0]['id'] + 1 if res else 1
    except Exception:
        import time
        return int(time.time() * 1000) % 1000000

# =========================================================

@app.route('/api/data', methods=['GET'])
def get_all_data():
    if use_sqlite:
        try:
            with get_db() as conn:
                students = [dict(row) for row in conn.execute('SELECT * FROM students').fetchall()]
                faculty = [dict(row) for row in conn.execute('SELECT * FROM faculty').fetchall()]
                courses = [dict(row) for row in conn.execute('SELECT * FROM courses').fetchall()]
                notifications = [dict(row) for row in conn.execute('SELECT * FROM notifications ORDER BY id DESC').fetchall()]
                disciplinary = [dict(row) for row in conn.execute('SELECT * FROM disciplinary ORDER BY id DESC').fetchall()]
                odRequests = [dict(row) for row in conn.execute('SELECT * FROM od_requests ORDER BY id DESC').fetchall()]
                attendance_records = [dict(row) for row in conn.execute('SELECT * FROM attendance_records').fetchall()]
                student_courses = [dict(row) for row in conn.execute('SELECT * FROM student_courses').fetchall()]
                chatbotLogs = [dict(row) for row in conn.execute('SELECT * FROM chatbot_logs ORDER BY id ASC').fetchall()]
                blockedUsers = [row['user_id'] for row in conn.execute('SELECT user_id FROM blocked_users').fetchall()]
                
                return jsonify({
                    'students': students,
                    'faculty': faculty,
                    'courses': courses,
                    'notifications': notifications,
                    'disciplinary': disciplinary,
                    'odRequests': odRequests,
                    'attendance_records': attendance_records,
                    'student_courses': student_courses,
                    'chatbotLogs': chatbotLogs,
                    'blockedUsers': blockedUsers,
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
        except Exception as e:
            return jsonify({'error': f"SQLite Error: {str(e)}"}), 500

    if not supabase: return jsonify({'error': 'Supabase not configured'}), 500
    try:
        def fetch_table(table, order_col=None, desc=False, select_cols='*'):
            q = supabase.table(table).select(select_cols)
            if order_col:
                q = q.order(order_col, desc=desc)
            return q.execute().data

        with ThreadPoolExecutor(max_workers=10) as executor:
            f_students = executor.submit(fetch_table, 'students')
            f_faculty = executor.submit(fetch_table, 'faculty')
            f_courses = executor.submit(fetch_table, 'courses')
            f_notifs = executor.submit(fetch_table, 'notifications', 'id', True)
            f_disc = executor.submit(fetch_table, 'disciplinary', 'id', True)
            f_od = executor.submit(fetch_table, 'od_requests', 'id', True)
            f_att = executor.submit(fetch_table, 'attendance_records')
            f_sc = executor.submit(fetch_table, 'student_courses')
            f_chat = executor.submit(fetch_table, 'chatbot_logs', 'id', False)
            f_block = executor.submit(fetch_table, 'blocked_users', None, False, 'user_id')

        students = f_students.result()
        faculty = f_faculty.result()
        courses = f_courses.result()
        notifications = f_notifs.result()
        disciplinary = f_disc.result()
        odRequests = f_od.result()
        attendance_records = f_att.result()
        student_courses = f_sc.result()
        chatbotLogs = f_chat.result()
        blockedUsers = [r['user_id'] for r in f_block.result()]
        
        return jsonify({
            'students': students,
            'faculty': faculty,
            'courses': courses,
            'notifications': notifications,
            'disciplinary': disciplinary,
            'odRequests': odRequests,
            'attendance_records': attendance_records,
            'student_courses': student_courses,
            'chatbotLogs': chatbotLogs,
            'blockedUsers': blockedUsers,
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
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.json
    if use_sqlite:
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

    if not supabase: return jsonify({'success': False, 'error': 'Supabase not configured'}), 500
    try:
        supabase.table('students').insert({
            'reg': data['reg'], 'name': data['name'], 'dept': data['dept'], 'spec': data.get('spec', ''), 
            'batch': data['batch'], 'email': data['email'], 'phone': data['phone'], 'cgpa': data['cgpa'], 
            'sem': data['sem'], 'credits': data.get('credits', 0), 'pass': int(data['pass']==True), 'disc': 0, 'att': 100
        }).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/students/<reg>', methods=['DELETE'])
def delete_student(reg):
    if use_sqlite:
        try:
            with get_db() as conn:
                conn.execute('DELETE FROM disciplinary WHERE student=?', (reg,))
                conn.execute('DELETE FROM students WHERE reg=?', (reg,))
                conn.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    if not supabase: return jsonify({'success': False, 'error': 'Supabase not configured'}), 500
    try:
        supabase.table('disciplinary').delete().eq('student', reg).execute()
        supabase.table('students').delete().eq('reg', reg).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/notifications', methods=['POST'])
def add_notification():
    data = request.json
    if use_sqlite:
        try:
            with get_db() as conn:
                conn.execute('INSERT INTO notifications (title, msg, date, priority, read) VALUES (?, ?, ?, ?, 0)',
                             (data['title'], data['msg'], data.get('date', 'Today'), data['priority']))
                conn.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    if not supabase: return jsonify({'success': False}), 500
    try:
        supabase.table('notifications').insert({
            'id': get_next_id_supabase('notifications'), 'title': data['title'], 'msg': data['msg'], 'date': data.get('date', 'Today'), 'priority': data['priority'], 'read': 0
        }).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/disciplinary', methods=['POST'])
def add_disc():
    data = request.json
    if use_sqlite:
        try:
            with get_db() as conn:
                conn.execute('INSERT INTO disciplinary (student, name, severity, reason, date, faculty, notes) VALUES (?, ?, ?, ?, ?, ?, ?)',
                             (data['student'], data['name'], data['severity'], data['reason'], data['date'], data['faculty'], data.get('notes', '')))
                conn.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    if not supabase: return jsonify({'success': False}), 500
    try:
        supabase.table('disciplinary').insert({
            'id': get_next_id_supabase('disciplinary'), 'student': data['student'], 'name': data['name'], 'severity': data['severity'], 'reason': data['reason'], 'date': data['date'], 'faculty': data['faculty'], 'notes': data.get('notes', '')
        }).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/od', methods=['POST'])
def request_od():
    data = request.json
    if use_sqlite:
        try:
            with get_db() as conn:
                conn.execute('INSERT INTO od_requests (date, course, reason, student_reg, faculty_status, admin_status) VALUES (?, ?, ?, ?, "Pending", "Pending")',
                             (data['date'], data['course'], data['reason'], data.get('student_reg', 'UNKNOWN')))
                conn.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    if not supabase: return jsonify({'success': False}), 500
    try:
        supabase.table('od_requests').insert({
            'id': get_next_id_supabase('od_requests'), 'date': data['date'], 'course': data['course'], 'reason': data['reason'], 'student_reg': data.get('student_reg', 'UNKNOWN'), 'faculty_status': 'Pending', 'admin_status': 'Pending'
        }).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/od/<int:id>', methods=['PUT'])
def update_od(id):
    data = request.json
    role = data.get('role')
    status = data.get('status')
    if use_sqlite:
        try:
            with get_db() as conn:
                if role == 'faculty':
                    conn.execute('UPDATE od_requests SET faculty_status = ? WHERE id = ?', (status, id))
                elif role == 'admin':
                    conn.execute('UPDATE od_requests SET admin_status = ? WHERE id = ?', (status, id))
                conn.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    if not supabase: return jsonify({'success': False}), 500
    try:
        if role == 'faculty':
            supabase.table('od_requests').update({'faculty_status': status}).eq('id', id).execute()
        elif role == 'admin':
            supabase.table('od_requests').update({'admin_status': status}).eq('id', id).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/courses', methods=['POST'])
def create_course():
    data = request.json
    if use_sqlite:
        try:
            with get_db() as conn:
                conn.execute('INSERT INTO courses (code, name, credits, dept, sem, faculty, students, progress, grade, schedule, room) VALUES (?, ?, ?, ?, ?, ?, 0, 0, "", ?, "")',
                             (data['code'], data['name'], data['credits'], data['dept'], data['sem'], data['faculty'], data['schedule']))
                conn.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    if not supabase: return jsonify({'success': False}), 500
    try:
        supabase.table('courses').insert({
            'code': data['code'], 'name': data['name'], 'credits': data['credits'], 'dept': data['dept'], 'sem': data['sem'], 'faculty': data['faculty'], 'students': 0, 'progress': 0, 'grade': '', 'schedule': data['schedule'], 'room': ''
        }).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/enroll', methods=['POST'])
def enroll_student():
    data = request.json
    if use_sqlite:
        try:
            with get_db() as conn:
                cur = conn.execute('SELECT * FROM student_courses WHERE student_reg=? AND course_code=?', (data['student_reg'], data['course_code'])).fetchone()
                if not cur:
                    conn.execute('INSERT INTO student_courses (student_reg, course_code) VALUES (?, ?)', (data['student_reg'], data['course_code']))
                    conn.execute('UPDATE courses SET students = students + 1 WHERE code = ?', (data['course_code'],))
                    conn.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    if not supabase: return jsonify({'success': False, 'error': 'Supabase not configured'}), 500
    try:
        cur = supabase.table('student_courses').select('*').eq('student_reg', data['student_reg']).eq('course_code', data['course_code']).execute().data
        if not cur:
            supabase.table('student_courses').insert({'id': get_next_id_supabase('student_courses'), 'student_reg': data['student_reg'], 'course_code': data['course_code']}).execute()
            course = supabase.table('courses').select('students').eq('code', data['course_code']).execute().data[0]
            supabase.table('courses').update({'students': course['students'] + 1}).eq('code', data['course_code']).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/attendance', methods=['POST'])
def submit_bulk_attendance():
    records = request.json.get('records', [])
    if use_sqlite:
        try:
            with get_db() as conn:
                for r in records:
                    conn.execute('INSERT INTO attendance_records (date, course, status, student_reg) VALUES (?, ?, ?, ?)',
                                 (r['date'], r['course'], r['status'], r['student_reg']))
                conn.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    if not supabase: return jsonify({'success': False}), 500
    try:
        start_id = get_next_id_supabase('attendance_records')
        data_to_insert = [{'id': start_id + idx, 'date': r['date'], 'course': r['course'], 'status': r['status'], 'student_reg': r['student_reg']} for idx, r in enumerate(records)]
        if data_to_insert:
            supabase.table('attendance_records').insert(data_to_insert).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/chatbot', methods=['POST'])
def send_chatbot_msg():
    try:
        data = request.json
        uid = data.get('user_id')
        role = data.get('role')
        name = data.get('name')
        msg = data.get('message', '')
        
        # Check if blocked
        if use_sqlite:
            with get_db() as conn:
                blocked = conn.execute('SELECT * FROM blocked_users WHERE user_id=?', (uid,)).fetchone()
                if blocked:
                    return jsonify({'success': False, 'error': 'Blocked by Administrator'})
        else:
            if supabase:
                blocked = supabase.table('blocked_users').select('*').eq('user_id', uid).execute().data
                if blocked:
                    return jsonify({'success': False, 'error': 'Blocked by Administrator'})
        
        # Simple bot logic
        trigger_words = ['hack', 'cheat', 'badword', 'stupid', 'idiot', 'unnecessary']
        is_unnecessary = 1 if any(w in msg.lower() for w in trigger_words) else 0
        if CHATBOT_API_KEY:
            import urllib.request
            url = "https://api.groq.com/openai/v1/chat/completions"
            payload = json.dumps({
                "model": "llama-3.1-8b-instant",
                "messages": [
                    {"role": "system", "content": "You are a smart Portal AI Assistant. Provide helpful, short and concise answers."},
                    {"role": "user", "content": msg}
                ]
            }).encode('utf-8')
            req = urllib.request.Request(url, data=payload, headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {CHATBOT_API_KEY}',
                'User-Agent': 'requests/2.31.0'
            })
            try:
                with urllib.request.urlopen(req) as response:
                    resp_data = json.loads(response.read().decode('utf-8'))
                    resp = resp_data['choices'][0]['message']['content']
            except Exception as e:
                error_body = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
                resp = f"Error connecting to Groq API: {error_body}"
        else:
            resp = "Hello! I am your AI assistant. I have recorded your message. (Note: Please paste your Groq API Key at the top of backend/app.py to enable real AI!)"
            if "help" in msg.lower():
                resp = "I can help you navigate the portal or find standard procedures. Please specify what you need."
            elif "date" in msg.lower():
                import datetime as dt_mod
                resp = f"Today's date is {dt_mod.datetime.now().strftime('%Y-%m-%d')}."
            elif is_unnecessary:
                resp = "Warning: This message has been flagged as unnecessary."
        
        if use_sqlite:
            import datetime as dt_mod
            with get_db() as conn:
                conn.execute('INSERT INTO chatbot_logs (user_id, role, name, message, response, timestamp, is_unnecessary) VALUES (?, ?, ?, ?, ?, ?, ?)',
                             (uid, role, name, msg, resp, dt_mod.datetime.now().strftime('%I:%M %p'), is_unnecessary))
                conn.commit()
        else:
            if supabase:
                import datetime as dt_mod
                supabase.table('chatbot_logs').insert({
                    'id': get_next_id_supabase('chatbot_logs'), 'user_id': uid, 'role': role, 'name': name, 'message': msg, 'response': resp, 'timestamp': dt_mod.datetime.now().strftime('%I:%M %p'), 'is_unnecessary': is_unnecessary
                }).execute()
            
        return jsonify({'success': True, 'response': resp})
    except Exception as e:
        return jsonify({'success': False, 'error': f"Server Exception: {str(e)}"})

@app.route('/api/chatbot/block', methods=['POST'])
def block_chatbot_user():
    data = request.json
    uid = data['user_id']
    role = data.get('role', 'student')
    action = data.get('action')
    
    if use_sqlite:
        try:
            with get_db() as conn:
                if action == 'block':
                    existing = conn.execute('SELECT * FROM blocked_users WHERE user_id=?', (uid,)).fetchone()
                    if not existing:
                        conn.execute('INSERT INTO blocked_users (user_id, role) VALUES (?, ?)', (uid, role))
                else:
                    conn.execute('DELETE FROM blocked_users WHERE user_id=?', (uid,))
                conn.commit()
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 400

    if not supabase: return jsonify({'success': False}), 500
    try:
        if action == 'block':
            existing = supabase.table('blocked_users').select('*').eq('user_id', uid).execute().data
            if not existing:
                supabase.table('blocked_users').insert({'user_id': uid, 'role': role}).execute()
        else:
            supabase.table('blocked_users').delete().eq('user_id', uid).execute()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/')
def index():
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'index.html')
    return send_file(html_path)

@app.route('/api/seed', methods=['POST'])
def seed_database():
    if use_sqlite:
        # SQLite db already pre-seeded or can use the schema's default seed.
        return jsonify({'success': True, 'msg': 'SQLite database is already pre-seeded.'})

    if not supabase: return jsonify({'success': False, 'error': 'Supabase not configured'}), 500
    try:
        res = supabase.table('students').select('*', count='exact').limit(1).execute()
        if res.count and res.count > 0:
            return jsonify({'success': True, 'msg': 'Already seeded'})
            
        import random
        students_data = [
            {'reg':'202611001', 'name':'Arjun Krishnan', 'dept':'CSE', 'spec':'AI & ML', 'batch':'2026', 'email':'arjun@student.edu', 'phone':'9876543210', 'cgpa':8.7, 'sem':6, 'credits':120, 'pass':1, 'disc':0, 'att':82},
            {'reg':'202611002', 'name':'Priya Nair', 'dept':'CSE', 'spec':'Cybersecurity', 'batch':'2026', 'email':'priya@student.edu', 'phone':'9876543211', 'cgpa':9.1, 'sem':6, 'credits':128, 'pass':1, 'disc':1, 'att':91},
            {'reg':'202624001', 'name':'Rahul Mehta', 'dept':'AIDS', 'spec':'Data Science', 'batch':'2026', 'email':'rahul@student.edu', 'phone':'9876543212', 'cgpa':7.9, 'sem':6, 'credits':112, 'pass':1, 'disc':0, 'att':79},
            {'reg':'202625001', 'name':'Sneha Iyer', 'dept':'AIML', 'spec':'Deep Learning', 'batch':'2026', 'email':'sneha@student.edu', 'phone':'9876543213', 'cgpa':8.4, 'sem':6, 'credits':118, 'pass':1, 'disc':2, 'att':74},
            {'reg':'202611003', 'name':'Karthik Rajan', 'dept':'CSE', 'spec':'IoT', 'batch':'2026', 'email':'karthik@student.edu', 'phone':'9876543214', 'cgpa':6.8, 'sem':6, 'credits':100, 'pass':1, 'disc':0, 'att':68},
            {'reg':'202625002', 'name':'Ananya Sharma', 'dept':'AIML', 'spec':'NLP', 'batch':'2026', 'email':'ananya@student.edu', 'phone':'9876543215', 'cgpa':9.3, 'sem':6, 'credits':130, 'pass':1, 'disc':0, 'att':95}
        ]
        
        depts = ['CSE', 'AIDS', 'AIML']
        specs = {'CSE': ['AI & ML', 'Cybersecurity', 'IoT'], 'AIDS': ['Data Science', 'Big Data'], 'AIML': ['Deep Learning', 'NLP']}
        fnames = ['Vikram', 'Divya', 'Rohan', 'Lakshmi', 'Amit', 'Neha', 'Sanjay', 'Pooja', 'Vivek', 'Kavita']
        lnames = ['Singh', 'Murthy', 'Nambiar', 'Patel', 'Kumar', 'Reddy', 'Gowda', 'Menon', 'Pillai', 'Rao']
        
        for i in range(11, 220):
            dept = random.choice(depts)
            spec = random.choice(specs[dept])
            reg = f"2026{'11' if dept=='CSE' else '24' if dept=='AIDS' else '25'}{i:04d}"
            name = f"{random.choice(fnames)} {random.choice(lnames)}"
            students_data.append({'reg':reg, 'name':name, 'dept':dept, 'spec':spec, 'batch':'2026', 'email':f"{name.split(' ')[0].lower()}@student.edu", 'phone':f"9{random.randint(10000000, 99999999)}", 'cgpa':round(random.uniform(6.0, 9.9), 1), 'sem':6, 'credits':random.randint(110, 130), 'pass':1, 'disc':0, 'att':random.randint(65, 99)})
            
        supabase.table('students').insert(students_data).execute()
        
        faculties = [
            {'id':'DG11001', 'name':'Dr. Deepa Gopal', 'dept':'CSE', 'desig':'Associate Professor', 'email':'deepa@college.edu', 'phone':'9876540001', 'courses':3},
            {'id':'DG24001', 'name':'Prof. Anand Kumar', 'dept':'AIDS', 'desig':'Assistant Professor', 'email':'anand@college.edu', 'phone':'9876540002', 'courses':2},
            {'id':'DG25001', 'name':'Dr. Ramya Suresh', 'dept':'AIML', 'desig':'Professor', 'email':'ramya@college.edu', 'phone':'9876540003', 'courses':3}
        ]
        supabase.table('faculty').insert(faculties).execute()
        
        courses = [
            {'code':'CS601', 'name':'Machine Learning', 'credits':4, 'dept':'CSE', 'sem':6, 'faculty':'DG11001', 'students':42, 'progress':70, 'grade':'A', 'schedule':'Mon/Wed 10:30', 'room':'Room 204'},
            {'code':'CS602', 'name':'Cloud Computing', 'credits':3, 'dept':'CSE', 'sem':6, 'faculty':'DG11001', 'students':38, 'progress':55, 'grade':'B+', 'schedule':'Tue/Thu 9:00', 'room':'Lab 3'},
            {'code':'AI601', 'name':'Deep Learning', 'credits':4, 'dept':'AIML', 'sem':6, 'faculty':'DG25001', 'students':35, 'progress':80, 'grade':'A+', 'schedule':'Mon/Fri 11:00', 'room':'Lab 1'},
            {'code':'DS601', 'name':'Data Analytics', 'credits':3, 'dept':'AIDS', 'sem':6, 'faculty':'DG24001', 'students':40, 'progress':65, 'grade':'A', 'schedule':'Wed/Fri 2:00', 'room':'Room 102'},
            {'code':'CS603', 'name':'Blockchain Tech', 'credits':2, 'dept':'CSE', 'sem':6, 'faculty':'DG11001', 'students':30, 'progress':45, 'grade':'B', 'schedule':'Fri 1:00', 'room':'Room 101'}
        ]
        supabase.table('courses').insert(courses).execute()
        
        notifs = [
            {'title':'Assignment Due Soon', 'msg':'ML Assignment 3 due on March 20 — submit via portal', 'date':'Mar 13', 'priority':'warning', 'read':0},
            {'title':'Internal Assessment 2', 'msg':'IA2 starts April 1. Syllabus coverage: Units 3-5', 'date':'Mar 12', 'priority':'danger', 'read':0},
            {'title':'Fee Payment Reminder', 'msg':'Last date for semester fee payment is March 31', 'date':'Mar 11', 'priority':'info', 'read':1}
        ]
        supabase.table('notifications').insert(notifs).execute()
        
        discs = [
            {'student':'202611002', 'name':'Priya Nair', 'severity':'Minor', 'reason':'Late submission of assignment', 'date':'2026-02-15', 'faculty':'DG11001', 'notes':'First occurrence. Warning issued.'},
            {'student':'202625001', 'name':'Sneha Iyer', 'severity':'Serious', 'reason':'Plagiarism detected in project', 'date':'2026-02-20', 'faculty':'DG25001', 'notes':'Academic integrity violation. Re-submission required.'},
            {'student':'202611003', 'name':'Karthik Rajan', 'severity':'Minor', 'reason':'Dress code violation', 'date':'2026-03-01', 'faculty':'DG11001', 'notes':'Verbal warning given.'}
        ]
        supabase.table('disciplinary').insert(discs).execute()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
