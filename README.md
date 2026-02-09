# AlUla Inspection AI

An AI-powered heritage site inspection and compliance analytics platform for AlUla, Saudi Arabia (a UNESCO World Heritage Site).

---

## 📋 Project Overview

AlUla Inspection AI is a full-stack application that combines real-time inspection data with machine learning predictions to help inspection teams, managers, and analysts understand inspection data, identify risks, and improve compliance at heritage sites.

### Key Features

- **AI-Powered Chat Interface** - Natural language queries about inspection data using Claude AI
- **10 KPI Dashboards** - Real-time key performance indicators with interactive visualizations
- **9 ML Prediction Models** - Forecasting, risk assessment, anomaly detection, and more
- **Real-time Database Integration** - Live connection to SQL Server inspection database

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Next.js)                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  ChatInterface  │  │AnalysisDashboard│  │   ChatMessage   │  │
│  └────────┬────────┘  └────────┬────────┘  └─────────────────┘  │
│           │                    │                                 │
│           └────────────────────┴─────────────────────────────────│
│                               │                                  │
│                          localhost:3000                          │
└───────────────────────────────┼──────────────────────────────────┘
                                │ HTTP/REST API
┌───────────────────────────────┼──────────────────────────────────┐
│                        BACKEND (FastAPI)                         │
│                          localhost:8000                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ InspectionAgent │  │    Database     │  │   Claude API    │  │
│  │  (AI Assistant) │  │   (SQL Server)  │  │ (Azure OpenAI)  │  │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘  │
│           │                    │                    │            │
│           └────────────────────┴────────────────────┘            │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🖥️ Frontend (Next.js 14)

**Location:** `/frontend`  
**Port:** `http://localhost:3000`

### Technology Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 14.2.5 | React framework with App Router |
| React | 18.x | UI library |
| TypeScript | 5.x | Type safety |
| Tailwind CSS | 3.4.1 | Styling |
| Framer Motion | 11.x | Animations |
| Recharts | 2.10.x | Data visualizations |
| Lucide React | 0.263.x | Icons |

### Components

| Component | Description |
|-----------|-------------|
| `ChatInterface.tsx` | Main chat UI with message handling, tile navigation, and responsive layout |
| `ChatMessage.tsx` | Individual message rendering with typewriter effect |
| `AnalysisDashboard.tsx` | 70% width panel displaying KPI/ML charts and visualizations |
| `DashboardSidebar.tsx` | Navigation sidebar for dashboard views |
| `MLModelsChart.tsx` | ML model performance visualizations |

### Features

- **Responsive Split Layout**: Chat (30%) + Dashboard (70%) when viewing analytics
- **AI Chat**: Natural language interface to query inspection data
- **KPI Tiles**: 10 clickable KPI cards with drill-down visualizations
- **ML Model Tiles**: 9 prediction model cards with forecasting charts
- **Suggested Prompts**: Quick-start queries for common questions
- **Typewriter Effect**: Animated message rendering
- **Dark Glass-morphism UI**: Modern translucent design with AlUla branding

---

## ⚙️ Backend (FastAPI + Python)

**Location:** `/backend`  
**Port:** `http://localhost:8000`

### Technology Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| FastAPI | 0.104+ | REST API framework |
| Uvicorn | 0.24+ | ASGI server |
| Pydantic | 2.10+ | Data validation |
| pyodbc | 5.2+ | SQL Server connection |
| Pandas | 2.2+ | Data manipulation |
| python-dotenv | 1.0+ | Environment variables |

### Core Modules

#### `main.py` - API Server & AI Agent

The main application file containing:

