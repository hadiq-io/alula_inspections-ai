import { X, TrendingUp, AlertTriangle, Users, Calendar, MapPin, CheckCircle, XCircle, BarChart3, Activity, Zap, Clock, Target, Shield, Gauge, Brain, Eye, Layers, GitBranch, Database, Cpu, FileCheck, Timer, Award, PieChart as PieChartIcon } from 'lucide-react';
import { motion } from 'framer-motion';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ComposedChart, ScatterChart, Scatter } from 'recharts';

interface AnalysisDashboardProps {
  type: 'predictions' | 'kpis' | null;
  onClose: () => void;
  isCompact?: boolean;
}

export default function AnalysisDashboard({ type, onClose, isCompact = false }: AnalysisDashboardProps) {
  if (!type) return null;

  // KPI Data
  const monthlyInspections = [
    { month: 'Jan', inspections: 145, target: 150 },
    { month: 'Feb', inspections: 178, target: 150 },
    { month: 'Mar', inspections: 162, target: 150 },
    { month: 'Apr', inspections: 189, target: 150 },
    { month: 'May', inspections: 201, target: 150 },
    { month: 'Jun', inspections: 195, target: 150 },
  ];

  const complianceRate = [
    { month: 'Jan', rate: 87 },
    { month: 'Feb', rate: 89 },
    { month: 'Mar', rate: 92 },
    { month: 'Apr', rate: 88 },
    { month: 'May', rate: 94 },
    { month: 'Jun', rate: 96 },
  ];

  const inspectorPerformance = [
    { name: 'Ahmed Al-Rashid', inspections: 89, compliance: 98 },
    { name: 'Fatima Hassan', inspections: 76, compliance: 96 },
    { name: 'Omar Khalil', inspections: 82, compliance: 94 },
    { name: 'Layla Ibrahim', inspections: 71, compliance: 92 },
    { name: 'Yusuf Mansour', inspections: 68, compliance: 91 },
  ];

  const locationRisk = [
    { name: 'Low Risk', value: 45, color: '#10b981' },
    { name: 'Medium Risk', value: 35, color: '#f59e0b' },
    { name: 'High Risk', value: 20, color: '#ef4444' },
  ];

  const issueCategories = [
    { category: 'Structural', count: 28 },
    { category: 'Environmental', count: 42 },
    { category: 'Safety', count: 19 },
    { category: 'Documentation', count: 15 },
    { category: 'Maintenance', count: 34 },
  ];

  const weeklyTrend = [
    { week: 'Week 1', count: 32 },
    { week: 'Week 2', count: 45 },
    { week: 'Week 3', count: 38 },
    { week: 'Week 4', count: 51 },
  ];

  // Additional KPI Data (7-10)
  const responseTimeData = [
    { month: 'Jan', avgTime: 4.2, target: 3.5 },
    { month: 'Feb', avgTime: 3.8, target: 3.5 },
    { month: 'Mar', avgTime: 3.2, target: 3.5 },
    { month: 'Apr', avgTime: 2.9, target: 3.5 },
    { month: 'May', avgTime: 2.5, target: 3.5 },
    { month: 'Jun', avgTime: 2.3, target: 3.5 },
  ];

  const siteConditionScores = [
    { site: 'Hegra Tombs', score: 92, lastMonth: 89 },
    { site: 'Dadan Sanctuary', score: 87, lastMonth: 85 },
    { site: 'Jabal Ikmah', score: 95, lastMonth: 94 },
    { site: 'Old Town District', score: 78, lastMonth: 82 },
    { site: 'Elephant Rock', score: 96, lastMonth: 95 },
  ];

  const budgetUtilization = [
    { category: 'Personnel', allocated: 450000, spent: 412000 },
    { category: 'Equipment', allocated: 180000, spent: 165000 },
    { category: 'Transportation', allocated: 95000, spent: 88000 },
    { category: 'Training', allocated: 65000, spent: 52000 },
    { category: 'Technology', allocated: 120000, spent: 118000 },
  ];

  const stakeholderSatisfaction = [
    { category: 'Response Time', score: 4.5 },
    { category: 'Report Quality', score: 4.7 },
    { category: 'Communication', score: 4.3 },
    { category: 'Technical Expertise', score: 4.8 },
    { category: 'Issue Resolution', score: 4.2 },
    { category: 'Overall Satisfaction', score: 4.5 },
  ];

  // ML Prediction Data
  const volumeForecast = [
    { month: 'Jul', actual: 195, predicted: 210 },
    { month: 'Aug', actual: null, predicted: 225 },
    { month: 'Sep', actual: null, predicted: 218 },
    { month: 'Oct', actual: null, predicted: 230 },
    { month: 'Nov', actual: null, predicted: 245 },
    { month: 'Dec', actual: null, predicted: 240 },
  ];

  const complianceForecast = [
    { month: 'Jul', rate: 97 },
    { month: 'Aug', rate: 96 },
    { month: 'Sep', rate: 98 },
    { month: 'Oct', rate: 97 },
    { month: 'Nov', rate: 99 },
    { month: 'Dec', rate: 98 },
  ];

  const riskPrediction = [
    { location: 'Hegra', risk: 25, trend: 'decreasing' },
    { location: 'Dadan', risk: 45, trend: 'increasing' },
    { location: 'Jabal Ikmah', risk: 18, trend: 'stable' },
    { location: 'Old Town', risk: 62, trend: 'increasing' },
    { location: 'Elephant Rock', risk: 12, trend: 'decreasing' },
  ];

  const anomalyDetection = [
    { type: 'Temperature Spike', severity: 'High', locations: 8 },
    { type: 'Moisture Level', severity: 'Medium', locations: 12 },
    { type: 'Visitor Traffic', severity: 'Low', locations: 5 },
    { type: 'Structural Stress', severity: 'High', locations: 3 },
  ];

  const modelAccuracy = [
    { model: 'Risk Predictor', accuracy: 94.2 },
    { model: 'Volume Forecast', accuracy: 91.8 },
    { model: 'Compliance ML', accuracy: 96.5 },
    { model: 'Anomaly Detector', accuracy: 89.3 },
  ];

  // Additional ML Prediction Data (6-10)
  const resourceOptimization = [
    { month: 'Jul', current: 85, optimized: 92 },
    { month: 'Aug', current: 78, optimized: 94 },
    { month: 'Sep', current: 82, optimized: 95 },
    { month: 'Oct', current: 88, optimized: 96 },
    { month: 'Nov', current: 75, optimized: 93 },
    { month: 'Dec', current: 80, optimized: 97 },
  ];

  const deteriorationPrediction = [
    { site: 'Hegra North Wall', current: 85, predicted6Mo: 78, predicted12Mo: 71, priority: 'Medium' },
    { site: 'Dadan Temple A', current: 72, predicted6Mo: 65, predicted12Mo: 55, priority: 'High' },
    { site: 'Jabal Inscriptions', current: 94, predicted6Mo: 92, predicted12Mo: 89, priority: 'Low' },
    { site: 'Old Town Facade', current: 68, predicted6Mo: 58, predicted12Mo: 45, priority: 'Critical' },
    { site: 'Rock Art Section', current: 88, predicted6Mo: 84, predicted12Mo: 79, priority: 'Low' },
  ];

  const visitorImpactPrediction = [
    { month: 'Jul', visitors: 12500, riskScore: 35 },
    { month: 'Aug', visitors: 18200, riskScore: 52 },
    { month: 'Sep', visitors: 15800, riskScore: 44 },
    { month: 'Oct', visitors: 22100, riskScore: 68 },
    { month: 'Nov', visitors: 28500, riskScore: 82 },
    { month: 'Dec', visitors: 31200, riskScore: 88 },
  ];

  const maintenanceSchedulePrediction = [
    { task: 'Structural Reinforcement', urgency: 92, daysUntil: 14, cost: 45000 },
    { task: 'Climate Control Update', urgency: 78, daysUntil: 30, cost: 28000 },
    { task: 'Erosion Prevention', urgency: 85, daysUntil: 21, cost: 35000 },
    { task: 'Lighting System Upgrade', urgency: 45, daysUntil: 60, cost: 18000 },
    { task: 'Security Enhancement', urgency: 62, daysUntil: 45, cost: 22000 },
  ];

  const seasonalPatterns = [
    { subject: 'Visitor Volume', Jan: 65, Apr: 85, Jul: 95, Oct: 78 },
    { subject: 'Risk Level', Jan: 42, Apr: 55, Jul: 78, Oct: 48 },
    { subject: 'Staffing Need', Jan: 70, Apr: 80, Jul: 98, Oct: 75 },
    { subject: 'Maintenance', Jan: 85, Apr: 72, Jul: 45, Oct: 68 },
    { subject: 'Budget Pressure', Jan: 55, Apr: 65, Jul: 88, Oct: 72 },
  ];

  return (
    <motion.div
      initial={{ x: '100%', opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: '100%', opacity: 0 }}
      transition={{ type: 'spring', damping: 30, stiffness: 300 }}
      className="h-full backdrop-blur-2xl bg-black/30 border-l border-white/20 flex flex-col"
    >
      {/* Header - Mobile optimized */}
      <div className={`flex items-center justify-between ${isCompact ? 'px-3 sm:px-4 py-2.5 sm:py-3' : 'px-4 sm:px-6 py-4 sm:py-5'} bg-white/5 border-b border-white/20`}>
        <div className="flex items-center gap-2 sm:gap-3">
          {type === 'predictions' ? (
            <div className={`${isCompact ? 'w-7 h-7 sm:w-8 sm:h-8' : 'w-8 h-8 sm:w-10 sm:h-10'} rounded-lg sm:rounded-xl bg-gradient-to-br from-[#C0754D] to-[#B6410F] flex items-center justify-center shadow-lg`}>
              <Zap className={`${isCompact ? 'w-3.5 h-3.5 sm:w-4 sm:h-4' : 'w-4 h-4 sm:w-5 sm:h-5'} text-white`} strokeWidth={2.5} />
            </div>
          ) : (
            <div className={`${isCompact ? 'w-7 h-7 sm:w-8 sm:h-8' : 'w-8 h-8 sm:w-10 sm:h-10'} rounded-lg sm:rounded-xl bg-gradient-to-br from-[#104C64] to-[#0d3d50] flex items-center justify-center shadow-lg`}>
              <BarChart3 className={`${isCompact ? 'w-3.5 h-3.5 sm:w-4 sm:h-4' : 'w-4 h-4 sm:w-5 sm:h-5'} text-white`} strokeWidth={2.5} />
            </div>
          )}
          <h2 className={`${isCompact ? 'text-base sm:text-lg' : 'text-lg sm:text-2xl'} font-bold text-white`}>
            {type === 'predictions' ? 'ML Predictions' : 'KPIs Dashboard'}
          </h2>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 sm:p-2 hover:bg-white/10 rounded-lg transition-colors"
        >
          <X className="w-4 h-4 sm:w-5 sm:h-5 text-white/70 hover:text-white" />
        </button>
      </div>

      {/* Content - Mobile optimized */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-3 sm:p-6">
        <div className="space-y-4 sm:space-y-6">
          {type === 'predictions' ? (
            <>
              {/* ML Prediction 1: Volume Forecast */}
              <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl sm:rounded-2xl p-4 sm:p-6 shadow-2xl">
                <div className="flex items-center gap-2 sm:gap-3 mb-3 sm:mb-4">
                  <TrendingUp className="w-5 h-5 sm:w-6 sm:h-6 text-[#C0754D]" />
                  <div>
                    <h3 className="text-base sm:text-lg font-bold text-white">Inspection Volume Forecast</h3>
                    <p className="text-xs sm:text-sm text-white/70">LSTM neural network predicts 15% increase over next 6 months based on seasonal patterns and historical trends</p>
                  </div>
                </div>
                <div className="mb-3 sm:mb-4 p-2 sm:p-3 bg-[#C0754D]/20 border border-[#C0754D]/30 rounded-lg sm:rounded-xl">
                  <p className="text-[10px] sm:text-xs text-[#e8b896]"><strong>Model Confidence: 94.2%</strong> — Forecast incorporates tourism seasonality, weather patterns, and scheduled heritage events. December peak aligns with winter tourism surge.</p>
                </div>
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={volumeForecast}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="month" stroke="#fff" tick={{ fontSize: 10 }} />
                    <YAxis stroke="#fff" tick={{ fontSize: 10 }} />
                    <Tooltip contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: '1px solid rgba(255,255,255,0.2)', fontSize: 12 }} />
                    <Legend wrapperStyle={{ fontSize: 10 }} />
                    <Line type="monotone" dataKey="actual" stroke="#10b981" strokeWidth={2} name="Actual" />
                    <Line type="monotone" dataKey="predicted" stroke="#f59e0b" strokeWidth={2} strokeDasharray="5 5" name="Predicted" />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* ML Prediction 2: Compliance Forecast */}
              <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl sm:rounded-2xl p-4 sm:p-6 shadow-2xl">
                <div className="flex items-center gap-2 sm:gap-3 mb-3 sm:mb-4">
                  <CheckCircle className="w-5 h-5 sm:w-6 sm:h-6 text-green-400" />
                  <div>
                    <h3 className="text-base sm:text-lg font-bold text-white">Compliance Rate Forecast</h3>
                    <p className="text-xs sm:text-sm text-white/70">Gradient boosting model predicts sustained 97%+ compliance through Q4, exceeding regulatory thresholds</p>
                  </div>
                </div>
                <div className="mb-4 p-3 bg-green-500/10 border border-green-500/20 rounded-xl">
                  <p className="text-xs text-green-300"><strong>Model Confidence: 96.5%</strong> — November projected to achieve 99% compliance, the highest in program history. Continuous training improvements driving upward trend.</p>
                </div>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={complianceForecast}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="month" stroke="#fff" />
                    <YAxis stroke="#fff" domain={[85, 100]} />
                    <Tooltip contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: '1px solid rgba(255,255,255,0.2)' }} />
                    <Bar dataKey="rate" fill="#10b981" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* ML Prediction 3: Risk Assessment */}
              <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-2xl">
                <div className="flex items-center gap-3 mb-4">
                  <AlertTriangle className="w-6 h-6 text-orange-400" />
                  <div>
                    <h3 className="text-lg font-bold text-white">Dynamic Risk Prediction</h3>
                    <p className="text-sm text-white/70">Random forest classifier identifies emerging risk patterns across heritage sites with real-time sensor integration</p>
                  </div>
                </div>
                <div className="mb-4 p-3 bg-orange-500/10 border border-orange-500/20 rounded-xl">
                  <p className="text-xs text-orange-300"><strong>Alert:</strong> Old Town showing 62% risk score with increasing trend. Dadan Sanctuary risk elevated by 12% due to recent environmental factors.</p>
                </div>
                <div className="space-y-3">
                  {riskPrediction.map((loc, i) => (
                    <div key={i} className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
                      <div className="flex items-center gap-3">
                        <MapPin className="w-5 h-5 text-[#C0754D]" />
                        <span className="text-white font-semibold">{loc.location}</span>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                          <div className="w-32 bg-white/10 rounded-full h-2">
                            <div 
                              className={`h-2 rounded-full ${loc.risk > 50 ? 'bg-red-500' : loc.risk > 30 ? 'bg-orange-500' : 'bg-green-500'}`}
                              style={{ width: `${loc.risk}%` }}
                            ></div>
                          </div>
                          <span className="text-white/80 text-sm">{loc.risk}%</span>
                        </div>
                        <span className={`text-xs px-2 py-1 rounded ${loc.trend === 'increasing' ? 'bg-red-500/20 text-red-300' : loc.trend === 'decreasing' ? 'bg-green-500/20 text-green-300' : 'bg-blue-500/20 text-blue-300'}`}>
                          {loc.trend}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* ML Prediction 4: Anomaly Detection */}
              <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-2xl">
                <div className="flex items-center gap-3 mb-4">
                  <Activity className="w-6 h-6 text-purple-400" />
                  <div>
                    <h3 className="text-lg font-bold text-white">Anomaly Detection System</h3>
                    <p className="text-sm text-white/70">Isolation forest algorithm monitors 500+ sensor streams to detect unusual patterns requiring immediate attention</p>
                  </div>
                </div>
                <div className="mb-4 p-3 bg-purple-500/10 border border-purple-500/20 rounded-xl">
                  <p className="text-xs text-purple-300"><strong>Active Monitoring:</strong> 8 locations flagged for temperature anomalies exceeding 2 standard deviations. Structural stress detected at 3 critical heritage structures.</p>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  {anomalyDetection.map((anomaly, i) => (
                    <div key={i} className="p-4 bg-white/5 rounded-xl border border-white/10">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-white font-semibold text-sm">{anomaly.type}</span>
                        <span className={`text-xs px-2 py-1 rounded ${anomaly.severity === 'High' ? 'bg-red-500/20 text-red-300' : anomaly.severity === 'Medium' ? 'bg-orange-500/20 text-orange-300' : 'bg-green-500/20 text-green-300'}`}>
                          {anomaly.severity}
                        </span>
                      </div>
                      <div className="text-2xl font-bold text-white">{anomaly.locations}</div>
                      <div className="text-xs text-white/60">locations affected</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* ML Prediction 5: Model Accuracy */}
              <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-2xl">
                <div className="flex items-center gap-3 mb-4">
                  <Zap className="w-6 h-6 text-yellow-400" />
                  <div>
                    <h3 className="text-lg font-bold text-white">ML Model Performance Metrics</h3>
                    <p className="text-sm text-white/70">Production model accuracy scores with continuous retraining on new inspection data</p>
                  </div>
                </div>
                <div className="mb-4 p-3 bg-yellow-500/10 border border-yellow-500/20 rounded-xl">
                  <p className="text-xs text-yellow-300"><strong>Model Health:</strong> All 4 production models exceed 89% accuracy threshold. Compliance ML leads at 96.5% after recent feature engineering improvements.</p>
                </div>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={modelAccuracy} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis type="number" domain={[80, 100]} stroke="#fff" />
                    <YAxis dataKey="model" type="category" stroke="#fff" width={120} />
                    <Tooltip contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: '1px solid rgba(255,255,255,0.2)' }} />
                    <Bar dataKey="accuracy" fill="#8b5cf6" radius={[0, 8, 8, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* ML Prediction 6: Resource Optimization */}
              <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-2xl">
                <div className="flex items-center gap-3 mb-4">
                  <Cpu className="w-6 h-6 text-cyan-400" />
                  <div>
                    <h3 className="text-lg font-bold text-white">AI-Driven Resource Optimization</h3>
                    <p className="text-sm text-white/70">Machine learning algorithms recommend optimal resource allocation, projecting 15% efficiency gains through intelligent scheduling</p>
                  </div>
                </div>
                <div className="mb-4 p-3 bg-cyan-500/10 border border-cyan-500/20 rounded-xl">
                  <p className="text-xs text-cyan-300"><strong>Insight:</strong> The optimization model analyzes historical workload patterns, inspector availability, and site conditions to maximize inspection coverage while minimizing operational costs.</p>
                </div>
                <ResponsiveContainer width="100%" height={250}>
                  <AreaChart data={resourceOptimization}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="month" stroke="#fff" />
                    <YAxis stroke="#fff" domain={[60, 100]} />
                    <Tooltip contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: '1px solid rgba(255,255,255,0.2)' }} />
                    <Legend />
                    <Area type="monotone" dataKey="current" stroke="#6b7280" fill="#6b7280" fillOpacity={0.3} name="Current Efficiency %" />
                    <Area type="monotone" dataKey="optimized" stroke="#06b6d4" fill="#06b6d4" fillOpacity={0.3} name="ML-Optimized %" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              {/* ML Prediction 7: Deterioration Prediction */}
              <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-2xl">
                <div className="flex items-center gap-3 mb-4">
                  <Eye className="w-6 h-6 text-rose-400" />
                  <div>
                    <h3 className="text-lg font-bold text-white">Heritage Deterioration Forecast</h3>
                    <p className="text-sm text-white/70">Deep learning model predicts structural condition changes using environmental sensors, historical decay rates, and material analysis</p>
                  </div>
                </div>
                <div className="mb-4 p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl">
                  <p className="text-xs text-rose-300"><strong>Critical Alert:</strong> Old Town Facade requires immediate intervention. Model predicts 23-point deterioration within 12 months without proactive maintenance.</p>
                </div>
                <div className="space-y-3">
                  {deteriorationPrediction.map((site, i) => (
                    <div key={i} className="p-4 bg-white/5 rounded-xl border border-white/10">
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-white font-semibold">{site.site}</span>
                        <span className={`text-xs px-2 py-1 rounded-full font-medium ${site.priority === 'Critical' ? 'bg-red-500/30 text-red-300 border border-red-500/50' : site.priority === 'High' ? 'bg-orange-500/30 text-orange-300 border border-orange-500/50' : site.priority === 'Medium' ? 'bg-yellow-500/30 text-yellow-300 border border-yellow-500/50' : 'bg-green-500/30 text-green-300 border border-green-500/50'}`}>
                          {site.priority} Priority
                        </span>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="flex-1">
                          <div className="flex justify-between text-xs text-white/60 mb-1">
                            <span>Current: {site.current}%</span>
                            <span>6 Mo: {site.predicted6Mo}%</span>
                            <span>12 Mo: {site.predicted12Mo}%</span>
                          </div>
                          <div className="h-2 bg-white/10 rounded-full overflow-hidden flex">
                            <div className="h-full bg-green-500" style={{ width: `${site.predicted12Mo}%` }}></div>
                            <div className="h-full bg-yellow-500" style={{ width: `${site.predicted6Mo - site.predicted12Mo}%` }}></div>
                            <div className="h-full bg-red-500" style={{ width: `${site.current - site.predicted6Mo}%` }}></div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* ML Prediction 8: Visitor Impact Analysis */}
              <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-2xl">
                <div className="flex items-center gap-3 mb-4">
                  <Users className="w-6 h-6 text-indigo-400" />
                  <div>
                    <h3 className="text-lg font-bold text-white">Visitor Impact Correlation Model</h3>
                    <p className="text-sm text-white/70">Neural network correlates visitor traffic patterns with site stress indicators to predict preservation risk levels</p>
                  </div>
                </div>
                <div className="mb-4 p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl">
                  <p className="text-xs text-indigo-300"><strong>Peak Season Warning:</strong> November-December visitor surge projected to increase site stress by 150%. Recommend implementing visitor flow controls at Hegra and Old Town.</p>
                </div>
                <ResponsiveContainer width="100%" height={280}>
                  <ComposedChart data={visitorImpactPrediction}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="month" stroke="#fff" />
                    <YAxis yAxisId="left" stroke="#fff" />
                    <YAxis yAxisId="right" orientation="right" stroke="#ef4444" domain={[0, 100]} />
                    <Tooltip contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: '1px solid rgba(255,255,255,0.2)' }} />
                    <Legend />
                    <Bar yAxisId="left" dataKey="visitors" fill="#6366f1" radius={[8, 8, 0, 0]} name="Projected Visitors" />
                    <Line yAxisId="right" type="monotone" dataKey="riskScore" stroke="#ef4444" strokeWidth={3} name="Site Risk Score" />
                  </ComposedChart>
                </ResponsiveContainer>
              </div>

              {/* ML Prediction 9: Predictive Maintenance Scheduler */}
              <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-2xl">
                <div className="flex items-center gap-3 mb-4">
                  <Timer className="w-6 h-6 text-amber-400" />
                  <div>
                    <h3 className="text-lg font-bold text-white">Predictive Maintenance Scheduler</h3>
                    <p className="text-sm text-white/70">AI prioritizes maintenance tasks based on urgency scores, cost-benefit analysis, and operational constraints</p>
                  </div>
                </div>
                <div className="mb-4 p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl">
                  <p className="text-xs text-amber-300"><strong>Budget Optimization:</strong> Prioritizing top 3 tasks within the next 30 days can prevent estimated SAR 180,000 in emergency repair costs.</p>
                </div>
                <div className="space-y-3">
                  {maintenanceSchedulePrediction.map((task, i) => (
                    <div key={i} className="p-4 bg-white/5 rounded-xl border border-white/10">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-white font-semibold">{task.task}</span>
                        <div className="flex items-center gap-3">
                          <span className="text-xs text-white/60">Est. Cost: SAR {task.cost.toLocaleString()}</span>
                          <span className={`text-xs px-2 py-1 rounded ${task.daysUntil <= 21 ? 'bg-red-500/20 text-red-300' : task.daysUntil <= 45 ? 'bg-yellow-500/20 text-yellow-300' : 'bg-green-500/20 text-green-300'}`}>
                            {task.daysUntil} days
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-xs text-white/60">Urgency:</span>
                        <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                          <div 
                            className={`h-full rounded-full ${task.urgency > 80 ? 'bg-red-500' : task.urgency > 60 ? 'bg-orange-500' : task.urgency > 40 ? 'bg-yellow-500' : 'bg-green-500'}`}
                            style={{ width: `${task.urgency}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-bold text-white">{task.urgency}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* ML Prediction 10: Seasonal Pattern Recognition */}
              <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-2xl">
                <div className="flex items-center gap-3 mb-4">
                  <Brain className="w-6 h-6 text-fuchsia-400" />
                  <div>
                    <h3 className="text-lg font-bold text-white">Multi-Factor Seasonal Intelligence</h3>
                    <p className="text-sm text-white/70">Advanced pattern recognition identifies seasonal correlations across 5 key operational dimensions for strategic planning</p>
                  </div>
                </div>
                <div className="mb-4 p-3 bg-fuchsia-500/10 border border-fuchsia-500/20 rounded-xl">
                  <p className="text-xs text-fuchsia-300"><strong>Strategic Insight:</strong> July represents peak operational stress with highest visitor volume, risk levels, and staffing requirements. Plan preventive maintenance in January when operational pressure is lowest.</p>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-4">
                  {seasonalPatterns.map((pattern, i) => (
                    <div key={i} className="p-3 bg-white/5 rounded-xl border border-white/10 text-center">
                      <div className="text-xs text-white/60 mb-1">{pattern.subject}</div>
                      <div className="text-lg font-bold text-white">{Math.max(pattern.Jan, pattern.Apr, pattern.Jul, pattern.Oct)}%</div>
                      <div className="text-xs text-fuchsia-400">Peak Season</div>
                    </div>
                  ))}
                </div>
                <div className="grid grid-cols-4 gap-2 text-center text-xs">
                  <div className="p-2 bg-blue-500/20 rounded-lg text-blue-300">Q1 (Jan-Mar)</div>
                  <div className="p-2 bg-green-500/20 rounded-lg text-green-300">Q2 (Apr-Jun)</div>
                  <div className="p-2 bg-red-500/20 rounded-lg text-red-300">Q3 (Jul-Sep) ⚠️</div>
                  <div className="p-2 bg-yellow-500/20 rounded-lg text-yellow-300">Q4 (Oct-Dec)</div>
                </div>
              </div>
            </>
          ) : (
            <>
              {/* KPI 1: Monthly Inspections */}
              <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-2xl">
                <div className="flex items-center gap-3 mb-4">
                  <Calendar className="w-6 h-6 text-[#104C64]" />
                  <div>
                    <h3 className="text-lg font-bold text-white">Monthly Inspection Volume</h3>
                    <p className="text-sm text-white/70">Tracking inspection volume vs. targets shows 130% achievement rate in Q2 2024</p>
                  </div>
                </div>
                <div className="mb-4 p-3 bg-[#104C64]/20 border border-[#104C64]/30 rounded-xl">
                  <p className="text-xs text-[#7eb8d0]"><strong>Performance Highlight:</strong> Consistent target overachievement since February, with May reaching all-time high of 201 inspections—34% above baseline.</p>
                </div>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={monthlyInspections}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="month" stroke="#fff" />
                    <YAxis stroke="#fff" />
                    <Tooltip contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: '1px solid rgba(255,255,255,0.2)' }} />
                    <Legend />
                    <Bar dataKey="inspections" fill="#104C64" radius={[8, 8, 0, 0]} name="Actual" />
                    <Bar dataKey="target" fill="#D59D80" radius={[8, 8, 0, 0]} name="Target" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* KPI 2: Compliance Rate */}
              <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-2xl">
                <div className="flex items-center gap-3 mb-4">
                  <CheckCircle className="w-6 h-6 text-green-400" />
                  <div>
                    <h3 className="text-lg font-bold text-white">Compliance Rate Trend</h3>
                    <p className="text-sm text-white/70">Heritage site compliance improved by 9 percentage points over 6 months, exceeding regional standards</p>
                  </div>
                </div>
                <div className="mb-4 p-3 bg-green-500/10 border border-green-500/20 rounded-xl">
                  <p className="text-xs text-green-300"><strong>Regulatory Achievement:</strong> June's 96% compliance rate positions AlUla above the 90% threshold required for UNESCO World Heritage status maintenance.</p>
                </div>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={complianceRate}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="month" stroke="#fff" />
                    <YAxis stroke="#fff" domain={[80, 100]} />
                    <Tooltip contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: '1px solid rgba(255,255,255,0.2)' }} />
                    <Line type="monotone" dataKey="rate" stroke="#10b981" strokeWidth={3} />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* KPI 3: Inspector Performance */}
              <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-2xl">
                <div className="flex items-center gap-3 mb-4">
                  <Users className="w-6 h-6 text-blue-400" />
                  <div>
                    <h3 className="text-lg font-bold text-white">Inspector Performance Ranking</h3>
                    <p className="text-sm text-white/70">Top 5 inspectors ranked by volume productivity and compliance quality scores</p>
                  </div>
                </div>
                <div className="mb-4 p-3 bg-blue-500/10 border border-blue-500/20 rounded-xl">
                  <p className="text-xs text-blue-300"><strong>Team Excellence:</strong> Ahmed Al-Rashid leads with 89 inspections at 98% compliance—demonstrating that high volume and quality can coexist with proper training.</p>
                </div>
                <div className="space-y-3">
                  {inspectorPerformance.map((inspector, i) => (
                    <div key={i} className="flex items-center justify-between p-4 bg-white/5 rounded-xl border border-white/10">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#104C64] to-[#0d3d50] flex items-center justify-center text-white font-bold">
                          {i + 1}
                        </div>
                        <span className="text-white font-semibold">{inspector.name}</span>
                      </div>
                      <div className="flex gap-6">
                        <div className="text-right">
                          <div className="text-2xl font-bold text-white">{inspector.inspections}</div>
                          <div className="text-xs text-white/60">Inspections</div>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-green-400">{inspector.compliance}%</div>
                          <div className="text-xs text-white/60">Compliance</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* KPI 4: Location Risk Distribution */}
              <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-2xl">
                <div className="flex items-center gap-3 mb-4">
                  <AlertTriangle className="w-6 h-6 text-orange-400" />
                  <div>
                    <h3 className="text-lg font-bold text-white">Site Risk Classification</h3>
                    <p className="text-sm text-white/70">Distribution of heritage sites by current risk assessment level across the AlUla region</p>
                  </div>
                </div>
                <div className="mb-4 p-3 bg-orange-500/10 border border-orange-500/20 rounded-xl">
                  <p className="text-xs text-orange-300"><strong>Risk Distribution:</strong> 20% of sites classified as high-risk require priority intervention. 45% low-risk sites demonstrate effective preservation protocols.</p>
                </div>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={locationRisk}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {locationRisk.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: '1px solid rgba(255,255,255,0.2)' }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              {/* KPI 5: Issue Categories */}
              <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-2xl">
                <div className="flex items-center gap-3 mb-4">
                  <XCircle className="w-6 h-6 text-red-400" />
                  <div>
                    <h3 className="text-lg font-bold text-white">Issue Category Analysis</h3>
                    <p className="text-sm text-white/70">Breakdown of identified issues by category for targeted resource allocation and remediation planning</p>
                  </div>
                </div>
                <div className="mb-4 p-3 bg-red-500/10 border border-red-500/20 rounded-xl">
                  <p className="text-xs text-red-300"><strong>Priority Focus:</strong> Environmental issues (42) and Maintenance backlogs (34) represent 55% of all findings. Recommend increased environmental monitoring resources.</p>
                </div>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={issueCategories}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="category" stroke="#fff" />
                    <YAxis stroke="#fff" />
                    <Tooltip contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: '1px solid rgba(255,255,255,0.2)' }} />
                    <Bar dataKey="count" fill="#C0754D" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* KPI 6: Weekly Activity Trend */}
              <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-2xl">
                <div className="flex items-center gap-3 mb-4">
                  <Activity className="w-6 h-6 text-purple-400" />
                  <div>
                    <h3 className="text-lg font-bold text-white">Weekly Inspection Activity</h3>
                    <p className="text-sm text-white/70">Last month shows peak activity in Week 4 with 51 inspections completed</p>
                  </div>
                </div>
                <div className="mb-4 p-3 bg-purple-500/10 border border-purple-500/20 rounded-xl">
                  <p className="text-xs text-purple-300"><strong>Trend Analysis:</strong> Weekly volumes show 59% increase from Week 1 to Week 4, indicating accelerating inspection pace as teams optimize workflows.</p>
                </div>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={weeklyTrend}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="week" stroke="#fff" />
                    <YAxis stroke="#fff" />
                    <Tooltip contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: '1px solid rgba(255,255,255,0.2)' }} />
                    <Line type="monotone" dataKey="count" stroke="#8b5cf6" strokeWidth={3} />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* KPI 7: Response Time Metrics */}
              <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-2xl">
                <div className="flex items-center gap-3 mb-4">
                  <Clock className="w-6 h-6 text-cyan-400" />
                  <div>
                    <h3 className="text-lg font-bold text-white">Average Response Time</h3>
                    <p className="text-sm text-white/70">Time from issue identification to inspector dispatch has decreased by 45% over 6 months</p>
                  </div>
                </div>
                <div className="mb-4 p-3 bg-cyan-500/10 border border-cyan-500/20 rounded-xl">
                  <p className="text-xs text-cyan-300"><strong>Performance Milestone:</strong> Response times now exceed target by 34%, enabling faster issue resolution and improved heritage protection outcomes.</p>
                </div>
                <ResponsiveContainer width="100%" height={250}>
                  <AreaChart data={responseTimeData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="month" stroke="#fff" />
                    <YAxis stroke="#fff" domain={[0, 6]} />
                    <Tooltip contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: '1px solid rgba(255,255,255,0.2)' }} formatter={(value: number) => [`${value} hours`, '']} />
                    <Legend />
                    <Area type="monotone" dataKey="target" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.2} strokeDasharray="5 5" name="Target (hours)" />
                    <Area type="monotone" dataKey="avgTime" stroke="#06b6d4" fill="#06b6d4" fillOpacity={0.4} name="Actual (hours)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              {/* KPI 8: Site Condition Scores */}
              <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-2xl">
                <div className="flex items-center gap-3 mb-4">
                  <Shield className="w-6 h-6 text-emerald-400" />
                  <div>
                    <h3 className="text-lg font-bold text-white">Heritage Site Condition Index</h3>
                    <p className="text-sm text-white/70">Comprehensive condition scoring based on structural integrity, environmental factors, and preservation status</p>
                  </div>
                </div>
                <div className="mb-4 p-3 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
                  <p className="text-xs text-emerald-300"><strong>Preservation Status:</strong> 80% of monitored sites maintain condition scores above 85%, meeting UNESCO World Heritage preservation standards.</p>
                </div>
                <div className="space-y-3">
                  {siteConditionScores.map((site, i) => (
                    <div key={i} className="p-4 bg-white/5 rounded-xl border border-white/10">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-3">
                          <MapPin className="w-4 h-4 text-emerald-400" />
                          <span className="text-white font-semibold">{site.site}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className={`text-xs px-2 py-1 rounded ${site.score >= site.lastMonth ? 'bg-green-500/20 text-green-300' : 'bg-red-500/20 text-red-300'}`}>
                            {site.score >= site.lastMonth ? '↑' : '↓'} {Math.abs(site.score - site.lastMonth)}%
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="flex-1 h-3 bg-white/10 rounded-full overflow-hidden">
                          <div 
                            className={`h-full rounded-full ${site.score >= 90 ? 'bg-emerald-500' : site.score >= 80 ? 'bg-green-500' : site.score >= 70 ? 'bg-yellow-500' : 'bg-red-500'}`}
                            style={{ width: `${site.score}%` }}
                          ></div>
                        </div>
                        <span className="text-lg font-bold text-white w-12 text-right">{site.score}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* KPI 9: Budget Utilization */}
              <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-2xl">
                <div className="flex items-center gap-3 mb-4">
                  <Target className="w-6 h-6 text-amber-400" />
                  <div>
                    <h3 className="text-lg font-bold text-white">Budget Utilization Analysis</h3>
                    <p className="text-sm text-white/70">Departmental spending vs. allocated budget with 91.5% overall utilization efficiency</p>
                  </div>
                </div>
                <div className="mb-4 p-3 bg-amber-500/10 border border-amber-500/20 rounded-xl">
                  <p className="text-xs text-amber-300"><strong>Financial Insight:</strong> Technology budget is 98% utilized, suggesting need for increased allocation. Training budget shows 20% underutilization opportunity.</p>
                </div>
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={budgetUtilization} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis type="number" stroke="#fff" tickFormatter={(value) => `${(value / 1000).toFixed(0)}K`} />
                    <YAxis dataKey="category" type="category" stroke="#fff" width={100} />
                    <Tooltip contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: '1px solid rgba(255,255,255,0.2)' }} formatter={(value: number) => [`SAR ${value.toLocaleString()}`, '']} />
                    <Legend />
                    <Bar dataKey="allocated" fill="#f59e0b" radius={[0, 4, 4, 0]} name="Allocated (SAR)" />
                    <Bar dataKey="spent" fill="#10b981" radius={[0, 4, 4, 0]} name="Spent (SAR)" />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              {/* KPI 10: Stakeholder Satisfaction */}
              <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-2xl">
                <div className="flex items-center gap-3 mb-4">
                  <Award className="w-6 h-6 text-rose-400" />
                  <div>
                    <h3 className="text-lg font-bold text-white">Stakeholder Satisfaction Index</h3>
                    <p className="text-sm text-white/70">Quarterly survey results measuring service quality across 6 key performance dimensions</p>
                  </div>
                </div>
                <div className="mb-4 p-3 bg-rose-500/10 border border-rose-500/20 rounded-xl">
                  <p className="text-xs text-rose-300"><strong>Service Excellence:</strong> Technical Expertise rated highest at 4.8/5.0. Issue Resolution at 4.2/5.0 identified as primary improvement opportunity.</p>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                  {stakeholderSatisfaction.map((item, i) => (
                    <div key={i} className="p-4 bg-white/5 rounded-xl border border-white/10 text-center">
                      <div className="text-xs text-white/60 mb-2">{item.category}</div>
                      <div className="text-3xl font-bold text-white mb-1">{item.score}</div>
                      <div className="flex justify-center gap-1">
                        {[1, 2, 3, 4, 5].map((star) => (
                          <div 
                            key={star} 
                            className={`w-3 h-3 rounded-full ${star <= Math.floor(item.score) ? 'bg-amber-400' : star - 0.5 <= item.score ? 'bg-amber-400/50' : 'bg-white/20'}`}
                          ></div>
                        ))}
                      </div>
                      <div className="text-xs text-white/40 mt-1">out of 5.0</div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </motion.div>
  );
}
