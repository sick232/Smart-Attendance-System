"""
Test face_recognition with actual dataset images
"""

import face_recognition
from PIL import Image
import numpy as np
from pathlib import Path

def test_single_image():
    """Test loading and processing a single image"""
    
    img_path = Path("dataset/test_user/test_user_001.jpg")
    
    if not img_path.exists():
        print(f"Image not found: {img_path}")
        return
    
    print(f"Testing image: {img_path}")
    print()
    
    # Load with PIL
    pil_img = Image.open(img_path)
    print(f"PIL Image mode: {pil_img.mode}")
    print(f"PIL Image size: {pil_img.size}")
    
    # Convert to RGB
    if pil_img.mode != 'RGB':
        pil_img = pil_img.convert('RGB')
        print(f"Converted to RGB")
    
    # Convert to numpy
    arr = np.array(pil_img, dtype=np.uint8)
    print(f"Array shape: {arr.shape}")
    print(f"Array dtype: {arr.dtype}")
    print(f"Array min/max: {arr.min()}/{arr.max()}")
    print(f"Array flags: C_CONTIGUOUS={arr.flags['C_CONTIGUOUS']}, F_CONTIGUOUS={arr.flags['F_CONTIGUOUS']}")
    print()
    
    # Make contiguous
    arr = np.ascontiguousarray(arr)
    print(f"After ascontiguousarray:")
    print(f"Array flags: C_CONTIGUOUS={arr.flags['C_CONTIGUOUS']}")
    print()
    
    # Try to use face_recognition library directly
    print("Attempting face detection...")
    try:
        # Use the library's built-in image loading instead
        image = face_recognition.load_image_file(str(img_path))
        print(f"✓ Loaded with load_image_file()")
        print(f"  Shape: {image.shape}, dtype: {image.dtype}")
        
        face_locations = face_recognition.face_locations(image)
        print(f"✓ Face detection successful!")
        print(f"  Found {len(face_locations)} face(s)")
        
        if len(face_locations) > 0:
            encodings = face_recognition.face_encodings(image, face_locations)
            print(f"✓ Generated {len(encodings)} encoding(s)")
            print(f"  Encoding shape: {encodings[0].shape}")
        
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_single_image()
