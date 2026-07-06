'use client'

/**
 * API Configuration Check Page
 * Shows the current API URL configuration
 */

export default function ApiCheckPage() {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <div className="max-w-2xl w-full bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold mb-6 text-gray-900">
          API Configuration Check
        </h1>
        
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h2 className="font-semibold text-blue-900 mb-2">
              Backend API URL:
            </h2>
            <code className="text-sm bg-blue-100 px-3 py-2 rounded block text-blue-800">
              {apiUrl}
            </code>
          </div>
          
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h2 className="font-semibold text-gray-900 mb-2">
              Full API Base URL:
            </h2>
            <code className="text-sm bg-gray-100 px-3 py-2 rounded block text-gray-800">
              {apiUrl}/api/v1
            </code>
          </div>
          
          <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <h3 className="font-semibold text-yellow-900 mb-2">
              ℹ️ Note:
            </h3>
            <p className="text-sm text-yellow-800">
              If this shows <code className="bg-yellow-100 px-1 rounded">localhost:8000</code> on Render,
              the environment variable <code className="bg-yellow-100 px-1 rounded">NEXT_PUBLIC_API_URL</code> was not set during build.
            </p>
            <p className="text-sm text-yellow-800 mt-2">
              To fix: Go to Render dashboard → Frontend service → Environment → Add 
              <code className="bg-yellow-100 px-1 rounded mx-1">NEXT_PUBLIC_API_URL</code> → 
              Click "Clear build cache & deploy"
            </p>
          </div>
        </div>
        
        <div className="mt-6">
          <a 
            href="/login" 
            className="inline-block bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Go to Login
          </a>
        </div>
      </div>
    </div>
  )
}
