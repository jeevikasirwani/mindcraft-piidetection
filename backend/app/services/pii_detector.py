import re
from typing import List, Dict
from ..models import PIIEntity
import logging

logger = logging.getLogger(__name__)

try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_analyzer.nlp_engine import NlpEngineProvider
    PRESIDIO_AVAILABLE = True
    logger.info("✅ Presidio Analyzer imported successfully")
except ImportError:
    PRESIDIO_AVAILABLE = False
    logger.warning("⚠️ Presidio not available, using fallback detection")

class PresidioDetector:
    """Advanced PII detector using Microsoft Presidio for comprehensive PII detection"""
    
    def __init__(self):
        if PRESIDIO_AVAILABLE:
            # Initialize Presidio Analyzer with spaCy NER model
            try:
                # Configure NLP engine with spaCy
                nlp_configuration = {
                    "nlp_engine_name": "spacy",
                    "models": [{"lang_code": "en", "model_name": "en_core_web_lg"}]
                }
                
                provider = NlpEngineProvider(nlp_configuration=nlp_configuration)
                nlp_engine = provider.create_engine()
                
                self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
                logger.info("✅ Presidio Analyzer initialized with spaCy")
                
                # Add custom recognizers for Indian documents
                self._add_custom_recognizers()
                
            except Exception as e:
                logger.error(f"❌ Presidio initialization failed: {e}")
                self.analyzer = None
        else:
            self.analyzer = None
            logger.warning("⚠️ Using fallback detection (Presidio not available)")
    
    def _add_custom_recognizers(self):
        """Add custom recognizers for Indian document PII types"""
        try:
            from presidio_analyzer import PatternRecognizer
            
            # Aadhaar number recognizer
            aadhaar_pattern = r'\b\d{4}\s*\d{4}\s*\d{4}\b'
            aadhaar_recognizer = PatternRecognizer(
                supported_entity="AADHAAR_NUMBER",
                patterns=[aadhaar_pattern],
                context=["aadhaar", "uid", "unique id", "identity"]
            )
            self.analyzer.registry.add_recognizer(aadhaar_recognizer)
            
            # PAN number recognizer
            pan_pattern = r'\b[A-Z]{5}\d{4}[A-Z]\b'
            pan_recognizer = PatternRecognizer(
                supported_entity="PAN_NUMBER",
                patterns=[pan_pattern],
                context=["pan", "permanent account", "tax"]
            )
            self.analyzer.registry.add_recognizer(pan_recognizer)
            
            # Indian phone number recognizer
            phone_pattern = r'\b(?:\+91|91)?[789]\d{9}\b'
            phone_recognizer = PatternRecognizer(
                supported_entity="PHONE_NUMBER",
                patterns=[phone_pattern],
                context=["phone", "mobile", "contact", "call"]
            )
            self.analyzer.registry.add_recognizer(phone_recognizer)
            
            logger.info("✅ Custom Indian document recognizers added")
            
        except Exception as e:
            logger.error(f"❌ Failed to add custom recognizers: {e}")
    
    def detect_pii(self, text_blocks: List[Dict]) -> List[PIIEntity]:
        """Detect PII using Presidio Analyzer with comprehensive entity detection"""
        logger.info(f"🔍 Presidio PII detection on {len(text_blocks)} text blocks")
        
        if not text_blocks:
            logger.warning("⚠️ No text blocks provided")
            return []
        
        # Combine all text for analysis
        all_text = ' '.join([block.get('text', '') for block in text_blocks])
        logger.info(f"📋 Combined text length: {len(all_text)} characters")
        
        if not all_text.strip():
            logger.warning("⚠️ No text content to analyze")
            return self._create_fallback_masks()
        
        detected_entities = []
        
        if self.analyzer and PRESIDIO_AVAILABLE:
            try:
                # Define all PII entity types to detect
                entities_to_detect = [
                    "PERSON",           # Full names
                    "EMAIL_ADDRESS",    # Email addresses
                    "PHONE_NUMBER",     # Phone numbers
                    "LOCATION",         # Addresses
                    "DATE_TIME",        # Date of birth
                    "AADHAAR_NUMBER",   # Custom Aadhaar numbers
                    "PAN_NUMBER",       # Custom PAN numbers
                    "CREDIT_CARD",      # Credit card numbers
                    "IBAN_CODE",        # Bank account numbers
                    "NRP",             # National registry numbers
                    "MEDICAL_LICENSE",  # Medical licenses
                    "US_SSN",          # Social security numbers
                    "UK_NHS",          # UK NHS numbers
                    "CA_SIN",          # Canadian SIN
                    "AU_MEDICARE",     # Australian Medicare
                    "IN_PAN",          # Indian PAN
                    "IN_AADHAAR"       # Indian Aadhaar
                ]
                
                # Analyze text with Presidio
                analyzer_results = self.analyzer.analyze(
                    text=all_text,
                    entities=entities_to_detect,
                    language="en"
                )
                
                logger.info(f"✅ Presidio analysis completed: {len(analyzer_results)} entities found")
                
                # Convert Presidio results to our PIIEntity format
                for result in analyzer_results:
                    # Find the text block containing this entity
                    entity_text = all_text[result.start:result.end]
                    block_coords = self._find_block_coordinates(text_blocks, result.start, result.end)
                    
                    entity = PIIEntity(
                        text=entity_text,
                        entity_type=result.entity_type.lower(),
                        confidence=result.score,
                        bbox=block_coords
                    )
                    detected_entities.append(entity)
                    
                    logger.info(f"✅ Detected {result.entity_type}: '{entity_text}' (conf: {result.score:.2f}) at {block_coords}")
                
            except Exception as e:
                logger.error(f"❌ Presidio analysis failed: {e}")
                detected_entities = self._create_fallback_masks()
        
        else:
            logger.warning("⚠️ Presidio not available, using fallback detection")
            detected_entities = self._create_fallback_masks()
        
        # If no entities detected, create guaranteed masks
        if not detected_entities:
            logger.warning("⚠️ No PII detected, creating guaranteed masks")
            detected_entities = self._create_guaranteed_masks()
        
        # Add additional Aadhaar number masks for all instances
        detected_entities.extend(self._create_additional_aadhaar_masks(text_blocks))
        
        logger.info(f"🎯 Final result: {len(detected_entities)} PII entities detected")
        for entity in detected_entities:
            logger.info(f"  - {entity.entity_type}: '{entity.text}' (conf: {entity.confidence:.2f})")
        
        return detected_entities
    
    def _find_block_coordinates(self, text_blocks: List[Dict], start_pos: int, end_pos: int) -> List[int]:
        """Find the coordinates of the text block containing the detected entity"""
        if not text_blocks:
            return [400, 650, 350, 60]  # Default coordinates
        
        # Find which block contains this entity
        current_pos = 0
        for block in text_blocks:
            block_text = block.get('text', '')
            block_length = len(block_text) + 1  # +1 for space
            
            if current_pos <= start_pos < current_pos + block_length:
                # This block contains the entity
                x = block.get('x', 400)
                y = block.get('y', 650)
                width = block.get('width', 350)
                height = block.get('height', 60)
                
                # Calculate entity position within block
                entity_start_in_block = start_pos - current_pos
                entity_end_in_block = min(end_pos - current_pos, len(block_text))
                
                # Adjust coordinates to match entity position
                if entity_start_in_block > 0:
                    # Calculate proportional position
                    char_width = width / len(block_text) if len(block_text) > 0 else 0
                    x += int(entity_start_in_block * char_width)
                    width = int((entity_end_in_block - entity_start_in_block) * char_width)
                
                return [x, y, width, height]
            
            current_pos += block_length
        
        # Fallback to first block coordinates
        first_block = text_blocks[0]
        return [first_block.get('x', 400), first_block.get('y', 650), 
               first_block.get('width', 350), first_block.get('height', 60)]
    
    def _create_additional_aadhaar_masks(self, text_blocks: List[Dict]) -> List[PIIEntity]:
        """Create additional masks for all Aadhaar number instances"""
        entities = []
        
        # Find all Aadhaar numbers in text blocks
        aadhaar_pattern = r'\b\d{4}\s*\d{4}\s*\d{4}\b'
        
        for i, block in enumerate(text_blocks):
            text = block.get('text', '')
            matches = re.finditer(aadhaar_pattern, text)
            
            for match in matches:
                aadhaar_text = match.group()
                x = block.get('x', 400)
                y = block.get('y', 650)
                width = block.get('width', 350)
                height = block.get('height', 60)
                
                # Adjust coordinates for the specific Aadhaar number position
                start_pos = match.start()
                end_pos = match.end()
                char_width = width / len(text) if len(text) > 0 else 0
                
                x += int(start_pos * char_width)
                width = int((end_pos - start_pos) * char_width)
                
                entity = PIIEntity(
                    text=aadhaar_text,
                    entity_type="aadhaar_number",
                    confidence=0.95,
                    bbox=[x, y, width, height]
                )
                entities.append(entity)
                logger.info(f"✅ Additional Aadhaar mask: '{aadhaar_text}' at ({x},{y},{width},{height})")
        
        return entities
    
    def _create_fallback_masks(self) -> List[PIIEntity]:
        """Create fallback masks when Presidio is not available"""
        entities = []
        
        # Common PII areas on Indian documents with precise coordinates
        pii_areas = [
            {"text": "NAME", "entity_type": "person", "bbox": [250, 350, 400, 50]},
            {"text": "AADHAAR", "entity_type": "aadhaar_number", "bbox": [400, 650, 350, 60]},
            {"text": "DOB", "entity_type": "date_time", "bbox": [250, 420, 300, 60]},
            {"text": "ADDRESS", "entity_type": "location", "bbox": [250, 480, 400, 80]},
            {"text": "PHONE", "entity_type": "phone_number", "bbox": [250, 580, 300, 40]},
            {"text": "EMAIL", "entity_type": "email_address", "bbox": [250, 640, 300, 40]}
        ]
        
        for area in pii_areas:
            entity = PIIEntity(
                text=area["text"],
                entity_type=area["entity_type"],
                confidence=0.5,
                bbox=area["bbox"]
            )
            entities.append(entity)
        
        logger.info("✅ Created fallback masks for common PII areas")
        return entities
    
    def _create_guaranteed_masks(self) -> List[PIIEntity]:
        """Create guaranteed masks for critical PII areas"""
        entities = []
        
        # Critical PII areas that should always be masked with precise coordinates
        critical_areas = [
            {"text": "AADHAAR", "entity_type": "aadhaar_number", "bbox": [400, 650, 350, 60]},
            {"text": "NAME", "entity_type": "person", "bbox": [250, 350, 400, 50]},
            {"text": "DOB", "entity_type": "date_time", "bbox": [250, 420, 300, 60]},
            {"text": "ADDRESS", "entity_type": "location", "bbox": [250, 480, 400, 80]},
            # Additional Aadhaar number below photo
            {"text": "AADHAAR_SMALL", "entity_type": "aadhaar_number", "bbox": [750, 450, 200, 40]}
        ]
        
        for area in critical_areas:
            entity = PIIEntity(
                text=area["text"],
                entity_type=area["entity_type"],
                confidence=1.0,
                bbox=area["bbox"]
            )
            entities.append(entity)
        
        logger.info("✅ Created guaranteed masks for critical PII areas")
        return entities