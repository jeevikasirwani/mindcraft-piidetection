# MindCraft Frontend

A modern React application for AI-powered PII detection and image processing.

## Features

- **Drag & Drop Upload**: Easy image upload with drag and drop functionality
- **Real-time Processing**: Instant PII detection using computer vision
- **Visual Results**: Preview and masked image display
- **Entity Detection**: Detailed breakdown of detected PII entities
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Server Health Monitoring**: Real-time backend connection status

## Technology Stack

- **React 18**: Modern React with hooks and functional components
- **Tailwind CSS**: Utility-first CSS framework for styling
- **Axios**: HTTP client for API communication
- **React Dropzone**: Drag and drop file upload
- **Lucide React**: Beautiful icons
- **React Router**: Client-side routing (if needed)

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Backend server running on `http://localhost:8000`

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

4. Open [http://localhost:3000](http://localhost:3000) in your browser.

### Environment Variables

Create a `.env` file in the frontend directory:

```env
REACT_APP_API_URL=http://localhost:8000
```

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   ├── Header.js
│   │   ├── Footer.js
│   │   ├── ImageUpload.js
│   │   └── ResultsDisplay.js
│   ├── api/
│   │   └── client.js
│   ├── App.js
│   ├── index.js
│   └── index.css
├── package.json
├── tailwind.config.js
└── postcss.config.js
```

## API Integration

The frontend communicates with the backend through the following endpoints:

- `GET /` - Health check
- `POST /process-image/` - Process uploaded image
- `GET /uploads/{filename}` - Serve uploaded files

## Key Components

### ImageUpload
Handles file upload with drag and drop functionality, file validation, and processing state management.

### ResultsDisplay
Displays processing results including:
- Processing statistics
- Preview and masked images
- Detected PII entities with confidence scores
- Download functionality for processed images

### Header & Footer
Navigation and branding components with responsive design.

## Styling

The application uses Tailwind CSS with custom components and animations:

- Custom color scheme with primary and secondary colors
- Responsive grid layouts
- Smooth animations and transitions
- Modern card-based design

## Development

### Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

### Code Style

- Functional components with hooks
- ES6+ syntax
- Consistent naming conventions
- Proper error handling
- Responsive design patterns

## Deployment

1. Build the application:
   ```bash
   npm run build
   ```

2. The `build` folder contains the production-ready files.

3. Deploy to your preferred hosting service (Netlify, Vercel, etc.)

## Troubleshooting

### Common Issues

1. **Backend Connection Failed**
   - Ensure the backend server is running on port 8000
   - Check CORS settings in the backend
   - Verify API endpoints are accessible

2. **Image Upload Issues**
   - Check file size limits
   - Verify supported file formats (PNG, JPG, JPEG)
   - Ensure proper file permissions

3. **Styling Issues**
   - Clear browser cache
   - Restart development server
   - Check Tailwind CSS configuration

## Contributing

1. Follow the existing code style
2. Add proper error handling
3. Test on different screen sizes
4. Update documentation as needed

## License

This project is part of the MindCraft PII Detection platform. 