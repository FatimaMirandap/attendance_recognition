# Face-Attendance-Recognition-System

Facial recognition based attendance web application, designed for universities and to be used by students and teachers. Students can register their attendance by taking a photo through their device's camera, which will be validated by a machine learning model in real time; they can also register in the system to be added to the database. Teachers can access attendance reports. The system is developed to integrate with a real-time database, ensuring accurate and efficient attendance management.


## Main Functionalities:
- User Registration: Authentication system that allows differentiated access for students and teachers.
- Attendance Capture:
  - Students can activate the camera, capture their photo, and the system validates their identity with the facial recognition model.
  - If the system correctly identifies the student, it automatically registers their attendance.
- For Teachers:
  - Teachers can access by selecting their group and subject in order to obtain an attendance report for a selected period of time.

## Technologies Used:
- Frontend: 
- Backend: 
- Facial Recognition: Amazon Rekognition for facial detection and authentication with a machine learning model
- Database: Amazon RDS (linked to MySQL) for attendance, user and configuration data management.
