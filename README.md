# LumanSense 💡

LumanSense is an adaptive municipal street-lighting control system. It utilizes Edge AI, Multi-Agent Coordination, and Model Context Protocol (MCP) services to optimize the urban energy footprint while prioritizing public safety. By analyzing real-time pedestrian flow telemetry, the system dynamically dims or brightens streetlights.

---

## 📖 The Problem

Traditional municipal street-lighting systems operate on static timers or basic photocells, keeping lights at 100% brightness throughout the night. This approach leads to:
1. **High Energy Waste**: Heavy power consumption during late-night or low-traffic hours when streets are empty.
2. **Shortened Equipment Lifespans**: Constant maximum-power operations degrade LED components faster.
3. **Public Safety Concerns**: Arbitrary dimming schedules can leave zones pitch-black when pedestrians or vehicles are actually present, increasing security risks.

---

## 🚀 The Solution

LumanSense addresses these issues through **predictive and reactive street-lighting control**:
* **Reactive Actuation**: Dims or brightens streetlights in real-time based on current pedestrian detections classified using hysteresis filters (e.g., normal activity, spikes, clearing, low activity).
* **Predictive Planning**: Leverages a Markov Chain model to forecast pedestrian transition probabilities across zones (e.g., if a pedestrian enters Zone A, they are likely to transition to Zone B in future steps) and establishes a proactive brightness schedule.
* **Intelligent Actuation Blending**: Combines predictive forecasts and real-time reactive signals to compute the optimal brightness percentage:
  $$\text{Brightness}_{\text{lamp}} = (\text{Forecast}_{\text{prob}} \times \text{Brightness}_{\text{plan}}) + ((1 - \text{Forecast}_{\text{prob}}) \times \text{Brightness}_{\text{reactive}})$$
* **Traffic Density Clustering**: Employs K-Means clustering (`k-means-clusterer-mcp`) to classify traffic densities (`LOW_TRAFFIC`, `PEAK_TRAFFIC`, `TRAFFIC_SURGE`, etc.) by comparing current footfalls against exponential moving averages (EMA).
* **AI-Assisted Operations**: Features an interactive Natural Language chat assistant enabling municipal operators to check metrics, forecast distributions, and audit decisions.

---

## 🏗️ Architecture

LumanSense is built using the **Google ADK (Agent Development Kit)** and a series of **FastMCP servers** that decouple database access, machine learning clustering, and hardware simulation.

### System Architecture Block Diagram
```mermaid
graph TD
    classDef client fill:#3b82f6,stroke:#1d4ed8,stroke-width:2px,color:#fff;
    classDef agent fill:#10b981,stroke:#047857,stroke-width:2px,color:#fff;
    classDef mcp fill:#f59e0b,stroke:#d97706,stroke-width:2px,color:#fff;
    classDef db fill:#ec4899,stroke:#be185d,stroke-width:2px,color:#fff;

    subgraph Client Interface
        UI[Streamlit Dashboard / lumanui.py]:::client
        Sim[Telemetry Producer / app/main.py]:::client
    end

    subgraph ADK Agent Ecosystem
        Orch[Orchestrator Agent]:::agent
        CtrlAgent[Controller Agent]:::agent
        Planner[Brightness Planner Agent]:::agent
        Analyst[Ask Luman Agent]:::agent
        Auditor[Auditor Agent / Critic]:::agent
    end

    subgraph MCP Service Servers
        VisionMCP[Vision MCP]:::mcp
        DBMCP[Database MCP]:::mcp
        ActuatorMCP[Controller MCP]:::mcp
        EnergyMCP[Energy MCP]:::mcp
        KMeansMCP[K-Means Clusterer MCP]:::mcp
    end

    subgraph Data Storage
        SQLite[(luman_sense.db)]:::db
    end

    Sim -->|Process Raw Frames| VisionMCP
    VisionMCP -->|Event Queue| CtrlAgent
    Orch -->|Delegates Real-Time Control| CtrlAgent
    CtrlAgent -->|Retrieve Predictions| Planner
    CtrlAgent -->|Classify Density State| KMeansMCP
    CtrlAgent -->|Save Events| DBMCP
    CtrlAgent -->|Actuate Dimming| ActuatorMCP
    CtrlAgent -->|Calculate Savings| EnergyMCP
    UI -->|Interactive Analytics| Analyst
    Analyst -->|Audit Decisions| Auditor
    Analyst -->|Query Metrics| DBMCP
    DBMCP --> SQLite
    Auditor --> DBMCP
```

