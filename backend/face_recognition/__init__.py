"""Face Recognition Module for Smart Attendance System"""

from .recognizer import FaceRecognizer
from .anti_spoofing import AntiSpoofingDetector
from .mask_detector import MaskDetector

__all__ = ['FaceRecognizer', 'AntiSpoofingDetector', 'MaskDetector']
