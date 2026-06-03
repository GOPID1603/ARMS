-- Run this script in your Supabase SQL Editor to create all necessary tables

CREATE TABLE IF NOT EXISTS students (
    reg TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    dept TEXT NOT NULL,
    spec TEXT,
    batch TEXT,
    email TEXT,
    phone TEXT,
    cgpa NUMERIC,
    sem INTEGER,
    credits INTEGER,
    pass INTEGER,
    disc INTEGER,
    att NUMERIC
);

CREATE TABLE IF NOT EXISTS faculty (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    dept TEXT NOT NULL,
    desig TEXT,
    email TEXT,
    phone TEXT,
    courses INTEGER
);

CREATE TABLE IF NOT EXISTS courses (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    credits INTEGER,
    dept TEXT,
    sem INTEGER,
    faculty TEXT,
    students INTEGER,
    progress INTEGER,
    grade TEXT,
    schedule TEXT,
    room TEXT
);

CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    msg TEXT NOT NULL,
    date TEXT,
    priority TEXT,
    read INTEGER
);

CREATE TABLE IF NOT EXISTS disciplinary (
    id SERIAL PRIMARY KEY,
    student TEXT NOT NULL,
    name TEXT NOT NULL,
    severity TEXT,
    reason TEXT,
    date TEXT,
    faculty TEXT,
    notes TEXT,
    FOREIGN KEY(student) REFERENCES students(reg) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS attendance_records (
    id SERIAL PRIMARY KEY,
    date TEXT,
    course TEXT,
    status TEXT,
    student_reg TEXT,
    FOREIGN KEY(course) REFERENCES courses(code) ON DELETE CASCADE,
    FOREIGN KEY(student_reg) REFERENCES students(reg) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS od_requests (
    id SERIAL PRIMARY KEY,
    date TEXT,
    course TEXT,
    reason TEXT,
    student_reg TEXT,
    faculty_status TEXT DEFAULT 'Pending',
    admin_status TEXT DEFAULT 'Pending'
);

CREATE TABLE IF NOT EXISTS student_courses (
    id SERIAL PRIMARY KEY,
    student_reg TEXT,
    course_code TEXT,
    FOREIGN KEY(student_reg) REFERENCES students(reg) ON DELETE CASCADE,
    FOREIGN KEY(course_code) REFERENCES courses(code) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS chatbot_logs (
    id SERIAL PRIMARY KEY,
    user_id TEXT,
    role TEXT,
    name TEXT,
    message TEXT,
    response TEXT,
    timestamp TEXT,
    is_unnecessary INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS blocked_users (
    user_id TEXT PRIMARY KEY,
    role TEXT
);
