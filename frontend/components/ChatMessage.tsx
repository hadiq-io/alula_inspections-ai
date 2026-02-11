import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { BarChart3, Brain, ChevronRight, User, Bot, Sparkles, CheckCircle, AlertTriangle, Info, TrendingUp, MapPin, Users, Calendar, PieChart, Target, Search } from 'lucide-react';
import InlineChart from './InlineChart';
import FeedbackButtons from './FeedbackButtons';

interface ChartConfig {
  type: "bar" | "line" | "pie" | "composed" | "area" | "none";
  xKey?: string;
  yKeys?: string[];
  title?: string;
  title_ar?: string;
}

interface Recommendation {
  text: string;
  text_en: string;
  text_ar: string;
  icon: string;
}

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  content_en?: string;  // English version of content
  content_ar?: string;  // Arabic version of content
  tiles?: any[];
  type?: string;
  onTileClick?: (tileId: string, tileType: string) => void;
  onContentUpdate?: () => void;
  isCompact?: boolean;
  // New props for bilingual and chart support
  chartData?: Record<string, any>[];
  chartConfig?: ChartConfig;
  isRTL?: boolean;
  // Recommendations
  recommendations?: Recommendation[];
  onRecommendationClick?: (text: string) => void;
  // Feedback system props
  messageId?: string;
  feedbackEnabled?: boolean;
  onClarificationRetry?: (retryResponse: any) => void;
}

// Icon mapping for recommendations
const getRecommendationIcon = (iconName: string) => {
  const iconProps = { className: "w-4 h-4 text-white", strokeWidth: 2 };
  switch (iconName) {
    case 'alert': return <AlertTriangle {...iconProps} />;
    case 'map': return <MapPin {...iconProps} />;
    case 'trend': return <TrendingUp {...iconProps} />;
    case 'calendar': return <Calendar {...iconProps} />;
    case 'users': return <Users {...iconProps} />;
    case 'pie': return <PieChart {...iconProps} />;
    case 'check': return <CheckCircle {...iconProps} />;
    case 'bar': return <BarChart3 {...iconProps} />;
    case 'target': return <Target {...iconProps} />;
    case 'ranking': return <TrendingUp {...iconProps} />;
    default: return <Search {...iconProps} />;
  }
};

// Gradient colors for recommendation tiles
const RECOMMENDATION_GRADIENTS = [
  "from-amber-500 to-orange-600",
  "from-emerald-500 to-teal-600",
  "from-blue-500 to-indigo-600",
  "from-purple-500 to-violet-600",
];

// Check if a line is a table row (starts and ends with | or contains multiple |)
function isTableRow(line: string): boolean {
  const trimmed = line.trim();
  return trimmed.startsWith('|') && trimmed.endsWith('|') && trimmed.split('|').length >= 3;
}

// Check if a line is a table separator (contains only |, -, :, and spaces)
function isTableSeparator(line: string): boolean {
  const trimmed = line.trim();
  return trimmed.startsWith('|') && /^[\|\-:\s]+$/.test(trimmed);
}

// Parse table cells from a row
function parseTableCells(row: string): string[] {
  return row.split('|')
    .map(cell => cell.trim())
    .filter((cell, idx, arr) => idx > 0 && idx < arr.length - 1); // Remove empty first/last from split
}

