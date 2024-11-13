# database.py
from utils import *

# Configuración de la URL de conexión
DATABASE_URL = "mysql+pymysql://admin:didiercosas5@student-attendance-db.cjs6q2qyupii.us-east-2.rds.amazonaws.com/studentattendancedb"

# Crear el motor de conexión
engine = create_engine(DATABASE_URL)

# Crear la clase de sesión
Session = sessionmaker(bind=engine)


def get_session():
    return Session()

def get_user_info(name, email):
    """Consulta a la base de datos para obtener el ID y el rol del usuario por nombre y correo."""
    with Session() as session:
        result = session.execute(
            text("SELECT id, rol FROM Usuarios WHERE nombre = :name AND correo = :email"),
            {'name': name, 'email': email}
        ).fetchone()
    return result

def check_user_exists(name, email):
    """Verifica si un usuario ya existe en la base de datos."""
    with Session() as session:
        return session.execute(
            text("SELECT id FROM Usuarios WHERE nombre = :name AND correo = :email"),
            {'name': name, 'email': email}
        ).fetchone()

def insert_user(name, email):
    """Inserta un nuevo usuario en la base de datos."""
    with Session() as session:
        result = session.execute(
            text("INSERT INTO Usuarios (nombre, correo, rol) VALUES (:name, :email, 'Estudiante')"),
            {'name': name, 'email': email}
        )
        session.commit()
        return result.lastrowid  # Devuelve el ID del usuario recién insertado

def check_group_exists(group_name):
    """Verifica si un grupo existe en la base de datos."""
    with Session() as session:
        return session.execute(
            text("SELECT id FROM Grupos WHERE nombre = :group_name"),
            {'group_name': group_name}
        ).fetchone()

def insert_group(group_name):
    """Inserta un nuevo grupo en la base de datos si no existe."""
    with Session() as session:
        session.execute(
            text("INSERT INTO Grupos (nombre) VALUES (:group_name)"),
            {'group_name': group_name}
        )
        session.commit()
        return session.execute(text("SELECT LAST_INSERT_ID()")).fetchone()[0]

def insert_student(user_id, matricula, group_name):
    """Inserta los datos del estudiante en la base de datos."""
    with Session() as session:
        session.execute(
            text("INSERT INTO Estudiantes (id_usuario, matricula, grupo_id) VALUES (:user_id, :matricula, :group_name)"),
            {'user_id': user_id, 'matricula': matricula, 'group_name': group_name}
        )
        session.commit()

def save_photos(student_id, img_data1, img_data2, img_data3):
    """Guarda las fotografías del estudiante en la base de datos."""
    with Session() as session:
        session.execute(
            text("INSERT INTO Fotografias (estudiante_id, imagen1, imagen2, imagen3) VALUES (:student_id, :img1, :img2, :img3)"),
            {'student_id': student_id, 'img1': img_data1, 'img2': img_data2, 'img3': img_data3}
        )
        session.commit()

def get_day_of_week(date):
    """Obtiene el día de la semana a partir de la fecha."""
    with Session() as session:
        return session.execute(
            text("SELECT dia FROM FechaDias WHERE fecha = :date"),
            {'date': date}
        ).fetchone()

def get_user_id_by_name(name):
    """Obtiene el ID del usuario basado en su nombre."""
    with Session() as session:
        return session.execute(
            text("SELECT id FROM Usuarios WHERE nombre = :name"),
            {'name': name}
        ).fetchone()

def get_student_group(user_id):
    """Obtiene el grupo de un estudiante por su ID de usuario."""
    with Session() as session:
        return session.execute(
            text("SELECT grupo_id FROM Estudiantes WHERE id_usuario = :user_id"),
            {'user_id': user_id}
        ).fetchone()

def get_group_id_by_name(group_name):
    """Obtiene el ID del grupo basado en el nombre del grupo."""
    with Session() as session:
        return session.execute(
            text("SELECT id FROM Grupos WHERE nombre = :grupo_nombre"),
            {'grupo_nombre': group_name}
        ).fetchone()

