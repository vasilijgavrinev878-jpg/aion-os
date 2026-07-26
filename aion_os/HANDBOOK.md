# AION OS — Handoff Document

**Version:** 0.1.0
**Date:** July 27, 2026
**Author:** CEO — for Tech Team

---

## 📋 Overview

AION OS is the AI Operating System backend for the AION Telegram Mini App. It provides a complete AI assistant with:
- Voice + Text chat
- 8 specialized AI agents (Router, Search, Booking, CRM, Navigation, Memory, Knowledge, Partner)
- RAG engine for knowledge base search
- Long-term user memory
- CRM integration (bookings, orders, partners)
- WebAdmin panel

**Tech stack:** Python 3.12, FastAPI, PostgreSQL + pgvector, Redis, Docker

---

## 🚀 Quick Start for Developers

### Prerequisites
- Docker Desktop
- Telegram Bot Token (from @BotFather)
- Groq API key (free, 14K req/day) — get at https://console.groq.com

### 1. Configure

```bash
cd aion_os
cp .env.example .env
# Edit .env — add your keys:
#   TELEGRAM_BOT_TOKEN=...
#   OPENAI_API_KEY=gsk_... (Groq key)
```

### 2. Start

```bash
cd aion_os/docker
docker compose up -d
```

### 3. Verify

```bash
python docker/healthcheck.py --verbose
```

---

## 🧠 Architecture

```
Telegram Mini App (Frontend)
       ↕ WebSocket / REST
┌─────────────────────────────────┐
│   Backend API (FastAPI :8000)   │
│  ┌──────┐ ┌──────┐ ┌────────┐  │
│  │ REST │ │  WS  │ │  SSE   │  │
│  └──┬───┘ └──┬───┘ └───┬────┘  │
│     └────────┼──────────┘       │
│          ┌───┴───┐              │
│          │ Auth  │              │
│          └───┬───┘              │
└──────────────┼──────────────────┘
               ↓
┌─────────────────────────────────┐
│      AI Core                    │
│  ┌──────────┐ ┌──────────────┐  │
│  │ LLM      │ │ Agent Router │  │
│  │ Adapter  │ │ (classifies  │  │
│  │ (univers)│ │  intent)     │  │
│  └────┬─────┘ └──────┬───────┘  │
│       │              │          │
│       │    ┌─────────┴──────┐   │
│       │    │ Search Agent   │   │
│       │    │ Booking Agent  │   │
│       │    │ CRM Agent      │   │
│       │    │ Navigation Ag. │   │
│       │    │ Knowledge Ag.  │   │
│       │    │ Memory Agent   │   │
│       │    │ Partner Agent  │   │
│       │    └────────┬───────┘   │
│       └─────────────┼───────────┤
│                     ↓           │
│  ┌──────────────────────────┐   │
│  │  RAG Engine              │   │
│  │  (pgvector / SQLite)     │   │
│  └──────────┬───────────────┘   │
└─────────────┼───────────────────┘
              ↓
┌─────────────────────────────────┐
│  Databases                      │
│  ┌──────────┐ ┌──────┐         │
│  │PostgreSQL│ │Redis │         │
│  │ +pgvector│ │Cache │         │
│  └──────────┘ └──────┘         │
└─────────────────────────────────┘
```

### Services (Docker)

| Service | Port | Description | Depends On |
|---------|------|-------------|------------|
| `api` | 8000 | FastAPI backend | postgres, redis |
| `admin` | 8080 | Web admin panel (nginx) | api |
| `postgres` | 5432 | PostgreSQL 16 + pgvector | — |
| `redis` | 6379 | Cache + queues | — |
| `worker` | — | Background tasks | postgres, redis |
| `ollama` | 11434 | Local LLM (CPU profile) | — |
| `prometheus` | 9090 | Monitoring (opt-in) | — |

---

## 📁 Project Structure

```
aion_os/
├── backend/                    # Python backend
│   ├── app/
│   │   ├── api/               # REST, WebSocket, SSE
│   │   ├── agents/            # 8 AI agents
│   │   ├── core/              # Auth, Config, Security
│   │   ├── db/                # Database + migrations
│   │   ├── llm/               # Universal LLM adapter
│   │   │   └── providers/     # DeepSeek, Qwen, Llama, OpenAI
│   │   ├── memory/            # Long-term + conversation
│   │   ├── models/            # SQLAlchemy models
│   │   ├── rag/               # RAG engine
│   │   ├── voice/             # STT + TTS
│   │   └── services/          # CRM
│   ├── .env                   # 🔑 YOUR KEYS HERE
│   ├── requirements.txt
│   └── pyproject.toml
├── docker/
│   ├── docker-compose.yml     # All services
│   ├── Dockerfile.*           # Service images
│   ├── healthcheck.py         # Integration test
│   └── init-db.sh             # DB setup
├── admin_panel/                # Admin HTML
├── knowledge_base/             # RAG data
├── .env.example
└── HANDBOOK.md                 # ← You are here
```

