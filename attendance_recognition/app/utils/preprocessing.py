#preprocessing.py
from utils import *
from database import (save_photos)

def capture_or_upload_photos(student_id):
    st.write("Sube tres fotografías para el registro.")

    # Opciones para cargar o tomar fotos
    image1 = st.file_uploader("Sube la primera imagen", type=["jpg", "jpeg", "png"], key="photo1")
    image2 = st.file_uploader("Sube la segunda imagen", type=["jpg", "jpeg", "png"], key="photo2")
    image3 = st.file_uploader("Sube la tercera imagen", type=["jpg", "jpeg", "png"], key="photo3")

    # Convertir imágenes a base64 si están disponibles
    if image1 and image2 and image3:
        img_data1 = convert_to_base64(image1)
        img_data2 = convert_to_base64(image2)
        img_data3 = convert_to_base64(image3)

        # Guardar en la base de datos
        save_photos(student_id, img_data1, img_data2, img_data3)
        st.success("Fotografías guardadas exitosamente.")

def convert_to_base64(image_file):
    # Leer y convertir la imagen a base64
    image = Image.open(image_file)
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return img_str