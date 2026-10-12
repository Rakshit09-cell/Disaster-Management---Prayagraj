# 🚨 Multi-Agent Disaster Management System
### Prayagraj District, Uttar Pradesh, India

A multi-agent AI system that coordinates disaster response using 7 specialized AI agents powered by **LangChain** and **Groq AI**.

---

## 📐 Architecture

```
User Input (Disaster Scenario)
        │
        ▼
┌───────────────────────────────────────────────────┐
│              AGENT PIPELINE (Sequential)          │
├───────────────────────────────────────────────────┤
│                                                   │
│  🌦️ Weather Agent ──► 🗺️ GIS Agent ──► 🚑 Resource Agent
│         │                    │                │
│         ▼                    ▼                ▼
│  🏥 Hospital Agent ──► 🚒 Rescue Agent ──► 📢 Alert Agent
│                                                   │
│         All Reports Feed Into:                    │
│                   ▼                               │
│         🧠 Crisis Coordinator                     │
│         (Final Unified Action Plan)               │
│                                                   │
└───────────────────────────────────────────────────┘
```

## 🔧 Tech Stack

| Component       | Technology               |
|-----------------|--------------------------|
| Backend         | Python Flask              |
| AI Framework    | LangChain                 |
| LLM Provider    | Groq AI (LLaMA 3.3 70B)  |
| Frontend        | HTML/CSS/JavaScript       |
| Streaming       | Server-Sent Events (SSE)  |
| Data            | Simulated Prayagraj Data  |

## 🚀 Setup & Run

### 1. Get a Groq API Key
- Go to [https://console.groq.com](https://console.groq.com)
- Sign up (free) and create an API key

### 2. Install Dependencies
```bash
cd disaster-management-system
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```

### 4. Open in Browser
```
http://localhost:5000
```

### 5. Use the System
1. Paste your Groq API key
2. Type a disaster scenario (or click a quick-scenario button)
3. Click "Deploy Agents"
4. Watch agents activate one-by-one with real-time results
5. View the final coordinated action plan

---

## 🤖 Agent Details

| # | Agent | Role | LangChain Tool |
|---|-------|------|----------------|
| 1 | 🌦️ Weather Agent | Analyzes weather, river levels, IMD alerts | `get_weather_data` |
| 2 | 🗺️ GIS Agent | Identifies affected areas, population at risk | `get_location_data` |
| 3 | 🚑 Resource Agent | Assesses NDRF/SDRF/police/fire deployment | `get_resource_data` |
| 4 | 🏥 Hospital Agent | Maps hospitals, beds, ambulances, blood banks | `get_hospital_data` |
| 5 | 🚒 Rescue Agent | Plans evacuation routes and rescue operations | `get_evacuation_data` |
| 6 | 📢 Alert Agent | Drafts Hindi/English emergency alerts | `get_control_room_numbers` |
| 7 | 🧠 Coordinator | Synthesizes all reports into final action plan | All data |

## 🗂️ LangChain Components Used

- `ChatGroq` — LLM integration with Groq API
- `ChatPromptTemplate` — Structured prompts for each agent
- `StrOutputParser` — Output parsing
- `@tool` decorator — LangChain tools for data access
- `LCEL Pipe Syntax` — `prompt | llm | parser` chains

## 📍 Simulated Data Coverage

- **9 flood-prone areas** with population and risk levels
- **7 safe zones** with shelter capacities
- **7 hospitals** with bed/ICU/ambulance data
- **Emergency resources**: NDRF, SDRF, Police, Fire Brigade, NGOs
- **8 evacuation routes** with real-time status
- **10+ control room numbers**
- **Weather data**: rainfall, river levels, IMD alerts

---

## 📁 Project Structure

```
disaster-management-system/
├── app.py                  # Flask backend + LangChain agents
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── templates/
    └── index.html          # Frontend dashboard
```

---

## 📝 License

Final Year Academic Project — For educational purposes.
