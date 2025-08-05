import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './styles/email.css';
import Dashboard from './components/Dashboard';
import Sidebar from './components/Sidebar';
import EmailModal from './components/EmailModel';
import { getStatus, syncEmails, getEmails } from './services/api';
import './styles/globals.css';

function App() {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [authenticated, setAuthenticated] = useState(false);
  const [ollamaStatus, setOllamaStatus] = useState(false);
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [filter, setFilter] = useState('all'); // all, unreplied, replied
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    checkStatus();
    checkAuthFromURL();
    
    // Auto-refresh every 5 minutes
    const interval = setInterval(checkStatus, 300000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (authenticated) {
      loadEmails();
    }
  }, [authenticated]);

  const checkAuthFromURL = () => {
    const urlParams = new URLSearchParams(window.location.search);
    const authStatus = urlParams.get('auth');
    
    if (authStatus === 'success') {
      toast.success('Successfully authenticated with Microsoft!');
      setAuthenticated(true);
      // Clean URL
      window.history.replaceState({}, document.title, window.location.pathname);
    } else if (authStatus === 'error') {
      toast.error('Authentication failed. Please try again.');
      // Clean URL
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  };

  const checkStatus = async () => {
    try {
      const status = await getStatus();
      setAuthenticated(status.authenticated);
      setOllamaStatus(status.ollama_status);
    } catch (error) {
      console.error('Error checking status:', error);
      toast.error('Failed to check service status');
    }
  };

  const loadEmails = async () => {
    try {
      setLoading(true);
      const response = await getEmails();
      setEmails(response.emails || []);
    } catch (error) {
      console.error('Error loading emails:', error);
      toast.error('Failed to load emails');
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    if (!authenticated) {
      toast.error('Please authenticate first');
      return;
    }

    if (!ollamaStatus) {
      toast.error('Ollama service is not running. Please start Ollama first.');
      return;
    }

    try {
      setSyncing(true);
      const response = await syncEmails();
      toast.success(response.message || 'Emails synced successfully!');
      await loadEmails(); // Reload emails after sync
    } catch (error) {
      console.error('Error syncing emails:', error);
      toast.error('Failed to sync emails');
    } finally {
      setSyncing(false);
    }
  };

  const handleEmailSelect = (email) => {
    setSelectedEmail(email);
  };

  const handleEmailUpdate = (updatedEmail) => {
    setEmails(emails.map(email => 
      email.id === updatedEmail.id ? updatedEmail : email
    ));
  };

  const filteredEmails = emails.filter(email => {
    // Apply filter
    if (filter === 'unreplied' && email.has_reply) return false;
    if (filter === 'replied' && !email.has_reply) return false;
    
    // Apply search
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        (email.subject || '').toLowerCase().includes(query) ||
        (email.sender || '').toLowerCase().includes(query) ||
        (email.summary || '').toLowerCase().includes(query)
      );
    }
    
    return true;
  });

  const getServiceStatus = () => {
    if (!authenticated) return { status: 'error', text: 'Not authenticated' };
    if (!ollamaStatus) return { status: 'warning', text: 'Ollama not running' };
    return { status: 'success', text: 'All services running' };
  };

  const serviceStatus = getServiceStatus();

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <div className="flex">
          {/* Sidebar */}
          <Sidebar
            collapsed={sidebarCollapsed}
            onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
            authenticated={authenticated}
            ollamaStatus={ollamaStatus}
            onSync={handleSync}
            syncing={syncing}
            filter={filter}
            onFilterChange={setFilter}
            searchQuery={searchQuery}
            onSearchChange={setSearchQuery}
            emailCount={{
              total: emails.length,
              unreplied: emails.filter(e => !e.has_reply).length,
              replied: emails.filter(e => e.has_reply).length
            }}
          />

          {/* Main Content */}
          <div className={`flex-1 transition-all duration-300 ${
            sidebarCollapsed ? 'ml-16' : 'ml-80'
          }`}>
            {/* Header */}
            <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-40">
              <div className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h1 className="text-2xl font-bold text-gray-900">
                      Smart Email Assistant
                    </h1>
                    <p className="text-sm text-gray-600 mt-1">
                      AI-powered email management and response generation
                    </p>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    {/* Service Status Indicator */}
                    <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm font-medium ${
                      serviceStatus.status === 'success' 
                        ? 'bg-green-100 text-green-800' 
                        : serviceStatus.status === 'warning'
                        ? 'bg-yellow-100 text-yellow-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      <div className={`w-2 h-2 rounded-full ${
                        serviceStatus.status === 'success' 
                          ? 'bg-green-500' 
                          : serviceStatus.status === 'warning'
                          ? 'bg-yellow-500'
                          : 'bg-red-500'
                      }`} />
                      <span>{serviceStatus.text}</span>
                    </div>

                    {/* Sync Button */}
                    <button
                      onClick={handleSync}
                      disabled={syncing || !authenticated || !ollamaStatus}
                      className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg font-medium transition-colors duration-200 flex items-center space-x-2"
                    >
                      {syncing ? (
                        <>
                          <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />
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
                </div>
              </div>
            </header>

            {/* Main Dashboard */}
            <main className="p-6">
              <Routes>
                <Route 
                  path="/" 
                  element={
                    <Dashboard
                      emails={filteredEmails}
                      loading={loading}
                      authenticated={authenticated}
                      onEmailSelect={handleEmailSelect}
                      onRefresh={loadEmails}
                    />
                  } 
                />
              </Routes>
            </main>
          </div>
        </div>

        {/* Email Modal */}
        {selectedEmail && (
          <EmailModal
            email={selectedEmail}
            onClose={() => setSelectedEmail(null)}
            onUpdate={handleEmailUpdate}
          />
        )}

        {/* Toast Notifications */}
        <ToastContainer
          position="top-right"
          autoClose={5000}
          hideProgressBar={false}
          newestOnTop={false}
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
          theme="light"
        />
      </div>
    </Router>
  );
}

export default App;