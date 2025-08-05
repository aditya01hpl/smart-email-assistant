import React from 'react';
import { initiateAuth } from '../services/api';

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

  const handleAuth = () => {
    console.log('Initiating authentication from sidebar...');
    initiateAuth();
  };

  return (
    <div className={`fixed left-0 top-0 h-full bg-white border-r border-gray-200 shadow-lg z-50 transition-all duration-300 ${
      collapsed ? 'w-16' : 'w-80'
    }`}>
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex items-center justify-between">
          {!collapsed && (
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">EA</span>
              </div>
              <h2 className="text-lg font-bold">Email AI</h2>
            </div>
          )}
          <button onClick={onToggle} className="p-2 hover:bg-gray-100 rounded">
            {collapsed ? '→' : '←'}
          </button>
        </div>
      </div>
      
      {/* Content when not collapsed */}
      {!collapsed && (
        <div className="flex flex-col h-full">
          {/* Status Section */}
          <div className="p-4 border-b">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Microsoft Auth:</span>
                <div className={`w-2 h-2 rounded-full ${authenticated ? 'bg-green-500' : 'bg-red-500'}`}></div>
              </div>
              <div className="flex justify-between text-sm">
                <span>Ollama AI:</span>
                <div className={`w-2 h-2 rounded-full ${ollamaStatus ? 'bg-green-500' : 'bg-red-500'}`}></div>
              </div>
            </div>

            {/* Auth Button */}
            {!authenticated && (
              <button
                onClick={handleAuth}
                className="w-full mt-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white text-sm font-medium py-2 px-3 rounded-lg transition-all duration-200 flex items-center justify-center space-x-2"
              >
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M23.64 12.2c0-.79-.07-1.54-.19-2.28H12.16v4.51h6.18c-.26 1.37-1.04 2.53-2.21 3.31v2.74h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path d="M12.16 24c2.97 0 5.46-.99 7.28-2.69l-3.57-2.74c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 24 12.16 24z"/>
                  <path d="M6 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.97-.62z"/>
                  <path d="M12.16 4.74c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 1.09 14.97 0 12.16 0 7.7 0 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                <span>Connect Email</span>
              </button>
            )}
          </div>

          {/* Search Section - only show when authenticated */}
          {authenticated && (
            <div className="p-4 border-b">
              <input
                type="text"
                placeholder="Search emails..."
                value={searchQuery || ''}
                onChange={(e) => onSearchChange && onSearchChange(e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          )}

          {/* Menu Items - only show when authenticated */}
          {authenticated && (
            <div className="flex-1 p-4">
              <div className="space-y-1">
                {menuItems.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => onFilterChange && onFilterChange(item.id)}
                    className={`w-full flex items-center justify-between p-3 rounded-lg text-sm font-medium transition-colors ${
                      filter === item.id 
                        ? 'bg-blue-50 text-blue-700 border border-blue-200' 
                        : 'text-gray-700 hover:bg-gray-100'
                    }`}
                  >
                    <span>{item.label}</span>
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      filter === item.id 
                        ? 'bg-blue-200 text-blue-800' 
                        : 'bg-gray-200 text-gray-600'
                    }`}>
                      {item.count}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Sync Button - only show when authenticated */}
          {authenticated && (
            <div className="p-4 border-t">
              <button
                onClick={onSync}
                disabled={syncing || !authenticated || !ollamaStatus}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white py-3 px-4 rounded-lg font-medium transition-colors flex items-center justify-center space-x-2"
              >
                {syncing ? (
                  <>
                    <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></div>
                    <span>Syncing...</span>
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    <span>Sync Emails</span>
                  </>
                )}
              </button>
            </div>
          )}

          {/* Help text when not authenticated */}
          {!authenticated && (
            <div className="flex-1 p-4 flex items-center justify-center">
              <div className="text-center text-sm text-gray-500">
                <p className="mb-2">🔐 Authentication Required</p>
                <p>Connect your Microsoft account to access email features</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Collapsed state content */}
      {collapsed && (
        <div className="p-4 space-y-4">
          {!authenticated ? (
            <button
              onClick={handleAuth}
              className="w-full p-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-lg transition-all duration-200"
              title="Connect Email"
            >
              <svg className="w-4 h-4 mx-auto" viewBox="0 0 24 24" fill="currentColor">
                <path d="M23.64 12.2c0-.79-.07-1.54-.19-2.28H12.16v4.51h6.18c-.26 1.37-1.04 2.53-2.21 3.31v2.74h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path d="M12.16 24c2.97 0 5.46-.99 7.28-2.69l-3.57-2.74c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 24 12.16 24z"/>
                <path d="M6 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.97-.62z"/>
                <path d="M12.16 4.74c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 1.09 14.97 0 12.16 0 7.7 0 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
            </button>
          ) : (
            <>
              <button
                onClick={onSync}
                disabled={syncing || !authenticated || !ollamaStatus}
                className="w-full p-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg transition-colors"
                title="Sync Emails"
              >
                {syncing ? (
                  <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full mx-auto"></div>
                ) : (
                  <svg className="w-4 h-4 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                )}
              </button>

              <div className="space-y-2 text-center">
                <div className={`w-3 h-3 rounded-full mx-auto ${authenticated ? 'bg-green-500' : 'bg-red-500'}`} title={authenticated ? 'Authenticated' : 'Not Authenticated'}></div>
                <div className={`w-3 h-3 rounded-full mx-auto ${ollamaStatus ? 'bg-green-500' : 'bg-red-500'}`} title={ollamaStatus ? 'Ollama Running' : 'Ollama Not Running'}></div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default Sidebar;