import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Footer from './components/Footer';
import ImageUpload from './components/ImageUpload';
import ResultsDisplay from './components/ResultsDisplay';
import { api } from './api/client';
import { AlertCircle, CheckCircle, Server } from 'lucide-react';

function App() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');
  const [serverStatus, setServerStatus] = useState('checking');

  // Check server health on component mount
  useEffect(() => {
    checkServerHealth();
  }, []);

  const checkServerHealth = async () => {
    try {
      const response = await api.healthCheck();
      setServerStatus('connected');
      console.log('Server health check:', response.data);
    } catch (error) {
      setServerStatus('disconnected');
      console.error('Server health check failed:', error);
    }
  };

  const handleImageProcessed = async (file) => {
    setIsProcessing(true);
    setError('');
    setResults(null);

    try {
      const response = await api.processImage(file);
      setResults(response.data);
      console.log('Processing results:', response.data);
    } catch (error) {
      console.error('Error processing image:', error);
      setError(
        error.response?.data?.detail || 
        error.message || 
        'Failed to process image. Please try again.'
      );
    } finally {
      setIsProcessing(false);
    }
  };

  const getStatusIcon = () => {
    switch (serverStatus) {
      case 'connected':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'disconnected':
        return <AlertCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Server className="w-4 h-4 text-yellow-500 animate-pulse" />;
    }
  };

  const getStatusText = () => {
    switch (serverStatus) {
      case 'connected':
        return 'Server Connected';
      case 'disconnected':
        return 'Server Disconnected';
      default:
        return 'Checking Server...';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Header />
      
      <main className="flex-1 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Server Status */}
          <div className="mb-6">
            <div className="flex items-center justify-center space-x-2 text-sm">
              {getStatusIcon()}
              <span className={`
                ${serverStatus === 'connected' ? 'text-green-600' : ''}
                ${serverStatus === 'disconnected' ? 'text-red-600' : ''}
                ${serverStatus === 'checking' ? 'text-yellow-600' : ''}
              `}>
                {getStatusText()}
              </span>
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center">
                <AlertCircle className="w-5 h-5 text-red-500 mr-2" />
                <span className="text-red-700">{error}</span>
              </div>
            </div>
          )}

          {/* Main Content */}
          <div className="space-y-8">
            {/* Upload Section */}
            <ImageUpload 
              onImageProcessed={handleImageProcessed}
              isProcessing={isProcessing}
            />

            {/* Results Section */}
            {results && (
              <div className="animate-fade-in">
                <ResultsDisplay results={results} />
              </div>
            )}
          </div>

          
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default App; 