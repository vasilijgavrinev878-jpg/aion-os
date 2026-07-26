#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate real База исполнитель HTML files for all cities from research data."""

import os, json, sys

# ──────────────────────────────────────────────
# CSS + HTML TEMPLATES
# ──────────────────────────────────────────────

CSS = """<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>База исполнителей {city_ru} — AION</title>
<style>
  :root {{ --primary: #0A0F1E; --accent: #6366f1; --gold: #D4A853; --text: #1e293b; --text-light: #64748b; --bg: #ffffff; --bg-alt: #f8fafc; --border: #e2e8f0; --deep-blue: #0A1628; }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html {{ scroll-behavior: smooth; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; line-height: 1.6; color: var(--text); background: var(--bg); max-width: 1100px; margin: 0 auto; padding: 0; }}
  .cover {{ background: linear-gradient(135deg, var(--deep-blue) 0%, #1a2a4a 50%, var(--deep-blue) 100%); color: white; padding: 60px 40px 50px; text-align: center; position: relative; overflow: hidden; }}
  .cover::before {{ content: "\\221E"; position: absolute; font-size: 300px; opacity: 0.04; top: -60px; right: -40px; font-weight: 100; }}
  .cover::after {{ content: "AION"; position: absolute; font-size: 180px; opacity: 0.03; bottom: -40px; left: -20px; font-weight: 900; letter-spacing: 20px; }}
  .cover-label {{ font-size: 11px; letter-spacing: 6px; text-transform: uppercase; opacity: 0.5; margin-bottom: 16px; }}
  .cover h1 {{ font-size: 48px; font-weight: 800; letter-spacing: 4px; margin-bottom: 8px; }}
  .cover .subtitle {{ font-size: 16px; opacity: 0.75; font-weight: 300; letter-spacing: 2px; }}
  .cover .meta {{ margin-top: 28px; font-size: 12px; opacity: 0.4; letter-spacing: 1px; }}
  .nav {{ position: sticky; top: 0; z-index: 100; background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); border-bottom: 1px solid var(--border); padding: 8px 20px; display: flex; gap: 4px; flex-wrap: wrap; font-size: 12px; }}
  .nav a {{ color: var(--text-light); text-decoration: none; padding: 3px 10px; border-radius: 4px; transition: all 0.2s; white-space: nowrap; }}
  .nav a:hover {{ background: var(--bg-alt); color: var(--accent); }}
  .section {{ padding: 24px 32px 32px; border-bottom: 1px solid var(--border); }}
  .section:last-child {{ border-bottom: none; }}
  .section-header {{ display: flex; align-items: baseline; gap: 12px; margin-bottom: 20px; padding-bottom: 8px; border-bottom: 2px solid var(--accent); }}
  .section-header h2 {{ font-size: 20px; font-weight: 700; color: var(--deep-blue); }}
  .section-header .count {{ font-size: 13px; color: var(--text-light); font-weight: 400; }}
  .entry-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 10px; }}
  .entry {{ border: 1px solid var(--border); border-radius: 8px; padding: 12px 14px; background: var(--bg); transition: border-color 0.2s; }}
  .entry:hover {{ border-color: var(--accent); }}
  .entry .num {{ font-size: 10px; color: var(--accent); font-weight: 600; letter-spacing: 0.5px; }}
  .entry .contact {{ font-size: 14px; font-weight: 600; color: var(--deep-blue); margin: 1px 0 2px; }}
  .entry .contact a {{ color: var(--deep-blue); text-decoration: none; }}
  .entry .contact a:hover {{ color: var(--accent); text-decoration: underline; }}
  .entry .service {{ font-size: 13px; color: var(--text); line-height: 1.5; }}
  .entry .tags {{ display: flex; flex-wrap: wrap; gap: 4px; margin-top: 5px; }}
  .entry .tag {{ display: inline-block; padding: 1px 8px; border-radius: 8px; font-size: 10px; font-weight: 500; }}
  .tag-info {{ background: #eef2ff; color: #4338ca; }}
  @media (max-width: 640px) {{ .cover h1 {{ font-size: 28px; }} .section {{ padding: 16px 14px; }} .entry-grid {{ grid-template-columns: 1fr; }} .nav {{ padding: 6px 10px; gap: 2px; }} .nav a {{ font-size: 11px; padding: 2px 6px; }} }}
</style>
</head>
<body>

<div class="cover">
  <div class="cover-label">AION Partner Base</div>
  <h1>База исполнителей</h1>
  <div class="subtitle">{city_ru} — проверенные специалисты и услуги для русскоязычных</div>
  <div class="meta">AION · {total} контактов · 12 категорий</div>
</div>

<nav class="nav" id="nav">
  <a href="#beauty">Красота и уход</a>
  <a href="#fitness">Фитнес и спорт</a>
  <a href="#kids">Дети и развитие</a>
  <a href="#psychology">Психология и здоровье</a>
  <a href="#medicine">Медицина</a>
  <a href="#photo">Фото и видео</a>
  <a href="#rental">Аренда и транспорт</a>
  <a href="#tourism">Туризм и экскурсии</a>
  <a href="#food">Еда и продукты</a>
  <a href="#digital">Цифровые услуги</a>
  <a href="#realty">Недвижимость</a>
  <a href="#other">Прочее</a>
</nav>
"""

CAT_NAMES = {
    "beauty": "Красота и уход",
    "fitness": "Фитнес и спорт",
    "kids": "Дети и развитие",
    "psychology": "Психология и здоровье",
    "medicine": "Медицина",
    "photo": "Фото и видео",
    "rental": "Аренда и транспорт",
    "tourism": "Туризм и экскурсии",
    "food": "Еда и продукты",
    "digital": "Цифровые услуги",
    "realty": "Недвижимость",
    "other": "Прочее",
}

CAT_IDS = list(CAT_NAMES.keys())

def make_section(cat_id, entries, start_num):
    if not entries:
        return "", 0
    name = CAT_NAMES[cat_id]
    lines = []
    lines.append(f'<div class="section" id="{cat_id}">')
    lines.append(f'  <div class="section-header"><h2>{name}</h2><span class="count">{len(entries)} контактов</span></div>')
    lines.append(f'  <div class="entry-grid">')
    for i, e in enumerate(entries):
        num = start_num + i
        contact = e["contact"]
        service = e["service"]
        if contact.startswith("http"):
            link = contact
            label = contact.replace("https://", "").replace("http://", "").rstrip("/")
            if len(label) > 50:
                label = label[:50] + "…"
            contact_html = f'<a href="{contact}" target="_blank">{label}</a>'
        else:
            contact_html = contact
        lines.append(f'    <div class="entry">')
        lines.append(f'      <div class="num">#{num}</div>')
        lines.append(f'      <div class="contact">{contact_html}</div>')
        lines.append(f'      <div class="service">{service}</div>')
        lines.append(f'      <div class="tags"><span class="tag tag-info">{name}</span></div>')
        lines.append(f'    </div>')
    lines.append(f'  </div>')
    lines.append(f'</div>')
    return "\n".join(lines), len(entries)

def build_nav():
    return '\n'.join(f'  <a href="#{cid}">{CAT_NAMES[cid]}</a>' for cid in CAT_IDS)

def generate_file(city_ru, city_subtitle, all_entries):
    total = sum(len(v) for v in all_entries.values())
    html = CSS.format(city_ru=city_ru, total=total)
    # nav
    html += '<nav class="nav" id="nav">\n'
    html += build_nav() + '\n</nav>\n'
    # sections
    start = 1
    for cid in CAT_IDS:
        ents = all_entries.get(cid, [])
        sec, cnt = make_section(cid, ents, start)
        if sec:
            html += sec + "\n"
            start += cnt
    # any uncategorized - put in "other"
    html += '</body>\n</html>'
    return html

def save_file(filename, html):
    os.makedirs(os.path.dirname(filename) or ".", exist_ok=True)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"  ✓ {filename}")

# ──────────────────────────────────────────────
# CITY DATA
# ──────────────────────────────────────────────
# Each city: dict of category -> list of {"contact": str, "service": str}

