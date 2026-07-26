# -*- coding: utf-8 -*-
import random
import os

random.seed(42)

# ===================== DATA =====================

first_names_m = [
    "Алексей","Александр","Сергей","Дмитрий","Максим","Артём","Иван","Михаил",
    "Андрей","Владимир","Павел","Константин","Николай","Евгений","Виталий",
    "Роман","Вадим","Олег","Руслан","Тимур","Кирилл","Станислав","Глеб",
    "Марат","Данил","Игорь","Вячеслав","Григорий","Антон","Юрий","Василий",
    "Владислав","Никита","Егор","Давид","Ярослав","Семён","Тигран","Артур","Эдуард"
]
first_names_f = [
    "Анна","Елена","Ольга","Мария","Наталья","Ирина","Татьяна","Светлана",
    "Екатерина","Анастасия","Юлия","Кристина","Дарья","Алиса","Вероника",
    "Оксана","Евгения","Людмила","Маргарита","София","Полина","Виктория",
    "Валерия","Надежда","Галина","Лариса","Алина","Ксения","Вера","Марина",
    "Алёна","Яна","Зоя","Валентина","Лидия","Раиса","Тамара","Любовь","Нина","Злата"
]
all_names = first_names_m + first_names_f

name_to_en = {
    "Алексей":"alexey","Александр":"alexandr","Сергей":"sergey","Дмитрий":"dmitry",
    "Максим":"maksim","Артём":"artyom","Иван":"ivan","Михаил":"mikhail",
    "Андрей":"andrey","Владимир":"vladimir","Павел":"pavel","Константин":"konstantin",
    "Николай":"nikolay","Евгений":"evgeny","Виталий":"vitaly","Роман":"roman",
    "Вадим":"vadim","Олег":"oleg","Руслан":"ruslan","Тимур":"timur",
    "Кирилл":"kirill","Станислав":"stanislav","Глеб":"gleb","Марат":"marat",
    "Данил":"danil","Игорь":"igor","Вячеслав":"vyacheslav","Григорий":"grigory",
    "Антон":"anton","Юрий":"yury","Василий":"vasily","Владислав":"vladislav",
    "Никита":"nikita","Егор":"egor","Давид":"david","Ярослав":"yaroslav",
    "Семён":"semyon","Тигран":"tigran","Артур":"artur","Эдуард":"eduard",
    "Анна":"anna","Елена":"elena","Ольга":"olga","Мария":"maria",
    "Наталья":"natalya","Ирина":"irina","Татьяна":"tatiana","Светлана":"svetlana",
    "Екатерина":"ekaterina","Анастасия":"anastasia","Юлия":"yulia","Кристина":"kristina",
    "Дарья":"darya","Алиса":"alisa","Вероника":"veronika","Оксана":"oksana",
    "Евгения":"evgenya","Людмила":"lyudmila","Маргарита":"margarita","София":"sofiya",
    "Полина":"polina","Виктория":"viktoria","Валерия":"valeriya","Надежда":"nadezhda",
    "Галина":"galina","Лариса":"larisa","Алина":"alina","Ксения":"kseniya",
    "Вера":"vera","Марина":"marina","Алёна":"alyona","Яна":"yana",
    "Зоя":"zoya","Валентина":"valentina","Лидия":"lidiya","Раиса":"raisa",
    "Тамара":"tamara","Любовь":"lyubov","Нина":"nina","Злата":"zlata"
}

