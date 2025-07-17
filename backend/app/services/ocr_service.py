import pytesseract
import cv2
import numpy as np
import re
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class EnhancedOCRService:
    """Enhanced OCR service with multiple preprocessing techniques for better text extraction"""
    
    def __init__(self):
        # Configure Tesseract path (adjust based on your system)
        try:
            # Windows path
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        except:
            try:
                # Linux/Mac path
                pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
            except:
                # Use system PATH
                pass
        
        # OCR configurations for different scenarios
        self.configs = {
            'default': r'--oem 3 --psm 6',
            'single_line': r'--oem 3 --psm 8',
            'numbers_only': r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789 ',
            'text_only': r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz ',
            'general': r'--oem 3 --psm 11'
        }
    
    def extract_text_from_image(self, image_path: str) -> Dict[str, any]:
        """Enhanced text extraction with multiple OCR approaches"""
        try:
            logger.info(f"🔍 Starting enhanced OCR on: {image_path}")
            
            # Read original image
            original_image = cv2.imread(image_path)
            if original_image is None:
                return self._error_response(f"Could not read image: {image_path}")
            
            logger.info(f"📷 Image loaded: {original_image.shape}")
            
            # Try multiple preprocessing approaches
            all_text_blocks = []
            processing_methods = []
            
            # Method 1: Standard OCR on original image
            try:
                standard_blocks = self._extract_standard(original_image)
                all_text_blocks.extend(standard_blocks)
                processing_methods.append('standard')
                logger.info(f"✅ Standard OCR: {len(standard_blocks)} blocks")
            except Exception as e:
                logger.error(f"Standard OCR failed: {e}")
            
            # Method 2: Enhanced preprocessing
            try:
                enhanced_blocks = self._extract_enhanced(original_image)
                all_text_blocks.extend(enhanced_blocks)
                processing_methods.append('enhanced')
                logger.info(f"✅ Enhanced OCR: {len(enhanced_blocks)} blocks")
            except Exception as e:
                logger.error(f"Enhanced OCR failed: {e}")
            
            # Method 3: Specialized for numbers (Aadhaar detection)
            try:
                number_blocks = self._extract_numbers(original_image)
                all_text_blocks.extend(number_blocks)
                processing_methods.append('numbers')
                logger.info(f"✅ Number extraction: {len(number_blocks)} blocks")
            except Exception as e:
                logger.error(f"Number OCR failed: {e}")
            
            # Method 4: High contrast binary
            try:
                binary_blocks = self._extract_binary(original_image)
                all_text_blocks.extend(binary_blocks)
                processing_methods.append('binary')
                logger.info(f"✅ Binary OCR: {len(binary_blocks)} blocks")
            except Exception as e:
                logger.error(f"Binary OCR failed: {e}")
            
            # Merge and deduplicate all results
            final_blocks = self._merge_and_deduplicate(all_text_blocks)
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(final_blocks)
            
            logger.info(f"🎯 Final result: {len(final_blocks)} unique text blocks")
            for block in final_blocks:
                logger.info(f"  📝 '{block['text']}' (conf: {block['confidence']}, method: {block.get('method', 'unknown')})")
            
            return {
                'success': True,
                'text_blocks': final_blocks,
                'full_text': ' '.join([block['text'] for block in final_blocks]),
                'ocr_score': quality_score,
                'processing_methods': processing_methods
            }
            
        except Exception as e:
            logger.error(f"❌ OCR error: {str(e)}")
            return self._error_response(f"OCR failed: {str(e)}")
    
    def _extract_standard(self, image: np.ndarray) -> List[Dict]:
        """Standard OCR extraction"""
        # Convert to RGB for Tesseract
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Run OCR
        data = pytesseract.image_to_data(rgb_image, config=self.configs['default'], 
                                       output_type=pytesseract.Output.DICT)
        
        return self._process_ocr_data(data, 'standard', min_confidence=25)
    
    def _extract_enhanced(self, image: np.ndarray) -> List[Dict]:
        """OCR with enhanced preprocessing"""
        # Enhanced preprocessing pipeline
        processed = self._enhance_image(image)
        
        # Run OCR on enhanced image
        data = pytesseract.image_to_data(processed, config=self.configs['default'],
                                       output_type=pytesseract.Output.DICT)
        
        return self._process_ocr_data(data, 'enhanced', min_confidence=30)
    
    def _extract_numbers(self, image: np.ndarray) -> List[Dict]:
        """Specialized extraction for numbers (Aadhaar detection)"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Enhance contrast specifically for numbers
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        
        # Apply threshold
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Run OCR with numbers-only config
        data = pytesseract.image_to_data(binary, config=self.configs['numbers_only'],
                                       output_type=pytesseract.Output.DICT)
        
        return self._process_ocr_data(data, 'numbers', min_confidence=40)
    
    def _extract_binary(self, image: np.ndarray) -> List[Dict]:
        """OCR with high contrast binary image"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply aggressive binary threshold
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        
        # Clean up with morphological operations
        kernel = np.ones((2,2), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # Run OCR
        data = pytesseract.image_to_data(cleaned, config=self.configs['general'],
                                       output_type=pytesseract.Output.DICT)
        
        return self._process_ocr_data(data, 'binary', min_confidence=35)
    
    def _enhance_image(self, image: np.ndarray) -> np.ndarray:
        """Apply enhancement pipeline for better OCR"""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Remove noise
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(denoised)
        
        # Sharpen
        kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        
        # Scale up if image is small
        height, width = sharpened.shape
        if height < 500 or width < 500:
            scale_factor = 2
            sharpened = cv2.resize(sharpened, None, fx=scale_factor, fy=scale_factor, 
                                 interpolation=cv2.INTER_CUBIC)
        
        return sharpened
    
    def _process_ocr_data(self, data: Dict, method: str, min_confidence: int = 25) -> List[Dict]:
        """Process OCR data into standardized text blocks"""
        blocks = []
        
        for i in range(len(data['text'])):
            confidence = int(data['conf'][i])
            text = data['text'][i].strip()
            
            # Filter by confidence and text quality
            if confidence >= min_confidence and len(text) >= 1:
                if self._is_quality_text(text):
                    block = {
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i],
                        'text': text,
                        'confidence': confidence,
                        'method': method
                    }
                    blocks.append(block)
        
        return blocks
    
    def _is_quality_text(self, text: str) -> bool:
        """Check if extracted text meets quality criteria"""
        # Filter very short text
        if len(text) < 1:
            return False
        
        # Filter pure noise patterns
        noise_patterns = ['|', '||', '|||', '—', '－', '_', '..', '...', '....']
        if text in noise_patterns:
            return False
        
        # Check character composition
        alpha_count = sum(1 for c in text if c.isalpha())
        digit_count = sum(1 for c in text if c.isdigit())
        space_count = sum(1 for c in text if c.isspace())
        punct_count = sum(1 for c in text if c in '.,/-:')
        
        total_good = alpha_count + digit_count + space_count + punct_count
        
        # Should have reasonable character composition (at least 70% good characters)
        if total_good < len(text) * 0.7:
            return False
        
        return True
    
    def _merge_and_deduplicate(self, all_blocks: List[Dict]) -> List[Dict]:
        """Merge and deduplicate text blocks from multiple OCR runs"""
        if not all_blocks:
            return []
        
        # Group blocks by approximate position
        position_groups = {}
        tolerance = 25  # pixels
        
        for block in all_blocks:
            # Create position key (rounded to tolerance)
            pos_key = (
                round(block['x'] / tolerance) * tolerance,
                round(block['y'] / tolerance) * tolerance
            )
            
            if pos_key not in position_groups:
                position_groups[pos_key] = []
            position_groups[pos_key].append(block)
        
        # Select best block from each position group
        final_blocks = []
        
        for pos_key, blocks in position_groups.items():
            if len(blocks) == 1:
                final_blocks.append(blocks[0])
            else:
                # Select best block based on multiple criteria
                best_block = max(blocks, key=lambda b: (
                    b['confidence'],                    # Higher confidence
                    len(b['text']),                    # Longer text
                    self._text_quality_score(b['text']), # Better quality
                    b['method'] == 'enhanced'           # Prefer enhanced method
                ))
                final_blocks.append(best_block)
        
        # Sort blocks by position (top to bottom, left to right)
        final_blocks.sort(key=lambda b: (b['y'], b['x']))
        
        return final_blocks
    
    def _text_quality_score(self, text: str) -> float:
        """Calculate text quality score"""
        if not text:
            return 0
        
        # Various quality factors
        alpha_ratio = sum(1 for c in text if c.isalpha()) / len(text)
        digit_ratio = sum(1 for c in text if c.isdigit()) / len(text)
        
        # Prefer text with good character mix
        quality = alpha_ratio + digit_ratio * 0.9
        
        # Length bonus (prefer reasonable length)
        if 2 <= len(text) <= 30:
            quality += 0.3
        elif len(text) > 30:
            quality -= 0.1
        
        # Pattern bonuses
        if re.match(r'^[A-Z][a-z]+$', text):  # Proper names
            quality += 0.2
        elif re.match(r'^\d{4}\s*\d{4}\s*\d{4}$', text):  # Aadhaar pattern
            quality += 0.5
        elif re.match(r'^[A-Z]{5}\d{4}[A-Z]$', text):  # PAN pattern
            quality += 0.5
        
        return quality
    
    def _calculate_quality_score(self, blocks: List[Dict]) -> float:
        """Calculate overall OCR quality score"""
        if not blocks:
            return 0
        
        # Average confidence
        avg_confidence = sum(b['confidence'] for b in blocks) / len(blocks)
        
        # Text quality
        total_quality = sum(self._text_quality_score(b['text']) for b in blocks)
        avg_quality = total_quality / len(blocks)
        
        # Method diversity bonus (using multiple methods is good)
        methods = set(b.get('method', 'unknown') for b in blocks)
        method_bonus = len(methods) * 0.1
        
        # Combined score
        score = (avg_confidence / 100) * 0.6 + avg_quality * 0.3 + method_bonus
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _error_response(self, error_msg: str) -> Dict[str, any]:
        """Create standardized error response"""
        return {
            'success': False,
            'error': error_msg,
            'text_blocks': [],
            'full_text': '',
            'ocr_score': 0,
            'processing_methods': []
        }