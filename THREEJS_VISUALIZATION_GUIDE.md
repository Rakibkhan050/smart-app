# Financial Data Visualization with Three.js

This guide explains how to visualize financial reports using Three.js for immersive 3D data representation.

## Overview

Three.js can transform traditional 2D charts into interactive 3D visualizations, making financial data more engaging and easier to understand. This is particularly useful for:

- **P&L Reports**: 3D bar charts showing revenue vs expenses over time
- **Expense Breakdown**: 3D pie charts or stacked bars by category
- **VAT Analysis**: 3D scatter plots showing tax collected vs paid
- **Trend Analysis**: 3D line graphs showing financial trends across multiple dimensions

## Architecture

```
Frontend (React/Vue/Angular)
    ↓
Fetch financial data from API endpoints
    ↓
Transform data into 3D-friendly format
    ↓
Render with Three.js
```

## API Endpoints for Visualization

### 1. Dashboard Metrics
```
GET /api/finance/reports/dashboard/
Query Params:
  - start_date: YYYY-MM-DD
  - end_date: YYYY-MM-DD

Response:
{
  "total_revenue": "10000.00",
  "total_expenses": "6000.00",
  "net_profit": "4000.00",
  "profit_margin": "40.00",
  "expense_by_category": {
    "cogs": "3000.00",
    "rent": "1500.00",
    "salaries": "1000.00",
    ...
  }
}
```

### 2. P&L Report
```
GET /api/finance/reports/profit_loss/
Query Params:
  - start_date: YYYY-MM-DD
  - end_date: YYYY-MM-DD

Response:
{
  "total_revenue": "10000.00",
  "cogs": "3000.00",
  "operating_expenses": "3000.00",
  "gross_profit": "7000.00",
  "net_profit": "4000.00",
  "total_tax_collected": "1000.00",
  "total_tax_paid": "500.00",
  "net_tax_liability": "500.00"
}
```

### 3. VAT Aggregation
```
GET /api/finance/reports/vat_aggregation/
Query Params:
  - start_date: YYYY-MM-DD
  - end_date: YYYY-MM-DD

Response:
{
  "vat_on_sales": "1500.00",
  "vat_on_purchases": "900.00",
  "net_vat_payable": "600.00",
  "vat_by_rate": [
    {
      "rate_name": "VAT 15%",
      "rate_percentage": 15.0,
      "amount": 450.00
    }
  ]
}
```

## Three.js Implementation Examples

### 1. 3D Bar Chart for P&L Comparison

```javascript
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

class FinancialBarChart {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.scene = new THREE.Scene();
    this.camera = new THREE.PerspectiveCamera(
      75,
      this.container.clientWidth / this.container.clientHeight,
      0.1,
      1000
    );
    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    this.container.appendChild(this.renderer.domElement);

    // Add lighting
    const ambientLight = new THREE.AmbientLight(0x404040);
    this.scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
    directionalLight.position.set(10, 10, 10);
    this.scene.add(directionalLight);

    // Add orbit controls
    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.camera.position.set(10, 10, 20);
    this.controls.update();

    // Add grid
    const gridHelper = new THREE.GridHelper(20, 20);
    this.scene.add(gridHelper);
  }

  async loadPLData(startDate, endDate) {
    const response = await fetch(
      `/api/finance/reports/profit_loss/?start_date=${startDate}&end_date=${endDate}`
    );
    const data = await response.json();
    this.renderPLBars(data);
  }

  renderPLBars(data) {
    const barData = [
      { label: 'Revenue', value: parseFloat(data.total_revenue), color: 0x4caf50 },
      { label: 'COGS', value: parseFloat(data.cogs), color: 0xff9800 },
      { label: 'OpEx', value: parseFloat(data.operating_expenses), color: 0xff5722 },
      { label: 'Net Profit', value: parseFloat(data.net_profit), color: 0x2196f3 }
    ];

    const barWidth = 2;
    const barSpacing = 3;
    const maxHeight = Math.max(...barData.map(d => d.value)) / 1000;

    barData.forEach((item, index) => {
      const height = item.value / 1000; // Scale down for visualization
      const geometry = new THREE.BoxGeometry(barWidth, height, barWidth);
      const material = new THREE.MeshPhongMaterial({ color: item.color });
      const bar = new THREE.Mesh(geometry, material);

      bar.position.x = (index - barData.length / 2) * barSpacing;
      bar.position.y = height / 2;

      this.scene.add(bar);

      // Add label using sprite
      this.addLabel(item.label, bar.position.x, height + 1, 0);
    });
  }

  addLabel(text, x, y, z) {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    context.font = 'Bold 48px Arial';
    context.fillStyle = 'white';
    context.fillText(text, 0, 48);

    const texture = new THREE.CanvasTexture(canvas);
    const spriteMaterial = new THREE.SpriteMaterial({ map: texture });
    const sprite = new THREE.Sprite(spriteMaterial);
    sprite.position.set(x, y, z);
    sprite.scale.set(4, 2, 1);
    this.scene.add(sprite);
  }

  animate() {
    requestAnimationFrame(() => this.animate());
    this.controls.update();
    this.renderer.render(this.scene, this.camera);
  }
}

// Usage
const chart = new FinancialBarChart('chart-container');
chart.loadPLData('2026-01-01', '2026-01-31');
chart.animate();
```

