import React from 'react';

const EmailCard = ({ email, onClick, view = 'grid' }) => {
  return (
    <div 
      className="bg-white p-4 rounded-lg shadow cursor-pointer hover:shadow-md transition-shadow"
      onClick={onClick}
    >
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-semibold truncate">{email?.sender || 'Unknown Sender'}</h3>
        <span className="text-xs text-gray-500">
          {email?.timestamp ? new Date(email.timestamp).toLocaleDateString() : 'No date'}
        </span>
      </div>
      <p className="text-sm font-medium mb-2 truncate">{email?.subject || 'No Subject'}</p>
      <p className="text-sm text-gray-600 line-clamp-2">{email?.summary || email?.body || 'No content'}</p>
    </div>
  );
};

export default EmailCard;