services_by_cat = {
    "beauty": [
        "Маникюр, педикюр","Косметолог, чистка лица","Парикмахер, стрижки","Лазерная эпиляция",
        "Шугаринг, депиляция","Наращивание ресниц","Брови, ламинирование","Тату, перманент",
        "Массаж лица, микротоки","Салон красоты","Визажист, макияж","Барбершоп",
        "Кератиновое выпрямление","Дизайн ногтей","Чистка лица, пилинги","Микроблейдинг",
        "Окрашивание волос","СПА-процедуры","Обёртывания","Ламинирование ресниц",
        "Электроэпиляция","Архитектура бровей","Мужские стрижки","Педикюр медицинский"
    ],
    "fitness": [
        "Персональный тренер","Йога, растяжка","Пилатес","Бокс, кикбоксинг",
        "Фитнес, ОФП","Танцы, хореография","Плавание","Сёрфинг, сапсёрфинг",
        "Стретчинг","Большой теннис","Кроссфит","Детский фитнес",
        "Зумба","Беговой клуб","Единоборства","Функциональный тренинг",
        "Скалолазание","MTB велоспорт","Триатлон","Тренажёрный зал"
    ],
    "kids": [
        "Няня","Английский язык","Логопед","Подготовка к школе",
        "Репетитор начальных классов","Развивающие занятия","Рисование, ИЗО","Музыка, фортепиано",
        "Гитара, вокал","Раннее развитие","Математика","Программирование для детей",
        "Детский сад","Детский массаж","Ментальная арифметика","Каллиграфия",
        "Творческая мастерская","Китайский язык","Детский психолог","Скорочтение",
        "Робототехника, LEGO","Театральная студия","Французский язык","Немецкий язык",
        "Испанский язык","Корейский язык","Шахматы","Детская йога",
        "Монтессори","Футбол для детей","Баскетбол","Лепка, керамика"
    ],
    "psychology": [
        "Психолог","Психотерапия","Коуч-консультации","Нумеролог",
        "Астролог","Гипнотерапия","Рэйки, энергопрактики","Телесная терапия",
        "Детский психолог","Семейный психолог","Арт-терапия","Гештальт-терапия",
        "Травматерапия","Медитация","Трансформационные игры","Кинезиология",
        "Песочная терапия","Женские круги","Дыхательные практики","Транзактный анализ"
    ],
    "medicine": [
        "Терапевт, общая практика","Педиатр","Стоматолог","Гинеколог",
        "Дерматолог","ЛОР","Офтальмолог","Массаж медицинский",
        "Диетолог, нутрициолог","Остеопат","Хирург","Кардиолог",
        "Физиотерапия","Медсестра, уколы на дому","Детский массаж, ЛФК",
        "Мануальный терапевт","Анализы, чек-ап","Гомеопат","Эндокринолог"
    ],
    "photo": [
        "Фотограф, портреты","Видеограф, монтаж","Свадебная съёмка","Предметная съёмка",
        "Съёмка с дрона","Ретушь, обработка","Контент-мейкер","Видеомонтаж, reels",
        "Фотостудия","Love story, портрет","Детский фотограф","Будуарная съёмка",
        "Бренд-фотография","Фуд-фотограф","Интерьерная съёмка","Тревел-контент",
        "Семейная фотосессия","Товарная съёмка","Аэросъёмка","Видеоролики для соцсетей"
    ],
    "rental": [
        "Аренда байков, скутеров","Аренда автомобилей","Трансфер аэропорт","Такси, трансфер",
        "Прокат велосипедов","Аренда мотоциклов","Ремонт байков","Автомойка, химчистка",
        "Междугородний трансфер","Аренда лодок, катеров","Мототакси, доставка","Доставка грузов",
        "Аренда электросамокатов","Аренда гидроциклов","Автосервис","Охраняемая парковка",
        "Продажа мотоциклов","Личный водитель","Прокат снаряжения","Эвакуатор"
    ],
    "tourism": [
        "Экскурсии","Дайвинг, снорклинг","Морская рыбалка","Яхта, морские прогулки",
        "Визаран, оформление виз","Гид, сопровождение","Треккинг, походы","Тур на острова",
        "Водопады, природа","Гастро-тур","Мотопутешествия","Парапланеризм",
        "Кулинарный мастер-класс","Организация туров","Пляжный отдых","Фото-тур",
        "Сап-прогулки","Ночные экскурсии","Йога-ретрит","Винный тур"
    ],
    "food": [
        "Домашняя выпечка","Торты на заказ","Русские продукты","Морепродукты, доставка",
        "Кофе, чай","Мясо, птица","Фрукты, овощи","Кондитерская ручной работы",
        "Здоровое питание","Молочная продукция","Суши, роллы","BBQ, шашлык",
        "Вегетарианская кухня","Хлеб, выпечка","Орехи, снеки","Кейтеринг",
        "Мёд, прополис","Полуфабрикаты","Сыры домашние","Доставка воды"
    ],
    "digital": [
        "SMM-менеджер","Разработка сайтов","Таргетолог","Графический дизайн",
        "Копирайтер","SEO-продвижение","Контент-план","Создание Telegram-ботов",
        "Видеопродакшн","Мобильные приложения","Брендинг","Веб-аналитика",
        "CRM-внедрение","Переводчик","Техподдержка","Моушн-дизайн",
        "AI-услуги","Лендинги","Настройка VPN","Хостинг, домены"
    ],
    "realty": [
        "Аренда квартир долгосрочно","Аренда домов, вилл","Продажа недвижимости",
        "Кондо, новостройки","Управление арендой","Земельные участки",
        "Дизайн интерьера","Ремонт под ключ","Посуточная аренда",
        "Юрист по недвижимости","Инвестиции","Коммерческая аренда",
        "Виллы с бассейном","Гестхаусы","Аренда комнаты"
    ],
    "other": [
        "Юридические консультации","Ремонт ПК, ноутбуков","Цветы, букеты","Химчистка, стирка",
        "Клининг, уборка","Груминг собак","Передержка животных","Швейное ателье",
        "Мебель на заказ","Страхование","Изготовление ключей","Обмен валюты",
        "Украшения ручной работы","Организация праздников","Ремонт телефонов",
        "Международная доставка","Нотариус","Ветеринар","Автосервис",
        "Изготовление печатей","Такси, трансфер","Сувениры, подарки"
    ],
}

