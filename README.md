This repository contains the code for a facial recognition-based attendance system designed to streamline attendance tracking for university students and professors. 

The system was designed for the Universidad Politécnica de Yucatán and uses a cookie-cutter project structure, in this case we only toke a single gropu, but you can  add as many groups you want in the db.

## Contents
- [Face-Attendance-Recognition-System](#Face-Attendance-Recognition-System)
- [Project Structure](#project-structure)
- [Technologies Used](technologies-used)
- [Features](#features)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [Modules](#modules)
  - [Main Functions](#main-functions)
  - [Data Preprocessing](#data-preprocessing)
  - [User Validation and Attendance Recording](#user-validation-and-attendance-recording)
  - [Professor View](#professor-view)
  - [Styles and Customization](#styles-and-customization)
- [API Details](#api-details)
- [Technical Requirements](#technical-requirements)
- [Contributions](#contributions)
- [License](#license)
  
# Face-Attendance-Recognition-System

Facial recognition based attendance web application, designed for universities and to be used by students and teachers. Students can register their attendance by taking a photo through their device's camera, which will be validated by a machine learning model in real time; they can also register in the system to be added to the database. Teachers can access attendance reports. The system is developed to integrate with a real-time database, ensuring accurate and efficient attendance management. The main fucntionalities of our project:
- User Registration: Authentication system that allows differentiated access for students and teachers.
- Attendance Capture:
  - Students can activate the camera, capture their photo, and the system validates their identity with the facial recognition model.
  - If the system correctly identifies the student, it automatically registers their attendance.
- For Teachers:
  - Teachers can access by selecting their group and subject in order to obtain an attendance report for a selected period of time.

## Project Structure

attendance_recognition/  # Main project directory  
├── app/                  # Application directory  
│   ├── main.py           # Main application entry point  
│   ├── utils/            # Utility functions  
│   │   └── __init__.py   # Initializes the utils package  
│   └── app_styles.css    # CSS styling for the application  
├── data/                 # Data storage  
│   └── encodings/        # Encoded data for facial recognition  
├── model/                # Machine learning model storage  
│   └── model.py          # Model definitions and handling  
├── scripts/              # Scripts for data processing and model setup  
│   ├── data_cleaning.py  # Data cleaning procedures  
│   ├── init_database.py  # Database initialization scripts  
│   └── train_model.py    # Model training functions  
├── tests/                # Unit and integration tests  
├── environment.yml       # Conda environment setup  
├── requirements.txt      # Python dependencies  
├── setup.py              # Installation script  
├── .gitignore            # Files and directories to ignore in git  
├── LICENSE               # License file  
└── README.md             # Primary project documentation

## Features

1. **Facial Recognition**: Capture and recognize student faces in real time.
2. **User Roles**: Different functionality for students and professors.
3. **Attendance Records**: Automatic attendance logging based on class schedules and photo timestamps.
4. **Analytics Dashboard**: Professor view includes attendance and downloadable reports.
5. **Real-Time Model Training**: Dynamic photo upload for enhancing facial recognition accuracy.


## Technologies Used

- **Frontend**: Streamlit for a user-friendly interface.
- **Backend**: Python with Streamlit, SQLAlchemy for database ORM.
- **Facial Recognition**: Amazon Rekognition for facial detection and authentication using a machine learning model.
- **Database**: Amazon RDS (connected to MySQL) for managing attendance, user, and configuration data.

## Setup and Installation

### Prerequisites
- Python 3.8 or higher
- Install dependencies with:
  ```bash
  pip install -r requirements.txt
  ```

### - Database Configuration
This project requires a database to store user and attendance information. Set up your database and update connection strings in database.py.

### - Running the Application
  - 1 Run the main application with:
    ```bash
    streamlit run app/main.py
    ```
  - 2 Access the app in your web browser at http://localhost:8501.

## Usage
  - For Students:
    - First-time users register by providing name, email, and group.
         -  Upload three photos for the facial recognition training.
          - Return to the app, authenticate, and take a photo to log attendance.
- For Professors:
  - Log in and select classes to view attendance records.
  - Download attendance reports and analyze metrics.


## Modules
### Main Functions
- validate_user: Checks if a user is registered and retrieves their role.
- register_new_user: Registers new students and uploads photos for model training.
- handle_student: Handles student-specific actions such as photo capture and attendance logging.
- handle_professor: Allows professors to access class attendance records.
    
### Data Preprocessing
- Located in preprocessing.py, this module includes:
    - capture_or_upload_photos: Guides students to upload three photos for training.
    - convert_to_base64: Converts photos to Base64 format for database storage.

### User Validation and Attendance Recording
The handlers.py module manages:
  - register_new_user: Registers new students and inserts records into the database.
  - check_user_exists: Checks if a user already exists based on their institutional email.
  - recognize_identity: Matches captured photo against registered user photos for attendance logging.

### Professor View
The handle_professor function enables:
  - Attendance Viewing: Professors select a class and date to view or download attendance.

### Styles and Customization
The styles.py file includes CSS for customizing the app interface. Modify styles here to match university branding.

## API Details
The system includes several internal API endpoints for interactions:
  - User Registration: Validates and registers new users in the system.
  - Attendance Logging: Records attendance based on facial recognition match.
  - Data Retrieval: Provides attendance records and  for professor.

## Technical Requirements
- Backend: Python with Streamlit, SQLAlchemy for database ORM.
- Database: Configured to store user data, group information, and attendance records.
- Frontend: Streamlit-based interface with support for image capture and uploads.


## License
This project is licensed under the MIT License.


