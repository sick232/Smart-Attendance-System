"""
Simplified Dataset Capture - Saves in guaranteed compatible format
"""

import cv2
import numpy as np
from PIL import Image
from pathlib import Path
import sys

def capture_simple(person_name, num_images=10):
    """Capture images with guaranteed compatible format"""
    
    # Create directory
    person_dir = Path("dataset") / person_name
    person_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize webcam
    print("Initializing webcam...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam")
        sys.exit(1)
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print(f"\n{'='*60}")
    print(f"Capturing images for: {person_name}")
    print(f"{'='*60}")
    print("Press 'a' for AUTO CAPTURE or SPACE for manual capture")
    print("Press 'q' to quit")
    print(f"{'='*60}\n")
    
    count = 0
    auto_mode = False
    frame_count = 0
    
    while count < num_images:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Display
        display_frame = frame.copy()
        cv2.putText(display_frame, f"Captured: {count}/{num_images}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(display_frame, "Press 'a' for auto or SPACE for manual", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        cv2.imshow('Capture', display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        # Auto mode
        if key == ord('a'):
            auto_mode = True
            print("Auto-capture mode activated!")
        
        # Manual capture
        if key == ord(' ') or (auto_mode and frame_count % 10 == 0):
            # Convert frame to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            pil_img = Image.fromarray(rgb_frame.astype('uint8'), 'RGB')
            
            # Save using PIL
            filename = person_dir / f"{person_name}_{count+1:03d}.jpg"
            pil_img.save(filename, 'JPEG', quality=95)
            
            count += 1
            print(f"✓ Captured image {count}/{num_images}")
            
            # Flash effect
            cv2.rectangle(display_frame, (0, 0), (640, 480), (255, 255, 255), 20)
            cv2.imshow('Capture', display_frame)
            cv2.waitKey(100)
        
        # Quit
        if key == ord('q'):
            break
        
        frame_count += 1
    
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"\n{'='*60}")
    print(f"✓ Captured {count} images successfully!")
    print(f"Saved to: {person_dir}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    person_name = sys.argv[1] if len(sys.argv) > 1 else "test_user"
    num_images = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    
    capture_simple(person_name, num_images)
