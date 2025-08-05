import React, { useState, useEffect } from 'react';
import axios from 'axios';

const DebugDashboard = () => {
  const [debugInfo, setDebugInfo] = useState({
    database: null,
    ollama: null,
    status: null,
    emails: null
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    runDebugTests();
  }, []);

  const runDebugTests = async () => {
    setLoading(true);
    
    try {
      // Test database
      console.log('Testing database...');
      const dbTest = await axios.get('/api/debug/db-test');
      setDebugInfo(prev => ({ ...prev, database: dbTest.data }));
      
      // Test Ollama
      console.log('Testing Ollama...');
      const ollamaTest = await axios.get('/api/debug/ollama-test');
      setDebugInfo(prev => ({ ...prev, ollama: ollamaTest.data }));
      
      // Get status
      console.log('Getting status...');
      const status = await axios.get('/api/status');
      setDebugInfo(prev => ({ ...prev, status: status.data }));
      
      // Get emails
      console.log('Getting emails...');
      const emails = await axios.get('/api/emails');
      setDebugInfo(prev => ({ ...prev, emails: emails.data }));
      
    } catch (error) {
      console.error('Debug test failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    try {
      console.log('Starting sync...');
      const response = await axios.post('/api/emails/sync');
      console.log('Sync response:', response.data);
      
      // Refresh emails after sync
      const emails = await axios.get('/api/emails');
      setDebugInfo(prev => ({ ...prev, emails: emails.data }));
      
      alert(`Sync completed! ${response.data.message}`);
    } catch (error) {
      console.error('Sync failed:', error);
      alert(`Sync failed: ${error.response?.data?.error || error.message}`);
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center">
          <div className="animate-spin w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full"></div>
          <span className="ml-2">Running debug tests...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Debug Dashboard</h1>
        <div className="space-x-2">
          <button
            onClick={runDebugTests}
            className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded"
          >
            Refresh Tests
          </button>
          <button
            onClick={handleSync}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded"
          >
            Test Sync
          </button>
        </div>
      </div>

      {/* Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="font-semibold mb-2">Authentication</h3>
          <div className={`w-4 h-4 rounded-full ${
            debugInfo.status?.authenticated ? 'bg-green-500' : 'bg-red-500'
          }`}></div>
          <p className="text-sm mt-1">
            {debugInfo.status?.authenticated ? 'Connected' : 'Not Connected'}
          </p>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="font-semibold mb-2">Ollama AI</h3>
          <div className={`w-4 h-4 rounded-full ${
            debugInfo.status?.ollama_status ? 'bg-green-500' : 'bg-red-500'
          }`}></div>
          <p className="text-sm mt-1">
            {debugInfo.status?.ollama_status ? 'Running' : 'Not Running'}
          </p>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="font-semibold mb-2">Database</h3>
          <div className={`w-4 h-4 rounded-full ${
            debugInfo.database?.database_working ? 'bg-green-500' : 'bg-red-500'
          }`}></div>
          <p className="text-sm mt-1">
            {debugInfo.database?.email_count || 0} emails stored
          </p>
        </div>

        <div className="bg-white p-4 rounded-lg shadow">
          <h3 className="font-semibold mb-2">Last Sync</h3>
          <p className="text-sm">
            {debugInfo.status?.last_sync ? 
              new Date(debugInfo.status.last_sync).toLocaleString() : 
              'Never'
            }
          </p>
        </div>
      </div>

      {/* Database Test Results */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Database Test Results</h2>
        {debugInfo.database ? (
          <div className="space-y-2">
            <p><strong>Status:</strong> {debugInfo.database.database_working ? '✅ Working' : '❌ Failed'}</p>
            <p><strong>Email Count:</strong> {debugInfo.database.email_count}</p>
            <p><strong>Stats:</strong> {JSON.stringify(debugInfo.database.stats, null, 2)}</p>
            
            {debugInfo.database.sample_emails && debugInfo.database.sample_emails.length > 0 && (
              <div>
                <p><strong>Sample Emails:</strong></p>
                <pre className="bg-gray-100 p-2 rounded text-sm overflow-x-auto">
                  {JSON.stringify(debugInfo.database.sample_emails, null, 2)}
                </pre>
              </div>
            )}
          </div>
        ) : (
          <p>No database test results</p>
        )}
      </div>

      {/* Ollama Test Results */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Ollama AI Test Results</h2>
        {debugInfo.ollama ? (
          <div className="space-y-2">
            <p><strong>Status:</strong> {debugInfo.ollama.ollama_working ? '✅ Working' : '❌ Failed'}</p>
            <p><strong>Health:</strong> {debugInfo.ollama.health ? '✅ Healthy' : '❌ Unhealthy'}</p>
            
            {debugInfo.ollama.test_summary && (
              <div>
                <p><strong>Test Summary:</strong></p>
                <div className="bg-gray-100 p-2 rounded text-sm">
                  {debugInfo.ollama.test_summary}
                </div>
              </div>
            )}
            
            {debugInfo.ollama.test_reply && (
              <div>
                <p><strong>Test Reply:</strong></p>
                <div className="bg-gray-100 p-2 rounded text-sm">
                  {debugInfo.ollama.test_reply}
                </div>
              </div>
            )}
            
            {debugInfo.ollama.error && (
              <div>
                <p><strong>Error:</strong></p>
                <div className="bg-red-100 p-2 rounded text-sm text-red-700">
                  {debugInfo.ollama.error}
                </div>
              </div>
            )}
          </div>
        ) : (
          <p>No Ollama test results</p>
        )}
      </div>

      {/* Current Emails */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-semibold mb-4">Current Emails in Database</h2>
        {debugInfo.emails?.emails && debugInfo.emails.emails.length > 0 ? (
          <div className="space-y-4">
            <p><strong>Total:</strong> {debugInfo.emails.emails.length} emails</p>
            <div className="grid gap-4">
              {debugInfo.emails.emails.slice(0, 5).map((email, index) => (
                <div key={email.id || index} className="border p-3 rounded">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-medium">{email.subject || 'No Subject'}</h4>
                    <span className={`px-2 py-1 rounded text-xs ${
                      email.has_reply ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {email.has_reply ? 'Replied' : 'Needs Reply'}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600">From: {email.sender}</p>
                  <p className="text-sm text-gray-600">
                    Time: {email.timestamp ? new Date(email.timestamp).toLocaleString() : 'Unknown'}
                  </p>
                  {email.summary && (
                    <div className="mt-2">
                      <p className="text-sm font-medium">Summary:</p>
                      <p className="text-sm text-gray-700">{email.summary.substring(0, 150)}...</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
            
            {debugInfo.emails.emails.length > 5 && (
              <p className="text-sm text-gray-500">
                ... and {debugInfo.emails.emails.length - 5} more emails
              </p>
            )}
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-500 mb-4">No emails found in database</p>
            <div className="space-y-2 text-sm text-gray-600">
              <p>Possible reasons:</p>
              <ul className="list-disc list-inside space-y-1">
                <li>Not authenticated with Microsoft</li>
                <li>No emails in the last 7 days</li>
                <li>All emails filtered out as irrelevant</li>
                <li>Sync hasn't been run yet</li>
                <li>API permission issues</li>
              </ul>
            </div>
          </div>
        )}
      </div>

      {/* Instructions */}
      <div className="bg-blue-50 p-6 rounded-lg">
        <h2 className="text-xl font-semibold mb-4 text-blue-900">Debugging Instructions</h2>
        <div className="space-y-3 text-sm text-blue-800">
          <div>
            <h3 className="font-medium">If no emails are showing:</h3>
            <ol className="list-decimal list-inside ml-4 space-y-1">
              <li>Check if you're authenticated (green status above)</li>
              <li>Ensure Ollama is running: <code className="bg-blue-100 px-1 rounded">ollama serve</code></li>
              <li>Ensure phi3 model is available: <code className="bg-blue-100 px-1 rounded">ollama pull phi3:mini</code></li>
              <li>Click "Test Sync" button above</li>
              <li>Check the browser console (F12) for errors</li>
              <li>Check the Flask terminal for debug messages</li>
            </ol>
          </div>
          
          <div>
            <h3 className="font-medium">Debug Endpoints:</h3>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li><code className="bg-blue-100 px-1 rounded">GET /api/debug/db-test</code> - Test database</li>
              <li><code className="bg-blue-100 px-1 rounded">GET /api/debug/ollama-test</code> - Test AI service</li>
              <li><code className="bg-blue-100 px-1 rounded">GET /api/status</code> - Get current status</li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-medium">Common Issues:</h3>
            <ul className="list-disc list-inside ml-4 space-y-1">
              <li><strong>Authentication:</strong> Click "Sign in with Microsoft" and complete OAuth flow</li>
              <li><strong>Ollama:</strong> Make sure Ollama service is running on port 11434</li>
              <li><strong>Permissions:</strong> Ensure Azure app has Mail.Read, Mail.Send, Mail.ReadWrite permissions</li>
              <li><strong>CORS:</strong> Frontend should be on localhost:3000, backend on localhost:5000</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DebugDashboard;