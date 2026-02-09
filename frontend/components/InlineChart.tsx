"use client";

import { useMemo, useState } from "react";
import dynamic from "next/dynamic";
import { motion, AnimatePresence } from "framer-motion";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ComposedChart,
  Area,
  AreaChart,
} from "recharts";
import { useLanguage } from "./LanguageToggle";
import { BarChart3, TrendingUp, PieChart as PieChartIcon, Activity, Maximize2, Minimize2, Map } from "lucide-react";

// Dynamic import for MapChart to avoid SSR issues with Mapbox
const MapChart = dynamic(() => import('./MapChart'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[350px] bg-slate-800/50 rounded-2xl flex items-center justify-center">
      <div className="w-6 h-6 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
    </div>
  )
});

// Modern gradient colors matching AnalysisDashboard
const GRADIENT_COLORS = [
  { start: "#10b981", end: "#059669", name: "emerald" },  // Emerald
  { start: "#f59e0b", end: "#d97706", name: "amber" },    // Amber
  { start: "#3b82f6", end: "#2563eb", name: "blue" },     // Blue
  { start: "#8b5cf6", end: "#7c3aed", name: "violet" },   // Violet
  { start: "#ef4444", end: "#dc2626", name: "red" },      // Red
  { start: "#06b6d4", end: "#0891b2", name: "cyan" },     // Cyan
  { start: "#ec4899", end: "#db2777", name: "pink" },     // Pink
  { start: "#84cc16", end: "#65a30d", name: "lime" },     // Lime
];

const CHART_COLORS = GRADIENT_COLORS.map(c => c.start);

// Custom tooltip with glass effect
const CustomTooltip = ({ active, payload, label, isRTL }: any) => {
  if (active && payload && payload.length) {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="backdrop-blur-xl bg-black/80 border border-white/20 rounded-xl px-4 py-3 shadow-2xl"
        style={{ direction: isRTL ? "rtl" : "ltr" }}
      >
        <p className="text-white/70 text-xs mb-2 font-medium">{label}</p>
        {payload.map((entry: any, index: number) => (
          <div key={index} className="flex items-center gap-2 py-1">
            <div 
              className="w-3 h-3 rounded-full shadow-lg" 
              style={{ background: `linear-gradient(135deg, ${entry.color}, ${entry.color}dd)` }}
            />
            <span className="text-white/90 text-sm font-semibold">
              {entry.name}: <span className="text-white">{typeof entry.value === 'number' ? entry.value.toLocaleString() : entry.value}</span>
            </span>
          </div>
        ))}
      </motion.div>
    );
  }
  return null;
};

// Custom legend with modern styling
const CustomLegend = ({ payload, isRTL }: any) => {
  return (
    <div className={`flex flex-wrap justify-center gap-4 mt-4 ${isRTL ? 'flex-row-reverse' : ''}`}>
      {payload?.map((entry: any, index: number) => (
        <motion.div
          key={index}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          className="flex items-center gap-2 px-3 py-1.5 bg-white/5 backdrop-blur-sm rounded-lg border border-white/10"
        >
          <div 
            className="w-3 h-3 rounded-full shadow-md" 
            style={{ background: entry.color }}
          />
          <span className="text-white/80 text-xs font-medium">{entry.value}</span>
        </motion.div>
      ))}
    </div>
  );
};

// Chart type icon component
const ChartTypeIcon = ({ type }: { type: string }) => {
  const iconProps = { className: "w-4 h-4 text-white", strokeWidth: 2 };
  switch (type) {
    case "bar": return <BarChart3 {...iconProps} />;
    case "line": return <TrendingUp {...iconProps} />;
    case "pie": return <PieChartIcon {...iconProps} />;
    case "area":
    case "composed": return <Activity {...iconProps} />;
    case "map": return <Map {...iconProps} />;
    default: return <BarChart3 {...iconProps} />;
  }
};

interface ChartConfig {
  type: "bar" | "line" | "pie" | "composed" | "area" | "map" | "none";
  xKey?: string;
  yKeys?: string[];
  title?: string;
  title_ar?: string;
  colorBy?: 'violations' | 'score' | 'risk_level' | 'inspections';
}

interface InlineChartProps {
  data: Record<string, any>[];
  config: ChartConfig;
  height?: number;
}

