from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import time
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title='Enhanced PII Detection API', version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000', '*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs('uploads', exist_ok=True)

# Initialize services
ocr_service = None
pii_detector = None
image_processor = None

try:
    from .services.ocr_service import EnhancedOCRService
    from .services.pii_detector import AdvancedBlueUnderlinedDetector
    from .services.image_processor import ImprovedImageProcessor
    
    ocr_service = EnhancedOCRService()
    pii_detector = AdvancedBlueUnderlinedDetector()
    image_processor = ImprovedImageProcessor()
    
    logger.info("✅ All enhanced services initialized successfully")
    
except Exception as e:
    logger.error(f"❌ Service initialization failed: {e}")
    logger.exception("Full initialization error:")
    raise

@app.get('/health')
async def health_check():
    return {
        'status': 'healthy',
        'timestamp': time.time(),
        'version': '3.0.0',
        'services': {
            'ocr': type(ocr_service).__name__ if ocr_service else 'Not initialized',
            'pii_detector': type(pii_detector).__name__ if pii_detector else 'Not initialized',
            'image_processor': type(image_processor).__name__ if image_processor else 'Not initialized'
        }
    }

@app.post('/upload-image')
async def upload_image(file: UploadFile = File(...)):
    start_time = time.time()
    
    try:
        # Check if services are initialized
        if not all([ocr_service, pii_detector, image_processor]):
            raise HTTPException(status_code=500, detail="Services not properly initialized")
        
        logger.info(f"Processing file: {file.filename}")
        
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail='File must be an image')
        
        # Save uploaded file
        timestamp = int(time.time())
        file_extension = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
        safe_filename = f"{timestamp}_{(file.filename or 'upload').replace(' ', '_')}"
        file_path = f"uploads/{safe_filename}"
        
        with open(file_path, 'wb') as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"File saved to: {file_path}")

        # Step 1: Extract text using OCR
        logger.info("🔍 Starting enhanced OCR extraction...")
        ocr_result = ocr_service.extract_text_from_image(file_path)
        
        if not ocr_result['success']:
            error_msg = f"OCR failed: {ocr_result.get('error', 'Unknown error')}"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
        
        ocr_score = ocr_result.get('ocr_score', 0)
        logger.info(f"✅ OCR completed. Score: {ocr_score:.2f}, Blocks: {len(ocr_result['text_blocks'])}")

        # Step 2: Detect PII in extracted text
        logger.info("🔍 Starting enhanced PII detection...")
        detected_entities = pii_detector.detect_pii(ocr_result['text_blocks'])
        logger.info(f"✅ PII detection completed. Found {len(detected_entities)} entities")
        
        # Log detected entities for debugging
        entity_summary = {}
        for entity in detected_entities:
            entity_type = entity.entity_type
            entity_summary[entity_type] = entity_summary.get(entity_type, 0) + 1
            logger.info(f"  📋 {entity.entity_type}: '{entity.text}' (conf: {entity.confidence:.2f})")
        
        logger.info(f"📊 Entity summary: {entity_summary}")

        # Step 3: Create preview image (showing detected PII with colored boxes)
        preview_image_path = None
        if detected_entities:
            logger.info("🎨 Creating preview image...")
            try:
                preview_image_path = image_processor.create_detection_preview(file_path, detected_entities)
                logger.info(f"✅ Preview image created: {preview_image_path}")
            except Exception as e:
                logger.error(f"⚠️ Preview creation failed: {e}")
                logger.exception("Preview creation error:")

        # Step 4: Mask PII on image
        masked_image_path = None
        if detected_entities:
            logger.info("🔒 Starting enhanced image masking...")
            try:
                masked_image_path = image_processor.mask_pii_on_image(file_path, detected_entities)
                logger.info(f"✅ Image masking completed: {masked_image_path}")
            except Exception as e:
                logger.error(f"⚠️ Image masking failed: {e}")
                logger.exception("Image masking error:")
        
        processing_time = time.time() - start_time
        
        # Step 5: Create comparison view
        comparison_image_path = None
        if masked_image_path:
            try:
                comparison_image_path = image_processor.create_comparison_view(file_path, masked_image_path)
                logger.info(f"✅ Comparison image created: {comparison_image_path}")
            except Exception as e:
                logger.error(f"⚠️ Comparison creation failed: {e}")
        
        # Step 6: Return comprehensive response
        response = {
            "success": True,
            "message": "Image processed successfully with enhanced PII detection",
            "file_path": file_path,
            "preview_image_path": preview_image_path,
            "masked_image_path": masked_image_path,
            "comparison_image_path": comparison_image_path,
            "detected_entities": [
                {
                    "text": entity.text,
                    "entity_type": entity.entity_type,
                    "confidence": round(entity.confidence, 3),
                    "bbox": entity.bbox
                }
                for entity in detected_entities
            ],
            "processing_time": round(processing_time, 2),
            "extracted_text": ocr_result['full_text'],
            "statistics": {
                "total_text_blocks": len(ocr_result['text_blocks']),
                "detected_pii_count": len(detected_entities),
                "entity_types": list(entity_summary.keys()),
                "entity_counts": entity_summary,
                "ocr_score": round(ocr_score, 2),
                "processing_methods": ocr_result.get('processing_methods', [])
            }
        }
        
        logger.info(f"🎉 Processing completed in {processing_time:.2f} seconds")
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error processing image: {str(e)}"
        logger.error(error_msg)
        logger.exception("Full error traceback:")
        raise HTTPException(status_code=500, detail=error_msg)

