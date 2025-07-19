import React from 'react';
import { Shield, Brain } from 'lucide-react';

const Header = () => {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center">
            <div className="flex items-center space-x-2">
              <div className="p-2 bg-primary-100 rounded-lg">
                <Brain className="w-6 h-6 text-primary-600" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">PII Detection</h1>
                <p className="text-sm text-gray-500">AI-Powered PII Detection</p>
              </div>
            </div>
          </div>
          
          
        </div>
      </div>
    </header>
  );
};

export default Header; 