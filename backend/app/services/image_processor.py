import cv2
import numpy as np
from typing import List
from ..models import PIIEntity

class ImprovedImageProcessor:
    """Enhanced image processing with better masking techniques and full compatibility"""
    
    def __init__(self):
        # Define masking strategies by sensitivity level
        self.masking_strategies = {
            # Highest sensitivity - complete obstruction
            'high': ['aadhaar', 'pan', 'account', 'ssn', 'payment_id'],
            
            # Medium sensitivity - strong obfuscation  
            'medium': ['phone', 'email', 'date'],
            
            # Lower sensitivity - readable but marked
            'low': ['name', 'father_name', 'address'],
            
            # Special handling
            'special': ['signature']
        }
        
        # Color scheme for different entity types in preview
        self.color_map = {
            'aadhaar': (0, 0, 255),      # Red - High sensitivity
            'pan': (0, 0, 255),          # Red - High sensitivity
            'account': (0, 0, 255),      # Red - High sensitivity
            'payment_id': (0, 0, 255),   # Red - High sensitivity
            'phone': (255, 0, 0),        # Blue - Medium sensitivity
            'email': (255, 0, 0),        # Blue - Medium sensitivity
            'date': (255, 0, 0),         # Blue - Medium sensitivity
            'name': (0, 255, 0),         # Green - Lower sensitivity
            'father_name': (0, 255, 0),  # Green - Lower sensitivity
            'address': (0, 255, 0),      # Green - Lower sensitivity
            'signature': (255, 255, 0),  # Cyan - Special
        }
    
    def mask_pii_on_image(self, image_path: str, entities: List[PIIEntity]) -> str:
        """Apply appropriate masking based on PII sensitivity"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Could not read image")
            
            masked_image = image.copy()
            
            for entity in entities:
                x, y, w, h = self._normalize_bbox(entity.bbox, image.shape)
                
                if w <= 0 or h <= 0:
                    continue
                
                # Apply masking based on sensitivity
                sensitivity = self._get_sensitivity_level(entity.entity_type)
                
                if sensitivity == 'high':
                    self._apply_complete_masking(masked_image, x, y, w, h, entity.entity_type)
                elif sensitivity == 'medium':
                    self._apply_strong_masking(masked_image, x, y, w, h, entity.entity_type)
                elif sensitivity == 'low':
                    self._apply_light_masking(masked_image, x, y, w, h, entity.entity_type)
                elif sensitivity == 'special':
                    self._apply_signature_masking(masked_image, x, y, w, h)
                else:
                    # Default masking for unknown types
                    self._apply_strong_masking(masked_image, x, y, w, h, entity.entity_type)
            
            # Save masked image
            masked_path = image_path.replace('.', '_masked.')
            cv2.imwrite(masked_path, masked_image)
            
            return masked_path
            
        except Exception as e:
            raise Exception(f"Error masking image: {str(e)}")
    
    def create_masked_preview(self, image_path: str, entities: List[PIIEntity]) -> str:
        """
        Create preview showing all detected PII with colored boxes
        (Main method for compatibility with existing code)
        """
        return self.create_detection_preview(image_path, entities)
    
    def create_detection_preview(self, image_path: str, entities: List[PIIEntity]) -> str:
        """Create preview showing all detected PII with colored boxes"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Could not read image")
            
            for entity in entities:
                x, y, w, h = self._normalize_bbox(entity.bbox, image.shape)
                
                if w <= 0 or h <= 0:
                    continue
                
                color = self.color_map.get(entity.entity_type, (255, 255, 255))  # White default
                
                # Draw rectangle
                cv2.rectangle(image, (x, y), (x + w, y + h), color, 3)
                
                # Add label with confidence
                label = f"{entity.entity_type}: {entity.confidence:.2f}"
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.6
                
                # Calculate text background
                (text_width, text_height), _ = cv2.getTextSize(label, font, font_scale, 2)
                text_x = x
                text_y = max(y - 10, text_height)
                
                # Draw text background
                cv2.rectangle(image, (text_x, text_y - text_height - 5), 
                            (text_x + text_width + 5, text_y + 5), color, -1)
                
                # Draw text
                cv2.putText(image, label, (text_x + 2, text_y - 2), font, font_scale, (255, 255, 255), 2)
            
            # Save preview
            preview_path = image_path.replace('.', '_preview.')
            cv2.imwrite(preview_path, image)
            
            return preview_path
            
        except Exception as e:
            raise Exception(f"Error creating preview: {str(e)}")
    
    def blur_pii_on_image(self, image_path: str, entities: List[PIIEntity]) -> str:
        """
        Blur detected PII entities on image (alternative to black rectangles)
        (Maintains compatibility with existing code)
        """
        try:
            # Read original image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Could not read image")
            
            # Blur detected PII areas
            for entity in entities:
                x, y, w, h = self._normalize_bbox(entity.bbox, image.shape)
                
                if w <= 0 or h <= 0:
                    continue
                
                # Extract region of interest
                roi = image[y:y+h, x:x+w]
                
                # Apply blur
                blurred_roi = cv2.GaussianBlur(roi, (25, 25), 0)
                
                # Replace original region with blurred version
                image[y:y+h, x:x+w] = blurred_roi
                
                # Add border to indicate masking
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Save blurred image
            blurred_path = image_path.replace('.', '_blurred.')
            cv2.imwrite(blurred_path, image)
            
            return blurred_path
            
        except Exception as e:
            raise Exception(f"Error blurring image: {str(e)}")
    
    def create_comparison_view(self, original_path: str, masked_path: str) -> str:
        """Create side-by-side comparison of original and masked images"""
        try:
            original = cv2.imread(original_path)
            masked = cv2.imread(masked_path)
            
            if original is None or masked is None:
                raise ValueError("Could not read images for comparison")
            
            # Resize images to same height
            height = min(original.shape[0], masked.shape[0])
            original_resized = cv2.resize(original, (int(original.shape[1] * height / original.shape[0]), height))
            masked_resized = cv2.resize(masked, (int(masked.shape[1] * height / masked.shape[0]), height))
            
            # Create comparison image
            comparison = np.hstack([original_resized, masked_resized])
            
            # Add labels
            cv2.putText(comparison, "ORIGINAL", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(comparison, "MASKED", (original_resized.shape[1] + 20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Save comparison
            comparison_path = original_path.replace('.', '_comparison.')
            cv2.imwrite(comparison_path, comparison)
            
            return comparison_path
            
        except Exception as e:
            raise Exception(f"Error creating comparison: {str(e)}")
    
    # PRIVATE HELPER METHODS
    
    def _get_sensitivity_level(self, entity_type: str) -> str:
        """Determine sensitivity level for entity type"""
        for level, types in self.masking_strategies.items():
            if entity_type in types:
                return level
        return 'medium'  # Default to medium sensitivity
    
    def _normalize_bbox(self, bbox: List[int], image_shape) -> tuple:
        """Normalize bounding box coordinates with padding"""
        x, y, w, h = bbox
        
        # Ensure coordinates are within image bounds
        x = max(0, x)
        y = max(0, y)
        w = min(w, image_shape[1] - x)
        h = min(h, image_shape[0] - y)
        
        # Add padding for better coverage
        padding = 5
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(w + 2*padding, image_shape[1] - x)
        h = min(h + 2*padding, image_shape[0] - y)
        
        return x, y, w, h
    
    def _apply_complete_masking(self, image: np.ndarray, x: int, y: int, w: int, h: int, entity_type: str):
        """Complete obstruction for highly sensitive data"""
        # Solid black rectangle
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 0), -1)
        
        # Thick red border for visibility
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 3)
        
        # Add text label
        self._add_masking_label(image, x, y, w, h, entity_type.upper(), (255, 255, 255))
    
    def _apply_strong_masking(self, image: np.ndarray, x: int, y: int, w: int, h: int, entity_type: str):
        """Strong obfuscation that preserves some structure"""
        roi = image[y:y+h, x:x+w]
        
        # Heavy pixelation
        small_roi = cv2.resize(roi, (max(1, w//15), max(1, h//15)))
        pixelated_roi = cv2.resize(small_roi, (w, h), interpolation=cv2.INTER_NEAREST)
        
        # Apply additional noise
        noise = np.random.randint(0, 50, pixelated_roi.shape, dtype=np.uint8)
        pixelated_roi = cv2.add(pixelated_roi, noise)
        
        image[y:y+h, x:x+w] = pixelated_roi
        
        # Blue border
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)
        
        # Add label
        self._add_masking_label(image, x, y, w, h, entity_type.upper(), (255, 255, 255), size_factor=0.5)
    
    def _apply_light_masking(self, image: np.ndarray, x: int, y: int, w: int, h: int, entity_type: str):
        """Light masking that indicates PII but keeps some readability"""
        roi = image[y:y+h, x:x+w]
        
        # Light blur
        blurred_roi = cv2.GaussianBlur(roi, (15, 15), 0)
        
        # Semi-transparent overlay
        overlay = np.full(roi.shape, (0, 255, 255), dtype=np.uint8)  # Yellow
        blended = cv2.addWeighted(blurred_roi, 0.7, overlay, 0.3, 0)
        
        image[y:y+h, x:x+w] = blended
        
        # Green border
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 1)
    
    def _apply_signature_masking(self, image: np.ndarray, x: int, y: int, w: int, h: int):
        """Special masking for signatures"""
        roi = image[y:y+h, x:x+w]
        
        # Very heavy blur
        blurred_roi = cv2.GaussianBlur(roi, (35, 35), 0)
        
        # Dark overlay to obscure
        overlay = np.full(roi.shape, (50, 50, 50), dtype=np.uint8)
        blended = cv2.addWeighted(blurred_roi, 0.5, overlay, 0.5, 0)
        
        image[y:y+h, x:x+w] = blended
        
        # Cyan border
        cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 0), 2)
        
        # Add signature label
        self._add_masking_label(image, x, y, w, h, "SIGNATURE", (0, 0, 0))
    
    def _add_masking_label(self, image: np.ndarray, x: int, y: int, w: int, h: int, 
                          text: str, color: tuple, size_factor: float = 0.8):
        """Add text label to masked area"""
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = min(w, h) / 80.0 * size_factor
        font_scale = max(0.3, min(font_scale, 1.2))
        
        # Calculate text position (center of the box)
        (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, 2)
        text_x = x + (w - text_width) // 2
        text_y = y + (h + text_height) // 2
        
        # Ensure text fits in the box
        if text_width > w * 0.9:
            font_scale *= 0.7
            (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, 2)
            text_x = x + (w - text_width) // 2
            text_y = y + (h + text_height) // 2
        
        # Draw text with outline for better visibility
        cv2.putText(image, text, (text_x, text_y), font, font_scale, (0, 0, 0), 3)  # Outline
        cv2.putText(image, text, (text_x, text_y), font, font_scale, color, 2)      # Text