@app.post('/preview-detection')
async def preview_detection(file: UploadFile = File(...)):
    """Preview endpoint that shows detected PII without masking"""
    try:
        if not all([ocr_service, pii_detector, image_processor]):
            raise HTTPException(status_code=500, detail="Services not properly initialized")
            
        logger.info(f"Creating preview for file: {file.filename}")
        
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail='File must be an image')
        
        timestamp = int(time.time())
        safe_filename = f"preview_{timestamp}_{(file.filename or 'upload').replace(' ', '_')}"
        file_path = f"uploads/{safe_filename}"
        
        with open(file_path, 'wb') as buffer:
            content = await file.read()
            buffer.write(content)
        
        ocr_result = ocr_service.extract_text_from_image(file_path)
        
        if not ocr_result['success']:
            raise HTTPException(status_code=500, detail=f"OCR failed: {ocr_result.get('error', 'Unknown error')}")
        
        detected_entities = pii_detector.detect_pii(ocr_result['text_blocks'])
        
        preview_path = None
        if detected_entities:
            preview_path = image_processor.create_detection_preview(file_path, detected_entities)
        
        return {
            "success": True,
            "preview_image_path": preview_path,
            "detected_entities": [
                {
                    "text": entity.text,
                    "entity_type": entity.entity_type,
                    "confidence": round(entity.confidence, 3),
                    "bbox": entity.bbox
                }
                for entity in detected_entities
            ],
            "total_entities": len(detected_entities),
            "entity_summary": {
                entity_type: len([e for e in detected_entities if e.entity_type == entity_type])
                for entity_type in set(entity.entity_type for entity in detected_entities)
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Error creating preview: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get('/uploads/{filename}')
async def get_file(filename: str):
    """Serve uploaded files"""
    file_path = f'uploads/{filename}'
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail='File not found')

@app.get('/api/statistics')
async def get_statistics():
    """Get processing statistics"""
    try:
        uploads_dir = 'uploads'
        if not os.path.exists(uploads_dir):
            return {"total_files": 0, "file_types": {}}
        
        files = os.listdir(uploads_dir)
        file_types = {}
        processing_files = {'masked': 0, 'preview': 0, 'comparison': 0, 'original': 0}
        
        for file in files:
            if '.' in file:
                ext = file.split('.')[-1].lower()
                file_types[ext] = file_types.get(ext, 0) + 1
                
                if '_masked.' in file:
                    processing_files['masked'] += 1
                elif '_preview.' in file:
                    processing_files['preview'] += 1
                elif '_comparison.' in file:
                    processing_files['comparison'] += 1
                else:
                    processing_files['original'] += 1
        
        return {
            "total_files": len(files),
            "file_types": file_types,
            "processing_files": processing_files,
            "uploads_directory": uploads_dir,
            "service_info": {
                'ocr': type(ocr_service).__name__ if ocr_service else 'Not initialized',
                'pii_detector': type(pii_detector).__name__ if pii_detector else 'Not initialized',
                'image_processor': type(image_processor).__name__ if image_processor else 'Not initialized'
            }
        }
    
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail="Error getting statistics")

@app.delete('/cleanup')
async def cleanup_files():
    """Clean up old uploaded files"""
    try:
        uploads_dir = 'uploads'
        if not os.path.exists(uploads_dir):
            return {"message": "No uploads directory found"}
        
        files = os.listdir(uploads_dir)
        deleted_count = 0
        
        for file in files:
            file_path = os.path.join(uploads_dir, file)
            try:
                os.remove(file_path)
                deleted_count += 1
            except Exception as e:
                logger.error(f"Could not delete {file}: {e}")
        
        return {
            "message": f"Cleanup completed",
            "deleted_files": deleted_count,
            "remaining_files": len(os.listdir(uploads_dir)) if os.path.exists(uploads_dir) else 0
        }
    
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        raise HTTPException(status_code=500, detail="Error during cleanup")