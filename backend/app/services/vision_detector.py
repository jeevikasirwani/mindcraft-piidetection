import cv2
import numpy as np
from typing import List, Dict
from ..models import PIIEntity
import logging
import re

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
        
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"Could not read image: {image_path}")
            return []
        
        height, width = image.shape[:2]
        logger.info(f"Image dimensions: {width}x{height}")
        
        if ocr_data and ocr_data.get('success') and ocr_data.get('text_blocks'):
            logger.info("Using OCR data for PII detection")
            return self._detect_from_ocr(ocr_data.get('text_blocks'), width, height)
        else:
            logger.warning("No OCR data available - AI-based detection requires OCR")
            return []
    
    def _detect_from_ocr(self, text_blocks: List[Dict], width: int, height: int) -> List[PIIEntity]:
        if self.advanced_detector:
            logger.info("Using advanced PII detection with Presidio and spaCy")
            entities = self.advanced_detector.detect_pii_advanced(text_blocks)
            
            if entities:
                logger.info(f"Advanced PII detection found {len(entities)} entities")
                return entities
        
        logger.info("Using basic pattern matching as fallback")
        entities = []
        
        for block in text_blocks:
            text = block.get('text', '').strip()
            if not text:
                continue
            
            entity = self._detect_critical_pii_pattern(text, block)
            if entity:
                entities.append(entity)
        
        logger.info(f"Basic pattern detection found {len(entities)} PII entities")
        return entities
    
    def _detect_critical_pii_pattern(self, text: str, block: Dict) -> PIIEntity:
        text_lower = text.lower()
        
        # Aadhaar number patterns
        aadhaar_pattern = r'\b\d{4}\s?\d{4}\s?\d{4}\b'
        if re.search(aadhaar_pattern, text):
            return PIIEntity(
                text=text,
                entity_type="aadhaar_number",
                confidence=0.95,
                bbox=[block['x'], block['y'], block['width'], block['height']]
            )
        
        # Also check for Aadhaar numbers without spaces
        aadhaar_no_spaces = r'\b\d{12}\b'
        if re.search(aadhaar_no_spaces, text):
            return PIIEntity(
                text=text,
                entity_type="aadhaar_number",
                confidence=0.95,
                bbox=[block['x'], block['y'], block['width'], block['height']]
            )
        
        # PAN number pattern
        pan_pattern = r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b'
        if re.search(pan_pattern, text):
            return PIIEntity(
                text=text,
                entity_type="pan_number",
                confidence=0.95,
                bbox=[block['x'], block['y'], block['width'], block['height']]
            )
        
        # Phone number patterns (Indian mobile)
        phone_pattern = r'\b[6-9]\d{9}\b'
        if re.search(phone_pattern, text):
            return PIIEntity(
                text=text,
                entity_type="phone_number",
                confidence=0.9,
                bbox=[block['x'], block['y'], block['width'], block['height']]
            )
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.search(email_pattern, text):
            return PIIEntity(
                text=text,
                entity_type="email",
                confidence=0.9,
                bbox=[block['x'], block['y'], block['width'], block['height']]
            )
        
        # Date patterns (DOB)
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        if re.search(date_pattern, text):
            return PIIEntity(
                text=text,
                entity_type="date_time",
                confidence=0.85,
                bbox=[block['x'], block['y'], block['width'], block['height']]
            )
        
        # Name patterns (Full Name)
        name_pattern = r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'
        if re.search(name_pattern, text) and len(text.split()) >= 2:
            return PIIEntity(
                text=text,
                entity_type="person",
                confidence=0.8,
                bbox=[block['x'], block['y'], block['width'], block['height']]
            )
        
        # Name indicators (Hindi and English)
        name_indicators = ['name', 'नाम', 'jeevika', 'kamlesh', 'sirwani', 'father', 'mother', 'parent']
        if any(indicator in text_lower for indicator in name_indicators):
            return PIIEntity(
                text=text,
                entity_type="person",
                confidence=0.7,
                bbox=[block['x'], block['y'], block['width'], block['height']]
            )
        
        # Address patterns (comprehensive)
        address_keywords = [
            'address', 'पता', 'village', 'गाँव', 'city', 'शहर', 'street', 'road', 'lane', 
            'colony', 'sector', 'block', 'flat', 'apartment', 'house', 'building',
            'near', 'opposite', 'behind', 'in front of', 'next to', 'area', 'locality',
            'postal', 'pin', 'district', 'state', 'country'
        ]
        if any(keyword in text_lower for keyword in address_keywords):
            return PIIEntity(
                text=text,
                entity_type="location",
                confidence=0.75,
                bbox=[block['x'], block['y'], block['width'], block['height']]
            )
        
        # Address with numbers (house numbers, etc.)
        address_with_numbers = r'\b\d+\s+(?:street|road|lane|colony|sector|block|flat|apartment|house|building)\b'
        if re.search(address_with_numbers, text_lower):
            return PIIEntity(
                text=text,
                entity_type="location",
                confidence=0.8,
                bbox=[block['x'], block['y'], block['width'], block['height']]
            )
        
        return None 