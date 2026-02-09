"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";

// API Base URL - uses environment variable or relative path for same-origin
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';
import { Send, Loader2, BarChart3, TrendingUp, Brain, Zap, RotateCcw, Globe, FileText, MapPin, Users, AlertTriangle, Calendar, PieChart, Target, Shield, Activity } from "lucide-react";
import ChatMessage from "./ChatMessage";
import { LanguageToggle, LanguageProvider, useLanguage } from "./LanguageToggle";

// Message interface with chart support
interface Recommendation {
  text: string;
  text_en: string;
  text_ar: string;
  icon: string;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  content_en?: string;  // Store English version
  content_ar?: string;  // Store Arabic version
  tiles?: any[];
  type?: string;
  chartData?: Record<string, any>[];
  chartConfig?: {
    type: "bar" | "line" | "pie" | "composed" | "area" | "none";
    xKey?: string;
    yKeys?: string[];
    title?: string;
    title_ar?: string;
  };
  recommendations?: Recommendation[];
}

function ChatInterfaceInner() {
  const { language, isRTL, t } = useLanguage();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [useV2Api, setUseV2Api] = useState(true); // Toggle between V1 and V2 API
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom function
  const scrollToBottom = useCallback(() => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
    }
  }, []);

  // Scroll on new messages
  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Handle content update during typewriter effect
  const handleContentUpdate = useCallback(() => {
    scrollToBottom();
  }, [scrollToBottom]);

  const handleSend = async (messageText?: string) => {
    const msg = messageText || input;
    if (!msg.trim()) return;

    setMessages((prev) => [...prev, { role: "user", content: msg }]);
    setInput("");
    setIsLoading(true);

    try {
      // Use V2 API for bilingual support with charts
      if (useV2Api) {
        const res = await fetch(`${API_BASE_URL}/api/v2/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ 
            message: msg,
            session_id: sessionId,
            language: language
          }),
        });

        const data = await res.json();
        
        // Store session ID for follow-up context
        if (data.session_id) {
          setSessionId(data.session_id);
        }

        // Get the appropriate response based on language
        const responseText = language === "ar" && data.response_ar 
          ? data.response_ar 
          : data.response;

        setMessages((prev) => [
          ...prev,
          { 
            role: "assistant", 
            content: responseText || "I couldn't generate a response.",
            content_en: data.response_en || data.response || "",
            content_ar: data.response_ar || "",
            chartData: data.data,
            chartConfig: data.chart_config,
            recommendations: data.recommendations
          },
        ]);
      } else {
        // Fallback to V1 API
        const res = await fetch(`${API_BASE_URL}/api/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: msg }),
        });

        const data = await res.json();

        if (data.type === "kpi_tiles" || data.type === "prediction_tiles") {
          setMessages((prev) => [
            ...prev,
            { role: "assistant", content: "", tiles: data.tiles, type: data.type },
          ]);
        } else {
          setMessages((prev) => [
            ...prev,
            { role: "assistant", content: data.message },
          ]);
        }
      }
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [
        ...prev,
        { 
          role: "assistant", 
          content: language === "ar" 
            ? "عذراً، حدث خطأ. يرجى المحاولة مرة أخرى." 
            : "Sorry, I encountered an error. Please try again."
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTileClick = (tileId: string) => {
    // Tiles are hidden in simplified UI
    console.log('Tile clicked:', tileId);
  };

  const handleClear = async () => {
    await fetch(`${API_BASE_URL}/api/clear`, { method: "POST" });
    // Also clear V2 session
    if (sessionId) {
      await fetch(`${API_BASE_URL}/api/v2/session/${sessionId}`, { method: "DELETE" });
      setSessionId(null);
    }
    setMessages([]);
  };

  return (
    <div className="relative flex h-[100dvh] overflow-hidden">
      {/* Background with AlUla image */}
      <div 
        className="absolute inset-0 bg-cover bg-center z-0"
        style={{ 
          backgroundImage: "url('/alula-bg.jpg')",
          filter: "brightness(0.4)"
        }}
      />
      
      {/* Gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-black/70 via-black/50 to-transparent z-0" />

      {/* Main Chat Container */}
      <motion.div 
        className="relative flex flex-col z-10 h-full w-full"
      >
        <div className="flex-1 flex items-center justify-center p-2 sm:p-4 md:p-8 transition-all duration-300">
          <div className="w-full max-w-4xl h-[98dvh] sm:h-[95vh] backdrop-blur-2xl bg-white/10 border border-white/20 rounded-2xl sm:rounded-3xl shadow-2xl flex flex-col overflow-hidden transition-all duration-300">
            
            {/* Header - Mobile Optimized */}
            <div className="flex items-center justify-between px-3 sm:px-6 py-3 sm:py-4 border-b border-white/10">
              <div className="flex items-center gap-2 sm:gap-3 min-w-0 flex-1">
                {/* AlUla Logo - Responsive Size */}
                <img 
                  src="/alula-logo.png" 
                  alt="AlUla Logo" 
                  className="h-8 sm:h-12 md:h-14 w-auto brightness-0 invert transition-all duration-300 flex-shrink-0"
                />
                <div className="h-6 sm:h-10 w-px bg-white/30 transition-all duration-300 hidden sm:block" />
                <div className="flex flex-col min-w-0">
                  <h1 className="text-sm sm:text-lg md:text-xl font-bold text-white transition-all duration-300 truncate">
                    {isRTL ? "الذكاء الاصطناعي للتفتيش" : "Inspection AI"}
                  </h1>
                  <p className="text-white/50 text-[10px] sm:text-xs hidden sm:block truncate">
                    {isRTL 
                      ? "مراقبة المواقع التراثية"
                      : "Heritage Site Analytics"
                    }
                  </p>
                </div>
              </div>
              
              <div className="flex items-center gap-1 sm:gap-3 flex-shrink-0">
                {/* Language Toggle */}
                <LanguageToggle />
                
                {/* Clear Button */}
                {messages.length > 0 && (
                  <button 
                    onClick={handleClear}
                    className="flex items-center gap-1 sm:gap-2 text-white/60 hover:text-white transition-colors px-2 sm:px-3 py-1.5 rounded-lg hover:bg-white/10"
                    title={isRTL ? "مسح المحادثة" : "Clear conversation"}
                  >
                    <RotateCcw className="w-4 h-4" />
                    <span className="text-xs sm:text-sm hidden sm:inline">{isRTL ? "مسح" : "Clear"}</span>
                  </button>
                )}
              </div>
            </div>

            {/* Messages */}
            <main ref={messagesContainerRef} className="flex-1 overflow-y-auto custom-scrollbar px-2 sm:px-4 py-3 sm:py-4">
              <AnimatePresence mode="popLayout">
                {messages.length === 0 ? (
                  <motion.div 
                    initial={{ opacity: 0 }} 
                    animate={{ opacity: 1 }} 
                    exit={{ opacity: 0 }} 
                    className="flex flex-col items-center justify-center h-full"
                  >
                    {/* Welcome Message - Mobile Optimized */}
                    <motion.div
                      initial={{ y: -20, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                      transition={{ delay: 0.1 }}
                      className="text-center mb-4 sm:mb-8 px-2"
                    >
                      <h2 className="text-lg sm:text-2xl font-bold text-white mb-1 sm:mb-2">
                        {isRTL ? "مرحباً بك في مساعد العُلا الذكي" : "Welcome to AlUla Intelligence"}
                      </h2>
                      <p className="text-white/60 text-xs sm:text-sm max-w-lg">
                        {isRTL 
                          ? "اسألني أي شيء عن الفحوصات والمخالفات"
                          : "Ask me anything about inspections & violations"
                        }
                      </p>
                    </motion.div>

                    {/* Suggested Questions Grid - Mobile: 1 col, Tablet: 2 cols */}
                    <motion.div
                      initial={{ y: 20, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                      transition={{ delay: 0.3 }}
                      className="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-3 w-full max-w-3xl px-2"
                    >
                      {(isRTL ? [
                        { icon: PieChart, text: "ما هو معدل الامتثال الحالي؟", color: "from-emerald-500 to-teal-600" },
                        { icon: AlertTriangle, text: "أظهر لي المخالفات المتكررة", color: "from-red-500 to-rose-600" },
                        { icon: Users, text: "من هم أفضل المفتشين أداءً؟", color: "from-blue-500 to-indigo-600" },
                        { icon: MapPin, text: "المخالفات حسب الحي", color: "from-amber-500 to-orange-600" },
                        { icon: TrendingUp, text: "اتجاهات الفحوصات الشهرية", color: "from-purple-500 to-violet-600" },
                        { icon: Target, text: "المواقع عالية المخاطر", color: "from-pink-500 to-rose-600" },
                        { icon: Calendar, text: "إحصائيات هذا الشهر", color: "from-cyan-500 to-blue-600" },
                        { icon: BarChart3, text: "مقارنة بين الأحياء", color: "from-lime-500 to-green-600" },
                        { icon: Shield, text: "حالة الامتثال العامة", color: "from-indigo-500 to-purple-600" },
                        { icon: Activity, text: "تقرير النشاط اليومي", color: "from-orange-500 to-red-600" }
                      ] : [
                        { icon: PieChart, text: "What is the current compliance rate?", color: "from-emerald-500 to-teal-600" },
                        { icon: AlertTriangle, text: "Show me repeat violations", color: "from-red-500 to-rose-600" },
                        { icon: Users, text: "Who are the top performing inspectors?", color: "from-blue-500 to-indigo-600" },
                        { icon: MapPin, text: "Violations by neighborhood", color: "from-amber-500 to-orange-600" },
                        { icon: TrendingUp, text: "Monthly inspection trends", color: "from-purple-500 to-violet-600" },
                        { icon: Target, text: "High-risk locations", color: "from-pink-500 to-rose-600" },
                        { icon: Calendar, text: "This month's statistics", color: "from-cyan-500 to-blue-600" },
                        { icon: BarChart3, text: "Neighborhood comparison", color: "from-lime-500 to-green-600" },
                        { icon: Shield, text: "Overall compliance status", color: "from-indigo-500 to-purple-600" },
                        { icon: Activity, text: "Daily activity report", color: "from-orange-500 to-red-600" }
                      ]).map((item, idx) => {
                        const IconComponent = item.icon;
                        return (
                          <motion.button
                            key={idx}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.4 + idx * 0.05 }}
                            whileHover={{ scale: 1.02, y: -2 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => handleSend(item.text)}
                            className="group flex items-center gap-2 sm:gap-3 p-3 sm:p-4 bg-white/5 hover:bg-white/10 backdrop-blur-lg border border-white/10 hover:border-white/30 rounded-xl sm:rounded-2xl text-left transition-all duration-300"
                            dir={isRTL ? "rtl" : "ltr"}
                          >
                            <div className={`w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-gradient-to-br ${item.color} flex items-center justify-center shadow-lg group-hover:shadow-xl transition-shadow flex-shrink-0`}>
                              <IconComponent className="w-4 h-4 sm:w-5 sm:h-5 text-white" strokeWidth={2} />
                            </div>
                            <span className="text-white/80 group-hover:text-white text-xs sm:text-sm font-medium transition-colors line-clamp-2">
                              {item.text}
                            </span>
                          </motion.button>
                        );
                      })}
                    </motion.div>
                  </motion.div>
                ) : (
                  <div className="space-y-4">
                    {messages.map((msg, idx) => (
                      <motion.div
                        key={idx}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.3 }}
                      >
                        <ChatMessage
                          role={msg.role}
                          content={msg.content}
                          content_en={msg.content_en}
                          content_ar={msg.content_ar}
                          tiles={msg.tiles}
                          type={msg.type}
                          onTileClick={handleTileClick}
                          onContentUpdate={handleContentUpdate}
                          isCompact={false}
                          chartData={msg.chartData}
                          chartConfig={msg.chartConfig}
                          isRTL={isRTL}
                          recommendations={msg.recommendations}
                          onRecommendationClick={(text) => handleSend(text)}
                        />
                      </motion.div>
                    ))}
                    {isLoading && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex gap-3 items-start"
                      >
                        <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shadow-lg flex-shrink-0">
                          <Loader2 className="w-4 h-4 sm:w-5 sm:h-5 text-white animate-spin" />
                        </div>
                        <div className="flex-1 bg-white/10 backdrop-blur-lg border border-white/20 rounded-xl sm:rounded-2xl p-3 sm:p-4">
                          <div className="flex gap-1">
                            {[0, 1, 2].map((i) => (
                              <motion.div
                                key={i}
                                animate={{ y: [0, -8, 0] }}
                                transition={{
                                  repeat: Infinity,
                                  duration: 0.6,
                                  delay: i * 0.15,
                                }}
                                className="w-2 h-2 bg-gradient-to-r from-amber-500 to-orange-600 rounded-full"
                              />
                            ))}
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </div>
                )}
              </AnimatePresence>
              <div ref={messagesEndRef} />
            </main>

            {/* Input Area - Mobile Optimized */}
            <div className="p-3 sm:p-6 border-t border-white/10 transition-all duration-300 safe-area-bottom">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSend();
                }}
                className="flex gap-2"
              >
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={isRTL 
                    ? "اسأل عن الفحوصات..."
                    : "Ask about inspections..."
                  }
                  className="flex-1 bg-white/10 backdrop-blur-lg border border-white/20 rounded-xl px-3 sm:px-5 py-2.5 sm:py-3 text-sm sm:text-base text-white placeholder-white/40 focus:outline-none focus:border-amber-500/50 focus:ring-2 focus:ring-amber-500/20 transition-all"
                  disabled={isLoading}
                  dir={isRTL ? "rtl" : "ltr"}
                />
                <button
                  type="submit"
                  disabled={!input.trim() || isLoading}
                  className="bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700 disabled:from-gray-500 disabled:to-gray-600 disabled:cursor-not-allowed text-white px-4 sm:px-6 py-2.5 sm:py-3 rounded-xl font-medium transition-all shadow-lg hover:shadow-xl disabled:shadow-none"
                >
                  <Send className="w-4 h-4 sm:w-5 sm:h-5" />
                </button>
              </form>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

// Wrap in LanguageProvider for bilingual support
export default function ChatInterface() {
  return (
    <LanguageProvider>
      <ChatInterfaceInner />
    </LanguageProvider>
  );
}
