import cv2
import numpy as np
from typing import List, Dict
from ..models import PIIEntity
import logging
import re
from .pii_patterns import get_pii_patterns, should_exclude_text

logger = logging.getLogger(__name__)

class VisionDetector:
    def __init__(self):
        logger.info("Vision Detector initialized")
        
        try:
            from .advanced_pii_detector import AdvancedPIIDetector
            self.advanced_detector = AdvancedPIIDetector()
            logger.info("Advanced PII Detector initialized")
        except Exception as e:
            logger.warning(f"Advanced PII Detector not available: {e}")
            self.advanced_detector = None
    
    def detect_pii_from_image(self, image_path: str, ocr_data: Dict = None) -> List[PIIEntity]:
        logger.info(f"PII detection on: {image_path}")
        
        # Image validation
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"Could not read image: {image_path}")
            return []
        
        height, width = image.shape[:2]
        logger.info(f"Image dimensions: {width}x{height}")
        
        # OCR data validation
        if ocr_data and ocr_data.get('success') and ocr_data.get('text_blocks'):
            logger.info("Using OCR data for PII detection")
            return self._detect_from_ocr(ocr_data.get('text_blocks'), width, height)
        else:
            logger.warning("No OCR data available - AI-based detection requires OCR")
            return []
    
    def _detect_from_ocr(self, text_blocks: List[Dict], width: int, height: int) -> List[PIIEntity]:
        # Try advanced detection first
        if self.advanced_detector:
            logger.info("Using advanced PII detection with Presidio")
            entities = self.advanced_detector.detect_pii_advanced(text_blocks)
            
            if entities:
                logger.info(f"Advanced PII detection found {len(entities)} entities")
                return entities
        
        # Fallback to basic patterns using modular patterns
        logger.info("Using basic pattern matching as fallback")
        entities = []
        
        for block in text_blocks:
            text = block.get('text', '').strip()
            if not text:
                continue
            
            entity = self._detect_basic_patterns(text, block)
            if entity:
                entities.append(entity)
        
        logger.info(f"Basic pattern detection found {len(entities)} PII entities")
        return entities
    
    def _detect_basic_patterns(self, text: str, block: Dict) -> PIIEntity:
        # Use modular patterns from pii_patterns.py
        if should_exclude_text(text):
            return None
        
        patterns = get_pii_patterns()
        
        # Check each pattern type
        for entity_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, text, re.IGNORECASE):
                    # Special handling for Aadhaar 4-digit patterns
                    if entity_type == 'aadhaar_number' and len(text.strip()) == 4 and text.isdigit():
                        confidence = 0.8
                    else:
                        confidence = 0.95 if entity_type in ['aadhaar_number', 'pan_number'] else 0.85
                    
                    return PIIEntity(
                        text=text,
                        entity_type=entity_type,
                        confidence=confidence,
                        bbox=[block['x'], block['y'], block['width'], block['height']]
                    )
        
        return None 