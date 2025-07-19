import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout for image processing
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    console.log('Making request to:', config.url);
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    console.log('Response received:', response.status);
    return response;
  },
  (error) => {
    console.error('Response error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export const api = {
  // Health check
  healthCheck: () => apiClient.get('/'),
  
  // Process image
  processImage: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    return apiClient.post('/process-image/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  
  // Get file (for masked images)
  getFile: (filename) => `${API_BASE_URL}/files/${filename}`,
  
  // Get uploads directory (for preview images)
  getUploadsUrl: (filename) => `${API_BASE_URL}/files/${filename}`,
  
  // Get masked image URL
  getMaskedImageUrl: (filename) => {
    const url = `${API_BASE_URL}/files/${filename}`;
    console.log('getMaskedImageUrl called with filename:', filename);
    console.log('Generated URL:', url);
    return url;
  },
};

export default apiClient; 