# AION OS — AI Operating System for Telegram Mini App

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

**AION OS** is the AI-powered backend for the AION Telegram Mini App — a platform that helps Russian-speaking expats, relocators, and digital nomads find services, book appointments, and manage daily life abroad.

> One conversation — any service. AI agents do the work.

---

## ✨ Features

- **🤖 8 AI Agents** — Router, Search, Booking, CRM, Navigation, Memory, Knowledge, Partner
- **⚡ Three-tier intelligent routing** — CommandRouter → IntentCache → LLM → Agent
- **🎙️ Voice pipeline** — Speech-to-text + text-to-speech (streaming)
- **🧠 RAG Engine** — Knowledge base search with pgvector
- **💾 Long-term memory** — Remembers user preferences across sessions
- **🔌 Universal LLM Adapter** — Works with DeepSeek, Qwen, Llama, Groq, OpenAI
- **📡 Real-time communication** — WebSocket + SSE streaming
- **🔐 Security** — Telegram InitData verification + JWT
- **🐳 Docker** — Full containerized deployment (PostgreSQL + pgvector, Redis, nginx)

---

## 🏗️ Architecture

```
User → Telegram Mini App
           ↕ WebSocket / REST
    ┌─────────────────────┐
    │   FastAPI Backend   │
    │  ┌───────────────┐  │
    │  │ COMMAND       │  │  ◄── 0 LLM (30 patterns, 0.1ms)
    │  │ ROUTER        │  │      Navigation, greetings, help
    │  └──────┬────────┘  │
    │  ┌──────┴────────┐  │
    │  │ INTENT CACHE  │  │  ◄── 0 LLM (LRU, 200 entries)
    │  └──────┬────────┘  │
    │  ┌──────┴────────┐  │
    │  │ LLM ADAPTER   │  │  ◄── 1 LLM call (complex queries)
    │  └──────┬────────┘  │
    │  ┌──────┴────────┐  │
    │  │ AI AGENTS     │  │  ◄── 8 specialist agents
    │  │ (Search, CRM, │  │
    │  │  Booking, ...) │  │
    │  └──────┬────────┘  │
    │  ┌──────┴────────┐  │
    │  │ RAG + Memory  │  │
    │  └───────────────┘  │
    └─────────┬───────────┘
              ↓
    ┌─────────────────────┐
    │  PostgreSQL + Redis │
    └─────────────────────┘
```

---

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/YOUR_USER/aion-os.git
cd aion-os/aion_os

# 2. Configure
cp .env.example .env
# Edit .env — add your keys:
#   TELEGRAM_BOT_TOKEN=...
#   OPENAI_API_KEY=gsk_... (Groq — free, 14K req/day)

# 3. Docker
cd docker
docker compose up -d

# 4. Verify
python ../docker/healthcheck.py --wait --verbose

# Open: http://localhost:8000
# Swagger: http://localhost:8000/docs
# Admin: http://localhost:8080
```

### Quick local test (no Docker)

```bash
cd aion_os/backend
AION_TEST_MODE=1 python test_all.py
```

---

## 🧠 AI Agents

| Agent | Responsibility | Intent Trigger |
|-------|---------------|----------------|
| **Router** | Routes messages to correct agent | All messages |
| **Search** | Finds services, partners, items | `search` |
| **Booking** | Creates/manages bookings | `booking` |
| **CRM** | Orders, history, cancellations | `crm` |
| **Navigation** | Opens screens, categories | `navigate` |
| **Memory** | Stores/retrieves preferences | `memory` |
| **Knowledge** | Answers from knowledge base | `knowledge` |
| **Partner** | Finds & recommends partners | `partner` |

---

## 📡 API

### REST

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/auth/telegram` | — | Telegram InitData → JWT |
| POST | `/api/v1/chat/text` | JWT | Send message → AI response |
| POST | `/api/v1/chat/voice` | JWT | Voice input → AI response |
| GET | `/api/v1/categories` | — | 23 service categories |
| POST | `/api/v1/partners/search` | — | Search partners |
| POST | `/api/v1/bookings` | JWT | Create booking |

### WebSocket `ws://host:8000/ws`

```json
→ {"type": "auth", "token": "jwt..."}
← {"type": "auth_ok", "user_id": 123}

→ {"type": "chat.message", "text": "Найди стоматолога"}
← {"type": "chat.stream", "text": "Вот..."}
← {"type": "chat.done", "text": "...", "navigation": {...}, "cards": [...]}
```

---

## 💾 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | FastAPI + Python 3.12 |
| **Database** | PostgreSQL 16 + pgvector |
| **Cache** | Redis 7 |
| **LLM** | DeepSeek / Qwen / Llama / Groq (universal adapter) |
| **Voice** | Whisper (STT) + Kokoro (TTS) |
| **Agents** | Custom agent framework (8 agents) |
| **Streaming** | WebSocket + SSE |
| **Auth** | Telegram InitData + JWT |
| **Deployment** | Docker Compose + nginx |

---

## 📁 Project Structure

```
aion_os/
├── backend/              # Python backend
│   ├── app/
│   │   ├── api/          # REST, WebSocket, SSE endpoints
│   │   ├── agents/       # 8 AI agents + CommandRouter + IntentCache
│   │   ├── core/         # Auth, Config, Security
│   │   ├── db/           # Database models + migrations
│   │   ├── llm/          # Universal LLM adapter (4 providers)
│   │   ├── memory/       # Long-term + conversation memory
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── rag/          # RAG engine (pgvector)
│   │   ├── voice/        # STT + TTS pipeline
│   │   └── services/     # CRM, partner services
│   ├── test_*.py         # Test suites (REST, WebSocket, Agents)
│   └── requirements.txt
├── docker/
│   ├── docker-compose.yml
│   ├── Dockerfile.*
│   └── healthcheck.py    # Integration test
├── admin_panel/          # Web admin interface
├── knowledge_base/       # RAG documents
├── .env.example          # Configuration template
├── HANDBOOK.md           # Full handoff documentation
└── README.md             # This file
```

---

## 🧪 Testing

```bash
# Master test suite (3 test suites, 26 checks)
cd aion_os/backend
AION_TEST_MODE=1 OPENAI_API_KEY=gsk_... python test_all.py

# Individual tests
AION_TEST_MODE=1 python test_server.py        # REST API
AION_TEST_MODE=1 python test_websocket.py      # WebSocket
AION_TEST_MODE=1 OPENAI_API_KEY=... python test_agents_live.py  # AI Agents

# Docker integration
cd aion_os/docker
python healthcheck.py --wait --verbose
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE).

---

## 👥 Team

Built for the AION Tech Team.  
Questions? → CEO KB
