import cv2
import numpy as np
from typing import List, Dict, Tuple
from ..models import PIIEntity
import logging
import re
import os
from PIL import Image
import io

logger = logging.getLogger(__name__)

try:
    from google.cloud import vision
    from google.cloud.vision_v1 import types
    GOOGLE_VISION_AVAILABLE = True
    logger.info("✅ Google Vision API imported successfully")
except ImportError:
    GOOGLE_VISION_AVAILABLE = False
    logger.warning("⚠️ Google Vision API not available")

try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_analyzer.nlp_engine import NlpEngineProvider
    PRESIDIO_AVAILABLE = True
    logger.info("✅ Presidio Analyzer imported successfully")
except ImportError:
    PRESIDIO_AVAILABLE = False
    logger.warning("⚠️ Presidio not available")

class VisionDetector:
    """Advanced PII detector using Google Vision API + Presidio for comprehensive detection"""
    
    def __init__(self):
        self.client = None
        self.presidio_analyzer = None
        
        # Initialize Google Vision API
        if GOOGLE_VISION_AVAILABLE:
            try:
                # Check for credentials
                if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
                    self.client = vision.ImageAnnotatorClient()
                    logger.info("✅ Google Vision API client initialized")
                else:
                    logger.warning("⚠️ GOOGLE_APPLICATION_CREDENTIALS not set")
            except Exception as e:
                logger.error(f"❌ Google Vision API initialization failed: {e}")
        
        # Initialize Presidio
        if PRESIDIO_AVAILABLE:
            try:
                nlp_configuration = {
                    "nlp_engine_name": "spacy",
                    "models": [{"lang_code": "en", "model_name": "en_core_web_lg"}]
                }
                provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
                nlp_engine = provider.create_engine()
                self.presidio_analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
                self._add_custom_recognizers()
                logger.info("✅ Presidio Analyzer initialized")
            except Exception as e:
                logger.error(f"❌ Presidio initialization failed: {e}")
        
        # Enhanced PII patterns for Indian documents
        self.pii_patterns = {
            'aadhaar': r'\b\d{4}\s*\d{4}\s*\d{4}\b',
            'pan': r'\b[A-Z]{5}\d{4}[A-Z]\b',
            'phone': r'\b(?:\+91|91)?[789]\d{9}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b',
            'name': r'\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
        }
        
        logger.info("✅ Vision Detector initialized with Google Vision + Presidio")
    
    def _add_custom_recognizers(self):
        """Add custom recognizers for Indian document PII types"""
        try:
            from presidio_analyzer import PatternRecognizer
            
            # Enhanced Aadhaar number recognizer
            aadhaar_pattern = r'\b\d{4}\s*\d{4}\s*\d{4}\b'
            aadhaar_recognizer = PatternRecognizer(
                supported_entity="AADHAAR_NUMBER",
                patterns=[aadhaar_pattern],
                context=["aadhaar", "uid", "unique id", "identity", "आधार"]
            )
            self.presidio_analyzer.registry.add_recognizer(aadhaar_recognizer)
            
            # Enhanced PAN number recognizer
            pan_pattern = r'\b[A-Z]{5}\d{4}[A-Z]\b'
            pan_recognizer = PatternRecognizer(
                supported_entity="PAN_NUMBER",
                patterns=[pan_pattern],
                context=["pan", "permanent account", "tax", "पैन"]
            )
            self.presidio_analyzer.registry.add_recognizer(pan_recognizer)
            
            # Indian name recognizer
            name_pattern = r'\b[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
            name_recognizer = PatternRecognizer(
                supported_entity="PERSON",
                patterns=[name_pattern],
                context=["name", "नाम", "father", "पिता"]
            )
            self.presidio_analyzer.registry.add_recognizer(name_recognizer)
            
            logger.info("✅ Custom Indian document recognizers added")
            
        except Exception as e:
            logger.error(f"❌ Failed to add custom recognizers: {e}")
    
    def detect_pii_from_image(self, image_path: str) -> List[PIIEntity]:
        """Detect PII using Google Vision API + Presidio for comprehensive detection"""
        logger.info(f"🔍 Advanced PII detection on: {image_path}")
        
        detected_entities = []
        
        if self.client and GOOGLE_VISION_AVAILABLE:
            # Use Google Vision API for OCR and text detection
            vision_entities = self._detect_with_google_vision(image_path)
            detected_entities.extend(vision_entities)
        
        # Fallback to template-based detection if Google Vision fails
        if not detected_entities:
            logger.info("🔄 Falling back to template-based detection")
            detected_entities = self._detect_with_templates(image_path)
        
        # Remove duplicates and validate
        unique_entities = self._remove_duplicates(detected_entities)
        
        logger.info(f"🎯 Final result: {len(unique_entities)} PII entities detected")
        return unique_entities
    
    def _detect_with_google_vision(self, image_path: str) -> List[PIIEntity]:
        """Detect PII using Google Vision API OCR + Presidio analysis"""
        entities = []
        
        try:
            # Read image file
            with open(image_path, 'rb') as image_file:
                content = image_file.read()
            
            # Create image object
            image = types.Image(content=content)
            
            # Perform OCR
            response = self.client.text_detection(image=image)
            texts = response.text_annotations
            
            if not texts:
                logger.warning("⚠️ No text detected in image")
                return entities
            
            # Extract all text blocks with coordinates
            text_blocks = []
            for text in texts[1:]:  # Skip the first one (full text)
                vertices = text.bounding_poly.vertices
                x_coords = [vertex.x for vertex in vertices]
                y_coords = [vertex.y for vertex in vertices]
                
                text_blocks.append({
                    'text': text.description,
                    'x': min(x_coords),
                    'y': min(y_coords),
                    'width': max(x_coords) - min(x_coords),
                    'height': max(y_coords) - min(y_coords)
                })
            
            logger.info(f"📋 Google Vision detected {len(text_blocks)} text blocks")
            
            # Use Presidio to analyze detected text
            if self.presidio_analyzer and PRESIDIO_AVAILABLE:
                entities = self._analyze_with_presidio(text_blocks)
            
            # Add additional pattern-based detection
            pattern_entities = self._detect_patterns_in_blocks(text_blocks)
            entities.extend(pattern_entities)
            
        except Exception as e:
            logger.error(f"❌ Google Vision detection failed: {e}")
        
        return entities
    
    def _analyze_with_presidio(self, text_blocks: List[Dict]) -> List[PIIEntity]:
        """Analyze text blocks with Presidio for PII detection"""
        entities = []
        
        try:
            # Combine all text for analysis
            all_text = ' '.join([block.get('text', '') for block in text_blocks])
            
            if not all_text.strip():
                return entities
            
            # Define entities to detect
            entities_to_detect = [
                "PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "LOCATION", 
                "DATE_TIME", "AADHAAR_NUMBER", "PAN_NUMBER", "CREDIT_CARD",
                "IBAN_CODE", "NRP", "MEDICAL_LICENSE", "US_SSN", "UK_NHS",
                "CA_SIN", "AU_MEDICARE", "IN_PAN", "IN_AADHAAR"
            ]
            
            # Analyze with Presidio
            analyzer_results = self.presidio_analyzer.analyze(
                text=all_text,
                entities=entities_to_detect,
                language="en"
            )
            
            # Convert Presidio results to PIIEntity format
            for result in analyzer_results:
                entity_text = all_text[result.start:result.end]
                block_coords = self._find_block_coordinates(text_blocks, result.start, result.end)
                
                entity = PIIEntity(
                    text=entity_text,
                    entity_type=result.entity_type.lower(),
                    confidence=result.score,
                    bbox=block_coords
                )
                entities.append(entity)
                
                logger.info(f"✅ Presidio detected {result.entity_type}: '{entity_text}' (conf: {result.score:.2f})")
        
        except Exception as e:
            logger.error(f"❌ Presidio analysis failed: {e}")
        
        return entities
    
    def _detect_patterns_in_blocks(self, text_blocks: List[Dict]) -> List[PIIEntity]:
        """Detect PII patterns in text blocks"""
        entities = []
        
        for block in text_blocks:
            text = block.get('text', '')
            
            # Check each pattern
            for pattern_name, pattern in self.pii_patterns.items():
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    matched_text = match.group()
                    x = block.get('x', 0)
                    y = block.get('y', 0)
                    width = block.get('width', 0)
                    height = block.get('height', 0)
                    
                    # Calculate position within block
                    start_pos = match.start()
                    end_pos = match.end()
                    char_width = width / len(text) if len(text) > 0 else 0
                    
                    entity_x = x + int(start_pos * char_width)
                    entity_width = int((end_pos - start_pos) * char_width)
                    
                    entity = PIIEntity(
                        text=matched_text,
                        entity_type=pattern_name,
                        confidence=0.9,
                        bbox=[entity_x, y, entity_width, height]
                    )
                    entities.append(entity)
                    
                    logger.info(f"✅ Pattern detected {pattern_name}: '{matched_text}' at ({entity_x},{y})")
        
        return entities
    
    def _find_block_coordinates(self, text_blocks: List[Dict], start_pos: int, end_pos: int) -> List[int]:
        """Find coordinates of text block containing the entity"""
        if not text_blocks:
            return [400, 650, 350, 60]
        
        current_pos = 0
        for block in text_blocks:
            block_text = block.get('text', '')
            block_length = len(block_text) + 1
            
            if current_pos <= start_pos < current_pos + block_length:
                x = block.get('x', 400)
                y = block.get('y', 650)
                width = block.get('width', 350)
                height = block.get('height', 60)
                
                # Calculate entity position within block
                entity_start_in_block = start_pos - current_pos
                entity_end_in_block = min(end_pos - current_pos, len(block_text))
                
                if entity_start_in_block > 0:
                    char_width = width / len(block_text) if len(block_text) > 0 else 0
                    x += int(entity_start_in_block * char_width)
                    width = int((entity_end_in_block - entity_start_in_block) * char_width)
                
                return [x, y, width, height]
            
            current_pos += block_length
        
        # Fallback
        first_block = text_blocks[0]
        return [first_block.get('x', 400), first_block.get('y', 650), 
               first_block.get('width', 350), first_block.get('height', 60)]
    
    def _detect_with_templates(self, image_path: str) -> List[PIIEntity]:
        """Enhanced template-based detection with better coordinate mapping"""
        entities = []
        
        # Read image to get dimensions
        image = cv2.imread(image_path)
        if image is None:
            logger.error(f"❌ Could not read image: {image_path}")
            return entities
        
        height, width = image.shape[:2]
        logger.info(f"📏 Image dimensions: {width}x{height}")
        
        # Enhanced Aadhaar card template
        if self._is_aadhaar_card(image_path):
            logger.info("📋 Detected Aadhaar card - applying enhanced template")
            
            # Main Aadhaar number (bottom center) - more precise
            entities.append(PIIEntity(
                text="AADHAAR_MAIN",
                entity_type="aadhaar_number",
                confidence=1.0,
                bbox=[int(width*0.29), int(height*0.78), int(width*0.42), int(height*0.09)]
            ))
            
            # Small Aadhaar number (below photo) - corrected position
            entities.append(PIIEntity(
                text="AADHAAR_SMALL",
                entity_type="aadhaar_number",
                confidence=1.0,
                bbox=[int(width*0.69), int(height*0.58), int(width*0.25), int(height*0.06)]
            ))
            
            # Name area - more precise
            entities.append(PIIEntity(
                text="NAME",
                entity_type="person",
                confidence=0.95,
                bbox=[int(width*0.24), int(height*0.38), int(width*0.42), int(height*0.07)]
            ))
            
            # DOB area - includes the actual date value
            entities.append(PIIEntity(
                text="DOB_VALUE",
                entity_type="date_time",
                confidence=0.95,
                bbox=[int(width*0.24), int(height*0.48), int(width*0.31), int(height*0.07)]
            ))
            
            # Gender area - more precise
            entities.append(PIIEntity(
                text="GENDER",
                entity_type="person",
                confidence=0.9,
                bbox=[int(width*0.24), int(height*0.54), int(width*0.22), int(height*0.05)]
            ))
        
        # Enhanced PAN card template
        elif self._is_pan_card(image_path):
            logger.info("📋 Detected PAN card - applying enhanced template")
            
            # PAN number area - corrected
            entities.append(PIIEntity(
                text="PAN_NUMBER",
                entity_type="pan_number",
                confidence=1.0,
                bbox=[int(width*0.29), int(height*0.48), int(width*0.42), int(height*0.08)]
            ))
            
            # Name area - more precise
            entities.append(PIIEntity(
                text="NAME",
                entity_type="person",
                confidence=0.95,
                bbox=[int(width*0.24), int(height*0.38), int(width*0.42), int(height*0.07)]
            ))
            
            # Father's name area - new detection
            entities.append(PIIEntity(
                text="FATHER_NAME",
                entity_type="person",
                confidence=0.9,
                bbox=[int(width*0.24), int(height*0.45), int(width*0.42), int(height*0.07)]
            ))
            
            # DOB area - includes actual date value
            entities.append(PIIEntity(
                text="DOB_VALUE",
                entity_type="date_time",
                confidence=0.95,
                bbox=[int(width*0.24), int(height*0.58), int(width*0.31), int(height*0.07)]
            ))
            
            # Signature area - new detection
            entities.append(PIIEntity(
                text="SIGNATURE",
                entity_type="signature",
                confidence=0.85,
                bbox=[int(width*0.24), int(height*0.65), int(width*0.22), int(height*0.08)]
            ))
        
        # Generic document template
        else:
            logger.info("📋 Generic document - applying basic template")
            
            # Generic text areas
            entities.append(PIIEntity(
                text="GENERIC_TEXT_1",
                entity_type="text",
                confidence=0.7,
                bbox=[int(width*0.2), int(height*0.3), int(width*0.6), int(height*0.1)]
            ))
            
            entities.append(PIIEntity(
                text="GENERIC_TEXT_2",
                entity_type="text",
                confidence=0.7,
                bbox=[int(width*0.2), int(height*0.5), int(width*0.6), int(height*0.1)]
            ))
        
        return entities
    
    def _is_aadhaar_card(self, image_path: str) -> bool:
        """Enhanced Aadhaar card detection"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return False
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Check image proportions
            height, width = gray.shape
            aspect_ratio = width / height
            
            # Aadhaar cards are typically wider than tall
            if 1.5 < aspect_ratio < 2.5:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error checking Aadhaar card: {e}")
            return False
    
    def _is_pan_card(self, image_path: str) -> bool:
        """Enhanced PAN card detection"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                return False
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Check image proportions
            height, width = gray.shape
            aspect_ratio = width / height
            
            # PAN cards are typically wider than tall
            if 1.3 < aspect_ratio < 2.0:
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Error checking PAN card: {e}")
            return False
    
    def _remove_duplicates(self, entities: List[PIIEntity]) -> List[PIIEntity]:
        """Remove duplicate entities based on text and position"""
        unique_entities = []
        seen = set()
        
        for entity in entities:
            # Create a unique key based on text and position
            key = f"{entity.text}_{entity.bbox[0]}_{entity.bbox[1]}"
            
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities 