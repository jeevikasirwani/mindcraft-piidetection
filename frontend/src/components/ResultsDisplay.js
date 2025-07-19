import React, { useState } from 'react';
import { Eye, Download, Shield, AlertTriangle, CheckCircle } from 'lucide-react';
import { api } from '../api/client';

const ResultsDisplay = ({ results }) => {
  const [activeTab, setActiveTab] = useState('preview');

  if (!results) return null;

  const { 
    detected_entities, 
    preview_image_path, 
    masked_image_path, 
    processing_time,
    statistics 
  } = results;

  const getEntityTypeColor = (entityType) => {
    const colors = {
      'PERSON': 'bg-red-100 text-red-800',
      'ORGANIZATION': 'bg-blue-100 text-blue-800',
      'LOCATION': 'bg-green-100 text-green-800',
      'EMAIL': 'bg-purple-100 text-purple-800',
      'PHONE_NUMBER': 'bg-orange-100 text-orange-800',
      'ID_NUMBER': 'bg-yellow-100 text-yellow-800',
      'CREDIT_CARD': 'bg-pink-100 text-pink-800',
      'DATE': 'bg-indigo-100 text-indigo-800',
    };
    return colors[entityType] || 'bg-gray-100 text-gray-800';
  };

  

  const handleDownload = (imagePath) => {
    if (!imagePath) return;
    
    // Use different endpoints for different image types
    const url = imagePath.includes('masked') 
      ? api.getMaskedImageUrl(imagePath.replace(/^uploads[\\/]/, ''))
      : api.getUploadsUrl(imagePath.split('/').pop());
    
    const link = document.createElement('a');
    link.href = url;
    link.download = imagePath.replace(/^uploads[\\/]/, '').split('/').pop();
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="w-full max-w-6xl mx-auto space-y-6">
      {/* Processing Summary */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-900">Processing Results</h3>
          <div className="text-sm text-gray-500">
            Processed in {processing_time.toFixed(2)}s
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">
              {detected_entities.length}
            </div>
            <div className="text-sm text-blue-700">PII Entities Detected</div>
          </div>
          
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {statistics?.pii_types_detected?.length || 0}
            </div>
            <div className="text-sm text-green-700">PII Types Found</div>
          </div>
          
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <div className="text-2xl font-bold text-purple-600">
              {statistics?.detection_method || 'Computer Vision'}
            </div>
            <div className="text-sm text-purple-700">Detection Method</div>
          </div>
        </div>
      </div>

      {/* Image Display Tabs */}
      <div className="card">
        <div className="flex space-x-1 mb-6">
          <button
            onClick={() => setActiveTab('preview')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              activeTab === 'preview'
                ? 'bg-primary-100 text-primary-700'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Eye className="w-4 h-4 inline mr-2" />
            Preview
          </button>
          {masked_image_path && (
            <button
              onClick={() => setActiveTab('masked')}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                activeTab === 'masked'
                  ? 'bg-primary-100 text-primary-700'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Shield className="w-4 h-4 inline mr-2" />
              Masked Image
            </button>
          )}
        </div>

        {/* Image Display */}
        <div className="relative">
          {activeTab === 'preview' && preview_image_path && (
            <div className="text-center">
              <img
                src={api.getUploadsUrl(preview_image_path.split('/').pop())}
                alt="Preview with PII detection"
                className="max-w-full h-auto rounded-lg shadow-lg"
              />
              <button
                onClick={() => handleDownload(preview_image_path)}
                className="mt-4 btn-secondary"
              >
                <Download className="w-4 h-4 inline mr-2" />
                Download Preview
              </button>
            </div>
          )}
          
          {activeTab === 'masked' && masked_image_path && (
            <div className="text-center">
              <img
                src={api.getMaskedImageUrl(masked_image_path.replace(/^uploads[\\/]/, ''))}
                alt="Masked image"
                className="max-w-full h-auto rounded-lg shadow-lg"
              />
              <button
                onClick={() => handleDownload(masked_image_path)}
                className="mt-4 btn-secondary"
              >
                <Download className="w-4 h-4 inline mr-2" />
                Download Masked Image
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Detected Entities */}
      {detected_entities.length > 0 && (
        <div className="card">
          <h3 className="text-xl font-bold text-gray-900 mb-4">
            Detected PII Entities ({detected_entities.length})
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {detected_entities.map((entity, index) => (
              <div
                key={index}
                                className="p-4 rounded-lg border transition-all hover:shadow-md"               
              >
                <div className="flex items-start justify-between mb-2">
                  <div className={`px-2 py-1 rounded-full text-xs font-medium ${getEntityTypeColor(entity.entity_type)}`}>
                    {entity.entity_type}
                  </div>
                  <div className="text-xs text-gray-500">
                    {(entity.confidence * 100).toFixed(1)}%
                  </div>
                </div>
                
                <div className="text-sm font-medium text-gray-900 mb-1">
                  {entity.text}
                </div>
                

              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
};

export default ResultsDisplay; 