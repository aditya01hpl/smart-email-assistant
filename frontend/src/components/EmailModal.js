import React from 'react';

const EmailModal = ({ email, onClose, onUpdate }) => {
  if (!email) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black bg-opacity-50" onClick={onClose}></div>
      <div className="relative bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-start mb-4">
          <h2 className="text-xl font-bold">{email.subject}</h2>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-xl"
          >
            X
          </button>
        </div>
        <div className="mb-4">
          <p><strong>From:</strong> {email.sender}</p>
          <p><strong>Date:</strong> {new Date(email.timestamp).toLocaleString()}</p>
        </div>
        <div className="mb-4">
          <h3 className="font-semibold mb-2">Summary:</h3>
          <div className="bg-gray-50 p-3 rounded">
            {email.summary || 'No summary available'}
          </div>
        </div>
        <div>
          <h3 className="font-semibold mb-2">Content:</h3>
          <div className="bg-gray-50 p-3 rounded max-h-60 overflow-y-auto">
            {email.body || 'No content available'}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmailModal;