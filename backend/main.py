"""
Smart Attendance System - Main FastAPI Application
High-performance backend with async endpoints for real-time face recognition
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
import asyncio
import cv2
import numpy as np
import base64
from io import BytesIO
import logging

from database.db_manager import DatabaseManager
from face_recognition.recognizer import FaceRecognizer
from face_recognition.anti_spoofing import AntiSpoofingDetector
from face_recognition.mask_detector import MaskDetector
from utils.export_utils import export_to_csv, export_to_excel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Smart Attendance System", version="1.0.0")

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db_manager = DatabaseManager()
face_recognizer = FaceRecognizer()
anti_spoof = AntiSpoofingDetector()
mask_detector = MaskDetector()

# Pydantic models for request/response
class RegisterRequest(BaseModel):
    name: str
    person_id: str
    
class RecognitionResponse(BaseModel):
    success: bool
    person_id: Optional[str] = None
    name: Optional[str] = None
    confidence: Optional[float] = None
    is_live: Optional[bool] = None
    has_mask: Optional[bool] = None
    message: str

class AttendanceRecord(BaseModel):
    id: int
    person_id: str
    name: str
    date: str
    time: str

class AttendanceFilter(BaseModel):
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    person_id: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    logger.info("Starting Smart Attendance System...")
    db_manager.initialize_database()
    await face_recognizer.load_encodings()
    logger.info("System initialized successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down...")
    face_recognizer.cleanup()


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "system": "Smart Attendance System",
        "version": "1.0.0"
    }


@app.post("/api/register", response_model=RecognitionResponse)
async def register_person(
    name: str = Form(...),
    person_id: str = Form(...),
    images: List[UploadFile] = File(...)
):
    """
    Register a new person with face images
    Requires 5-10 images for robust encoding
    """
    try:
        # Validate inputs
        if not name or not person_id:
            raise HTTPException(status_code=400, detail="Name and person_id are required")
        
        if len(images) < 5:
            raise HTTPException(status_code=400, detail="At least 5 images required for registration")
        
        # Check if person already exists
        if db_manager.person_exists(person_id):
            raise HTTPException(status_code=400, detail="Person ID already registered")
        
        # Process images and extract face encodings
        face_encodings = []
        for image_file in images:
            # Read image
            contents = await image_file.read()
            nparr = np.frombuffer(contents, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            # Extract encoding
            encoding = await face_recognizer.extract_encoding(img)
            if encoding is not None:
                face_encodings.append(encoding)
        
        if len(face_encodings) < 3:
            raise HTTPException(
                status_code=400, 
                detail="Could not extract enough face encodings. Please provide clear face images"
            )
        
        # Register person
        success = await face_recognizer.register_person(person_id, name, face_encodings)
        
        if success:
            # Add to database
            db_manager.add_person(person_id, name)
            
            return RecognitionResponse(
                success=True,
                person_id=person_id,
                name=name,
                message=f"Successfully registered {name} with {len(face_encodings)} face encodings"
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to register person")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/recognize", response_model=RecognitionResponse)
async def recognize_face(image: UploadFile = File(...)):
    """
    Recognize face from uploaded image with anti-spoofing and mask detection
    Optimized for low latency (<300ms)
    """
    try:
        # Read and decode image
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image")
        
        # Perform anti-spoofing check
        is_live = await anti_spoof.check_liveness(img)
        
        if not is_live:
            return RecognitionResponse(
                success=False,
                is_live=False,
                message="Liveness check failed. Please ensure you are a real person."
            )
        
        # Detect mask
        has_mask = await mask_detector.detect_mask(img)
        
        # Recognize face
        person_id, name, confidence = await face_recognizer.recognize_face(img)
        
        if person_id is None:
            return RecognitionResponse(
                success=False,
                is_live=True,
                has_mask=has_mask,
                message="Face not recognized"
            )
        
        # Check if already marked attendance today
        today = date.today().isoformat()
        if db_manager.has_attendance_today(person_id, today):
            return RecognitionResponse(
                success=False,
                person_id=person_id,
                name=name,
                confidence=confidence,
                is_live=True,
                has_mask=has_mask,
                message=f"Attendance already marked for {name} today"
            )
        
        # Mark attendance
        current_time = datetime.now().strftime("%H:%M:%S")
        db_manager.mark_attendance(person_id, name, today, current_time)
        
        return RecognitionResponse(
            success=True,
            person_id=person_id,
            name=name,
            confidence=confidence,
            is_live=True,
            has_mask=has_mask,
            message=f"Attendance marked successfully for {name}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Recognition error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/attendance", response_model=List[AttendanceRecord])
async def get_attendance(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    person_id: Optional[str] = None
):
    """
    Get attendance records with optional filtering
    """
    try:
        records = db_manager.get_attendance(
            start_date=start_date,
            end_date=end_date,
            person_id=person_id
        )
        
        return [
            AttendanceRecord(
                id=r[0],
                person_id=r[1],
                name=r[2],
                date=r[3],
                time=r[4]
            )
            for r in records
        ]
    except Exception as e:
        logger.error(f"Get attendance error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/export/csv")
async def export_csv(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    person_id: Optional[str] = None
):
    """
    Export attendance records to CSV
    """
    try:
        records = db_manager.get_attendance(
            start_date=start_date,
            end_date=end_date,
            person_id=person_id
        )
        
        csv_buffer = export_to_csv(records)
        
        return StreamingResponse(
            BytesIO(csv_buffer.getvalue().encode()),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=attendance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )
    except Exception as e:
        logger.error(f"CSV export error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/export/excel")
async def export_excel(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    person_id: Optional[str] = None
):
    """
    Export attendance records to Excel
    """
    try:
        records = db_manager.get_attendance(
            start_date=start_date,
            end_date=end_date,
            person_id=person_id
        )
        
        excel_buffer = export_to_excel(records)
        
        return StreamingResponse(
            excel_buffer,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f"attachment; filename=attendance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            }
        )
    except Exception as e:
        logger.error(f"Excel export error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/persons")
async def get_all_persons():
    """
    Get list of all registered persons
    """
    try:
        persons = db_manager.get_all_persons()
        return [{"person_id": p[0], "name": p[1]} for p in persons]
    except Exception as e:
        logger.error(f"Get persons error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/person/{person_id}")
async def delete_person(person_id: str):
    """
    Delete a registered person
    """
    try:
        success = await face_recognizer.delete_person(person_id)
        if success:
            db_manager.delete_person(person_id)
            return {"success": True, "message": f"Person {person_id} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Person not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete person error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
