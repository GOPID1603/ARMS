import cv2
import requests
import time

API_URL = "http://localhost:5000/api/attendance"
CAMERA_ID = 0

print("Initializing Biometric Edge Node...")

def capture_and_recognize():
    cap = cv2.VideoCapture(CAMERA_ID)
    print("Camera active. Monitoring hall for registered faces...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # In a real scenario, face_recognition logic would execute here:
        # face_locations = face_recognition.face_locations(frame)
        # face_encodings = face_recognition.face_encodings(frame, face_locations)
        # for encoding in face_encodings:
        #     matches = face_recognition.compare_faces(known_face_encodings, encoding)
        
        # MOCK EDGE LOGIC FOR DEMONSTRATION
        # Suppose the camera recognized Student ID 202611001
        recognized_student_reg = "202611001"
        course = "CS601"
        
        # We simulate a recognition event every 10 seconds
        print(f"Recognized Student: {recognized_student_reg}. Transmitting to backend...")
        
        try:
            # Note: /api/attendance endpoint needs to be fully implemented in app.py to accept this exact payload
            payload = {"date": time.strftime("%Y-%m-%d"), "course": course, "student_reg": recognized_student_reg, "status": "Present"}
            # res = requests.post(API_URL, json=payload)
            # print("Backend Ack:", res.json())
        except Exception as e:
            print("Failed to reach backend:", str(e))
            
        time.sleep(10)

if __name__ == "__main__":
    # Uncomment to actually run the loop if hardware is connected
    # capture_and_recognize()
    print("Edge Node stub ready.")
