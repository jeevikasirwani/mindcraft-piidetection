# Google Vision API Setup Guide

## Overview
This guide helps you set up Google Vision API for enhanced PII detection in the MindCraft application.

## Prerequisites
1. Google Cloud Platform (GCP) account
2. Google Cloud Vision API enabled
3. Service account with Vision API permissions

## Step-by-Step Setup

### 1. Create a Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Cloud Vision API:
   - Go to "APIs & Services" > "Library"
   - Search for "Cloud Vision API"
   - Click "Enable"

### 2. Create a Service Account
1. Go to "IAM & Admin" > "Service Accounts"
2. Click "Create Service Account"
3. Fill in the details:
   - Name: `mindcraft-vision-api`
   - Description: `Service account for MindCraft PII detection`
4. Click "Create and Continue"
5. Add the "Cloud Vision API User" role
6. Click "Done"

### 3. Generate JSON Key
1. Click on your service account
2. Go to "Keys" tab
3. Click "Add Key" > "Create new key"
4. Select "JSON" format
5. Download the JSON file
6. **Important**: Keep this file secure and never commit it to version control

### 4. Set Environment Variable
Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable:

**Windows:**
```cmd
set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\your\service-account-key.json
```

**Linux/Mac:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
```

**For Development:**
Create a `.env` file in the backend directory:
```
GOOGLE_APPLICATION_CREDENTIALS=./service-account-key.json
```

### 5. Test the Setup
1. Place your service account JSON file in the backend directory
2. Restart your FastAPI server
3. Upload an image to test the enhanced PII detection

## Enhanced Features

With Google Vision API enabled, you'll get:

### ✅ Improved Detection
- **Better OCR**: More accurate text extraction from images
- **Precise Coordinates**: Exact bounding box positions for PII entities
- **Multiple Languages**: Support for Hindi and English text
- **Handwritten Text**: Detection of handwritten content

### ✅ Enhanced PII Types
- **Names**: Both English and Hindi names
- **Dates**: Birth dates, issue dates, expiry dates
- **Numbers**: Aadhaar, PAN, phone numbers
- **Addresses**: Complete address detection
- **Signatures**: Handwritten signature detection

### ✅ Better Accuracy
- **Context Awareness**: Understands document structure
- **Confidence Scores**: More reliable detection confidence
- **Duplicate Removal**: Eliminates false positives
- **Pattern Matching**: Enhanced regex patterns for Indian documents

## Troubleshooting

### Common Issues

1. **"GOOGLE_APPLICATION_CREDENTIALS not set"**
   - Ensure the environment variable is set correctly
   - Check the file path exists

2. **"Permission denied"**
   - Verify the service account has Vision API permissions
   - Check if the API is enabled in your project

3. **"Quota exceeded"**
   - Check your Google Cloud billing
   - Monitor usage in the Google Cloud Console

### Fallback Mode
If Google Vision API is not available, the system will automatically fall back to:
- Template-based detection
- Presidio analysis
- Pattern matching

## Cost Considerations
- Google Vision API has a free tier: 1,000 requests/month
- Additional requests cost $1.50 per 1,000 requests
- Monitor usage in Google Cloud Console

## Security Best Practices
1. Never commit service account keys to version control
2. Use environment variables for credentials
3. Regularly rotate service account keys
4. Monitor API usage for unusual activity
5. Set up billing alerts

## Next Steps
1. Test with various document types
2. Monitor detection accuracy
3. Adjust confidence thresholds if needed
4. Consider adding more custom recognizers 