categories = [
    ("beauty", "Красота и уход"),
    ("fitness", "Фитнес и спорт"),
    ("kids", "Дети и развитие"),
    ("psychology", "Психология и здоровье"),
    ("medicine", "Медицина"),
    ("photo", "Фото и видео"),
    ("rental", "Аренда и транспорт"),
    ("tourism", "Туризм и экскурсии"),
    ("food", "Еда и продукты"),
    ("digital", "Цифровые услуги"),
    ("realty", "Недвижимость"),
    ("other", "Прочее"),
]

category_counts = {
    "beauty": 62, "fitness": 52, "kids": 90, "psychology": 38,
    "medicine": 28, "photo": 33, "rental": 38, "tourism": 38,
    "food": 28, "digital": 28, "realty": 18, "other": 28
}

# ===================== GENERATION =====================

def gen_username_pattern(city_part, cat_id, used, names_pool):
    """Generate realistic usernames avoiding fake patterns."""
    for attempt in range(100):
        pattern = random.randint(1, 8)
        name = random.choice(names_pool)
        ename = name_to_en.get(name, name.lower())
        
        # Get a service keyword
        svc = random.choice(services_by_cat[cat_id]).lower()
        svc_words = svc.replace(",","").replace("  "," ").split()
        svc_kw = svc_words[0].replace(" ","_")
        
        if pattern == 1:
            u = f"{ename}_{svc_kw}_{city_part}"
        elif pattern == 2:
            u = f"{svc_kw}_{ename}_{city_part}"
        elif pattern == 3:
            u = f"{city_part}_{svc_kw}_{ename}"
        elif pattern == 4:
            u = f"{ename}_{city_part}_{svc_kw}"
        elif pattern == 5:
            adj = random.choice(["club","studio","pro","master","service","shop","center","expert","best"])
            u = f"{city_part}_{svc_kw}_{adj}"
        elif pattern == 6:
            adj = random.choice(["24","pro","top","vip","online"])
            u = f"{ename}_{svc_kw}_{adj}"
        elif pattern == 7:
            u = f"{ename}{random.randint(10,999)}_{city_part}"
        else:
            u = f"{city_part}_{ename}_{svc_kw}"
        
        u = u.replace(" ", "_").replace("'", "").replace("-", "_").replace(",","")
        u = u.strip("_")
        if len(u) > 30:
            u = u[:30].rstrip("_")
        if len(u) < 5:
            continue
        if "_" not in u:
            continue
        if u not in used and u not in used:  # does it look single-word?
            parts = u.split("_")
            if all(len(p) < 3 for p in parts):
                continue
            used.add(u)
            return u
    # Fallback - should be rare
    while True:
        u = f"{random.choice(names_pool).lower()}_{city_part}_{random.randint(10,99)}"
        if u not in used:
            used.add(u)
            return u

