import React from 'react';
import Head from 'next/head';
import Link from 'next/link';

const HomePage: React.FC = () => {
  const features = [
    {
      title: '3D Dashboard',
      description: 'Immersive 3D visualization of business metrics with real-time data',
      icon: '📊',
      href: '/dashboard-3d',
      color: 'from-blue-600 to-blue-700',
      stats: 'Real-time analytics'
    },
    {
      title: 'POS System',
      description: 'Complete point-of-sale with order management and checkout',
      icon: '🛒',
      href: '/dashboard',
      color: 'from-green-600 to-green-700',
      stats: 'Fast checkout'
    },
    {
      title: 'Inventory Manager',
      description: 'Track products, stock levels, and automatic low-stock alerts',
      icon: '📦',
      href: 'http://localhost:8000/admin/inventory/product/',
      color: 'from-purple-600 to-purple-700',
      external: true,
      stats: 'Auto alerts'
    },
    {
      title: 'Customer CRM',
      description: 'Manage customers, loyalty points, and purchase history',
      icon: '👥',
      href: 'http://localhost:8000/admin/crm/customer/',
      color: 'from-pink-600 to-pink-700',
      external: true,
      stats: 'Loyalty system'
    },
    {
      title: 'Delivery Tracker',
      description: 'GPS tracking, delivery personnel, and status management',
      icon: '🚚',
      href: 'http://localhost:8000/admin/delivery/delivery/',
      color: 'from-yellow-600 to-yellow-700',
      external: true,
      stats: 'GPS enabled'
    },
    {
      title: 'Payment Gateway',
      description: 'Visa, Mastercard, Amex, Apple Pay, Google Pay, bKash, Nagad',
      icon: '💳',
      href: 'http://localhost:8000/admin/payments/payment/',
      color: 'from-indigo-600 to-indigo-700',
      external: true,
      stats: 'Multi-payment'
    },
    {
      title: 'Finance Reports',
      description: 'P&L analysis, VAT calculation, expense tracking',
      icon: '💰',
      href: 'http://localhost:8000/admin/finance/expense/',
      color: 'from-red-600 to-red-700',
      external: true,
      stats: 'Tax ready'
    },
    {
      title: 'User Management',
      description: 'Role-based access: Owner, Admin, Manager, Cashier',
      icon: '⚙️',
      href: '/admin/users',
      color: 'from-cyan-600 to-cyan-700',
      stats: 'RBAC system'
    },
  ];

  const stats = [
    { label: 'Products', value: '2,500+', icon: '📦', color: 'text-blue-400' },
    { label: 'Revenue', value: '$125K', icon: '💰', color: 'text-green-400' },
    { label: 'Customers', value: '1,834', icon: '👥', color: 'text-purple-400' },
    { label: 'Orders', value: '8,942', icon: '🛒', color: 'text-yellow-400' },
  ];

  const systemFeatures = [
    '✅ Universal Inventory Management (Grocery, Electronics, Pharmacy)',
    '✅ Global Payment Gateway (Visa, Mastercard, Amex, Apple Pay, Google Pay)',
    '✅ Local Payment Support (bKash, Nagad, Rocket)',
    '✅ GPS-Enabled Delivery Tracking',
    '✅ Customer CRM with Loyalty Points',
    '✅ Automated PDF Receipts',
    '✅ P&L Reports & VAT Calculator',
    '✅ Role-Based Access Control (Owner, Admin, Manager, Cashier)',
    '✅ Low Stock Alerts & Notifications',
    '✅ Supplier Management',
    '✅ Three.js 3D Analytics Dashboard',
    '✅ Multi-Tenant Support'
  ];

  return (
    <>
      <Head>
        <title>Multi-Purpose POS | Business Management Platform</title>
        <meta name="description" content="Complete business management solution with 3D analytics" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🏢</text></svg>" />
      </Head>

      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900">
        {/* Header */}
        <header className="bg-gradient-to-r from-gray-900 via-blue-900 to-gray-900 shadow-xl border-b border-gray-700">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="text-5xl">🏢</div>
                <div>
                  <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                    Multi-Purpose POS
                  </h1>
                  <p className="text-gray-400 text-sm">Advanced Business Intelligence Platform</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <a
                  href="http://localhost:8000/admin"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-4 py-2 bg-gray-800 hover:bg-gray-700 text-white rounded-lg transition-colors duration-200 flex items-center space-x-2"
                >
                  <span>⚙️</span>
                  <span>Admin</span>
                </a>
                <div className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg flex items-center space-x-2">
                  <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center font-bold">
                    A
                  </div>
                  <span>Admin User</span>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Hero Section */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-white mb-4">
              Multi-Purpose Global Business Manager & POS System
            </h2>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Complete, professional, and universal business management solution with advanced features for retail, grocery, pharmacy, electronics, and more
            </p>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-12">
            {stats.map((stat, index) => (
              <div
                key={index}
                className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 border border-gray-700 hover:border-gray-600 transition-all duration-300 hover:scale-105 shadow-xl"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm mb-1">{stat.label}</p>
                    <p className={`text-3xl font-bold ${stat.color}`}>{stat.value}</p>
                  </div>
                  <div className="text-4xl opacity-50">{stat.icon}</div>
                </div>
              </div>
            ))}
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
            {features.map((feature, index) => (
              feature.external ? (
                <a
                  key={index}
                  href={feature.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="group relative bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 border border-gray-700 hover:border-gray-600 transition-all duration-300 hover:scale-105 shadow-xl overflow-hidden"
                >
                  <div className={`absolute inset-0 bg-gradient-to-br ${feature.color} opacity-0 group-hover:opacity-10 transition-opacity duration-300`}></div>
                  <div className="relative">
                    <div className="text-5xl mb-3">{feature.icon}</div>
                    <div className={`px-2 py-1 bg-gradient-to-r ${feature.color} rounded-full text-white text-xs font-semibold mb-3 inline-block`}>
                      {feature.stats}
                    </div>
                    <h3 className="text-lg font-bold text-white mb-2 flex items-center">
                      {feature.title}
                      <span className="ml-2 text-xs opacity-50">↗</span>
                    </h3>
                    <p className="text-gray-400 text-sm">{feature.description}</p>
                  </div>
                </a>
              ) : (
                <Link
                  key={index}
                  href={feature.href}
                  className="group relative bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 border border-gray-700 hover:border-gray-600 transition-all duration-300 hover:scale-105 shadow-xl overflow-hidden"
                >
                  <div className={`absolute inset-0 bg-gradient-to-br ${feature.color} opacity-0 group-hover:opacity-10 transition-opacity duration-300`}></div>
                  <div className="relative">
                    <div className="text-5xl mb-3">{feature.icon}</div>
                    <div className={`px-2 py-1 bg-gradient-to-r ${feature.color} rounded-full text-white text-xs font-semibold mb-3 inline-block`}>
                      {feature.stats}
                    </div>
                    <h3 className="text-lg font-bold text-white mb-2">{feature.title}</h3>
                    <p className="text-gray-400 text-sm">{feature.description}</p>
                  </div>
                </Link>
              )
            ))}
          </div>

          {/* System Features List */}
          <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-2xl p-8 border border-gray-700 shadow-xl mb-12">
            <h3 className="text-2xl font-bold text-white mb-6 flex items-center">
              <span className="text-3xl mr-3">🚀</span>
              Complete System Features
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {systemFeatures.map((feature, index) => (
                <div key={index} className="text-gray-300 flex items-start space-x-2">
                  <span className="text-green-400 mt-1">✓</span>
                  <span>{feature.slice(2)}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Call-to-Action Buttons */}
          <div className="flex flex-col md:flex-row items-center justify-center gap-4 mb-6">
            <Link
              href="/dashboard-3d"
              className="inline-flex items-center space-x-3 px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white text-xl font-bold rounded-xl shadow-2xl transition-all duration-300 hover:scale-110"
            >
              <span className="text-2xl">🚀</span>
              <span>Launch 3D Dashboard</span>
              <span>→</span>
            </Link>
            <a
              href="http://localhost:8000/admin"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center space-x-3 px-8 py-4 bg-gradient-to-r from-red-600 to-pink-600 hover:from-red-700 hover:to-pink-700 text-white text-xl font-bold rounded-xl shadow-2xl transition-all duration-300 hover:scale-110"
            >
              <span className="text-2xl">⚙️</span>
              <span>Open Admin Panel</span>
              <span>↗</span>
            </a>
          </div>
          
          <p className="text-gray-500 text-center mb-4">
            Complete Multi-Purpose Global Business Manager & POS System. Built with Next.js, Django, PostgreSQL, and Three.js
          </p>
        </section>

        {/* Footer */}
        <footer className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 mt-12 border-t border-gray-800">
          <div className="text-center text-gray-400 text-sm">
            <p>© 2026 Multi-Purpose POS. Built with Next.js, Django, and Three.js</p>
            <p className="mt-2">
              <span className="inline-flex items-center space-x-4">
                <span>✅ 82 Tests Passing</span>
                <span>•</span>
                <span>🔒 Secure</span>
                <span>•</span>
                <span>⚡ Fast</span>
                <span>•</span>
                <span>📱 Responsive</span>
              </span>
            </p>
          </div>
        </footer>
      </div>
    </>
  );
};

export default HomePage;

// Disable static optimization to avoid prerender errors on Vercel
export async function getServerSideProps() {
  return { props: {} }
}
