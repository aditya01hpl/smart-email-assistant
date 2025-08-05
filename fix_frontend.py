"""
Frontend Fix Script
Fixes common frontend setup issues
"""

import os
import shutil
from pathlib import Path

def fix_frontend_structure():
    """Fix frontend file structure and naming issues"""
    
    frontend_dir = Path('./frontend')
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        return False
    
    os.chdir('frontend')
    
    # Create necessary directories
    directories = [
        'src/components',
        'src/services', 
        'src/styles'
    ]
    
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {dir_path}")
    
    # Check for case-sensitive file issues
    styles_dir = Path('src/styles')
    if styles_dir.exists():
        # Check if there's a "Styles" directory (capital S)
        parent_dir = styles_dir.parent
        for item in parent_dir.iterdir():
            if item.is_dir() and item.name.lower() == 'styles' and item.name != 'styles':
                print(f"🔄 Found case mismatch: {item.name} -> styles")
                # Rename to correct case
                temp_name = item.name + '_temp'
                item.rename(parent_dir / temp_name)
                (parent_dir / temp_name).rename(parent_dir / 'styles')
                break
    
    # Create empty component files if they don't exist
    component_files = [
        'src/components/Dashboard.js',
        'src/components/EmailCard.js', 
        'src/components/EmailModal.js',
        'src/components/Sidebar.js'
    ]
    
    for comp_file in component_files:
        comp_path = Path(comp_file)
        if not comp_path.exists():
            comp_path.touch()
            print(f"📄 Created empty file: {comp_file}")
    
    # Create empty service and style files
    other_files = [
        'src/services/api.js',
        'src/styles/globals.css'
    ]
    
    for file_path in other_files:
        file_obj = Path(file_path)
        if not file_obj.exists():
            file_obj.touch()
            print(f"📄 Created empty file: {file_path}")
    
    os.chdir('..')
    print("✅ Frontend structure fixed!")
    return True

