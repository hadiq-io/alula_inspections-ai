'use client';

import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { api } from '../lib/api';

export default function MLModelsChart() {
  const [data, setData] = useState([]);

  useEffect(() => {
    api.getModels().then((models) => {
      const chartData = models.map((m: any) => ({
        name: m.Model,
        records: m.RecordCount || 0,
      }));
      setData(chartData);
    });
  }, []);

  return (
    <div className="bg-[#1a2332] rounded-3xl p-6 border border-gray-800">
      <h3 className="text-white text-lg font-semibold mb-4">10 ML Models Performance</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2a3544" />
          <XAxis 
            dataKey="name" 
            stroke="#6b7280" 
            tick={{ fill: '#9ca3af', fontSize: 11 }} 
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis stroke="#6b7280" tick={{ fill: '#9ca3af' }} />
          <Tooltip
            contentStyle={{
              backgroundColor: '#0f1419',
              border: '1px solid #374151',
              borderRadius: '12px',
              color: '#fff',
            }}
          />
          <Bar dataKey="records" fill="url(#barGradient)" radius={[8, 8, 0, 0]} />
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