**InspectionAgent Class:**
- `__init__()` - Initializes Azure OpenAI endpoint, API key, and database connection
- `get_system_prompt()` - Comprehensive AI persona for AlUla heritage inspection assistant
- `get_database_context()` - Fetches relevant data based on user query keywords
- `call_claude()` - Makes API calls to Claude via Azure OpenAI endpoint
- `detect_intent()` - Routes messages to appropriate handlers (KPI tiles, ML tiles, or AI chat)
- `process_message()` - Main entry point for message processing
- `get_kpi_tiles_response()` - Returns 10 KPI tile definitions
- `get_prediction_tiles_response()` - Returns 10 ML prediction tile definitions

**API Endpoints:**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Main chat endpoint - processes user messages |
| `/api/chat/clear` | DELETE | Clears conversation history |
| `/` | GET | Health check - returns server status |
| `/api/health` | GET | Detailed health check with database status |

#### `database.py` - Database Layer

SQL Server connection and query methods:

| Method | Description |
|--------|-------------|
| `get_connection()` | Creates pyodbc connection to SQL Server |
| `execute_query()` | Executes SQL and returns DataFrame |
| `get_ml_summary()` | Summary of all 9 ML model tables |
| `get_high_risk_locations()` | Top N locations by risk probability |
| `get_inspector_performance()` | Inspector metrics and classifications |
| `get_anomalies()` | Detected anomalies and outliers |
| `get_recurrence_predictions()` | Violation recurrence forecasts |
| `get_dashboard_stats()` | Aggregate dashboard statistics |

---

## 📊 KPIs (Key Performance Indicators)

| # | KPI Name | Description | Data Source |
|---|----------|-------------|-------------|
| 1 | Monthly Inspection Trends | Inspection volume, types, and outcomes over time | Event |
| 2 | Compliance Rate Analysis | Compliance levels by month and establishment type | Event |
| 3 | Inspector Performance Metrics | Workload, efficiency, and violation detection | Event |
| 4 | Violation Severity Distribution | Violations by severity level and financial impact | EventViolation |
| 5 | Geographic Distribution Analysis | Inspections and violations across regions | Event |
| 6 | Seasonal Patterns | Seasonal trends in inspections and violations | Event |
| 7 | Objection & Resolution Rates | Objection filing and resolution patterns | EventViolation |
| 8 | Top Violating Establishments | Establishments with the most violations | Event |
| 9 | Violation Recurrence Analysis | Repeat violations and improvement patterns | Event |
| 10 | Issue Category Analysis | Distribution of violations by category | EventViolation |

---

## 🤖 ML Prediction Models

| # | Model Name | Description | Algorithm | Table |
|---|------------|-------------|-----------|-------|
| 1 | Inspection Volume Forecast | Future inspection trends | Prophet/ARIMA | ML_Predictions |
| 2 | Compliance Rate Forecast | Predicted compliance rates | Time Series | ML_Predictions |
| 3 | Location Risk Assessment | Geographic risk zones | Random Forest | ML_Location_Risk |
| 4 | Anomaly Detection | Unusual patterns and outliers | Isolation Forest | ML_Anomalies |
| 5 | Severity Predictions | Predicted violation severity | XGBoost | ML_Severity_Predictions |
| 6 | Scheduling Recommendations | Optimal inspection timing | Decision Tree | ML_Scheduling_Recommendations |
| 7 | Objection Likelihood | Objection rate predictions | Logistic Regression | ML_Objection_Predictions |
| 8 | Location Clustering | Establishment groupings | K-Means | ML_Location_Clusters |
| 9 | Recurrence Risk Prediction | Repeat violation likelihood | LSTM | ML_Recurrence_Predictions |
| 10 | Inspector Performance Forecast | Performance tier classification | Neural Network | ML_Inspector_Performance |

---

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- ODBC Driver 18 for SQL Server
- Access to Azure OpenAI endpoint (Claude)

### Installation

**1. Clone the repository**
```bash
git clone <repository-url>
cd alula-inspection-ai
```

**2. Backend Setup**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**3. Configure Environment Variables**

