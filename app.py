# app.py (Final Corrected Version)
from flask import Flask, render_template, Response
from flask_socketio import SocketIO
import cv2
import face_recognition
import numpy as np
import pickle
import os
from datetime import datetime
import time
import base64
import csv

# --- App Initialization ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key!'
socketio = SocketIO(app)

# --- Global Variables & Constants ---
KNOWN_FACES_DIR = 'known_faces'
ENCODING_DATA_FILE = 'known_face_data.pkl'
UNIDENTIFIED_DIR = 'unidentified_visitors'
ATTENDANCE_FILE = 'attendance.csv'
TOLERANCE = 0.6

# --- In-memory Data ---
known_faces_encodings = []
known_faces_names = []
today_attendance = set()
last_unknown_saved_time = 0
processing_frame = False  # <<<<<<< 1. INITIAL DECLARATION OF THE VARIABLE

# --- Function to re-encode faces and reload data ---
def reencode_and_reload_data():
    global known_faces_encodings, known_faces_names
    print("Re-encoding and reloading face data...")
    # ... (rest of this function is unchanged)
    temp_encodings = []
    temp_names = []
    for name in os.listdir(KNOWN_FACES_DIR):
        person_dir = os.path.join(KNOWN_FACES_DIR, name)
        if not os.path.isdir(person_dir):
            continue
        for filename in os.listdir(person_dir):
            filepath = os.path.join(person_dir, filename)
            try:
                image = face_recognition.load_image_file(filepath)
                encodings = face_recognition.face_encodings(image)
                if len(encodings) > 0:
                    temp_encodings.append(encodings[0])
                    temp_names.append(name)
            except Exception as e:
                print(f"Error processing {filepath}: {e}")
    with open(ENCODING_DATA_FILE, 'wb') as f:
        pickle.dump({'encodings': temp_encodings, 'names': temp_names}, f)
    known_faces_encodings = temp_encodings
    known_faces_names = temp_names
    print("Reload complete. Known faces:", len(known_faces_names))

# --- Initial Load of Face Data ---
# ... (this section is unchanged)
if os.path.exists(ENCODING_DATA_FILE):
    with open(ENCODING_DATA_FILE, 'rb') as f:
        data = pickle.load(f)
        known_faces_encodings = data['encodings']
        known_faces_names = data['names']
else:
    reencode_and_reload_data()
if os.path.exists(ATTENDANCE_FILE):
    with open(ATTENDANCE_FILE, 'r') as f:
        today_str = datetime.now().strftime('%Y-%m-%d')
        for line in f.readlines():
            if today_str in line:
                today_attendance.add(line.split(',')[0])

# --- Flask Routes ---
@app.route('/')
def index():
    return render_template('index.html')

# NEW: Add a new route for the attendance page
@app.route('/attendance')
def attendance():
    attendance_data = []
    if os.path.exists(ATTENDANCE_FILE):
        with open(ATTENDANCE_FILE, 'r', newline='') as f:
            csv_reader = csv.reader(f)
            # Skip header if you have one, otherwise remove this line
            # next(csv_reader, None) 
            for row in csv_reader:
                if row: # ensure row is not empty
                    attendance_data.append(row)
    # Reverse the list to show the most recent entries first
    return render_template('attendance.html', attendance_data=reversed(attendance_data))

# --- Socket.IO Event Handlers ---
@socketio.on('add_new_person')
def add_new_person(data):
    # ... (this function is unchanged)
    name = data['name']
    img_data_b64 = data['image'].split(',')[1]
    person_dir = os.path.join(KNOWN_FACES_DIR, name)
    os.makedirs(person_dir, exist_ok=True)
    img_data = base64.b64decode(img_data_b64)
    try:
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        face_locations = face_recognition.face_locations(img)
        if len(face_locations) == 0:
            socketio.emit('add_person_response', {'success': False, 'message': 'No face could be detected. Please try again.'})
            return
        if len(face_locations) > 1:
            socketio.emit('add_person_response', {'success': False, 'message': 'Multiple faces detected. Please ensure only one person is in the frame.'})
            return
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(person_dir, f'{timestamp}.jpg')
        with open(filename, 'wb') as f:
            f.write(img_data)
        reencode_and_reload_data()
        socketio.emit('add_person_response', {'success': True, 'message': f'{name} was added successfully!'})
    except Exception as e:
        print(f"Error in add_new_person: {e}")
        socketio.emit('add_person_response', {'success': False, 'message': 'An error occurred on the server.'})

@socketio.on('process_frame')
def handle_process_frame(data):
    global processing_frame  # <<<<<<< 2. TELLING THE FUNCTION TO USE THE GLOBAL VARIABLE
    
    if processing_frame:
        return

    try:
        processing_frame = True
        img_data_b64 = data['image'].split(',')[1]
        img_data = base64.b64decode(img_data_b64)
        np_arr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        results = []
        for face_location, face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_faces_encodings, face_encoding, tolerance=TOLERANCE)
            name = "Unknown"
            face_distances = face_recognition.face_distance(known_faces_encodings, face_encoding)
            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_faces_names[best_match_index]
                    if name not in today_attendance:
                        now = datetime.now()
                        date_str = now.strftime('%Y-%m-%d')
                        time_str = now.strftime('%H:%M:%S')
                        with open(ATTENDANCE_FILE, 'a') as f:
                            f.write(f'{name},{date_str},{time_str}\n')
                        today_attendance.add(name)
                        socketio.emit('update_attendance', {'name': name, 'time': time_str})

            top, right, bottom, left = face_location
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            results.append({'box': (left, top, right, bottom), 'name': name})
        
        socketio.emit('recognition_results', {'results': results})
    finally:
        processing_frame = False

# --- Main Execution ---
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)