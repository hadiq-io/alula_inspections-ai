'use client';

import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';
import { 
  BarChart3, 
  GitBranch, 
  LayoutGrid, 
  Flame,
  Download,
  Maximize2,
  Minimize2
} from 'lucide-react';

// Chart types supported by this component
export type AdvancedChartType = 'sankey' | 'treemap' | 'heatmap' | 'sunburst' | 'chord';

interface ChartDataItem {
  name: string;
  name_ar?: string;
  value: number;
  category?: string;
  source?: string;
  target?: string;
  color?: string;
  children?: ChartDataItem[];
  row?: string | number;
  col?: string | number;
}

interface AdvancedChartProps {
  type: AdvancedChartType;
  data: ChartDataItem[];
  title?: string;
  title_ar?: string;
  isRTL?: boolean;
  width?: number;
  height?: number;
  colorScheme?: string[];
  showLegend?: boolean;
  showTooltip?: boolean;
  className?: string;
  onNodeClick?: (node: ChartDataItem) => void;
}

// Default color schemes
const COLOR_SCHEMES = {
  default: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#ec4899', '#84cc16'],
  cool: ['#0ea5e9', '#06b6d4', '#14b8a6', '#10b981', '#22c55e', '#84cc16', '#a3e635', '#d9f99d'],
  warm: ['#f97316', '#f59e0b', '#eab308', '#facc15', '#fde047', '#fef08a', '#fef9c3', '#fefce8'],
  purple: ['#7c3aed', '#8b5cf6', '#a78bfa', '#c4b5fd', '#ddd6fe', '#ede9fe', '#f5f3ff', '#faf5ff'],
  gradient: ['#1e3a8a', '#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe', '#dbeafe', '#eff6ff']
};

// Icon mapping for chart types
const getChartIcon = (type: AdvancedChartType) => {
  switch (type) {
    case 'sankey':
      return <GitBranch className="w-4 h-4" />;
    case 'treemap':
      return <LayoutGrid className="w-4 h-4" />;
    case 'heatmap':
      return <Flame className="w-4 h-4" />;
    case 'sunburst':
      return <BarChart3 className="w-4 h-4" />;
    default:
      return <BarChart3 className="w-4 h-4" />;
  }
};

