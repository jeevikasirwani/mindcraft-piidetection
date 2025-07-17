# PII Detection and Masking Application

A full-stack web application that automatically detects and masks Personally Identifiable Information (PII) from images.

## Features

- **Image Upload**: Drag and drop or click to upload images
- **PII Detection**: Automatically detects names, addresses, dates, phone numbers, emails, and ID numbers
- **Real-time Masking**: Masks detected PII with black rectangles
- **Download Result**: Download the masked image
- **Modern UI**: Clean, responsive interface built with React

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **OpenCV**: Image processing and masking
- **Tesseract OCR**: Text extraction from images
- **Pandas**: Data processing
- **Pillow**: Image manipulation
- **Uvicorn**: ASGI server

### Frontend
- **React.js**: Modern UI framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Axios**: HTTP client
- **React Dropzone**: File upload handling

## Project Structure

```
mindcraft/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── ocr_service.py
│   │   │   ├── pii_detector.py
│   │   │   └── image_processor.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── helpers.py
│   ├── requirements.txt
│   └── uploads/
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   ├── types/
│   │   └── App.tsx
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

## Setup Instructions

### Backend Setup
1. Navigate to backend directory
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run server: `uvicorn app.main:app --reload`

### Frontend Setup
1. Navigate to frontend directory
2. Install dependencies: `npm install`
3. Start development server: `npm start`

## API Endpoints

- `POST /upload-image`: Upload and process image for PII detection
- `GET /health`: Health check endpoint

## PII Detection Capabilities

- **Names**: Full names, first names, last names
- **Addresses**: Street addresses, cities, states
- **Dates**: Birth dates, issue dates, expiry dates
- **Phone Numbers**: Various formats (Indian and international)
- **Email Addresses**: Standard email format validation
- **ID Numbers**: Aadhaar numbers, PAN numbers, etc.

## Learning Outcomes

This project demonstrates:
- Full-stack development with Python and React
- Image processing and OCR techniques
- PII detection using regex and NLP
- Modern web development practices
- API design and integration
- File upload and processing
- Real-time image manipulation 