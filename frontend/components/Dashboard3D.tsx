import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import axios from 'axios';

interface DashboardMetrics {
  date_range: {
    start: string;
    end: string;
    days: number;
  };
  financial: {
    revenue_trend: Array<{ date: string; revenue: number; orders: number }>;
    expense_breakdown: Array<{ category: string; amount: number; count: number }>;
    total_revenue: number;
    total_expenses: number;
    net_profit: number;
    profit_margin: number;
  };
  delivery: {
    status_distribution: Array<{ status: string; count: number; percentage: number }>;
    delivery_map: Array<{ id: number; lat: number; lon: number; status: string; city: string }>;
    completion_rate: number;
    total_deliveries: number;
  };
  inventory: {
    low_stock_count: number;
    total_products: number;
    categories: Array<{ category: string; quantity: number; products: number; low_stock: number }>;
    restock_alerts: Array<any>;
  };
  automation: {
    notification_stats: Array<{ type: string; total: number; read: number; unread: number }>;
    task_execution: Record<string, number>;
  };
}

interface Dashboard3DProps {
  apiBaseUrl?: string;
  authToken?: string;
}

const Dashboard3D: React.FC<Dashboard3DProps> = ({ 
  apiBaseUrl = 'http://localhost:8000/api', 
  authToken 
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<'revenue' | 'expenses' | 'delivery' | 'inventory'>('revenue');
  
  // Three.js references
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
  const controlsRef = useRef<OrbitControls | null>(null);

  // Fetch dashboard metrics
  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        
        // Get token from localStorage or use provided authToken
        const token = authToken || (typeof window !== 'undefined' ? localStorage.getItem('token') : null);
        
        const response = await axios.get(`${apiBaseUrl}/finance/dashboard/3d-metrics/`, {
          headers: token ? { Authorization: `Bearer ${token}` } : {},
          params: { days: 30 }
        });
        setMetrics(response.data);
        setError(null);
      } catch (err: any) {
        console.error('Failed to fetch metrics:', err);
        const errorMsg = err.response?.data?.error || err.response?.data?.detail || 'Failed to load dashboard metrics';
        setError(errorMsg);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [apiBaseUrl, authToken]);

  // Initialize Three.js scene
  useEffect(() => {
    if (!containerRef.current || !metrics) return;

    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0e27);
    scene.fog = new THREE.Fog(0x0a0e27, 50, 200);
    sceneRef.current = scene;

    // Camera setup
    const camera = new THREE.PerspectiveCamera(
      75,
      containerRef.current.clientWidth / containerRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.set(0, 20, 40);
    cameraRef.current = camera;

    // Renderer setup
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    containerRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Controls setup
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.minDistance = 10;
    controls.maxDistance = 100;
    controlsRef.current = controls;

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 20, 10);
    directionalLight.castShadow = true;
    scene.add(directionalLight);

    const pointLight1 = new THREE.PointLight(0x4a90e2, 1, 100);
    pointLight1.position.set(-20, 10, -20);
    scene.add(pointLight1);

    const pointLight2 = new THREE.PointLight(0xe24a90, 1, 100);
    pointLight2.position.set(20, 10, 20);
    scene.add(pointLight2);

    // Grid helper
    const gridHelper = new THREE.GridHelper(100, 20, 0x444444, 0x222222);
    scene.add(gridHelper);

    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    };
    animate();

    // Handle window resize
    const handleResize = () => {
      if (!containerRef.current || !camera || !renderer) return;
      camera.aspect = containerRef.current.clientWidth / containerRef.current.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    };
    window.addEventListener('resize', handleResize);

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      if (containerRef.current && renderer.domElement) {
        containerRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [metrics]);

  // Update visualization based on selected view
  useEffect(() => {
    if (!sceneRef.current || !metrics) return;

    // Clear existing objects (except lights and helpers)
    const scene = sceneRef.current;
    const objectsToRemove = scene.children.filter(
      child => child instanceof THREE.Mesh || child instanceof THREE.Group
    );
    objectsToRemove.forEach(obj => scene.remove(obj));

    // Render based on view
    switch (view) {
      case 'revenue':
        renderRevenueChart(scene, metrics.financial.revenue_trend);
        break;
      case 'expenses':
        renderExpenseChart(scene, metrics.financial.expense_breakdown);
        break;
      case 'delivery':
        renderDeliveryMap(scene, metrics.delivery.delivery_map);
        break;
      case 'inventory':
        renderInventoryChart(scene, metrics.inventory.categories);
        break;
    }
  }, [view, metrics]);

  // Render 3D revenue bar chart
  const renderRevenueChart = (scene: THREE.Scene, data: Array<any>) => {
    if (data.length === 0) return;

    const maxRevenue = Math.max(...data.map(d => d.revenue));
    const barWidth = 1.5;
    const spacing = 0.5;
    const totalWidth = (barWidth + spacing) * data.length;
    const startX = -totalWidth / 2;

    data.forEach((day, index) => {
      const height = (day.revenue / maxRevenue) * 20 + 1;
      const geometry = new THREE.BoxGeometry(barWidth, height, barWidth);
      const material = new THREE.MeshStandardMaterial({
        color: new THREE.Color().setHSL(0.5 + (day.revenue / maxRevenue) * 0.3, 0.7, 0.6),
        metalness: 0.3,
        roughness: 0.4
      });
      const bar = new THREE.Mesh(geometry, material);
      bar.position.x = startX + index * (barWidth + spacing);
      bar.position.y = height / 2;
      bar.castShadow = true;
      bar.receiveShadow = true;
      scene.add(bar);

      // Add glow effect for top performers
      if (day.revenue > maxRevenue * 0.7) {
        const glowGeometry = new THREE.BoxGeometry(barWidth * 1.2, height * 1.05, barWidth * 1.2);
        const glowMaterial = new THREE.MeshBasicMaterial({
          color: 0x00ff88,
          transparent: true,
          opacity: 0.3
        });
        const glow = new THREE.Mesh(glowGeometry, glowMaterial);
        glow.position.copy(bar.position);
        scene.add(glow);
      }
    });
  };

  // Render 3D expense pie chart (as stacked cylinders)
  const renderExpenseChart = (scene: THREE.Scene, data: Array<any>) => {
    if (data.length === 0) return;

    const totalExpense = data.reduce((sum, e) => sum + e.amount, 0);
    let currentAngle = 0;
    const radius = 15;

    const colors = [0x3498db, 0xe74c3c, 0xf39c12, 0x2ecc71, 0x9b59b6, 0x1abc9c, 0xe67e22];

    data.forEach((expense, index) => {
      const angle = (expense.amount / totalExpense) * Math.PI * 2;
      const segments = Math.max(8, Math.floor(angle / (Math.PI / 16)));

      const shape = new THREE.Shape();
      shape.moveTo(0, 0);
      for (let i = 0; i <= segments; i++) {
        const a = currentAngle + (angle * i) / segments;
        shape.lineTo(Math.cos(a) * radius, Math.sin(a) * radius);
      }
      shape.lineTo(0, 0);

      const extrudeSettings = {
        depth: 5,
        bevelEnabled: true,
        bevelThickness: 0.5,
        bevelSize: 0.3,
        bevelSegments: 3
      };

      const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
      const material = new THREE.MeshStandardMaterial({
        color: colors[index % colors.length],
        metalness: 0.2,
        roughness: 0.5
      });

      const mesh = new THREE.Mesh(geometry, material);
      mesh.rotation.x = -Math.PI / 2;
      mesh.position.y = 2.5;
      mesh.castShadow = true;
      scene.add(mesh);

      currentAngle += angle;
    });
  };

  // Render 3D delivery map (globe with pins)
  const renderDeliveryMap = (scene: THREE.Scene, data: Array<any>) => {
    if (data.length === 0) return;

    // Create simplified globe
    const globeGeometry = new THREE.SphereGeometry(12, 32, 32);
    const globeMaterial = new THREE.MeshStandardMaterial({
      color: 0x1a237e,
      metalness: 0.3,
      roughness: 0.7,
      wireframe: true,
      transparent: true,
      opacity: 0.3
    });
    const globe = new THREE.Mesh(globeGeometry, globeMaterial);
    scene.add(globe);

    // Add delivery markers
    const statusColors: Record<string, number> = {
      pending: 0xffa500,
      assigned: 0x4169e1,
      picked_up: 0x9370db,
      in_transit: 0x1e90ff,
      delivered: 0x32cd32,
      failed: 0xff4444
    };

    data.forEach(delivery => {
      // Convert lat/lon to 3D position on sphere
      const phi = (90 - delivery.lat) * (Math.PI / 180);
      const theta = (delivery.lon + 180) * (Math.PI / 180);
      const radius = 12.5;

      const x = -(radius * Math.sin(phi) * Math.cos(theta));
      const y = radius * Math.cos(phi);
      const z = radius * Math.sin(phi) * Math.sin(theta);

      // Create marker
      const markerGeometry = new THREE.SphereGeometry(0.5, 8, 8);
      const markerMaterial = new THREE.MeshStandardMaterial({
        color: statusColors[delivery.status] || 0xffffff,
        emissive: statusColors[delivery.status] || 0xffffff,
        emissiveIntensity: 0.5
      });
      const marker = new THREE.Mesh(markerGeometry, markerMaterial);
      marker.position.set(x, y, z);
      scene.add(marker);

      // Add connection line to globe center (for in-transit deliveries)
      if (delivery.status === 'in_transit') {
        const lineGeometry = new THREE.BufferGeometry().setFromPoints([
          new THREE.Vector3(x, y, z),
          new THREE.Vector3(0, 0, 0)
        ]);
        const lineMaterial = new THREE.LineBasicMaterial({
          color: 0x1e90ff,
          transparent: true,
          opacity: 0.3
        });
        const line = new THREE.Line(lineGeometry, lineMaterial);
        scene.add(line);
      }
    });

    // Rotate globe slowly
    const rotateGlobe = () => {
      globe.rotation.y += 0.001;
      requestAnimationFrame(rotateGlobe);
    };
    rotateGlobe();
  };

  // Render 3D inventory chart (clustered bars by category)
  const renderInventoryChart = (scene: THREE.Scene, data: Array<any>) => {
    if (data.length === 0) return;

    const maxQuantity = Math.max(...data.map(c => c.quantity));
    const barWidth = 2;
    const spacing = 1;
    const totalWidth = (barWidth + spacing) * data.length;
    const startX = -totalWidth / 2;

    data.forEach((category, index) => {
      // Main quantity bar
      const height = (category.quantity / maxQuantity) * 15 + 1;
      const geometry = new THREE.BoxGeometry(barWidth, height, barWidth);
      const material = new THREE.MeshStandardMaterial({
        color: category.low_stock > 0 ? 0xff4444 : 0x44ff44,
        metalness: 0.4,
        roughness: 0.3
      });
      const bar = new THREE.Mesh(geometry, material);
      bar.position.x = startX + index * (barWidth + spacing);
      bar.position.y = height / 2;
      bar.castShadow = true;
      scene.add(bar);

      // Low stock indicator
      if (category.low_stock > 0) {
        const alertGeometry = new THREE.ConeGeometry(0.5, 1.5, 4);
        const alertMaterial = new THREE.MeshStandardMaterial({
          color: 0xffaa00,
          emissive: 0xffaa00,
          emissiveIntensity: 0.5
        });
        const alert = new THREE.Mesh(alertGeometry, alertMaterial);
        alert.position.x = bar.position.x;
        alert.position.y = height + 1;
        alert.rotation.y = Math.PI / 4;
        scene.add(alert);
      }
    });
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900">
        <div className="relative">
          <div className="w-20 h-20 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-4xl">📊</div>
          </div>
        </div>
        <div className="mt-6 text-white text-2xl font-bold animate-pulse">Loading 3D Dashboard...</div>
        <div className="mt-2 text-gray-400 text-sm">Initializing Three.js engine</div>
      </div>
    );
  }

  if (error) {
    const backendRoot = (apiBaseUrl || '').replace(/\/api\/?$/, '') || 'https://smart-app-production.up.railway.app';
    const isNoTenantError = error.includes('business') || error.includes('tenant');
    
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-gradient-to-br from-gray-900 via-red-900 to-gray-900 px-4">
        <div className="max-w-2xl w-full bg-gray-800/50 backdrop-blur-sm rounded-2xl p-8 shadow-2xl border border-red-500/30">
          <div className="text-6xl mb-4 text-center">⚠️</div>
          <div className="text-red-400 text-2xl font-semibold mb-3 text-center">Error Loading Dashboard</div>
          <div className="text-red-300 text-base mb-6 text-center">{error}</div>
          
          {isNoTenantError && (
            <div className="bg-yellow-900/30 border border-yellow-600/50 rounded-lg p-4 mb-6">
              <div className="flex items-start space-x-3">
                <span className="text-2xl">💡</span>
                <div>
                  <div className="text-yellow-400 font-semibold mb-2">Quick Fix:</div>
                  <ol className="text-yellow-200 text-sm space-y-2 list-decimal list-inside">
                    <li>Go to the Admin Panel</li>
                    <li>Create your first Business/Tenant</li>
                    <li>Come back and refresh this page</li>
                  </ol>
                </div>
              </div>
            </div>
          )}
          
          <div className="flex flex-col sm:flex-row gap-3">
            <button 
              onClick={() => window.location.reload()} 
              className="flex-1 px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors duration-200 font-medium"
            >
              🔄 Retry
            </button>
            {isNoTenantError && (
              <a
                href={`${backendRoot}/admin`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors duration-200 text-center font-medium"
              >
                ⚙️ Open Admin
              </a>
            )}
            <a
              href="/"
              className="flex-1 px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors duration-200 text-center font-medium"
            >
              🏠 Go Home
            </a>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="relative w-full h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-gray-900">
      {/* Control Panel */}
      <div className="absolute top-4 left-4 z-10 bg-gradient-to-br from-gray-800 to-gray-900 bg-opacity-95 backdrop-blur-sm rounded-xl p-5 text-white shadow-2xl border border-gray-700">
        <div className="flex items-center space-x-2 mb-4">
          <div className="text-2xl">📊</div>
          <h2 className="text-xl font-bold">3D Dashboard</h2>
        </div>
        
        <div className="space-y-2">
          <button
            onClick={() => setView('revenue')}
            className={`w-full px-4 py-3 rounded-lg font-semibold transition-all duration-300 flex items-center justify-between ${
              view === 'revenue' 
                ? 'bg-gradient-to-r from-blue-600 to-blue-700 shadow-lg transform scale-105' 
                : 'bg-gray-700 hover:bg-gray-600 hover:shadow-md'
            }`}
          >
            <span className="flex items-center space-x-2">
              <span>📈</span>
              <span>Revenue Trend</span>
            </span>
            {view === 'revenue' && <span>✓</span>}
          </button>
          
          <button
            onClick={() => setView('expenses')}
            className={`w-full px-4 py-3 rounded-lg font-semibold transition-all duration-300 flex items-center justify-between ${
              view === 'expenses' 
                ? 'bg-gradient-to-r from-red-600 to-red-700 shadow-lg transform scale-105' 
                : 'bg-gray-700 hover:bg-gray-600 hover:shadow-md'
            }`}
          >
            <span className="flex items-center space-x-2">
              <span>💰</span>
              <span>Expense Breakdown</span>
            </span>
            {view === 'expenses' && <span>✓</span>}
          </button>
          
          <button
            onClick={() => setView('delivery')}
            className={`w-full px-4 py-3 rounded-lg font-semibold transition-all duration-300 flex items-center justify-between ${
              view === 'delivery' 
                ? 'bg-gradient-to-r from-green-600 to-green-700 shadow-lg transform scale-105' 
                : 'bg-gray-700 hover:bg-gray-600 hover:shadow-md'
            }`}
          >
            <span className="flex items-center space-x-2">
              <span>🚚</span>
              <span>Delivery Map</span>
            </span>
            {view === 'delivery' && <span>✓</span>}
          </button>
          
          <button
            onClick={() => setView('inventory')}
            className={`w-full px-4 py-3 rounded-lg font-semibold transition-all duration-300 flex items-center justify-between ${
              view === 'inventory' 
                ? 'bg-gradient-to-r from-purple-600 to-purple-700 shadow-lg transform scale-105' 
                : 'bg-gray-700 hover:bg-gray-600 hover:shadow-md'
            }`}
          >
            <span className="flex items-center space-x-2">
              <span>📦</span>
              <span>Inventory Status</span>
            </span>
            {view === 'inventory' && <span>✓</span>}
          </button>
        </div>

        {metrics && (
          <div className="text-sm space-y-2 border-t border-gray-700 pt-4 mt-4">
            <div className="flex justify-between items-center p-2 bg-green-900/30 rounded-lg">
              <span className="text-gray-300">💵 Net Profit:</span>
              <span className="font-bold text-green-400 text-lg">
                ${metrics.financial.net_profit.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between items-center p-2 bg-blue-900/30 rounded-lg">
              <span className="text-gray-300">🚚 Deliveries:</span>
              <span className="font-bold text-blue-400">{metrics.delivery.total_deliveries}</span>
            </div>
            <div className="flex justify-between items-center p-2 bg-red-900/30 rounded-lg">
              <span className="text-gray-300">⚠️ Low Stock:</span>
              <span className="font-bold text-red-400">{metrics.inventory.low_stock_count}</span>
            </div>
            <div className="flex justify-between items-center p-2 bg-purple-900/30 rounded-lg">
              <span className="text-gray-300">✓ Completion:</span>
              <span className="font-bold text-purple-400">
                {metrics.delivery.completion_rate.toFixed(1)}%
              </span>
            </div>
          </div>
        )}
        
        {/* Quick Actions */}
        <div className="mt-4 pt-4 border-t border-gray-700 space-y-2">
          <a 
            href={(process.env.NEXT_PUBLIC_API_URL || '').replace(/\/api\/?$/, '') || 'https://smart-app-production.up.railway.app/admin'} 
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-center text-sm transition-colors duration-200"
          >
            ⚙️ Open Admin Panel
          </a>
          <a 
            href="/" 
            className="block w-full px-3 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-center text-sm transition-colors duration-200"
          >
            🏠 Back to Home
          </a>
        </div>
      </div>

      {/* Info Panel */}
      <div className="absolute bottom-4 left-4 z-10 bg-gradient-to-br from-gray-800 to-gray-900 bg-opacity-95 backdrop-blur-sm rounded-xl p-5 text-white text-sm max-w-md shadow-2xl border border-gray-700">
        <div className="flex items-center space-x-2 mb-3">
          <span className="text-xl">🎮</span>
          <h3 className="font-bold text-lg">Interactive Controls</h3>
        </div>
        <ul className="space-y-2 text-gray-300">
          <li className="flex items-center space-x-2">
            <span className="text-blue-400">🖱️</span>
            <span><strong>Left-click + drag</strong> → Rotate view</span>
          </li>
          <li className="flex items-center space-x-2">
            <span className="text-green-400">🔍</span>
            <span><strong>Mouse wheel</strong> → Zoom in/out</span>
          </li>
          <li className="flex items-center space-x-2">
            <span className="text-purple-400">👆</span>
            <span><strong>Right-click + drag</strong> → Pan camera</span>
          </li>
        </ul>
        <div className="mt-4 pt-3 border-t border-gray-700 text-xs text-gray-400">
          <div className="flex items-center justify-between">
            <span>🔄 Auto-refresh: 60s</span>
            <span className="px-2 py-1 bg-green-900/30 text-green-400 rounded">● Live</span>
          </div>
        </div>
      </div>
      
      {/* Top Navigation Bar */}
      <div className="absolute top-4 right-4 z-10 flex items-center space-x-2">
        <div className="bg-gradient-to-br from-gray-800 to-gray-900 bg-opacity-95 backdrop-blur-sm rounded-lg px-4 py-2 text-white text-sm shadow-lg border border-gray-700">
          <span className="text-gray-400">Date Range:</span>
          <span className="ml-2 font-semibold text-blue-400">Last 30 Days</span>
        </div>
      </div>

      {/* 3D Canvas */}
      <div ref={containerRef} className="w-full h-full" />
    </div>
  );
};

export default Dashboard3D;
