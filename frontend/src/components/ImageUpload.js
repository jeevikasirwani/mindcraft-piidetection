import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileImage, AlertCircle, CheckCircle } from 'lucide-react';

const ImageUpload = ({ onImageProcessed, isProcessing }) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [error, setError] = useState('');

  const onDrop = useCallback((acceptedFiles, rejectedFiles) => {
    setError('');
    
    if (rejectedFiles.length > 0) {
      setError('Please select a valid image file (PNG, JPG, JPEG)');
      return;
    }

    const file = acceptedFiles[0];
    if (file) {
      setSelectedFile(file);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg']
    },
    multiple: false,
    disabled: isProcessing
  });

  const handleProcessImage = async () => {
    if (!selectedFile) return;
    
    try {
      await onImageProcessed(selectedFile);
      setSelectedFile(null);
    } catch (error) {
      console.error('Error processing image:', error);
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setError('');
      setSelectedFile(file);
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="card">
        <div className="text-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Upload Image for PII Detection
          </h2>
          <p className="text-gray-600">
            Upload an image containing sensitive information to detect and mask PII
          </p>
        </div>

        {/* Dropzone */}
        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200
            ${isDragActive || dragActive 
              ? 'border-primary-500 bg-primary-50' 
              : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
            }
            ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          <input {...getInputProps()} />
          <input
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
            id="file-input"
            disabled={isProcessing}
          />
          
          <div className="flex flex-col items-center">
            {isDragActive ? (
              <Upload className="w-12 h-12 text-primary-500 mb-4" />
            ) : (
              <FileImage className="w-12 h-12 text-gray-400 mb-4" />
            )}
            
            <p className="text-lg font-medium text-gray-700 mb-2">
              {isDragActive 
                ? 'Drop the image here' 
                : 'Drag & drop an image here, or click to select'
              }
            </p>
            
            <p className="text-sm text-gray-500">
              Supports PNG, JPG, JPEG files
            </p>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center">
            <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
            <span className="text-red-700 text-sm">{error}</span>
          </div>
        )}

        {/* Selected File Info */}
        {selectedFile && (
          <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center">
              <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
              <div className="flex-1">
                <p className="text-green-800 font-medium">{selectedFile.name}</p>
                <p className="text-green-600 text-sm">
                  {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Process Button */}
        {selectedFile && (
          <button
            onClick={handleProcessImage}
            disabled={isProcessing}
            className={`
              w-full mt-4 py-3 px-6 rounded-lg font-medium transition-all duration-200
              ${isProcessing
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'btn-primary'
              }
            `}
          >
            {isProcessing ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Processing...
              </div>
            ) : (
              'Process Image for PII Detection'
            )}
          </button>
        )}
      </div>
    </div>
  );
};

export default ImageUpload; 