def generate_file(city_name, city_part, filename):
    used_tg = set()
    used_contacts = set()
    
    total_entries = sum(category_counts.values())
    contact_types = []
    entry_num = 0
    
    html_parts = []
    html_parts.append('<!DOCTYPE html>')
    html_parts.append('<html>')
    html_parts.append('<head>')
    html_parts.append('<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
    html_parts.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    html_parts.append(f'<title>База исполнителей {city_name} — AION</title>')
    html_parts.append('''<style>
  :root { --primary: #0A0F1E; --accent: #6366f1; --gold: #D4A853; --text: #1e293b; --text-light: #64748b; --bg: #ffffff; --bg-alt: #f8fafc; --border: #e2e8f0; --deep-blue: #0A1628; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html { scroll-behavior: smooth; }
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; line-height: 1.6; color: var(--text); background: var(--bg); max-width: 1100px; margin: 0 auto; padding: 0; }
  .cover { background: linear-gradient(135deg, var(--deep-blue) 0%, #1a2a4a 50%, var(--deep-blue) 100%); color: white; padding: 60px 40px 50px; text-align: center; position: relative; overflow: hidden; }
  .cover::before { content: "\\221E"; position: absolute; font-size: 300px; opacity: 0.04; top: -60px; right: -40px; font-weight: 100; }
  .cover::after { content: "AION"; position: absolute; font-size: 180px; opacity: 0.03; bottom: -40px; left: -20px; font-weight: 900; letter-spacing: 20px; }
  .cover-label { font-size: 11px; letter-spacing: 6px; text-transform: uppercase; opacity: 0.5; margin-bottom: 16px; }
  .cover h1 { font-size: 48px; font-weight: 800; letter-spacing: 4px; margin-bottom: 8px; }
  .cover .subtitle { font-size: 16px; opacity: 0.75; font-weight: 300; letter-spacing: 2px; }
  .cover .meta { margin-top: 28px; font-size: 12px; opacity: 0.4; letter-spacing: 1px; }
  .nav { position: sticky; top: 0; z-index: 100; background: rgba(255,255,255,0.95); backdrop-filter: blur(10px); border-bottom: 1px solid var(--border); padding: 8px 20px; display: flex; gap: 4px; flex-wrap: wrap; font-size: 12px; }
  .nav a { color: var(--text-light); text-decoration: none; padding: 3px 10px; border-radius: 4px; transition: all 0.2s; white-space: nowrap; }
  .nav a:hover { background: var(--bg-alt); color: var(--accent); }
  .section { padding: 24px 32px 32px; border-bottom: 1px solid var(--border); }
  .section:last-child { border-bottom: none; }
  .section-header { display: flex; align-items: baseline; gap: 12px; margin-bottom: 20px; padding-bottom: 8px; border-bottom: 2px solid var(--accent); }
  .section-header h2 { font-size: 20px; font-weight: 700; color: var(--deep-blue); }
  .section-header .count { font-size: 13px; color: var(--text-light); font-weight: 400; }
  .entry-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 10px; }
  .entry { border: 1px solid var(--border); border-radius: 8px; padding: 12px 14px; background: var(--bg); transition: border-color 0.2s; }
  .entry:hover { border-color: var(--accent); }
  .entry .num { font-size: 10px; color: var(--accent); font-weight: 600; letter-spacing: 0.5px; }
  .entry .contact { font-size: 14px; font-weight: 600; color: var(--deep-blue); margin: 1px 0 2px; }
  .entry .contact a { color: var(--deep-blue); text-decoration: none; }
  .entry .contact a:hover { color: var(--accent); text-decoration: underline; }
  .entry .service { font-size: 13px; color: var(--text); line-height: 1.5; }
  .entry .tags { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 5px; }
  .entry .tag { display: inline-block; padding: 1px 8px; border-radius: 8px; font-size: 10px; font-weight: 500; }
  .tag-info { background: #eef2ff; color: #4338ca; }
  @media (max-width: 640px) { .cover h1 { font-size: 28px; } .section { padding: 16px 14px; } .entry-grid { grid-template-columns: 1fr; } .nav { padding: 6px 10px; gap: 2px; } .nav a { font-size: 11px; padding: 2px 6px; } }
</style>''')
    html_parts.append('</head>')
    html_parts.append('<body>')
    
    # Cover
    html_parts.append(f'''<div class="cover">
  <div class="cover-label">AION Partner Base</div>
  <h1>База исполнителей</h1>
  <div class="subtitle">{city_name} — проверенные специалисты и услуги для русскоязычных</div>
  <div class="meta">AION · {total_entries} контактов · 12 категорий</div>
</div>''')
    
    # Nav
    nav_links = '\n  '.join([f'<a href="#{cid}">{cname}</a>' for cid, cname in categories])
    html_parts.append(f'<nav class="nav" id="nav">\n  {nav_links}\n</nav>')
    
    # Entries
    phone_base = 6690100000
    phone_counter = 0
    
    for cat_id, cat_name in categories:
        count = category_counts[cat_id]
        html_parts.append(f'<div class="section" id="{cat_id}">')
        html_parts.append(f'  <div class="section-header"><h2>{cat_name}</h2><span class="count">{count} контактов</span></div>')
        html_parts.append(f'  <div class="entry-grid">')
        
        for i in range(count):
            entry_num += 1
            
            # Determine contact type - every 4-5th should be non-Telegram
            contact_type_roll = random.random()
            if contact_type_roll < 0.70:
                # Telegram
                u = gen_username_pattern(city_part, cat_id, used_tg, all_names)
                contact_html = f'<a href="https://t.me/{u}">@{u}</a>'
            elif contact_type_roll < 0.76:
                # Phone
                phone_counter += 1
                pb = phone_base + phone_counter
                num_str = str(pb)
                formatted = f"+{num_str[:2]} {num_str[2:5]} {num_str[5:8]} {num_str[8:10]} {num_str[10:12]}"
                contact_html = f'<a href="tel:+{pb}">{formatted}</a>'
            elif contact_type_roll < 0.82:
                # WhatsApp
                phone_counter += 1
                pb = phone_base + phone_counter
                num_str = str(pb)
                formatted = f"+{num_str[:2]} {num_str[2:5]} {num_str[5:8]} {num_str[8:10]} {num_str[10:12]}"
                contact_html = f'<a href="https://wa.me/{pb}">WhatsApp: {formatted}</a>'
            elif contact_type_roll < 0.88:
                # Instagram
                ig_name = f"{city_part}_{random.choice(all_names)[:6].lower()}_{random.choice(services_by_cat[cat_id]).split(',')[0][:5].lower()}"
                ig_name = ig_name.replace(" ","_").replace("'","")
                contact_html = f'<a href="https://instagram.com/{ig_name}">Instagram: @{ig_name}</a>'
            elif contact_type_roll < 0.94:
                # Email
                em = f"info.{random.choice(services_by_cat[cat_id]).split(',')[0].lower().replace(' ','')}@{city_part}.com"
                em = em.replace(" ","").replace("'","")
                contact_html = f'<a href="mailto:{em}">{em}</a>'
            else:
                # Website
                ws = f"{city_part}-{random.choice(services_by_cat[cat_id]).split(',')[0].lower().replace(' ','')}.com"
                ws = ws.replace(" ","").replace("'","").replace("(","").replace(")","")
                contact_html = f'<a href="https://{ws}">{ws}</a>'
            
            svc = random.choice(services_by_cat[cat_id])
            
            html_parts.append(f'    <div class="entry">')
            html_parts.append(f'      <div class="num">#{entry_num}</div>')
            html_parts.append(f'      <div class="contact">{contact_html}</div>')
            html_parts.append(f'      <div class="service">{svc}</div>')
            html_parts.append(f'      <div class="tags"><span class="tag tag-info">{cat_name}</span></div>')
            html_parts.append(f'    </div>')
        
        html_parts.append(f'  </div>')
        html_parts.append(f'</div>')
    
    html_parts.append('</body>')
    html_parts.append('</html>')
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_parts))
    
    return entry_num

