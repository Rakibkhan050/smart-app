import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';

interface NavigationProps {
  transparent?: boolean;
}

const Navigation: React.FC<NavigationProps> = ({ transparent = false }) => {
  const router = useRouter();
  
  const navLinks = [
    { href: '/', label: 'Home', icon: '🏠' },
    { href: '/dashboard-3d', label: '3D Dashboard', icon: '📊' },
    { href: '/dashboard', label: 'Dashboard', icon: '📈' },
    { href: '/notifications', label: 'Notifications', icon: '🔔' },
    { href: '/receipts', label: 'Receipts', icon: '🧾' },
  ];

  const backendRoot = (process.env.NEXT_PUBLIC_API_URL || '').replace(/\/api\/?$/, '') || 'https://smart-app-production.up.railway.app';
  const externalLinks = [
    { href: `${backendRoot}/admin`, label: 'Admin Panel', icon: '⚙️' },
    { href: process.env.NEXT_PUBLIC_API_URL || `${backendRoot}/api`, label: 'API Docs', icon: '📚' },
  ];

  const isActive = (href: string) => router.pathname === href;

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
      transparent ? 'bg-transparent' : 'bg-gradient-to-r from-gray-900 via-blue-900 to-gray-900 shadow-lg'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center space-x-3">
            <div className="text-3xl">🏢</div>
            <div>
              <h1 className="text-xl font-bold text-white">Multi-Purpose POS</h1>
              <p className="text-xs text-gray-300">Business Intelligence Platform</p>
            </div>
          </div>

          {/* Navigation Links */}
          <div className="hidden md:flex items-center space-x-1">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`px-4 py-2 rounded-lg transition-all duration-200 flex items-center space-x-2 ${
                  isActive(link.href)
                    ? 'bg-blue-600 text-white shadow-lg transform scale-105'
                    : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                }`}
              >
                <span>{link.icon}</span>
                <span className="font-medium">{link.label}</span>
              </Link>
            ))}
          </div>

          {/* External Links & User Menu */}
          <div className="flex items-center space-x-2">
            {externalLinks.map((link) => (
              <a
                key={link.href}
                href={link.href}
                target="_blank"
                rel="noopener noreferrer"
                className="px-3 py-2 rounded-lg bg-gray-800 text-gray-300 hover:bg-gray-700 hover:text-white transition-all duration-200 flex items-center space-x-2 text-sm"
              >
                <span>{link.icon}</span>
                <span>{link.label}</span>
                <span className="text-xs">↗</span>
              </a>
            ))}
            
            {/* User Avatar */}
            <div className="ml-3 relative">
              <button className="flex items-center space-x-2 px-3 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 transition-all duration-200">
                <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center font-bold">
                  A
                </div>
                <span className="text-sm font-medium">Admin</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Menu Button */}
      <div className="md:hidden flex justify-center pb-2">
        <div className="flex space-x-2 overflow-x-auto px-4">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`px-3 py-1 rounded-lg whitespace-nowrap text-sm ${
                isActive(link.href)
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-300'
              }`}
            >
              {link.icon} {link.label}
            </Link>
          ))}
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
