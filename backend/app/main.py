from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import time
from .models import ProcessImageResponse
from .services.ocr_service import OCRService
from .services.vision_detector import VisionDetector
from .services.image_processor import ImageProcessor

app = FastAPI(title="PII Detection API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

ocr_service = None
vision_detector = None
image_processor = None
# service initialization
try:
    ocr_service = OCRService()
    vision_detector = VisionDetector()
    image_processor = ImageProcessor()
except Exception as e:
    print(f"Service initialization failed: {e}")

def normalize_path_for_web(path):
    if path is None:
        return None
    return path.replace("\\", "/")

@app.get("/")
async def root():
    return {
        "message": "PII Detection API",
        "status": "running",
        "services": {
            'ocr': type(ocr_service).__name__ if ocr_service else 'Not initialized',
            'vision_detector': type(vision_detector).__name__ if vision_detector else 'Not initialized',
            'image_processor': type(image_processor).__name__ if image_processor else 'Not initialized'
        }
    }

@app.post("/process-image/", response_model=ProcessImageResponse)
async def process_image(file: UploadFile = File(...)):
    start_time = time.time()
    
    try:
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            raise HTTPException(status_code=400, detail="Only PNG and JPG files are supported")
        
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        timestamp = int(time.time())
        file_extension = os.path.splitext(file.filename)[1]
        safe_filename = f"{timestamp}_{file.filename.replace(' ', '_')}"
        file_path = os.path.join(upload_dir, safe_filename)
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        ocr_result = ocr_service.extract_text_from_image(file_path)
        detected_entities = vision_detector.detect_pii_from_image(file_path, ocr_result)
        
        masked_image_path = None
        preview_image_path = None
        if detected_entities:
            try:
                masked_image_path = image_processor.mask_pii_areas(file_path, detected_entities)
                preview_image_path = image_processor.create_preview(file_path, detected_entities)
            except Exception as e:
                print(f"Image processing failed: {e}")
        
        processing_time = time.time() - start_time
        
        entities_dict = []
        for entity in detected_entities:
            entities_dict.append({
                "text": entity.text,
                "entity_type": entity.entity_type,
                "confidence": round(entity.confidence, 3),
                "bbox": entity.bbox
            })
        
        extracted_text = ""
        if ocr_result.get('success'):
            text_blocks = ocr_result.get('text_blocks', [])
            extracted_text = " ".join([block.get('text', '') for block in text_blocks])
        
        return ProcessImageResponse(
            success=True,
            message="Image processed successfully",
            file_path=file_path,
            preview_image_path=normalize_path_for_web(preview_image_path) if preview_image_path else None,
            masked_image_path=normalize_path_for_web(masked_image_path) if masked_image_path else None,
            detected_entities=entities_dict,
            processing_time=processing_time,
            extracted_text=extracted_text,
            statistics={
                "detected_pii_count": len(detected_entities),
                "pii_types_detected": list(set([e.entity_type for e in detected_entities])),
                "detection_method": f"ocr_{ocr_result.get('method', 'unknown')}",
                "ocr_blocks": ocr_result.get('total_blocks', 0)
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/files/{filename}")
async def get_file(filename: str):
    file_path = os.path.join("uploads", filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path, media_type="image/jpeg")