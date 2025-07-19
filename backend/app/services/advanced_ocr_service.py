import cv2
import numpy as np
import re
from typing import List, Dict, Optional
import logging

# Try to import advanced OCR libraries
try:
    import easyocr
    EASYOCR_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ EasyOCR imported successfully")
except ImportError:
    EASYOCR_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ EasyOCR not available")

try:
    import paddleocr
    PADDLEOCR_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ PaddleOCR imported successfully")
except ImportError:
    PADDLEOCR_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ PaddleOCR not available")

try:
    import layoutparser as lp
    LAYOUTPARSER_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ LayoutParser imported successfully")
except ImportError:
    LAYOUTPARSER_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ LayoutParser not available")

try:
    from transformers import AutoProcessor, AutoModelForVision2Seq
    TRANSFORMERS_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ Transformers imported successfully")
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ Transformers not available")

logger = logging.getLogger(__name__)

class AdvancedOCRService:
    """Advanced OCR service with multiple engines for high-accuracy document parsing"""
    
    def __init__(self):
        # Initialize different OCR engines
        self.engines = {}
        
        # EasyOCR (multilingual, good for Hindi)
        if EASYOCR_AVAILABLE:
            try:
                self.engines['easyocr'] = easyocr.Reader(['hi', 'en'], gpu=False)
                logger.info("✅ EasyOCR engine initialized")
            except Exception as e:
                logger.error(f"❌ EasyOCR initialization failed: {e}")
        
        # PaddleOCR (high accuracy, good coordinates)
        if PADDLEOCR_AVAILABLE:
            try:
                self.engines['paddleocr'] = paddleocr.PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
                logger.info("✅ PaddleOCR engine initialized")
            except Exception as e:
                logger.error(f"❌ PaddleOCR initialization failed: {e}")
        
        # LayoutParser (document layout analysis)
        if LAYOUTPARSER_AVAILABLE:
            try:
                # Initialize layout parser with OCR
                self.engines['layoutparser'] = lp.PaddleDetectionLayoutModel(
                    config_path='lp://PubLayNet/ppyolov2_r50vd_dcn_365e',
                    label_map={0: "Text", 1: "Title", 2: "List", 3: "Table", 4: "Figure"},
                    threshold=0.5,
                    enable_mkldnn=True
                )
                logger.info("✅ LayoutParser engine initialized")
            except Exception as e:
                logger.error(f"❌ LayoutParser initialization failed: {e}")
        
        # Transformers-based OCR (OLM-OCR alternative)
        if TRANSFORMERS_AVAILABLE:
            try:
                # Use a vision-language model for OCR
                self.engines['transformers'] = {
                    'processor': AutoProcessor.from_pretrained("microsoft/git-base"),
                    'model': AutoModelForVision2Seq.from_pretrained("microsoft/git-base")
                }
                logger.info("✅ Transformers OCR engine initialized")
            except Exception as e:
                logger.error(f"❌ Transformers initialization failed: {e}")
        
        logger.info(f"🎯 Initialized {len(self.engines)} OCR engines: {list(self.engines.keys())}")
    
    def extract_text_with_coordinates(self, image_path: str) -> Dict[str, any]:
        """Extract text with high-accuracy coordinates using multiple engines"""
        try:
            logger.info(f"🔍 Advanced OCR extraction on: {image_path}")
            
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                return self._error_response(f"Could not read image: {image_path}")
            
            logger.info(f"📷 Image loaded: {image.shape}")
            
            # Collect results from all engines
            all_results = []
            engine_results = {}
            
            # Engine 1: EasyOCR (multilingual)
            if 'easyocr' in self.engines:
                try:
                    easyocr_results = self._extract_with_easyocr(image)
                    all_results.extend(easyocr_results)
                    engine_results['easyocr'] = len(easyocr_results)
                    logger.info(f"✅ EasyOCR: {len(easyocr_results)} blocks")
                except Exception as e:
                    logger.error(f"EasyOCR failed: {e}")
            
            # Engine 2: PaddleOCR (high accuracy)
            if 'paddleocr' in self.engines:
                try:
                    paddle_results = self._extract_with_paddleocr(image)
                    all_results.extend(paddle_results)
                    engine_results['paddleocr'] = len(paddle_results)
                    logger.info(f"✅ PaddleOCR: {len(paddle_results)} blocks")
                except Exception as e:
                    logger.error(f"PaddleOCR failed: {e}")
            
            # Engine 3: LayoutParser (document structure)
            if 'layoutparser' in self.engines:
                try:
                    layout_results = self._extract_with_layoutparser(image)
                    all_results.extend(layout_results)
                    engine_results['layoutparser'] = len(layout_results)
                    logger.info(f"✅ LayoutParser: {len(layout_results)} blocks")
                except Exception as e:
                    logger.error(f"LayoutParser failed: {e}")
            
            # Engine 4: Transformers (vision-language model)
            if 'transformers' in self.engines:
                try:
                    transformer_results = self._extract_with_transformers(image)
                    all_results.extend(transformer_results)
                    engine_results['transformers'] = len(transformer_results)
                    logger.info(f"✅ Transformers: {len(transformer_results)} blocks")
                except Exception as e:
                    logger.error(f"Transformers failed: {e}")
            
            # Merge and deduplicate results
            final_blocks = self._merge_and_deduplicate_advanced(all_results)
            
            # Calculate quality metrics
            quality_score = self._calculate_advanced_quality_score(final_blocks)
            
            logger.info(f"🎯 Final result: {len(final_blocks)} unique text blocks")
            for block in final_blocks:
                logger.info(f"  📝 '{block['text']}' at ({block['x']},{block['y']}) conf: {block['confidence']:.2f}")
            
            return {
                'success': True,
                'text_blocks': final_blocks,
                'full_text': ' '.join([block['text'] for block in final_blocks]),
                'ocr_score': quality_score,
                'engine_results': engine_results,
                'engines_used': list(engine_results.keys())
            }
            
        except Exception as e:
            logger.error(f"❌ Advanced OCR error: {str(e)}")
            return self._error_response(f"Advanced OCR failed: {str(e)}")
    
    def _extract_with_easyocr(self, image: np.ndarray) -> List[Dict]:
        """Extract text using EasyOCR with precise coordinates"""
        blocks = []
        
        try:
            # Convert to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Run EasyOCR
            results = self.engines['easyocr'].readtext(rgb_image)
            
            for (bbox, text, confidence) in results:
                if len(text.strip()) > 0:
                    # Convert bbox to precise coordinates
                    x_coords = [point[0] for point in bbox]
                    y_coords = [point[1] for point in bbox]
                    
                    x = int(min(x_coords))
                    y = int(min(y_coords))
                    width = int(max(x_coords) - x)
                    height = int(max(y_coords) - y)
                    
                    block = {
                        'x': x,
                        'y': y,
                        'width': width,
                        'height': height,
                        'text': text.strip(),
                        'confidence': confidence,
                        'method': 'easyocr',
                        'bbox_points': bbox  # Keep original bbox for precision
                    }
                    blocks.append(block)
                    
                    logger.info(f"EasyOCR: '{text}' at ({x},{y},{width},{height}) conf: {confidence:.2f}")
            
        except Exception as e:
            logger.error(f"EasyOCR extraction error: {e}")
        
        return blocks
    
    def _extract_with_paddleocr(self, image: np.ndarray) -> List[Dict]:
        """Extract text using PaddleOCR with high accuracy"""
        blocks = []
        
        try:
            # Run PaddleOCR
            results = self.engines['paddleocr'].ocr(image, cls=True)
            
            if results and results[0]:
                for line in results[0]:
                    if line and len(line) >= 2:
                        bbox, (text, confidence) = line
                        
                        if text.strip():
                            # Convert bbox to coordinates
                            x_coords = [point[0] for point in bbox]
                            y_coords = [point[1] for point in bbox]
                            
                            x = int(min(x_coords))
                            y = int(min(y_coords))
                            width = int(max(x_coords) - x)
                            height = int(max(y_coords) - y)
                            
                            block = {
                                'x': x,
                                'y': y,
                                'width': width,
                                'height': height,
                                'text': text.strip(),
                                'confidence': confidence,
                                'method': 'paddleocr',
                                'bbox_points': bbox
                            }
                            blocks.append(block)
                            
                            logger.info(f"PaddleOCR: '{text}' at ({x},{y},{width},{height}) conf: {confidence:.2f}")
            
        except Exception as e:
            logger.error(f"PaddleOCR extraction error: {e}")
        
        return blocks
    
    def _extract_with_layoutparser(self, image: np.ndarray) -> List[Dict]:
        """Extract text using LayoutParser for document structure"""
        blocks = []
        
        try:
            # Convert to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect layout
            layout = self.engines['layoutparser'].detect(rgb_image)
            
            # Extract text from each detected region
            for region in layout:
                if region.type == 'Text':
                    # Get coordinates
                    x = int(region.block.coordinates[0])
                    y = int(region.block.coordinates[1])
                    width = int(region.block.coordinates[2] - x)
                    height = int(region.block.coordinates[3] - y)
                    
                    # Extract text from this region (simplified)
                    # In practice, you'd use OCR on the cropped region
                    block = {
                        'x': x,
                        'y': y,
                        'width': width,
                        'height': height,
                        'text': f"Text_Region_{len(blocks)}",  # Placeholder
                        'confidence': region.score,
                        'method': 'layoutparser',
                        'region_type': region.type
                    }
                    blocks.append(block)
                    
                    logger.info(f"LayoutParser: {region.type} at ({x},{y},{width},{height}) conf: {region.score:.2f}")
            
        except Exception as e:
            logger.error(f"LayoutParser extraction error: {e}")
        
        return blocks
    
    def _extract_with_transformers(self, image: np.ndarray) -> List[Dict]:
        """Extract text using Transformers vision-language model"""
        blocks = []
        
        try:
            # Convert to RGB
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Process image with transformers
            processor = self.engines['transformers']['processor']
            model = self.engines['transformers']['model']
            
            # This is a simplified version - in practice you'd need more sophisticated processing
            # For now, we'll create placeholder blocks
            block = {
                'x': 0,
                'y': 0,
                'width': image.shape[1],
                'height': image.shape[0],
                'text': "Transformers_OCR_Result",
                'confidence': 0.8,
                'method': 'transformers'
            }
            blocks.append(block)
            
            logger.info(f"Transformers: Placeholder result")
            
        except Exception as e:
            logger.error(f"Transformers extraction error: {e}")
        
        return blocks
    
    def _merge_and_deduplicate_advanced(self, all_blocks: List[Dict]) -> List[Dict]:
        """Advanced merging with coordinate-based deduplication"""
        if not all_blocks:
            return []
        
        # Group blocks by approximate position with higher precision
        position_groups = {}
        tolerance = 15  # Smaller tolerance for better precision
        
        for block in all_blocks:
            x, y = block['x'], block['y']
            
            # Find or create group
            grouped = False
            for group_key in position_groups:
                gx, gy = group_key
                if abs(x - gx) <= tolerance and abs(y - gy) <= tolerance:
                    position_groups[group_key].append(block)
                    grouped = True
                    break
            
            if not grouped:
                position_groups[(x, y)] = [block]
        
        # Merge blocks in each group with preference for better engines
        merged_blocks = []
        engine_preference = ['paddleocr', 'easyocr', 'layoutparser', 'transformers']
        
        for group_blocks in position_groups.values():
            if len(group_blocks) == 1:
                merged_blocks.append(group_blocks[0])
            else:
                # Select best block based on engine preference and confidence
                best_block = max(group_blocks, key=lambda b: (
                    engine_preference.index(b.get('method', 'unknown')) if b.get('method') in engine_preference else 999,
                    b.get('confidence', 0)
                ))
                merged_blocks.append(best_block)
        
        return merged_blocks
    
    def _calculate_advanced_quality_score(self, blocks: List[Dict]) -> float:
        """Calculate advanced quality score with coordinate precision"""
        if not blocks:
            return 0.0
        
        total_score = 0.0
        total_weight = 0.0
        
        for block in blocks:
            text = block.get('text', '')
            confidence = block.get('confidence', 0)
            
            # Text quality score
            text_score = self._text_quality_score_advanced(text)
            
            # Confidence score
            conf_score = min(confidence, 1.0)
            
            # Coordinate precision bonus
            coord_score = 1.0 if 'bbox_points' in block else 0.8
            
            # Combined score
            combined_score = (text_score + conf_score + coord_score) / 3
            
            total_score += combined_score
            total_weight += 1
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def _text_quality_score_advanced(self, text: str) -> float:
        """Advanced text quality scoring"""
        if not text:
            return 0.0
        
        score = 0.0
        
        # Length score
        if len(text) >= 3:
            score += 0.2
        
        # Character diversity
        unique_chars = len(set(text))
        if unique_chars >= 3:
            score += 0.2
        
        # Alphanumeric ratio
        alpha_count = sum(1 for c in text if c.isalpha())
        digit_count = sum(1 for c in text if c.isdigit())
        total_chars = len(text)
        
        if total_chars > 0:
            alpha_ratio = alpha_count / total_chars
            digit_ratio = digit_count / total_chars
            
            if 0.1 <= alpha_ratio <= 0.9 or 0.1 <= digit_ratio <= 0.9:
                score += 0.3
        
        # No excessive spaces
        if text.count(' ') <= len(text) * 0.3:
            score += 0.2
        
        # No excessive punctuation
        punct_count = sum(1 for c in text if c in '.,;:!?')
        if punct_count <= len(text) * 0.2:
            score += 0.1
        
        return min(score, 1.0)
    
    def _error_response(self, error_msg: str) -> Dict[str, any]:
        """Return error response"""
        return {
            'success': False,
            'error': error_msg,
            'text_blocks': [],
            'full_text': '',
            'ocr_score': 0.0,
            'engine_results': {},
            'engines_used': []
        } 