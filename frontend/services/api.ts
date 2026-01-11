import axios from 'axios'

const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'

// Show warning if using localhost in production
if (typeof window !== 'undefined' && apiBaseUrl.includes('localhost') && process.env.NODE_ENV === 'production') {
  console.error(
    '%c⚠️ LOCALHOST ERROR',
    'color: red; font-size: 16px; font-weight: bold;',
    '\nYour app is using localhost:8000 which is not accessible from deployed Vercel.\n\n' +
    'FIX: Set NEXT_PUBLIC_API_URL environment variable on Vercel:\n' +
    '  Settings → Environment Variables → NEXT_PUBLIC_API_URL\n' +
    '  Value: https://smart-app-production.up.railway.app/api\n\n' +
    'Then redeploy your Vercel project.'
  )
}

const api = axios.create({
  baseURL: apiBaseUrl,
  headers: { 'Content-Type': 'application/json' }
})

// simple JWT handling helpers
api.interceptors.request.use((config)=>{
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
  if(token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Error interceptor to show localhost warnings
api.interceptors.response.use(
  response => response,
  error => {
    if (error.code === 'ECONNABORTED' || error.message?.includes('localhost')) {
      console.error(
        '%c🚫 Backend Connection Failed',
        'color: #ff4444; font-size: 14px; font-weight: bold;',
        '\nCannot connect to backend. Possible causes:\n' +
        '1. Using localhost URL (set NEXT_PUBLIC_API_URL on Vercel)\n' +
        '2. Railway backend is offline\n' +
        '3. Network/firewall issue\n\n' +
        'Current API URL: ' + apiBaseUrl
      )
    }
    return Promise.reject(error)
  }
)

export default api
