"""REST API endpoints for AION OS.

Chat, search, memory, partners, bookings, admin.
"""

from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.router import AgentContext, RouterAgent
from app.core.auth import TelegramUser, create_access_token, verify_telegram_init_data
from app.core.deps import get_current_user_id, get_db, verify_telegram_auth
from app.db.session import get_session
from app.llm.adapter import LLMAdapter
from app.memory.manager import MemoryManager
from app.memory.store import ConversationStore
from app.models.booking import Booking
from app.models.partner import Partner
from app.rag.engine import RAGEngine
from app.rag.ingestion import IngestionService
from app.voice.streaming import VoicePipeline

router = APIRouter(prefix="/api/v1")


# ─── Schemas ──────────────────────────────────────────────


class ChatRequest(BaseModel):
    message: str
    conversation_id: str = ""
    language: str = "ru"


class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    navigation: dict | None = None
    cards: list[dict] | None = None
    latency_ms: float = 0.0


class AuthRequest(BaseModel):
    init_data: str


class AuthResponse(BaseModel):
    token: str
    user: dict
    expires_in: int


class MemoryResponse(BaseModel):
    memories: list[dict[str, Any]]


class MemoryUpdateRequest(BaseModel):
    key: str
    value: str
    type: str = "preference"


class BookingCreate(BaseModel):
    category: str
    service_name: str
    description: str = ""
    preferred_date: str = ""
    preferred_time: str = ""
    partner_id: int = 0
    contact_name: str = ""
    contact_phone: str = ""


class PartnerSearchRequest(BaseModel):
    category: str = ""
    city: str = ""
    language: str = ""
    query: str = ""
    min_rating: float = 0.0


# ─── Auth ──────────────────────────────────────────────────


@router.post("/auth/telegram", response_model=AuthResponse)
async def auth_telegram(request: AuthRequest):
    """Authenticate via Telegram InitData and return JWT."""
    user = verify_telegram_init_data(request.init_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram InitData",
        )

    token = create_access_token({
        "user_id": user.id,
        "first_name": user.first_name,
        "username": user.username,
        "lang": user.language_code,
    })

    return AuthResponse(
        token=token,
        user=user.model_dump(),
        expires_in=3600,
    )


# ─── Chat ──────────────────────────────────────────────────


