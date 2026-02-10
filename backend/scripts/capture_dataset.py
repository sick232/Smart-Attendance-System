"""
Dataset Capture Script
Capture face images from webcam for registration
Automatically detects and saves face images
"""

import cv2
import os
import sys
from pathlib import Path
import time

def capture_dataset(person_name: str, num_images: int = 50):
    """
    Capture face images for dataset
    
    Args:
        person_name: Name of the person
        num_images: Number of images to capture (default: 50)
    """
    # Create dataset directory structure
    dataset_dir = Path("dataset")
    person_dir = dataset_dir / person_name
    person_dir.mkdir(parents=True, exist_ok=True)
    
    # Load face detector
    face_cascade = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    
    # Initialize webcam
    print("Initializing webcam...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open webcam")
        sys.exit(1)
    
    # Set camera resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print(f"\n{'='*60}")
    print(f"Dataset Capture for: {person_name}")
    print(f"{'='*60}")
    print(f"Target images: {num_images}")
    print("\nInstructions:")
    print("- Position your face in the frame")
    print("- Look at different angles (left, right, up, down)")
    print("- Try different expressions")
    print("- Vary distance from camera")
    print("- Press 'q' to quit early")
    print(f"{'='*60}\n")
    
    count = 0
    frame_skip = 0
    skip_frames = 5  # Capture every 5th frame
    
    print("Press SPACE to start capturing...")
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("Error: Failed to capture frame")
            break
        
        # Flip frame horizontally for mirror effect
        frame = cv2.flip(frame, 1)
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(100, 100)
        )
        
        # Draw rectangles around faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"Face Detected",
                (x, y-10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )
        
        # Display progress
        cv2.putText(
            frame,
            f"Captured: {count}/{num_images}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )
        
        cv2.putText(
            frame,
            f"Person: {person_name}",
            (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2
        )
        
        if count < num_images:
            cv2.putText(
                frame,
                "Press SPACE to capture or 'a' for auto-capture",
                (10, frame.shape[0] - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )
        else:
            cv2.putText(
                frame,
                "Capture Complete! Press 'q' to exit",
                (10, frame.shape[0] - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )
        
        cv2.imshow('Dataset Capture', frame)
        
        key = cv2.waitKey(1) & 0xFF
        
        # Manual capture with SPACE
        if key == ord(' '):
            if len(faces) > 0 and count < num_images:
                # Save the full frame (not just face region for better compatibility)
                filename = person_dir / f"{person_name}_{count+1:03d}.jpg"
                # Ensure image is saved in standard RGB format
                cv2.imwrite(str(filename), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                
                count += 1
                print(f"Captured image {count}/{num_images}")
                
                # Brief flash effect
                cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), (255, 255, 255), 20)
                cv2.imshow('Dataset Capture', frame)
                cv2.waitKey(100)
        
        # Auto-capture mode
        elif key == ord('a'):
            print("\nAuto-capture mode activated!")
            while count < num_images:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame = cv2.flip(frame, 1)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(100, 100))
                
                if len(faces) > 0:
                    frame_skip += 1
                    if frame_skip % skip_frames == 0:
                        (x, y, w, h) = faces[0]
                        
                        filename = person_dir / f"{person_name}_{count+1:03d}.jpg"
                        # Save full frame in standard format
                        cv2.imwrite(str(filename), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                        
                        count += 1
                        print(f"Auto-captured image {count}/{num_images}")
                        
                        # Draw rectangle
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Update display
                cv2.putText(frame, f"Captured: {count}/{num_images}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.imshow('Dataset Capture', frame)
                
                if cv2.waitKey(50) & 0xFF == ord('q'):
                    break
                
                time.sleep(0.1)
        
        # Quit
        elif key == ord('q'):
            break
        
        # Auto-complete
        if count >= num_images:
            time.sleep(1)
            break
    
    # Cleanup
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"\n{'='*60}")
    print(f"Dataset capture completed!")
    print(f"Total images captured: {count}")
    print(f"Images saved to: {person_dir}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python capture_dataset.py <person_name> [num_images]")
        print("Example: python capture_dataset.py john_doe 50")
        sys.exit(1)
    
    person_name = sys.argv[1]
    num_images = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    capture_dataset(person_name, num_images)
