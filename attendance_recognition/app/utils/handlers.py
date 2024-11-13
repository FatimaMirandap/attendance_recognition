#handlers.py

from utils import *
from database import (get_session, get_user_info, check_user_exists, insert_user, check_group_exists,
                      insert_group, insert_student,get_day_of_week, get_user_id_by_name, 
                      get_student_group, get_group_id_by_name, get_schedule_for_day,
                      check_attendance_exists, register_attendance,get_classes_by_professor, 
                      get_attendance_by_date_range, get_attendance_by_date)

from face_recognition_utils import recognize_identity
from preprocessing import capture_or_upload_photos


def validate_user(name, email, role):
    user_info = get_user_info(name, email)

    if user_info:
        st.session_state['validated'] = True
        st.session_state['role'] = user_info.rol
        st.session_state['user_id'] = user_info.id
        st.success(f"Usuario validado como {user_info.rol.lower()}.")
    else:
        st.session_state['validated'] = False
        st.error("Usuario no encontrado o no es estudiante.")

#def handle_newuser():

def register_new_user(name, email, group_name): 
    # Verificar si el usuario ya existe
    existing_user = check_user_exists(name, email)
    if existing_user:
        st.warning("El usuario ya existe en el sistema.")
        return

    # Extraer matrícula del correo institucional
    matricula_match = re.match(r"(\d+)@upy\.edu\.mx", email)
    if not matricula_match:
        st.error("El correo institucional no es válido. Asegúrate de que esté en el formato correcto.")
        return
    matricula = matricula_match.group(1)

    # Insertar datos del nuevo usuario
    user_id = insert_user(name, email)
    st.write(f"Nuevo usuario registrado con ID: {user_id}, Nombre: {name}, Correo: {email}, Rol: Estudiante")

    # Verificar si el grupo existe en la tabla Grupos, y si no, crearlo
    group_info = check_group_exists(group_name)
    if not group_info:
        # Insertar el nuevo grupo en la tabla Grupos si no existe
        group_info = insert_group(group_name)
        st.write(f"Nuevo grupo registrado con ID: {group_info}, Nombre: {group_name}")
    
    # Insertar los datos del estudiante en la tabla Estudiantes
    insert_student(user_id, matricula, group_name)

    st.success("Usuario y estudiante registrado exitosamente.")

    # Captura o carga de tres imágenes
    capture_or_upload_photos(user_id)


#def handle_student():

def handle_student():
    image_predict = st.camera_input("Toma tu fotografía de asistencia", key='student_camera')
    if image_predict is not None:
        img = Image.open(io.BytesIO(image_predict.getvalue()))
        img = img.convert("RGB")
        identity, confidence = recognize_identity(img)
        
        if identity == "Desconocido":
            st.error("No se detectó ningún rostro o no hubo coincidencia.")
            return
        else:
            st.success(f"Identidad reconocida: {identity} (Confianza: {confidence}%)")
            st.image(img, caption=f"{identity} - Confianza: {confidence}%", use_column_width=True)

            # Obtener la fecha y hora actual en la zona horaria de México
            now = datetime.now(pytz.timezone('America/Mexico_City'))
            current_time = now.time()
            current_date = now.date()

            st.write(f"Hora actual para el registro: {current_time}")

            # Paso 0: Obtener el día de la semana
            day_of_week = get_day_of_week(now.strftime('%Y-%m-%d'))
            if day_of_week:
                st.write(f"Día de la semana: {day_of_week.dia if day_of_week else 'No encontrado'}")

                # Paso 1: Obtener el ID del usuario
                user_info = get_user_id_by_name(identity)
                if user_info:
                    st.write(f"Numero de lista: {user_info.id}")

                    # Paso 2: Obtener el grupo del estudiante
                    student_group_name = get_student_group(user_info.id)
                    if student_group_name:
                        st.write(f"Grupo: {student_group_name.grupo_id}")

                        # Paso 2.5: Obtener el ID real del grupo
                        group_id = get_group_id_by_name(student_group_name.grupo_id)
                        if group_id:
                            # Paso 3: Obtener el horario del grupo
                            schedule_info = get_schedule_for_day(group_id.id, day_of_week.dia)
                            if schedule_info:
                                st.write("Clases del día:")
                                for schedule in schedule_info:
                                    st.write(f"Materia: {schedule.materia_nombre}, Desde: {schedule.hora_inicio}, Hasta: {schedule.hora_fin}")

                                # Paso 4: Determinar a qué materia asistió según la hora actual
                                current_class = next(
                                    (s for s in schedule_info
                                    if time.fromisoformat(str(s.hora_inicio)) <= current_time <= time.fromisoformat(str(s.hora_fin))),
                                    None
                                )

                                if current_class:
                                    # Verificar si ya existe un registro de asistencia
                                    existing_attendance = check_attendance_exists(user_info.id, current_class.materia_id, current_date)
                                    if existing_attendance:
                                        st.info(f"El estudiante ya tiene una asistencia registrada para la materia: {current_class.materia_nombre}")
                                    else:
                                        # Registrar la asistencia
                                        register_attendance(user_info.id, current_class.materia_id, current_date, current_time)
                                        st.success(f"Asistencia registrada exitosamente para la materia: {current_class.materia_nombre}")
                                else:
                                    st.error("No hay clases en este momento para el estudiante según el horario actual.")
                            else:
                                st.error("No se encontraron materias para hoy.")