CITIES = {}

# ══════════════ VIETNAM (NEW) ══════════════

CITIES["Вунгтау"] = {
    "beauty": [
        {"contact": "https://t.me/vungtau_chat", "service": "Главный чат Вунгтау — поиск мастеров красоты, парикмахеров, косметологов, маникюр"},
        {"contact": "https://t.me/+0UMhojq4mb5kMzcy", "service": "Чат TravelAsk Вунгтау — общение, поиск специалистов, вопросы"},
    ],
    "fitness": [],
    "kids": [],
    "psychology": [],
    "medicine": [
        {"contact": "+84 898 78 00 70", "service": "Хиропрактика и акупунктура, доктор Андрей"},
        {"contact": "Le Loi Hospital — 22 Le Loi Str.", "service": "Главная больница Вунгтау"},
        {"contact": "International SOS — 1 Le Ngoc Han, тел: 064 3858 776", "service": "Международная клиника, круглосуточно"},
        {"contact": "VietSovPetro Hospital — Pasteur 2, тел: 064 3857 017", "service": "Больница Вьетсовпетро"},
        {"contact": "Medicoast Hospital — 165 Thuy Van, тел: +84 64 352 1183", "service": "Медицинский центр"},
    ],
    "photo": [],
    "rental": [
        {"contact": "https://t.me/vietnam_rent", "service": "Аренда жилья по всему Вьетнаму"},
    ],
    "tourism": [
        {"contact": "https://vungtau.expert", "service": "Путеводитель по Вунгтау на русском — места, услуги, чаты"},
    ],
    "food": [],
    "digital": [],
    "realty": [
        {"contact": "https://t.me/vietnam_rent", "service": "Аренда жилья во Вьетнаме"},
        {"contact": "https://searche.ru/vungtau/", "service": "Доска объявлений о продаже недвижимости"},
    ],
    "other": [
        {"contact": "https://vn.rutumba.com", "service": "Доска объявлений во Вьетнаме на русском"},
        {"contact": "https://t.me/tele_360chat", "service": "Все чаты по 140+ странам мира"},
    ],
}

CITIES["Дананг"] = {
    "beauty": [
        {"contact": "https://ru.gurutto-vietnam.com/beauty/", "service": "Рейтинг салонов красоты, массажа, спа в Дананге"},
        {"contact": "https://t.me/danang_woman", "service": "Женский чат Дананг — искать мастеров маникюра, косметологов, парикмахеров"},
        {"contact": "https://t.me/danang_forum", "service": "Форум Дананг — поиск любых специалистов"},
    ],
    "fitness": [],
    "kids": [
        {"contact": "https://t.me/danang_woman", "service": "Обсуждение детских садов, школ, нянь"},
        {"contact": "https://t.me/danang_forum", "service": "Международные школы Дананга — отзывы"},
    ],
    "psychology": [],
    "medicine": [
        {"contact": "https://t.me/danang_forum", "service": "Поиск врачей, больниц, стоматологий через форум"},
        {"contact": "https://t.me/rus_danang", "service": "Русский Дананг — рекомендации по медицине"},
    ],
    "photo": [
        {"contact": "https://t.me/danang_forum", "service": "Поиск фотографов и видеографов в Дананге"},
    ],
    "rental": [
        {"contact": "https://t.me/vietnam_rent", "service": "Аренда жилья по всему Вьетнаму"},
        {"contact": "http://ru-logistic.ru/vietnam/danang-rulogistic/", "service": "Трансфер, аренда, отправка грузов в Россию"},
        {"contact": "https://t.me/RULOGISTIC_DANANG_CDEK", "service": "Заказ доставки CDEK из Дананга"},
    ],
    "tourism": [
        {"contact": "https://t.me/danang_afisha", "service": "Афиша Дананг — мероприятия, экскурсии"},
        {"contact": "https://t.me/visarunDanang", "service": "Виза Ран Дананг-Лаос"},
        {"contact": "https://needguide.ru/view_guide.php?user_id=16992", "service": "Гид-экскурсовод Дмитрий Шило по Данангу, Хойану, Хюэ"},
    ],
    "food": [
        {"contact": "https://t.me/danang_food", "service": "Кафе и рестораны Дананга, отзывы"},
        {"contact": "https://t.me/foodwithlovevn", "service": "Русская кухня: лагман, чебуреки, пельмени, борщ"},
    ],
    "digital": [
        {"contact": "https://t.me/it_danang", "service": "Чат IT-специалистов Дананга"},
    ],
    "realty": [
        {"contact": "https://t.me/vietnam_rent", "service": "Аренда жилья по всему Вьетнаму"},
    ],
    "other": [
        {"contact": "https://t.me/Danang_Viet", "service": "Главный чат Дананг (38 364 участника)"},
        {"contact": "https://t.me/danang_forum", "service": "Форум Дананг (11 779 участников)"},
        {"contact": "https://t.me/danang_mart", "service": "Барахолка Дананг"},
        {"contact": "https://t.me/it_danang", "service": "Чат айтишников Дананга"},
        {"contact": "https://t.me/rusconsdanang", "service": "Генконсульство России в Дананге"},
        {"contact": "https://letfind.me/faq/it-danang/", "service": "FAQ айтишников Дананга — жильё, симки, обмен валют"},
        {"contact": "https://t.me/@VietChangeBot", "service": "Обмен валют с доставкой"},
        {"contact": "https://t.me/biblioteka_danang", "service": "Библиотека Дананг — продажа/обмен книг"},
        {"contact": "https://t.me/vietnam_job", "service": "Работа во Вьетнаме"},
    ],
}

CITIES["Муйне"] = {
    "beauty": [
        {"contact": "https://t.me/muine_woman", "service": "Женский чат Муйне — поиск бьюти-мастеров"},
        {"contact": "https://t.me/muine", "service": "Главный чат Муйне (6 685 участников) — объявления мастеров"},
    ],
    "fitness": [
        {"contact": "SURF4YOU — школа виндсерфинга в Муйне", "service": "Виндсерфинг, кайтсёрфинг, сапсёрфинг, обучение"},
    ],
    "kids": [],
    "psychology": [],
    "medicine": [],
    "photo": [],
    "rental": [
        {"contact": "https://t.me/muine_house", "service": "Аренда жилья в Муйне (999 участников)"},
        {"contact": "https://t.me/muinebikes", "service": "Аренда байков в Муйне"},
    ],
    "tourism": [
        {"contact": "https://t.me/muine_guide", "service": "Экскурсии и трансферы в Муйне"},
        {"contact": "https://t.me/muine_afisha", "service": "Афиша Муйне — мероприятия, туры"},
        {"contact": "https://muine.info", "service": "Путеводитель по Муйне на русском"},
    ],
    "food": [
        {"contact": "https://t.me/food_muine", "service": "Кафе и рестораны Муйне (785 участников)"},
        {"contact": "https://t.me/muine_delivery", "service": "Отзывы о ресторанах (1 010 участников)"},
    ],
    "digital": [],
    "realty": [
        {"contact": "https://t.me/muine_house", "service": "Аренда жилья в Муйне"},
        {"contact": "https://t.me/vietnam_rent", "service": "Аренда жилья по всему Вьетнаму"},
    ],
    "other": [
        {"contact": "https://t.me/muine", "service": "Главный чат Муйне (6 685 участников)"},
        {"contact": "https://t.me/muine_faq", "service": "Муйне Инфо (1 513 подписчиков)"},
        {"contact": "https://t.me/forum_muine", "service": "Муйне чат форум (1 080 участников)"},
        {"contact": "https://t.me/muine_woman", "service": "Женский чат Муйне"},
    ],
}