def get_schedule_for_day(group_id, day_of_week):
    """Obtiene los horarios de clase para un grupo en un día específico."""
    with Session() as session:
        return session.execute(
            text("""
                SELECT Horarios.materia_id, Materias.nombre AS materia_nombre, Horarios.hora_inicio, Horarios.hora_fin
                FROM Horarios 
                JOIN Materias ON Horarios.materia_id = Materias.id
                WHERE Horarios.grupo_id = :grupo_id AND Horarios.dia = :day
            """),
            {'grupo_id': group_id, 'day': day_of_week}
        ).fetchall()

def check_attendance_exists(student_id, materia_id, date):
    """Verifica si ya existe un registro de asistencia para un estudiante en una materia en una fecha específica."""
    with Session() as session:
        return session.execute(
            text("""
                SELECT id FROM Asistencias
                WHERE estudiante_id = :estudiante_id AND materia_id = :materia_id AND fecha = :fecha
            """),
            {'estudiante_id': student_id, 'materia_id': materia_id, 'fecha': date}
        ).fetchone()

def register_attendance(student_id, materia_id, date, time):
    """Registra la asistencia de un estudiante en una materia."""
    with Session() as session:
        session.execute(
            text("""
                INSERT INTO Asistencias (estudiante_id, materia_id, fecha, hora_registro, estado)
                VALUES (:estudiante_id, :materia_id, :fecha, :hora_registro, 'Presente')
            """),
            {'estudiante_id': student_id, 'materia_id': materia_id, 'fecha': date, 'hora_registro': time}
        )
        session.commit()

def get_classes_by_professor(professor_id):
    """Obtiene las clases y grupos que un profesor enseña."""
    with Session() as session:
        return session.execute(
            text("""
                SELECT Horarios.materia_id, Materias.nombre AS materia_nombre, Horarios.grupo_id, Grupos.nombre AS grupo_nombre
                FROM Horarios
                JOIN Materias ON Horarios.materia_id = Materias.id
                JOIN Grupos ON Horarios.grupo_id = Grupos.id
                WHERE Horarios.profesor_id = :profesor_id
            """),
            {'profesor_id': professor_id}
        ).fetchall()

def get_attendance_by_date_range(professor_id, materia_id, start_date, end_date):
    """Obtiene la lista de asistencias de un profesor para una materia y un rango de fechas."""
    with Session() as session:
        query = text("""
            SELECT Asistencias.id, Usuarios.nombre AS estudiante_nombre, Asistencias.fecha, Asistencias.hora_registro, Asistencias.estado
            FROM Asistencias
            JOIN Estudiantes ON Asistencias.estudiante_id = Estudiantes.id_usuario
            JOIN Usuarios ON Estudiantes.id_usuario = Usuarios.id
            WHERE Asistencias.fecha BETWEEN :start_date AND :end_date
              AND Asistencias.materia_id = :materia_id
        """)
        return session.execute(query, {
            'start_date': start_date,
            'end_date': end_date,
            'materia_id': materia_id
        }).fetchall()

def get_attendance_by_date(professor_id, materia_id, date):
    """Obtiene la lista de asistencias de un profesor para una materia en un día específico."""
    with Session() as session:
        query = text("""
            SELECT Asistencias.id, Usuarios.nombre AS estudiante_nombre, Asistencias.fecha, Asistencias.hora_registro, Asistencias.estado
            FROM Asistencias
            JOIN Estudiantes ON Asistencias.estudiante_id = Estudiantes.id_usuario
            JOIN Usuarios ON Estudiantes.id_usuario = Usuarios.id
            WHERE Asistencias.fecha = :date
              AND Asistencias.materia_id = :materia_id
        """)
        return session.execute(query, {
            'date': date,
            'materia_id': materia_id
        }).fetchall()