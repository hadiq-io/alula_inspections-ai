"use client";

import { useState, useEffect, createContext, useContext } from "react";
import { motion } from "framer-motion";

// Language context for the entire app
interface LanguageContextType {
  language: "en" | "ar";
  setLanguage: (lang: "en" | "ar") => void;
  isRTL: boolean;
  t: (key: string) => string;
}

const translations: Record<string, Record<string, string>> = {
  // Header
  "app.title": {
    en: "AlUla Inspection AI",
    ar: "الذكاء الاصطناعي لتفتيش العُلا",
  },
  "app.subtitle": {
    en: "Ask Your Data",
    ar: "اسأل بياناتك",
  },
  
  // Chat
  "chat.placeholder": {
    en: "Ask a question about inspections, violations, or performance...",
    ar: "اسأل سؤالاً عن الفحوصات أو المخالفات أو الأداء...",
  },
  "chat.send": {
    en: "Send",
    ar: "إرسال",
  },
  "chat.thinking": {
    en: "Analyzing your question...",
    ar: "جاري تحليل سؤالك...",
  },
  "chat.error": {
    en: "An error occurred. Please try again.",
    ar: "حدث خطأ. يرجى المحاولة مرة أخرى.",
  },
  "chat.welcome": {
    en: "Hello! I can help you analyze inspection data for AlUla. Ask me about violations, inspector performance, neighborhood compliance, or forecasts.",
    ar: "مرحباً! يمكنني مساعدتك في تحليل بيانات التفتيش في العُلا. اسألني عن المخالفات أو أداء المفتشين أو امتثال الأحياء أو التوقعات.",
  },
  
  // Sidebar
  "sidebar.dashboard": {
    en: "Dashboard",
    ar: "لوحة التحكم",
  },
  "sidebar.chat": {
    en: "Chat",
    ar: "المحادثة",
  },
  "sidebar.analytics": {
    en: "Analytics",
    ar: "التحليلات",
  },
  "sidebar.settings": {
    en: "Settings",
    ar: "الإعدادات",
  },
  
  // KPIs
  "kpi.inspections": {
    en: "Total Inspections",
    ar: "إجمالي الفحوصات",
  },
  "kpi.violations": {
    en: "Total Violations",
    ar: "إجمالي المخالفات",
  },
  "kpi.compliance": {
    en: "Compliance Rate",
    ar: "معدل الامتثال",
  },
  "kpi.inspectors": {
    en: "Active Inspectors",
    ar: "المفتشين النشطين",
  },
  
  // Chart labels
  "chart.noData": {
    en: "No data available",
    ar: "لا توجد بيانات",
  },
  "chart.loading": {
    en: "Loading chart...",
    ar: "جاري تحميل الرسم البياني...",
  },
  
  // Time periods
  "time.today": {
    en: "Today",
    ar: "اليوم",
  },
  "time.week": {
    en: "This Week",
    ar: "هذا الأسبوع",
  },
  "time.month": {
    en: "This Month",
    ar: "هذا الشهر",
  },
  "time.year": {
    en: "This Year",
    ar: "هذا العام",
  },
  
  // Sample questions
  "sample.q1": {
    en: "How many violations were there in 2024?",
    ar: "كم عدد المخالفات في 2024؟",
  },
  "sample.q2": {
    en: "Which neighborhood has the best compliance?",
    ar: "أي حي لديه أفضل امتثال؟",
  },
  "sample.q3": {
    en: "Show me monthly inspection trends",
    ar: "أظهر لي اتجاهات الفحوصات الشهرية",
  },
  "sample.q4": {
    en: "Who are the top performing inspectors?",
    ar: "من هم أفضل المفتشين أداءً؟",
  },
};

const LanguageContext = createContext<LanguageContextType>({
  language: "en",
  setLanguage: () => {},
  isRTL: false,
  t: () => "",
});

export const useLanguage = () => useContext(LanguageContext);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const [language, setLanguage] = useState<"en" | "ar">("en");
  const isRTL = language === "ar";

  // Update document direction when language changes
  useEffect(() => {
    document.documentElement.dir = isRTL ? "rtl" : "ltr";
    document.documentElement.lang = language;
    
    // Add or remove RTL class
    if (isRTL) {
      document.body.classList.add("rtl");
    } else {
      document.body.classList.remove("rtl");
    }
  }, [isRTL, language]);

  const t = (key: string): string => {
    const translation = translations[key];
    if (!translation) {
      console.warn(`Translation missing for key: ${key}`);
      return key;
    }
    return translation[language] || translation["en"] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, isRTL, t }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function LanguageToggle() {
  const { language, setLanguage, isRTL } = useLanguage();

  return (
    <motion.button
      onClick={() => setLanguage(language === "en" ? "ar" : "en")}
      className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      title={language === "en" ? "Switch to Arabic" : "التبديل إلى الإنجليزية"}
    >
      {/* Globe icon */}
      <svg
        className="w-5 h-5 text-gray-600 dark:text-gray-300"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"
        />
      </svg>
      
      {/* Language indicator */}
      <span className="font-medium text-sm text-gray-700 dark:text-gray-200">
        {language === "en" ? "EN" : "AR"}
      </span>
      
      {/* Animated indicator */}
      <motion.div
        className="relative w-10 h-5 bg-gray-300 dark:bg-gray-600 rounded-full"
        style={{ direction: "ltr" }}
      >
        <motion.div
          className="absolute top-0.5 w-4 h-4 bg-white rounded-full shadow"
          animate={{ x: language === "en" ? 2 : 22 }}
          transition={{ type: "spring", stiffness: 500, damping: 30 }}
        />
        <span
          className={`absolute text-[8px] font-bold top-0.5 ${
            language === "en" ? "right-1 text-gray-500" : "left-1 text-gray-500"
          }`}
        >
          {language === "en" ? "ع" : "E"}
        </span>
      </motion.div>
    </motion.button>
  );
}

export default LanguageToggle;