CITIES["Фукуок"] = {
    "beauty": [
        {"contact": "https://t.me/fukokchat", "service": "Главный чат Фукуока — поиск бьюти-мастеров, косметологов"},
        {"contact": "https://t.me/forum_phuquoc", "service": "Форум Фукуок (1 850 участников) — услуги красоты"},
    ],
    "fitness": [],
    "kids": [],
    "psychology": [],
    "medicine": [
        {"contact": "+84 77 808 00 77 (Марина)", "service": "Юридическая поддержка, медстраховка, помощь с Вьетнамом"},
    ],
    "photo": [],
    "rental": [
        {"contact": "https://t.me/vietnam_rent", "service": "Аренда жилья по всему Вьетнаму"},
    ],
    "tourism": [
        {"contact": "+7 953 515 30 14", "service": "Русский гид на Фукуоке"},
        {"contact": "+7 963 054 07 39", "service": "Экскурсии на Фукуоке на русском языке"},
        {"contact": "https://phuquoc24.ru", "service": "Путеводитель по Фукуоку на русском"},
        {"contact": "https://phuquoclife.ru", "service": "Фукуок лайф — всё об острове на русском"},
        {"contact": "https://phuquocinside.com", "service": "Фукуок инсайд — гид по острову"},
    ],
    "food": [],
    "digital": [],
    "realty": [
        {"contact": "https://t.me/vietnam_rent", "service": "Аренда жилья по всему Вьетнаму"},
    ],
    "other": [
        {"contact": "https://t.me/fukokchat", "service": "Главный чат Фукуока"},
        {"contact": "https://t.me/forum_phuquoc", "service": "Форум Фукуок (1 850 участников)"},
        {"contact": "https://t.me/chat_Vietnam_ru", "service": "Главный чат Вьетнама (58 313 участников)"},
        {"contact": "https://t.me/vietnam_viza", "service": "Визы во Вьетнам — оформление"},
        {"contact": "https://t.me/vietnam_woman", "service": "Женский чат Вьетнама"},
        {"contact": "https://vn.rutumba.com", "service": "Доска объявлений во Вьетнаме на русском"},
    ],
}

CITIES["Ханой"] = {
    "beauty": [
        {"contact": "https://t.me/Hanoi_Viet", "service": "Главный чат Ханоя (7 701 участник) — поиск мастеров"},
        {"contact": "+84 353 299 484", "service": "EverBeauty студия — косметология, уход за лицом"},
    ],
    "fitness": [],
    "kids": [],
    "psychology": [],
    "medicine": [
        {"contact": "Vietmed — акупунктура в Ханое", "service": "Акупунктура, восточная медицина"},
    ],
    "photo": [],
    "rental": [],
    "tourism": [
        {"contact": "+84 33 326 7771 (Толя/Тхо)", "service": "Русский гид в Ханое"},
        {"contact": "https://needguide.ru", "service": "Каталог гидов и экскурсоводов Ханоя на русском"},
        {"contact": "https://t.me/hanoi_forum", "service": "Форум Ханоя — экскурсии, маршруты"},
    ],
    "food": [
        {"contact": "https://t.me/Hanoi_Viet", "service": "Поиск русских продуктов, доставки еды через чат"},
    ],
    "digital": [],
    "realty": [
        {"contact": "https://t.me/vietnam_rent", "service": "Аренда жилья по всему Вьетнаму"},
    ],
    "other": [
        {"contact": "https://t.me/Hanoi_Viet", "service": "Главный чат Ханоя (7 701 участник)"},
        {"contact": "https://t.me/hanoi_forum", "service": "Форум Ханоя"},
        {"contact": "https://t.me/chat_Vietnam_ru", "service": "Главный чат Вьетнама (58 313 участников)"},
        {"contact": "https://t.me/vietnam_job", "service": "Работа во Вьетнаме"},
        {"contact": "https://t.me/vietnam_viza", "service": "Визы во Вьетнам"},
        {"contact": "https://t.me/vietnam_woman", "service": "Женский чат Вьетнама"},
    ],
}

CITIES["Хошимин"] = {
    "beauty": [
        {"contact": "https://ru.gurutto-vietnam.com/beauty/", "service": "Рейтинг спа/салонов красоты Хошимина на русском"},
        {"contact": "https://t.me/HoChiMinh_Saigon", "service": "Главный чат Хошимина (7 281 участник) — поиск мастеров"},
        {"contact": "https://t.me/hochiminh_chat", "service": "Чат Хошимина (5 047 участников) — услуги, специалисты"},
    ],
    "fitness": [],
    "kids": [],
    "psychology": [],
    "medicine": [],
    "photo": [],
    "rental": [
        {"contact": "https://t.me/hcmc_arenda", "service": "Аренда жилья в Хошимине"},
        {"contact": "https://t.me/ArendaHCMC", "service": "Аренда квартир и домов в Хошимине"},
    ],
    "tourism": [
        {"contact": "https://t.me/hochiminhguide", "service": "Гиды и экскурсии в Хошимине"},
        {"contact": "https://t.me/HoChiMinh_Saigon", "service": "Обсуждение туров, достопримечательностей"},
    ],
    "food": [
        {"contact": "https://t.me/HoChiMinh_Saigon", "service": "Поиск русских продуктов, доставки еды через чат"},
    ],
    "digital": [],
    "realty": [
        {"contact": "https://t.me/hcmc_arenda", "service": "Аренда жилья в Хошимине"},
        {"contact": "https://t.me/ArendaHCMC", "service": "Аренда квартир и домов"},
        {"contact": "https://t.me/vietnam_rent", "service": "Аренда жилья по всему Вьетнаму"},
    ],
    "other": [
        {"contact": "https://t.me/HoChiMinh_Saigon", "service": "Главный чат Хошимина (7 281 участник)"},
        {"contact": "https://t.me/hochiminh_chat", "service": "Чат Хошимина (5 047 участников)"},
        {"contact": "https://t.me/chat_Vietnam_ru", "service": "Главный чат Вьетнама (58 313 участников)"},
        {"contact": "https://t.me/vietnam_job", "service": "Работа во Вьетнаме"},
        {"contact": "https://t.me/vietnam_viza", "service": "Визы во Вьетнам"},
        {"contact": "https://t.me/vietnam_woman", "service": "Женский чат Вьетнама"},
        {"contact": "https://t.me/vietnam_rent", "service": "Аренда жилья"},
        {"contact": "https://t.me/diaspora_chat", "service": "Чат DIASPORA — русскоязычные по всему миру"},
        {"contact": "https://t.me/expatfm_chat", "service": "ExpatFM чат — экспаты Вьетнама"},
    ],
}

# ══════════════ TURKEY ══════════════

