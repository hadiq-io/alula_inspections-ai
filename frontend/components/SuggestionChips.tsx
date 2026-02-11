'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, 
  TrendingUp, 
  BarChart2, 
  Calendar, 
  MapPin, 
  Users, 
  AlertTriangle,
  Clock,
  ChevronRight,
  RefreshCw
} from 'lucide-react';

interface Suggestion {
  id: string;
  text: string;
  text_ar?: string;
  category: 'kpi' | 'analytics' | 'prediction' | 'comparison' | 'entity' | 'temporal';
  icon?: string;
  context?: Record<string, string>;
}

interface SuggestionChipsProps {
  onSuggestionClick: (suggestion: string) => void;
  isRTL?: boolean;
  context?: {
    lastQuery?: string;
    lastEntity?: string;
    lastTimeframe?: string;
    conversationHistory?: string[];
  };
  maxSuggestions?: number;
  className?: string;
}

// Default suggestions organized by category
const DEFAULT_SUGGESTIONS: Suggestion[] = [
  // KPI Suggestions
  {
    id: 'kpi_compliance',
    text: 'What is the overall compliance rate?',
    text_ar: 'ما هو معدل الامتثال الإجمالي؟',
    category: 'kpi',
    icon: 'chart'
  },
  {
    id: 'kpi_violations',
    text: 'Show me the top 10 violations',
    text_ar: 'أظهر لي أعلى 10 مخالفات',
    category: 'kpi',
    icon: 'alert'
  },
  {
    id: 'kpi_inspections',
    text: 'How many inspections this month?',
    text_ar: 'كم عدد الفحوصات هذا الشهر؟',
    category: 'kpi',
    icon: 'calendar'
  },
  
  // Analytics Suggestions
  {
    id: 'analytics_trend',
    text: 'Show me the inspection trend over time',
    text_ar: 'أظهر لي اتجاه الفحوصات مع الوقت',
    category: 'analytics',
    icon: 'trending'
  },
  {
    id: 'analytics_distribution',
    text: 'What is the distribution of violations by type?',
    text_ar: 'ما هو توزيع المخالفات حسب النوع؟',
    category: 'analytics',
    icon: 'bar'
  },
  {
    id: 'analytics_ranking',
    text: 'Rank locations by compliance score',
    text_ar: 'رتب المواقع حسب نقاط الامتثال',
    category: 'analytics',
    icon: 'ranking'
  },
  
  // Prediction Suggestions
  {
    id: 'prediction_forecast',
    text: 'Predict violations for next month',
    text_ar: 'توقع المخالفات للشهر القادم',
    category: 'prediction',
    icon: 'sparkle'
  },
  {
    id: 'prediction_risk',
    text: 'Which locations are high risk?',
    text_ar: 'أي المواقع عالية المخاطر؟',
    category: 'prediction',
    icon: 'alert'
  },
  
  // Comparison Suggestions
  {
    id: 'comparison_yoy',
    text: 'Compare this year vs last year',
    text_ar: 'قارن هذا العام بالعام الماضي',
    category: 'comparison',
    icon: 'compare'
  },
  {
    id: 'comparison_neighborhoods',
    text: 'Compare neighborhoods by performance',
    text_ar: 'قارن الأحياء حسب الأداء',
    category: 'comparison',
    icon: 'map'
  },
  
  // Entity Suggestions
  {
    id: 'entity_inspector',
    text: 'Show top performing inspectors',
    text_ar: 'أظهر أفضل المفتشين أداءً',
    category: 'entity',
    icon: 'users'
  },
  {
    id: 'entity_location',
    text: 'Which locations need attention?',
    text_ar: 'أي المواقع تحتاج اهتماماً؟',
    category: 'entity',
    icon: 'map'
  },
  
  // Temporal Suggestions
  {
    id: 'temporal_weekly',
    text: 'Show weekly inspection summary',
    text_ar: 'أظهر ملخص الفحوصات الأسبوعي',
    category: 'temporal',
    icon: 'calendar'
  },
  {
    id: 'temporal_monthly',
    text: 'Monthly performance breakdown',
    text_ar: 'تفصيل الأداء الشهري',
    category: 'temporal',
    icon: 'clock'
  }
];

