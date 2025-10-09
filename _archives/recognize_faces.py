# recognize_faces.py
import face_recognition
import cv2
import numpy as np
import os
import time

# --- Settings ---
KNOWN_FACES_DIR = 'known_faces'
TOLERANCE = 0.6  # How strict the matching is. Lower is stricter.
FRAME_THICKNESS = 3
FONT_THICKNESS = 2
MODEL = 'hog'  # 'hog' is faster on CPU, 'cnn' is more accurate but slower

# --- Initialization ---
print('Loading known faces...')

known_faces_encodings = []
known_faces_names = []

# Loop through each person in the known_faces directory
for name in os.listdir(KNOWN_FACES_DIR):
    person_dir = os.path.join(KNOWN_FACES_DIR, name)
    if os.path.isdir(person_dir):
        for filename in os.listdir(person_dir):
            filepath = os.path.join(person_dir, filename)
            
            # Load an image
            image = face_recognition.load_image_file(filepath)
            
            # Get the face encoding (the 128-dimensional representation of the face)
            # We assume there is only one face in each known image
            encodings = face_recognition.face_encodings(image)
            
            if len(encodings) > 0:
                encoding = encodings[0]
                known_faces_encodings.append(encoding)
                known_faces_names.append(name)
            else:
                print(f"Warning: No face found in {filepath}. Skipping.")

print(f"Loaded {len(known_faces_names)} known face(s).")

# Get a reference to the webcam
video_capture = cv2.VideoCapture(0)

print("Starting video stream...")
time.sleep(2.0) # Give camera time to warm up

# --- Main Loop ---
while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()
    if not ret:
        print("Error: Failed to capture frame.")
        break

    # Resize frame for faster processing (optional)
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Find all the faces and face encodings in the current frame of video
    face_locations = face_recognition.face_locations(rgb_small_frame, model=MODEL)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    # Loop through each face found in the frame
    for face_location, face_encoding in zip(face_locations, face_encodings):
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(known_faces_encodings, face_encoding, tolerance=TOLERANCE)
        name = "Unknown"

        # Use the known face with the smallest distance to the new face
        face_distances = face_recognition.face_distance(known_faces_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        
        if matches[best_match_index]:
            name = known_faces_names[best_match_index]

        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top, right, bottom, left = face_location
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), FRAME_THICKNESS)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
        cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), FONT_THICKNESS)

    # Display the resulting image
    cv2.imshow('Face Recognition', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- Cleanup ---
print("Cleaning up...")
video_capture.release()
cv2.destroyAllWindows()
