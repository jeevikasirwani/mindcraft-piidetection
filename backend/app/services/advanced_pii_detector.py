import logging
import re
from typing import List, Dict
from ..models import PIIEntity

logger = logging.getLogger(__name__)

class AdvancedPIIDetector:
    def __init__(self):
        logger.info("Advanced PII Detector initializing")
        
        self.presidio_analyzer = None
        self.nlp = None
        
        try:
            from presidio_analyzer import AnalyzerEngine
            self.presidio_analyzer = AnalyzerEngine()
            logger.info("Presidio analyzer initialized")
        except Exception as e:
            logger.warning(f"Presidio not available: {e}")
        
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy NER initialized")
        except Exception as e:
            logger.warning(f"spaCy not available: {e}")
    
    def detect_pii_advanced(self, text_blocks: List[Dict]) -> List[PIIEntity]:
        all_entities = []
        
        if not self.presidio_analyzer:
            logger.warning("Presidio not available, using fallback detection")
            return self._fallback_detection(text_blocks)
        
        logger.info(f"Starting advanced PII detection on {len(text_blocks)} text blocks")
        
        for block in text_blocks:
            text = block.get('text', '').strip()
            if not text:
                continue
            
            presidio_entities = self._detect_with_presidio(text, block)
            all_entities.extend(presidio_entities)
            
            spacy_entities = self._detect_with_spacy(text, block)
            all_entities.extend(spacy_entities)
            
            custom_entities = self._detect_custom_patterns(text, block)
            all_entities.extend(custom_entities)
        
        unique_entities = self._deduplicate_entities(all_entities)
        
        logger.info(f"Advanced PII detection found {len(unique_entities)} unique entities")
        return unique_entities
    
    def _detect_with_presidio(self, text: str, block: Dict) -> List[PIIEntity]:
        entities = []
        
        try:
            results = self.presidio_analyzer.analyze(text=text, language='en')
            
            for result in results:
                entity_type = self._map_presidio_entity_type(result.entity_type)
                
                if entity_type:
                    entity = PIIEntity(
                        text=text[result.start:result.end],
                        entity_type=entity_type,
                        confidence=result.score,
                        bbox=[block['x'], block['y'], block['width'], block['height']]
                    )
                    entities.append(entity)
                    
                    logger.debug(f"Presidio detected {entity_type}: '{entity.text}' (confidence: {result.score:.2f})")
        
        except Exception as e:
            logger.error(f"Presidio detection failed: {e}")
        
        return entities
    
    def _detect_with_spacy(self, text: str, block: Dict) -> List[PIIEntity]:
        entities = []
        
        try:
            if self.nlp:
                doc = self.nlp(text)
                
                for ent in doc.ents:
                    entity_type = self._map_spacy_entity_type(ent.label_)
                    
                    if entity_type:
                        entity = PIIEntity(
                            text=ent.text,
                            entity_type=entity_type,
                            confidence=0.8,
                            bbox=[block['x'], block['y'], block['width'], block['height']]
                        )
                        entities.append(entity)
                        
                        logger.debug(f"spaCy detected {entity_type}: '{entity.text}'")
        
        except Exception as e:
            logger.error(f"spaCy detection failed: {e}")
        
        return entities
    
    def _detect_custom_patterns(self, text: str, block: Dict) -> List[PIIEntity]:
        entities = []
        
        patterns = {
            'aadhaar_number': [
                r'\b\d{4}\s?\d{4}\s?\d{4}\b',
                r'\b\d{4}-\d{4}-\d{4}\b',
                r'\b\d{12}\b',
            ],
            'pan_number': [
                r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b',
                r'\b[A-Z]{3}[A-Z0-9]{1}[0-9]{4}[A-Z]{1}\b',
            ],
            'phone_number': [
                r'\b[6-9]\d{9}\b',
                r'\b\d{3}-\d{3}-\d{4}\b',
                r'\b\d{5}-\d{5}\b',
            ],
            'email': [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            ],
            'date_time': [
                r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
                r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b',
                r'\b(?:DOB|Date of Birth|जन्म तिथि)\s*[:.]?\s*\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
            ],
            'person': [
                r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',
                r'\b(?:Name|नाम|Father|Mother|Parent)\s*[:.]?\s*[A-Z][a-z]+\s+[A-Z][a-z]+\b',
            ],
            'address': [
                r'\b(?:address|पता|village|गाँव|city|शहर|street|road|lane|colony|sector|block|flat|apartment|house|building)\b',
                r'\b\d+\s+(?:street|road|lane|colony|sector|block|flat|apartment|house|building)\b',
                r'\b(?:near|opposite|behind|in front of|next to)\s+[A-Za-z\s]+\b',
                r'\b(?:area|locality|postal|pin|district|state|country)\b',
            ]
        }
        
        for entity_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entity = PIIEntity(
                        text=match.group(),
                        entity_type=entity_type,
                        confidence=0.95,
                        bbox=[block['x'], block['y'], block['width'], block['height']]
                    )
                    entities.append(entity)
                    
                    logger.debug(f"Custom pattern detected {entity_type}: '{entity.text}'")
        
        return entities
    
    def _map_presidio_entity_type(self, presidio_type: str) -> str:
        mapping = {
            'PERSON': 'person',
            'EMAIL_ADDRESS': 'email',
            'PHONE_NUMBER': 'phone_number',
            'CREDIT_CARD': 'credit_card',
            'DATE_TIME': 'date_time',
            'URL': 'url',
            'IP_ADDRESS': 'ip_address',
            'IBAN_CODE': 'iban',
            'US_SSN': 'ssn',
            'US_PASSPORT': 'passport',
            'US_DRIVER_LICENSE': 'driver_license',
        }
        return mapping.get(presidio_type, presidio_type.lower())
    
    def _map_spacy_entity_type(self, spacy_type: str) -> str:
        mapping = {
            'PERSON': 'person',
            'DATE': 'date_time',
            'TIME': 'date_time',
            'MONEY': 'money',
            'CARDINAL': 'number',
        }
        return mapping.get(spacy_type, spacy_type.lower())
    
    def _deduplicate_entities(self, entities: List[PIIEntity]) -> List[PIIEntity]:
        if not entities:
            return []
        
        entities.sort(key=lambda x: x.confidence, reverse=True)
        
        unique_entities = []
        seen_texts = set()
        
        for entity in entities:
            if entity.text.lower() not in seen_texts:
                unique_entities.append(entity)
                seen_texts.add(entity.text.lower())
        
        return unique_entities
    
    def _fallback_detection(self, text_blocks: List[Dict]) -> List[PIIEntity]:
        entities = []
        
        for block in text_blocks:
            text = block.get('text', '').strip()
            if not text:
                continue
            
            custom_entities = self._detect_custom_patterns(text, block)
            entities.extend(custom_entities)
        
        return entities 