CITIES["Анталия"] = {
    "beauty": [
        {"contact": "https://t.me/Beauty_Chat_Antalya", "service": "Бьюти ЧАТ Анталия — маникюр, педикюр, ресницы, брови, шугаринг, парикмахер"},
        {"contact": "https://t.me/nail_masters_antalya", "service": "Мастера маникюра в Анталии — профессиональный чат"},
        {"contact": "https://t.me/antaliya_alaniya", "service": "Анталия | Услуги красоты — все услуги"},
        {"contact": "https://t.me/masteriklientantalya", "service": "Мастер и клиент Анталия — поиск мастеров и клиентов"},
        {"contact": "https://t.me/krasota_antalya", "service": "Услуги красоты Анталия — макияж, ресницы, брови, уход"},
        {"contact": "https://www.instagram.com/beauty_art_lara/", "service": "Beauty Art Lara — салон: ногти, ресницы, волосы, косметолог, лазер"},
    ],
    "fitness": [
        {"contact": "https://www.instagram.com/anna.fitness.antalya/", "service": "Фитнес-тренер Анна — групповые и персональные тренировки Antalya Lara"},
    ],
    "kids": [
        {"contact": "https://t.me/moms_relocants", "service": "Сады и школы в Анталии ЧАТ — детские сады, школы"},
        {"contact": "https://t.me/anaokulu_reviews", "service": "Детские сады и школы Анталии ОТЗЫВЫ"},
        {"contact": "https://rusokulu.ru/", "service": "Международная Русская школа в Анталии"},
        {"contact": "https://t.me/nynyadlydetei", "service": "Чат няни для детей — поиск нянь и семей"},
    ],
    "psychology": [
        {"contact": "https://t.me/psyhelpon", "service": "Психологическая помощь онлайн из Турции"},
    ],
    "medicine": [
        {"contact": "https://t.me/vrachi_antalya", "service": "Врачи Анталии — медицина, больницы, клиники"},
        {"contact": "https://t.me/medantalya", "service": "Медицина Анталья — врачи, клиники"},
        {"contact": "https://www.antalyavrach.com/", "service": "Русскоязычные врачи в Анталии, Кемере, Белеке, Сиде"},
        {"contact": "https://t.me/tyrciya_medicina", "service": "Турция медицина (все города) — 7 000+ участников"},
    ],
    "photo": [
        {"contact": "https://t.me/masteriklientantalya", "service": "Поиск фотографов и видеооператоров через чат мастеров"},
    ],
    "rental": [
        {"contact": "https://t.me/antalyatransfer1", "service": "Трансфер Анталья-Аланья-Стамбул"},
        {"contact": "https://t.me/ant_sale", "service": "Барахолка Анталья-Кемер-Белек — аренда, товары, услуги"},
        {"contact": "https://t.me/arenda_antalya", "service": "Аренда квартир/вилл Анталия Кемер (7 500+ участников)"},
        {"contact": "https://antalyada.ru/rentacar", "service": "Прокат авто в Анталии — antalyada.ru"},
    ],
    "tourism": [
        {"contact": "https://ekskursii-antalya.ru/", "service": "500+ экскурсий в Анталье на русском языке"},
        {"contact": "https://www.sputnik8.com/ru/antalya", "service": "Экскурсии по Анталье на русском — Sputnik8"},
        {"contact": "https://easy-travel-club.com/antalya", "service": "Групповые туры с русскими гидами"},
    ],
    "food": [],
    "digital": [
        {"contact": "https://t.me/biznesdvigturkey", "service": "Бизнес чат Турция — IT, SMM, цифровые услуги"},
    ],
    "realty": [
        {"contact": "https://t.me/globe_nedvizhkaantalya", "service": "Недвижимость Анталия — аренда/продажа (7 500+ участников)"},
        {"contact": "https://t.me/antalia_nedvijka", "service": "Анталия | НЕДВИЖИМОСТЬ — аренда/продажа"},
        {"contact": "https://t.me/Antalya_realestates", "service": "Турция недвижимость — Анталия, Алания, Сиде, Кемер"},
    ],
    "other": [
        {"contact": "https://t.me/antalyadaa", "service": "Анталия главный канал города (7 270+ подписчиков)"},
        {"contact": "https://t.me/russiansinturkey_antalya", "service": "Русские в Анталии (ExpatFM) — 26 300+ участников"},
        {"contact": "https://t.me/antalya_online", "service": "Общий чат по Анталии"},
        {"contact": "https://t.me/billboard_antalya", "service": "Анталия: объявления, работа, барахолка"},
        {"contact": "https://antalyada.ru", "service": "AntalyaDa.ru — портал о жизни в Анталии"},
        {"contact": "https://www.facebook.com/groups/412389343635656/", "service": "Услуги Русских в Анталии (FB группа)"},
    ],
}

CITIES["Стамбул"] = {
    "beauty": [
        {"contact": "https://t.me/istanbul_guzellik", "service": "Бьюти чат Стамбул — салоны красоты, SPA"},
        {"contact": "https://t.me/guzellik_merkezi", "service": "Эстетика и косметология Стамбул"},
        {"contact": "https://t.me/istanbul_ru", "service": "Поиск бьюти-мастеров через главный чат"},
    ],
    "fitness": [],
    "kids": [
        {"contact": "https://t.me/istanbul_ru", "service": "Поиск нянь, репетиторов, школ через главный чат"},
    ],
    "psychology": [],
    "medicine": [
        {"contact": "https://t.me/tyrciya_medicina", "service": "Медицина Турции — подбор клиник в Стамбуле, 7 000+ участников"},
        {"contact": "https://t.me/istanbul_ru", "service": "Поиск врачей и клиник через главный чат"},
    ],
    "photo": [],
    "rental": [
        {"contact": "https://t.me/istanbul_rent", "service": "Аренда жилья в Стамбуле"},
        {"contact": "https://t.me/istanbul_ru", "service": "Трансферы, аренда авто — поиск в чате"},
    ],
    "tourism": [
        {"contact": "https://ekskursii-antalya.ru/", "service": "Экскурсии в Стамбуле на русском"},
        {"contact": "https://www.sputnik8.com/ru/stambul", "service": "Экскурсии по Стамбулу на русском"},
    ],
    "food": [],
    "digital": [
        {"contact": "https://t.me/biznesdvigturkey", "service": "Бизнес чат Турция — IT, SMM, разработка"},
    ],
    "realty": [
        {"contact": "https://t.me/istanbul_rent", "service": "Аренда жилья в Стамбуле"},
        {"contact": "https://t.me/turcia_arenda", "service": "Турция аренда недвижимости — Стамбул, Анталья, Аланья"},
    ],
    "other": [
        {"contact": "https://t.me/istanbul_ru", "service": "Стамбул чат — форум Турция (12 400+ участников)"},
        {"contact": "https://t.me/russiansinturkey_stambul", "service": "Русские в Стамбуле (ExpatFM) — 25 000+ участников"},
        {"contact": "https://t.me/ruskievstambule", "service": "Русские в Стамбуле — помощь, общение"},
        {"contact": "https://t.me/stambul_biznes", "service": "Бизнес чат Стамбула"},
        {"contact": "https://t.me/stambyl_nedvijka", "service": "Недвижимость Стамбула"},
    ],
}

CITIES["Кемер"] = {
    "beauty": [
        {"contact": "https://t.me/kemerchat", "service": "Чат Кемер — поиск бьюти-мастеров, косметологов, парикмахеров"},
    ],
    "fitness": [],
    "kids": [],
    "psychology": [],
    "medicine": [
        {"contact": "https://www.antalyavrach.com/", "service": "Русскоязычные врачи в Кемере, Белеке, Сиде"},
        {"contact": "https://t.me/tyrciya_medicina", "service": "Медицина Турции — подбор клиник в Кемере"},
    ],
    "photo": [],
    "rental": [
        {"contact": "https://t.me/ant_sale", "service": "Барахолка Анталья-Кемер-Белек"},
        {"contact": "https://t.me/arenda_antalya", "service": "Аренда квартир/вилл Анталия Кемер"},
    ],
    "tourism": [
        {"contact": "https://ekskursii-antalya.ru/", "service": "Экскурсии из Кемера на русском"},
        {"contact": "https://www.sputnik8.com/ru/kemer", "service": "Экскурсии по Кемеру"},
    ],
    "food": [],
    "digital": [],
    "realty": [
        {"contact": "https://t.me/Antalya_realestates", "service": "Недвижимость — Кемер, Анталия, Алания"},
        {"contact": "https://t.me/arenda_antalya", "service": "Аренда квартир/вилл Кемер"},
    ],
    "other": [
        {"contact": "https://t.me/kemerchat", "service": "Главный чат Кемера"},
        {"contact": "https://antalyada.ru", "service": "AntalyaDa.ru — гид по Анталии и Кемеру"},
    ],
}

# ══════════════ THAILAND ══════════════

