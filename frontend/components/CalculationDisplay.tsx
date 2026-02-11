'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Calculator, 
  ChevronDown, 
  ChevronUp, 
  Info,
  Equal,
  Divide,
  X,
  Plus,
  Minus
} from 'lucide-react';

interface CalculationStep {
  id: string;
  label: string;
  label_ar?: string;
  value: number | string;
  unit?: string;
  operation?: 'add' | 'subtract' | 'multiply' | 'divide' | 'equals' | 'none';
  description?: string;
  description_ar?: string;
  isHighlighted?: boolean;
  subSteps?: CalculationStep[];
}

interface CalculationDisplayProps {
  title: string;
  title_ar?: string;
  result: number | string;
  result_label?: string;
  result_label_ar?: string;
  unit?: string;
  steps: CalculationStep[];
  formula?: string;
  formula_ar?: string;
  isRTL?: boolean;
  className?: string;
  defaultExpanded?: boolean;
}

// Operation icons
const getOperationIcon = (operation?: string) => {
  switch (operation) {
    case 'add':
      return <Plus className="w-3 h-3 text-emerald-400" />;
    case 'subtract':
      return <Minus className="w-3 h-3 text-red-400" />;
    case 'multiply':
      return <X className="w-3 h-3 text-amber-400" />;
    case 'divide':
      return <Divide className="w-3 h-3 text-blue-400" />;
    case 'equals':
      return <Equal className="w-3 h-3 text-purple-400" />;
    default:
      return null;
  }
};

// Format numbers with locale
const formatNumber = (value: number | string, locale: string = 'en-US'): string => {
  if (typeof value === 'string') return value;
  return new Intl.NumberFormat(locale, {
    maximumFractionDigits: 2,
    minimumFractionDigits: 0
  }).format(value);
};

