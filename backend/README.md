# Student 360 Enterprise Backend

This directory contains the Python SQLite backend for the Student 360 portal.

## Setup Instructions

1. Install Python 3.9+ if not installed.
2. Install required dependencies:
   ```bash
   pip install flask flask-cors opencv-python face_recognition
   ```
3. Run the API server:
   ```bash
   python app.py
   ```
   *Note: On the first run, the SQLite database `database.db` will be automatically generated and seeded with around 200 mock students, 3 faculty members, courses, and notifications.*

## API Endpoints

- **`GET /api/data`**: Returns the full JSON aggregate of all tables.
- **`POST /api/students`**: Register a new student.
- **`DELETE /api/students/<reg>`**: Remove a student and their disciplinary records.
- **`POST /api/notifications`**: Broadcast a notification to the portal.
- **`POST /api/disciplinary`**: Log a disciplinary incident.
- **`POST /api/od`**: Apply for On-Duty leave.

## Edge Device Integration
The `face_recognition_edge.py` script demonstrates how a Raspberry Pi or CCTV camera system can hook into this backend API to automate AI-driven biometric roll calls.
