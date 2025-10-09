# encode_faces.py
import face_recognition
import os
import pickle

print("Starting encoding process...")

KNOWN_FACES_DIR = 'known_faces'
OUTPUT_ENCODING_FILE = 'known_face_data.pkl'

known_faces_encodings = []
known_faces_names = []

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
                # Assuming one face per image
                known_faces_encodings.append(encodings[0])
                known_faces_names.append(name)
                print(f"Encoded {filename} for {name}")
            else:
                print(f"Warning: No face found in {filepath}. Skipping.")
        except Exception as e:
            print(f"Error processing {filepath}: {e}")

# Save the encodings and names to a file
with open(OUTPUT_ENCODING_FILE, 'wb') as f:
    pickle.dump({'encodings': known_faces_encodings, 'names': known_faces_names}, f)

print(f"Encoding complete. Data saved to {OUTPUT_ENCODING_FILE}")