"""
Fix image formats in dataset
Converts all images to standard RGB format
"""

import cv2
from pathlib import Path
import sys

def fix_images(dataset_path="dataset"):
    """Convert all images to standard RGB format"""
    dataset_dir = Path(dataset_path)
    
    if not dataset_dir.exists():
        print(f"Dataset directory not found: {dataset_path}")
        return
    
    total_fixed = 0
    
    for person_dir in dataset_dir.iterdir():
        if not person_dir.is_dir():
            continue
        
        print(f"\nFixing images for: {person_dir.name}")
        
        for img_path in person_dir.glob("*.jpg"):
            try:
                # Read image
                img = cv2.imread(str(img_path), cv2.IMREAD_COLOR)
                
                if img is None:
                    print(f"  Could not read: {img_path.name}")
                    continue
                
                # Convert to RGB then back to BGR for OpenCV
                if len(img.shape) == 3 and img.shape[2] == 4:
                    # Has alpha channel - remove it
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                
                # Re-save in standard format
                cv2.imwrite(str(img_path), img, [cv2.IMWRITE_JPEG_QUALITY, 95])
                total_fixed += 1
                print(f"  ✓ Fixed: {img_path.name}")
                
            except Exception as e:
                print(f"  ✗ Error fixing {img_path.name}: {e}")
    
    print(f"\nTotal images fixed: {total_fixed}")

if __name__ == "__main__":
    fix_images()