#def handle_professor():
def handle_professor():
    st.header("Bienvenido, Profesor")
    session = get_session()

    # Obtener el id del profesor desde la sesión
    profesor_id = st.session_state['user_id']

    # Paso 1: Buscar las materias y grupos que enseña el profesor
    clases = get_classes_by_professor(profesor_id)

    if not clases:
        st.warning("No se encontraron clases asignadas a este profesor.")
        return

    # Mostrar las clases disponibles para selección
    clase_options = {f"{clase.materia_nombre} - {clase.grupo_nombre}": (clase.materia_id, clase.grupo_id) for clase in clases}
    selected_clase = st.selectbox("Selecciona la clase para ver la asistencia", list(clase_options.keys()))

    # Elegir un día específico o un rango de fechas
    date_selection_type = st.radio("Selecciona el tipo de fecha", ["Día específico", "Rango de fechas"])

    if date_selection_type == "Día específico":
        selected_date = st.date_input("Selecciona la fecha")
        if st.button("Generar lista de asistencia"):
            mostrar_asistencia_por_fecha(profesor_id, clase_options[selected_clase], selected_date, selected_date)
    else:
        start_date = st.date_input("Fecha de inicio")
        end_date = st.date_input("Fecha de fin")
        if st.button("Generar métricas de asistencia"):
            mostrar_asistencia_por_fecha(profesor_id, clase_options[selected_clase], start_date, end_date)

def mostrar_asistencia_por_fecha(profesor_id, clase_info, start_date, end_date):
    materia_id = clase_info[0]

    # Imprimir los valores de entrada para la consulta
    st.write(f"Valores para la consulta: Materia ID: {materia_id}, Fecha inicio: {start_date}, Fecha fin: {end_date}")

    # Consultar asistencias según el rango de fechas
    resultados = get_attendance_by_date_range(profesor_id, materia_id, start_date, end_date)

    # Procesar resultados finales
    if resultados:
        # Convertir a DataFrame para visualizar y descargar
        df_asistencias = pd.DataFrame(
            resultados, 
            columns=["ID", "Nombre del Estudiante", "Fecha", "Hora de Registro", "Estado"]
        )
        
        st.write("Lista de Asistencia")
        st.dataframe(df_asistencias)

        # Agregar opción para descargar como CSV
        csv = df_asistencias.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar lista de asistencia en CSV",
            data=csv,
            file_name=f"asistencia_materia_{materia_id}.csv",
            mime="text/csv"
        )

        # Generar métricas de asistencia
        asistencia_total = df_asistencias.shape[0]
        presentes = df_asistencias[df_asistencias["Estado"] == "Validado"].shape[0]
        porcentaje_asistencia = (presentes / asistencia_total) * 100 if asistencia_total > 0 else 0
        st.write(f"Total de registros: {asistencia_total}")
        st.write(f"Presentes: {presentes}")
        st.write(f"Porcentaje de asistencia: {porcentaje_asistencia:.2f}%")
    else:
        st.warning("No se encontraron registros de asistencia para la fecha o rango seleccionado.")