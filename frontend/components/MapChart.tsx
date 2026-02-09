'use client';

import React, { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import dynamic from 'next/dynamic';

const MapContainer = dynamic(
  () => import('react-leaflet').then((mod) => mod.MapContainer),
  { ssr: false }
);
const TileLayer = dynamic(
  () => import('react-leaflet').then((mod) => mod.TileLayer),
  { ssr: false }
);
const CircleMarker = dynamic(
  () => import('react-leaflet').then((mod) => mod.CircleMarker),
  { ssr: false }
);
const Popup = dynamic(
  () => import('react-leaflet').then((mod) => mod.Popup),
  { ssr: false }
);
const Tooltip = dynamic(
  () => import('react-leaflet').then((mod) => mod.Tooltip),
  { ssr: false }
);

interface MapDataPoint {
  name?: string;
  name_ar?: string;
  latitude?: number;
  longitude?: number;
  lat?: number;
  lng?: number;
  value?: number;
  violations?: number;
  inspections?: number;
  score?: number;
  risk_level?: string;
  location_type?: string;
  location_name?: string;
  location_name_ar?: string;
  activity_type?: string;
  [key: string]: any;
}

interface MapChartProps {
  data: MapDataPoint[];
  title?: string;
  isRTL?: boolean;
  mapStyle?: 'streets' | 'satellite' | 'dark' | 'light';
  showHeatmap?: boolean;
  colorBy?: 'violations' | 'score' | 'risk_level' | 'inspections';
}

const ALULA_CENTER: [number, number] = [26.6174, 37.9236];
const DEFAULT_ZOOM = 11;

export default function MapChart({
  data,
  title,
  isRTL = false,
  mapStyle = 'dark',
  colorBy = 'violations'
}: MapChartProps) {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
    // CSS is imported globally in globals.css
  }, []);

  const getTileLayer = (style: string) => {
    const tiles: Record<string, { url: string; attribution: string }> = {
      streets: {
        url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attribution: '© OpenStreetMap'
      },
      satellite: {
        url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attribution: '© Esri'
      },
      dark: {
        url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
        attribution: '© OpenStreetMap © CARTO'
      },
      light: {
        url: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
        attribution: '© OpenStreetMap © CARTO'
      }
    };
    return tiles[style] || tiles.dark;
  };

  const getColor = (point: MapDataPoint): string => {
    if (colorBy === 'risk_level') {
      const risk = point.risk_level?.toLowerCase() || '';
      if (risk.includes('high')) return '#ef4444';
      if (risk.includes('medium')) return '#f59e0b';
      return '#22c55e';
    }
    if (colorBy === 'score') {
      const score = point.score || 0;
      if (score >= 90) return '#22c55e';
      if (score >= 70) return '#f59e0b';
      return '#ef4444';
    }
    if (colorBy === 'violations') {
      const violations = point.violations || point.value || 0;
      if (violations >= 10) return '#ef4444';
      if (violations >= 5) return '#f59e0b';
      return '#22c55e';
    }
    if (colorBy === 'inspections') {
      const inspections = point.inspections || 0;
      if (inspections >= 20) return '#3b82f6';
      if (inspections >= 10) return '#8b5cf6';
      return '#06b6d4';
    }
    return '#3b82f6';
  };

  const getRadius = (point: MapDataPoint): number => {
    const value = point.violations || point.inspections || point.value || 1;
    return Math.min(Math.max(value * 1.5 + 6, 8), 30);
  };

  const mapCenter = useMemo(() => {
    if (!data.length) return ALULA_CENTER;
    
    const validPoints = data.filter(p => {
      const lat = p.latitude || p.lat;
      const lng = p.longitude || p.lng;
      return lat && lng && !isNaN(lat) && !isNaN(lng);
    });

    if (!validPoints.length) return ALULA_CENTER;

    const sumLat = validPoints.reduce((sum, p) => sum + (p.latitude || p.lat || 0), 0);
    const sumLng = validPoints.reduce((sum, p) => sum + (p.longitude || p.lng || 0), 0);
    
    return [sumLat / validPoints.length, sumLng / validPoints.length] as [number, number];
  }, [data]);

  const processedData = useMemo(() => {
    return data.map((point, index) => {
      const lat = point.latitude || point.lat;
      const lng = point.longitude || point.lng;
      
      return {
        ...point,
        coords: lat && lng && !isNaN(lat) && !isNaN(lng) 
          ? [lat, lng] as [number, number]
          : null,
        color: getColor(point),
        radius: getRadius(point),
        id: index
      };
    }).filter(p => p.coords !== null);
  }, [data, colorBy]);

  const tileConfig = getTileLayer(mapStyle);

  const stats = useMemo(() => {
    const totalViolations = data.reduce((sum, p) => sum + (p.violations || 0), 0);
    const totalInspections = data.reduce((sum, p) => sum + (p.inspections || 0), 0);
    const avgScore = data.length 
      ? Math.round(data.reduce((sum, p) => sum + (p.score || 0), 0) / data.length)
      : 0;
    return { totalViolations, totalInspections, avgScore, locations: processedData.length };
  }, [data, processedData]);

  if (!isClient) {
    return (
      <div className="w-full h-[500px] bg-gray-900/50 rounded-xl flex items-center justify-center">
        <div className="flex items-center gap-3">
          <div className="w-6 h-6 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
          <span className="text-gray-400">Loading map...</span>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full h-[350px] sm:h-[450px] md:h-[500px] bg-gray-900/50 rounded-xl overflow-hidden border border-gray-700/50 relative"
    >
      {title && (
        <div className="absolute top-0 left-0 right-0 z-[1000] bg-gradient-to-b from-gray-900/90 to-transparent p-2 sm:p-4">
          <h3 className={`text-sm sm:text-lg font-semibold text-white ${isRTL ? 'text-right' : ''}`}>
            {title}
          </h3>
        </div>
      )}

      <div className="absolute top-2 sm:top-4 right-2 sm:right-4 z-[1000] bg-gray-900/90 backdrop-blur-sm rounded-lg p-2 sm:p-3 border border-gray-700/50">
        <div className="grid grid-cols-2 gap-2 sm:gap-3 text-[10px] sm:text-xs">
          <div className="text-center">
            <div className="text-cyan-400 font-bold text-sm sm:text-lg">{stats.locations}</div>
            <div className="text-gray-400">{isRTL ? 'المواقع' : 'Locations'}</div>
          </div>
          <div className="text-center">
            <div className="text-red-400 font-bold text-sm sm:text-lg">{stats.totalViolations}</div>
            <div className="text-gray-400">{isRTL ? 'المخالفات' : 'Violations'}</div>
          </div>
          <div className="text-center">
            <div className="text-blue-400 font-bold text-sm sm:text-lg">{stats.totalInspections}</div>
            <div className="text-gray-400">{isRTL ? 'الفحوصات' : 'Inspections'}</div>
          </div>
          <div className="text-center">
            <div className="text-green-400 font-bold text-sm sm:text-lg">{stats.avgScore}%</div>
            <div className="text-gray-400">{isRTL ? 'المتوسط' : 'Avg Score'}</div>
          </div>
        </div>
      </div>

      <div className="absolute bottom-2 sm:bottom-4 left-2 sm:left-4 z-[1000] bg-gray-900/90 backdrop-blur-sm rounded-lg p-2 sm:p-3 border border-gray-700/50">
        <div className="text-[10px] sm:text-xs text-gray-400 mb-1 sm:mb-2">
          {colorBy === 'violations' && (isRTL ? 'حسب المخالفات' : 'By Violations')}
          {colorBy === 'score' && (isRTL ? 'حسب الدرجة' : 'By Score')}
          {colorBy === 'risk_level' && (isRTL ? 'حسب المخاطر' : 'By Risk Level')}
          {colorBy === 'inspections' && (isRTL ? 'حسب الفحوصات' : 'By Inspections')}
        </div>
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <span className="text-xs text-gray-300">High</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-yellow-500" />
            <span className="text-xs text-gray-300">Medium</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-green-500" />
            <span className="text-xs text-gray-300">Low</span>
          </div>
        </div>
      </div>

      <MapContainer
        center={mapCenter}
        zoom={DEFAULT_ZOOM}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
        zoomControl={true}
      >
        <TileLayer
          attribution={tileConfig.attribution}
          url={tileConfig.url}
        />
        
        {processedData.map((point) => (
          <CircleMarker
            key={point.id}
            center={point.coords!}
            radius={point.radius}
            pathOptions={{
              color: '#ffffff',
              weight: 2,
              fillColor: point.color,
              fillOpacity: 0.8
            }}
          >
            <Tooltip direction="top" offset={[0, -10]} opacity={0.95}>
              <div style={{ padding: '8px', minWidth: '150px' }}>
                <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
                  {isRTL ? (point.name_ar || point.name) : (point.name || point.location_name)}
                </div>
                {point.violations !== undefined && (
                  <div>Violations: {point.violations}</div>
                )}
                {point.inspections !== undefined && (
                  <div>Inspections: {point.inspections}</div>
                )}
                {point.score !== undefined && (
                  <div>Score: {point.score}%</div>
                )}
                {point.risk_level && (
                  <div>Risk: {point.risk_level}</div>
                )}
              </div>
            </Tooltip>
            
            <Popup>
              <div style={{ padding: '8px', minWidth: '180px' }}>
                <div style={{ fontWeight: 'bold', fontSize: '14px', marginBottom: '8px', borderBottom: '1px solid #ddd', paddingBottom: '4px' }}>
                  {isRTL ? (point.name_ar || point.name) : (point.name || point.location_name)}
                </div>
                {point.violations !== undefined && (
                  <div style={{ marginBottom: '4px' }}>🚨 Violations: <strong>{point.violations}</strong></div>
                )}
                {point.inspections !== undefined && (
                  <div style={{ marginBottom: '4px' }}>📋 Inspections: <strong>{point.inspections}</strong></div>
                )}
                {point.score !== undefined && (
                  <div style={{ marginBottom: '4px' }}>📊 Score: <strong>{point.score}%</strong></div>
                )}
                {point.risk_level && (
                  <div style={{ marginBottom: '4px' }}>⚠️ Risk: <strong>{point.risk_level}</strong></div>
                )}
                {point.activity_type && (
                  <div style={{ marginBottom: '4px' }}>🏢 Type: <strong>{point.activity_type}</strong></div>
                )}
                <div style={{ fontSize: '11px', color: '#666', marginTop: '8px' }}>
                  📍 {point.coords?.[0]?.toFixed(4)}, {point.coords?.[1]?.toFixed(4)}
                </div>
              </div>
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>

      {processedData.length === 0 && (
        <div className="absolute inset-0 z-[1001] bg-gray-900/80 flex items-center justify-center">
          <div className="text-center">
            <div className="text-4xl mb-3">🗺️</div>
            <div className="text-gray-300 text-lg">
              {isRTL ? 'لا توجد بيانات جغرافية' : 'No geographic data available'}
            </div>
            <div className="text-gray-500 text-sm mt-1">
              {isRTL ? 'البيانات المحددة لا تحتوي على إحداثيات' : 'The selected data has no coordinates'}
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
}