CITIES["Паттайя"] = {
    "beauty": [
        {"contact": "https://t.me/pattaya_beauty_service", "service": "Бьюти услуги Паттайя — маникюр, педикюр, парикмахер, косметолог"},
        {"contact": "https://t.me/pattaya_beauty", "service": "Паттайя Бангкок Бьюти услуги — наращивание, лазерная эпиляция"},
        {"contact": "https://t.me/pattaya_beauty_services", "service": "Бьюти Паттайя — маникюр, парикмахер, косметолог, тату"},
        {"contact": "https://t.me/cosy_pattaya", "service": "Паттайя ногтевой сервис, брови, ресницы, косметология"},
    ],
    "fitness": [
        {"contact": "https://t.me/sportpattaya", "service": "Спортивная Паттайя — фитнес, кроссфит, йога, тренеры"},
    ],
    "kids": [
        {"contact": "https://t.me/kids_pattaya", "service": "Паттайя с детьми — сады, школы, репетиторы, няни, врачи"},
    ],
    "psychology": [
        {"contact": "https://t.me/live_spirit_for_you", "service": "Live Spirit — психолог, работа с тревогой и страхами"},
    ],
    "medicine": [
        {"contact": "https://t.me/thai_medicine", "service": "Медицина в Таиланде — врачи, больницы, страховки"},
        {"contact": "https://t.me/thai_med", "service": "Аптечка Таиланд — лекарства, аптеки"},
        {"contact": "https://t.me/thailand_med", "service": "Клиники, стоматология, диагностика в Паттайе"},
    ],
    "photo": [
        {"contact": "https://t.me/pattaya_connect", "service": "Поиск фотографов и видеографов через общий чат"},
    ],
    "rental": [
        {"contact": "https://t.me/pattaya_arenda", "service": "Аренда авто/мототехники в Паттайе"},
        {"contact": "https://t.me/pattayamoto", "service": "Паттайя Авто Мото №1 — аренда и продажа"},
        {"contact": "https://t.me/pattaya_arendaa", "service": "Паттайя: аренда недвижимости"},
        {"contact": "https://t.me/Thailand_ATP1", "service": "Таиланд Авто Мото Транспорт"},
    ],
    "tourism": [
        {"contact": "https://t.me/uslugi_pattaya", "service": "УСЛУГИ ПАТТАЙЯ — экскурсии, билеты, трансферы"},
        {"contact": "https://t.me/sabai_pattaya", "service": "Сабай Паттайя — визовые услуги, визараны, DTV, ED visa"},
        {"contact": "https://t.me/pattaya_tour", "service": "Паттайя Экскурсии Трансферы"},
    ],
    "food": [
        {"contact": "https://t.me/pattaya_food", "service": "Еда в Паттайе — кафе, рестораны, доставка"},
    ],
    "digital": [
        {"contact": "https://t.me/it_pattaya", "service": "IT-чат Паттайи — разработка, SMM, дизайн"},
    ],
    "realty": [
        {"contact": "https://t.me/pattaya_arendaa", "service": "Паттайя: аренда недвижимости"},
        {"contact": "https://t.me/pattaia_obmenik", "service": "Чат Паттайя Аренда — квартиры, кондо"},
    ],
    "other": [
        {"contact": "https://t.me/pattaya_chat", "service": "Главный чат Паттайи"},
        {"contact": "https://t.me/pattaya_connect", "service": "Паттайя Connect — общение, услуги"},
        {"contact": "https://t.me/baraholka_pattaya", "service": "Барахолка Паттайя"},
        {"contact": "https://t.me/pattaya_ru", "service": "Русские в Паттайе"},
    ],
}

CITIES["Пхукет"] = {
    "beauty": [
        {"contact": "https://t.me/phuket_beauty", "service": "Бьюти услуги Пхукет — маникюр, косметолог, парикмахер"},
        {"contact": "https://t.me/phuket_wellness", "service": "Веллис Пхукет — SPA, массаж, уход"},
    ],
    "fitness": [
        {"contact": "https://t.me/phuket_sport", "service": "Спорт на Пхукете — фитнес, йога, тренеры"},
    ],
    "kids": [
        {"contact": "https://t.me/phuket_kids", "service": "Пхукет с детьми — школы, сады, няни"},
    ],
    "psychology": [],
    "medicine": [
        {"contact": "https://t.me/thai_medicine", "service": "Медицина в Таиланде — врачи, больницы"},
        {"contact": "https://t.me/thailand_med", "service": "Клиники, стоматология на Пхукете"},
    ],
    "photo": [
        {"contact": "https://t.me/phuket_photo", "service": "Фотографы на Пхукете"},
    ],
    "rental": [
        {"contact": "https://t.me/phuket_rental", "service": "Аренда авто/байков на Пхукете"},
        {"contact": "https://t.me/Thailand_ATP1", "service": "Таиланд Авто Мото Транспорт"},
    ],
    "tourism": [
        {"contact": "https://t.me/phuket_tour", "service": "Экскурсии на Пхукете"},
        {"contact": "https://t.me/phuket_visa", "service": "Визовые услуги на Пхукете"},
        {"contact": "https://t.me/phuket", "service": "Главный чат Пхукета (15 000+ участников)"},
    ],
    "food": [
        {"contact": "https://t.me/phuket_food", "service": "Еда на Пхукете — кафе, рестораны, доставка"},
    ],
    "digital": [
        {"contact": "https://t.me/phuket_it", "service": "IT-чат Пхукета — разработка, SMM"},
    ],
    "realty": [
        {"contact": "https://t.me/phuket_rental", "service": "Аренда жилья на Пхукете"},
    ],
    "other": [
        {"contact": "https://t.me/phuket", "service": "Главный чат Пхукета (15 000+ участников)"},
        {"contact": "https://t.me/russians_on_phuket", "service": "Русские на Пхукете (16 000+ участников)"},
        {"contact": "https://t.me/phuketads", "service": "Phuket Ads — объявления (17 000+)"},
        {"contact": "https://t.me/PhuketBuySell", "service": "Phuket Buy & Sell (19 000+)"},
        {"contact": "http://rusdiaspora.com/countries/thailand/107-russian-telegram-channels-phuket", "service": "Полный каталог 107 русских каналов Пхукета"},
        {"contact": "https://t.me/phuket_chat", "service": "Общий чат Пхукета"},
    ],
}

# ══════════════ GEORGIA / ARMENIA ══════════════

CITIES["Батуми"] = {
    "beauty": [
        {"contact": "https://t.me/Enigma_Batumi", "service": "ENIGMA beauty salon — студия маникюра и педикюра, ул. Такаишвили 71"},
        {"contact": "https://heavennails.ge/", "service": "HEAVEN Beauty Studio — ногтевой сервис, макияж, брови, ресницы"},
        {"contact": "https://t.me/batumi_beauty", "service": "Батуми БЬЮТИ канал — 2 100+ подписчиков, услуги красоты"},
        {"contact": "https://t.me/bb_baraholka", "service": "Бьюти БАРАХОЛКА Батуми — продажа, аренда, вакансии, модели (2 368 уч.)"},
        {"contact": "https://dikidi.net/ru/profile/almond_1771591", "service": "Almond Batumi — студия маникюра, центр города"},
        {"contact": "https://t.me/beautyexpert_batumi", "service": "Эстетика Совершенства Батуми — профессиональный косметолог-эстетист"},
    ],
    "fitness": [
        {"contact": "https://t.me/Batumi_stretching", "service": "BATUMI STRETCHING PRO FITNESS — студия фитнеса, растяжки и танцев"},
        {"contact": "https://t.me/silabatumi", "service": "ЙОГА БАТУМИ «Место Силы» — йога, фитнес, танцы"},
        {"contact": "https://t.me/ombatumi", "service": "Om Batumi — духовные практики, йога, цигун, медитации"},
    ],
    "kids": [
        {"contact": "https://t.me/Georgia_with_kids", "service": "В Грузии с детьми — Telegram-канал, 4 300 подписчиков"},
        {"contact": "https://www.facebook.com/groups/georgiawithkids/", "service": "FB группа «В Грузии с детьми» (10 200 участников)"},
    ],
    "psychology": [
        {"contact": "https://t.me/ombatumi", "service": "Психология, саморазвитие, эзотерика — мероприятия в Батуми"},
    ],
    "medicine": [],
    "photo": [],
    "rental": [
        {"contact": "https://t.me/ads_ge", "service": "Трансфер Тбилиси-Батуми-Ереван"},
        {"contact": "https://t.me/BatumiOffer", "service": "БАРАХОЛКА Батуми — услуги, аренда (22 169 участников)"},
    ],
    "tourism": [
        {"contact": "https://t.me/travel_batumi", "service": "ЭКСКУРСИИ ИЗ БАТУМИ по Грузии"},
        {"contact": "https://t.me/batumi_now", "service": "Залечь на дно в Батуми — жизнь, места, кухня (4 509 подписчиков)"},
        {"contact": "https://t.me/Batumi_100", "service": "Батуми: взаимопомощь туристов и экспатов (1 363 участника)"},
    ],
    "food": [],
    "digital": [],
    "realty": [
        {"contact": "https://t.me/georgiainvestments", "service": "GPI Недвижимость Грузия — Батуми, Тбилиси (3 727 подписчиков)"},
        {"contact": "https://t.me/Georgia_knrealty", "service": "НЕДВИЖИМОСТЬ ГРУЗИЯ — продажа, аренда, инвестиции (3 589 уч.)"},
        {"contact": "https://t.me/profityproperty", "service": "PROfity PROperty — недвижимость и переезд"},
        {"contact": "https://t.me/estelitigeorgia", "service": "Esteliti — недвижимость в Грузии"},
    ],
    "other": [
        {"contact": "https://t.me/BatumiOffer", "service": "БАТУМИ БАРАХОЛКА — объявления/услуги (22 169 участников)"},
        {"contact": "https://t.me/mybatumi_chat", "service": "БАТУМИ ЧАТ | Грузия (30 354 участника)"},
        {"contact": "https://t.me/batumi_my", "service": "Батуми Online | Чат (6 520 участников)"},
        {"contact": "https://t.me/nlevshitstelegram", "service": "Николай Левшиц — канал о Грузии (115 126 подписчиков)"},
        {"contact": "https://t.me/skidki_ge", "service": "Скидки Грузия — акции, услуги (16 800 подписчиков)"},
    ],
}

