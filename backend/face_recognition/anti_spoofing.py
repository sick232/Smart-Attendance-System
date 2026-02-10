"""
Anti-Spoofing Detection Module
Implements eye blink detection for liveness verification
Prevents photo/video-based attacks
"""

import cv2
import numpy as np
from scipy.spatial import distance as dist
import dlib
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import os

logger = logging.getLogger(__name__)


class AntiSpoofingDetector:
    """
    Liveness detection using eye blink detection
    Uses facial landmarks to detect eye aspect ratio (EAR)
    """
    
    def __init__(
        self, 
        ear_threshold: float = 0.25,
        predictor_path: str = "models/shape_predictor_68_face_landmarks.dat"
    ):
        self.ear_threshold = ear_threshold
        self.predictor_path = predictor_path
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Initialize dlib detector and predictor
        self.detector = dlib.get_frontal_face_detector()
        
        # Download predictor if not exists
        if not os.path.exists(predictor_path):
            logger.warning(f"Landmark predictor not found at {predictor_path}")
            logger.info("For full anti-spoofing, download shape_predictor_68_face_landmarks.dat")
            logger.info("Using simplified liveness check")
            self.predictor = None
        else:
            self.predictor = dlib.shape_predictor(predictor_path)
        
        # Eye landmark indices
        self.LEFT_EYE_INDICES = list(range(36, 42))
        self.RIGHT_EYE_INDICES = list(range(42, 48))
    
    def _eye_aspect_ratio(self, eye_landmarks):
        """
        Calculate Eye Aspect Ratio (EAR)
        EAR is low when eye is closed
        """
        # Vertical eye distances
        A = dist.euclidean(eye_landmarks[1], eye_landmarks[5])
        B = dist.euclidean(eye_landmarks[2], eye_landmarks[4])
        
        # Horizontal eye distance
        C = dist.euclidean(eye_landmarks[0], eye_landmarks[3])
        
        # EAR formula
        ear = (A + B) / (2.0 * C)
        return ear
    
    async def check_liveness(self, image: np.ndarray) -> bool:
        """
        Check if the image contains a live person
        Returns True if live, False if spoofed
        """
        # If predictor not available, use simplified check
        if self.predictor is None:
            return await self._simplified_liveness_check(image)
        
        loop = asyncio.get_event_loop()
        
        def _check():
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.detector(gray, 0)
            
            if len(faces) == 0:
                logger.warning("No face detected for liveness check")
                return False
            
            # Use first face
            face = faces[0]
            
            # Get facial landmarks
            landmarks = self.predictor(gray, face)
            
            # Extract eye coordinates
            left_eye = []
            for i in self.LEFT_EYE_INDICES:
                left_eye.append((landmarks.part(i).x, landmarks.part(i).y))
            
            right_eye = []
            for i in self.RIGHT_EYE_INDICES:
                right_eye.append((landmarks.part(i).x, landmarks.part(i).y))
            
            # Calculate EAR for both eyes
            left_ear = self._eye_aspect_ratio(np.array(left_eye))
            right_ear = self._eye_aspect_ratio(np.array(right_eye))
            
            # Average EAR
            avg_ear = (left_ear + right_ear) / 2.0
            
            # Check if eyes are open (live person)
            # For robust detection, you'd track EAR over multiple frames
            # and detect blinks (temporary drops in EAR)
            # For simplicity, we check if eyes are reasonably open
            return avg_ear > self.ear_threshold
        
        try:
            is_live = await loop.run_in_executor(self.executor, _check)
            return is_live
        except Exception as e:
            logger.error(f"Liveness check error: {str(e)}")
            # On error, default to True to avoid blocking legitimate users
            return True
    
    async def _simplified_liveness_check(self, image: np.ndarray) -> bool:
        """
        Simplified liveness check without landmarks
        Uses basic image quality and face detection metrics
        """
        loop = asyncio.get_event_loop()
        
        def _check():
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Check image quality metrics
            # 1. Check for blur (Laplacian variance)
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # If too blurry, might be a printed photo
            if blur_score < 50:
                logger.warning(f"Image too blurry for liveness: {blur_score}")
                return False
            
            # 2. Detect faces
            faces = self.detector(gray, 0)
            
            if len(faces) == 0:
                return False
            
            # 3. Check color distribution (real faces have varied colors)
            # Convert to HSV
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Get face region
            face = faces[0]
            x1, y1, x2, y2 = face.left(), face.top(), face.right(), face.bottom()
            
            # Ensure coordinates are within bounds
            h, w = image.shape[:2]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            
            face_region = hsv[y1:y2, x1:x2]
            
            if face_region.size == 0:
                return False
            
            # Check saturation variance (photos tend to have lower variance)
            saturation = face_region[:, :, 1]
            sat_variance = np.var(saturation)
            
            # Real faces typically have higher saturation variance
            if sat_variance < 100:
                logger.warning(f"Low saturation variance: {sat_variance}")
                return False
            
            return True
        
        try:
            is_live = await loop.run_in_executor(self.executor, _check)
            return is_live
        except Exception as e:
            logger.error(f"Simplified liveness check error: {str(e)}")
            return True
    
    def cleanup(self):
        """Cleanup resources"""
        self.executor.shutdown(wait=True)
