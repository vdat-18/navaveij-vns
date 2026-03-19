# Navaveij Clinical Recommendation Engine 🏥

Welcome to **Navaveij**, an AI-powered system designed to help doctors suggest the best health checkup plans for their patients. This system uses advanced AI and clinical rules to analyze medical data safely and accurately.

---

## 🚀 What does this system do?

Think of Navaveij as an **"AI Medical Assistant."** It follows a specific path to give a recommendation:

1.  **Get Data**: It connects to hospital records to get patient info (blood tests, heart rate, etc.).
2.  **Protect Privacy**: It hides the patient's name and ID so the AI doesn't know who they are.
3.  **Analyze Trends**: It looks at how a patient's health changed over the last 3 years.
4.  **AI Reasoning**: It asks a smart AI (LLM) to choose the best checkup package (Standard, Advanced, or Premium).
5.  **Explain Why**: It provides a clear medical reason for its choice.

---

## 🏗️ Project Structure (How code is organized)

The code is split into logical "layers" to keep it clean and professional:

*   📂 `src/api/`: The **Entry Point**. This is where the website or mobile app talks to the system.
*   📂 `src/orchestrator/`: The **Brain**.
    *   `manager.py`: Controls the whole process from start to finish.
    *   `workflows/`: Steps of medical reasoning.
    *   `infrastructure/`: Handles the connection to medical databases (MCP).
    *   `privacy/`: Masks private information (names, IDs).
    *   `safety/`: Double-checks AI advice to make sure it is medically safe.
*   📂 `src/mcp_server/`: The **Data Connector**. It fetches real medical data using the Model Context Protocol (MCP).
*   📂 `src/synthesis/`: The **Data Factory**. It uses AI to create "fake patients" with real medical logic for testing.
*   📂 `src/shared/`: Common tools like error handling (Exceptions) and settings.

---

## 🛠️ Technology Stack (What we use)

We use modern and professional tools:

| Tool | Purpose |
| :--- | :--- |
| **Python 3.10+** | The main language. |
| **FastAPI** | Makes the system fast and easy to talk to over the internet. |
| **BAML** | A special tool to make sure the AI always gives us clean, structured data. |
| **MCP** | "Model Context Protocol" – a new way to connect AI to databases. |
| **Pydantic** | Ensures all data (numbers, dates) is in the correct format. |
| **Loguru** | Helps us see what's happening inside the system by writing clear logs. |

---

## 🔬 Scientific Logic (The 5-Phase Workflow)

### 0. Run with Docker (Recommended for PoC) 🐳
The easiest way to launch the entire ecosystem is using Docker Compose. Ensure you have Docker and Docker Compose installed.

```bash
# Build and start all services
docker-compose up --build
```
*   **Backend**: `http://localhost:8000`
*   **Frontend**: `http://localhost:3000`
*   **Persistence**: Data in `assets/` and `logs/` is preserved across restarts via volumes.

### 1. Backend Setup & Run (Manual)
```bash
# Install dependencies
uv sync
When the system analyzes a patient, it follows these 5 steps:

1.  **Baseline**: Get the basic profile (age, gender, history).
2.  **Signals**: Find medical alerts (e.g., "Blood pressure is too high!").
3.  **Trends**: Look at changes (e.g., "Is the patient getting heavier every year?").
4.  **AI Inference**: The AI considers everything and picks a checkup tier.
5.  **Finalize**: Combine everything into a final report for the doctor.

---

## 🧪 How to Test and Run

### 2. MCP Inspector (PoC & Debugging) 🛡️
Visualizes the secure clinical data layer and AI tool orchestration:
```bash
# Run from the project root
npx @modelcontextprotocol/inspector uv run python -m src.mcp_server.server
```
*   **Interface**: `http://localhost:6274`
*   **Example Tool**: `get_clinical_signals`
*   **Example Patient ID**: `id_2bb52ad3` (Metabolic Syndrome case) or `id_7d5e2a4b` (Cancer screening case).


### 3. Frontend Setup & Run
### 1. Generating Test Data
You can create fake patients to test the system:
```bash
uv run python -m src.synthesis --count 1
```

### 2. Running the API
To start the system server:
```bash
uv run python -m src.api.main
```

### 3. Running Tests
To make sure everything is working correctly:
```bash
pytest
```

---

## 🛡️ Error Policy
We follow a simple rule: **"Let it crash."** We don't hide errors with complicated `try/except` blocks. If something goes wrong, the system shows us the exact error immediately so we can fix it.

---

*Developed with ❤️ for Navavej International Hospital.*
