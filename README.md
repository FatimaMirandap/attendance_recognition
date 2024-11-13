This repository contains the code for a facial recognition-based attendance system designed to streamline attendance tracking for university students and professors. 

The system was designed for the Universidad Politécnica de Yucatán and uses a cookie-cutter project structure, in this case we only toke a single gropu, but you can  add as many groups you want in the db.

## Contents
- [Project Overview](#project-overview)
- [Project Structure](#project-structure)
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
- 
# Face-Attendance-Recognition-System

Facial recognition based attendance web application, designed for universities and to be used by students and teachers. Students can register their attendance by taking a photo through their device's camera, which will be validated by a machine learning model in real time; they can also register in the system to be added to the database. Teachers can access attendance reports. The system is developed to integrate with a real-time database, ensuring accurate and efficient attendance management.


## Main Functionalities:
- User Registration: Authentication system that allows differentiated access for students and teachers.
- Attendance Capture:
  - Students can activate the camera, capture their photo, and the system validates their identity with the facial recognition model.
  - If the system correctly identifies the student, it automatically registers their attendance.
- For Teachers:
  - Teachers can access by selecting their group and subject in order to obtain an attendance report for a selected period of time.

## Project Structure

attendance_recognition/
attendance_recognition/ # Main project directory ├── app/ # Application directory │ ├── main.py # Main application entry point │ ├── utils/ # Utility functions │ │ ├── init.py # Initializes the utils package │ │ ├── app_styles.css # CSS styling for the application ├── data/ # Data storage │ └── encodings/ # Encoded data for facial recognition ├── docs/ # Project documentation │ └── README.md # Additional project documentation ├── model/ # Machine learning model storage │ └── model.py # Model definitions and handling ├── scripts/ # Scripts for data processing and model setup │ ├── data_cleaning.py # Data cleaning procedures │ ├── init_database.py # Database initialization scripts │ └── train_model.py # Model training functions ├── tests/ # Unit and integration tests │ └── README.md # Test documentation ├── environment.yml # Conda environment setup ├── requirements.txt # Python dependencies ├── setup.py # Installation script ├── .gitignore # Files and directories to ignore in git ├── LICENSE # License file └── README.md # Primary project documentation

## Technologies Used
- Frontend: 
- Backend: 
- Facial Recognition: Amazon Rekognition for facial detection and authentication with a machine learning model
- Database: Amazon RDS (linked to MySQL) for attendance, user and configuration data management.
