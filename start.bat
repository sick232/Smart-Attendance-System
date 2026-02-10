@echo off
REM Quick Start Script - Starts both backend and frontend

echo ================================
echo Smart Attendance System - Quick Start
echo ================================

REM Start backend
echo Starting backend server...
start "Backend Server" cmd /k "cd backend && venv\Scripts\activate && python main.py"

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend
echo Starting frontend server...
start "Frontend Server" cmd /k "cd frontend && npm start"

echo.
echo ================================
echo System is running!
echo ================================
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Close the terminal windows to stop the servers
echo.

pause