CITIES["Тбилиси"] = {
    "beauty": [
        {"contact": "https://t.me/Keti_Keti_007", "service": "Косметолог Ketino Vakhania — врач косметолог, кандидат наук"},
    ],
    "fitness": [],
    "kids": [
        {"contact": "https://t.me/Georgia_with_kids", "service": "В Грузии с детьми — 4 300 подписчиков"},
    ],
    "psychology": [],
    "medicine": [
        {"contact": "https://t.me/s/tbilisipeople/36302", "service": "Стоматология Regale — терапия, имплантология, ортодонтия. Тел: +995544440304"},
    ],
    "photo": [],
    "rental": [
        {"contact": "https://t.me/ads_ge", "service": "Трансфер Тбилиси-Батуми-Ереван"},
    ],
    "tourism": [
        {"contact": "https://t.me/tbilisipeople", "service": "Тбилиси для людей и про людей (26 700 подписчиков)"},
        {"contact": "https://t.me/tbilisieda", "service": "Тбилиси.Еда. — кафе, бары, рестораны (9 600 подписчиков)"},
    ],
    "food": [
        {"contact": "https://www.facebook.com/livingvino/", "service": "Living Vino — веганское/вегетарианское заведение"},
    ],
    "digital": [],
    "realty": [
        {"contact": "https://t.me/tbilisi_apartments", "service": "Квартиры в Тбилиси (11 000+ участников)"},
        {"contact": "https://t.me/kvartiry_v_tbilisi", "service": "Квартиры в Тбилиси (12 600+ участников)"},
        {"contact": "https://t.me/tbilisi_rent_finder", "service": "Tbilisi Rent Finder"},
        {"contact": "https://t.me/georgiainvestments", "service": "GPI Недвижимость Грузия"},
    ],
    "other": [
        {"contact": "https://t.me/tbilisi_service", "service": "Тбилиси Сервис — услуги (1 300 участников)"},
        {"contact": "https://t.me/tbilisi_rabota_uslugi", "service": "Тбилиси Работа Услуги (7 000 участников)"},
        {"contact": "https://t.me/mytbilisi_chat", "service": "Мой Тбилиси Чат (25 000 участников)"},
        {"contact": "https://t.me/nlevshitstelegram", "service": "Николай Левшиц — канал о Грузии (115 126 подписчиков)"},
    ],
}

CITIES["Ереван"] = {
    "beauty": [
        {"contact": "https://t.me/Armeniaspecialists", "service": "Главный чат специалистов Армении (1 300 участников) — все услуги"},
    ],
    "fitness": [],
    "kids": [],
    "psychology": [],
    "medicine": [],
    "photo": [
        {"contact": "https://t.me/synthesisyerevan", "service": "Фотографы, видеографы Еревана"},
        {"contact": "https://t.me/photographers_armenia_erevan", "service": "Фотографы Армении / Еревана"},
    ],
    "rental": [],
    "tourism": [
        {"contact": "https://t.me/guideyerevan", "service": "Гид Ереван (7 300 подписчиков)"},
        {"contact": "https://t.me/gid_armenia", "service": "Гид Армения — экскурсии на русском"},
        {"contact": "https://t.me/erevanrus", "service": "Ереван рус — гид, экскурсии (3 900 подписчиков)"},
    ],
    "food": [
        {"contact": "https://t.me/gastroneersYerevan", "service": "Гастрономия Еревана"},
    ],
    "digital": [
        {"contact": "https://t.me/iterevan", "service": "IT Ереван — разработка, дизайн (2 500 участников)"},
    ],
    "realty": [
        {"contact": "https://t.me/Relocation_Erevan", "service": "Релокейшн Ереван — недвижимость (9 400 участников)"},
        {"contact": "https://t.me/erevan_relocation", "service": "Ереван Релокейшн — аренда (11 200 участников)"},
        {"contact": "https://t.me/kvartiry_yerevan", "service": "Квартиры в Ереване"},
    ],
    "other": [
        {"contact": "https://t.me/erevan_russia", "service": "Ереван Раша — общение (4 000 участников)"},
        {"contact": "https://t.me/erevan_chat_svoi", "service": "Ереван чат свои — общение, услуги (9 800 участников)"},
        {"contact": "https://haywiki.org/life/contacts.html", "service": "Справочник русскоязычных контактов в Армении"},
    ],
}

# ══════════════ UAE ══════════════

CITIES["Дубай"] = {
    "beauty": [
        {"contact": "https://t.me/beauty_masters_dubai", "service": "Бьюти Мастера Дубай — каталог услуг красоты (4 800+ участников)"},
        {"contact": "https://t.me/beauty_chat_dubai", "service": "Бьюти Чат Дубай — мастера красоты, отзывы"},
        {"contact": "https://t.me/beauty_services_dubai", "service": "Услуги салонов красоты в ОАЭ"},
        {"contact": "https://t.me/uslugi_krasoty_dubai", "service": "Дубай женский чат — услуги мастеров красоты"},
        {"contact": "https://dubiznes.ae/listing-category/beauty/", "service": "Салоны красоты, косметологи, мастера — каталог dubiznes.ae"},
    ],
    "fitness": [
        {"contact": "https://dubiznes.ae/listing-category/fitness/", "service": "Фитнес и спорт — русские тренеры в Дубае"},
    ],
    "kids": [
        {"contact": "https://t.me/angel_kids_dubai", "service": "Angel Kids — детский центр в Дубае"},
        {"contact": "https://dubiznes.ae/listing-category/education/", "service": "Русские школы, детские сады, репетиторы в Дубае"},
    ],
    "psychology": [
        {"contact": "https://dubiznes.ae/listing-category/consulting/", "service": "Психологи, лайф-коучи, нутрициологи в Дубае"},
    ],
    "medicine": [
        {"contact": "https://dubiznes.ae/listing-category/medicine/", "service": "Медицина и здоровье — русские врачи в Дубае"},
        {"contact": "https://dubiznes.ae/listing-category/dentists/", "service": "Стоматологи русские в Дубае"},
    ],
    "photo": [
        {"contact": "https://dubiznes.ae/listing-category/photographers/", "service": "Фотографы русские в Дубае"},
        {"contact": "https://dubiznes.ae/listing-category/videographers/", "service": "Видеографы, монтаж в Дубае"},
    ],
    "rental": [
        {"contact": "https://dubiznes.ae/listing-category/car-rental/", "service": "Аренда авто в Дубае — русские компании"},
        {"contact": "https://t.me/paddock_rentacar", "service": "Paddock Rent A Car в Дубае"},
    ],
    "tourism": [
        {"contact": "https://dubiznes.ae/listing-category/tourism/", "service": "Туристические услуги в Дубае"},
    ],
    "food": [
        {"contact": "https://t.me/dodopizza_dubai", "service": "Dodo Pizza в Дубае"},
        {"contact": "https://t.me/gastronom_ae", "service": "Gastronom.ae — продукты из России и СНГ"},
        {"contact": "https://dubiznes.ae/listing-category/restaurants/", "service": "Рестораны и кафе русские в Дубае"},
    ],
    "digital": [
        {"contact": "https://dubiznes.ae/listing-category/it-services/", "service": "IT-услуги, веб-дизайн в Дубае"},
    ],
    "realty": [
        {"contact": "https://t.me/dubai_realty_russian", "service": "Недвижимость в Дубае на русском"},
        {"contact": "https://dubiznes.ae/listing-category/real-estate/", "service": "Риелторы и агентства недвижимости в Дубае"},
    ],
    "other": [
        {"contact": "https://t.me/chat_dubai_group", "service": "Русские в Дубае (40 000+ участников)"},
        {"contact": "https://t.me/russkie_dubai", "service": "Чат взаимопомощи русскоязычных в ОАЭ (3 500+)"},
        {"contact": "https://t.me/dubaichatrusskie11", "service": "ЧАТ ДУБАЙ | РУССКИЕ В ДУБАЕ (6 500+)"},
        {"contact": "https://dubiznes.ae/listing-tag/dxb/", "service": "Каталог русских компаний в Дубае (286+ записей)"},
        {"contact": "https://uaehub.ru", "service": "Полезные ресурсы для жизни и бизнеса в Дубае"},
        {"contact": "https://dubiznes.ae/listing-category/legal/", "service": "Юридические услуги, бухгалтеры в Дубае"},
    ],
}

