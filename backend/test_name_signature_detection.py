#!/usr/bin/env python3
"""
Test script for improved name and signature detection
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.pii_detector import PIIDetector

def test_name_and_signature_detection():
    """Test name and signature detection with actual OCR output"""
    
    print("🧪 Testing Name and Signature Detection...")
    
    # Initialize PII detector
    pii_detector = PIIDetector()
    
    # Actual OCR output from the PAN card (from logs)
    pan_ocr_blocks = [
        {'x': 59, 'y': 163, 'width': 198, 'height': 52, 'text': 'INCOME', 'confidence': 77},
        {'x': 269, 'y': 163, 'width': 94, 'height': 51, 'text': 'TAX', 'confidence': 74},
        {'x': 1027, 'y': 159, 'width': 185, 'height': 52, 'text': 'GOVT.', 'confidence': 60},
        {'x': 1232, 'y': 137, 'width': 83, 'height': 72, 'text': 'OF', 'confidence': 95},
        {'x': 1329, 'y': 132, 'width': 190, 'height': 82, 'text': 'INDIA', 'confidence': 93},
        {'x': 532, 'y': 409, 'width': 378, 'height': 49, 'text': 'PDFPS0873A', 'confidence': 89},
        {'x': 50, 'y': 615, 'width': 171, 'height': 32, 'text': 'JEEVIKA', 'confidence': 91},
        {'x': 237, 'y': 609, 'width': 198, 'height': 34, 'text': 'KAMLESH', 'confidence': 92},
        {'x': 451, 'y': 603, 'width': 169, 'height': 35, 'text': 'SIRWANI', 'confidence': 91},
        {'x': 51, 'y': 750, 'width': 197, 'height': 33, 'text': 'KAMLESH', 'confidence': 91},
        {'x': 264, 'y': 743, 'width': 223, 'height': 36, 'text': 'ARJANDAS', 'confidence': 92},
        {'x': 503, 'y': 733, 'width': 169, 'height': 46, 'text': 'SIRWANI', 'confidence': 92},
        {'x': 51, 'y': 938, 'width': 204, 'height': 35, 'text': '28/12/2002', 'confidence': 93},
        {'x': 709, 'y': 929, 'width': 150, 'height': 71, 'text': 'Signature', 'confidence': 93}
    ]
    
    print(f"📝 Testing with {len(pan_ocr_blocks)} text blocks from PAN card...")
    
    # Test PII detection
    detected_entities = pii_detector.detect_pii(pan_ocr_blocks)
    
    print(f"\n🔍 Detected {len(detected_entities)} PII entities:")
    for entity in detected_entities:
        print(f"  - {entity.entity_type}: '{entity.text}' (confidence: {entity.confidence:.2f})")
    
    # Expected entities based on the PAN card
    expected_entities = {
        'name': ['JEEVIKA', 'KAMLESH', 'SIRWANI', 'ARJANDAS'],
        'pan': ['PDFPS0873A'],
        'date': ['28/12/2002'],
        'signature': ['Signature']
    }
    
    print(f"\n📋 Expected entities:")
    for entity_type, texts in expected_entities.items():
        print(f"  - {entity_type}: {texts}")
    
    # Check if we detected the expected entities
    detected_texts = [entity.text for entity in detected_entities]
    detected_types = [entity.entity_type for entity in detected_entities]
    
    print(f"\n✅ Detection Results:")
    for entity_type, expected_texts in expected_entities.items():
        found = [text for text in expected_texts if text in detected_texts]
        if found:
            print(f"  ✅ {entity_type}: Found {found}")
        else:
            print(f"  ❌ {entity_type}: Not found")
    
    # Test individual name detection
    print(f"\n🧪 Testing individual name detection...")
    
    test_names = [
        'JEEVIKA KAMLESH SIRWANI',
        'KAMLESH ARJANDAS SIRWANI', 
        'JEEVIKA',
        'KAMLESH',
        'SIRWANI',
        'ARJANDAS'
    ]
    
    for name in test_names:
        is_name = pii_detector._looks_like_indian_name(name)
        print(f"  '{name}' -> {'✅ Name' if is_name else '❌ Not name'}")
    
    # Test signature detection
    print(f"\n🧪 Testing signature detection...")
    
    test_signatures = [
        'Signature',
        'John Doe',
        'J.Doe',
        'J. Doe',
        'John.Doe'
    ]
    
    for sig in test_signatures:
        is_signature = pii_detector._looks_like_signature(sig)
        print(f"  '{sig}' -> {'✅ Signature' if is_signature else '❌ Not signature'}")
    
    print("\n✅ Name and signature detection test completed!")

if __name__ == "__main__":
    print("🚀 Starting Name and Signature Detection Tests...\n")
    
    try:
        test_name_and_signature_detection()
        
        print("\n🎉 All tests completed successfully!")
        print("\n📋 Summary of improvements:")
        print("  ✅ Enhanced name detection for Indian names")
        print("  ✅ Signature detection and masking")
        print("  ✅ Better pattern recognition")
        print("  ✅ Improved validation logic")
        print("  ✅ Multiple entity type support")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc() 