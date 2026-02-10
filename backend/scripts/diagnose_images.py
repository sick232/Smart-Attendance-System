"""
Diagnose and fix image issues
"""

from PIL import Image
import numpy as np
from pathlib import Path

def diagnose_images():
    dataset_dir = Path("dataset/test_user")
    
    if not dataset_dir.exists():
        print("Dataset directory not found")
        return
    
    print("Checking images...\n")
    
    for img_path in sorted(dataset_dir.glob("*.jpg")):
        try:
            img = Image.open(img_path)
            arr = np.array(img)
            
            print(f"{img_path.name}:")
            print(f"  Mode: {img.mode}")
            print(f"  Size: {img.size}")
            print(f"  Array shape: {arr.shape}")
            print(f"  Array dtype: {arr.dtype}")
            print()
            
            # Fix the image
            if img.mode != 'RGB':
                print(f"  Converting {img.mode} to RGB...")
                img_rgb = img.convert('RGB')
            else:
                img_rgb = img
            
            # Ensure 8-bit
            arr_rgb = np.array(img_rgb, dtype=np.uint8)
            
            # Save fixed image
            fixed_img = Image.fromarray(arr_rgb, mode='RGB')
            fixed_img.save(img_path, 'JPEG', quality=95)
            print(f"  ✓ Fixed and saved\n")
            
        except Exception as e:
            print(f"Error with {img_path.name}: {e}\n")

if __name__ == "__main__":
    diagnose_images()
