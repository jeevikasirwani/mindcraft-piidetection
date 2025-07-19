import React from 'react';
import { Github, Mail, Shield } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-lg font-semibold mb-4">MindCraft</h3>
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
              <li>• Secure Data Masking</li>
              <li>• Multiple PII Type Support</li>
              <li>• High Accuracy Detection</li>
            </ul>
          </div>
          
          <div>
            <h4 className="text-md font-semibold mb-4">Security</h4>
            <div className="flex items-center space-x-2 text-gray-300 text-sm mb-2">
              <Shield className="w-4 h-4" />
              <span>End-to-end encryption</span>
            </div>
            <div className="flex items-center space-x-2 text-gray-300 text-sm mb-2">
              <Shield className="w-4 h-4" />
              <span>Secure file processing</span>
            </div>
            <div className="flex items-center space-x-2 text-gray-300 text-sm">
              <Shield className="w-4 h-4" />
              <span>Privacy-first approach</span>
            </div>
          </div>
        </div>
        
        <div className="border-t border-gray-700 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
          <div className="text-gray-300 text-sm">
            © 2024 MindCraft. All rights reserved.
          </div>
          
          <div className="flex space-x-4 mt-4 md:mt-0">
            <a 
              href="https://github.com" 
              className="text-gray-300 hover:text-white transition-colors"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Github className="w-5 h-5" />
            </a>
            <a 
              href="mailto:support@mindcraft.ai" 
              className="text-gray-300 hover:text-white transition-colors"
            >
              <Mail className="w-5 h-5" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer; 