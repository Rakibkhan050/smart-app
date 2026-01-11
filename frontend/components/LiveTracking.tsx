import React, { useState, useEffect, useRef } from 'react';
import api from '../services/api';

interface Location {
  latitude: number;
  longitude: number;
  timestamp: string;
}

interface DriverLocation extends Location {
  name: string;
  phone: string;
  vehicle_type: string;
  vehicle_number: string;
  status: string;
}

interface TrackingData {
  tracking_number: string;
  order_reference: string;
  status: string;
  status_display: string;
  expected_delivery?: string;
  destination?: {
    latitude: number | null;
    longitude: number | null;
    address: string;
    city: string;
  };
  driver?: DriverLocation;
}

interface LiveTrackingProps {
  trackingNumber: string;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

const LiveTracking: React.FC<LiveTrackingProps> = ({ 
  trackingNumber, 
  autoRefresh = true,
  refreshInterval = 10000 // 10 seconds
}) => {
  const [trackingData, setTrackingData] = useState<TrackingData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchTrackingData = async () => {
    try {
      const response = await api.get(`/drivers/track/${trackingNumber}/`);
      setTrackingData(response.data);
      setLastUpdated(new Date());
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to fetch tracking data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTrackingData();

    if (autoRefresh) {
      intervalRef.current = setInterval(fetchTrackingData, refreshInterval);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [trackingNumber, autoRefresh, refreshInterval]);

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'bg-yellow-500',
      assigned: 'bg-blue-500',
      picked_up: 'bg-indigo-500',
      in_transit: 'bg-purple-500',
      delivered: 'bg-green-500',
      failed: 'bg-red-500',
    };
    return colors[status] || 'bg-gray-500';
  };

  const openInMaps = (lat: number, lon: number) => {
    const url = `https://www.google.com/maps/search/?api=1&query=${lat},${lon}`;
    window.open(url, '_blank');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">{error}</p>
      </div>
    );
  }

  if (!trackingData) {
    return null;
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Track Delivery</h2>
            <p className="text-gray-600">Tracking: {trackingData.tracking_number}</p>
            <p className="text-sm text-gray-500">Order: {trackingData.order_reference}</p>
          </div>
          <span className={`${getStatusColor(trackingData.status)} text-white px-4 py-2 rounded-full text-sm font-medium`}>
            {trackingData.status_display}
          </span>
        </div>

        {lastUpdated && (
          <p className="text-xs text-gray-500">
            Last updated: {lastUpdated.toLocaleTimeString()}
            {autoRefresh && <span className="ml-2">• Auto-refreshing</span>}
          </p>
        )}
      </div>

      {/* Driver Info */}
      {trackingData.driver && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <span className="w-3 h-3 bg-green-500 rounded-full mr-2 animate-pulse"></span>
            Driver Information
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Name</p>
              <p className="font-medium">{trackingData.driver.name}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Phone</p>
              <p className="font-medium">
                <a href={`tel:${trackingData.driver.phone}`} className="text-blue-600 hover:underline">
                  {trackingData.driver.phone}
                </a>
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Vehicle</p>
              <p className="font-medium">
                {trackingData.driver.vehicle_type} - {trackingData.driver.vehicle_number}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Status</p>
              <p className="font-medium capitalize">{trackingData.driver.status}</p>
            </div>
          </div>

          {trackingData.driver.current_location && (
            <div className="mt-4 p-4 bg-blue-50 rounded-lg">
              <p className="text-sm font-medium text-blue-900 mb-2">Current Location</p>
              <p className="text-sm text-blue-800">
                {trackingData.driver.current_location.latitude.toFixed(6)}, 
                {trackingData.driver.current_location.longitude.toFixed(6)}
              </p>
              <p className="text-xs text-blue-600 mt-1">
                Updated: {new Date(trackingData.driver.current_location.last_updated).toLocaleString()}
              </p>
              <button
                onClick={() => openInMaps(
                  trackingData.driver!.current_location.latitude,
                  trackingData.driver!.current_location.longitude
                )}
                className="mt-3 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition text-sm"
              >
                📍 View on Map
              </button>
            </div>
          )}
        </div>
      )}

      {/* Destination */}
      {trackingData.destination && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4">Delivery Destination</h3>
          <div>
            <p className="font-medium">{trackingData.destination.address}</p>
            <p className="text-gray-600">{trackingData.destination.city}</p>
            {trackingData.destination.latitude && trackingData.destination.longitude && (
              <button
                onClick={() => openInMaps(
                  trackingData.destination!.latitude!,
                  trackingData.destination!.longitude!
                )}
                className="mt-3 bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition text-sm"
              >
                📍 View Destination on Map
              </button>
            )}
          </div>
        </div>
      )}

      {/* Expected Delivery */}
      {trackingData.expected_delivery && (
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-2">Expected Delivery</h3>
          <p className="text-gray-700">
            {new Date(trackingData.expected_delivery).toLocaleString()}
          </p>
        </div>
      )}

      {/* Refresh Button */}
      <button
        onClick={fetchTrackingData}
        className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition font-medium"
      >
        🔄 Refresh Location
      </button>
    </div>
  );
};

export default LiveTracking;
