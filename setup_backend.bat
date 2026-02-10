@echo off
REM Backend Setup Script for Windows

echo ================================
echo Smart Attendance System - Backend Setup
echo ================================

REM Navigate to backend directory
cd backend

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create necessary directories
echo Creating directories...
if not exist "models" mkdir models
if not exist "dataset" mkdir dataset
if not exist "logs" mkdir logs

REM Copy environment file
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
)

echo.
echo ================================
echo Backend setup completed!
echo ================================
echo.
echo Next steps:
echo 1. Activate virtual environment: backend\venv\Scripts\activate
echo 2. (Optional) Download shape_predictor_68_face_landmarks.dat for advanced anti-spoofing
echo 3. Capture dataset: python scripts\capture_dataset.py person_name
echo 4. Train encodings: python scripts\train_encodings.py
echo 5. Start server: python main.py
echo.

pause
