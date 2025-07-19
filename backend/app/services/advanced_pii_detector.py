import logging
import re
from typing import List, Dict
from ..models import PIIEntity
from .pii_patterns import get_pii_patterns, should_exclude_text

logger = logging.getLogger(__name__)

class AdvancedPIIDetector:
    def __init__(self):
        logger.info("Advanced PII Detector initializing")
        
        self.presidio_analyzer = None
        
        try:
            from presidio_analyzer import AnalyzerEngine
            from presidio_analyzer.nlp_engine import NlpEngineProvider
            
            # Configure Presidio for both English and Hindi
            configuration = {
                "nlp_engine_name": "spacy",
                "models": [
                    {"lang_code": "en", "model_name": "en_core_web_lg"},
                    {"lang_code": "hi", "model_name": "xx_ent_wiki_sm"},  # Hindi support
                ],
            }
            
            # Create NLP engine with multi-language support
            provider = NlpEngineProvider(nlp_configuration=configuration)
            nlp_engine = provider.create_engine()
            
            # Initialize analyzer with English and Hindi support
            self.presidio_analyzer = AnalyzerEngine(
                nlp_engine=nlp_engine,
                supported_languages=["en", "hi"]
            )
            logger.info("Presidio analyzer initialized (English + Hindi)")
            
        except Exception as e:
            logger.warning(f"Presidio not available: {e}")
    
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
            
            custom_entities = self._detect_custom_patterns(text, block)
            all_entities.extend(custom_entities)
        
        unique_entities = self._deduplicate_entities(all_entities)
        
        logger.info(f" PII detection found {len(unique_entities)} unique entities")
        return unique_entities
    
    def _detect_with_presidio(self, text: str, block: Dict) -> List[PIIEntity]:
        entities = []
        
        try:
          
            languages = ['hi', 'en']
            
            for lang in languages:
                try:
                    results = self.presidio_analyzer.analyze(text=text, language=lang)
                    
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
                            
                            logger.debug(f"Presidio ({lang}) detected {entity_type}: '{entity.text}' (confidence: {result.score:.2f})")
                    
                    # If we found entities in this language, don't try the other
                    if entities:
                        break
                        
                except Exception as e:
                    logger.debug(f"Presidio detection failed for {lang}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Presidio detection failed: {e}")
        
        return entities
    
    def _detect_custom_patterns(self, text: str, block: Dict) -> List[PIIEntity]:
        entities = []
        
        # Check if text should be excluded
        if should_exclude_text(text):
            return entities
        
        # Get patterns from modular file
        patterns = get_pii_patterns()
        
        for entity_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    if entity_type == 'aadhaar_number' and len(match.group().strip()) == 4 and match.group().isdigit():
                        if len(text.strip()) == 4:
                            entity = PIIEntity(
                                text=match.group(),
                                entity_type=entity_type,
                                confidence=0.8,
                                bbox=[block['x'], block['y'], block['width'], block['height']]
                            )
                            entities.append(entity)
                    else:
                        entity = PIIEntity(
                            text=match.group(),
                            entity_type=entity_type,
                            confidence=0.95,
                            bbox=[block['x'], block['y'], block['width'], block['height']]
                        )
                        entities.append(entity)
        
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
            'LOCATION': 'location',  # May catch some pincodes
        }
        return mapping.get(presidio_type, presidio_type.lower())
    
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