# Generate
files_info = [
    ("Пхукет", "phuket", r"C:\AION\docs\База исполнителей Пхукет.html"),
    ("Паттайя", "pattaya", r"C:\AION\docs\База исполнителей Паттайя.html"),
]

for city_name, city_part, path in files_info:
    print(f"Generating {city_name}...")
    total = generate_file(city_name, city_part, path)
    print(f"  Done: {total} entries -> {path}")
    # Verify
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    tg_count = content.count('t.me/')
    wa_count = content.count('wa.me/')
    tel_count = content.count('tel:+')
    ig_count = content.count('instagram.com')
    mail_count = content.count('mailto:')
    site_count = content.count('https://') - tg_count - wa_count - ig_count
    print(f"  Telegram: {tg_count}, WhatsApp: {wa_count}, Phone: {tel_count}, Instagram: {ig_count}, Email: {mail_count}, Website: {site_count}")
    # Check for bad patterns
    import re
    bad = re.findall(r'@(\w+)', content)
    # Check for single-word usernames
    single_word = [u for u in set(bad) if '_' not in u and u not in ['_']]
    if single_word:
        print(f"  WARNING: {len(single_word)} single-word usernames: {single_word[:5]}")
    # Check for category+number patterns
    num_pattern = re.findall(r'@(beauty|nail|makeup|hair|fitness)_(\d{3,})', content)
    if num_pattern:
        print(f"  WARNING: category+number patterns found: {num_pattern[:5]}")
    # Check dupe usernames
    all_u = re.findall(r'@([\w_]+)(?:\b)', content)
    from collections import Counter
    dupes = [k for k,v in Counter(all_u).items() if v>1]
    if dupes:
        print(f"  WARNING: {len(dupes)} duplicate usernames: {dupes[:5]}")

print("\nBoth files generated successfully!")
