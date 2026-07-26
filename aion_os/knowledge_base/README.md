# AION Knowledge Base

This directory contains the knowledge base for the AION RAG system.

## Structure

```
knowledge_base/
├── bible/           # Core knowledge documents
│   ├── world.md     # Geography, cities, countries info
│   ├── technology.md# Tech stack, architecture docs
│   ├── service.md   # Service descriptions, how-tos
│   ├── location.md  # Location-specific info
│   └── character.md # User personas, behavior patterns
├── faq/             # Frequently asked questions
│   ├── general.md
│   ├── partners.md
│   └── users.md
└── services/        # Service category descriptions
    ├── real_estate.md
    ├── medical.md
    ├── transport.md
    ├── visas.md
    ├── beauty.md
    └── ...
```

## Ingestion

To ingest all knowledge base content:

```bash
curl -X POST http://localhost:8000/api/v1/kb/ingest/directory \
  -H "Content-Type: application/json" \
  -d '{"directory": "/knowledge_base"}'
```

Or via admin panel: click "📥 Ingest KB".