### 2. 3D Pie Chart for Expense Breakdown

```javascript
class ExpensePieChart3D {
  constructor(containerId) {
    // Setup scene, camera, renderer (same as above)
    this.scene = new THREE.Scene();
    // ... similar setup
  }

  async loadExpenseData(startDate, endDate) {
    const response = await fetch(
      `/api/finance/reports/dashboard/?start_date=${startDate}&end_date=${endDate}`
    );
    const data = await response.json();
    this.renderPieChart(data.expense_by_category);
  }

  renderPieChart(expenseByCategory) {
    const total = Object.values(expenseByCategory).reduce((a, b) => a + parseFloat(b), 0);
    const colors = [
      0xe91e63, 0x9c27b0, 0x673ab7, 0x3f51b5,
      0x2196f3, 0x00bcd4, 0x009688, 0x4caf50
    ];

    let currentAngle = 0;
    Object.entries(expenseByCategory).forEach(([category, amount], index) => {
      const percentage = parseFloat(amount) / total;
      const angle = percentage * Math.PI * 2;

      // Create wedge geometry
      const shape = new THREE.Shape();
      shape.moveTo(0, 0);
      shape.absarc(0, 0, 5, currentAngle, currentAngle + angle, false);
      shape.lineTo(0, 0);

      const extrudeSettings = {
        depth: 2,
        bevelEnabled: true,
        bevelThickness: 0.1,
        bevelSize: 0.1,
        bevelSegments: 3
      };

      const geometry = new THREE.ExtrudeGeometry(shape, extrudeSettings);
      const material = new THREE.MeshPhongMaterial({ color: colors[index % colors.length] });
      const wedge = new THREE.Mesh(geometry, material);

      // Rotate to face camera
      wedge.rotation.x = -Math.PI / 2;
      wedge.position.y = 0;

      this.scene.add(wedge);

      // Add label at midpoint of wedge
      const midAngle = currentAngle + angle / 2;
      const labelX = Math.cos(midAngle) * 6;
      const labelZ = Math.sin(midAngle) * 6;
      this.addLabel(
        `${category}\n${(percentage * 100).toFixed(1)}%`,
        labelX, 1, labelZ
      );

      currentAngle += angle;
    });
  }

  // ... addLabel and animate methods
}
```

### 3. Time-Series 3D Surface Plot