export function InlineChart({ data, config, height = 250 }: InlineChartProps) {
  const { isRTL, language } = useLanguage();
  const [isExpanded, setIsExpanded] = useState(false);
  
  // Use smaller height on mobile
  const isMobile = typeof window !== 'undefined' && window.innerWidth < 640;
  const baseHeight = isMobile ? 220 : height;
  
  // Memoize processed data
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return [];
    return data.map((item) => ({
      ...item,
      // Ensure numeric values
      ...Object.fromEntries(
        Object.entries(item).map(([key, value]) => [
          key,
          typeof value === "string" && !isNaN(Number(value))
            ? Number(value)
            : value,
        ])
      ),
    }));
  }, [data]);

  // Get display name based on language
  const getLabel = (key: string): string => {
    // Try to get Arabic version if RTL
    if (isRTL && data[0]) {
      const arKey = `${key}_ar`;
      if (data[0][arKey]) {
        return String(data[0][arKey]);
      }
    }
    
    // Format key for display
    return key
      .replace(/_/g, " ")
      .replace(/([A-Z])/g, " $1")
      .trim()
      .split(" ")
      .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
      .join(" ");
  };

  if (!data || data.length === 0 || config.type === "none") {
    return null;
  }

  const title = isRTL && config.title_ar ? config.title_ar : config.title;
  const chartHeight = isExpanded ? 400 : baseHeight;

  // Generate gradient definitions for charts
  const renderGradientDefs = () => (
    <defs>
      {GRADIENT_COLORS.map((color, index) => (
        <linearGradient key={index} id={`gradient-${color.name}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color.start} stopOpacity={0.9} />
          <stop offset="100%" stopColor={color.end} stopOpacity={0.6} />
        </linearGradient>
      ))}
      {GRADIENT_COLORS.map((color, index) => (
        <linearGradient key={`area-${index}`} id={`gradient-area-${color.name}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color.start} stopOpacity={0.4} />
          <stop offset="100%" stopColor={color.start} stopOpacity={0.05} />
        </linearGradient>
      ))}
    </defs>
  );

  const renderChart = () => {
    const xKey = config.xKey || Object.keys(data[0])[0];
    const yKeys = config.yKeys || Object.keys(data[0]).filter((k) => k !== xKey && !k.endsWith("_ar"));

    const commonAxisProps = {
      stroke: "rgba(255,255,255,0.3)",
      tick: { fill: "rgba(255,255,255,0.7)", fontSize: 11 },
      tickLine: { stroke: "rgba(255,255,255,0.2)" },
      axisLine: { stroke: "rgba(255,255,255,0.2)" },
    };

    switch (config.type) {
      case "bar":
        return (
          <ResponsiveContainer width="100%" height={chartHeight}>
            <BarChart
              data={chartData}
              layout="horizontal"
              margin={{ top: 20, right: 30, left: isRTL ? 30 : 20, bottom: 5 }}
            >
              {renderGradientDefs()}
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" vertical={false} />
              <XAxis
                dataKey={xKey}
                {...commonAxisProps}
                tickFormatter={(value) => 
                  String(value).length > 12 
                    ? String(value).substring(0, 12) + "..." 
                    : String(value)
                }
              />
              <YAxis {...commonAxisProps} />
              <Tooltip content={<CustomTooltip isRTL={isRTL} />} cursor={{ fill: 'rgba(255,255,255,0.05)' }} />
              <Legend content={<CustomLegend isRTL={isRTL} />} />
              {yKeys.map((key, index) => (
                <Bar
                  key={key}
                  dataKey={key}
                  fill={`url(#gradient-${GRADIENT_COLORS[index % GRADIENT_COLORS.length].name})`}
                  name={getLabel(key)}
                  radius={[8, 8, 0, 0]}
                  animationBegin={index * 100}
                  animationDuration={800}
                  animationEasing="ease-out"
                />
              ))}
            </BarChart>
          </ResponsiveContainer>
        );

      case "line":
        return (
          <ResponsiveContainer width="100%" height={chartHeight}>
            <LineChart
              data={chartData}
              margin={{ top: 20, right: 30, left: isRTL ? 30 : 20, bottom: 5 }}
            >
              {renderGradientDefs()}
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey={xKey} {...commonAxisProps} />
              <YAxis {...commonAxisProps} />
              <Tooltip content={<CustomTooltip isRTL={isRTL} />} />
              <Legend content={<CustomLegend isRTL={isRTL} />} />
              {yKeys.map((key, index) => (
                <Line
                  key={key}
                  type="monotone"
                  dataKey={key}
                  stroke={GRADIENT_COLORS[index % GRADIENT_COLORS.length].start}
                  strokeWidth={3}
                  dot={{ 
                    r: 4, 
                    fill: GRADIENT_COLORS[index % GRADIENT_COLORS.length].start,
                    stroke: 'rgba(255,255,255,0.8)',
                    strokeWidth: 2
                  }}
                  activeDot={{ 
                    r: 7, 
                    fill: GRADIENT_COLORS[index % GRADIENT_COLORS.length].start,
                    stroke: 'white',
                    strokeWidth: 3,
                    filter: 'drop-shadow(0 0 8px rgba(255,255,255,0.5))'
                  }}
                  name={getLabel(key)}
                  animationBegin={index * 100}
                  animationDuration={1000}
                  animationEasing="ease-out"
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        );

      case "pie":
        const pieDataKey = yKeys[0] || "value";
        const nameKey = xKey;
        
        return (
          <ResponsiveContainer width="100%" height={chartHeight}>
            <PieChart>
              {renderGradientDefs()}
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={55}
                outerRadius={85}
                paddingAngle={3}
                dataKey={pieDataKey}
                nameKey={nameKey}
                label={({ name, percent }) =>
                  `${String(name).length > 10 ? String(name).substring(0, 10) + '...' : name}: ${(percent * 100).toFixed(0)}%`
                }
                labelLine={{ stroke: "rgba(255,255,255,0.5)", strokeWidth: 1 }}
                animationBegin={0}
                animationDuration={1200}
                animationEasing="ease-out"
              >
                {chartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={`url(#gradient-${GRADIENT_COLORS[index % GRADIENT_COLORS.length].name})`}
                    stroke="rgba(255,255,255,0.2)"
                    strokeWidth={1}
                  />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip isRTL={isRTL} />} />
              <Legend content={<CustomLegend isRTL={isRTL} />} />
            </PieChart>
          </ResponsiveContainer>
        );

      case "composed":
      case "area":
        return (
          <ResponsiveContainer width="100%" height={chartHeight}>
            <ComposedChart
              data={chartData}
              margin={{ top: 20, right: 30, left: isRTL ? 30 : 20, bottom: 5 }}
            >
              {renderGradientDefs()}
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey={xKey} {...commonAxisProps} />
              <YAxis {...commonAxisProps} />
              <Tooltip content={<CustomTooltip isRTL={isRTL} />} />
              <Legend content={<CustomLegend isRTL={isRTL} />} />
              {yKeys.map((key, index) => {
                const color = GRADIENT_COLORS[index % GRADIENT_COLORS.length];
                // Alternate between Area and Line for composed
                if (index % 2 === 0) {
                  return (
                    <Area
                      key={key}
                      type="monotone"
                      dataKey={key}
                      fill={`url(#gradient-area-${color.name})`}
                      stroke={color.start}
                      strokeWidth={2}
                      name={getLabel(key)}
                      animationBegin={index * 100}
                      animationDuration={1000}
                    />
                  );
                }
                return (
                  <Line
                    key={key}
                    type="monotone"
                    dataKey={key}
                    stroke={color.start}
                    strokeWidth={3}
                    dot={{ r: 4, fill: color.start, stroke: 'white', strokeWidth: 2 }}
                    name={getLabel(key)}
                    animationBegin={index * 100}
                    animationDuration={1000}
                  />
                );
              })}
            </ComposedChart>
          </ResponsiveContainer>
        );

      case "map":
        return (
          <MapChart
            data={chartData}
            title={title}
            isRTL={isRTL}
            colorBy={config.colorBy || 'violations'}
          />
        );

      default:
        return null;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="mt-3 sm:mt-4 relative group"
      style={{ direction: isRTL ? "rtl" : "ltr" }}
    >
      {/* Glass container with gradient border */}
      <div className="relative overflow-hidden rounded-xl sm:rounded-2xl">
        {/* Animated gradient border */}
        <div className="absolute inset-0 bg-gradient-to-r from-amber-500/30 via-orange-500/30 to-amber-500/30 rounded-xl sm:rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
        
        {/* Main content container */}
        <div className="relative m-[1px] bg-white/10 backdrop-blur-xl rounded-xl sm:rounded-2xl border border-white/20 overflow-hidden shadow-2xl">
          {/* Header with title and controls */}
          {title && (
            <div className="flex items-center justify-between px-3 sm:px-5 py-2 sm:py-3 border-b border-white/10 bg-white/5">
              <div className="flex items-center gap-2 sm:gap-3 min-w-0 flex-1">
                <div className="w-6 h-6 sm:w-8 sm:h-8 rounded-lg bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shadow-lg flex-shrink-0">
                  <ChartTypeIcon type={config.type} />
                </div>
                <h4 className="text-xs sm:text-sm font-semibold text-white truncate">
                  {title}
                </h4>
              </div>
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setIsExpanded(!isExpanded)}
                className="p-1.5 sm:p-2 hover:bg-white/10 rounded-lg transition-colors flex-shrink-0"
              >
                {isExpanded ? (
                  <Minimize2 className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-white/60 hover:text-white" />
                ) : (
                  <Maximize2 className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-white/60 hover:text-white" />
                )}
              </motion.button>
            </div>
          )}
          
          {/* Chart area with padding */}
          <motion.div 
            className="p-2 sm:p-4"
            animate={{ height: chartHeight + 40 }}
            transition={{ duration: 0.3, ease: "easeInOut" }}
          >
            <AnimatePresence mode="wait">
              <motion.div
                key={isExpanded ? "expanded" : "collapsed"}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
              >
                {renderChart()}
              </motion.div>
            </AnimatePresence>
          </motion.div>
          
          {/* Subtle glow effect on hover */}
          <div className="absolute inset-0 pointer-events-none opacity-0 group-hover:opacity-100 transition-opacity duration-500">
            <div className="absolute -inset-1 bg-gradient-to-r from-amber-500/10 via-transparent to-orange-500/10 blur-xl" />
          </div>
        </div>
      </div>
    </motion.div>
  );
}

export default InlineChart;