@router.post("/chat/text", response_model=ChatResponse)
async def chat_text(
    request: ChatRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Send a text message and get AI response via agent router."""
    start = time.monotonic()

    router_agent = RouterAgent()
    ctx = AgentContext(
        user_id=user_id,
        message=request.message,
        conversation_id=request.conversation_id or f"conv_{user_id}_{int(time.time())}",
        session=db,
        user_lang=request.language,
    )

    result = await router_agent.execute(ctx)

    return ChatResponse(
        response=result.response,
        conversation_id=ctx.conversation_id,
        navigation=result.navigation,
        cards=result.cards,
        latency_ms=(time.monotonic() - start) * 1000,
    )


# ─── Voice ─────────────────────────────────────────────────


@router.post("/chat/voice")
async def chat_voice(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id),
):
    """Process a voice message and return AI response."""
    audio_data = await file.read()
    pipeline = VoicePipeline()

    # Transcribe audio
    text = await pipeline.audio_to_text(
        audio_data.hex(),  # Simplified — real impl uses base64
    )

    # Send through chat pipeline
    router_agent = RouterAgent()
    ctx = AgentContext(
        user_id=user_id,
        message=text,
        conversation_id=f"voice_{user_id}_{int(time.time())}",
    )
    result = await router_agent.execute(ctx)

    return {
        "transcribed": text,
        "response": result.response,
        "navigation": result.navigation,
        "cards": result.cards,
    }


# ─── Memory ────────────────────────────────────────────────


@router.get("/memory/{user_id}", response_model=MemoryResponse)
async def get_memory(user_id: int):
    """Get stored memories for a user."""
    mgr = MemoryManager()
    memories = await mgr.retrieve(user_id)
    return MemoryResponse(memories=memories)


@router.put("/memory/{user_id}")
async def update_memory(user_id: int, request: MemoryUpdateRequest):
    """Store a memory value."""
    mgr = MemoryManager()
    await mgr._store_fact(user_id, {
        "key": request.key,
        "value": request.value,
        "type": request.type,
    })
    return {"status": "stored"}


@router.delete("/memory/{user_id}")
async def clear_memory(user_id: int, key: str | None = None):
    """Delete memories for a user."""
    mgr = MemoryManager()
    if key:
        deleted = await mgr.delete_key(user_id, key)
    else:
        deleted = await mgr.delete_all(user_id)
    return {"deleted": deleted > 0}


# ─── Categories ────────────────────────────────────────────


@router.get("/categories")
async def get_categories():
    """Get all service categories."""
    categories = [
        {"id": "real_estate", "name": "Недвижимость", "icon": "🏠"},
        {"id": "visas", "name": "Визы и документы", "icon": "📄"},
        {"id": "transport", "name": "Транспорт", "icon": "🚗"},
        {"id": "currency", "name": "Обмен валюты", "icon": "💳"},
        {"id": "health", "name": "Здоровье и медицина", "icon": "🏥"},
        {"id": "insurance", "name": "Страхование", "icon": "🛡️"},
        {"id": "food", "name": "Еда и доставка", "icon": "🍽️"},
        {"id": "cleaning", "name": "Клининг и дом", "icon": "🧹"},
        {"id": "beauty", "name": "Красота и SPA", "icon": "💆"},
        {"id": "kids", "name": "Дети и семья", "icon": "👶"},
        {"id": "pets", "name": "Услуги для животных", "icon": "🐶"},
        {"id": "tours", "name": "Экскурсии", "icon": "🌴"},
        {"id": "sports", "name": "Спорт", "icon": "🏋️"},
        {"id": "wellness", "name": "Душа и энергия", "icon": "🧘"},
        {"id": "photo", "name": "Фото и медиа", "icon": "📷"},
        {"id": "flowers", "name": "Цветы и подарки", "icon": "💐"},
        {"id": "events", "name": "Мероприятия", "icon": "🏆"},
        {"id": "education", "name": "Образование", "icon": "🎓"},
        {"id": "rental", "name": "Прокат", "icon": "🛵"},
        {"id": "emergency", "name": "Экстренная помощь", "icon": "🆘"},
        {"id": "repair", "name": "Ремонт", "icon": "🔧"},
        {"id": "finance", "name": "Финансы", "icon": "💰"},
        {"id": "shopping", "name": "Шопинг", "icon": "🛍️"},
    ]
    return {"categories": categories}


# ─── Partners ──────────────────────────────────────────────


@router.post("/partners/search")
async def search_partners(request: PartnerSearchRequest, db: AsyncSession = Depends(get_db)):
    """Search partners by criteria."""
    from sqlalchemy import select

    query = select(Partner).where(Partner.is_active == True)

    if request.category:
        query = query.where(Partner.category.ilike(f"%{request.category}%"))
    if request.city:
        query = query.where(Partner.city.ilike(f"%{request.city}%"))
    if request.min_rating > 0:
        query = query.where(Partner.rating >= request.min_rating)

    query = query.order_by(Partner.rating.desc()).limit(20)
    result = await db.execute(query)
    partners = result.scalars().all()

    return {
        "partners": [
            {
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "city": p.city,
                "rating": p.rating,
                "phone": p.phone,
                "description": p.description[:200],
            }
            for p in partners
        ],
        "total": len(partners),
    }


@router.get("/partners/{partner_id}")
async def get_partner(partner_id: int, db: AsyncSession = Depends(get_db)):
    """Get partner details."""
    from sqlalchemy import select

    result = await db.execute(select(Partner).where(Partner.id == partner_id))
    partner = result.scalar_one_or_none()

    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")

    return {
        "id": partner.id,
        "name": partner.name,
        "category": partner.category,
        "subcategory": partner.subcategory,
        "city": partner.city,
        "phone": partner.phone,
        "email": partner.email,
        "rating": partner.rating,
        "price_range": partner.price_range,
        "description": partner.description,
        "languages": partner.languages,
        "is_verified": partner.is_verified,
    }


# ─── Bookings ──────────────────────────────────────────────


@router.post("/bookings")
async def create_booking(
    request: BookingCreate,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Create a new booking."""
    booking = Booking(
        user_id=user_id,
        partner_id=request.partner_id,
        category=request.category,
        service_name=request.service_name,
        description=request.description,
        preferred_date=request.preferred_date,
        preferred_time=request.preferred_time,
        contact_name=request.contact_name,
        contact_phone=request.contact_phone,
    )
    db.add(booking)
    await db.commit()
    await db.refresh(booking)

    return {
        "booking_id": booking.id,
        "status": booking.status,
        "message": f"Бронирование #{booking.id} создано",
    }


@router.get("/bookings")
async def get_bookings(user_id: int = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)):
    """Get user's bookings."""
    from sqlalchemy import select

    result = await db.execute(
        select(Booking)
        .where(Booking.user_id == user_id)
        .order_by(Booking.created_at.desc())
        .limit(20)
    )
    bookings = result.scalars().all()

    return {
        "bookings": [
            {
                "id": b.id,
                "service_name": b.service_name,
                "category": b.category,
                "status": b.status,
                "created_at": b.created_at.isoformat(),
            }
            for b in bookings
        ]
    }


# ─── RAG / Knowledge Base ──────────────────────────────────


@router.post("/kb/search")
async def search_knowledge_base(
    query: str,
    category: str = "",
    db: AsyncSession = Depends(get_db),
):
    """Search the knowledge base."""
    rag = RAGEngine(db)
    results = await rag.search(query, category=category)

    return {
        "results": [r.to_dict() for r in results],
        "total": len(results),
    }


@router.post("/kb/ingest/file")
async def ingest_file(
    filepath: str,
    db: AsyncSession = Depends(get_db),
):
    """Ingest a file into the knowledge base."""
    service = IngestionService(db)
    count = await service.ingest_file(filepath)
    return {"ingested_chunks": count}


@router.post("/kb/ingest/directory")
async def ingest_directory(
    directory: str,
    db: AsyncSession = Depends(get_db),
):
    """Ingest all supported files from a directory."""
    service = IngestionService(db)
    results = await service.ingest_directory(directory)
    return {"ingested": results}


# ─── Admin ─────────────────────────────────────────────────


@router.get("/admin/health")
async def health_check():
    """System health check."""
    return {
        "status": "ok",
        "version": "0.1.0",
        "timestamp": time.time(),
    }


@router.get("/admin/stats")
async def admin_stats(db: AsyncSession = Depends(get_db)):
    """Get system statistics (admin)."""
    from sqlalchemy import func, select

    # Count users
    from app.models.user import User
    user_count = await db.scalar(select(func.count(User.id)))

    # Count bookings
    booking_count = await db.scalar(select(func.count(Booking.id)))

    # Count partners
    partner_count = await db.scalar(select(func.count(Partner.id)))

    return {
        "users": user_count or 0,
        "bookings": booking_count or 0,
        "partners": partner_count or 0,
        "timestamp": time.time(),
    }