```javascript
class FinancialSurfacePlot {
  constructor(containerId) {
    // Setup scene
    this.scene = new THREE.Scene();
    // ... similar setup
  }

  async loadTimeSeriesData(months = 12) {
    // Fetch monthly P&L data for the past N months
    const promises = [];
    const endDate = new Date();
    
    for (let i = 0; i < months; i++) {
      const date = new Date(endDate);
      date.setMonth(date.getMonth() - i);
      const startOfMonth = new Date(date.getFullYear(), date.getMonth(), 1);
      const endOfMonth = new Date(date.getFullYear(), date.getMonth() + 1, 0);
      
      promises.push(
        fetch(`/api/finance/reports/profit_loss/?start_date=${formatDate(startOfMonth)}&end_date=${formatDate(endOfMonth)}`)
          .then(r => r.json())
      );
    }
    
    const data = await Promise.all(promises);
    this.renderSurface(data.reverse());
  }

  renderSurface(monthlyData) {
    const width = monthlyData.length;
    const depth = 4; // Revenue, COGS, OpEx, Profit
    const geometry = new THREE.PlaneGeometry(width * 2, depth * 2, width - 1, depth - 1);
    
    const vertices = geometry.attributes.position.array;
    
    monthlyData.forEach((month, x) => {
      const values = [
        parseFloat(month.total_revenue),
        parseFloat(month.cogs),
        parseFloat(month.operating_expenses),
        parseFloat(month.net_profit)
      ];
      
      values.forEach((value, z) => {
        const index = (x + z * width) * 3;
        vertices[index + 2] = value / 1000; // Z height based on value
      });
    });
    
    geometry.computeVertexNormals();
    
    const material = new THREE.MeshPhongMaterial({
      color: 0x2196f3,
      side: THREE.DoubleSide,
      wireframe: false
    });
    
    const surface = new THREE.Mesh(geometry, material);
    surface.rotation.x = -Math.PI / 4;
    this.scene.add(surface);
    
    // Add wireframe overlay
    const wireframeGeo = new THREE.WireframeGeometry(geometry);
    const wireframeMat = new THREE.LineBasicMaterial({ color: 0xffffff, linewidth: 2 });
    const wireframe = new THREE.LineSegments(wireframeGeo, wireframeMat);
    wireframe.rotation.x = -Math.PI / 4;
    this.scene.add(wireframe);
  }
}
```

## React Integration Example

```jsx
import React, { useEffect, useRef } from 'react';
import { FinancialBarChart } from './three-charts';

function FinancialDashboard() {
  const chartRef = useRef(null);
  const [dateRange, setDateRange] = useState({
    start: '2026-01-01',
    end: '2026-01-31'
  });

  useEffect(() => {
    if (chartRef.current) {
      const chart = new FinancialBarChart('chart-container');
      chart.loadPLData(dateRange.start, dateRange.end);
      chart.animate();

      return () => {
        // Cleanup
        chart.dispose();
      };
    }
  }, [dateRange]);

  return (
    <div>
      <div className="controls">
        <input
          type="date"
          value={dateRange.start}
          onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
        />
        <input
          type="date"
          value={dateRange.end}
          onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value }))}
        />
      </div>
      <div id="chart-container" style={{ width: '100%', height: '600px' }} />
    </div>
  );
}
```

## Advanced Features

### 1. Interactive Tooltips
Add raycasting to detect mouse hover over 3D objects and show detailed information:

```javascript
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

renderer.domElement.addEventListener('mousemove', (event) => {
  mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
  mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;
  
  raycaster.setFromCamera(mouse, camera);
  const intersects = raycaster.intersectObjects(scene.children);
  
  if (intersects.length > 0) {
    const object = intersects[0].object;
    showTooltip(object.userData); // Show data associated with 3D object
  }
});
```

### 2. Animated Transitions
Use Tween.js for smooth transitions when data updates:

```javascript
import TWEEN from '@tweenjs/tween.js';

function updateBarHeight(bar, newHeight) {
  new TWEEN.Tween(bar.scale)
    .to({ y: newHeight }, 1000)
    .easing(TWEEN.Easing.Quadratic.Out)
    .start();
}

function animate() {
  requestAnimationFrame(animate);
  TWEEN.update();
  renderer.render(scene, camera);
}
```

### 3. VR/AR Support
Use WebXR for immersive financial data exploration:

```javascript
renderer.xr.enabled = true;
document.body.appendChild(VRButton.createButton(renderer));

function animate() {
  renderer.setAnimationLoop(() => {
    controls.update();
    renderer.render(scene, camera);
  });
}
```

## Libraries to Consider

1. **Three.js** - Core 3D rendering
2. **Chart.js + Three.js** - Hybrid 2D/3D charts
3. **D3.js + Three.js** - Data transformation + 3D rendering
4. **React-Three-Fiber** - React integration for Three.js
5. **Tween.js** - Smooth animations
6. **dat.GUI** - Debug controls for parameters

## Performance Optimization

- Use instanced meshes for repeated geometries
- Implement level-of-detail (LOD) for complex scenes
- Use web workers for data processing
- Lazy load charts (render on scroll)
- Implement frustum culling for off-screen objects

## Deployment Considerations

- Ensure backend CORS is configured for frontend domain
- Use CDN for Three.js library
- Implement loading states while fetching data
- Add fallback to 2D charts for unsupported browsers
- Optimize texture sizes and polygon counts
