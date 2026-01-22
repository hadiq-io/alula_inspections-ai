"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Loader2, BarChart3, TrendingUp, MapPin, Users, X } from "lucide-react";
import ChatMessage from "./ChatMessage";
import AnalysisDashboard from "./AnalysisDashboard";

export default function ChatInterface() {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [activePanel, setActivePanel] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const quickPrompts = [
    { icon: BarChart3, text: "Show me all KPIs", prompt: "Show me all KPIs" },
    { icon: TrendingUp, text: "ML Models", prompt: "Show me all ML models" },
    { icon: MapPin, text: "Location Analysis", prompt: "Show me location risk analysis" },
    { icon: Users, text: "Inspector Stats", prompt: "Show me inspector performance" },
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (messageText?: string) => {
    const msg = messageText || input;
    if (!msg.trim()) return;

    setMessages((prev) => [...prev, { role: "user", content: msg }]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await fetch("http://localhost:8000/api/chat", {
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
    } catch (error) {
      console.error("Chat error:", error);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, I encountered an error." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleTileClick = (tileId: string) => {
    setActivePanel(tileId);
  };

  const handleClear = async () => {
    await fetch("http://localhost:8000/api/clear", { method: "POST" });
    setMessages([]);
  };

  return (
    <div className="relative flex h-screen overflow-hidden">
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
        animate={{ width: activePanel ? '60%' : '100%' }} 
        transition={{ type: 'spring', damping: 30, stiffness: 300 }} 
        className="relative flex flex-col z-10"
      >
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="w-full max-w-4xl h-[85vh] backdrop-blur-2xl bg-white/10 border border-white/20 rounded-3xl shadow-2xl flex flex-col overflow-hidden">
            
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
              <div className="flex items-center gap-3">
                {/* AlUla Logo */}
                <img 
                  src="/alula-logo.png" 
                  alt="AlUla Logo" 
                  className="h-10 w-auto"
                />
                <div className="h-8 w-px bg-white/20" />
                <h1 className="text-xl font-bold text-white">Inspection Intelligence</h1>
              </div>
              {messages.length > 0 && (
                <button 
                  onClick={handleClear}
                  className="text-white/60 hover:text-white transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              )}
            </div>

            {/* Messages */}
            <main className="flex-1 overflow-y-auto custom-scrollbar px-6 py-4">
              <AnimatePresence mode="popLayout">
                {messages.length === 0 ? (
                  <motion.div 
                    initial={{ opacity: 0 }} 
                    animate={{ opacity: 1 }} 
                    exit={{ opacity: 0 }} 
                    className="flex flex-col items-center justify-center h-full space-y-8"
                  >
                    {/* Welcome Message */}
                    <div className="text-center space-y-4">
                      <motion.div
                        initial={{ scale: 0.8, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        transition={{ delay: 0.1 }}
                      >
                        <BarChart3 className="w-16 h-16 text-amber-400 mx-auto mb-4" strokeWidth={1.5} />
                      </motion.div>
                      
                      <motion.h2
                        initial={{ y: 20, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        transition={{ delay: 0.2 }}
                        className="text-3xl font-bold text-white"
                      >
                        Welcome to AlUla Intelligence Hub
                      </motion.h2>
                      
                      <motion.p
                        initial={{ y: 20, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        transition={{ delay: 0.3 }}
                        className="text-white/70 max-w-md mx-auto"
                      >
                        AI-powered insights for heritage site inspections and compliance monitoring
                      </motion.p>
                    </div>

                    {/* Quick Action Cards */}
                    <motion.div 
                      initial={{ y: 20, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                      transition={{ delay: 0.4 }}
                      className="grid grid-cols-2 gap-4 w-full max-w-2xl"
                    >
                      {quickPrompts.map((item, idx) => (
                        <motion.button
                          key={idx}
                          whileHover={{ scale: 1.02, y: -2 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => handleSend(item.prompt)}
                          className="group relative overflow-hidden bg-white/5 backdrop-blur-lg border border-white/10 rounded-2xl p-6 hover:bg-white/10 hover:border-white/20 transition-all duration-300"
                        >
                          <div className="absolute inset-0 bg-gradient-to-br from-amber-500/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                          <div className="relative flex items-center gap-4">
                            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-amber-500/20 to-orange-600/20 flex items-center justify-center group-hover:from-amber-500/30 group-hover:to-orange-600/30 transition-all">
                              <item.icon className="w-6 h-6 text-amber-400" strokeWidth={2} />
                            </div>
                            <span className="text-white font-medium text-left">{item.text}</span>
                          </div>
                        </motion.button>
                      ))}
                    </motion.div>

                    {/* Suggested Prompts */}
                    <motion.div
                      initial={{ y: 20, opacity: 0 }}
                      animate={{ y: 0, opacity: 1 }}
                      transition={{ delay: 0.5 }}
                      className="text-center"
                    >
                      <p className="text-white/50 text-sm mb-3">or try asking:</p>
                      <div className="flex flex-wrap gap-2 justify-center max-w-xl">
                        {[
                          "What is the compliance rate?",
                          "Show me repeat violations",
                          "Inspector performance stats"
                        ].map((prompt, idx) => (
                          <button
                            key={idx}
                            onClick={() => setInput(prompt)}
                            className="px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-full text-white/70 hover:text-white text-sm transition-all"
                          >
                            {prompt}
                          </button>
                        ))}
                      </div>
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
                          tiles={msg.tiles}
                          type={msg.type}
                          onTileClick={handleTileClick}
                        />
                      </motion.div>
                    ))}
                    {isLoading && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex gap-3 items-start"
                      >
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center shadow-lg">
                          <Loader2 className="w-5 h-5 text-white animate-spin" />
                        </div>
                        <div className="flex-1 bg-white/10 backdrop-blur-lg border border-white/20 rounded-2xl p-4">
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

            {/* Input Area */}
            <div className="p-6 border-t border-white/10">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSend();
                }}
                className="flex gap-3"
              >
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Ask about inspections, violations, compliance..."
                  className="flex-1 bg-white/10 backdrop-blur-lg border border-white/20 rounded-xl px-5 py-3 text-white placeholder-white/40 focus:outline-none focus:border-amber-500/50 focus:ring-2 focus:ring-amber-500/20 transition-all"
                  disabled={isLoading}
                />
                <button
                  type="submit"
                  disabled={!input.trim() || isLoading}
                  className="bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700 disabled:from-gray-500 disabled:to-gray-600 disabled:cursor-not-allowed text-white px-6 py-3 rounded-xl font-medium transition-all shadow-lg hover:shadow-xl disabled:shadow-none"
                >
                  <Send className="w-5 h-5" />
                </button>
              </form>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Right Panel - Analysis Dashboard */}
      <AnimatePresence>
        {activePanel && (
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 30, stiffness: 300 }}
            className="relative w-[40%] z-20"
          >
            <AnalysisDashboard 
              selectedKpi={activePanel} 
              onClose={() => setActivePanel(null)} 
            />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
