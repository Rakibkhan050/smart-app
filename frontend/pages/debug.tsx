import React from 'react';

const DebugInfo: React.FC = () => {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'NOT SET';
  const appUrl = process.env.NEXT_PUBLIC_APP_URL || 'NOT SET';
  const isDev = process.env.NODE_ENV === 'development';
  const isLocalhost = apiUrl.includes('localhost');

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-8">🔧 Debug Information</h1>

        {/* Environment Status */}
        <div className="bg-gray-800 rounded-lg p-6 mb-6 border border-gray-700">
          <h2 className="text-2xl font-semibold text-white mb-4">Environment Status</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-gray-900 rounded">
              <span className="text-gray-400">Environment:</span>
              <span className={`font-bold ${isDev ? 'text-blue-400' : 'text-green-400'}`}>
                {isDev ? 'Development' : 'Production'}
              </span>
            </div>
            <div className="flex items-center justify-between p-3 bg-gray-900 rounded">
              <span className="text-gray-400">Is Localhost:</span>
              <span className={`font-bold ${isLocalhost ? 'text-red-400' : 'text-green-400'}`}>
                {isLocalhost ? '⚠️ YES (Backend will not work)' : '✅ NO (Using remote backend)'}
              </span>
            </div>
          </div>
        </div>

        {/* API Configuration */}
        <div className="bg-gray-800 rounded-lg p-6 mb-6 border border-gray-700">
          <h2 className="text-2xl font-semibold text-white mb-4">API Configuration</h2>
          <div className="space-y-3">
            <div className="p-3 bg-gray-900 rounded">
              <p className="text-gray-400 text-sm">NEXT_PUBLIC_API_URL</p>
              <p className="text-white font-mono break-all">{apiUrl}</p>
              {apiUrl === 'NOT SET' && (
                <p className="text-red-400 text-sm mt-2">
                  ⚠️ Not set! Set this on Vercel: Settings → Environment Variables
                </p>
              )}
            </div>
            <div className="p-3 bg-gray-900 rounded">
              <p className="text-gray-400 text-sm">NEXT_PUBLIC_APP_URL</p>
              <p className="text-white font-mono break-all">{appUrl}</p>
            </div>
          </div>
        </div>

        {/* Connectivity Tests */}
        <div className="bg-gray-800 rounded-lg p-6 mb-6 border border-gray-700">
          <h2 className="text-2xl font-semibold text-white mb-4">Connectivity Tests</h2>
          <div className="space-y-3">
            <ConnectivityTest 
              label="API Base URL"
              url={apiUrl.replace(/\/$/, '')}
            />
            <ConnectivityTest 
              label="Dashboard Endpoint"
              url={`${apiUrl.replace(/\/$/, '')}/finance/dashboard/3d-metrics/`}
            />
            <ConnectivityTest 
              label="Admin Panel"
              url={apiUrl.replace('/api', '/admin').replace(/\/$/, '')}
            />
          </div>
        </div>

        {/* Setup Instructions */}
        {isLocalhost && (
          <div className="bg-red-900/30 border border-red-600 rounded-lg p-6 mb-6">
            <h2 className="text-2xl font-semibold text-red-400 mb-4">⚠️ Configuration Error</h2>
            <p className="text-red-200 mb-4">
              Your frontend is pointing to localhost:8000, which doesn't work in production.
            </p>
            <ol className="text-red-200 space-y-2 list-decimal list-inside mb-4">
              <li>Go to Vercel project settings</li>
              <li>Add environment variable: <code className="bg-red-950 px-2 py-1 rounded">NEXT_PUBLIC_API_URL</code></li>
              <li>Set value to: <code className="bg-red-950 px-2 py-1 rounded">https://smart-app-production.up.railway.app/api</code></li>
              <li>Redeploy on Vercel</li>
            </ol>
            <a
              href="https://vercel.com/dashboard"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block bg-red-600 hover:bg-red-700 text-white px-6 py-3 rounded-lg font-semibold transition"
            >
              📋 Open Vercel Dashboard
            </a>
          </div>
        )}

        {/* Success State */}
        {!isLocalhost && apiUrl !== 'NOT SET' && (
          <div className="bg-green-900/30 border border-green-600 rounded-lg p-6">
            <h2 className="text-2xl font-semibold text-green-400 mb-4">✅ Configuration Correct</h2>
            <p className="text-green-200">
              Your environment variables are properly set. The app should connect to the Railway backend.
            </p>
          </div>
        )}

        {/* Back Button */}
        <div className="mt-8">
          <a
            href="/"
            className="inline-block bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition"
          >
            ← Back to Home
          </a>
        </div>
      </div>
    </div>
  );
};

interface ConnectivityTestProps {
  label: string;
  url: string;
}

const ConnectivityTest: React.FC<ConnectivityTestProps> = ({ label, url }) => {
  const [status, setStatus] = React.useState<'loading' | 'success' | 'error' | 'idle'>('idle');
  const [message, setMessage] = React.useState<string>('');

  const test = async () => {
    setStatus('loading');
    setMessage('Testing...');
    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
      });
      if (response.ok) {
        setStatus('success');
        setMessage(`✅ Connected (${response.status})`);
      } else {
        setStatus('error');
        setMessage(`❌ Server error (${response.status})`);
      }
    } catch (error: any) {
      setStatus('error');
      setMessage(`❌ ${error.message || 'Connection failed'}`);
    }
  };

  const statusColor = {
    idle: 'bg-gray-900 text-gray-400',
    loading: 'bg-yellow-900/30 text-yellow-400',
    success: 'bg-green-900/30 text-green-400',
    error: 'bg-red-900/30 text-red-400',
  }[status];

  return (
    <div className={`p-3 rounded flex items-center justify-between ${statusColor}`}>
      <div>
        <p className="font-semibold">{label}</p>
        <p className="text-xs opacity-75 font-mono break-all">{url}</p>
        {message && <p className="text-sm mt-1">{message}</p>}
      </div>
      <button
        onClick={test}
        disabled={status === 'loading'}
        className="ml-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded font-semibold whitespace-nowrap transition"
      >
        {status === 'loading' ? '⏳' : '🧪'} Test
      </button>
    </div>
  );
};

export default DebugInfo;
