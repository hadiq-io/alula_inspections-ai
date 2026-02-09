'use client';

import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

// Static demo data for ML models (component not currently used in main app)
const mockModels = [
  { name: 'Risk Predictor', records: 1250 },
  { name: 'Volume Forecast', records: 980 },
  { name: 'Compliance ML', records: 1540 },
  { name: 'Anomaly Detector', records: 720 },
  { name: 'Trend Analyzer', records: 1120 },
  { name: 'Resource Optimizer', records: 890 },
  { name: 'Priority Classifier', records: 1340 },
  { name: 'Condition Scorer', records: 1050 },
  { name: 'Seasonal Model', records: 760 },
  { name: 'Heritage Predictor', records: 1180 },
];

export default function MLModelsChart() {
  const [data, setData] = useState<{ name: string; records: number }[]>([]);

  useEffect(() => {
    // Using static demo data
    setData(mockModels);
  }, []);

  return (
    <div className="bg-[#1a2332] rounded-xl sm:rounded-3xl p-4 sm:p-6 border border-gray-800">
      <h3 className="text-white text-base sm:text-lg font-semibold mb-3 sm:mb-4">10 ML Models Performance</h3>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a3544" />
          <XAxis 
            dataKey="name" 
            stroke="#6b7280" 
            tick={{ fill: '#9ca3af', fontSize: 9 }} 
            angle={-45}
            textAnchor="end"
            height={70}
          />
          <YAxis stroke="#6b7280" tick={{ fill: '#9ca3af', fontSize: 10 }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#0f1419',
              border: '1px solid #374151',
              borderRadius: '12px',
              color: '#fff',
              fontSize: 12,
            }}
          />
          <Bar dataKey="records" fill="url(#barGradient)" radius={[6, 6, 0, 0]} />
          <defs>
            <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#06b6d4" />
              <stop offset="100%" stopColor="#f97316" />
            </linearGradient>
          </defs>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