// Render a markdown table
function renderTable(tableLines: string[], startKey: number): React.ReactNode {
  const rows = tableLines.filter(line => !isTableSeparator(line));
  if (rows.length === 0) return null;
  
  const headerCells = parseTableCells(rows[0]);
  const bodyRows = rows.slice(1);
  
  return (
    <div key={`table-${startKey}`} className="my-4 overflow-x-auto">
      <table className="w-full border-collapse rounded-lg overflow-hidden">
        <thead>
          <tr className="bg-gradient-to-r from-amber-500/20 to-orange-600/20 border-b border-white/20">
            {headerCells.map((cell, idx) => (
              <th key={idx} className="px-4 py-3 text-left text-sm font-semibold text-white border-r border-white/10 last:border-r-0">
                {cleanText(cell)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {bodyRows.map((row, rowIdx) => {
            const cells = parseTableCells(row);
            return (
              <tr key={rowIdx} className={`border-b border-white/10 last:border-b-0 ${rowIdx % 2 === 0 ? 'bg-white/5' : 'bg-white/[0.02]'} hover:bg-white/10 transition-colors`}>
                {cells.map((cell, cellIdx) => (
                  <td key={cellIdx} className="px-4 py-2.5 text-sm text-white/90 border-r border-white/10 last:border-r-0">
                    {cleanText(cell)}
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

// Clean and format the entire content
function formatContent(text: string): React.ReactNode[] {
  if (!text) return [];
  
  const elements: React.ReactNode[] = [];
  const lines = text.split('\n');
  
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    const trimmedLine = line.trim();
    
    // Check if this starts a table
    if (isTableRow(trimmedLine)) {
      const tableLines: string[] = [];
      while (i < lines.length && (isTableRow(lines[i].trim()) || isTableSeparator(lines[i].trim()))) {
        tableLines.push(lines[i].trim());
        i++;
      }
      if (tableLines.length > 0) {
        elements.push(renderTable(tableLines, i));
      }
      continue;
    }
    
    // Skip empty lines but add spacing
    if (!trimmedLine) {
      if (i > 0 && i < lines.length - 1) {
        elements.push(<div key={i} className="h-2" />);
      }
      i++;
      continue;
    }
    
    // Handle ### headers (h3)
    if (trimmedLine.startsWith('### ')) {
      const headerText = trimmedLine.replace(/^###\s*/, '').replace(/[*#]/g, '');
      elements.push(
        <div key={i} className="flex items-center gap-2 mt-4 mb-2">
          <Info className="w-4 h-4 text-blue-400 flex-shrink-0" />
          <span className="font-semibold text-white text-base">{cleanText(headerText)}</span>
        </div>
      );
      i++;
      continue;
    }
    
    // Handle ## headers (h2)
    if (trimmedLine.startsWith('## ')) {
      const headerText = trimmedLine.replace(/^##\s*/, '').replace(/[*#]/g, '');
      elements.push(
        <div key={i} className="flex items-center gap-2 mt-4 mb-3">
          <Sparkles className="w-5 h-5 text-amber-400 flex-shrink-0" />
          <span className="font-bold text-white text-lg">{cleanText(headerText)}</span>
        </div>
      );
      i++;
      continue;
    }
    
    // Handle # headers (h1)
    if (trimmedLine.startsWith('# ')) {
      const headerText = trimmedLine.replace(/^#\s*/, '').replace(/[*#]/g, '');
      elements.push(
        <div key={i} className="flex items-center gap-2 mt-4 mb-3">
          <Sparkles className="w-5 h-5 text-amber-400 flex-shrink-0" />
          <span className="font-bold text-white text-xl">{cleanText(headerText)}</span>
        </div>
      );
      i++;
      continue;
    }
    
    // Handle numbered lists (1. 2. 3. etc) - with or without bold
    const numberedMatch = trimmedLine.match(/^(\d+)[.)]\s*(.+)$/);
    if (numberedMatch) {
      elements.push(
        <div key={i} className="flex gap-3 my-2 ml-1">
          <span className="flex-shrink-0 w-6 h-6 rounded-full bg-gradient-to-br from-amber-500/30 to-orange-600/30 flex items-center justify-center text-amber-300 text-xs font-bold border border-amber-500/30">
            {numberedMatch[1]}
          </span>
          <span className="flex-1 text-white/90">{cleanText(numberedMatch[2])}</span>
        </div>
      );
      i++;
      continue;
    }
    
    // Handle bullet points (- or * or •) - but not table separators
    const bulletMatch = trimmedLine.match(/^[-*•]\s+(.+)$/);
    if (bulletMatch && !isTableSeparator(trimmedLine)) {
      elements.push(
        <div key={i} className="flex gap-3 my-1.5 ml-3">
          <span className="flex-shrink-0 w-1.5 h-1.5 rounded-full bg-amber-400 mt-2"></span>
          <span className="flex-1 text-white/90">{cleanText(bulletMatch[1])}</span>
        </div>
      );
      i++;
      continue;
    }
    
    // Handle lines that are just bold (like **High Objection Rate (>20%)**)
    if (trimmedLine.startsWith('**') && trimmedLine.includes('**')) {
      const cleanedLine = cleanText(trimmedLine);
      // Check if original line ends with : (since cleanText returns ReactNode, not string)
      if (trimmedLine.endsWith(':') || trimmedLine.endsWith(':**')) {
        // It's a sub-header
        elements.push(
          <div key={i} className="flex items-center gap-2 mt-3 mb-1">
            <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span className="font-semibold text-white">{cleanedLine}</span>
          </div>
        );
      } else {
        elements.push(
          <p key={i} className="my-1.5 font-semibold text-white">
            {cleanedLine}
          </p>
        );
      }
      i++;
      continue;
    }
    
    // Handle lines ending with : (section headers)
    if (trimmedLine.endsWith(':') && trimmedLine.length < 80 && !trimmedLine.includes('http')) {
      elements.push(
        <div key={i} className="flex items-center gap-2 mt-3 mb-1">
          <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0" />
          <span className="font-semibold text-white">{cleanText(trimmedLine)}</span>
        </div>
      );
      i++;
      continue;
    }
    
    // Regular paragraph
    elements.push(
      <p key={i} className="my-1.5 leading-relaxed text-white/90">
        {cleanText(trimmedLine)}
      </p>
    );
    i++;
  }
  
  return elements;
}

// Clean text by removing markdown syntax and formatting inline elements
function cleanText(text: string): React.ReactNode {
  // Remove emoji characters
  let cleaned = text.replace(/[\u{1F300}-\u{1F9FF}]|[\u{2600}-\u{26FF}]|[\u{2700}-\u{27BF}]|[\u{1F600}-\u{1F64F}]|[\u{1F680}-\u{1F6FF}]|📋|📊|📈|📉|⚠️|✅|❌|🔍|💡|🎯|📝|🏛️|🤖|👥|📌/gu, '');
  
  // Process the text to handle bold, code, etc.
  const parts: React.ReactNode[] = [];
  let remaining = cleaned;
  let keyIndex = 0;
  
  while (remaining.length > 0) {
    // Find bold text **text**
    const boldMatch = remaining.match(/\*\*([^*]+)\*\*/);
    if (boldMatch && boldMatch.index !== undefined) {
      // Add text before the bold
      if (boldMatch.index > 0) {
        parts.push(remaining.slice(0, boldMatch.index));
      }
      // Add bold text
      parts.push(
        <span key={keyIndex++} className="font-semibold text-white">
          {boldMatch[1]}
        </span>
      );
      remaining = remaining.slice(boldMatch.index + boldMatch[0].length);
      continue;
    }
    
    // Find code text `text`
    const codeMatch = remaining.match(/`([^`]+)`/);
    if (codeMatch && codeMatch.index !== undefined) {
      // Add text before the code
      if (codeMatch.index > 0) {
        parts.push(remaining.slice(0, codeMatch.index));
      }
      // Add code text
      parts.push(
        <code key={keyIndex++} className="px-1.5 py-0.5 bg-white/15 rounded text-amber-300 font-mono text-sm">
          {codeMatch[1]}
        </code>
      );
      remaining = remaining.slice(codeMatch.index + codeMatch[0].length);
      continue;
    }
    
    // No more special formatting, add the rest
    parts.push(remaining);
    break;
  }
  
  return parts.length === 1 && typeof parts[0] === 'string' ? parts[0] : <>{parts}</>;
}

export default function ChatMessage({ 
  role, 
  content, 
  tiles, 
  type, 
  onTileClick, 
  onContentUpdate, 
  isCompact = false,
  chartData,
  chartConfig,
  isRTL = false,
  recommendations,
  onRecommendationClick,
  content_en,
  content_ar,
  messageId,
  feedbackEnabled = false,
  onClarificationRetry
}: ChatMessageProps) {
  const [displayedContent, setDisplayedContent] = useState('');
  const [textComplete, setTextComplete] = useState(false);
  const [showChart, setShowChart] = useState(false);
  const [showRecommendations, setShowRecommendations] = useState(false);
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const isUser = role === 'user';
  const contentRef = useRef<HTMLDivElement>(null);

  // Determine which content to show based on language
  const effectiveContent = React.useMemo(() => {
    if (isUser) return content; // User messages stay as entered
    // For assistant messages, use language-specific content if available
    if (isRTL && content_ar) return content_ar;
    if (!isRTL && content_en) return content_en;
    return content; // Fallback to original content
  }, [isUser, isRTL, content, content_en, content_ar]);

  // Reset animation states when content changes
  useEffect(() => {
    setTextComplete(false);
    setShowChart(false);
    setShowRecommendations(false);
  }, [effectiveContent]);

  // Fast typewriter effect - complete text first
  useEffect(() => {
    if (type === 'kpi_tiles' || type === 'prediction_tiles') {
      setDisplayedContent('');
      setTextComplete(true);
      return;
    }
    if (!effectiveContent) {
      setDisplayedContent('');
      setTextComplete(true);
      return;
    }
    
    // For user messages, show immediately
    if (isUser) {
      setDisplayedContent(effectiveContent);
      setTextComplete(true);
      return;
    }
    
    // Fast typewriter for assistant - 5ms per character (was 15ms)
    let currentIndex = 0;
    setDisplayedContent('');
    const streamInterval = setInterval(() => {
      if (currentIndex < effectiveContent.length) {
        // Show chunks of 3 characters at a time for faster display
        const endIndex = Math.min(currentIndex + 3, effectiveContent.length);
        setDisplayedContent(effectiveContent.slice(0, endIndex));
        currentIndex = endIndex;
        onContentUpdate?.();
      } else {
        clearInterval(streamInterval);
        setTextComplete(true);
      }
    }, 5);
    return () => clearInterval(streamInterval);
  }, [effectiveContent, type, onContentUpdate, isUser]);

  // Show chart after text is complete (with small delay)
  useEffect(() => {
    if (textComplete && chartData && chartData.length > 0) {
      const timer = setTimeout(() => setShowChart(true), 200);
      return () => clearTimeout(timer);
    }
  }, [textComplete, chartData]);

  // Show recommendations after chart appears (with delay)
  useEffect(() => {
    if (showChart && recommendations && recommendations.length > 0) {
      const timer = setTimeout(() => setShowRecommendations(true), 400);
      return () => clearTimeout(timer);
    } else if (textComplete && !chartData?.length && recommendations && recommendations.length > 0) {
      // If no chart, show recommendations after text
      const timer = setTimeout(() => setShowRecommendations(true), 300);
      return () => clearTimeout(timer);
    }
  }, [showChart, textComplete, recommendations, chartData]);

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
        
        <div className="mt-4 flex items-center gap-2 text-sm text-white/70">
          <ChevronRight className="w-4 h-4 text-amber-400" />
          <span>Click any tile to view detailed analysis and insights</span>
        </div>
      </div>
    );
  }

  return (
    <div 
      className={`${isCompact ? 'mb-2' : 'mb-4 sm:mb-6'} ${isUser ? 'flex justify-end' : ''}`}
      style={{ direction: isRTL ? 'rtl' : 'ltr' }}
    >
      <div className={`flex items-start ${isCompact ? 'gap-2' : 'gap-2 sm:gap-4'} ${isUser ? 'flex-row-reverse max-w-full' : 'max-w-full'}`}>
        {/* Avatar with professional icons - Mobile optimized */}
        <div className={`flex-shrink-0 ${isCompact ? 'w-6 h-6 sm:w-7 sm:h-7' : 'w-7 h-7 sm:w-9 sm:h-9'} rounded-lg sm:rounded-xl ${isUser ? 'bg-gradient-to-br from-[#C0754D] to-[#B6410F]' : 'bg-gradient-to-br from-[#104C64] to-[#0d3d50]'} flex items-center justify-center shadow-lg`}>
          {isUser ? (
            <User className={`${isCompact ? 'w-3 h-3' : 'w-3.5 h-3.5 sm:w-4 sm:h-4'} text-white`} strokeWidth={2.5} />
          ) : (
            <Bot className={`${isCompact ? 'w-3 h-3' : 'w-3.5 h-3.5 sm:w-4 sm:h-4'} text-white`} strokeWidth={2.5} />
          )}
        </div>
        
        <div className="flex-1 min-w-0 overflow-hidden">
          {/* Name label */}
          {!isCompact && (
            <div className={`text-[10px] sm:text-xs font-medium text-white/60 mb-1 sm:mb-1.5 uppercase tracking-wide ${isUser ? 'text-right' : ''}`}>
              {isUser ? (isRTL ? 'أنت' : 'You') : (isRTL ? 'مساعد العُلا' : 'AlUla Assistant')}
            </div>
          )}
          
          {/* Message content with proper formatting - Mobile optimized */}
          <div 
            ref={contentRef}
            className={`rounded-xl sm:rounded-2xl ${isCompact ? 'px-2.5 sm:px-3 py-1.5 sm:py-2 text-sm' : 'px-3 sm:px-4 py-2 sm:py-3'} ${
              isUser 
                ? 'bg-gradient-to-br from-[#C0754D]/30 to-[#B6410F]/20 border border-[#C0754D]/30' 
                : 'bg-white/10 backdrop-blur-sm border border-white/10'
            }`}
          >
            <div className={`text-white/90 ${isUser ? 'text-right' : ''} ${isCompact ? 'text-sm' : 'text-sm sm:text-base'} leading-relaxed overflow-x-auto`}>
              {isUser ? displayedContent : formatContent(displayedContent)}
            </div>
            
            {/* Inline Chart - Only show after text is complete */}
            {!isUser && showChart && chartData && chartData.length > 0 && chartConfig && chartConfig.type !== 'none' && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, ease: "easeOut" }}
              >
                <InlineChart 
                  data={chartData} 
                  config={chartConfig}
                  height={isCompact ? 200 : 280}
                />
              </motion.div>
            )}
            
            {/* Follow-up Recommendations - Show after chart */}
            {!isUser && showRecommendations && recommendations && recommendations.length > 0 && onRecommendationClick && (
              <motion.div 
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, ease: "easeOut" }}
                className="mt-4 pt-4 border-t border-white/10"
              >
                <p className="text-xs text-white/50 mb-3 flex items-center gap-2">
                  <Sparkles className="w-3 h-3" />
                  {isRTL ? 'اقتراحات للمتابعة:' : 'Follow-up suggestions:'}
                </p>
                <div className="grid grid-cols-2 gap-2">
                  {recommendations.map((rec, idx) => (
                    <motion.button
                      key={idx}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.08, duration: 0.3 }}
                      whileHover={{ scale: 1.02, y: -2 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => onRecommendationClick(isRTL ? rec.text_ar : rec.text_en)}
                      className="group flex items-center gap-2 p-3 bg-white/5 hover:bg-white/10 backdrop-blur-lg border border-white/10 hover:border-white/30 rounded-xl text-left transition-all duration-300"
                      dir={isRTL ? "rtl" : "ltr"}
                    >
                      <div className={`w-8 h-8 rounded-lg bg-gradient-to-br ${RECOMMENDATION_GRADIENTS[idx % RECOMMENDATION_GRADIENTS.length]} flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow flex-shrink-0`}>
                        {getRecommendationIcon(rec.icon)}
                      </div>
                      <span className="text-white/70 group-hover:text-white text-xs font-medium transition-colors line-clamp-2">
                        {rec.text}
                      </span>
                      <ChevronRight className="w-4 h-4 text-white/30 group-hover:text-white/60 group-hover:translate-x-1 transition-all flex-shrink-0 ml-auto" />
                    </motion.button>
                  ))}
                </div>
              </motion.div>
            )}
            
            {/* User Feedback Buttons - Show after recommendations */}
            {!isUser && textComplete && feedbackEnabled && messageId && !feedbackSubmitted && (
              <FeedbackButtons
                messageId={messageId}
                isRTL={isRTL}
                onFeedbackSubmitted={(status) => {
                  setFeedbackSubmitted(true);
                  console.log(`Feedback submitted: ${status} for message ${messageId}`);
                }}
                onClarificationRetry={onClarificationRetry}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