// Context-aware follow-up suggestions
const FOLLOWUP_SUGGESTIONS: Record<string, Suggestion[]> = {
  compliance: [
    {
      id: 'followup_compliance_breakdown',
      text: 'Break it down by neighborhood',
      text_ar: 'قسمها حسب الحي',
      category: 'analytics',
      icon: 'bar'
    },
    {
      id: 'followup_compliance_trend',
      text: 'How has it changed over time?',
      text_ar: 'كيف تغيرت مع الوقت؟',
      category: 'temporal',
      icon: 'trending'
    },
    {
      id: 'followup_compliance_compare',
      text: 'Compare with last year',
      text_ar: 'قارن بالعام الماضي',
      category: 'comparison',
      icon: 'compare'
    }
  ],
  violations: [
    {
      id: 'followup_violations_top',
      text: 'Which locations have the most?',
      text_ar: 'أي المواقع لديها أكثر؟',
      category: 'entity',
      icon: 'map'
    },
    {
      id: 'followup_violations_types',
      text: 'Break down by violation type',
      text_ar: 'قسمها حسب نوع المخالفة',
      category: 'analytics',
      icon: 'bar'
    },
    {
      id: 'followup_violations_trend',
      text: 'Show trend over time',
      text_ar: 'أظهر الاتجاه مع الوقت',
      category: 'temporal',
      icon: 'trending'
    }
  ],
  inspections: [
    {
      id: 'followup_inspections_inspector',
      text: 'Who did the most inspections?',
      text_ar: 'من أجرى أكثر فحوصات؟',
      category: 'entity',
      icon: 'users'
    },
    {
      id: 'followup_inspections_location',
      text: 'By location',
      text_ar: 'حسب الموقع',
      category: 'entity',
      icon: 'map'
    },
    {
      id: 'followup_inspections_daily',
      text: 'Daily breakdown',
      text_ar: 'التفصيل اليومي',
      category: 'temporal',
      icon: 'calendar'
    }
  ],
  location: [
    {
      id: 'followup_location_violations',
      text: 'What violations occurred there?',
      text_ar: 'ما المخالفات التي حدثت هناك؟',
      category: 'analytics',
      icon: 'alert'
    },
    {
      id: 'followup_location_history',
      text: 'Show inspection history',
      text_ar: 'أظهر سجل الفحوصات',
      category: 'temporal',
      icon: 'clock'
    },
    {
      id: 'followup_location_compare',
      text: 'Compare with similar locations',
      text_ar: 'قارن بمواقع مماثلة',
      category: 'comparison',
      icon: 'compare'
    }
  ],
  inspector: [
    {
      id: 'followup_inspector_performance',
      text: 'Show their performance trend',
      text_ar: 'أظهر اتجاه أدائهم',
      category: 'temporal',
      icon: 'trending'
    },
    {
      id: 'followup_inspector_locations',
      text: 'Which locations did they inspect?',
      text_ar: 'أي المواقع فحصوها؟',
      category: 'entity',
      icon: 'map'
    },
    {
      id: 'followup_inspector_compare',
      text: 'Compare with other inspectors',
      text_ar: 'قارن مع مفتشين آخرين',
      category: 'comparison',
      icon: 'users'
    }
  ]
};

// Icon mapping
const getIcon = (iconType: string) => {
  switch (iconType) {
    case 'sparkle':
      return <Sparkles className="w-3.5 h-3.5" />;
    case 'trending':
      return <TrendingUp className="w-3.5 h-3.5" />;
    case 'bar':
    case 'chart':
      return <BarChart2 className="w-3.5 h-3.5" />;
    case 'calendar':
      return <Calendar className="w-3.5 h-3.5" />;
    case 'map':
      return <MapPin className="w-3.5 h-3.5" />;
    case 'users':
      return <Users className="w-3.5 h-3.5" />;
    case 'alert':
      return <AlertTriangle className="w-3.5 h-3.5" />;
    case 'clock':
      return <Clock className="w-3.5 h-3.5" />;
    default:
      return <ChevronRight className="w-3.5 h-3.5" />;
  }
};

