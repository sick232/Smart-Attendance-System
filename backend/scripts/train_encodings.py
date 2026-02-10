"""
Training Script
Generate face encodings from dataset images
Serialize encodings for fast recognition
"""

import face_recognition
import pickle
import cv2
from pathlib import Path
import sys
import numpy as np
from tqdm import tqdm

def train_encodings(dataset_path: str = "dataset", output_path: str = "models/face_encodings.pkl"):
    """
    Generate face encodings from dataset
    
    Args:
        dataset_path: Path to dataset directory
        output_path: Path to save encodings
    """
    dataset_dir = Path(dataset_path)
    
    if not dataset_dir.exists():
        print(f"Error: Dataset directory '{dataset_path}' not found")
        sys.exit(1)
    
    print(f"\n{'='*60}")
    print("Face Encodings Training")
    print(f"{'='*60}")
    print(f"Dataset path: {dataset_dir}")
    print(f"Output path: {output_path}\n")
    
    known_encodings = {}
    known_names = {}
    
    # Get all person directories
    person_dirs = [d for d in dataset_dir.iterdir() if d.is_dir()]
    
    if len(person_dirs) == 0:
        print("Error: No person directories found in dataset")
        print("Expected structure: dataset/person_name/image1.jpg ...")
        sys.exit(1)
    
    print(f"Found {len(person_dirs)} persons in dataset\n")
    
    total_images = 0
    total_encodings = 0
    
    for person_dir in person_dirs:
        person_name = person_dir.name
        person_id = person_name.lower().replace(" ", "_")
        
        # Get all image files
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png']:
            image_files.extend(person_dir.glob(ext))
        
        if len(image_files) == 0:
            print(f"Warning: No images found for {person_name}")
            continue
        
        print(f"Processing {person_name} ({len(image_files)} images)...")
        
        person_encodings = []
        
        for image_path in tqdm(image_files, desc=f"  Encoding"):
            total_images += 1
            
            try:
                # Load image using face_recognition's built-in loader
                rgb_image = face_recognition.load_image_file(str(image_path))
                
                # Detect face locations
                face_locations = face_recognition.face_locations(rgb_image, model="hog")
                
                if len(face_locations) == 0:
                    print(f"  Warning: No face detected in {image_path.name}")
                    continue
                
                # Get encodings
                encodings = face_recognition.face_encodings(rgb_image, face_locations)
                
                if len(encodings) > 0:
                    person_encodings.append(encodings[0])
                    total_encodings += 1
                
            except Exception as e:
                print(f"  Error processing {image_path.name}: {str(e)}")
                continue
        
        if len(person_encodings) > 0:
            known_encodings[person_id] = person_encodings
            known_names[person_id] = person_name
            print(f"  ✓ Generated {len(person_encodings)} encodings for {person_name}\n")
        else:
            print(f"  ✗ No valid encodings generated for {person_name}\n")
    
    # Save encodings
    if len(known_encodings) > 0:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'encodings': known_encodings,
            'names': known_names
        }
        
        with open(output_path, 'wb') as f:
            pickle.dump(data, f)
        
        print(f"{'='*60}")
        print("Training Summary:")
        print(f"{'='*60}")
        print(f"Total images processed: {total_images}")
        print(f"Total encodings generated: {total_encodings}")
        print(f"Persons registered: {len(known_encodings)}")
        print(f"\nEncodings saved to: {output_path}")
        print(f"{'='*60}\n")
        
        # Display person-wise summary
        print("Person-wise encodings:")
        for person_id, encodings in known_encodings.items():
            name = known_names[person_id]
            print(f"  • {name}: {len(encodings)} encodings")
        
    else:
        print("Error: No encodings generated. Please check your dataset.")
        sys.exit(1)


if __name__ == "__main__":
    dataset_path = sys.argv[1] if len(sys.argv) > 1 else "dataset"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "models/face_encodings.pkl"
    
    train_encodings(dataset_path, output_path)