---

## 🔌 API Reference

### REST Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/auth/telegram` | — | Telegram InitData → JWT |
| POST | `/api/v1/chat/text` | JWT | Send message → AI response |
| POST | `/api/v1/chat/voice` | JWT | Voice → text → AI response |
| GET | `/api/v1/categories` | — | 23 service categories |
| GET | `/api/v1/memory/{user_id}` | — | Get user memories |
| PUT | `/api/v1/memory/{user_id}` | — | Store memory |
| DELETE | `/api/v1/memory/{user_id}` | — | Clear memories |
| POST | `/api/v1/partners/search` | — | Search partners |
| GET | `/api/v1/partners/{id}` | — | Partner details |
| POST | `/api/v1/bookings` | JWT | Create booking |
| GET | `/api/v1/bookings` | JWT | User bookings |
| POST | `/api/v1/kb/search` | JWT | RAG search |
| POST | `/api/v1/kb/ingest/file` | JWT | Ingest document |
| POST | `/api/v1/kb/ingest/directory` | JWT | Ingest directory |
| GET | `/api/v1/admin/health` | — | System health |
| GET | `/api/v1/admin/stats` | — | System stats |

### WebSocket: `ws://host:8000/ws`

**Auth flow:**
```json
→ {"type": "auth", "token": "jwt_token_here"}
← {"type": "auth_ok", "user_id": 123}
```

**Chat flow:**
```json
→ {"type": "chat.message", "text": "Привет!", "lang": "ru"}
← {"type": "chat.stream", "text": "При..."}
← {"type": "chat.stream", "text": "вет!"}
← {"type": "chat.done", "text": "Привет!", "navigation": {...}, "cards": [...]}
```

**Voice flow:**
```json
→ {"type": "chat.voice", "audio": "base64...", "voice_response": true}
← {"type": "voice.transcribed", "text": "..."}
← {"type": "chat.stream", "text": "..."}
← {"type": "chat.voice_stream", "audio": "base64...", "format": "ogg"}
← {"type": "chat.done", "text": "...", "navigation": {...}, "cards": [...]}
```

### SSE Streaming: `GET /api/v1/chat/stream?q=...&conversation_id=...`

```
event: start
data: {"status": "started"}

event: message
data: {"text": "streaming chunk..."}

event: done
data: {"text": "full response...", "status": "complete"}
```

---

## 🤖 AI Agents

### Router Agent
**Entry point for all messages.** Classifies intent and routes to specialist agents.

| Intent | Routed To | Example |
|--------|-----------|---------|
| `search` | SearchAgent | «Найди стоматолога» |
| `booking` | BookingAgent | «Запиши на массаж» |
| `navigate` | NavigationAgent | «Открой категории» |
| `knowledge` | KnowledgeAgent | «Что такое AION?» |
| `partner` | PartnerAgent | «Найди партнёра» |
| `crm` | CRMAgent | «Мои заказы» |
| `memory` | MemoryAgent | «Запомни...» |
| `chat` | LLM (direct) | «Привет!» |

### Search Agent (3-stage search)
```
Query → Intent Classification → 1. RAG (pgvector)
                                  → 2. Direct DB query (partners)
                                  → 3. LLM generates response
```

### Booking Agent
Creates and manages service bookings. Extracts booking details via LLM.

### CRM Agent
Lists orders, checks status, cancels bookings, creates support tickets.

### Navigation Agent
Returns `navigation` commands for the Mini App to open screens/categories.

### Memory Agent
Stores/retrieves user preferences via LLM-powered extraction.

### Partner Agent
Searches, filters, and recommends service partners from the database.

### Knowledge Agent
Answers questions from the RAG knowledge base (FAQ, docs, bibles).

---

## 💾 Database Schema

### Tables (auto-created via SQLAlchemy)

| Table | Key Fields | Purpose |
|-------|-----------|---------|
| `users` | telegram_id, language_code, preferences | Users |
| `partners` | name, category, city, rating, phone | Service providers |
| `bookings` | user_id, partner_id, category, status | Bookings |
| `user_memory` | user_id, memory_type, memory_key, value | Long-term memory |
| `agent_logs` | user_id, agent_name, action, latency | Monitoring |
| `knowledge_chunks` | content, embedding(vector), metadata | RAG (pgvector) |

