import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        {/* PWA Meta Tags */}
        <meta name="application-name" content="Smart Multi-Tenant SaaS" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="SmartApp" />
        <meta name="description" content="Professional Multi-tenant SaaS platform for Agricultural Business Management" />
        <meta name="format-detection" content="telephone=no" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="theme-color" content="#10b981" />
        
        {/* Apple Touch Icons */}
        <link rel="apple-touch-icon" href="/icon-152.png" />
        <link rel="apple-touch-icon" sizes="152x152" href="/icon-152.png" />
        <link rel="apple-touch-icon" sizes="180x180" href="/icon-192.png" />
        <link rel="apple-touch-icon" sizes="167x167" href="/icon-192.png" />
        
        {/* Favicon */}
        <link rel="icon" type="image/png" sizes="32x32" href="/icon-96.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/icon-72.png" />
        
        {/* Manifest */}
        <link rel="manifest" href="/manifest.json" />
        
        {/* Safari Pinned Tab */}
        <link rel="mask-icon" href="/icon-192.png" color="#10b981" />
        
        {/* MS Tile */}
        <meta name="msapplication-TileColor" content="#10b981" />
        <meta name="msapplication-tap-highlight" content="no" />
        <meta name="msapplication-config" content="/browserconfig.xml" />
        
        {/* Twitter Card */}
        <meta name="twitter:card" content="summary" />
        <meta name="twitter:url" content="https://yourapp.com" />
        <meta name="twitter:title" content="Smart Multi-Tenant SaaS" />
        <meta name="twitter:description" content="Professional Multi-tenant SaaS platform for Agricultural Business" />
        <meta name="twitter:image" content="/icon-192.png" />
        <meta name="twitter:creator" content="@yourhandle" />
        
        {/* Open Graph */}
        <meta property="og:type" content="website" />
        <meta property="og:title" content="Smart Multi-Tenant SaaS" />
        <meta property="og:description" content="Professional Multi-tenant SaaS platform for Agricultural Business" />
        <meta property="og:site_name" content="SmartApp" />
        <meta property="og:url" content="https://yourapp.com" />
        <meta property="og:image" content="/icon-512.png" />
      </Head>
      <body>
        <Main />
        <NextScript />
        
        {/* Register Service Worker */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              if ('serviceWorker' in navigator) {
                window.addEventListener('load', function() {
                  navigator.serviceWorker.register('/sw.js').then(
                    function(registration) {
                      console.log('Service Worker registered:', registration.scope);
                    },
                    function(err) {
                      console.log('Service Worker registration failed:', err);
                    }
                  );
                });
              }
            `,
          }}
        />
      </body>
    </Html>
  );
}