export default function AdvancedChart({
  type,
  data,
  title,
  title_ar,
  isRTL = false,
  width = 600,
  height = 400,
  colorScheme = COLOR_SCHEMES.default,
  showLegend = true,
  showTooltip = true,
  className = '',
  onNodeClick
}: AdvancedChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [tooltip, setTooltip] = useState<{ x: number; y: number; content: string } | null>(null);
  const [isD3Loaded, setIsD3Loaded] = useState(false);

  const displayTitle = isRTL && title_ar ? title_ar : title;

  // Load D3 dynamically
  useEffect(() => {
    const loadD3 = async () => {
      if (typeof window !== 'undefined') {
        try {
          // Using pure SVG rendering - no D3 dependency needed
          // D3 can be added later for more complex visualizations
          setIsD3Loaded(true);
        } catch (error) {
          console.error('Failed to initialize chart:', error);
        }
      } else {
        setIsD3Loaded(true);
      }
    };
    loadD3();
  }, []);

  // Render appropriate chart based on type
  useEffect(() => {
    if (!svgRef.current || !data || data.length === 0) return;

    const svg = svgRef.current;
    // Clear previous content
    while (svg.firstChild) {
      svg.removeChild(svg.firstChild);
    }

    switch (type) {
      case 'treemap':
        renderTreemap(svg, data, width, height, colorScheme);
        break;
      case 'heatmap':
        renderHeatmap(svg, data, width, height, colorScheme);
        break;
      case 'sankey':
        renderSankey(svg, data, width, height, colorScheme);
        break;
      case 'sunburst':
        renderSunburst(svg, data, width, height, colorScheme);
        break;
      default:
        renderTreemap(svg, data, width, height, colorScheme);
    }
  }, [type, data, width, height, colorScheme, isD3Loaded]);

  const handleDownload = () => {
    if (!svgRef.current) return;
    
    const svgData = new XMLSerializer().serializeToString(svgRef.current);
    const blob = new Blob([svgData], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `${type}-chart.svg`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className={`bg-white/5 border border-white/10 rounded-xl overflow-hidden ${className}`}>
      {/* Header */}
      <div className={`flex items-center justify-between p-3 border-b border-white/10 ${isRTL ? 'flex-row-reverse' : ''}`}>
        <div className={`flex items-center gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
          <div className="p-1.5 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-lg">
            {getChartIcon(type)}
          </div>
          {displayTitle && (
            <h3 className="text-sm font-medium text-white">{displayTitle}</h3>
          )}
        </div>
        
        <div className="flex items-center gap-1">
          <button
            onClick={handleDownload}
            className="p-1.5 hover:bg-white/10 rounded transition-colors"
            title="Download SVG"
          >
            <Download className="w-4 h-4 text-white/50" />
          </button>
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-1.5 hover:bg-white/10 rounded transition-colors"
            title={isFullscreen ? 'Exit fullscreen' : 'Fullscreen'}
          >
            {isFullscreen ? (
              <Minimize2 className="w-4 h-4 text-white/50" />
            ) : (
              <Maximize2 className="w-4 h-4 text-white/50" />
            )}
          </button>
        </div>
      </div>

      {/* Chart container */}
      <div 
        ref={containerRef}
        className={`relative p-4 ${isFullscreen ? 'fixed inset-0 z-50 bg-gray-900' : ''}`}
      >
        <svg
          ref={svgRef}
          width={isFullscreen ? window.innerWidth - 32 : width}
          height={isFullscreen ? window.innerHeight - 100 : height}
          className="mx-auto"
        />

        {/* Tooltip */}
        {showTooltip && tooltip && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="absolute z-10 px-3 py-2 bg-gray-800 border border-white/20 rounded-lg shadow-lg text-sm text-white"
            style={{ left: tooltip.x, top: tooltip.y }}
          >
            {tooltip.content}
          </motion.div>
        )}
      </div>

      {/* Legend */}
      {showLegend && data.length > 0 && (
        <div className={`p-3 border-t border-white/10 ${isRTL ? 'text-right' : 'text-left'}`}>
          <div className={`flex flex-wrap gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
            {getUniqueCategories(data).slice(0, 8).map((category, index) => (
              <div 
                key={category}
                className={`flex items-center gap-1.5 text-xs ${isRTL ? 'flex-row-reverse' : ''}`}
              >
                <div 
                  className="w-3 h-3 rounded-sm"
                  style={{ backgroundColor: colorScheme[index % colorScheme.length] }}
                />
                <span className="text-white/70">{category}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// Helper to get unique categories from data
function getUniqueCategories(data: ChartDataItem[]): string[] {
  const categories = new Set<string>();
  data.forEach(item => {
    if (item.category) categories.add(item.category);
    if (item.name) categories.add(item.name);
  });
  return Array.from(categories);
}

// ============================================================================
// SVG Rendering Functions (Pure SVG, no D3 dependency)
// ============================================================================

function renderTreemap(
  svg: SVGSVGElement,
  data: ChartDataItem[],
  width: number,
  height: number,
  colors: string[]
) {
  const margin = { top: 10, right: 10, bottom: 10, left: 10 };
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  // Calculate total value
  const totalValue = data.reduce((sum, d) => sum + d.value, 0);
  
  // Simple treemap layout (squarified)
  const rects = squarify(data, innerWidth, innerHeight, totalValue);
  
  // Create group for margin
  const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  g.setAttribute('transform', `translate(${margin.left},${margin.top})`);
  svg.appendChild(g);

  // Render rectangles
  rects.forEach((rect, i) => {
    // Rectangle
    const rectEl = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rectEl.setAttribute('x', String(rect.x));
    rectEl.setAttribute('y', String(rect.y));
    rectEl.setAttribute('width', String(Math.max(0, rect.width - 2)));
    rectEl.setAttribute('height', String(Math.max(0, rect.height - 2)));
    rectEl.setAttribute('fill', colors[i % colors.length]);
    rectEl.setAttribute('rx', '4');
    rectEl.setAttribute('opacity', '0.8');
    rectEl.style.cursor = 'pointer';
    rectEl.style.transition = 'opacity 0.2s';
    rectEl.addEventListener('mouseenter', () => rectEl.setAttribute('opacity', '1'));
    rectEl.addEventListener('mouseleave', () => rectEl.setAttribute('opacity', '0.8'));
    g.appendChild(rectEl);

    // Label (if rect is big enough)
    if (rect.width > 60 && rect.height > 30) {
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', String(rect.x + rect.width / 2));
      text.setAttribute('y', String(rect.y + rect.height / 2));
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('dominant-baseline', 'middle');
      text.setAttribute('fill', 'white');
      text.setAttribute('font-size', '12');
      text.setAttribute('font-weight', '500');
      text.style.pointerEvents = 'none';
      text.textContent = rect.name.length > 15 ? rect.name.slice(0, 12) + '...' : rect.name;
      g.appendChild(text);

      // Value
      const valueText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      valueText.setAttribute('x', String(rect.x + rect.width / 2));
      valueText.setAttribute('y', String(rect.y + rect.height / 2 + 14));
      valueText.setAttribute('text-anchor', 'middle');
      valueText.setAttribute('dominant-baseline', 'middle');
      valueText.setAttribute('fill', 'rgba(255,255,255,0.7)');
      valueText.setAttribute('font-size', '10');
      valueText.style.pointerEvents = 'none';
      valueText.textContent = formatValue(rect.value);
      g.appendChild(valueText);
    }
  });
}

function renderHeatmap(
  svg: SVGSVGElement,
  data: ChartDataItem[],
  width: number,
  height: number,
  colors: string[]
) {
  const margin = { top: 30, right: 30, bottom: 30, left: 60 };
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  // Get unique rows and columns
  const rows = [...new Set(data.map(d => String(d.row || d.category || 'Row')))];
  const cols = [...new Set(data.map(d => String(d.col || d.name)))];
  
  const cellWidth = innerWidth / cols.length;
  const cellHeight = innerHeight / rows.length;

  // Find min/max values for color scaling
  const values = data.map(d => d.value);
  const minValue = Math.min(...values);
  const maxValue = Math.max(...values);

  // Create group for margin
  const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  g.setAttribute('transform', `translate(${margin.left},${margin.top})`);
  svg.appendChild(g);

  // Render cells
  data.forEach(item => {
    const rowIdx = rows.indexOf(String(item.row || item.category || 'Row'));
    const colIdx = cols.indexOf(String(item.col || item.name));
    
    if (rowIdx === -1 || colIdx === -1) return;

    const x = colIdx * cellWidth;
    const y = rowIdx * cellHeight;
    
    // Calculate color based on value
    const normalizedValue = (item.value - minValue) / (maxValue - minValue || 1);
    const colorIdx = Math.floor(normalizedValue * (colors.length - 1));
    
    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.setAttribute('x', String(x));
    rect.setAttribute('y', String(y));
    rect.setAttribute('width', String(cellWidth - 2));
    rect.setAttribute('height', String(cellHeight - 2));
    rect.setAttribute('fill', colors[colorIdx]);
    rect.setAttribute('rx', '2');
    g.appendChild(rect);

    // Value label (if cell is big enough)
    if (cellWidth > 30 && cellHeight > 20) {
      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', String(x + cellWidth / 2));
      text.setAttribute('y', String(y + cellHeight / 2));
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('dominant-baseline', 'middle');
      text.setAttribute('fill', normalizedValue > 0.5 ? 'white' : 'black');
      text.setAttribute('font-size', '10');
      text.textContent = formatValue(item.value);
      g.appendChild(text);
    }
  });

  // Row labels
  rows.forEach((row, i) => {
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', '-5');
    text.setAttribute('y', String(i * cellHeight + cellHeight / 2));
    text.setAttribute('text-anchor', 'end');
    text.setAttribute('dominant-baseline', 'middle');
    text.setAttribute('fill', 'rgba(255,255,255,0.7)');
    text.setAttribute('font-size', '10');
    text.textContent = row.length > 10 ? row.slice(0, 8) + '...' : row;
    g.appendChild(text);
  });

  // Column labels
  cols.forEach((col, i) => {
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', String(i * cellWidth + cellWidth / 2));
    text.setAttribute('y', '-10');
    text.setAttribute('text-anchor', 'middle');
    text.setAttribute('fill', 'rgba(255,255,255,0.7)');
    text.setAttribute('font-size', '10');
    text.textContent = col.length > 10 ? col.slice(0, 8) + '...' : col;
    g.appendChild(text);
  });
}

function renderSankey(
  svg: SVGSVGElement,
  data: ChartDataItem[],
  width: number,
  height: number,
  colors: string[]
) {
  const margin = { top: 20, right: 20, bottom: 20, left: 20 };
  const innerWidth = width - margin.left - margin.right;
  const innerHeight = height - margin.top - margin.bottom;

  // Get unique nodes
  const sources = new Set<string>();
  const targets = new Set<string>();
  data.forEach(d => {
    if (d.source) sources.add(d.source);
    if (d.target) targets.add(d.target);
  });

  const sourceNodes = Array.from(sources);
  const targetNodes = Array.from(targets);
  
  const nodeWidth = 20;
  const sourceX = 0;
  const targetX = innerWidth - nodeWidth;
  
  // Create group
  const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  g.setAttribute('transform', `translate(${margin.left},${margin.top})`);
  svg.appendChild(g);

  // Calculate node heights based on values
  const sourceValues: Record<string, number> = {};
  const targetValues: Record<string, number> = {};
  
  data.forEach(d => {
    if (d.source) sourceValues[d.source] = (sourceValues[d.source] || 0) + d.value;
    if (d.target) targetValues[d.target] = (targetValues[d.target] || 0) + d.value;
  });

  const totalSourceValue = Object.values(sourceValues).reduce((a, b) => a + b, 0);
  const totalTargetValue = Object.values(targetValues).reduce((a, b) => a + b, 0);

  // Calculate positions
  const sourcePositions: Record<string, { y: number; height: number }> = {};
  const targetPositions: Record<string, { y: number; height: number }> = {};
  
  let sourceY = 0;
  sourceNodes.forEach((node, i) => {
    const nodeHeight = (sourceValues[node] / totalSourceValue) * innerHeight;
    sourcePositions[node] = { y: sourceY, height: nodeHeight };
    sourceY += nodeHeight + 5;
  });

  let targetY = 0;
  targetNodes.forEach((node, i) => {
    const nodeHeight = (targetValues[node] / totalTargetValue) * innerHeight;
    targetPositions[node] = { y: targetY, height: nodeHeight };
    targetY += nodeHeight + 5;
  });

  // Render links
  data.forEach((d, i) => {
    if (!d.source || !d.target) return;
    
    const sourcePos = sourcePositions[d.source];
    const targetPos = targetPositions[d.target];
    if (!sourcePos || !targetPos) return;

    const linkHeight = (d.value / sourceValues[d.source]) * sourcePos.height;
    
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    const pathD = `
      M ${sourceX + nodeWidth} ${sourcePos.y + linkHeight / 2}
      C ${innerWidth / 2} ${sourcePos.y + linkHeight / 2},
        ${innerWidth / 2} ${targetPos.y + linkHeight / 2},
        ${targetX} ${targetPos.y + linkHeight / 2}
    `;
    path.setAttribute('d', pathD);
    path.setAttribute('fill', 'none');
    path.setAttribute('stroke', colors[i % colors.length]);
    path.setAttribute('stroke-width', String(Math.max(1, linkHeight)));
    path.setAttribute('opacity', '0.4');
    g.appendChild(path);
  });

  // Render source nodes
  sourceNodes.forEach((node, i) => {
    const pos = sourcePositions[node];
    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.setAttribute('x', String(sourceX));
    rect.setAttribute('y', String(pos.y));
    rect.setAttribute('width', String(nodeWidth));
    rect.setAttribute('height', String(pos.height));
    rect.setAttribute('fill', colors[i % colors.length]);
    rect.setAttribute('rx', '3');
    g.appendChild(rect);

    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', String(sourceX + nodeWidth + 5));
    text.setAttribute('y', String(pos.y + pos.height / 2));
    text.setAttribute('dominant-baseline', 'middle');
    text.setAttribute('fill', 'rgba(255,255,255,0.8)');
    text.setAttribute('font-size', '11');
    text.textContent = node;
    g.appendChild(text);
  });

  // Render target nodes
  targetNodes.forEach((node, i) => {
    const pos = targetPositions[node];
    const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    rect.setAttribute('x', String(targetX));
    rect.setAttribute('y', String(pos.y));
    rect.setAttribute('width', String(nodeWidth));
    rect.setAttribute('height', String(pos.height));
    rect.setAttribute('fill', colors[(sourceNodes.length + i) % colors.length]);
    rect.setAttribute('rx', '3');
    g.appendChild(rect);

    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', String(targetX - 5));
    text.setAttribute('y', String(pos.y + pos.height / 2));
    text.setAttribute('text-anchor', 'end');
    text.setAttribute('dominant-baseline', 'middle');
    text.setAttribute('fill', 'rgba(255,255,255,0.8)');
    text.setAttribute('font-size', '11');
    text.textContent = node;
    g.appendChild(text);
  });
}

function renderSunburst(
  svg: SVGSVGElement,
  data: ChartDataItem[],
  width: number,
  height: number,
  colors: string[]
) {
  const centerX = width / 2;
  const centerY = height / 2;
  const radius = Math.min(width, height) / 2 - 40;

  const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
  g.setAttribute('transform', `translate(${centerX},${centerY})`);
  svg.appendChild(g);

  const totalValue = data.reduce((sum, d) => sum + d.value, 0);
  let currentAngle = 0;

  data.forEach((item, i) => {
    const angle = (item.value / totalValue) * 2 * Math.PI;
    
    // Create arc path
    const startAngle = currentAngle;
    const endAngle = currentAngle + angle;
    
    const innerRadius = radius * 0.3;
    const outerRadius = radius;
    
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    const pathD = describeArc(0, 0, innerRadius, outerRadius, startAngle, endAngle);
    path.setAttribute('d', pathD);
    path.setAttribute('fill', colors[i % colors.length]);
    path.setAttribute('stroke', 'rgba(0,0,0,0.2)');
    path.setAttribute('stroke-width', '1');
    path.style.cursor = 'pointer';
    path.style.transition = 'opacity 0.2s';
    path.addEventListener('mouseenter', () => path.setAttribute('opacity', '0.8'));
    path.addEventListener('mouseleave', () => path.setAttribute('opacity', '1'));
    g.appendChild(path);

    // Add label (if arc is big enough)
    if (angle > 0.3) {
      const labelAngle = startAngle + angle / 2;
      const labelRadius = (innerRadius + outerRadius) / 2;
      const labelX = Math.cos(labelAngle - Math.PI / 2) * labelRadius;
      const labelY = Math.sin(labelAngle - Math.PI / 2) * labelRadius;

      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', String(labelX));
      text.setAttribute('y', String(labelY));
      text.setAttribute('text-anchor', 'middle');
      text.setAttribute('dominant-baseline', 'middle');
      text.setAttribute('fill', 'white');
      text.setAttribute('font-size', '10');
      text.setAttribute('font-weight', '500');
      text.style.pointerEvents = 'none';
      text.textContent = item.name.length > 10 ? item.name.slice(0, 8) + '...' : item.name;
      g.appendChild(text);
    }

    currentAngle = endAngle;
  });

  // Center circle
  const centerCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
  centerCircle.setAttribute('cx', '0');
  centerCircle.setAttribute('cy', '0');
  centerCircle.setAttribute('r', String(radius * 0.3 - 2));
  centerCircle.setAttribute('fill', 'rgba(17,24,39,0.9)');
  g.appendChild(centerCircle);

  // Center text
  const centerText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
  centerText.setAttribute('x', '0');
  centerText.setAttribute('y', '0');
  centerText.setAttribute('text-anchor', 'middle');
  centerText.setAttribute('dominant-baseline', 'middle');
  centerText.setAttribute('fill', 'white');
  centerText.setAttribute('font-size', '14');
  centerText.setAttribute('font-weight', '600');
  centerText.textContent = formatValue(totalValue);
  g.appendChild(centerText);
}

// ============================================================================
// Helper Functions
// ============================================================================

function squarify(
  data: ChartDataItem[],
  width: number,
  height: number,
  totalValue: number
): (ChartDataItem & { x: number; y: number; width: number; height: number })[] {
  const sorted = [...data].sort((a, b) => b.value - a.value);
  const result: (ChartDataItem & { x: number; y: number; width: number; height: number })[] = [];
  
  let x = 0, y = 0;
  let remainingWidth = width, remainingHeight = height;
  let remainingValue = totalValue;

  sorted.forEach((item, i) => {
    const areaRatio = item.value / remainingValue;
    let itemWidth, itemHeight;

    if (remainingWidth > remainingHeight) {
      itemWidth = remainingWidth * areaRatio;
      itemHeight = remainingHeight;
      result.push({ ...item, x, y, width: itemWidth, height: itemHeight });
      x += itemWidth;
      remainingWidth -= itemWidth;
    } else {
      itemWidth = remainingWidth;
      itemHeight = remainingHeight * areaRatio;
      result.push({ ...item, x, y, width: itemWidth, height: itemHeight });
      y += itemHeight;
      remainingHeight -= itemHeight;
    }

    remainingValue -= item.value;
  });

  return result;
}

function describeArc(
  cx: number,
  cy: number,
  innerRadius: number,
  outerRadius: number,
  startAngle: number,
  endAngle: number
): string {
  const startOuter = polarToCartesian(cx, cy, outerRadius, endAngle);
  const endOuter = polarToCartesian(cx, cy, outerRadius, startAngle);
  const startInner = polarToCartesian(cx, cy, innerRadius, endAngle);
  const endInner = polarToCartesian(cx, cy, innerRadius, startAngle);

  const largeArcFlag = endAngle - startAngle <= Math.PI ? 0 : 1;

  return [
    'M', startOuter.x, startOuter.y,
    'A', outerRadius, outerRadius, 0, largeArcFlag, 0, endOuter.x, endOuter.y,
    'L', endInner.x, endInner.y,
    'A', innerRadius, innerRadius, 0, largeArcFlag, 1, startInner.x, startInner.y,
    'Z'
  ].join(' ');
}

function polarToCartesian(cx: number, cy: number, radius: number, angle: number) {
  return {
    x: cx + radius * Math.cos(angle - Math.PI / 2),
    y: cy + radius * Math.sin(angle - Math.PI / 2)
  };
}

function formatValue(value: number): string {
  if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
  if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
  return value.toFixed(0);
}

// Example usage
export function AdvancedChartExample() {
  const treemapData: ChartDataItem[] = [
    { name: 'Al-Ula Old Town', value: 245, category: 'High Traffic' },
    { name: 'Heritage Village', value: 189, category: 'High Traffic' },
    { name: 'Downtown', value: 156, category: 'Medium' },
    { name: 'Market District', value: 134, category: 'Medium' },
    { name: 'Industrial Zone', value: 98, category: 'Low' },
    { name: 'Residential Area', value: 67, category: 'Low' }
  ];

  return (
    <AdvancedChart
      type="treemap"
      data={treemapData}
      title="Inspections by Location"
      width={600}
      height={400}
    />
  );
}
