import cv2
import numpy as np
from typing import List
from ..models import PIIEntity
import logging

logger = logging.getLogger(__name__)

class SimpleImageProcessor:
    """Advanced image processor that masks PII with precise black rectangles"""
    
    def __init__(self):
        pass
    
    def mask_pii_on_image(self, image_path: str, entities: List[PIIEntity]) -> str:
        """Mask PII with precise black rectangles"""
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Could not read image")
            
            logger.info(f"🎨 Starting precise masking for {len(entities)} entities")
            
            # Apply black rectangles to each entity with precise positioning
            for i, entity in enumerate(entities):
                x, y, w, h = self._normalize_bbox(entity.bbox, image.shape)
                
                if w > 0 and h > 0:
                    # Ensure minimum size for visibility
                    w = max(w, 50)
                    h = max(h, 20)
                    
                    # Draw solid black rectangle with precise positioning
                    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 0), -1)
                    
                    # Add red border for visibility
                    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
                    
                    logger.info(f"✅ Masked {entity.entity_type}: '{entity.text}' at ({x},{y},{w},{h})")
                else:
                    logger.warning(f"⚠️ Invalid bbox for {entity.entity_type}: {entity.bbox}")
            
            # Save masked image
            masked_path = image_path.replace('.', '_masked.')
            cv2.imwrite(masked_path, image)
            
            logger.info(f"✅ Precise masking completed: {masked_path}")
            return masked_path
            
        except Exception as e:
            logger.error(f"❌ Masking failed: {e}")
            raise Exception(f"Error masking image: {str(e)}")
    
    def create_preview(self, image_path: str, entities: List[PIIEntity]) -> str:
        """Create preview with red boxes around detected PII"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Could not read image")
            
            logger.info(f"🎨 Creating preview for {len(entities)} entities")
            
            # Draw red rectangles around detected PII with precise positioning
            for entity in entities:
                x, y, w, h = self._normalize_bbox(entity.bbox, image.shape)
                
                if w > 0 and h > 0:
                    # Ensure minimum size for visibility
                    w = max(w, 50)
                    h = max(h, 20)
                    
                    # Draw red rectangle with precise positioning
                    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 3)
                    
                    # Add label with entity type
                    label = f"{entity.entity_type}: {entity.text}"
                    cv2.putText(image, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    
                    logger.info(f"✅ Preview box for {entity.entity_type}: '{entity.text}' at ({x},{y},{w},{h})")
            
            # Save preview
            preview_path = image_path.replace('.', '_preview.')
            cv2.imwrite(preview_path, image)
            
            logger.info(f"✅ Preview created: {preview_path}")
            return preview_path
            
        except Exception as e:
            logger.error(f"❌ Preview creation failed: {e}")
            raise Exception(f"Error creating preview: {str(e)}")
    
    def _normalize_bbox(self, bbox: List[int], image_shape) -> tuple:
        """Normalize bounding box coordinates with precise positioning"""
        x, y, w, h = bbox
        
        # Ensure coordinates are within image bounds
        x = max(0, x)
        y = max(0, y)
        w = min(w, image_shape[1] - x)
        h = min(h, image_shape[0] - y)
        
        # Add padding for better coverage
        padding = 15  # Increased padding for better coverage
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(w + 2*padding, image_shape[1] - x)
        h = min(h + 2*padding, image_shape[0] - y)
        
        # Ensure minimum size
        w = max(w, 50)
        h = max(h, 20)
        
        return x, y, w, h