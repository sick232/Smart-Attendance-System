#!/bin/bash

# Frontend Setup Script for Linux/Mac

echo "================================"
echo "Smart Attendance System - Frontend Setup"
echo "================================"

# Navigate to frontend directory
cd frontend

# Install dependencies
echo "Installing dependencies..."
npm install

# Copy environment file
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

echo ""
echo "================================"
echo "Frontend setup completed!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Update .env file with your API URL (if different from localhost:8000)"
echo "2. Start development server: npm start"
echo "3. Build for production: npm run build"
echo ""