def create_minimal_components():
    """Create minimal working components to prevent import errors"""
    
    os.chdir('frontend')
    
    # Minimal Dashboard component
    dashboard_content = '''import React from 'react';

const Dashboard = ({ emails, loading, authenticated, onEmailSelect, onRefresh }) => {
  if (!authenticated) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-4">Connect Your Email</h2>
          <p className="text-gray-600">Please authenticate to continue</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full"></div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Email Dashboard</h1>
      <div className="bg-white rounded-lg p-4 shadow">
        <p>Dashboard is loading... Please wait while we set up the components.</p>
        <p className="text-sm text-gray-600 mt-2">
          Found {emails?.length || 0} emails
        </p>
      </div>
    </div>
  );
};

export default Dashboard;'''

    # Write minimal components with UTF-8 encoding
    with open('src/components/Dashboard.js', 'w', encoding='utf-8') as f:
        f.write(dashboard_content)
    
    # Minimal EmailCard
    emailcard_content = '''import React from 'react';

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

export default EmailCard;'''

    with open('src/components/EmailCard.js', 'w', encoding='utf-8') as f:
        f.write(emailcard_content)
    
    # Minimal EmailModal (using X instead of Unicode)
    emailmodal_content = '''import React from 'react';

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

export default EmailModal;'''

    with open('src/components/EmailModal.js', 'w', encoding='utf-8') as f:
        f.write(emailmodal_content)
    
    # Minimal Sidebar (fixed syntax)
    sidebar_content = '''import React from 'react';

const Sidebar = ({ 
  collapsed, 
  onToggle, 
  authenticated, 
  ollamaStatus, 
  onSync, 
  syncing, 
  filter, 
  onFilterChange, 
  searchQuery, 
  onSearchChange,
  emailCount 
}) => {
  const menuItems = [
    { id: 'all', label: 'All Emails', count: emailCount?.total || 0 },
    { id: 'unreplied', label: 'Needs Reply', count: emailCount?.unreplied || 0 },
    { id: 'replied', label: 'Replied', count: emailCount?.replied || 0 }
  ];

  return (
    <div className={`fixed left-0 top-0 h-full bg-white border-r border-gray-200 shadow-lg z-50 transition-all duration-300 ${
      collapsed ? 'w-16' : 'w-80'
    }`}>
      <div className="p-4 border-b">
        <div className="flex items-center justify-between">
          {!collapsed && (
            <h2 className="text-lg font-bold">Email AI</h2>
          )}
          <button onClick={onToggle} className="p-2 hover:bg-gray-100 rounded">
            {collapsed ? '→' : '←'}
          </button>
        </div>
      </div>
      
      {!collapsed && (
        <div className="p-4">
          <div className="space-y-2 mb-4">
            <div className="flex justify-between text-sm">
              <span>Auth:</span>
              <span className={authenticated ? 'text-green-600' : 'text-red-600'}>
                {authenticated ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span>AI:</span>
              <span className={ollamaStatus ? 'text-green-600' : 'text-red-600'}>
                {ollamaStatus ? 'Running' : 'Stopped'}
              </span>
            </div>
          </div>
          
          <div className="mb-4">
            <input
              type="text"
              placeholder="Search emails..."
              value={searchQuery || ''}
              onChange={(e) => onSearchChange && onSearchChange(e.target.value)}
              className="w-full p-2 border rounded text-sm"
            />
          </div>

          <div className="space-y-1 mb-4">
            {menuItems.map((item) => (
              <button
                key={item.id}
                onClick={() => onFilterChange && onFilterChange(item.id)}
                className={`w-full flex items-center justify-between p-2 rounded text-sm ${
                  filter === item.id ? 'bg-blue-100 text-blue-700' : 'hover:bg-gray-100'
                }`}
              >
                <span>{item.label}</span>
                <span className="bg-gray-200 px-2 py-1 rounded-full text-xs">
                  {item.count}
                </span>
              </button>
            ))}
          </div>
          
          <button
            onClick={onSync}
            disabled={syncing || !authenticated}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white py-2 px-4 rounded transition-colors"
          >
            {syncing ? 'Syncing...' : 'Sync Emails'}
          </button>
        </div>
      )}
    </div>
  );
};

export default Sidebar;'''

    with open('src/components/Sidebar.js', 'w', encoding='utf-8') as f:
        f.write(sidebar_content)
    
    # Minimal API service
    api_content = '''import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

export const getStatus = async () => {
  const response = await api.get('/api/status');
  return response.data;
};

export const syncEmails = async () => {
  const response = await api.post('/api/emails/sync');
  return response.data;
};

export const getEmails = async () => {
  const response = await api.get('/api/emails');
  return response.data;
};

export const getEmailDetails = async (emailId) => {
  const response = await api.get(`/api/emails/${emailId}`);
  return response.data;
};

export const sendReply = async (emailId, content) => {
  const response = await api.post(`/api/emails/${emailId}/reply`, { content });
  return response.data;
};

export const regenerateReply = async (emailId) => {
  const response = await api.post(`/api/emails/${emailId}/regenerate-reply`);
  return response.data;
};

export const initiateAuth = async () => {
  const response = await api.get('/auth/login');
  window.location.href = response.data.auth_url;
};

export const formatTimestamp = (timestamp) => {
  try {
    return new Date(timestamp).toLocaleDateString();
  } catch {
    return 'Unknown';
  }
};

export const getSenderInitials = (name, email) => {
  if (name) {
    const parts = name.split(' ');
    return parts.length > 1 ? (parts[0][0] + parts[1][0]).toUpperCase() : parts[0][0].toUpperCase();
  }
  return email ? email[0].toUpperCase() : '?';
};

export const getAvatarColor = (email) => {
  const colors = ['bg-blue-500', 'bg-green-500', 'bg-purple-500', 'bg-pink-500'];
  return colors[email.charCodeAt(0) % colors.length];
};

export const getEmailPriority = (email) => {
  return 'normal';
};

export default api;'''

    with open('src/services/api.js', 'w', encoding='utf-8') as f:
        f.write(api_content)
    
    # Basic CSS
    css_content = '''@tailwind base;
@tailwind components;
@tailwind utilities;

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-6 {
  display: -webkit-box;
  -webkit-line-clamp: 6;
  -webkit-box-orient: vertical;
  overflow: hidden;
}'''

    with open('src/styles/globals.css', 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    os.chdir('..')
    print("✅ Created minimal components!")

if __name__ == "__main__":
    print("🔧 Fixing frontend structure...")
    
    if fix_frontend_structure():
        create_minimal_components()
        print("\n🎉 Frontend fixes complete!")
        print("\nNext steps:")
        print("1. Run: cd frontend && npm start")
        print("2. The app should now load without errors")
        print("3. You can then replace the minimal components with the full versions")
    else:
        print("❌ Failed to fix frontend structure")