### ADK Agents
1. **Orchestrator Agent** ([orchestrator_agent.py](file:///home/krithi/Downloads/Antigravity/AGY-PROJECTS/luman-sense/app/agent/orchestrator_agent.py)): Acts as the Environmental Coordinator. Routes real-time telemetry inputs to the dimming controller.
2. **Controller Agent** ([controller_agent.py](file:///home/krithi/Downloads/Antigravity/AGY-PROJECTS/luman-sense/app/agent/controller_agent.py)): The core loop coordinator. Processes queued detection events, queries plans, makes dimming decisions, and actuates physical brightness levels.
3. **Brightness Planner Agent** ([brightness_planner_agent.py](file:///home/krithi/Downloads/Antigravity/AGY-PROJECTS/luman-sense/app/agent/brightness_planner_agent.py)): Computes multi-step ahead transition probability forecasts across zones using historical matrices.
4. **Ask Luman Agent** ([ask_luman_agent.py](file:///home/krithi/Downloads/Antigravity/AGY-PROJECTS/luman-sense/app/agent/ask_luman_agent.py)): Enables natural language querying of database records, state distributions, and overall energy savings.
5. **Lighting Auditor Agent** ([luman_sense_critic_agent.py](file:///home/krithi/Downloads/Antigravity/AGY-PROJECTS/luman-sense/app/agent/luman_sense_critic_agent.py)): A critique agent that audits recent lighting dimming actions to verify if safety standards were maintained.

### MCP Tools & Services
* **VisionMCP** ([vision_service.py](file:///home/krithi/Downloads/Antigravity/AGY-PROJECTS/luman-sense/app/mcp/vision_service.py)): Classifies raw video frames (pedestrian count, timestamp, zone) into discrete activity states using hysteresis filters.
* **DatabaseMCP** ([database_mcp.py](file:///home/krithi/Downloads/Antigravity/AGY-PROJECTS/luman-sense/app/mcp/database_mcp.py)): Manages the SQLite database operations (`luman_sense.db`).
* **ControllerMCP** ([controller_service.py](file:///home/krithi/Downloads/Antigravity/AGY-PROJECTS/luman-sense/app/mcp/controller_service.py)): Mock hardware interface for adjusting lamp brightness.
* **EnergyMCP** ([energy_service.py](file:///home/krithi/Downloads/Antigravity/AGY-PROJECTS/luman-sense/app/mcp/energy_service.py)): Computes estimated energy savings relative to a baseline brightness level (defaults to 90%).
* **K-Means Clusterer MCP** ([k_means_clusterer.py](file:///home/krithi/Downloads/Antigravity/AGY-PROJECTS/luman-sense/app/mcp/k_means_clusterer.py)): Clusters pedestrian-EMA feature vectors to identify specific traffic congestion patterns.

---

## 📋 Data Schema

LumanSense stores its operational logs in a local SQLite file: `luman_sense.db`.

### 1. `detection_events`
Tracks incoming pedestrian data and classifications:
* `timestamp` (TEXT)
* `zone` (TEXT)
* `pedestrians` (INTEGER)
* `ema` (REAL)
* `trend_label` (TEXT)
* `zone_occupancy_forecast` (REAL)
* `delta_occupancy` (REAL)
* `cluster_label` (TEXT)

### 2. `decision_events`
Tracks dimming actuations and performance details:
* `timestamp` (TEXT)
* `zone` (TEXT)
* `state` (TEXT)
* `pred_brightness` (INTEGER)
* `reactive_brightness` (INTEGER)
* `brightness` (INTEGER) (Final Actuation)
* `energy_saved_watts` (INTEGER)
* `reason` (TEXT)

---

## 🔄 Real-Time Control Loop Flow

```mermaid
sequenceDiagram
    autonumber
    participant Sensor as Video Sensor (YOLO Mock)
    participant Vision as Vision MCP
    participant EventQueue as Event Bus Queue
    participant Controller as Controller Agent
    participant Planner as Brightness Planner
    participant KMeans as K-Means Clusterer MCP
    participant Actuator as Controller MCP Actuator
    participant DB as Database MCP

    Sensor->>Vision: process_detection(pedestrians, zone)
    Vision->>Vision: Update EMA & trend direction
    Vision->>Vision: Classify state (e.g. LOW_ACTIVITY, SPIKE)
    Vision->>EventQueue: Enqueue DetectionEvent
    EventQueue->>Controller: Dequeue event
    Controller->>KMeans: predict cluster (pedestrians, EMA)
    KMeans-->>Controller: Return density state (e.g. TRAFFIC_SURGE)
    Controller->>Planner: Fetch predictive zone plan (Markov forecast prob)
    Planner-->>Controller: Return expected forecast probability
    Controller->>Controller: Compute final brightness (Forecast * Plan + (1-Forecast) * Reactive)
    Controller->>Actuator: set_lamp_brightness(percentage)
    Controller->>DB: Save Detection & Decision events
```

---

## 🛠️ Setup Instructions

### Prerequisites
* Python version `3.11` to `3.13`
* `uv` (fast Python package manager)
* `google-agents-cli` (installed with `uv tool install google-agents-cli`)
* Valid GCP credentials and `GEMINI_API_KEY` set in your `.env` file.

### Installation
1. Clone the repository and navigate to the project directory:
   ```bash
   cd luman-sense
   ```
2. Install packages and set up dependencies:
   ```bash
   agents-cli install
   ```

---

## 🏃 Running LumanSense

### 1. Run the Control Loop Simulation
Executes the pedestrian telemetry generator (`yolo_mock_producer`) and drives the automated street-lighting coordinator over the scenarios:
```bash
uv run python -m app.main
```

### 2. Run the Streamlit Dashboard
Launches the Web UI containing real-time traffic statistics charts and the interactive **Ask LumanSense** AI Assistant portal:
```bash
uv run streamlit run lumanui.py
```

### 3. Local Development Playground
Launch the local `agents-cli` interactive developer playground to test agent routing and tool call logic manually:
```bash
agents-cli playground
```
