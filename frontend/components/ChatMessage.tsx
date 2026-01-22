import React, { useState, useEffect } from 'react';
import { BarChart3, Brain, ChevronRight } from 'lucide-react';

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  tiles?: any[];
  type?: string;
  onTileClick?: (tileId: string, tileType: string) => void;
}

export default function ChatMessage({ role, content, tiles, type, onTileClick }: ChatMessageProps) {
  const [displayedContent, setDisplayedContent] = useState('');
  const isUser = role === 'user';

  useEffect(() => {
    if (type === 'kpi_tiles' || type === 'prediction_tiles') {
      setDisplayedContent('');
      return;
    }
    if (!content) {
      setDisplayedContent('');
      return;
    }
    let currentIndex = 0;
    setDisplayedContent('');
    const streamInterval = setInterval(() => {
      if (currentIndex < content.length) {
        setDisplayedContent(content.slice(0, currentIndex + 1));
        currentIndex++;
      } else {
        clearInterval(streamInterval);
      }
    }, 20);
    return () => clearInterval(streamInterval);
  }, [content, type]);

  if (tiles && (type === 'kpi_tiles' || type === 'prediction_tiles')) {
    const isKPI = type === 'kpi_tiles';
    const Icon = isKPI ? BarChart3 : Brain;
    const title = isKPI ? 'Historical KPI Analysis' : 'ML Predictions & Forecasts';

    return (
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-4">
          <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${isKPI ? 'from-[#104C64] to-[#0d3d50]' : 'from-[#C0754D] to-[#B6410F]'} flex items-center justify-center shadow-xl`}>
            <Icon className="w-5 h-5 text-white" strokeWidth={2.5} />
          </div>
          <div className="font-semibold text-lg text-white">{title}</div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {tiles.map((tile: any, index: number) => (
            <div
              key={tile.id}
              onClick={() => onTileClick?.(tile.id, type)}
              className="group relative p-5 rounded-2xl bg-gradient-to-br from-white/20 to-white/5 backdrop-blur-xl border border-white/30 hover:border-[#C0754D] hover:shadow-2xl hover:shadow-[#C0754D]/30 transition-all duration-500 cursor-pointer transform hover:-translate-y-2 hover:scale-105"
              style={{
                boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.2)',
              }}
            >
              <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              
              <div className="relative z-10">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#104C64] to-[#0d3d50] flex items-center justify-center text-white font-bold shadow-lg">
                      {index + 1}
                    </div>
                    <h3 className="font-bold text-white group-hover:text-[#D59D80] transition-colors text-base">
                      {tile.name}
                    </h3>
                  </div>
                  <ChevronRight className="w-5 h-5 text-white/50 group-hover:text-[#C0754D] group-hover:translate-x-2 transition-all duration-300" />
                </div>
                
                <p className="text-sm text-white/80 mb-3 leading-relaxed">{tile.description}</p>
                
                <div className="flex items-center justify-between text-xs">
                  <span className="font-mono bg-white/10 text-white/90 px-3 py-1.5 rounded-lg backdrop-blur-sm border border-white/20">
                    {tile.table}
                  </span>
                  {tile.model && (
                    <span className="bg-gradient-to-r from-blue-500/30 to-purple-500/30 text-blue-200 px-3 py-1.5 rounded-lg backdrop-blur-sm border border-blue-400/30 font-semibold">
                      {tile.model}
                    </span>
                  )}
                </div>
              </div>

              {/* 3D Shadow Effect */}
              <div className="absolute -bottom-2 left-4 right-4 h-2 bg-black/20 blur-xl rounded-full transform group-hover:scale-110 transition-transform duration-500"></div>
            </div>
          ))}
        </div>
        
        <div className="mt-4 flex items-center gap-2 text-sm text-white/70 italic">
          <ChevronRight className="w-4 h-4" />
          <span>Click any tile to view detailed analysis and insights</span>
        </div>
      </div>
    );
  }

  return (
    <div className={`mb-6 ${isUser ? 'flex justify-end' : ''}`}>
      <div className={`flex items-start gap-4 ${isUser ? 'flex-row-reverse max-w-2xl' : 'max-w-full'}`}>
        <div className={`flex-shrink-0 w-8 h-8 rounded-lg ${isUser ? 'bg-gradient-to-br from-[#C0754D] to-[#B6410F]' : 'bg-gradient-to-br from-[#104C64] to-[#0d3d50]'} flex items-center justify-center shadow-lg`}>
          <span className="text-white font-bold text-sm">{isUser ? 'U' : 'AI'}</span>
        </div>
        <div className="flex-1">
          <div className={`text-sm font-semibold text-white/90 mb-1 ${isUser ? 'text-right' : ''}`}>
            {isUser ? 'You' : 'AlUla Assistant'}
          </div>
          <div className={`text-white whitespace-pre-wrap leading-relaxed ${isUser ? 'text-right' : ''}`}>
            {displayedContent}
          </div>
        </div>
      </div>
    </div>
  );
}
