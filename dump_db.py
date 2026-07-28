import sqlite3
import json
import os

def dump_db():
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'database.db')
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        students = [dict(row) for row in cursor.execute('SELECT * FROM students').fetchall()]
        faculty = [dict(row) for row in cursor.execute('SELECT * FROM faculty').fetchall()]
        courses = [dict(row) for row in cursor.execute('SELECT * FROM courses').fetchall()]
        notifications = [dict(row) for row in cursor.execute('SELECT * FROM notifications ORDER BY id DESC').fetchall()]
        disciplinary = [dict(row) for row in cursor.execute('SELECT * FROM disciplinary ORDER BY id DESC').fetchall()]
        odRequests = [dict(row) for row in cursor.execute('SELECT * FROM od_requests ORDER BY id DESC').fetchall()]
        attendance_records = [dict(row) for row in cursor.execute('SELECT * FROM attendance_records').fetchall()]
        student_courses = [dict(row) for row in cursor.execute('SELECT * FROM student_courses').fetchall()]
        chatbotLogs = [dict(row) for row in cursor.execute('SELECT * FROM chatbot_logs ORDER BY id ASC').fetchall()]
        blockedUsers = [row['user_id'] for row in cursor.execute('SELECT user_id FROM blocked_users').fetchall()]

        data = {
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
            }
        }

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'dump.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print("Successfully updated dump.json from database.")

    finally:
        conn.close()

if __name__ == '__main__':
    dump_db()
