#face_recognition_utils.py
from utils import *

# Cargar las codificaciones y nombres desde el archivo .pkl
with open('face_recognition_encodings.pkl', 'rb') as file:
    data = pickle.load(file)
encodings = data['encodings']
names = data['names']

def recognize_identity(image):
    image_array = np.array(image)
    face_locations = face_recognition.face_locations(image_array)
    face_encodings = face_recognition.face_encodings(image_array, face_locations)
    best_match = {"name": "Desconocido", "confidence": 0}

    for face_encoding in face_encodings:
        face_distances = face_recognition.face_distance(encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        confidence = max(0, int((1 - face_distances[best_match_index]) * 100))

        if face_distances[best_match_index] < 0.6:
            best_match = {"name": names[best_match_index], "confidence": confidence}

    return best_match["name"], best_match["confidence"]