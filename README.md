# AION

**Platform for Russian-speaking expats, relocators, and nomads**

> One window to solve up to 90% of life tasks in a new country — without markups, language barriers, or searching through chats.

**Status:** Discovery (April–July 2026)
**Owner:** KB
**First Market:** Nha Trang, Vietnam

## Product

AION is a platform that helps Russian-speaking users:
- Find and order services (housing, visas, medical, transport, etc.)
- Get city guides and nearby places
- Connect with verified partners
- Earn through referral program (4 levels)
- Access emergency support

## Target Personas

| # | Persona | Budget | Priority Services (MVP) |
|---|---------|--------|------------------------|
| P1 | Relocant (family) | $2k+/mo | Housing, school, visa, bank, medical |
| P2 | Expat | $3k+/mo | Premium housing, lawyer, insurance |
| P3 | Digital Nomad | $1.5-2.5k/mo | Short-term housing, SIM, coworking |
| P4 | Entrepreneur | $5-20k/mo | Business registration, legal, office |
| P5 | Tourist 18-35 RU | $150-200/trip | Transfer, SIM, exchange, excursions |
| P6 | Winterer / Seasonal | $400-800/mo | Mid-term housing, daily life |

## Project Structure

```
AION/
├── docs/           # Документация — 314 файлов (ТЗ, стратегии, отчёты, метрики)
├── tools/          # Технические инструменты для разработки
│   ├── telegram-parser/   # Invite Machine (сервер + ноды)
│   ├── scrapers/          # Скрипты для сбора и генерации данных
│   ├── data/              # Сырые данные (JSON, контакты)
│   └── archive/           # Архив старых черновиков
├── README.md       # Этот файл
└── *.html          # Справочники и каталоги услуг по городам
```

## Документация (`docs/`)

314 файлов, включая:

**Стратегия и видение**
- AION — Полный обзор проекта
- AION — полная документация проекта
- Легенда проекта AION
- Brand Book AION
- ПЛАН РАЗВИТИЯ (5 ЛЕТ)

**Технические задания (24 категории услуг)**
- ТЗ — Визы и документы
- ТЗ — Недвижимость
- ТЗ — Транспорт
- ТЗ — Здоровье и медицина
- ТЗ — Еда и доставка
- ТЗ — Красота и SPA
- И ещё 18 категорий

**Метрики и аналитика**
- Метрики продукта AION (DAU, MAU, LTV, CAC, Revenue)
- $100k GMV — разбивка по категориям
- Еженедельные отчёты (июнь–июль 2026)

**Маркетинг и рост**
- TikTok — стратегия продвижения
- YouTube-канал AION — стратегия
- Контент-планы (еженедельные)
- Реферальная программа
- Партнёрские программы
- Стратегия AION Invite Machine — 12 месяцев

**База контактов (по городам)**
- Нячанг, Дананг, Паттайя, Пхукет, Бангкок
- Анталия, Стамбул, Кемер
- Дубай, Рас-эль-Хайма
- Тбилиси, Батуми, Ереван, Сухум
- И ещё 12+ городов

**Организация и HR**
- Оргструктура AION
- Операторская модель
- Вакансии
- Система мотивации

## Roadmap

- **Phase 0 (3 weeks):** MVP foundation — Auth, Catalog, Order Flow, Partner Onboarding
- **Phase 1 (3-6 months):** SEA expansion — Payments, AI triage, B2B affiliate, City Governor
- **Phase 2 (6-12 months):** Maturity — Subscriptions, Gamification, Native apps, White-label