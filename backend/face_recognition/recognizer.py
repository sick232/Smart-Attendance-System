"""
Face Recognition Module
High-performance face recognition using face_recognition library (dlib-based)
Optimized for low latency with GPU support
"""

import face_recognition
import numpy as np
import cv2
import pickle
import os
from typing import Optional, Tuple, List
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)


class FaceRecognizer:
    """
    Face recognition handler with encoding-based matching
    Uses Euclidean distance for face comparison
    """
    
    def __init__(
        self, 
        encodings_path: str = "models/face_encodings.pkl",
        threshold: float = 0.6
    ):
        self.encodings_path = encodings_path
        self.threshold = threshold  # Lower = stricter matching
        self.known_encodings = {}  # {person_id: [encodings]}
        self.known_names = {}  # {person_id: name}
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Create models directory if it doesn't exist
        os.makedirs("models", exist_ok=True)
    
    async def load_encodings(self):
        """Load pre-computed face encodings from disk"""
        if os.path.exists(self.encodings_path):
            try:
                with open(self.encodings_path, 'rb') as f:
                    data = pickle.load(f)
                    self.known_encodings = data.get('encodings', {})
                    self.known_names = data.get('names', {})
                logger.info(f"Loaded encodings for {len(self.known_encodings)} persons")
            except Exception as e:
                logger.error(f"Error loading encodings: {str(e)}")
                self.known_encodings = {}
                self.known_names = {}
        else:
            logger.info("No existing encodings found, starting fresh")
    
    async def save_encodings(self):
        """Save face encodings to disk"""
        try:
            data = {
                'encodings': self.known_encodings,
                'names': self.known_names
            }
            with open(self.encodings_path, 'wb') as f:
                pickle.dump(data, f)
            logger.info("Encodings saved successfully")
        except Exception as e:
            logger.error(f"Error saving encodings: {str(e)}")
    
    async def extract_encoding(self, image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract face encoding from image
        Uses HOG-based face detection for speed (can switch to CNN for accuracy)
        """
        loop = asyncio.get_event_loop()
        
        def _extract():
            # Convert BGR to RGB (OpenCV uses BGR, face_recognition uses RGB)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect face locations (HOG is faster, CNN is more accurate)
            face_locations = face_recognition.face_locations(
                rgb_image, 
                model="hog"  # Use "cnn" for better accuracy but slower
            )
            
            if len(face_locations) == 0:
                logger.warning("No face detected in image")
                return None
            
            # Use the first detected face
            face_location = face_locations[0]
            
            # Compute face encoding
            encodings = face_recognition.face_encodings(rgb_image, [face_location])
            
            if len(encodings) > 0:
                return encodings[0]
            
            return None
        
        try:
            encoding = await loop.run_in_executor(self.executor, _extract)
            return encoding
        except Exception as e:
            logger.error(f"Error extracting encoding: {str(e)}")
            return None
    
    async def register_person(
        self, 
        person_id: str, 
        name: str, 
        face_encodings: List[np.ndarray]
    ) -> bool:
        """
        Register a new person with multiple face encodings
        Multiple encodings improve recognition accuracy
        """
        try:
            self.known_encodings[person_id] = face_encodings
            self.known_names[person_id] = name
            
            await self.save_encodings()
            
            logger.info(f"Registered {name} ({person_id}) with {len(face_encodings)} encodings")
            return True
        except Exception as e:
            logger.error(f"Error registering person: {str(e)}")
            return False
    
    async def recognize_face(
        self, 
        image: np.ndarray
    ) -> Tuple[Optional[str], Optional[str], Optional[float]]:
        """
        Recognize face in image
        Returns: (person_id, name, confidence)
        Optimized for low latency (<300ms)
        """
        loop = asyncio.get_event_loop()
        
        def _recognize():
            # Convert BGR to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            face_locations = face_recognition.face_locations(rgb_image, model="hog")
            
            if len(face_locations) == 0:
                return None, None, None
            
            # Get encoding for the first face
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            
            if len(face_encodings) == 0:
                return None, None, None
            
            face_encoding = face_encodings[0]
            
            # Compare with known faces
            best_match_id = None
            best_match_name = None
            min_distance = float('inf')
            
            for person_id, known_encodings_list in self.known_encodings.items():
                # Compare with all encodings for this person
                for known_encoding in known_encodings_list:
                    # Calculate Euclidean distance
                    distance = np.linalg.norm(face_encoding - known_encoding)
                    
                    if distance < min_distance:
                        min_distance = distance
                        best_match_id = person_id
                        best_match_name = self.known_names[person_id]
            
            # Check if best match is within threshold
            if min_distance <= self.threshold:
                confidence = 1.0 - (min_distance / 1.0)  # Convert distance to confidence
                return best_match_id, best_match_name, confidence
            
            return None, None, None
        
        try:
            person_id, name, confidence = await loop.run_in_executor(
                self.executor, 
                _recognize
            )
            return person_id, name, confidence
        except Exception as e:
            logger.error(f"Error recognizing face: {str(e)}")
            return None, None, None
    
    async def delete_person(self, person_id: str) -> bool:
        """Delete a person's face encodings"""
        try:
            if person_id in self.known_encodings:
                del self.known_encodings[person_id]
                del self.known_names[person_id]
                await self.save_encodings()
                logger.info(f"Deleted encodings for {person_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting person: {str(e)}")
            return False
    
    def cleanup(self):
        """Cleanup resources"""
        self.executor.shutdown(wait=True)
        logger.info("Face recognizer cleaned up")
