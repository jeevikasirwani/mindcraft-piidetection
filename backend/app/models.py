from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class PIIEntity(BaseModel):
    """Represents a detected PII entity"""
    text: str
    entity_type: str
    confidence: float
    bbox: List[int]  # [x, y, width, height]


class OCRResult(BaseModel):
    """OCR extraction result"""
    success: bool
    text_blocks: List[dict] = []
    full_text: str = ""
    ocr_score: float = 0.0
    error: Optional[str] = None
    processing_methods: List[str] = []


class ProcessImageResponse(BaseModel):
    """Response model for image processing"""
    success: bool
    message: str
    file_path: Optional[str] = None
    preview_image_path: Optional[str] = None
    masked_image_path: Optional[str] = None
    comparison_image_path: Optional[str] = None
    detected_entities: List[dict] = []
    processing_time: float
    extracted_text: Optional[str] = None
    statistics: Optional[dict] = None


class PreviewResponse(BaseModel):
    """Response model for preview detection"""
    success: bool
    preview_image_path: Optional[str] = None
    detected_entities: List[dict] = []
    total_entities: int = 0
    entity_summary: dict = {}


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: float
    version: str = "3.0.0"
    services: dict = {}


class StatisticsResponse(BaseModel):
    """Statistics response"""
    total_files: int
    file_types: dict
    processing_files: dict
    uploads_directory: str
    service_info: dict