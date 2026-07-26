#!/usr/bin/env python3
"""Live AI Agent Test — sends a real query through the full agent pipeline.

Tests:
1. RouterAgent intent classification
2. Agent routing
3. RAG search in knowledge base
4. Partner search in database
5. Final response generation via Groq LLM

Usage:
    AION_TEST_MODE=1 python test_agents_live.py
"""

import asyncio
import json
import logging
import os
import sys
import time
import traceback

# Silent noisy logs
logging.disable(logging.CRITICAL)

os.environ["AION_TEST_MODE"] = "1"
sys.stdout.reconfigure(encoding="utf-8")

# ─── Configuration ─────────────────────────────────────────
# Use the Groq API key from api_config.json or env
GROQ_API_KEY = os.environ.get("OPENAI_API_KEY", "")

QUERY = "Найди стоматолога в Нячанге"

# ─── Helpers ───────────────────────────────────────────────


def print_header(text: str):
    print()
    print("=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_step(step: str, detail: str = ""):
    print(f"\n  [{step}] {detail}")


def print_json(label: str, data: dict | list):
    print(f"\n  {label}:")
    formatted = json.dumps(data, ensure_ascii=False, indent=2)
    for line in formatted.split("\n"):
        print(f"    {line}")


# ─── Seed Test Data ────────────────────────────────────────


async def seed_database():
    """Populate SQLite with test partners and knowledge base entries."""
    print_step("SEED", "Populating test database...")

    from app.db.session import async_session_factory
    from app.models.partner import Partner
    from app.models.user import User
    from app.models.booking import Booking
    from app.models.memory import UserMemory
    from app.models.agent import AgentLog

    async with async_session_factory() as session:
        # Clear existing test data
        for model in [UserMemory, AgentLog, Booking, Partner, User]:
            await session.execute(model.__table__.delete())

        # Create a test user
        test_user = User(
            id=123456789,
            telegram_id=123456789,
            first_name="Тест",
            last_name="Пользователь",
            username="test_user",
            language_code="ru",
        )
        session.add(test_user)

        # Add test partners — Dentists in Nha Trang
        partners = [
            Partner(
                name="Стоматология «Улыбка»",
                category="health",
                subcategory="dentist",
                phone="+84901234567",
                email="smile@dental.vn",
                address="123 Nguyễn Thiện Thuật, Nha Trang",
                city="Nha Trang",
                country="Vietnam",
                languages='["русский", "английский", "вьетнамский"]',
                rating=4.8,
                price_range="$$",
                description="Современная стоматологическая клиника с русскоговорящими врачами. "
                            "Лечение зубов, имплантация, отбеливание, виниры. "
                            "Работаем с 2019 года. Принимаем страховки.",
                tags='["стоматология", "зубы", "импланты", "отбеливание", "русский язык"]',
                latitude=12.238791,
                longitude=109.196749,
                is_active=True,
                is_verified=True,
            ),
            Partner(
                name="Dental Clinic Nha Trang",
                category="health",
                subcategory="dentist",
                phone="+84908765432",
                email="info@dentalnt.com",
                address="45 Trần Phú, Nha Trang",
                city="Nha Trang",
                country="Vietnam",
                languages='["английский", "вьетнамский"]',
                rating=4.5,
                price_range="$$$",
                description="International dental clinic. Professional dentists with European diplomas. "
                            "Full range of dental services. English-speaking staff.",
                tags='["dentist", "dental", "implants", "teeth whitening", "English"]',
                latitude=12.245678,
                longitude=109.192345,
                is_active=True,
                is_verified=True,
            ),
            Partner(
                name="Медицинский центр «Айболит»",
                category="health",
                subcategory="general",
                phone="+84909123456",
                email="aibolit@med.vn",
                address="78 Nguyễn Trãi, Nha Trang",
                city="Nha Trang",
                country="Vietnam",
                languages='["русский", "вьетнамский"]',
                rating=4.6,
                price_range="$$",
                description="Многопрофильный медицинский центр. Терапевт, стоматолог, лор, окулист. "
                            "Русскоговорящие врачи. Анализы, УЗИ, ЭКГ. "
                            "Работаем 24/7. Скорая помощь.",
                tags='["медицина", "стоматолог", "терапевт", "анализы", "русский язык", "24/7"]',
                latitude=12.235678,
                longitude=109.189012,
                is_active=True,
                is_verified=True,
            ),
        ]

        for p in partners:
            session.add(p)

        await session.commit()
        print(f"    Added {len(partners)} partners + 1 user to the database")


# ─── Test Agent Pipeline ───────────────────────────────────


async def test_agent_pipeline():
    """Execute the full agent pipeline with the test query."""
    print_header(f"🔬 AION AGENT PIPELINE TEST")
    print(f"  Query: \"{QUERY}\"")
    print(f"  LLM:   Groq (llama-3.3-70b-versatile)")
    print(f"  DB:    SQLite (test mode)")
    print()

    start_time = time.time()

    # 1. RouterAgent — Intent Classification
    print_step("1/5", "ROUTER AGENT — Intent Classification")
    from app.agents.router import RouterAgent, AgentContext

    router = RouterAgent()

    ctx = AgentContext(
        user_id=123456789,
        user_name="Тест",
        user_lang="ru",
        message=QUERY,
        conversation_id=f"test_live_{int(time.time())}",
    )

    # Manually classify intent first to show the step
    intent = await router._classify_intent(QUERY)
    print_json("Intent Classification", intent)

    # 2. Execute Router (which will route to the right agent)
    print_step("2/5", "ROUTER AGENT — Executing (routing to specialist)")
    result = await router.execute(ctx)

    # 3. Show result
    print_step("3/5", "RESULT")
    print(f"\n  Response ({len(result.response)} chars):")
    print(f"  {'─' * 40}")
    for line in result.response.split("\n"):
        if line.strip():
            print(f"  {line}")
    print(f"  {'─' * 40}")

    if result.navigation:
        print_json("Navigation Command", result.navigation)

    if result.cards:
        print(f"\n  Cards ({len(result.cards)}):")
        for i, card in enumerate(result.cards[:5]):
            print(f"    {i+1}. {card.get('title', '?')} — {card.get('description', '')[:80]}")

    # 4. Direct LLM call to show raw response
    print_step("4/5", "DIRECT LLM CALL (for comparison)")
    from app.llm.adapter import LLMAdapter

    llm = LLMAdapter()
    llm_response = await llm.chat([
        {"role": "system", "content": "Ты — AI-ассистент AION. "
         "Отвечай на русском языке. Если спрашивают про поиск — используй информацию из БД."},
        {"role": "user", "content": QUERY},
    ])
    print(f"\n  LLM Response ({llm_response.latency_ms:.0f}ms):")
    print(f"  Model: {llm_response.model}")
    print(f"  Usage: {llm_response.usage.get('total_tokens', '?')} tokens")
    print(f"  {'─' * 40}")
    for line in llm_response.content.split("\n"):
        if line.strip():
            print(f"  {line}")
    print(f"  {'─' * 40}")

    # 5. Try partner search directly
    print_step("5/5", "DIRECT PARTNER SEARCH (from database)")
    from app.db.session import async_session_factory
    from sqlalchemy import select
    from app.models.partner import Partner

    partners = []
    async with async_session_factory() as session:
        db_result = await session.execute(
            select(Partner).where(
                Partner.is_active == True,
                Partner.category.ilike("%health%"),
            ).order_by(Partner.rating.desc())
        )
        partners = db_result.scalars().all()
        print(f"\n  Found {len(partners)} health partners in database:")
        for p in partners:
            tags = json.loads(p.tags) if isinstance(p.tags, str) else []
            langs = json.loads(p.languages) if isinstance(p.languages, str) else []
            print(f"\n    🏪 {p.name}")
            print(f"       ⭐ {p.rating}/5 | 📍 {p.city} | 💰 {p.price_range}")
            print(f"       🗣️  {', '.join(langs)}")
            print(f"       🏷️  {', '.join(tags[:4])}")
            print(f"       📞 {p.phone}")
            print(f"       📝 {p.description[:120]}...")

    # Summary
    elapsed = time.time() - start_time
    print()
    print("=" * 60)
    print(f"  ✅ AGENT PIPELINE TEST COMPLETE ({elapsed:.1f}s)")
    print("=" * 60)
    print(f"  Query:     \"{QUERY}\"")
    print(f"  Intent:    {intent.get('intent', '?')} (confidence: {intent.get('confidence', 0):.0%})")
    print(f"  Response:  {len(result.response)} chars")
    print(f"  LLM Model: {llm_response.model}")
    print(f"  Partners:  {len(partners)} found in DB")
    print(f"  Time:      {elapsed:.1f}s")


async def main():
    print_header("🛠️  AION OS — Live Agent Test Setup")

    # Check Groq key
    if not GROQ_API_KEY:
        print("  ⚠️  OPENAI_API_KEY not set in environment")
        print("  Set: export OPENAI_API_KEY=your_groq_api_key_here")
        return

    print(f"  ✅ Groq API key configured: {GROQ_API_KEY[:15]}...")
    print(f"  Setting LLM provider to: openai (Groq)")

    # Set the provider
    os.environ["LLM_DEFAULT_PROVIDER"] = "openai"
    os.environ["OPENAI_API_BASE"] = "https://api.groq.com/openai/v1"
    os.environ["OPENAI_MODEL"] = "llama-3.3-70b-versatile"

    # Initialize DB tables
    from app.db.session import init_db
    await init_db()
    print("  ✅ Database tables created")

    # Seed DB
    await seed_database()

    # Run the test
    await test_agent_pipeline()

    # Cleanup test DB (ignore file lock errors on Windows)
    db_path = os.path.join(os.path.dirname(__file__), 'aion_test.db')
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except PermissionError:
            print(f"  ⚠️  Could not remove {os.path.basename(db_path)} (file locked)")


if __name__ == "__main__":
    asyncio.run(main())
