#!/bin/bash

# Backend Setup Script for Linux/Mac

echo "================================"
echo "Smart Attendance System - Backend Setup"
echo "================================"

# Navigate to backend directory
cd backend

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p models
mkdir -p dataset
mkdir -p logs

# Copy environment file
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

echo ""
echo "================================"
echo "Backend setup completed!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source backend/venv/bin/activate"
echo "2. (Optional) Download shape_predictor_68_face_landmarks.dat for advanced anti-spoofing"
echo "3. Capture dataset: python scripts/capture_dataset.py <person_name>"
echo "4. Train encodings: python scripts/train_encodings.py"
echo "5. Start server: python main.py"
echo ""
