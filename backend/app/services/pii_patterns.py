


ORG_KEYWORDS = [
    'government', 'of india', 'uidai', 'unique identification authority', 
    'ministry', 'department', 'भारत सरकार', 'भारत', 'सरकार',
    'government of india', 'government of', 'of india',
    'permanent account number card', 'स्थायी लेखा संख्या कार्ड',
    'income tax department', 'आयकर विभाग', 'income tax',
    'card', 'कार्ड', 'document', 'documentation', 'form',
    'permanent account number', 'स्थायी लेखा संख्या',
    'unique identification', 'unique id', 'identification',
    'authority', 'authority of india', 'भारत सरकार का',
    'स्थायी लेखा संख्या कार्ड', 'स्थायी लेखा', 'लेखा संख्या',
    'भारतीय विशिष्ट पहचान प्राधिकरण', 'unique identification authority of india',
    'bhartiya vishisht pehchan pradhikaran', 'vishisht pehchan pradhikaran'
]

HINDI_EXCLUSIONS = [
    'स्थायी लेखा संख्या कार्ड',
    'स्थायी लेखा संख्या',
    'लेखा संख्या कार्ड',
    'स्थायी लेखा',
    'लेखा संख्या'
]

# PII Detection Patterns
PII_PATTERNS = {
    'aadhaar_number': [
        r'\b\d{4}\s?\d{4}\s?\d{4}\b',  # 1234 5678 9012
        r'\b\d{12}\b',                  # 123456789012
        r'\b\d{4}\b',                   # Last 4 digits (if standalone)
    ],
    
    'pan_number': [
        r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b',  # ABCDE1234F
    ],
    
    'phone_number': [
        r'\b[6-9]\d{9}\b',              # Indian mobile: 9876543210
        r'\b\+91[6-9]\d{9}\b',          # With country code: +919876543210
    ],
    
    'pincode': [
        r'\b\d{6}\b',                   # Standard 6-digit: 400001
        r'\bPIN\s*:?\s*\d{6}\b',        # PIN: 400001
        r'\bPincode\s*:?\s*\d{6}\b',    # Pincode: 400001
        r'\bपिन\s*:?\s*\d{6}\b',        # पिन: 400001
    ],
    
    'email': [
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    ],
    
    'date_time': [
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',  # DD/MM/YYYY or DD-MM-YYYY
        r'\b\d{1,2}\s+[A-Za-z]{3,9}\s+\d{2,4}\b',  # 15 March 2023
    ],
    
    'person': [
        # English names
        r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # John Smith
        r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # John Michael Smith
        r'\b(?:Mr|Mrs|Ms|Dr|Prof|Shri|Smt)\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # With titles
        
        # Names with labels
        r'\b(?:Name|नाम|Father|Mother|Parent)\s*[:.]?\s*[A-Z][a-z]+\s+[A-Z][a-z]+\b',
        
        # Hindi names
        r'\b[अ-ह]+\s+[अ-ह]+\b',  # राहुल शर्मा
        r'\b(?:Name|नाम|Father|पिता|Mother|माता|Parent|माता-पिता)\s*[:.]?\s*[अ-ह]+\s+[अ-ह]+\b',
        r'\b[अ-ह]{2,}\s+[अ-ह]{2,}\s+[अ-ह]{2,}\b',  # Three-word Hindi names
        r'\b(?:श्री|श्रीमती|डॉ\.|प्रो\.|कैप्टन|मेजर|कर्नल)\s+[अ-ह]+\s+[अ-ह]+\b',  # With titles
    ],
    
    'address': [
        # Address components with context
        r'\b(?:address|पता|village|गाँव|city|शहर|street|road|lane|colony|sector|block|flat|apartment|house|building|park)\s*[:.]?\s*[A-Za-z0-9\s,.-]+\b',
        
        # Wing patterns (A-wing, B-wing, etc.)
        r'\b[A-Z]\s*[-]?\s*wing\b',  # A-wing, A wing
        r'\bwing\s*[-]?\s*[A-Z]\b',  # wing-A, wing A
        
        # Society names and complexes
        r'\b(?:society|complex|residency|apartments|colony|park|garden|nagar|vihar|ashram|colony)\s+[A-Za-z\s]+\b',
        
        # Floor patterns
        r'\b(?:floor|level)\s*[-]?\s*[0-9A-Z]+\b',  # 2nd floor, floor 3
        r'\b[0-9A-Z]+\s*[-]?\s*(?:floor|level)\b',  # floor 2, level 3
        
        # Flat/Apartment patterns
        r'\b(?:flat|apartment|unit)\s*[-]?\s*[A-Z0-9]+\b',  # flat A-101
        r'\b[A-Z0-9]+\s*[-]?\s*(?:flat|apartment|unit)\b',  # A-101 flat
        
        # Building patterns
        r'\b(?:building|tower|block)\s*[-]?\s*[A-Z0-9]+\b',  # building A
        r'\b[A-Z0-9]+\s*[-]?\s*(?:building|tower|block)\b',  # A building
        
        # Directional patterns
        r'\b(?:near|opposite|behind|in front of|next to|beside)\s+[A-Za-z\s]+\b',
        
        # Address labels
        r'\b(?:area|locality|postal|pin|district|state|country)\s*[:.]?\s*[A-Za-z\s]+\b',
        
        # Relationship patterns
        r'\b(?:d/o|s/o|w/o|h/o|daughter of|son of|wife of|husband of)\s+[A-Za-z\s]+\b',
        
        # Number patterns
        r'\b(?:flat no|flat number|apartment no|apartment number|house no|house number)\s*[:.]?\s*[A-Z0-9]+\b',
        
        # Indian cities
        r'\b(?:pune|mumbai|delhi|bangalore|chennai|kolkata|hyderabad|ahmedabad|jaipur|surat|nagpur|indore|thane|bhopal|visakhapatnam|patna|vadodara|ghaziabad|lucknow|agra|nashik|faridabad|meerut|rajkot|kalyan|vasai|aurangabad|noida|howrah|coimbatore|raipur|jabalpur|gwalior|vijayawada|jodhpur|madurai|guwahati|chandigarh|thiruvananthapuram|srinagar|amritsar|allahabad|ranchi)\b',
        
        # Indian states
        r'\b(?:maharashtra|karnataka|tamil nadu|west bengal|telangana|andhra pradesh|punjab|haryana|gujarat|rajasthan|uttar pradesh|bihar|jharkhand|odisha|chhattisgarh|madhya pradesh|himachal pradesh|uttarakhand|sikkim|arunachal pradesh|assam|manipur|meghalaya|mizoram|nagaland|tripura|goa|kerala)\b',
        
        # Common address words
        r'\b(?:wing|floor|building|complex|society|colony|area|locality|park|garden|nagar|vihar|ashram|residency|apartments)\b',
    ]
}

def should_exclude_text(text: str) -> bool:
    
    text_lower = text.lower()
    text_stripped = text.strip()
    

    if any(keyword in text_lower for keyword in ORG_KEYWORDS):
        return True
    
    
    for exclusion in HINDI_EXCLUSIONS:
        if exclusion in text_stripped or exclusion in text:
            return True
    
    return False

def get_pii_patterns():
    
    return PII_PATTERNS

def get_org_keywords():

    return ORG_KEYWORDS

def get_hindi_exclusions():
   
    return HINDI_EXCLUSIONS 