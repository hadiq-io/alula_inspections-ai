'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Lock, ShieldCheck, AlertCircle } from 'lucide-react';

interface PinLoginProps {
  onSuccess: () => void;
}

const CORRECT_PIN = '1990';
const INACTIVITY_TIMEOUT = 10 * 60 * 1000; // 10 minutes in milliseconds

export default function PinLogin({ onSuccess }: PinLoginProps) {
  const [pin, setPin] = useState(['', '', '', '']);
  const [error, setError] = useState(false);
  const [shake, setShake] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);
  const inputRefs = [
    useRef<HTMLInputElement>(null),
    useRef<HTMLInputElement>(null),
    useRef<HTMLInputElement>(null),
    useRef<HTMLInputElement>(null),
  ];

  // Focus first input on mount
  useEffect(() => {
    inputRefs[0].current?.focus();
  }, []);

  const handleInputChange = (index: number, value: string) => {
    // Only allow digits
    if (value && !/^\d$/.test(value)) return;

    const newPin = [...pin];
    newPin[index] = value;
    setPin(newPin);
    setError(false);

    // Auto-focus next input
    if (value && index < 3) {
      inputRefs[index + 1].current?.focus();
    }

    // Check PIN when all digits entered
    if (value && index === 3) {
      const fullPin = newPin.join('');
      verifyPin(fullPin);
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent) => {
    // Handle backspace
    if (e.key === 'Backspace' && !pin[index] && index > 0) {
      inputRefs[index - 1].current?.focus();
    }
    
    // Handle paste
    if (e.key === 'v' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      navigator.clipboard.readText().then(text => {
        const digits = text.replace(/\D/g, '').slice(0, 4).split('');
        const newPin = ['', '', '', ''];
        digits.forEach((digit, i) => {
          newPin[i] = digit;
        });
        setPin(newPin);
        if (digits.length === 4) {
          verifyPin(digits.join(''));
        } else if (digits.length > 0) {
          inputRefs[Math.min(digits.length, 3)].current?.focus();
        }
      });
    }
  };

  const verifyPin = (enteredPin: string) => {
    setIsVerifying(true);
    
    // Small delay for UX
    setTimeout(() => {
      if (enteredPin === CORRECT_PIN) {
        onSuccess();
      } else {
        setError(true);
        setShake(true);
        setPin(['', '', '', '']);
        setTimeout(() => {
          setShake(false);
          inputRefs[0].current?.focus();
        }, 500);
      }
      setIsVerifying(false);
    }, 300);
  };

  const handleNumpadClick = (digit: string) => {
    const emptyIndex = pin.findIndex(p => p === '');
    if (emptyIndex !== -1) {
      handleInputChange(emptyIndex, digit);
    }
  };

  const handleClear = () => {
    setPin(['', '', '', '']);
    setError(false);
    inputRefs[0].current?.focus();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Background */}
      <div 
        className="absolute inset-0 bg-cover bg-center"
        style={{ 
          backgroundImage: "url('/alula-bg.jpg')",
          filter: 'brightness(0.3) blur(8px)'
        }}
      />
      <div className="absolute inset-0 bg-gradient-to-br from-black/80 via-black/60 to-transparent" />

      {/* Login Card */}
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className={`relative z-10 w-full max-w-sm mx-4 ${shake ? 'animate-shake' : ''}`}
      >
        <div className="backdrop-blur-2xl bg-white/10 border border-white/20 rounded-3xl p-8 shadow-2xl">
          {/* Logo */}
          <div className="flex flex-col items-center mb-8">
            <img 
              src="/alula-logo.png" 
              alt="AlUla Logo" 
              className="h-16 w-auto brightness-0 invert mb-4"
            />
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center mb-4 shadow-lg">
              <Lock className="w-7 h-7 text-white" />
            </div>
            <h2 className="text-xl font-bold text-white mb-1">Secure Access</h2>
            <p className="text-white/60 text-sm text-center">Enter your 4-digit PIN to continue</p>
          </div>

          {/* PIN Input */}
          <div className="flex justify-center gap-3 mb-6">
            {pin.map((digit, index) => (
              <motion.div
                key={index}
                animate={error ? { x: [0, -5, 5, -5, 5, 0] } : {}}
                transition={{ duration: 0.4 }}
              >
                <input
                  ref={inputRefs[index]}
                  type="password"
                  inputMode="numeric"
                  maxLength={1}
                  value={digit}
                  onChange={(e) => handleInputChange(index, e.target.value)}
                  onKeyDown={(e) => handleKeyDown(index, e)}
                  className={`w-14 h-16 text-center text-2xl font-bold rounded-xl border-2 bg-white/5 backdrop-blur-lg outline-none transition-all ${
                    error 
                      ? 'border-red-500 text-red-400' 
                      : digit 
                        ? 'border-amber-500 text-white' 
                        : 'border-white/20 text-white focus:border-amber-500/50'
                  }`}
                  disabled={isVerifying}
                />
              </motion.div>
            ))}
          </div>

          {/* Error Message */}
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="flex items-center justify-center gap-2 text-red-400 text-sm mb-4"
              >
                <AlertCircle className="w-4 h-4" />
                <span>Incorrect PIN. Please try again.</span>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Numpad for mobile */}
          <div className="grid grid-cols-3 gap-2 mb-6">
            {['1', '2', '3', '4', '5', '6', '7', '8', '9', '', '0', 'clear'].map((key, index) => (
              <button
                key={index}
                onClick={() => key === 'clear' ? handleClear() : key && handleNumpadClick(key)}
                disabled={!key || isVerifying}
                className={`h-12 rounded-xl font-semibold transition-all ${
                  key === 'clear'
                    ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30 text-sm'
                    : key
                      ? 'bg-white/10 text-white hover:bg-white/20 text-lg'
                      : 'invisible'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {key === 'clear' ? 'Clear' : key}
              </button>
            ))}
          </div>

          {/* Security Note */}
          <div className="flex items-center justify-center gap-2 text-white/40 text-xs">
            <ShieldCheck className="w-4 h-4" />
            <span>Session expires after 10 minutes of inactivity</span>
          </div>
        </div>
      </motion.div>

      {/* CSS for shake animation */}
      <style jsx global>{`
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
          20%, 40%, 60%, 80% { transform: translateX(5px); }
        }
        .animate-shake {
          animation: shake 0.5s ease-in-out;
        }
      `}</style>
    </div>
  );
}

// Hook to manage authentication state with inactivity timeout
export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  const resetTimeout = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    if (isAuthenticated) {
      timeoutRef.current = setTimeout(() => {
        setIsAuthenticated(false);
        sessionStorage.removeItem('alula_auth');
        sessionStorage.removeItem('alula_last_activity');
      }, INACTIVITY_TIMEOUT);
    }
  }, [isAuthenticated]);

  // Check stored auth on mount
  useEffect(() => {
    const storedAuth = sessionStorage.getItem('alula_auth');
    const lastActivity = sessionStorage.getItem('alula_last_activity');
    
    if (storedAuth === 'true' && lastActivity) {
      const elapsed = Date.now() - parseInt(lastActivity, 10);
      if (elapsed < INACTIVITY_TIMEOUT) {
        setIsAuthenticated(true);
      } else {
        sessionStorage.removeItem('alula_auth');
        sessionStorage.removeItem('alula_last_activity');
      }
    }
    setIsLoading(false);
  }, []);

  // Set up activity listeners
  useEffect(() => {
    if (!isAuthenticated) return;

    const updateActivity = () => {
      sessionStorage.setItem('alula_last_activity', Date.now().toString());
      resetTimeout();
    };

    // Track user activity
    const events = ['mousedown', 'mousemove', 'keydown', 'scroll', 'touchstart', 'click'];
    events.forEach(event => {
      window.addEventListener(event, updateActivity, { passive: true });
    });

    // Initial timeout setup
    resetTimeout();

    return () => {
      events.forEach(event => {
        window.removeEventListener(event, updateActivity);
      });
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [isAuthenticated, resetTimeout]);

  const login = useCallback(() => {
    setIsAuthenticated(true);
    sessionStorage.setItem('alula_auth', 'true');
    sessionStorage.setItem('alula_last_activity', Date.now().toString());
  }, []);

  const logout = useCallback(() => {
    setIsAuthenticated(false);
    sessionStorage.removeItem('alula_auth');
    sessionStorage.removeItem('alula_last_activity');
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
  }, []);

  return { isAuthenticated, isLoading, login, logout };
}