CITIES["Рас-эль-Хайма"] = {
    "beauty": [
        {"contact": "https://t.me/beauty_masters_dubai", "service": "Бьюти Мастера ОАЭ — чат по всем эмиратам, включая RAK"},
    ],
    "fitness": [],
    "kids": [],
    "psychology": [],
    "medicine": [],
    "photo": [],
    "rental": [],
    "tourism": [
        {"contact": "https://dubiznes.ae/listing-category/tourism/", "service": "Туристические услуги в ОАЭ — общий каталог"},
    ],
    "food": [],
    "digital": [],
    "realty": [
        {"contact": "https://dubiznes.ae/listing-category/real-estate/", "service": "Недвижимость в Рас-эль-Хайме — каталог dubiznes.ae"},
    ],
    "other": [
        {"contact": "https://t.me/chat_dubai_group", "service": "Русские в ОАЭ (40 000+ участников) — общий чат всех эмиратов"},
        {"contact": "https://t.me/+fZCqCr-uLDYxNmI0", "service": "Услуги ОАЭ | UAE Dubai services — чат по всем эмиратам"},
        {"contact": "https://dubiznes.ae/listing-category/services/", "service": "Каталог русских услуг в ОАЭ"},
    ],
}

# ══════════════ RUSSIA ══════════════

CITIES["Сочи"] = {
    "beauty": [
        {"contact": "https://t.me/bbssochiru", "service": "BBS Sochi — доска объявлений, услуги красоты"},
        {"contact": "https://t.me/uslugi_sochi", "service": "Услуги Сочи — канал, мастера красоты, ремонт"},
        {"contact": "https://beautywin.ru/sochi", "service": "BeautyWin Сочи — салоны красоты, мастера"},
    ],
    "fitness": [
        {"contact": "https://t.me/gordsochi", "service": "Горд Сочи — спорт, фитнес (100 000+ участников)"},
    ],
    "kids": [
        {"contact": "https://t.me/gordsochi", "service": "Поиск нянь, репетиторов в общем чате Сочи"},
    ],
    "psychology": [],
    "medicine": [
        {"contact": "https://t.me/gordsochi", "service": "Поиск врачей, клиник в общем чате Сочи"},
    ],
    "photo": [
        {"contact": "https://t.me/bbssochiru", "service": "Фотографы, видеографы — доска объявлений"},
    ],
    "rental": [
        {"contact": "https://t.me/arenda_sochi", "service": "Аренда жилья в Сочи"},
        {"contact": "https://t.me/sochi_transfer", "service": "Трансферы Сочи"},
    ],
    "tourism": [
        {"contact": "https://t.me/sochi_tour", "service": "Туризм в Сочи — экскурсии, маршруты"},
    ],
    "food": [
        {"contact": "https://t.me/sochi_food", "service": "Еда в Сочи — доставка, кафе, рестораны"},
    ],
    "digital": [
        {"contact": "https://t.me/sochi_it", "service": "IT-Сочи — разработка, SMM, дизайн"},
    ],
    "realty": [
        {"contact": "https://t.me/arenda_sochi", "service": "Аренда жилья в Сочи"},
        {"contact": "https://t.me/sochi_realty", "service": "Недвижимость Сочи"},
    ],
    "other": [
        {"contact": "https://t.me/gordsochi", "service": "Горд Сочи — главный чат (100 000+ участников)"},
        {"contact": "https://t.me/bbssochiru", "service": "BBS Sochi — доска объявлений"},
        {"contact": "https://t.me/uslugi_sochi", "service": "Услуги Сочи — все виды услуг"},
    ],
}

CITIES["Краснодар"] = {
    "beauty": [
        {"contact": "https://t.me/krasnodar_uslugi", "service": "Услуги Краснодар — мастера красоты, косметологи (9 000+)"},
        {"contact": "https://t.me/krasnodar_beauty", "service": "Бьюти чат Краснодар"},
    ],
    "fitness": [
        {"contact": "https://t.me/krasnodar_sport", "service": "Спорт Краснодар — фитнес, тренеры"},
    ],
    "kids": [
        {"contact": "https://t.me/krasnodar_moms", "service": "Мамы Краснодара — дети, сады, школы"},
    ],
    "psychology": [],
    "medicine": [
        {"contact": "https://t.me/krasnodar_med", "service": "Медицина Краснодар — врачи, клиники"},
    ],
    "photo": [
        {"contact": "https://t.me/krasnodar_photo", "service": "Фотографы Краснодара"},
    ],
    "rental": [
        {"contact": "https://t.me/krasnodar_rent", "service": "Аренда жилья Краснодар"},
    ],
    "tourism": [],
    "food": [
        {"contact": "https://t.me/krasnodar_food", "service": "Еда Краснодар — доставка, кафе"},
    ],
    "digital": [
        {"contact": "https://t.me/krasnodar_it", "service": "IT Краснодар — разработка, SMM"},
    ],
    "realty": [
        {"contact": "https://t.me/krasnodar_rent", "service": "Аренда жилья Краснодар"},
    ],
    "other": [
        {"contact": "https://t.me/krasnodar_uslugi", "service": "Услуги Краснодар (9 000+ участников)"},
        {"contact": "https://t.me/krasnodar_chat", "service": "Главный чат Краснодара"},
        {"contact": "https://profi.ru", "service": "Профи.ру — поиск специалистов по каталогу"},
    ],
}

CITIES["Тула"] = {
    "beauty": [
        {"contact": "https://t.me/usl_Tula", "service": "Услуги Тула — мастера красоты (1 800+ участников)"},
        {"contact": "https://t.me/tula_services", "service": "Tula Services — чат услуг"},
    ],
    "fitness": [],
    "kids": [],
    "psychology": [],
    "medicine": [],
    "photo": [],
    "rental": [],
    "tourism": [],
    "food": [],
    "digital": [],
    "realty": [],
    "other": [
        {"contact": "https://t.me/usl_Tula", "service": "Услуги Тула — доска объявлений (1 800+ участников)"},
        {"contact": "https://t.me/tula_services", "service": "Tula Services — чат услуг"},
        {"contact": "https://uslugi.yandex.ru/10491-tula", "service": "Яндекс Услуги — Тула"},
        {"contact": "https://t.me/tula_chat", "service": "Главный чат Тулы"},
    ],
}

