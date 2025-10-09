# Real-Time Face Recognition Attendance System

A web-based application built with Python, Flask, and JavaScript that performs real-time face detection and recognition to log attendance.

## Features

- **Live Face Detection:** Identifies faces from a live webcam feed.
- **Real-Time Recognition:** Matches detected faces against a database of known individuals.
- **Web-Based UI:** A modern, multi-page interface built with Flask and Bootstrap.
- **Dynamic Enrollment:** New users can be enrolled directly through the web interface by capturing their photo.
- **Attendance Logging:** Automatically logs the first time a known person is seen each day to a CSV file.

## Tech Stack

- **Backend:** Python, Flask, Flask-SocketIO
- **Computer Vision:** OpenCV, face_recognition (dlib)
- **Frontend:** HTML, CSS (Bootstrap 5), JavaScript

## Setup and Installation

1. **Clone the repository:**

    ```bash
    git clone [https://github.com/YourUsername/YourRepositoryName.git](https://github.com/YourUsername/YourRepositoryName.git)
    cd YourRepositoryName
    ```

2. **Create and activate a virtual environment:**

    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3. **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## How to Run

1. **Populate known faces:** Add sub-folders inside the `known_faces` directory for each person you want to recognize initially. Place their images inside their respective folders.

2. **Start the Flask server:**

    ```bash
    python app.py
    ```

3. **Open your web browser** and navigate to `http://127.0.0.1:5000`.
