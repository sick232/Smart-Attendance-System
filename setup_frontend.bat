@echo off
REM Frontend Setup Script for Windows

echo ================================
echo Smart Attendance System - Frontend Setup
echo ================================

REM Navigate to frontend directory
cd frontend

REM Install dependencies
echo Installing dependencies...
call npm install

REM Copy environment file
if not exist ".env" (
    echo Creating .env file...
    copy .env.example .env
)

echo.
echo ================================
echo Frontend setup completed!
echo ================================
echo.
echo Next steps:
echo 1. Update .env file with your API URL (if different from localhost:8000)
echo 2. Start development server: npm start
echo 3. Build for production: npm run build
echo.

pause
