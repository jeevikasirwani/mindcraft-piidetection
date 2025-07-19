import cv2
import numpy as np
from typing import List
from ..models import PIIEntity
import logging

logger = logging.getLogger(__name__)

class ImageProcessor:
    def __init__(self):
        logger.info("Image Processor initialized")
    
    def mask_pii_areas(self, image_path: str, entities: List[PIIEntity]) -> str:
        logger.info(f"Masking {len(entities)} PII entities in {image_path}")
        
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"Could not read image: {image_path}")
            return image_path
        
        height, width = image.shape[:2]
        logger.info(f"Image dimensions: {width}x{height}")
        
        for entity in entities:
            if entity.bbox and len(entity.bbox) == 4:
                x, y, w, h = entity.bbox
                
                if 0 <= x < width and 0 <= y < height and w > 0 and h > 0:
                    self._apply_mask(image, x, y, w, h, entity.entity_type)
                    logger.debug(f"Masked {entity.entity_type}: '{entity.text}' at ({x}, {y}, {w}, {h})")
        
        output_path = image_path.replace('.jpg', '_masked.jpg').replace('.png', '_masked.png')
        cv2.imwrite(output_path, image)
        logger.info(f"Masked image saved to: {output_path}")
        
        return output_path
    
    def create_preview(self, image_path: str, entities: List[PIIEntity]) -> str:
        logger.info(f"Creating preview for {len(entities)} PII entities in {image_path}")
        
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"Could not read image: {image_path}")
            return image_path
        
        height, width = image.shape[:2]
        logger.info(f"Image dimensions: {width}x{height}")
        
        for entity in entities:
            if entity.bbox and len(entity.bbox) == 4:
                x, y, w, h = entity.bbox
                
                if 0 <= x < width and 0 <= y < height and w > 0 and h > 0:
                    # Draw red rectangle around detected PII
                    cv2.rectangle(image, (x, y), (x+w, y+h), (0, 0, 255), 2)
                    
                    # Add label above the box
                    label = self._get_entity_label(entity.entity_type)
                    cv2.putText(image, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                    
                    logger.debug(f"Preview box for {entity.entity_type}: '{entity.text}' at ({x}, {y}, {w}, {h})")
        
        output_path = image_path.replace('.jpg', '_preview.jpg').replace('.png', '_preview.png')
        cv2.imwrite(output_path, image)
        logger.info(f"Preview image saved to: {output_path}")
        
        return output_path
    
    def _apply_mask(self, image: np.ndarray, x: int, y: int, w: int, h: int, entity_type: str):
        roi = image[y:y+h, x:x+w]
        
        if roi.size == 0:
            return
        
        blurred_roi = cv2.GaussianBlur(roi, (99, 99), 30)
        image[y:y+h, x:x+w] = blurred_roi
        
        label = self._get_entity_label(entity_type)
        cv2.putText(image, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 0, 255), 2)
    
    def _get_entity_label(self, entity_type: str) -> str:
        labels = {
            'person': 'NAME',
            'aadhaar_number': 'AADHAAR',
            'pan_number': 'PAN',
            'phone_number': 'PHONE',
            'date_time': 'DOB',
            'location': 'ADDRESS',
            'email': 'EMAIL'
        }
        return labels.get(entity_type, entity_type.upper())