Create `/backend/.env`:
```env
# Azure OpenAI / Claude
AZURE_OPENAI_ENDPOINT=<your-endpoint>
AZURE_OPENAI_KEY=<your-api-key>

# Database
DB_SERVER=<sql-server-ip>
DB_PORT=1433
DB_NAME=CHECK_ELM_AlUlaRC_DW
DB_USERNAME=<username>
DB_PASSWORD=<password>
```

**4. Frontend Setup**
```bash
cd frontend
npm install
```

### Running the Application

**Start Backend** (Terminal 1):
```bash
cd backend
source venv/bin/activate
python main.py
```
Backend runs at: `http://localhost:8000`

**Start Frontend** (Terminal 2):
```bash
cd frontend
npm run dev
```
Frontend runs at: `http://localhost:3000`

---

## 📁 Project Structure

```
alula-inspection-ai/
├── backend/
│   ├── main.py              # FastAPI app, InspectionAgent, endpoints
│   ├── database.py          # SQL Server connection & queries
│   ├── ai_service.py        # AI service utilities
│   ├── ai_functions.py      # AI helper functions
│   ├── requirements.txt     # Python dependencies
│   ├── venv/                # Virtual environment
│   └── .env                 # Environment variables (not in git)
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx         # Main page component
│   │   ├── layout.tsx       # Root layout
│   │   └── globals.css      # Global styles
│   ├── components/
│   │   ├── ChatInterface.tsx      # Main chat UI
│   │   ├── ChatMessage.tsx        # Message component
│   │   ├── AnalysisDashboard.tsx  # KPI/ML dashboard
│   │   ├── DashboardSidebar.tsx   # Navigation sidebar
│   │   └── MLModelsChart.tsx      # ML visualizations
│   ├── lib/
│   │   └── api.ts           # API client
│   ├── public/
│   │   ├── alula-bg.jpg     # Background image
│   │   └── alula-logo.png   # AlUla logo
│   ├── package.json         # Node dependencies
│   ├── tailwind.config.ts   # Tailwind configuration
│   └── tsconfig.json        # TypeScript configuration
│
└── README.md                # This file
```

---

## 🔌 API Reference

### POST /api/chat

Send a message to the AI assistant.

**Request:**
```json
{
  "message": "What is the current compliance rate?"
}
```

**Response (AI Chat):**
```json
{
  "message": "The current average compliance rate is 94%...",
  "chart_data": null,
  "chart_type": null
}
```

**Response (KPI Tiles):**
```json
{
  "type": "kpi_tiles",
  "tiles": [
    {
      "id": "kpi_01",
      "name": "Monthly Inspection Trends",
      "description": "Tracks inspection volume, types, and outcomes over time",
      "table": "Event"
    }
  ]
}
```

### DELETE /api/chat/clear

Clear conversation history.

**Response:**
```json
{
  "success": true,
  "message": "Conversation history cleared"
}
```

### GET /api/health

Get server and database health status.

**Response:**
```json
{
  "status": "running",
  "database": "connected",
  "ai_endpoint": "https://...",
  "agent": "AlUla Inspection Intelligence Assistant"
}
```

---

## 🎨 UI/UX Features

- **Glass-morphism Design**: Translucent panels with blur effects
- **AlUla Branding**: Custom colors (#104C64, #C0754D, #B6410F)
- **Responsive Layout**: Adapts between full-width chat and split dashboard view
- **Animated Transitions**: Smooth panel slides and message animations
- **Dark Theme**: Optimized for heritage site imagery backgrounds
- **Interactive Charts**: Hover tooltips, click interactions on Recharts visualizations

---

## 🔒 Security Notes

- API keys stored in environment variables (not committed to git)
- CORS configured for localhost development
- SQL Server connection uses TLS with certificate trust
- Conversation history limited to prevent memory overflow

---

## 📝 License

Proprietary - AlUla Royal Commission

---

## 👥 Contributors

- AlUla Inspection Team
- AI Development Team
