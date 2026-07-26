#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate HTML files from russian_service_providers_turkey.json
"""

import json

with open("russian_service_providers_turkey.json", "r", encoding="utf-8") as f:
    data = json.load(f)

CATEGORY_EMOJI = {
    "beauty": "💅",
    "fitness": "🏋️",
    "kids": "👶",
    "psychology": "🧠",
    "medicine": "🩺",
    "photo_video": "📸",
    "rental_transport": "🚗",
    "tourism": "🏝️",
    "food": "🍽️",
    "digital": "💻",
    "realty": "🏠",
}

CATEGORY_RU = {
    "beauty": "Красота",
    "fitness": "Фитнес",
    "kids": "Дети",
    "psychology": "Психология",
    "medicine": "Медицина",
    "photo_video": "Фото/Видео",
    "rental_transport": "Аренда/Транспорт",
    "tourism": "Туризм",
    "food": "Еда",
    "digital": "Цифровые услуги",
    "realty": "Недвижимость",
}

def generate_city_html(city):
    lines = []
    lines.append("<!DOCTYPE html>")
    lines.append('<html lang="ru">')
    lines.append("<head>")
    lines.append('    <meta charset="UTF-8">')
    lines.append(f'    <title>Русскоязычные специалисты и услуги - {city["name_ru"]}</title>')
    lines.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
    lines.append("    <style>")
    lines.append("""        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; }
        .container { max-width: 1100px; margin: 0 auto; padding: 20px; }
        h1 { font-size: 28px; margin-bottom: 5px; color: #1a1a2e; }
        h2.subtitle { font-size: 16px; color: #666; margin-bottom: 20px; font-weight: normal; }
        h2.section { font-size: 22px; margin: 30px 0 15px; padding-bottom: 8px; border-bottom: 3px solid #e94560; color: #1a1a2e; }
        h3 { font-size: 18px; margin: 20px 0 10px; color: #16213e; }
        .card { background: white; border-radius: 10px; padding: 15px; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.08); transition: transform 0.2s; }
        .card:hover { transform: translateY(-2px); box-shadow: 0 4px 10px rgba(0,0,0,0.12); }
        .card a { color: #e94560; text-decoration: none; font-weight: 600; font-size: 16px; }
        .card a:hover { text-decoration: underline; }
        .card .desc { color: #555; font-size: 14px; margin-top: 5px; line-height: 1.4; }
        .card .type-badge { display: inline-block; background: #eee; padding: 2px 8px; border-radius: 4px; font-size: 11px; color: #666; margin-right: 8px; }
        .card .link-icon { color: #e94560; font-size: 14px; }
        .general-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 10px; }
        .cat-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 10px; }
        .toc { background: white; border-radius: 10px; padding: 20px; margin: 20px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.08); }
        .toc a { color: #e94560; text-decoration: none; display: block; padding: 4px 0; }
        .toc a:hover { text-decoration: underline; }
        .footer { text-align: center; color: #999; font-size: 12px; margin: 40px 0 20px; }
        .stats { display: flex; gap: 15px; flex-wrap: wrap; margin: 15px 0; }
        .stat-box { background: #e94560; color: white; padding: 10px 20px; border-radius: 8px; font-size: 14px; }
        @media (max-width: 600px) {
            .general-grid { grid-template-columns: 1fr; }
            .cat-grid { grid-template-columns: 1fr; }
            .container { padding: 10px; }
        }
    """)
    lines.append("</style>")
    lines.append("</head>")
    lines.append("<body>")
    lines.append('<div class="container">')

    # Header
    lines.append(f'<h1>{city["name_ru"]} ({city["name_tr"]})</h1>')
    lines.append(f'<h2 class="subtitle">{city["description"]}</h2>')

    # Stats
    total_general = len(city["general_resources"])
    total_cat = sum(len(v) for v in city["categories"].values())
    lines.append('<div class="stats">')
    lines.append(f'<div class="stat-box">📋 Общих ресурсов: {total_general}</div>')
    lines.append(f'<div class="stat-box">📌 Специалистов: {total_cat}</div>')
    lines.append(f'<div class="stat-box">🏷️ Категорий: {len(city["categories"])}</div>')
    lines.append('</div>')

    # TOC
    lines.append('<div class="toc"><strong>📑 Содержание:</strong><br>')
    lines.append('<a href="#general">📋 Общие ресурсы</a>')
    for key, entries in city["categories"].items():
        ru = CATEGORY_RU.get(key, key)
        emoji = CATEGORY_EMOJI.get(key, "📌")
        if entries:
            lines.append(f'<a href="#cat-{key}">{emoji} {ru} ({len(entries)})</a>')
    lines.append('</div>')

    # General Resources
    lines.append(f'<h2 class="section" id="general">📋 Общие ресурсы ({total_general})</h2>')
    lines.append('<div class="general-grid">')
    for r in city["general_resources"]:
        t = r.get("type", "").replace("_", " ").title()
        lines.append(f'<div class="card"><span class="type-badge">{t}</span><a href="{r["link"]}" target="_blank">{r["name"]}</a><div class="desc">{r["description"]}</div></div>')
    lines.append("</div>")

    # Categories
    for key, entries in city["categories"].items():
        if not entries:
            continue
        ru = CATEGORY_RU.get(key, key)
        emoji = CATEGORY_EMOJI.get(key, "📌")
        lines.append(f'<h2 class="section" id="cat-{key}">{emoji} {ru} ({len(entries)})</h2>')
        lines.append('<div class="cat-grid">')
        for e in entries:
            lines.append(f'<div class="card"><a href="{e["link"]}" target="_blank">{e["name"]}</a><div class="desc">{e["description"]}</div></div>')
        lines.append("</div>")

    # Footer
    lines.append(f'<div class="footer">Сгенерировано из поисковых данных. Дата: 2026. Анталия · Стамбул · Кемер</div>')
    lines.append("</div>")
    lines.append("</body>")
    lines.append("</html>")
    return "\n".join(lines)

def generate_index_html(data):
    lines = []
    lines.append("<!DOCTYPE html>")
    lines.append('<html lang="ru">')
    lines.append("<head>")
    lines.append('    <meta charset="UTF-8">')
    lines.append('    <title>Русскоязычные специалисты в Турции</title>')
    lines.append('    <meta name="viewport" content="width=device-width, initial-scale=1.0">')
    lines.append("    <style>")
    lines.append("""        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; color: #333; }
        .container { max-width: 1100px; margin: 0 auto; padding: 20px; }
        h1 { font-size: 28px; margin-bottom: 5px; color: #1a1a2e; }
        .subtitle { font-size: 16px; color: #666; margin-bottom: 30px; }
        .city-card { background: white; border-radius: 12px; padding: 25px; margin-bottom: 20px; box-shadow: 0 3px 10px rgba(0,0,0,0.1); }
        .city-card h2 { font-size: 24px; margin-bottom: 5px; }
        .city-card .desc { color: #666; margin-bottom: 15px; }
        .city-stats { display: flex; gap: 10px; flex-wrap: wrap; margin: 10px 0; }
        .city-stats span { background: #f0f0f0; padding: 5px 12px; border-radius: 6px; font-size: 13px; }
        .btn { display: inline-block; background: #e94560; color: white; padding: 10px 25px; border-radius: 8px; text-decoration: none; font-weight: 600; margin-top: 10px; }
        .btn:hover { background: #d63850; }
        .cross { background: white; border-radius: 10px; padding: 20px; margin-top: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.08); }
        .cross h3 { margin-bottom: 10px; }
        .cross-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 10px; }
        .cross-item { padding: 8px 0; border-bottom: 1px solid #eee; }
        .cross-item:last-child { border-bottom: none; }
        .cross-item a { color: #e94560; text-decoration: none; }
        .cross-item a:hover { text-decoration: underline; }
        .cross-item .desc { color: #666; font-size: 13px; }
        .footer { text-align: center; color: #999; font-size: 12px; margin: 40px 0 20px; }
    """)
    lines.append("</style>")
    lines.append("</head>")
    lines.append("<body>")
    lines.append('<div class="container">')
    lines.append('<h1>🇷🇺 Русскоязычные специалисты в Турции</h1>')
    lines.append('<p class="subtitle">Проверенные Telegram каналы, чаты, сайты и контакты по 3 городам: Анталия, Стамбул, Кемер</p>')

    total_all = 0
    for city in data["cities"]:
        total_all += len(city["general_resources"])
        total_all += sum(len(v) for v in city["categories"].values())
        city_stats = sum(len(v) for v in city["categories"].values())
        lines.append(f'<div class="city-card">')
        lines.append(f'  <h2>{city["name_ru"]} ({city["name_tr"]})</h2>')
        lines.append(f'  <p class="desc">{city["description"]}</p>')
        lines.append(f'  <div class="city-stats">')
        lines.append(f'    <span>📋 Ресурсов: {len(city["general_resources"])}</span>')
        lines.append(f'    <span>📌 Специалистов: {city_stats}</span>')
        cat_count = len([k for k, v in city["categories"].items() if v])
        lines.append(f'    <span>🏷️ Категорий: {cat_count}</span>')
        lines.append(f'  </div>')
        lines.append(f'  <a class="btn" href="{city["name"].lower()}.html">Открыть → {city["name_ru"]}</a>')
        lines.append(f'</div>')

    lines.append(f'<p style="text-align:center;color:#999;margin:20px 0;">Всего найдено записей: <strong>{total_all}</strong></p>')

    # Cross-city
    cross = data.get("cross_city_resources", {})
    lines.append('<div class="cross">')
    lines.append('<h3>🌍 Ресурсы по всей Турции</h3>')
    lines.append('<div class="cross-grid">')
    for res_type, entries in cross.items():
        for e in entries:
            lines.append(f'<div class="cross-item"><a href="{e["link"]}" target="_blank">{e["name"]}</a><div class="desc">{e["description"]}</div></div>')
    lines.append('</div></div>')

    lines.append('<div class="footer">© 2026. Данные собраны из открытых источников. Перед использованием проверяйте актуальность.</div>')
    lines.append("</div>")
    lines.append("</body>")
    lines.append("</html>")
    return "\n".join(lines)

# Generate files
with open("index.html", "w", encoding="utf-8") as f:
    f.write(generate_index_html(data))
print("✓ index.html generated")

for city in data["cities"]:
    filename = f"{city['name'].lower()}.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(generate_city_html(city))
    print(f"✓ {filename} generated")

print("\nDone! Open index.html in browser.")
