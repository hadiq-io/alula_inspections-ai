'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ThumbsUp, ThumbsDown, Send, Loader2, MessageSquare } from 'lucide-react';

interface FeedbackButtonsProps {
  messageId: string;
  isRTL?: boolean;
  onFeedbackSubmitted?: (status: 'correct' | 'incorrect' | 'clarified') => void;
  onClarificationRetry?: (retryResponse: any) => void;
}

// Bilingual labels
const LABELS = {
  correct: { en: 'Helpful', ar: 'مفيد' },
  incorrect: { en: 'Not helpful', ar: 'غير مفيد' },
  clarifyPlaceholder: { 
    en: 'Please describe what you expected...', 
    ar: 'يرجى وصف ما كنت تتوقعه...' 
  },
  submit: { en: 'Submit', ar: 'إرسال' },
  sending: { en: 'Sending...', ar: 'جاري الإرسال...' },
  thanksCorrect: {
    en: 'Thank you! This query has been saved for future use.',
    ar: 'شكراً! تم حفظ هذا الاستعلام للاستخدام المستقبلي.'
  },
  thanksClarify: {
    en: 'Thank you for the clarification!',
    ar: 'شكراً للتوضيح!'
  },
  wasThisHelpful: {
    en: 'Was this response helpful?',
    ar: 'هل كانت هذه الإجابة مفيدة؟'
  }
};

// API Base URL - uses environment variable or empty string for same-origin (nginx proxy)
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

export default function FeedbackButtons({ 
  messageId, 
  isRTL = false,
  onFeedbackSubmitted,
  onClarificationRetry
}: FeedbackButtonsProps) {
  const [status, setStatus] = useState<'idle' | 'correct' | 'incorrect' | 'clarifying' | 'submitted' | 'error'>('idle');
  const [clarification, setClarification] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [feedbackMessage, setFeedbackMessage] = useState('');
  
  const lang = isRTL ? 'ar' : 'en';

  const handleCorrect = async () => {
    setIsSubmitting(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v2/feedback/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message_id: messageId, is_correct: true }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        setStatus('correct');
        setFeedbackMessage(isRTL ? data.message_ar : data.message_en);
        onFeedbackSubmitted?.('correct');
      } else {
        setStatus('error');
        setFeedbackMessage(data.error || 'Failed to record feedback');
      }
    } catch (error) {
      console.error('Feedback error:', error);
      setStatus('error');
      setFeedbackMessage('Network error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleIncorrect = async () => {
    setIsSubmitting(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v2/feedback/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message_id: messageId, is_correct: false }),
      });
      
      const data = await response.json();
      
      if (data.success && data.needs_clarification) {
        setStatus('clarifying');
      } else if (data.success) {
        setStatus('incorrect');
        onFeedbackSubmitted?.('incorrect');
      } else {
        setStatus('error');
        setFeedbackMessage(data.error || 'Failed to record feedback');
      }
    } catch (error) {
      console.error('Feedback error:', error);
      setStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSubmitClarification = async () => {
    if (!clarification.trim()) return;
    
    setIsSubmitting(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/v2/feedback/clarify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message_id: messageId, 
          clarification: clarification.trim(),
          language: lang
        }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        setStatus('submitted');
        setFeedbackMessage(isRTL ? data.message_ar : data.message_en);
        onFeedbackSubmitted?.('clarified');
        
        // If there's a retry response, pass it up
        if (data.retry_response) {
          onClarificationRetry?.(data.retry_response);
        }
      } else {
        setStatus('error');
        setFeedbackMessage(data.error || 'Failed to submit clarification');
      }
    } catch (error) {
      console.error('Clarification error:', error);
      setStatus('error');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Already submitted or no messageId
  if (!messageId || status === 'correct' || status === 'submitted') {
    if (feedbackMessage) {
      return (
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className={`mt-3 flex items-center gap-2 text-sm text-emerald-400 ${isRTL ? 'flex-row-reverse' : ''}`}
        >
          <ThumbsUp className="w-4 h-4" />
          <span>{feedbackMessage}</span>
        </motion.div>
      );
    }
    return null;
  }

  // Error state
  if (status === 'error') {
    return (
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="mt-3 text-sm text-red-400"
      >
        {feedbackMessage || 'An error occurred'}
      </motion.div>
    );
  }

  // Clarification input state
  if (status === 'clarifying') {
    return (
      <motion.div
        initial={{ opacity: 0, height: 0 }}
        animate={{ opacity: 1, height: 'auto' }}
        exit={{ opacity: 0, height: 0 }}
        className="mt-4 space-y-3"
      >
        <div className="flex items-center gap-2 text-amber-400 text-sm">
          <MessageSquare className="w-4 h-4" />
          <span>{LABELS.clarifyPlaceholder[lang]}</span>
        </div>
        
        <div className={`flex gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
          <textarea
            value={clarification}
            onChange={(e) => setClarification(e.target.value)}
            placeholder={LABELS.clarifyPlaceholder[lang]}
            className={`flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white placeholder-white/40 focus:outline-none focus:border-amber-500/50 resize-none ${isRTL ? 'text-right' : 'text-left'}`}
            rows={2}
            dir={isRTL ? 'rtl' : 'ltr'}
          />
          
          <button
            onClick={handleSubmitClarification}
            disabled={!clarification.trim() || isSubmitting}
            className="px-4 py-2 bg-gradient-to-r from-amber-500 to-orange-600 rounded-lg text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:from-amber-600 hover:to-orange-700 transition-all flex items-center gap-2"
          >
            {isSubmitting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="hidden sm:inline">{LABELS.sending[lang]}</span>
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span className="hidden sm:inline">{LABELS.submit[lang]}</span>
              </>
            )}
          </button>
        </div>
      </motion.div>
    );
  }

  // Default: Show feedback buttons
  return (
    <motion.div 
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
      className={`mt-4 pt-3 border-t border-white/10 ${isRTL ? 'text-right' : 'text-left'}`}
    >
      <div className={`flex items-center gap-3 ${isRTL ? 'flex-row-reverse' : ''}`}>
        <span className="text-xs text-white/40">{LABELS.wasThisHelpful[lang]}</span>
        
        <div className={`flex gap-2 ${isRTL ? 'flex-row-reverse' : ''}`}>
          {/* Correct Button */}
          <button
            onClick={handleCorrect}
            disabled={isSubmitting}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-medium hover:bg-emerald-500/20 hover:border-emerald-500/50 transition-all disabled:opacity-50"
          >
            {isSubmitting ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <ThumbsUp className="w-3.5 h-3.5" />
            )}
            <span>{LABELS.correct[lang]}</span>
          </button>
          
          {/* Incorrect Button */}
          <button
            onClick={handleIncorrect}
            disabled={isSubmitting}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-medium hover:bg-red-500/20 hover:border-red-500/50 transition-all disabled:opacity-50"
          >
            {isSubmitting ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <ThumbsDown className="w-3.5 h-3.5" />
            )}
            <span>{LABELS.incorrect[lang]}</span>
          </button>
        </div>
      </div>
    </motion.div>
  );
}
