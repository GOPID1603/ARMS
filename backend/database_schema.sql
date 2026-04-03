CREATE TABLE IF NOT EXISTS students (
    reg TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    dept TEXT NOT NULL,
    spec TEXT,
    batch TEXT,
    email TEXT,
    phone TEXT,
    cgpa REAL,
    sem INTEGER,
    credits INTEGER,
    pass INTEGER,
    disc INTEGER,
    att REAL
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
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    msg TEXT NOT NULL,
    date TEXT,
    priority TEXT,
    read INTEGER
);

CREATE TABLE IF NOT EXISTS disciplinary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student TEXT NOT NULL,
    name TEXT NOT NULL,
    severity TEXT,
    reason TEXT,
    date TEXT,
    faculty TEXT,
    notes TEXT,
    FOREIGN KEY(student) REFERENCES students(reg)
);

CREATE TABLE IF NOT EXISTS attendance_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    course TEXT,
    status TEXT,
    student_reg TEXT,
    FOREIGN KEY(course) REFERENCES courses(code),
    FOREIGN KEY(student_reg) REFERENCES students(reg)
);

CREATE TABLE IF NOT EXISTS od_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    course TEXT,
    reason TEXT,
    student_reg TEXT,
    faculty_status TEXT DEFAULT 'Pending',
    admin_status TEXT DEFAULT 'Pending'
);

CREATE TABLE IF NOT EXISTS student_courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_reg TEXT,
    course_code TEXT,
    FOREIGN KEY(student_reg) REFERENCES students(reg),
    FOREIGN KEY(course_code) REFERENCES courses(code)
);
