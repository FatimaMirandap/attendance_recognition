import os
import cv2
import numpy as np
import face_recognition
import pickle
from datetime import datetime
import mlflow
import mlflow.sklearn
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from flask import Flask, request, jsonify
import boto3
import tempfile

# Inicializar cliente de S3
s3 = boto3.client('s3')

class S3Handler:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    def list_folder_contents(self, folder_prefix):
        """Lista los objetos en una carpeta de un bucket de S3."""
        response = s3.list_objects_v2(Bucket=self.bucket_name, Prefix=folder_prefix)
        return response.get('Contents', [])

    def download_file(self, s3_key):
        """Descarga un archivo de S3 y devuelve su ruta local temporal."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            s3.download_fileobj(self.bucket_name, s3_key, tmp_file)
            return tmp_file.name

    def upload_file(self, local_path, s3_key):
        """Sube un archivo local a S3."""
        s3.upload_file(local_path, self.bucket_name, s3_key)

class FacialRecognitionSystem:
    def __init__(self, model_path=None, s3_handler=None):
        self.known_face_encodings = []
        self.known_face_names = []
        self.model_path = model_path
        self.s3_handler = s3_handler

        # Configura MLflow para usar un URI de S3 para el tracking
        mlflow.set_tracking_uri("sqlite:///mlflow.db")
        mlflow.set_experiment("facial_recognition")

    def process_image(self, image_path):
        """Procesa una imagen y retorna sus codificaciones faciales."""
        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image, model="hog")
        if not face_locations:
            return None
        face_encodings = face_recognition.face_encodings(image, face_locations)
        return face_encodings[0] if face_encodings else None

    def prepare_data_from_s3(self, folder_prefix):
        """Prepara los datos de entrenamiento desde S3."""
        print("Iniciando preparación de datos desde S3...")

        for obj in self.s3_handler.list_folder_contents(folder_prefix):
            file_key = obj['Key']
            person_name = os.path.basename(os.path.dirname(file_key))

            # Descarga la imagen desde S3
            temp_image_path = self.s3_handler.download_file(file_key)
            try:
                face_encoding = self.process_image(temp_image_path)
                if face_encoding is not None:
                    self.known_face_encodings.append(face_encoding)
                    self.known_face_names.append(person_name)
                    print(f"✓ Procesada imagen para {person_name}")
                else:
                    print(f"✗ No se encontró cara en: {file_key}")
            except Exception as e:
                print(f"Error procesando {file_key}: {str(e)}")
            finally:
                os.remove(temp_image_path)

        print(f"Procesamiento completado. Total de caras encontradas: {len(self.known_face_encodings)}")
        return len(self.known_face_encodings)

    def save_model_to_s3(self, s3_model_path):
        """Guarda el modelo en un bucket de S3."""
        data = {
            "encodings": self.known_face_encodings,
            "names": self.known_face_names
        }

        # Crear archivo temporal para guardar el modelo
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            pickle.dump(data, temp_file)
            temp_file_path = temp_file.name

        # Subir el archivo a S3
        self.s3_handler.upload_file(temp_file_path, s3_model_path)
        os.remove(temp_file_path)

    def load_model(self, s3_model_path):
        """Carga las codificaciones y nombres desde un bucket en S3."""
        # Descargar archivo desde S3 a una ruta temporal
        local_model_path = self.s3_handler.download_file(s3_model_path)

        # Cargar el modelo desde el archivo temporal
        with open(local_model_path, 'rb') as f:
            data = pickle.load(f)

        # Asignar los datos cargados a las variables correspondientes
        self.known_face_encodings = data["encodings"]
        self.known_face_names = data["names"]

        # Eliminar archivo temporal después de cargar el modelo
        os.remove(local_model_path)

    def predict(self, image_path, tolerance=0.6):
        """Realiza una predicción en una imagen."""
        try:
            face_encoding = self.process_image(image_path)
            if face_encoding is None:
                return {'error': 'No se encontró cara en la imagen'}

            # Comparar la codificación de la cara con las conocidas
            matches = face_recognition.compare_faces(
                self.known_face_encodings,
                face_encoding,
                tolerance=tolerance
            )
            face_distances = face_recognition.face_distance(
                self.known_face_encodings,
                face_encoding
            )

            if True in matches:
                best_match_index = np.argmin(face_distances)
                confidence = 1 - face_distances[best_match_index]
                return {
                    'person': self.known_face_names[best_match_index],
                    'confidence': float(confidence)
                }
            else:
                return {'person': 'Desconocido', 'confidence': 0.0}

        except Exception as e:
            return {'error': str(e)}

# Ejemplo de uso
def main():
    BUCKET_NAME = "images-by-users"  # Solo el nombre del bucket
    S3_FOLDER_PREFIX = "face_recognition_images_fulllname/"
    S3_MODEL_PATH = "model.pkl"

    s3_handler = S3Handler(BUCKET_NAME)
    system = FacialRecognitionSystem(s3_handler=s3_handler)

    print("Descargando y preparando datos desde S3...")
    num_faces = system.prepare_data_from_s3(S3_FOLDER_PREFIX)

    print(f"Total de caras procesadas: {num_faces}")

    system.save_model_to_s3(S3_MODEL_PATH)
    print(f"Modelo guardado en S3 en: s3://{BUCKET_NAME}/{S3_MODEL_PATH}")

if __name__ == "__main__":
    main()
