
import streamlit as st
from app.utils.styles import apply_styles  # Estilos CSS
from app.utils.handlers import validate_user, register_new_user, handle_student, handle_professor  # Importa las funciones desde handlers

def main():

    apply_styles()

    st.title("Bienvenido al sistema de Registro de Asistencias")
    # Mostrar el logo de la universidad
    logo_path = "C:\\Users\\Fatim\\Downloads\\HW9\\TRENDS\\APP FACE RECOGNITION\\App\\upy.png"  # Reemplaza con la ruta al archivo de logo
    st.image(logo_path, caption="Universidad Politécnica de Yucatán", use_column_width=True)

    role = st.selectbox("Selecciona tu perfil", ["Soy profesor", "Soy estudiante", "Soy estudiante sin registro"], key='role_select')

    if role:
        name = st.text_input("Ingresa tu nombre completo:", key='name_input')
        email = st.text_input("Ingresa tu correo electrónico:", key='email_input')

        if role == "Soy estudiante sin registro":
            # Campos adicionales para el registro de nuevo usuario
            group_name = st.text_input("Ingresa tu grupo:", key='group_input')

            if st.button("Registrar"):
                register_new_user(name, email, group_name)
        else:
            if st.button("Aceptar"):
                validate_user(name, email, role)

            # Asegurarnos de que se muestra la sección de profesor o estudiante según el rol validado
            if 'validated' in st.session_state and st.session_state['validated']:
                if st.session_state['role'] == "Estudiante":
                    handle_student()
                elif st.session_state['role'] == "Profesor":
                    st.write("Redirigiendo a la sección de profesor...")  # Mensaje de depuración
                    handle_professor()  # Aquí se llama a handle_professor si el rol es profesor
                else:
                    st.error("Rol no reconocido.")

if __name__ == "__main__":
    main()