### pgvector
```sql
CREATE EXTENSION vector;
CREATE TABLE knowledge_chunks (
    id TEXT PRIMARY KEY,
    content TEXT,
    embedding vector(1024),
    metadata JSONB
);
CREATE INDEX ON knowledge_chunks USING ivfflat (embedding vector_cosine_ops);
```

---

## 🔐 Security

- **InitData Verification**: HMAC-SHA256 with bot token
- **JWT**: Short-lived tokens (60 min default)
- **Database**: Encrypted at rest
- **Roles**: User / Partner / Admin / System
- **Logging**: Full audit trail

---

## 🧪 Testing

### Quick test (no Docker, no PostgreSQL):
```bash
cd aion_os/backend

# REST API (11 checks)
AION_TEST_MODE=1 python test_server.py

# WebSocket (9 checks)
AION_TEST_MODE=1 python test_websocket.py

# AI Agents with Groq (6 checks)
AION_TEST_MODE=1 OPENAI_API_KEY=gsk_... python test_agents_live.py

# ALL TESTS
AION_TEST_MODE=1 OPENAI_API_KEY=gsk_... python test_all.py
```

### Integration test (with Docker):
```bash
cd aion_os/docker
docker compose up -d
python healthcheck.py --wait --verbose
```

> ⚠️ **Important:** Before Docker deployment, remove `AION_TEST_MODE=1` from `.env`.
> This flag forces SQLite instead of PostgreSQL. If left in, the Docker containers
> will run with SQLite and the RAG engine (pgvector) won't work.

---

## 🔧 Configuration

### `.env` — all configuration in one file

| Variable | Default | Description |
|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | — | From @BotFather |
| `POSTGRES_PASSWORD` | `changeme` | Change in production |
| `JWT_SECRET_KEY` | `changeme` | Generate random 64+ chars |
| `LLM_DEFAULT_PROVIDER` | `deepseek` | `deepseek`, `qwen`, `llama`, `openai` |
| `OPENAI_API_KEY` | — | Groq key for free tier |
| `OPENAI_API_BASE` | `api.groq.com` | Change for other providers |
| `OPENAI_MODEL` | `llama-3.3-70b` | Model name |
| `AION_TEST_MODE` | `0` | `1` = SQLite (no PostgreSQL) |

---

## 📦 Dependencies

### Python (requirements.txt)
Key packages: fastapi, uvicorn, sqlalchemy[asyncio], aiosqlite, openai, httpx, websockets, python-jose, redis, aiofiles

### Docker Images
- `pgvector/pgvector:pg16` — PostgreSQL + vector support
- `redis:7-alpine` — Cache
- `nginx:alpine` — Reverse proxy
- `ollama/ollama:latest` — Local LLM (CPU profile)
- `prom/prometheus:latest` — Monitoring (opt-in)

---

## ⚡ Performance

| Endpoint | Avg Latency | Notes |
|----------|-------------|-------|
| `/health` | <5ms | No DB |
| `/categories` | <10ms | Static data |
| `/chat/text` (no AI) | 50-200ms | DB only |
| `/chat/text` (with Groq) | 1-3s | Depends on prompt size |
| WebSocket stream | 10-50ms/chunk | First chunk ~500ms |
| RAG search (pgvector) | 20-100ms | Depends on index size |

---

## 🚢 Deployment

### Production checklist:
1. ✅ Change all passwords in `.env`
2. ✅ Generate secure `JWT_SECRET_KEY` (64+ random chars)
3. ✅ Set up PostgreSQL with regular backups
4. ✅ Configure Redis persistence
5. ✅ Set up monitoring (Prometheus + Grafana)
6. ✅ Configure rate limiting
7. ✅ Set up HTTPS (TLS termination at nginx)
8. ✅ Run `healthcheck.py --wait` to verify

### Scaling:
- **API**: Horizontal scaling behind nginx (stateless)
- **Worker**: Add more replicas in docker-compose
- **PostgreSQL**: Read replicas for RAG queries
- **Redis**: Cluster mode for high availability

---

## 📞 Support

- **Issues**: Create GitHub issue in project repo
- **Documentation**: `/docs` and Swagger at `/docs`
- **Admin Panel**: `http://localhost:8080`

---

*Generated for the AION Tech Team. July 2026.*
