const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  chart_data?: any;
  chart_type?: string;
  tiles?: any[];
  type?: string;
  chartData?: Record<string, any>[];
  chartConfig?: {
    type: 'bar' | 'line' | 'pie' | 'composed' | 'area' | 'none';
    xKey?: string;
    yKeys?: string[];
    title?: string;
    title_ar?: string;
  };
}

export interface ChatResponse {
  message?: string;
  chart_data?: any;
  chart_type?: string;
  tiles?: any[];
  type?: string;
  success: boolean;
  error?: string;
}

// V2 API Types for bilingual support
export interface V2ChatRequest {
  message: string;
  session_id?: string;
  language: 'en' | 'ar';
}

export interface V2ChatResponse {
  response: string;
  response_ar?: string;
  data?: Record<string, any>[];
  chart_config?: {
    type: 'bar' | 'line' | 'pie' | 'composed' | 'area' | 'none';
    xKey?: string;
    yKeys?: string[];
    title?: string;
    title_ar?: string;
  };
  template_id?: string;
  session_id: string;
  intent?: string;
  entities?: Record<string, any>;
  error?: string;
}

export const api = {
  async sendMessage(message: string): Promise<ChatResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  // V2 API for bilingual chat with charts
  async sendMessageV2(request: V2ChatRequest): Promise<V2ChatResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v2/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API V2 Error:', error);
      throw error;
    }
  },

  async clearChat(): Promise<void> {
    try {
      await fetch(`${API_BASE_URL}/api/clear`, {
        method: 'POST',
      });
    } catch (error) {
      console.error('Clear chat error:', error);
    }
  },

  async clearSession(sessionId: string): Promise<void> {
    try {
      await fetch(`${API_BASE_URL}/api/v2/session/${sessionId}`, {
        method: 'DELETE',
      });
    } catch (error) {
      console.error('Clear session error:', error);
    }
  },

  async healthCheck(): Promise<{ status: string; database: string }> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/health`);
      return response.json();
    } catch (error) {
      console.error('Health check error:', error);
      throw error;
    }
  },

  async healthCheckV2(): Promise<Record<string, any>> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v2/health`);
      return response.json();
    } catch (error) {
      console.error('V2 Health check error:', error);
      throw error;
    }
  },
};
