# ⚡ ATLAS — Personal Cyber Assistant (v4.0)

ATLAS is an autonomous, local personal voice assistant engineered for the Linux ecosystem (Ubuntu/Debian). It integrates graph-based natural language processing, secure memory persistence, and multi-model AI redundancy.

---

## 🎯 Overview

Key engineering priorities include:

- Local execution and data privacy
- End-to-end asynchronous architecture
- Secure, structured state persistence
- Intelligent model routing and failover
- Low-latency, real-time voice processing
- Maintainability and modular scalability
- Adherence to 12-Factor App methodology

---

## 🛠️ System Architecture & Engineering

ATLAS is architected around **12-Factor App** principles, enforcing strict separation of config and code, environment parity, and seamless portability.

```text
[User] ──(Microphone / sounddevice)──> [src/speech/listener.py] (faster-whisper)
                                                     │
                                                     │ (Raw Text)
                                                     ▼
[Voice Output] <──(edge-tts)── [src/brain/agent_graph.py] (LangGraph)
                                                     │
                         ┌───────────────────────────┴───────────────────────────┐
                         ▼                                                       ▼
      [src/database/brain_database.py]                      [src/brain/model_manager.py]
        (aiosqlite - Local Storage)                           (Ollama / Gemini Flash)
```

---

## 🗂️ Project Structure

```text
atlas/
│
├── config/
│   ├── settings.py
│   └── logger.py
│
├── src/
│   ├── brain/
│   │   ├── agent_graph.py
│   │   └── model_manager.py
│   │
│   ├── database/
│   │   └── brain_database.py
│   │
│   ├── speech/
│   │   ├── listener.py
│   │   └── speaker.py
│   │
│   └── tools/
│
├── tests/
│
├── .env
├── .gitignore
├── requirements.txt
└── main.py
```

---

## 📦 Core Components

### Configuration (`config/`)

#### `settings.py`
Centralized application settings powered by Pydantic Settings.

Key features:
- Automatic type casting and validation
- Strict `.env` parsing
- Decoupled configuration logic
- High maintainability and testability

#### `logger.py`
Centralized logging pipeline providing:
- Size-based automatic file rotation (5 MB ceiling)
- Colored terminal output
- Structured event and error traceability

---

### Storage Layer (`src/database/`)

#### `brain_database.py`
Persistence interface governing ATLAS conversation state.

Features:
- Fully asynchronous I/O via `aiosqlite`
- Historical dialogue tracking
- Ephemeral short-term memory
- Extensible schema for long-term state persistence
- Non-blocking database operations

---

### Cognitive Engine (`src/brain/`)

#### `agent_graph.py`
Core cognitive loop powered by LangGraph.

Responsibilities:
- State management across execution cycles
- Reasoning flows and decision routing
- Memory and model layer orchestration

#### `model_manager.py`
Model orchestration and failover management.

Routing workflow:
```text
Ollama (Primary / Local)
        │
        ▼
Gemini Flash (Fallback / Cloud)
```

Advantages:
- High availability
- Operational redundancy
- Zero service interruption on local model degradation

---

### Audio Pipeline (`src/speech/`)

#### `listener.py`
Audio ingestion and Speech-to-Text (STT) pipeline.

Stack:
- `sounddevice`
- `faster-whisper`

Features:
- `float32` sample capture
- Low-latency inference
- Fully local transcription processing

#### `speaker.py`
Text-to-Speech (TTS) output pipeline.

Stack:
- `edge-tts`
- `pygame.mixer`

Features:
- High-fidelity voice synthesis
- Asynchronous, non-blocking playback
- Responsive user interaction cycles

---

### Tooling & Automation (`src/tools/`)

Reserved interface for OS-level tool calls and system automation.

Planned capabilities:
- Local workflow automation
- Linux/Ubuntu system monitoring
- Controlled script execution
- Native LangGraph tool bindings

Status: In active development.

---

## 📡 Module Implementation Status

| Subsystem | Technology Stack | Status | Notes |
|---|---|---|---|
| Configuration | Pydantic Settings + `.env` | 🟢 Operational | Strictly typed |
| Logging | `RotatingFileHandler` | 🟢 Operational | Persistent disk logs |
| Database | `aiosqlite` | 🟢 Operational | Fully asynchronous |
| Audio Input | `faster-whisper` | 🟢 Operational | Stable capture & inference |
| AI Routing | Ollama → Gemini Flash | 🟢 Operational | Automated failover active |
| Cognitive Graph | LangGraph | 🟢 Operational | State machine functional |
| Audio Output | `edge-tts` + `pygame` | 🟢 Operational | Non-blocking streaming |
| Tool Integration | Local OS Automation | 🔴 Planned | Queued for next release |

---

## 🚀 Installation & Setup

### 1. Clone the repository

```bash
git clone [https://github.com/eriklegramante-dev/atlas.git](https://github.com/eriklegramante-dev/atlas.git)
cd atlas
```

### 2. Configure the virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_api_key_here
OLLAMA_MODEL=llama3
DATABASE_PATH=data/atlas.db
LOG_LEVEL=INFO
```

---

## ▶️ Usage

Start the assistant:

```bash
python main.py
```

---

## 🧪 Test Suite & Diagnostics

Run integration and component tests via `pytest`:

### Memory integration test

```bash
pytest tests/test_memory_integration.py -s -v
```

### Cognitive graph execution test

```bash
pytest tests/test_graph.py -s -v
```

### Speech synthesis test

```bash
pytest tests/test_speech.py -s -v
```

---

## 🔒 Security Practices

- Strict separation of credentials and application code
- Environment variables ignored via `.gitignore`
- Local-first architecture to minimize external data transmission
- Guarded logging outputs to prevent credential leaks
- Sandboxed local database storage

---

## 📈 Roadmap

### Current Release (v4.0)

- [x] 12-Factor App architectural refactor
- [x] Asynchronous database pipeline
- [x] LangGraph state machine implementation
- [x] On-device STT with `faster-whisper`
- [x] Non-blocking TTS playback
- [x] Autonomous model failover strategy

### Upcoming Features (v5.0)

- [ ] Linux system automation tools
- [ ] Autonomous task scheduler
- [ ] Vector database integration (RAG / Semantic Memory)
- [ ] Modular plugin engine
- [ ] OS performance monitoring hooks
- [ ] Local web administration dashboard

---

## 🏛️ Design Philosophy

ATLAS is engineered with four core pillars: autonomy, privacy, scalability, and deterministic control.

The goal is to build a personal assistant capable of long-term contextual understanding and system orchestration on local hardware, without hard dependencies on proprietary external infrastructure.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 👨‍💻 Author

Built by [Erik Legramante](https://github.com/eriklegramante-dev). 