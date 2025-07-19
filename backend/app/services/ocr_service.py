import cv2
import numpy as np
from typing import Dict, List
import logging
import os

# Fix PIL ANTIALIAS issue for EasyOCR
try:
    from PIL import Image
    if not hasattr(Image, 'ANTIALIAS'):
        Image.ANTIALIAS = Image.LANCZOS
except ImportError:
    pass

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self):
        logger.info("OCR Service initialized")
        
        try:
            import easyocr
            self.easyocr_reader = easyocr.Reader(['en'])
            logger.info("EasyOCR initialized")
        except Exception as e:
            logger.warning(f"EasyOCR not available: {e}")
            self.easyocr_reader = None
        
        try:
            import pytesseract
            self.tesseract_available = True
            logger.info("Tesseract available")
        except Exception as e:
            logger.warning(f"Tesseract not available: {e}")
            self.tesseract_available = False
    
    def extract_text_from_image(self, image_path: str) -> Dict:
        logger.info(f"Extracting text from: {image_path}")
        
        if not os.path.exists(image_path):
            return {
                'success': False,
                'error': 'Image file not found',
                'method': 'none',
                'text_blocks': [],
                'total_blocks': 0
            }
        
        try:
            if self.easyocr_reader:
                return self._extract_with_easyocr(image_path)
            elif self.tesseract_available:
                return self._extract_with_tesseract(image_path)
            else:
                return {
                    'success': False,
                    'error': 'No OCR engine available',
                    'method': 'none',
                    'text_blocks': [],
                    'total_blocks': 0
                }
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'none',
                'text_blocks': [],
                'total_blocks': 0
            }
    
    def _extract_with_easyocr(self, image_path: str) -> Dict:
        try:
            results = self.easyocr_reader.readtext(image_path)
            
            text_blocks = []
            for (bbox, text, confidence) in results:
                if text.strip():
                    x_coords = [point[0] for point in bbox]
                    y_coords = [point[1] for point in bbox]
                    
                    x = int(min(x_coords))
                    y = int(min(y_coords))
                    width = int(max(x_coords) - x)
                    height = int(max(y_coords) - y)
                    
                    text_blocks.append({
                        'text': text.strip(),
                        'confidence': confidence,
                        'x': x,
                        'y': y,
                        'width': width,
                        'height': height
                    })
            
            logger.info(f"EasyOCR extracted {len(text_blocks)} text blocks")
            return {
                'success': True,
                'method': 'easyocr',
                'text_blocks': text_blocks,
                'total_blocks': len(text_blocks)
            }
        
        except Exception as e:
            logger.error(f"EasyOCR extraction failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'easyocr',
                'text_blocks': [],
                'total_blocks': 0
            }
    
    def _extract_with_tesseract(self, image_path: str) -> Dict:
        try:
            import pytesseract
            from PIL import Image
            
            image = Image.open(image_path)
            
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            text_blocks = []
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                if text and int(data['conf'][i]) > 30:
                    text_blocks.append({
                        'text': text,
                        'confidence': int(data['conf'][i]) / 100.0,
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i]
                    })
            
            logger.info(f"Tesseract extracted {len(text_blocks)} text blocks")
            return {
                'success': True,
                'method': 'tesseract',
                'text_blocks': text_blocks,
                'total_blocks': len(text_blocks)
            }
        
        except Exception as e:
            logger.error(f"Tesseract extraction failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'tesseract',
                'text_blocks': [],
                'total_blocks': 0
            }