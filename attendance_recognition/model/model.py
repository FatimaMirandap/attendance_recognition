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
from google.cloud import storage  # Importa el cliente de Google Cloud Storage

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
        """Descarga un archivo de S3 y devuelve su contenido."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            s3.download_fileobj(self.bucket_name, s3_key, tmp_file)
            return tmp_file.name

class GCPHandler:
    def __init__(self, bucket_name):
        self.client = storage.Client()
        self.bucket = self.client.get_bucket(bucket_name)

    def upload_model(self, local_path, destination_blob_name):
        """Sube un archivo local a GCP."""
        blob = self.bucket.blob(destination_blob_name)
        blob.upload_from_filename(local_path)
        print(f"Modelo subido a GCP en gs://{self.bucket.name}/{destination_blob_name}")

class FacialRecognitionSystem:
    def __init__(self, model_path=None, s3_handler=None, gcp_handler=None):
        self.known_face_encodings = []
        self.known_face_names = []
        self.model_path = model_path
        self.s3_handler = s3_handler
        self.gcp_handler = gcp_handler

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

    def save_model_to_gcp(self, gcp_model_path):
        """Guarda el modelo en un bucket de GCP."""
        data = {
            "encodings": self.known_face_encodings,
            "names": self.known_face_names
        }

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            pickle.dump(data, temp_file)
            temp_file_path = temp_file.name

        # Subir a GCP
        self.gcp_handler.upload_model(temp_file_path, gcp_model_path)
        os.remove(temp_file_path)

    def load_model(self, s3_model_path):
        """Carga las codificaciones y nombres desde un archivo en S3."""
        model_file_path = self.s3_handler.download_file(s3_model_path)
        with open(model_file_path, 'rb') as f:
            data = pickle.load(f)

        self.known_face_encodings = data["encodings"]
        self.known_face_names = data["names"]
        os.remove(model_file_path)

    def predict(self, image_path, tolerance=0.6):
        """Realiza una predicción en una imagen."""
        try:
            face_encoding = self.process_image(image_path)
            if face_encoding is None:
                return {'error': 'No se encontró cara en la imagen'}

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

# Ejemplo de uso en SageMaker
def main():
    BUCKET_NAME = "images-by-users"  # Solo el nombre del bucket
    S3_FOLDER_PREFIX = "face_recognition_images/"
    S3_MODEL_PATH = "model.pkl"
    GCP_BUCKET_NAME = "facerec-1"
    GCP_MODEL_PATH = "modelos/facial_recognition_model.pkl"

    s3_handler = S3Handler(BUCKET_NAME)
    gcp_handler = GCPHandler(GCP_BUCKET_NAME)
    system = FacialRecognitionSystem(s3_handler=s3_handler, gcp_handler=gcp_handler)

    print("Descargando y preparando datos desde S3...")
    num_faces = system.prepare_data_from_s3(S3_FOLDER_PREFIX)

    print(f"Total de caras procesadas: {num_faces}")

    system.save_model_to_gcp(GCP_MODEL_PATH)
    print(f"Modelo guardado en GCP en: gs://{GCP_BUCKET_NAME}/{GCP_MODEL_PATH}")

if __name__ == "__main__":
    main()