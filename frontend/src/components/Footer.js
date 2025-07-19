import React from 'react';
import { Github, Mail } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <h3 className="text-lg font-semibold mb-4">PII Detection</h3>
            <p className="text-gray-300 text-sm">
              Advanced AI-powered PII detection and image processing platform 
              using computer vision and machine learning technologies.
            </p>
          </div>
          
          <div>
            <h4 className="text-md font-semibold mb-4">Features</h4>
            <ul className="text-gray-300 text-sm space-y-2">
              <li>• Computer Vision PII Detection</li>
              <li>• Real-time Image Processing</li>
              <li>• Data Masking</li>
              <li>• Multiple PII Type Support</li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-gray-700 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
          <div className="text-gray-300 text-sm">
            © 2024 PII Detection. All rights reserved.
          </div>
          
          <div className="flex space-x-4 mt-4 md:mt-0">
            <a 
              href="https://github.com/jeevikasirwani/mindcraft-piidetection" 
              className="text-gray-300 hover:text-white transition-colors"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Github className="w-5 h-5" />
            </a>
            
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer; 