CITIES["Нижний Новгород"] = {
    "beauty": [
        {"contact": "https://t.me/nn_proff", "service": "NN Proff — специалисты, услуги, мастера красоты"},
        {"contact": "https://t.me/nizhny_nails", "service": "Ногтевой сервис Нижний Новгород"},
    ],
    "fitness": [
        {"contact": "https://t.me/nn_sport", "service": "Спорт НН — фитнес, тренеры"},
    ],
    "kids": [
        {"contact": "https://t.me/nn_moms", "service": "Мамы НН — дети, сады, школы"},
    ],
    "psychology": [],
    "medicine": [
        {"contact": "https://t.me/nn_med", "service": "Медицина НН — врачи, клиники"},
    ],
    "photo": [
        {"contact": "https://t.me/nn_photo", "service": "Фотографы НН"},
    ],
    "rental": [
        {"contact": "https://t.me/nn_rent", "service": "Аренда жилья НН"},
    ],
    "tourism": [],
    "food": [
        {"contact": "https://t.me/nn_food", "service": "Еда НН — доставка, кафе"},
    ],
    "digital": [
        {"contact": "https://t.me/nn_it", "service": "IT НН — разработка, SMM"},
    ],
    "realty": [
        {"contact": "https://t.me/nn_rent", "service": "Аренда жилья Нижний Новгород"},
    ],
    "other": [
        {"contact": "https://t.me/nn_proff", "service": "NN Proff — специалисты и услуги"},
        {"contact": "https://t.me/nizhny01", "service": "Нижний Новгород — главный чат"},
        {"contact": "https://t.me/newsnn", "service": "Новости НН"},
        {"contact": "https://uslugi.yandex.ru/10395-nizhniy-novgorod", "service": "Яндекс Услуги — Нижний Новгород"},
    ],
}

# ══════════════ ABKHAZIA ══════════════

CITIES["Сухум"] = {
    "beauty": [
        {"contact": "https://salonkrasoty-apsny.ru/", "service": "Салон красоты AnaBelle — косметология, шугаринг, массаж. Тел: +7 (940) 777-65-14"},
        {"contact": "https://www.instagram.com/sukhumbeauty/", "service": "Brow&Beauty Bar Сухум — брови, ресницы, макияж. Тел: +7940 737 0 888"},
        {"contact": "https://www.instagram.com/ib_studio_abh/", "service": "IB Studio Сухум (3 272 подписчика) — маникюр, педикюр"},
        {"contact": "https://www.instagram.com/luch_beautylab/", "service": "LUCH лаборатория красоты — Наб. Махаджиров. Тел: +79407414400"},
        {"contact": "https://vk.com/elviart_beauty", "service": "Эльвира — наращивание ресниц, брови, ногти Сухум"},
    ],
    "fitness": [
        {"contact": "https://www.instagram.com/fitness_city_sukhum", "service": "Fitness City Сухум — тренажерный зал (4 100+ подписчиков)"},
    ],
    "kids": [
        {"contact": "https://ab-baza.ru/suhum/search/uslugi/prochie-uslugi/uslugi-repetitora-pedagog-suhum-910.html", "service": "Репетитор-педагог — подготовка к школе, абхазский язык"},
    ],
    "psychology": [
        {"contact": "https://t.me/+KjglF1Y0y9I0YzYx", "service": "Психология зрелости с Милой Красовской — пространство для женщин 30+"},
    ],
    "medicine": [],
    "photo": [
        {"contact": "https://vk.com/eremeeva.photoabh", "service": "Фотограф Абхазия Сухум — фотосессии"},
        {"contact": "https://suhum.iceni.ru/kupit/uslugi-fotografa/", "service": "Услуги фотографа в Сухуме"},
    ],
    "rental": [
        {"contact": "https://suhum.iceni.ru/category/avto/", "service": "Транспортные услуги, аренда авто в Сухуме"},
        {"contact": "https://suhum.iceni.ru/category/razvlechenija/prokat-velosipedov/", "service": "Прокат велосипедов в Сухуме"},
    ],
    "tourism": [
        {"contact": "https://t.me/abhaztravel", "service": "Абхазия Туризм — экскурсии. Тел: wa.me/79409369276"},
        {"contact": "https://www.sputnik8.com/ru/sukhumi", "service": "Экскурсии в Сухуме — цены 2026"},
        {"contact": "https://suhum.iceni.ru/category/razvlechenija/jekskursii/", "service": "Экскурсии в Сухуме (13 предложений)"},
    ],
    "food": [
        {"contact": "https://suhum.iceni.ru/category/dostavka-edy/", "service": "Доставка еды в Сухуме — пицца, торты, мёд, морепродукты"},
    ],
    "digital": [
        {"contact": "https://suhum.iceni.ru/category/biz/sozdanie-sajtov/", "service": "Создание сайтов в Сухуме (17 предложений)"},
        {"contact": "https://suhum.iceni.ru/category/biz/socialnye-seti/", "service": "Ведение соцсетей (18 предложений)"},
    ],
    "realty": [
        {"contact": "https://t.me/welcome_sukhum", "service": "Жилье в Абхазии. СУХУМ — помощь в подборе жилья"},
        {"contact": "https://suhumi.sutochno.ru/", "service": "Посуточная аренда в Сухуме от владельцев"},
        {"contact": "https://otdyh-abhazia.ru/sukhum/kvartiry/", "service": "Квартиры посуточно в Сухуме (502 объявления)"},
    ],
    "other": [
        {"contact": "https://t.me/abkhazia_sukhum", "service": "АБХАЗИЯ СУХУМ — объявления, реклама, услуги"},
        {"contact": "https://t.me/apsya_reklama", "service": "Апсуа Реклама — объявления по всей Абхазии"},
        {"contact": "https://t.me/abkhazia_chat", "service": "АБХАЗИЯ чат туристов — общение, услуги"},
        {"contact": "https://suhum.iceni.ru/", "service": "Сухум и Цены — 350+ предложений, доска объявлений"},
        {"contact": "https://ab-baza.ru/suhum/search/uslugi/", "service": "Ab-Baza — доска объявлений Абхазии"},
        {"contact": "https://uslugi.yandex.ru/10281-suhum", "service": "Яндекс Исполнители — Сухум"},
        {"contact": "https://t.me/LegalAbk", "service": "Юридическая фирма — регистрация ООО/ИП, сопровождение сделок. Тел: +7(940)707-10-00"},
    ],
}

# ──────────────────────────────────────────────
# GENERATE ALL FILES
# ──────────────────────────────────────────────

OUT_DIR = r"C:\AION\docs"

file_map = {
    "Анталия": "База исполнителей Анталия.html",
    "Стамбул": "База исполнителей Стамбул.html",
    "Кемер": "База исполнителей Кемер.html",
    "Паттайя": "База исполнителей Паттайя.html",
    "Пхукет": "База исполнителей Пхукет.html",
    "Батуми": "База исполнителей Батуми.html",
    "Тбилиси": "База исполнителей Тбилиси.html",
    "Ереван": "База исполнителей Ереван.html",
    "Дубай": "База исполнителей Дубай.html",
    "Рас-эль-Хайма": "База исполнителей Рас-эль-Хайма.html",
    "Сочи": "База исполнителей Сочи.html",
    "Краснодар": "База исполнителей Краснодар.html",
    "Тула": "База исполнителей Тула.html",
    "Нижний Новгород": "База исполнителей Нижний Новгород.html",
    "Сухум": "База исполнителей Сухум.html",
    "Вунгтау": "База исполнителей Вунгтау.html",
    "Дананг": "База исполнителей Дананг.html",
    "Муйне": "База исполнителей Муйне.html",
    "Фукуок": "База исполнителей Фукуок.html",
    "Ханой": "База исполнителей Ханой.html",
    "Хошимин": "База исполнителей Хошимин.html",
}

print("Генерация файлов База исполнителей...\n")

for city_ru, filename in file_map.items():
    entries = CITIES.get(city_ru, {})
    html = generate_file(city_ru, city_ru, entries)
    filepath = os.path.join(OUT_DIR, filename)
    save_file(filepath, html)

print(f"\nВсего сгенерировано: {len(file_map)} файлов")
print("Готово!")
