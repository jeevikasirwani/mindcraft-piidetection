from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import time
import logging
from .models import ProcessImageResponse, PIIEntity
from .services.ocr_service import SimpleOCRService
from .services.vision_detector import VisionDetector
from .services.image_processor import SimpleImageProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Computer Vision PII Detection API", version="3.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads directory for file serving
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Initialize services
ocr_service = None
vision_detector = None
image_processor = None

try:
    from .services.ocr_service import SimpleOCRService
    from .services.vision_detector import VisionDetector
    from .services.image_processor import SimpleImageProcessor
    
    ocr_service = SimpleOCRService()
    vision_detector = VisionDetector()
    image_processor = SimpleImageProcessor()
    
    logger.info("✅ All computer vision services initialized successfully")
except Exception as e:
    logger.error(f"❌ Service initialization failed: {e}")

# Normalize paths for web

def normalize_path_for_web(path):
    if path is None:
        return None
    return path.replace("\\", "/")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Computer Vision PII Detection API with Google Vision & Azure",
        "status": "running",
        "services": {
            'ocr': type(ocr_service).__name__ if ocr_service else 'Not initialized',
            'vision_detector': type(vision_detector).__name__ if vision_detector else 'Not initialized',
            'image_processor': type(image_processor).__name__ if image_processor else 'Not initialized'
        }
    }

@app.post("/process-image/", response_model=ProcessImageResponse)
async def process_image(file: UploadFile = File(...)):
    """Process uploaded image for computer vision-based PII detection and masking"""
    start_time = time.time()
    
    try:
        # Validate file
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            raise HTTPException(status_code=400, detail="Only PNG and JPG files are supported")
        
        # Create uploads directory if it doesn't exist
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save uploaded file with timestamp
        timestamp = int(time.time())
        file_extension = os.path.splitext(file.filename)[1]
        safe_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
        file_path = os.path.join(upload_dir, safe_filename)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"File saved to: {file_path}")
        
        # Step 1: Computer Vision PII Detection (skip OCR)
        logger.info("🔍 Starting computer vision PII detection...")
        detected_entities = vision_detector.detect_pii_from_image(file_path)
        logger.info(f"✅ Computer vision detection completed. Found {len(detected_entities)} entities")
        
        # Step 2: Create preview
        preview_path = None
        if detected_entities:
            try:
                preview_path = image_processor.create_preview(file_path, detected_entities)
                logger.info(f"✅ Preview created: {preview_path}")
            except Exception as e:
                logger.error(f"⚠️ Preview creation failed: {e}")
        
        # Step 3: Mask PII on image
        masked_image_path = None
        if detected_entities:
            try:
                masked_image_path = image_processor.mask_pii_on_image(file_path, detected_entities)
                logger.info(f"✅ Computer vision masking completed: {masked_image_path}")
            except Exception as e:
                logger.error(f"⚠️ Image masking failed: {e}")
        
        processing_time = time.time() - start_time
        
        # Convert PIIEntity objects to dictionaries for response
        entities_dict = []
        for entity in detected_entities:
            entities_dict.append({
                "text": entity.text,
                "entity_type": entity.entity_type,
                "confidence": round(entity.confidence, 3),
                "bbox": entity.bbox
            })
        
        return ProcessImageResponse(
            success=True,
            message="Image processed successfully with computer vision PII detection",
            file_path=file_path,
            preview_image_path=normalize_path_for_web(preview_path) if preview_path else None,
            masked_image_path=normalize_path_for_web(masked_image_path) if masked_image_path else None,
            detected_entities=entities_dict,
            processing_time=processing_time,
            extracted_text="",  # No OCR text extraction
            statistics={
                "detected_pii_count": len(detected_entities),
                "pii_types_detected": list(set([e.entity_type for e in detected_entities])),
                "detection_method": "computer_vision"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Processing error: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/files/{filename}")
async def get_file(filename: str):
    """Serve uploaded files"""
    file_path = os.path.join("uploads", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path, media_type="image/jpeg")