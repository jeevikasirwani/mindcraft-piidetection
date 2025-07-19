import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.ocr_service import OCRService
from app.services.vision_detector import VisionDetector

def test_all_pii_detection():
    print("Testing comprehensive PII detection for ALL required types...")
    print("Required PII types: Full Name, Address, Date of Birth, Aadhaar Number, Phone Number, Email Address")
    print("=" * 80)
    
    test_image = "uploads/1752912397_aadhar_front_.jpg"
    
    if not os.path.exists(test_image):
        print(f"Test image not found: {test_image}")
        return
    
    print(f"Testing with image: {test_image}")
    
    # Test OCR
    ocr = OCRService()
    ocr_result = ocr.extract_text_from_image(test_image)
    
    if ocr_result.get('success'):
        text_blocks = ocr_result.get('text_blocks', [])
        print(f"\nOCR extracted {len(text_blocks)} text blocks:")
        for i, block in enumerate(text_blocks):
            text = block.get('text', '')
            print(f"  Block {i}: '{text}' at ({block['x']}, {block['y']})")
    
    # Test PII Detection
    detector = VisionDetector()
    entities = detector.detect_pii_from_image(test_image, ocr_result)
    
    print(f"\nPII Detection Results:")
    print(f"Total entities found: {len(entities)}")
    
    # Group by entity type
    entity_types = {}
    for entity in entities:
        if entity.entity_type not in entity_types:
            entity_types[entity.entity_type] = []
        entity_types[entity.entity_type].append(entity)
    
    # Check each required PII type
    required_types = ['person', 'location', 'date_time', 'aadhaar_number', 'phone_number', 'email']
    
    print("\nDetection Summary:")
    for pii_type in required_types:
        count = len(entity_types.get(pii_type, []))
        status = "✅ DETECTED" if count > 0 else "❌ MISSING"
        print(f"  {pii_type.upper()}: {count} entities - {status}")
        
        if count > 0:
            for entity in entity_types[pii_type]:
                print(f"    - '{entity.text}' (confidence: {entity.confidence})")
    
    # Check for any additional types
    additional_types = [k for k in entity_types.keys() if k not in required_types]
    if additional_types:
        print(f"\nAdditional PII types detected:")
        for pii_type in additional_types:
            count = len(entity_types[pii_type])
            print(f"  {pii_type.upper()}: {count} entities")
            for entity in entity_types[pii_type]:
                print(f"    - '{entity.text}' (confidence: {entity.confidence})")

if __name__ == "__main__":
    test_all_pii_detection() 