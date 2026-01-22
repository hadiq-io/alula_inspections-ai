import { X, TrendingUp, AlertTriangle, Users, Calendar, MapPin, CheckCircle, XCircle, BarChart3, Activity, Zap } from 'lucide-react';
import { motion } from 'framer-motion';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface AnalysisDashboardProps {
  type: 'predictions' | 'kpis' | null;
  onClose: () => void;
}

export default function AnalysisDashboard({ type, onClose }: AnalysisDashboardProps) {
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

  return (
    <motion.div
      initial={{ x: '100%', opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: '100%', opacity: 0 }}
      transition={{ type: 'spring', damping: 30, stiffness: 300 }}
      className="h-full backdrop-blur-2xl bg-black/30 border-l border-white/20 flex flex-col"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-5 bg-white/5 border-b border-white/20">
        <div className="flex items-center gap-3">
          {type === 'predictions' ? (
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#C0754D] to-[#B6410F] flex items-center justify-center shadow-lg">
              <Zap className="w-5 h-5 text-white" strokeWidth={2.5} />
            </div>
          ) : (
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#104C64] to-[#0d3d50] flex items-center justify-center shadow-lg">
              <BarChart3 className="w-5 h-5 text-white" strokeWidth={2.5} />
            </div>
          )}
          <h2 className="text-2xl font-bold text-white">
            {type === 'predictions' ? 'ML Predictions Analysis' : 'KPIs Dashboard'}
          </h2>
        </div>
        <button
          onClick={onClose}
          className="p-2 hover:bg-white/10 rounded-lg transition-colors"
        >
          <X className="w-5 h-5 text-white/70 hover:text-white" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto custom-scrollbar p-6">
        <div className="space-y-6">
          {type === 'predictions' ? (
            <>
              {/* ML Prediction 1: Volume Forecast */}
              <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-2xl">
                <div className="flex items-center gap-3 mb-4">
                  <TrendingUp className="w-6 h-6 text-[#C0754D]" />
                  <div>
                    <h3 className="text-lg font-bold text-white">Inspection Volume Forecast</h3>
                    <p className="text-sm text-white/70">AI predicts 15% increase in next 6 months based on seasonal patterns and historical data</p>
                  </div>
                </div>
                <ResponsiveContainer width="100%" height={250}>
                  <LineChart data={volumeForecast}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="month" stroke="#fff" />
                    <YAxis stroke="#fff" />
                    <Tooltip contentStyle={{ backgroundColor: 'rgba(0,0,0,0.8)', border: '1px solid rgba(255,255,255,0.2)' }} />
                    <Legend />
                    <Line type="monotone" dataKey="actual" stroke="#10b981" strokeWidth={3} name="Actual" />
                    <Line type="monotone" dataKey="predicted" stroke="#f59e0b" strokeWidth={3} strokeDasharray="5 5" name="Predicted" />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {/* ML Prediction 2: Compliance Forecast */}
              <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-2xl">
                <div className="flex items-center gap-3 mb-4">
                  <CheckCircle className="w-6 h-6 text-green-400" />
                  <div>
                    <h3 className="text-lg font-bold text-white">Compliance Rate Forecast</h3>
                    <p className="text-sm text-white/70">ML model predicts sustained 97%+ compliance through Q4 2024</p>
                  </div>
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
                    <h3 className="text-lg font-bold text-white">Location Risk Prediction</h3>
                    <p className="text-sm text-white/70">Deep learning identifies emerging risk patterns across heritage sites</p>
                  </div>
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
                    <h3 className="text-lg font-bold text-white">Anomaly Detection</h3>
                    <p className="text-sm text-white/70">Real-time ML monitoring detects unusual patterns requiring attention</p>
                  </div>
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
                    <h3 className="text-lg font-bold text-white">ML Model Performance</h3>
                    <p className="text-sm text-white/70">All models exceed 89% accuracy threshold with continuous learning</p>
                  </div>
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
            </>
          ) : (
            <>
              {/* KPI 1: Monthly Inspections */}
              <div className="bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-6 shadow-2xl">
                <div className="flex items-center gap-3 mb-4">
                  <Calendar className="w-6 h-6 text-[#104C64]" />
                  <div>
                    <h3 className="text-lg font-bold text-white">Monthly Inspection Trends</h3>
                    <p className="text-sm text-white/70">Tracking inspection volume vs. targets shows 130% achievement rate in Q2 2024</p>
                  </div>
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
                    <h3 className="text-lg font-bold text-white">Compliance Rate Analysis</h3>
                    <p className="text-sm text-white/70">Heritage site compliance improved by 9% over 6 months, exceeding regional standards</p>
                  </div>
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
                    <h3 className="text-lg font-bold text-white">Inspector Performance Metrics</h3>
                    <p className="text-sm text-white/70">Top 5 inspectors ranked by volume and compliance quality scores</p>
                  </div>
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
                    <h3 className="text-lg font-bold text-white">Location Risk Distribution</h3>
                    <p className="text-sm text-white/70">20% of sites require immediate attention, 45% are low-risk and well-maintained</p>
                  </div>
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
                    <h3 className="text-lg font-bold text-white">Issue Categories Breakdown</h3>
                    <p className="text-sm text-white/70">Environmental concerns account for 31% of all issues, followed by structural at 20%</p>
                  </div>
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
            </>
          )}
        </div>
      </div>
    </motion.div>
  );
}