// Category colors
const getCategoryColor = (category: string) => {
  switch (category) {
    case 'kpi':
      return 'from-blue-500/20 to-blue-600/10 border-blue-500/30 text-blue-300 hover:border-blue-400/50';
    case 'analytics':
      return 'from-emerald-500/20 to-emerald-600/10 border-emerald-500/30 text-emerald-300 hover:border-emerald-400/50';
    case 'prediction':
      return 'from-purple-500/20 to-purple-600/10 border-purple-500/30 text-purple-300 hover:border-purple-400/50';
    case 'comparison':
      return 'from-amber-500/20 to-amber-600/10 border-amber-500/30 text-amber-300 hover:border-amber-400/50';
    case 'entity':
      return 'from-cyan-500/20 to-cyan-600/10 border-cyan-500/30 text-cyan-300 hover:border-cyan-400/50';
    case 'temporal':
      return 'from-rose-500/20 to-rose-600/10 border-rose-500/30 text-rose-300 hover:border-rose-400/50';
    default:
      return 'from-gray-500/20 to-gray-600/10 border-gray-500/30 text-gray-300 hover:border-gray-400/50';
  }
};

export default function SuggestionChips({
  onSuggestionClick,
  isRTL = false,
  context,
  maxSuggestions = 4,
  className = ''
}: SuggestionChipsProps) {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Determine suggestions based on context
  useEffect(() => {
    let contextualSuggestions: Suggestion[] = [];

    if (context?.lastQuery) {
      const lastQueryLower = context.lastQuery.toLowerCase();
      
      // Find matching follow-up suggestions
      for (const [keyword, followups] of Object.entries(FOLLOWUP_SUGGESTIONS)) {
        if (lastQueryLower.includes(keyword)) {
          contextualSuggestions = [...contextualSuggestions, ...followups];
        }
      }
    }

    // If no contextual suggestions, use defaults
    if (contextualSuggestions.length === 0) {
      // Randomly select from defaults, ensuring variety
      const categories = ['kpi', 'analytics', 'prediction', 'comparison', 'entity', 'temporal'];
      const selectedCategories = categories.sort(() => Math.random() - 0.5).slice(0, maxSuggestions);
      
      contextualSuggestions = selectedCategories.map(cat => {
        const categoryItems = DEFAULT_SUGGESTIONS.filter(s => s.category === cat);
        return categoryItems[Math.floor(Math.random() * categoryItems.length)];
      }).filter(Boolean);
    }

    // Limit and set suggestions
    setSuggestions(contextualSuggestions.slice(0, maxSuggestions));
  }, [context, maxSuggestions]);

  const handleRefresh = () => {
    setIsRefreshing(true);
    
    // Shuffle and pick new suggestions
    const shuffled = [...DEFAULT_SUGGESTIONS].sort(() => Math.random() - 0.5);
    const newSuggestions = shuffled.slice(0, maxSuggestions);
    
    setTimeout(() => {
      setSuggestions(newSuggestions);
      setIsRefreshing(false);
    }, 300);
  };

  const handleChipClick = (suggestion: Suggestion) => {
    const text = isRTL && suggestion.text_ar ? suggestion.text_ar : suggestion.text;
    onSuggestionClick(text);
  };

  if (suggestions.length === 0) return null;

  return (
    <div className={`${className}`}>
      <div className={`flex items-center gap-2 mb-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
        <Sparkles className="w-3.5 h-3.5 text-amber-400" />
        <span className="text-xs text-white/40">
          {isRTL ? 'اقتراحات' : 'Suggestions'}
        </span>
        <button
          onClick={handleRefresh}
          className="ml-auto p-1 rounded hover:bg-white/5 transition-colors"
          title={isRTL ? 'تحديث الاقتراحات' : 'Refresh suggestions'}
        >
          <RefreshCw className={`w-3 h-3 text-white/30 ${isRefreshing ? 'animate-spin' : ''}`} />
        </button>
      </div>
      
      <div className={`flex flex-wrap gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
        <AnimatePresence mode="popLayout">
          {suggestions.map((suggestion, index) => (
            <motion.button
              key={suggestion.id}
              initial={{ opacity: 0, scale: 0.9, y: 10 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9 }}
              transition={{ delay: index * 0.05 }}
              onClick={() => handleChipClick(suggestion)}
              className={`
                flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium
                bg-gradient-to-r border backdrop-blur-sm
                transition-all duration-200 hover:scale-105 active:scale-95
                ${getCategoryColor(suggestion.category)}
                ${isRTL ? 'flex-row-reverse' : ''}
              `}
            >
              {suggestion.icon && getIcon(suggestion.icon)}
              <span>{isRTL && suggestion.text_ar ? suggestion.text_ar : suggestion.text}</span>
            </motion.button>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}
