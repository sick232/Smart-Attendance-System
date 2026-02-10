"""
Mask Detection Module
Detects whether a person is wearing a face mask
Uses pre-trained MobileNetV2-based classifier
"""

import cv2
import numpy as np
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging
import os

logger = logging.getLogger(__name__)

# TensorFlow is optional - only needed for advanced mask detection
try:
    from tensorflow import keras
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
    from tensorflow.keras.preprocessing.image import img_to_array
    HAS_TENSORFLOW = True
except ImportError:
    HAS_TENSORFLOW = False
    logger.warning("TensorFlow not installed. Using simplified mask detection.")


class MaskDetector:
    """
    Face mask detection using MobileNetV2
    Supports recognition with mask on
    """
    
    def __init__(
        self, 
        model_path: str = "models/mask_detector.h5",
        confidence_threshold: float = 0.5
    ):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.model = None
        self.executor = ThreadPoolExecutor(max_workers=2)
        
        # Load model if available
        self._load_model()
        
        # Face detector for preprocessing
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
    
    def _load_model(self):
        """Load pre-trained mask detection model"""
        if not HAS_TENSORFLOW:
            logger.info("TensorFlow not available. Using simplified mask detection.")
            self.model = None
            return
            
        try:
            if os.path.exists(self.model_path):
                self.model = keras.models.load_model(self.model_path)
                logger.info("Mask detection model loaded successfully")
            else:
                logger.warning(f"Mask detection model not found at {self.model_path}")
                logger.info("Mask detection will use simplified approach")
                self.model = None
        except Exception as e:
            logger.error(f"Error loading mask model: {str(e)}")
            self.model = None
    
    async def detect_mask(self, image: np.ndarray) -> bool:
        """
        Detect if person is wearing a mask
        Returns True if mask detected, False otherwise
        """
        if self.model is None:
            # Simplified mask detection without ML model
            return await self._simplified_mask_detection(image)
        
        loop = asyncio.get_event_loop()
        
        def _detect():
            # Convert to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(60, 60)
            )
            
            if len(faces) == 0:
                logger.warning("No face detected for mask detection")
                return False
            
            # Use first face
            (x, y, w, h) = faces[0]
            
            # Extract face ROI
            face_roi = rgb_image[y:y+h, x:x+w]
            
            # Preprocess for model
            face_roi = cv2.resize(face_roi, (224, 224))
            face_roi = img_to_array(face_roi)
            face_roi = preprocess_input(face_roi)
            face_roi = np.expand_dims(face_roi, axis=0)
            
            # Predict
            prediction = self.model.predict(face_roi, verbose=0)[0]
            
            # prediction[0] = no mask, prediction[1] = mask
            has_mask = prediction[1] > self.confidence_threshold
            
            return has_mask
        
        try:
            has_mask = await loop.run_in_executor(self.executor, _detect)
            return has_mask
        except Exception as e:
            logger.error(f"Mask detection error: {str(e)}")
            return False
    
    async def _simplified_mask_detection(self, image: np.ndarray) -> bool:
        """
        Simplified mask detection using color and region analysis
        Detects if lower face region has different characteristics
        """
        loop = asyncio.get_event_loop()
        
        def _detect():
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(60, 60)
            )
            
            if len(faces) == 0:
                return False
            
            # Use first face
            (x, y, w, h) = faces[0]
            
            # Divide face into upper and lower regions
            mid_y = y + h // 2
            
            # Upper face (eyes, forehead)
            upper_region = gray[y:mid_y, x:x+w]
            
            # Lower face (nose, mouth - where mask would be)
            lower_region = gray[mid_y:y+h, x:x+w]
            
            if upper_region.size == 0 or lower_region.size == 0:
                return False
            
            # Calculate texture features (standard deviation)
            # Masks typically have more uniform texture
            upper_std = np.std(upper_region)
            lower_std = np.std(lower_region)
            
            # If lower face has significantly lower texture variation,
            # might indicate a mask
            std_ratio = lower_std / (upper_std + 1e-6)
            
            # Also check edge density in lower region
            edges = cv2.Canny(lower_region, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Heuristic: mask if lower region is smoother and has fewer edges
            has_mask = (std_ratio < 0.7) and (edge_density < 0.1)
            
            return has_mask
        
        try:
            has_mask = await loop.run_in_executor(self.executor, _detect)
            return has_mask
        except Exception as e:
            logger.error(f"Simplified mask detection error: {str(e)}")
            return False
    
    def cleanup(self):
        """Cleanup resources"""
        self.executor.shutdown(wait=True)
