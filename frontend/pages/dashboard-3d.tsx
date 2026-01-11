import React from 'react';
import { GetServerSideProps } from 'next';
import dynamic from 'next/dynamic';
import Head from 'next/head';
import Navigation from '../components/Navigation';

// Dynamically import Three.js component (client-side only)
const Dashboard3D = dynamic(() => import('../components/Dashboard3D'), {
  ssr: false,
  loading: () => (
    <div className="flex flex-col items-center justify-center h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900">
      <div className="relative">
        <div className="w-20 h-20 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-4xl">📊</div>
        </div>
      </div>
      <div className="mt-6 text-white text-2xl font-bold animate-pulse">Initializing 3D Engine...</div>
      <div className="mt-2 text-gray-400 text-sm">Loading Three.js components</div>
    </div>
  )
});

interface Dashboard3DPageProps {
  apiBaseUrl: string;
  authToken?: string;
}

const Dashboard3DPage: React.FC<Dashboard3DPageProps> = ({ apiBaseUrl, authToken }) => {
  return (
    <>
      <Head>
        <title>3D Business Dashboard | Multi-Purpose POS</title>
        <meta name="description" content="Interactive 3D visualization of business metrics" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📊</text></svg>" />
      </Head>
      <div className="relative">
        <Dashboard3D apiBaseUrl={apiBaseUrl} authToken={authToken} />
        
        {/* Floating Back Button */}
        <a
          href="/"
          className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-full shadow-2xl transition-all duration-300 hover:scale-110 flex items-center space-x-2 font-semibold"
        >
          <span>←</span>
          <span>Exit 3D View</span>
        </a>
      </div>
    </>
  );
};

export const getServerSideProps: GetServerSideProps = async (context) => {
  // Get auth token from cookies/session
  const authToken = context.req.cookies['auth_token'] || null;
  
  return {
    props: {
      apiBaseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
      authToken
    }
  };
};

export default Dashboard3DPage;