export default function CalculationDisplay({
  title,
  title_ar,
  result,
  result_label,
  result_label_ar,
  unit = '',
  steps,
  formula,
  formula_ar,
  isRTL = false,
  className = '',
  defaultExpanded = false
}: CalculationDisplayProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);
  const [showFormula, setShowFormula] = useState(false);
  
  const locale = isRTL ? 'ar-SA' : 'en-US';
  const displayTitle = isRTL && title_ar ? title_ar : title;
  const displayFormula = isRTL && formula_ar ? formula_ar : formula;
  const displayResultLabel = isRTL && result_label_ar ? result_label_ar : result_label;

  return (
    <div className={`bg-white/5 border border-white/10 rounded-xl overflow-hidden ${className}`}>
      {/* Header */}
      <div 
        className={`flex items-center justify-between p-4 cursor-pointer hover:bg-white/5 transition-colors ${isRTL ? 'flex-row-reverse' : ''}`}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
          <div className="p-2 bg-gradient-to-br from-purple-500/20 to-blue-500/20 rounded-lg">
            <Calculator className="w-4 h-4 text-purple-400" />
          </div>
          <div className={isRTL ? 'text-right' : 'text-left'}>
            <h3 className="text-sm font-medium text-white">{displayTitle}</h3>
            {displayResultLabel && (
              <p className="text-xs text-white/50">{displayResultLabel}</p>
            )}
          </div>
        </div>
        
        <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
          {/* Result badge */}
          <div className="px-3 py-1.5 bg-gradient-to-r from-emerald-500/20 to-teal-500/20 border border-emerald-500/30 rounded-lg">
            <span className="text-lg font-bold text-emerald-300">
              {formatNumber(result, locale)}
              {unit && <span className="text-xs ml-1 text-emerald-400/70">{unit}</span>}
            </span>
          </div>
          
          {/* Expand/collapse */}
          <motion.div
            animate={{ rotate: isExpanded ? 180 : 0 }}
            transition={{ duration: 0.2 }}
          >
            <ChevronDown className="w-5 h-5 text-white/40" />
          </motion.div>
        </div>
      </div>

      {/* Expanded content */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <div className="px-4 pb-4 space-y-4">
              {/* Formula (if provided) */}
              {formula && (
                <div 
                  className={`p-3 bg-white/5 rounded-lg border border-white/10 ${isRTL ? 'text-right' : 'text-left'}`}
                  onMouseEnter={() => setShowFormula(true)}
                  onMouseLeave={() => setShowFormula(false)}
                >
                  <div className={`flex items-center gap-2 text-xs text-white/50 mb-1 ${isRTL ? 'flex-row-reverse' : ''}`}>
                    <Info className="w-3 h-3" />
                    <span>{isRTL ? 'الصيغة' : 'Formula'}</span>
                  </div>
                  <code className="text-sm text-blue-300 font-mono">
                    {displayFormula}
                  </code>
                </div>
              )}

              {/* Calculation steps */}
              <div className="space-y-2">
                {steps.map((step, index) => (
                  <CalculationStepRow 
                    key={step.id} 
                    step={step} 
                    index={index}
                    isRTL={isRTL}
                    locale={locale}
                    isLast={index === steps.length - 1}
                  />
                ))}
              </div>

              {/* Final result line */}
              <div className={`flex items-center gap-2 pt-2 border-t border-white/10 ${isRTL ? 'flex-row-reverse' : ''}`}>
                <Equal className="w-4 h-4 text-purple-400" />
                <span className="text-sm font-medium text-white">
                  {isRTL ? 'النتيجة النهائية' : 'Final Result'}:
                </span>
                <span className="text-lg font-bold text-emerald-300 ml-auto">
                  {formatNumber(result, locale)}
                  {unit && <span className="text-xs ml-1 text-emerald-400/70">{unit}</span>}
                </span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// Individual step row component
function CalculationStepRow({ 
  step, 
  index, 
  isRTL, 
  locale,
  isLast 
}: { 
  step: CalculationStep; 
  index: number;
  isRTL: boolean;
  locale: string;
  isLast: boolean;
}) {
  const [showSubSteps, setShowSubSteps] = useState(false);
  const displayLabel = isRTL && step.label_ar ? step.label_ar : step.label;
  const displayDescription = isRTL && step.description_ar ? step.description_ar : step.description;

  return (
    <div className="space-y-1">
      <motion.div
        initial={{ opacity: 0, x: isRTL ? 20 : -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: index * 0.05 }}
        className={`
          flex items-center gap-3 p-2 rounded-lg
          ${step.isHighlighted ? 'bg-amber-500/10 border border-amber-500/20' : 'bg-white/[0.02]'}
          ${isRTL ? 'flex-row-reverse' : ''}
        `}
      >
        {/* Operation icon */}
        <div className="w-5 flex justify-center">
          {getOperationIcon(step.operation)}
        </div>
        
        {/* Label */}
        <div className={`flex-1 ${isRTL ? 'text-right' : 'text-left'}`}>
          <span className={`text-sm ${step.isHighlighted ? 'text-amber-300 font-medium' : 'text-white/70'}`}>
            {displayLabel}
          </span>
          {displayDescription && (
            <p className="text-xs text-white/40 mt-0.5">{displayDescription}</p>
          )}
        </div>
        
        {/* Value */}
        <div className={`flex items-center gap-1 ${isRTL ? 'flex-row-reverse' : ''}`}>
          <span className={`text-sm font-mono ${step.isHighlighted ? 'text-amber-300 font-bold' : 'text-white/80'}`}>
            {formatNumber(step.value, locale)}
          </span>
          {step.unit && (
            <span className="text-xs text-white/40">{step.unit}</span>
          )}
        </div>
        
        {/* Expand sub-steps button */}
        {step.subSteps && step.subSteps.length > 0 && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              setShowSubSteps(!showSubSteps);
            }}
            className="p-1 hover:bg-white/10 rounded transition-colors"
          >
            {showSubSteps ? (
              <ChevronUp className="w-3 h-3 text-white/40" />
            ) : (
              <ChevronDown className="w-3 h-3 text-white/40" />
            )}
          </button>
        )}
      </motion.div>
      
      {/* Sub-steps */}
      <AnimatePresence>
        {showSubSteps && step.subSteps && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className={`pl-8 space-y-1 ${isRTL ? 'pr-8 pl-0' : ''}`}
          >
            {step.subSteps.map((subStep, subIndex) => (
              <div 
                key={subStep.id}
                className={`flex items-center gap-2 p-1.5 rounded bg-white/[0.02] text-xs ${isRTL ? 'flex-row-reverse' : ''}`}
              >
                <span className="text-white/50">{isRTL && subStep.label_ar ? subStep.label_ar : subStep.label}</span>
                <span className="text-white/70 font-mono ml-auto">
                  {formatNumber(subStep.value, locale)}
                  {subStep.unit && <span className="text-white/40 ml-1">{subStep.unit}</span>}
                </span>
              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

// Example usage component for documentation
export function CalculationDisplayExample() {
  const exampleSteps: CalculationStep[] = [
    {
      id: 'total_inspections',
      label: 'Total Inspections',
      label_ar: 'إجمالي الفحوصات',
      value: 1500,
      operation: 'none',
      description: 'All inspections in the period'
    },
    {
      id: 'compliant_inspections',
      label: 'Compliant Inspections',
      label_ar: 'الفحوصات الممتثلة',
      value: 1245,
      operation: 'none',
      description: 'Inspections with score >= 80',
      subSteps: [
        { id: 'high_score', label: 'Score 90-100', value: 650 },
        { id: 'medium_score', label: 'Score 80-89', value: 595 }
      ]
    },
    {
      id: 'division',
      label: 'Divide compliant by total',
      label_ar: 'قسمة الممتثلة على الإجمالي',
      value: '1245 ÷ 1500',
      operation: 'divide',
      isHighlighted: true
    },
    {
      id: 'multiply',
      label: 'Multiply by 100',
      label_ar: 'الضرب في 100',
      value: '0.83 × 100',
      operation: 'multiply'
    },
    {
      id: 'result',
      label: 'Compliance Rate',
      label_ar: 'معدل الامتثال',
      value: 83,
      unit: '%',
      operation: 'equals',
      isHighlighted: true
    }
  ];

  return (
    <CalculationDisplay
      title="Compliance Rate Calculation"
      title_ar="حساب معدل الامتثال"
      result={83}
      result_label="Overall Compliance Rate"
      result_label_ar="معدل الامتثال الإجمالي"
      unit="%"
      steps={exampleSteps}
      formula="(Compliant Inspections / Total Inspections) × 100"
      formula_ar="(الفحوصات الممتثلة ÷ إجمالي الفحوصات) × 100"
      defaultExpanded={true}
    />
  );
}
