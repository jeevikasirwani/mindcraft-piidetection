from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class PIIEntity(BaseModel):
    text: str
    entity_type: str
    confidence: float
    bbox: List[int]


class OCRResult(BaseModel):
    success: bool
    text_blocks: List[dict] = []
    full_text: str = ""
    ocr_score: float = 0.0
    error: Optional[str] = None
    processing_methods: List[str] = []


class ProcessImageResponse(BaseModel):
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
    success: bool
    preview_image_path: Optional[str] = None
    detected_entities: List[dict] = []
    total_entities: int = 0
    entity_summary: dict = {}


class HealthResponse(BaseModel):
    status: str
    timestamp: float
    version: str = "1.0.0"
    services: dict = {}


class StatisticsResponse(BaseModel):
    total_files: int
    file_types: dict
    processing_files: dict
    uploads_directory: str
    service_info: dict