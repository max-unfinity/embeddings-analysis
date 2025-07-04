import cv2
import numpy as np
from PIL import Image
import io
from pathlib import Path
from typing import Optional, Tuple
from .data_loader import data_loader

class ImageService:
    def __init__(self, images_dir: str = "data/images"):
        self.images_dir = Path(images_dir)
        
    def get_image_path(self, image_id: int) -> Optional[Path]:
        """Find image file by image_id"""
        if not data_loader.annotations:
            return None
            
        # Find image info in COCO annotations
        image_info = None
        for img in data_loader.annotations.get('images', []):
            if img['id'] == image_id:
                image_info = img
                break
                
        if not image_info:
            return None
            
        filename = image_info.get('file_name')
        if not filename:
            return None
            
        image_path = self.images_dir / filename
        
        # Try common extensions if exact filename doesn't exist
        if not image_path.exists():
            base_name = image_path.stem
            for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                alt_path = self.images_dir / f"{base_name}{ext}"
                if alt_path.exists():
                    return alt_path
                    
        return image_path if image_path.exists() else None
        
    def crop_detection(self, annotation_id: int, padding: int = 10) -> Optional[bytes]:
        """Crop detection region from image and return as bytes"""
        annotation = data_loader.get_annotation_by_id(annotation_id)
        if not annotation:
            return None
            
        image_id = annotation.get('image_id')
        bbox = annotation.get('bbox')  # [x, y, width, height] in COCO format
        
        if not image_id or not bbox:
            return None
            
        # Get image path
        image_path = self.get_image_path(image_id)
        if not image_path:
            return None
            
        try:
            # Load image
            image = cv2.imread(str(image_path))
            if image is None:
                return None
                
            # Get image dimensions
            img_height, img_width = image.shape[:2]
            
            # Extract bbox coordinates (COCO format: [x, y, width, height])
            x, y, w, h = bbox
            x, y, w, h = int(x), int(y), int(w), int(h)
            
            # Add padding and ensure within image bounds
            x1 = max(0, x - padding)
            y1 = max(0, y - padding)
            x2 = min(img_width, x + w + padding)
            y2 = min(img_height, y + h + padding)
            
            # Crop the region
            cropped = image[y1:y2, x1:x2]
            
            # Resize if too small (minimum 64x64)
            if cropped.shape[0] < 64 or cropped.shape[1] < 64:
                cropped = cv2.resize(cropped, (64, 64), interpolation=cv2.INTER_CUBIC)
            
            # Convert BGR to RGB
            cropped_rgb = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image and save to bytes
            pil_image = Image.fromarray(cropped_rgb)
            
            # Save to bytes buffer
            img_buffer = io.BytesIO()
            pil_image.save(img_buffer, format='JPEG', quality=90)
            img_buffer.seek(0)
            
            return img_buffer.getvalue()
            
        except Exception as e:
            print(f"Error cropping detection {annotation_id}: {e}")
            return None
            
    def create_placeholder_image(self, size: Tuple[int, int] = (64, 64)) -> bytes:
        """Create a placeholder image when crop fails"""
        # Create a simple gray placeholder
        placeholder = np.full((*size, 3), 128, dtype=np.uint8)
        
        # Add some pattern
        for i in range(0, size[0], 8):
            for j in range(0, size[1], 8):
                if (i // 8 + j // 8) % 2:
                    placeholder[i:i+4, j:j+4] = [160, 160, 160]
                    
        pil_image = Image.fromarray(placeholder)
        img_buffer = io.BytesIO()
        pil_image.save(img_buffer, format='JPEG', quality=90)
        img_buffer.seek(0)
        
        return img_buffer.getvalue()

# Global image service instance
image_service = ImageService()