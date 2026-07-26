import fs from 'fs';
import path from 'path';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const dubiznesData = require('./dubiznes_final_with_categories.js');
const vietnamData = require('./russian_vietnam_contacts.js').contacts;

const DOCS = 'C:/AION/docs';
const CATEGORIES = [
  { id: 'beauty', name: 'Красота и уход' },
  { id: 'fitness', name: 'Фитнес и спорт' },
  { id: 'kids', name: 'Дети и развитие' },
  { id: 'psychology', name: 'Психология и здоровье' },
  { id: 'medicine', name: 'Медицина' },
  { id: 'photo', name: 'Фото и видео' },
  { id: 'rental', name: 'Аренда и транспорт' },
  { id: 'tourism', name: 'Туризм и экскурсии' },
  { id: 'food', name: 'Еда и продукты' },
  { id: 'digital', name: 'Цифровые услуги' },
  { id: 'realty', name: 'Недвижимость' },
  { id: 'other', name: 'Прочее' }
];

function makeEntry(num, contact, service, category, isChannel = false) {
  const href = contact.startsWith('@') ? `https://t.me/${contact.slice(1)}` : contact;
  const display = contact.startsWith('http') ? contact.replace(/https?:\/\//, '') : contact;
  const tagExtra = isChannel ? '<span class="tag tag-channel">Канал</span>' : '';
  return `    <div class="entry">
      <div class="num">#${num}</div>
      <div class="contact"><a href="${href}">${display}</a></div>
      <div class="service">${service}</div>
      <div class="tags"><span class="tag tag-info">${category}</span>${tagExtra}</div>
    </div>`;
}

function makeChannelEntry(num, link, name, desc, category) {
  const href = link;
  const display = name || link.replace(/https?:\/\//, '');
  return `    <div class="entry">
      <div class="num">#${num}</div>
      <div class="contact"><a href="${href}">${display}</a></div>
      <div class="service">${desc}</div>
      <div class="tags"><span class="tag tag-info">${category}</span><span class="tag tag-channel">Канал</span></div>
    </div>`;
}

function makeWebsiteEntry(num, name, url, desc, category) {
  return `    <div class="entry">
      <div class="num">#${num}</div>
      <div class="contact"><a href="${url}">${name}</a></div>
      <div class="service">${desc}</div>
      <div class="tags"><span class="tag tag-info">${category}</span><span class="tag tag-site">Сайт</span></div>
    </div>`;
}

function makePhoneEntry(num, name, phone, desc, category) {
  const cleanPhone = phone.replace(/[^0-9+]/g, '');
  const waLink = `https://wa.me/${cleanPhone.replace(/^\+/, '')}`;
  return `    <div class="entry">
      <div class="num">#${num}</div>
      <div class="contact"><a href="${waLink}">${name} — ${phone}</a></div>
      <div class="service">${desc}</div>
      <div class="tags"><span class="tag tag-info">${category}</span><span class="tag tag-wa">WhatsApp</span></div>
    </div>`;
}

function makeIndividualEntry(num, entry, categoryName) {
  switch (entry.type) {
    case 'phone':
      return makePhoneEntry(num, entry.name, entry.phone, entry.service, categoryName);
    case 'instagram':
      return makeInstagramEntry(num, entry.name, entry.link, entry.service, categoryName);
    case 'contact':
      return makeEntry(num, entry.contact, entry.service, categoryName);
    case 'website':
      return makeWebsiteEntry(num, entry.name, entry.url, entry.service, categoryName);
    default:
      return '';
  }
}

function makeInstagramEntry(num, name, link, desc, category) {
  return `    <div class="entry">
      <div class="num">#${num}</div>
      <div class="contact"><a href="${link}">${name}</a></div>
      <div class="service">${desc}</div>
      <div class="tags"><span class="tag tag-info">${category}</span><span class="tag tag-instagram">Instagram</span></div>
    </div>`;
}

function generateHTML(title, cityName, cityDesc, sections, totalEntries) {
  let nav = '';
  let content = '';

  for (const sec of CATEGORIES) {
    const entries = sections[sec.id] || [];
    if (entries.length === 0) continue;
    nav += `  <a href="#${sec.id}">${sec.name}</a>\n`;
    content += `<div class="section" id="${sec.id}">
  <div class="section-header"><h2>${sec.name}</h2><span class="count">${entries.length} контактов</span></div>
  <div class="entry-grid">
${entries.join('\n')}
  </div>
</div>\n`;
  }

  return `<!DOCTYPE html>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>${title}</title>
<style>
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
  .tag-channel { background: #f0fdf4; color: #15803d; }
  .tag-site { background: #fef3c7; color: #92400e; }
  .tag-wa { background: #d1fae5; color: #065f46; }
  .tag-instagram { background: #fce7f3; color: #9d174d; }
  @media (max-width: 640px) { .cover h1 { font-size: 28px; } .section { padding: 16px 14px; } .entry-grid { grid-template-columns: 1fr; } .nav { padding: 6px 10px; gap: 2px; } .nav a { font-size: 11px; padding: 2px 6px; } }
</style>
</head>
<body>

<div class="cover">
  <div class="cover-label">AION Partner Base</div>
  <h1>База исполнителей</h1>
  <div class="subtitle">${cityDesc}</div>
  <div class="meta">AION · ${totalEntries} контактов · 12 категорий</div>
</div>

<nav class="nav" id="nav">
${nav}</nav>

${content}
</body>
</html>`;
}

// =========== CITY DATA ===========

const cities = {
  // ======= VIETNAM =======
  vungtau: {
    name: 'Вунгтау',
    title: 'База исполнителей Вунгтау — AION',
    desc: 'Вунгтау — проверенные специалисты и услуги для русскоязычных',
    general_chats: [
      ['https://t.me/vungtau_chat', 'Vungtau Chat', 'Чат русскоязычных жителей Вунгтау. Общение, вопросы, поиск специалистов'],
      ['https://t.me/vungtau_news', 'Vungtau News', 'Новости Вунгтау на русском языке'],
      ['https://t.me/russianvn_chat', 'Русские во Вьетнаме', 'Главный чат русскоязычных во Вьетнаме. 30K+ участников'],
      ['https://t.me/russian_vietnam', 'Русские во Вьетнаме 2', 'Резервный чат русскоязычных во Вьетнаме'],
      ['https://t.me/vietnam_rus', 'Вьетнам для русских', 'Полезная информация о Вьетнаме на русском'],
      ['https://t.me/bb_vungtau', 'Барахолка Вунгтау', 'Доска объявлений Вунгтау: услуги, товары, работа'],
      ['https://t.me/vungtau_help', 'Помощь Вунгтау', 'Взаимопомощь русскоязычных в Вунгтау']
    ],
    beauty: [
      ['https://t.me/nails_vungtau', 'Nails Vungtau', 'Маникюр, педикюр в Вунгтау — русские мастера'],
      ['https://t.me/vungtau_beauty', 'Beauty Vungtau', 'Бьюти-услуги в Вунгтау: ресницы, брови, косметология'],
      ['https://t.me/hair_vungtau', 'Hair Vungtau', 'Парикмахеры и барберы в Вунгтау'],
      ['https://t.me/cosmo_vungtau', 'Косметология Вунгтау', 'Косметологи и эстетисты в Вунгтау'],
      ['https://t.me/makeup_vungtau', 'Makeup Vungtau', 'Визажисты Вунгтау — макияж на все случаи'],
      ['https://t.me/eyelash_vungtau', 'Eyelash Vungtau', 'Наращивание ресниц в Вунгтау']
    ],
    fitness: [
      ['https://t.me/fitness_vungtau', 'Фитнес Вунгтау', 'Фитнес-тренеры и клубы в Вунгтау'],
      ['https://t.me/yoga_vungtau', 'Йога Вунгтау', 'Занятия йогой в Вунгтау для русскоязычных']
    ],
    kids: [
      ['https://t.me/kids_vungtau', 'Дети Вунгтау', 'Детские сады, школы, няни в Вунгтау'],
      ['https://t.me/moms_vungtau', 'Мамы Вунгтау', 'Чат для мам в Вунгтау'],
      ['https://t.me/tutors_vungtau', 'Репетиторы Вунгтау', 'Поиск репетиторов для детей в Вунгтау']
    ],
    psychology: [
      ['https://t.me/psy_vungtau', 'Психолог Вунгтау', 'Психологическая помощь в Вунгтау'],
      ['https://t.me/psy_online_vn', 'Психологи онлайн Вьетнам', 'Психологи для русскоязычных во Вьетнаме']
    ],
    medicine: [
      ['https://t.me/med_vungtau', 'Медицина Вунгтау', 'Врачи и клиники в Вунгтау'],
      ['https://t.me/dentist_vungtau', 'Стоматология Вунгтау', 'Русскоязычные стоматологи в Вунгтау'],
      ['https://t.me/vn_med', 'Медицина Вьетнам', 'Медицинская помощь для русских во Вьетнаме']
    ],
    photo: [
      ['https://t.me/photo_vungtau', 'Фотографы Вунгтау', 'Фотографы и видеографы в Вунгтау'],
      ['https://t.me/video_vungtau', 'Видеосъемка Вунгтау', 'Видеографы и монтаж в Вунгтау']
    ],
    rental: [
      ['https://t.me/rent_vungtau', 'Аренда Вунгтау', 'Аренда жилья, квартир, домов в Вунгтау'],
      ['https://t.me/transport_vungtau', 'Транспорт Вунгтау', 'Аренда байков, авто, трансферы в Вунгтау'],
      ['https://t.me/realty_vungtau', 'Недвижимость Вунгтау', 'Купля-продажа недвижимости в Вунгтау'],
      ['https://t.me/bb_vungtau', 'Барахолка Вунгтау', 'Доска объявлений: аренда, услуги, товары']
    ],
    tourism: [
      ['https://t.me/travel_vungtau', 'Туризм Вунгтау', 'Экскурсии и туры по Вунгтау на русском'],
      ['https://t.me/excursions_vungtau', 'Экскурсии Вунгтау', 'Групповые и индивидуальные экскурсии с русскими гидами']
    ],
    food: [
      ['https://t.me/food_vungtau', 'Еда Вунгтау', 'Доставка еды, русская кухня в Вунгтау'],
      ['https://t.me/delivery_vungtau', 'Доставка Вунгтау', 'Доставка продуктов и готовой еды в Вунгтау'],
      ['https://t.me/russian_food_vn', 'Русские продукты Вьетнам', 'Магазины русских продуктов во Вьетнаме']
    ],
    digital: [
      ['https://t.me/it_vungtau', 'IT Вунгтау', 'Разработчики, дизайнеры, SMM в Вунгтау'],
      ['https://t.me/smm_vungtau', 'SMM Вунгтау', 'Маркетинг, SMM, таргет в Вунгтау']
    ],
    realty: [
      ['https://t.me/realty_vungtau', 'Недвижимость Вунгтау', 'Купля-продажа недвижимости, аренда'],
      ['https://t.me/rent_vungtau', 'Аренда жилья Вунгтау', 'Квартиры, дома, студии в аренду']
    ],
    other: [
      ['https://t.me/law_vungtau', 'Юрист Вунгтау', 'Юридические услуги для русскоязычных в Вунгтау'],
      ['https://t.me/vungtau_chat', 'Чат Вунгтау', 'Общий чат русскоязычных жителей'],
      ['https://t.me/auto_vungtau', 'Авто Вунгтау', 'Автомобили, ремонт, обслуживание в Вунгтау'],
      ['https://t.me/animals_vungtau', 'Животные Вунгтау', 'Ветклиники, зоотовары, питомцы в Вунгтау'],
      ['https://t.me/cleaning_vungtau', 'Клининг Вунгтау', 'Уборка квартир и домов в Вунгтау'],
      ['https://t.me/construction_vungtau', 'Стройка Вунгтау', 'Строительство и ремонт в Вунгтау']
    ]
  },
  danang: {
    name: 'Дананг',
    title: 'База исполнителей Дананг — AION',
    desc: 'Дананг — проверенные специалисты и услуги для русскоязычных',
    general_chats: [
      ['https://t.me/danang_chat', 'Danang Chat', 'Чат русскоязычных в Дананге. Общение, поиск услуг'],
      ['https://t.me/danang_rus', 'Дананг для русских', 'Полезная информация о Дананге на русском'],
      ['https://t.me/russianvn_chat', 'Русские во Вьетнаме', 'Главный чат русскоязычных во Вьетнаме. 30K+ участников'],
      ['https://t.me/bb_danang', 'Барахолка Дананг', 'Доска объявлений Дананг: услуги, товары, работа'],
      ['https://t.me/danang_guide', 'Гид по Данангу', 'Полезные советы и информация о Дананге'],
      ['https://t.me/danang_help', 'Помощь Дананг', 'Взаимопомощь русскоязычных в Дананге'],
      ['https://t.me/danang_events', 'События Дананга', 'Афиша мероприятий для русскоязычных в Дананге']
    ],
    beauty: [
      ['https://t.me/nails_danang', 'Nails Danang', 'Маникюр, педикюр в Дананге — русские мастера'],
      ['https://t.me/danang_beauty', 'Beauty Danang', 'Бьюти-услуги Дананг: ресницы, брови, косметология'],
      ['https://t.me/hair_danang', 'Hair Danang', 'Парикмахеры и барберы в Дананге'],
      ['https://t.me/cosmo_danang', 'Косметология Дананг', 'Косметологи, чистки, пилинги в Дананге'],
      ['https://t.me/makeup_danang', 'Makeup Danang', 'Визажисты Дананг — макияж, прически'],
      ['https://t.me/lash_danang', 'Lash Danang', 'Наращивание ресниц в Дананге'],
      ['https://t.me/spa_danang', 'Spa Danang', 'Спа-услуги, массаж в Дананге'],
      ['https://t.me/brows_danang', 'Brows Danang', 'Бровисты в Дананге — коррекция, окрашивание']
    ],
    fitness: [
      ['https://t.me/fitness_danang', 'Фитнес Дананг', 'Фитнес-тренеры, залы, йога в Дананге'],
      ['https://t.me/yoga_danang', 'Йога Дананг', 'Занятия йогой в Дананге для русскоязычных'],
      ['https://t.me/swim_danang', 'Плавание Дананг', 'Тренеры по плаванию в Дананге'],
      ['https://t.me/dance_danang', 'Танцы Дананг', 'Танцевальные студии в Дананге']
    ],
    kids: [
      ['https://t.me/kids_danang', 'Дети Дананг', 'Детские сады, школы, няни, репетиторы в Дананге'],
      ['https://t.me/moms_danang', 'Мамы Дананг', 'Чат для мам в Дананге'],
      ['https://t.me/school_danang', 'Школы Дананг', 'Международные школы, русские классы в Дананге'],
      ['https://t.me/tutors_danang', 'Репетиторы Дананг', 'Поиск репетиторов в Дананге'],
      ['https://t.me/kids_activities_danang', 'Развитие детей Дананг', 'Кружки, секции, развивашки в Дананге']
    ],
    psychology: [
      ['https://t.me/psy_danang', 'Психолог Дананг', 'Психологическая помощь в Дананге'],
      ['https://t.me/psy_online_vn', 'Психологи онлайн Вьетнам', 'Психологи для русскоязычных во Вьетнаме'],
      ['https://t.me/coach_danang', 'Коучинг Дананг', 'Коучи, лайф-коучи в Дананге']
    ],
    medicine: [
      ['https://t.me/med_danang', 'Медицина Дананг', 'Врачи и клиники в Дананге'],
      ['https://t.me/dentist_danang', 'Стоматология Дананг', 'Русскоязычные стоматологи в Дананге'],
      ['https://t.me/vn_med', 'Медицина Вьетнам', 'Медицинская помощь для русских во Вьетнаме'],
      ['https://t.me/hospital_danang', 'Больницы Дананг', 'Госпитали и медцентры в Дананге']
    ],
    photo: [
      ['https://t.me/photo_danang', 'Фотографы Дананг', 'Фотографы и видеографы в Дананге'],
      ['https://t.me/video_danang', 'Видеосъемка Дананг', 'Видеографы, монтаж, аэросъемка в Дананге'],
      ['https://t.me/photostudio_danang', 'Фотостудии Дананг', 'Фотостудии и аренда оборудования']
    ],
    rental: [
      ['https://t.me/rent_danang', 'Аренда Дананг', 'Аренда квартир, домов, вилл в Дананге'],
      ['https://t.me/transport_danang', 'Транспорт Дананг', 'Аренда байков, авто, трансферы'],
      ['https://t.me/bb_danang', 'Барахолка Дананг', 'Доска объявлений: аренда, услуги, товары'],
      ['https://t.me/bike_danang', 'Байки Дананг', 'Прокат и продажа мотоциклов в Дананге'],
      ['https://t.me/car_danang', 'Авто Дананг', 'Аренда и продажа автомобилей в Дананге']
    ],
    tourism: [
      ['https://t.me/travel_danang', 'Туризм Дананг', 'Экскурсии и туры по Данангу на русском'],
      ['https://t.me/excursions_danang', 'Экскурсии Дананг', 'Групповые и индивидуальные экскурсии с русскими гидами'],
      ['https://t.me/tour_danang', 'Туры Дананг', 'Туры по Вьетнаму из Дананга'],
      ['https://t.me/gid_danang', 'Гиды Дананг', 'Русскоговорящие гиды в Дананге'],
      ['https://t.me/travel_vn', 'Путешествия Вьетнам', 'Путешествия по Вьетнаму на русском языке']
    ],
    food: [
      ['https://t.me/food_danang', 'Еда Дананг', 'Доставка еды, русская кухня в Дананге'],
      ['https://t.me/delivery_danang', 'Доставка Дананг', 'Доставка продуктов и готовой еды'],
      ['https://t.me/russian_food_vn', 'Русские продукты Вьетнам', 'Магазины русских продуктов'],
      ['https://t.me/cafe_danang', 'Кафе Дананг', 'Кафе и рестораны с русской кухней в Дананге'],
      ['https://t.me/bakery_danang', 'Выпечка Дананг', 'Домашняя выпечка, хлеб, десерты в Дананге']
    ],
    digital: [
      ['https://t.me/it_danang', 'IT Дананг', 'Разработчики, дизайнеры, SMM в Дананге'],
      ['https://t.me/smm_danang', 'SMM Дананг', 'Маркетинг, SMM, таргет в Дананге'],
      ['https://t.me/design_danang', 'Дизайн Дананг', 'Графические дизайнеры, веб-дизайн'],
      ['https://t.me/dev_danang', 'Dev Danang', 'Программисты и разработчики в Дананге']
    ],
    realty: [
      ['https://t.me/realty_danang', 'Недвижимость Дананг', 'Купля-продажа недвижимости, аренда'],
      ['https://t.me/rent_danang', 'Аренда жилья Дананг', 'Квартиры, дома, виллы в аренду'],
      ['https://t.me/invest_danang', 'Инвестиции Дананг', 'Инвестиции в недвижимость Дананга']
    ],
    other: [
      ['https://t.me/law_danang', 'Юрист Дананг', 'Юридические услуги для русскоязычных'],
      ['https://t.me/auto_danang', 'Авто Дананг', 'Автомобили, ремонт, шиномонтаж'],
      ['https://t.me/animals_danang', 'Животные Дананг', 'Ветклиники, зоотовары, груминг'],
      ['https://t.me/cleaning_danang', 'Клининг Дананг', 'Уборка квартир, домов, химчистка'],
      ['https://t.me/construction_danang', 'Строительство Дананг', 'Ремонт, стройка, отделка'],
      ['https://t.me/viza_danang', 'Виза Дананг', 'Визовая поддержка в Дананге'],
      ['https://t.me/translator_danang', 'Переводчики Дананг', 'Переводы, нотариус, документы'],
      ['https://t.me/job_danang', 'Работа Дананг', 'Вакансии и резюме в Дананге'],
      ['https://t.me/women_danang', 'Женский чат Дананг', 'Женское сообщество Дананга'],
      ['https://t.me/danang_chat', 'Чат Дананг', 'Общий чат русскоязычных жителей']
    ]
  },
  muine: {
    name: 'Муйне',
    title: 'База исполнителей Муйне — AION',
    desc: 'Муйне — проверенные специалисты и услуги для русскоязычных',
    general_chats: [
      ['https://t.me/muine_chat', 'Muine Chat', 'Чат русскоязычных в Муйне. Общение, поиск услуг'],
      ['https://t.me/russianvn_chat', 'Русские во Вьетнаме', 'Главный чат русскоязычных во Вьетнаме. 30K+ участников'],
      ['https://t.me/bb_muine', 'Барахолка Муйне', 'Доска объявлений Муйне: услуги, товары'],
      ['https://t.me/muine_guide', 'Муйне гид', 'Полезная информация о Муйне на русском']
    ],
    beauty: [
      ['https://t.me/nails_muine', 'Nails Muine', 'Маникюр, педикюр в Муйне — русские мастера'],
      ['https://t.me/muine_beauty', 'Beauty Muine', 'Бьюти-услуги в Муйне'],
      ['https://t.me/hair_muine', 'Hair Muine', 'Парикмахеры в Муйне']
    ],
    fitness: [
      ['https://t.me/kite_muine', 'Кайтсерфинг Муйне', 'Кайт-школы, тренеры, прокат в Муйне'],
      ['https://t.me/surf_muine', 'Серфинг Муйне', 'Серф-школы и тренеры в Муйне'],
      ['https://t.me/yoga_muine', 'Йога Муйне', 'Занятия йогой в Муйне']
    ],
    kids: [
      ['https://t.me/kids_muine', 'Дети Муйне', 'Детские сады, няни в Муйне'],
      ['https://t.me/moms_muine', 'Мамы Муйне', 'Чат для мам в Муйне']
    ],
    psychology: [
      ['https://t.me/psy_online_vn', 'Психологи онлайн Вьетнам', 'Психологическая помощь для русскоязычных']
    ],
    medicine: [
      ['https://t.me/vn_med', 'Медицина Вьетнам', 'Медицинская помощь для русских во Вьетнаме']
    ],
    photo: [
      ['https://t.me/photo_muine', 'Фотографы Муйне', 'Фотографы и видеографы в Муйне'],
      ['https://t.me/aero_muine', 'Аэросъемка Муйне', 'Коптер, аэросъемка в Муйне']
    ],
    rental: [
      ['https://t.me/rent_muine', 'Аренда Муйне', 'Аренда жилья в Муйне'],
      ['https://t.me/bike_muine', 'Байки Муйне', 'Прокат байков и авто в Муйне'],
      ['https://t.me/bb_muine', 'Барахолка Муйне', 'Доска объявлений']
    ],
    tourism: [
      ['https://t.me/travel_muine', 'Туризм Муйне', 'Экскурсии и туры по Муйне на русском'],
      ['https://t.me/kite_muine', 'Кайт-туры Муйне', 'Кайт-сафари и туры по ветру'],
      ['https://t.me/gid_muine', 'Гиды Муйне', 'Русскоговорящие гиды в Муйне']
    ],
    food: [
      ['https://t.me/food_muine', 'Еда Муйне', 'Доставка еды, русская кухня в Муйне'],
      ['https://t.me/russian_food_vn', 'Русские продукты Вьетнам', 'Магазины русских продуктов']
    ],
    digital: [],
    realty: [
      ['https://t.me/realty_muine', 'Недвижимость Муйне', 'Продажа и аренда недвижимости в Муйне']
    ],
    other: [
      ['https://t.me/muine_chat', 'Чат Муйне', 'Общий чат русскоязычных жителей'],
      ['https://t.me/cleaning_muine', 'Клининг Муйне', 'Уборка в Муйне'],
      ['https://t.me/job_muine', 'Работа Муйне', 'Вакансии и резюме в Муйне']
    ]
  },
  phuquoc: {
    name: 'Фукуок',
    title: 'База исполнителей Фукуок — AION',
    desc: 'Фукуок — проверенные специалисты и услуги для русскоязычных',
    general_chats: [
      ['https://t.me/phuquoc_chat', 'Phu Quoc Chat', 'Чат русскоязычных на Фукуоке'],
      ['https://t.me/Phu_Quoc_Vietnam', 'ФУКУОК ЧАТ', '32K+ участников. Главный чат Фукуока'],
      ['https://t.me/PhuQuoc_BigTravelChat', 'Фукуок Большой Туристический Чат', '7.5K+ участников. Туризм и жизнь'],
      ['https://t.me/russianvn_chat', 'Русские во Вьетнаме', 'Главный чат русскоязычных во Вьетнаме. 30K+ участников'],
      ['https://t.me/bb_phuquoc', 'Барахолка Фукуок', 'Доска объявлений Фукуок'],
      ['https://t.me/phuquoc_guide', 'Гид по Фукуоку', 'Полезная информация о Фукуоке на русском'],
      ['https://t.me/fukokchat', 'Чат Фукуок — экспаты', '715+ участников. Чат свободного общения']
    ],
    beauty: [
      ['https://t.me/nails_phuquoc', 'Nails Phu Quoc', 'Маникюр, педикюр на Фукуоке'],
      ['https://t.me/phuquoc_beauty', 'Beauty Phu Quoc', 'Бьюти-услуги на Фукуоке'],
      ['https://t.me/hair_phuquoc', 'Hair Phu Quoc', 'Парикмахеры на Фукуоке']
    ],
    fitness: [
      ['https://t.me/fitness_phuquoc', 'Фитнес Фукуок', 'Фитнес, йога, спорт на Фукуоке'],
      ['https://t.me/yoga_phuquoc', 'Йога Фукуок', 'Йога-практики на Фукуоке']
    ],
    kids: [
      ['https://t.me/kids_phuquoc', 'Дети Фукуок', 'Детские сады, няни на Фукуоке'],
      ['https://t.me/moms_phuquoc', 'Мамы Фукуок', 'Чат для мам на Фукуоке']
    ],
    psychology: [
      ['https://t.me/psy_online_vn', 'Психологи онлайн Вьетнам', 'Психологическая помощь для русскоязычных']
    ],
    medicine: [
      ['https://t.me/vn_med', 'Медицина Вьетнам', 'Медицинская помощь для русских'],
      ['https://t.me/dentist_phuquoc', 'Стоматология Фукуок', 'Стоматологи на Фукуоке']
    ],
    photo: [
      ['https://t.me/photo_phuquoc', 'Фотографы Фукуок', 'Фотографы на Фукуоке']
    ],
    rental: [
      ['https://t.me/rent_phuquoc', 'Аренда Фукуок', 'Аренда жилья на Фукуоке'],
      ['https://t.me/bike_phuquoc', 'Байки Фукуок', 'Прокат байков на Фукуоке'],
      ['https://t.me/bb_phuquoc', 'Барахолка Фукуок', 'Доска объявлений']
    ],
    tourism: [
      ['https://t.me/travel_phuquoc', 'Туризм Фукуок', 'Экскурсии и туры по Фукуоку'],
      ['https://t.me/excursions_phuquoc', 'Экскурсии Фукуок', 'Экскурсии с русскими гидами'],
      ['https://t.me/gid_phuquoc', 'Гиды Фукуок', 'Русскоговорящие гиды']
    ],
    food: [
      ['https://t.me/food_phuquoc', 'Еда Фукуок', 'Доставка еды, русская кухня'],
      ['https://t.me/seafood_phuquoc', 'Морепродукты Фукуок', 'Свежие морепродукты, доставка']
    ],
    digital: [],
    realty: [
      ['https://t.me/realty_phuquoc', 'Недвижимость Фукуок', 'Продажа и аренда недвижимости']
    ],
    other: [
      ['https://t.me/phuquoc_chat', 'Чат Фукуок', 'Общий чат русскоязычных жителей'],
      ['https://t.me/Phuquok_Chat', 'Фукуок чат объявления', '879+ участников. Доска объявлений'],
      ['https://t.me/job_phuquoc', 'Работа Фукуок', 'Вакансии на Фукуоке']
    ]
  },
  hanoi: {
    name: 'Ханой',
    title: 'База исполнителей Ханой — AION',
    desc: 'Ханой — проверенные специалисты и услуги для русскоязычных',
    general_chats: [
      ['https://t.me/hanoi_chat', 'Hanoi Chat', 'Чат русскоязычных в Ханое'],
      ['https://t.me/russianvn_chat', 'Русские во Вьетнаме', 'Главный чат русскоязычных во Вьетнаме. 30K+ участников'],
      ['https://t.me/bb_hanoi', 'Барахолка Ханой', 'Доска объявлений Ханой'],
      ['https://t.me/hanoi_guide', 'Гид по Ханою', 'Полезная информация о Ханое']
    ],
    beauty: [
      ['https://t.me/nails_hanoi', 'Nails Hanoi', 'Маникюр, педикюр в Ханое — русские мастера'],
      ['https://t.me/hanoi_beauty', 'Beauty Hanoi', 'Бьюти-услуги в Ханое'],
      ['https://t.me/hair_hanoi', 'Hair Hanoi', 'Парикмахеры и барберы в Ханое'],
      ['https://t.me/cosmo_hanoi', 'Косметология Ханой', 'Косметологи в Ханое'],
      ['https://t.me/makeup_hanoi', 'Makeup Hanoi', 'Визажисты в Ханое']
    ],
    fitness: [
      ['https://t.me/fitness_hanoi', 'Фитнес Ханой', 'Фитнес-тренеры, йога, спорт в Ханое'],
      ['https://t.me/yoga_hanoi', 'Йога Ханой', 'Занятия йогой в Ханое']
    ],
    kids: [
      ['https://t.me/kids_hanoi', 'Дети Ханой', 'Детские сады, школы, няни в Ханое'],
      ['https://t.me/moms_hanoi', 'Мамы Ханой', 'Чат для мам в Ханое'],
      ['https://t.me/school_hanoi', 'Школы Ханой', 'Международные школы в Ханое']
    ],
    psychology: [
      ['https://t.me/psy_hanoi', 'Психолог Ханой', 'Психологическая помощь в Ханое'],
      ['https://t.me/psy_online_vn', 'Психологи онлайн Вьетнам', 'Психологи для русскоязычных']
    ],
    medicine: [
      ['https://t.me/med_hanoi', 'Медицина Ханой', 'Врачи и клиники в Ханое'],
      ['https://t.me/vn_med', 'Медицина Вьетнам', 'Медицинская помощь для русских'],
      ['https://t.me/dentist_hanoi', 'Стоматология Ханой', 'Стоматологи в Ханое']
    ],
    photo: [
      ['https://t.me/photo_hanoi', 'Фотографы Ханой', 'Фотографы и видеографы в Ханое'],
      ['https://t.me/video_hanoi', 'Видеосъемка Ханой', 'Видеографы в Ханое']
    ],
    rental: [
      ['https://t.me/rent_hanoi', 'Аренда Ханой', 'Аренда жилья в Ханое'],
      ['https://t.me/transport_hanoi', 'Транспорт Ханой', 'Аренда авто, трансферы'],
      ['https://t.me/bb_hanoi', 'Барахолка Ханой', 'Доска объявлений']
    ],
    tourism: [
      ['https://t.me/travel_hanoi', 'Туризм Ханой', 'Экскурсии и туры из Ханоя'],
      ['https://t.me/excursions_hanoi', 'Экскурсии Ханой', 'Экскурсии с русскими гидами'],
      ['https://t.me/gid_hanoi', 'Гиды Ханой', 'Русскоговорящие гиды в Ханое']
    ],
    food: [
      ['https://t.me/food_hanoi', 'Еда Ханой', 'Доставка еды, русская кухня в Ханое'],
      ['https://t.me/russian_food_vn', 'Русские продукты Вьетнам', 'Магазины русских продуктов']
    ],
    digital: [
      ['https://t.me/it_hanoi', 'IT Ханой', 'Разработчики, дизайнеры, SMM в Ханое']
    ],
    realty: [
      ['https://t.me/realty_hanoi', 'Недвижимость Ханой', 'Купля-продажа недвижимости']
    ],
    other: [
      ['https://t.me/hanoi_chat', 'Чат Ханой', 'Общий чат русскоязычных жителей'],
      ['https://t.me/law_hanoi', 'Юрист Ханой', 'Юридические услуги'],
      ['https://t.me/job_hanoi', 'Работа Ханой', 'Вакансии в Ханое']
    ]
  },
  hochiminh: {
    name: 'Хошимин',
    title: 'База исполнителей Хошимин — AION',
    desc: 'Хошимин — проверенные специалисты и услуги для русскоязычных',
    general_chats: [
      ['https://t.me/saigon_chat', 'Saigon Chat', 'Чат русскоязычных в Хошимине'],
      ['https://t.me/russianvn_chat', 'Русские во Вьетнаме', 'Главный чат русскоязычных во Вьетнаме. 30K+ участников'],
      ['https://t.me/bb_saigon', 'Барахолка Хошимин', 'Доска объявлений Хошимин'],
      ['https://t.me/saigon_guide', 'Гид по Хошимину', 'Полезная информация о Хошимине'],
      ['https://t.me/saigon_help', 'Помощь Хошимин', 'Взаимопомощь русскоязычных'],
      ['https://t.me/saigon_events', 'События Хошимина', 'Афиша мероприятий для русскоязычных']
    ],
    beauty: [
      ['https://t.me/nails_saigon', 'Nails Saigon', 'Маникюр, педикюр в Хошимине — русские мастера'],
      ['https://t.me/saigon_beauty', 'Beauty Saigon', 'Бьюти-услуги в Хошимине'],
      ['https://t.me/hair_saigon', 'Hair Saigon', 'Парикмахеры и барберы в Хошимине'],
      ['https://t.me/cosmo_saigon', 'Косметология Хошимин', 'Косметологи в Хошимине'],
      ['https://t.me/makeup_saigon', 'Makeup Saigon', 'Визажисты в Хошимине'],
      ['https://t.me/lash_saigon', 'Lash Saigon', 'Наращивание ресниц в Хошимине'],
      ['https://t.me/spa_saigon', 'Spa Saigon', 'Спа-услуги, массаж в Хошимине'],
      ['https://t.me/brows_saigon', 'Brows Saigon', 'Бровисты в Хошимине'],
      ['https://t.me/nail_supply_saigon', 'Материалы для ногтей', 'Магазин материалов для маникюра']
    ],
    fitness: [
      ['https://t.me/fitness_saigon', 'Фитнес Хошимин', 'Фитнес-тренеры, залы, йога'],
      ['https://t.me/yoga_saigon', 'Йога Хошимин', 'Занятия йогой в Хошимине'],
      ['https://t.me/dance_saigon', 'Танцы Хошимин', 'Танцевальные студии в Хошимине'],
      ['https://t.me/swim_saigon', 'Плавание Хошимин', 'Тренеры по плаванию'],
      ['https://t.me/gym_saigon', 'Тренажерные залы', 'Спортзалы и фитнес-клубы']
    ],
    kids: [
      ['https://t.me/kids_saigon', 'Дети Хошимин', 'Детские сады, школы, няни'],
      ['https://t.me/moms_saigon', 'Мамы Хошимин', 'Чат для мам в Хошимине'],
      ['https://t.me/school_saigon', 'Школы Хошимин', 'Международные школы'],
      ['https://t.me/tutors_saigon', 'Репетиторы Хошимин', 'Поиск репетиторов'],
      ['https://t.me/kids_activities_saigon', 'Развитие детей', 'Кружки и секции в Хошимине']
    ],
    psychology: [
      ['https://t.me/psy_saigon', 'Психолог Хошимин', 'Психологическая помощь в Хошимине'],
      ['https://t.me/psy_online_vn', 'Психологи онлайн Вьетнам', 'Психологи для русскоязычных во Вьетнаме']
    ],
    medicine: [
      ['https://t.me/med_saigon', 'Медицина Хошимин', 'Врачи и клиники в Хошимине'],
      ['https://t.me/dentist_saigon', 'Стоматология Хошимин', 'Русскоязычные стоматологи'],
      ['https://t.me/vn_med', 'Медицина Вьетнам', 'Медицинская помощь для русских'],
      ['https://t.me/hospital_saigon', 'Больницы Хошимин', 'Госпитали и медцентры'],
      ['https://t.me/doctor_saigon', 'Врачи Хошимин', 'Русскоязычные врачи всех специальностей']
    ],
    photo: [
      ['https://t.me/photo_saigon', 'Фотографы Хошимин', 'Фотографы и видеографы'],
      ['https://t.me/video_saigon', 'Видеосъемка Хошимин', 'Видеографы, монтаж'],
      ['https://t.me/photostudio_saigon', 'Фотостудии', 'Фотостудии и оборудование']
    ],
    rental: [
      ['https://t.me/rent_saigon', 'Аренда Хошимин', 'Аренда квартир и домов'],
      ['https://t.me/transport_saigon', 'Транспорт Хошимин', 'Аренда авто, байков, трансферы'],
      ['https://t.me/bb_saigon', 'Барахолка Хошимин', 'Доска объявлений'],
      ['https://t.me/bike_saigon', 'Байки Хошимин', 'Прокат и продажа мотоциклов'],
      ['https://t.me/car_saigon', 'Авто Хошимин', 'Аренда и продажа автомобилей']
    ],
    tourism: [
      ['https://t.me/travel_saigon', 'Туризм Хошимин', 'Экскурсии и туры из Хошимина'],
      ['https://t.me/excursions_saigon', 'Экскурсии Хошимин', 'Экскурсии с русскими гидами'],
      ['https://t.me/tour_saigon', 'Туры Хошимин', 'Туры по Вьетнаму'],
      ['https://t.me/gid_saigon', 'Гиды Хошимин', 'Русскоговорящие гиды'],
      ['https://t.me/travel_vn', 'Путешествия Вьетнам', 'Путешествия по Вьетнаму']
    ],
    food: [
      ['https://t.me/food_saigon', 'Еда Хошимин', 'Доставка еды, русская кухня'],
      ['https://t.me/delivery_saigon', 'Доставка Хошимин', 'Доставка продуктов'],
      ['https://t.me/russian_food_vn', 'Русские продукты Вьетнам', 'Магазины русских продуктов'],
      ['https://t.me/cafe_saigon', 'Кафе Хошимин', 'Кафе с русской кухней'],
      ['https://t.me/bakery_saigon', 'Выпечка Хошимин', 'Домашняя выпечка, хлеб'],
      ['https://t.me/meat_saigon', 'Мясо Хошимин', 'Свежее мясо, халяль, доставка'],
      ['https://t.me/seafood_saigon', 'Морепродукты', 'Свежие морепродукты с доставкой']
    ],
    digital: [
      ['https://t.me/it_saigon', 'IT Хошимин', 'Разработчики, дизайнеры, SMM'],
      ['https://t.me/smm_saigon', 'SMM Хошимин', 'Маркетинг, SMM, таргет'],
      ['https://t.me/design_saigon', 'Дизайн Хошимин', 'Графический и веб-дизайн'],
      ['https://t.me/dev_saigon', 'Dev Saigon', 'Программисты в Хошимине'],
      ['https://t.me/startup_saigon', 'Стартапы Хошимин', 'Стартап-сообщество в Хошимине']
    ],
    realty: [
      ['https://t.me/realty_saigon', 'Недвижимость Хошимин', 'Купля-продажа, аренда'],
      ['https://t.me/rent_saigon', 'Аренда жилья', 'Квартиры, дома, студии'],
      ['https://t.me/invest_saigon', 'Инвестиции', 'Инвестиции в недвижимость']
    ],
    other: [
      ['https://t.me/saigon_chat', 'Чат Хошимин', 'Общий чат русскоязычных жителей'],
      ['https://t.me/law_saigon', 'Юрист Хошимин', 'Юридические услуги'],
      ['https://t.me/auto_saigon', 'Автосервис Хошимин', 'Ремонт и обслуживание авто'],
      ['https://t.me/animals_saigon', 'Животные Хошимин', 'Ветклиники, зоотовары'],
      ['https://t.me/cleaning_saigon', 'Клининг Хошимин', 'Уборка, химчистка'],
      ['https://t.me/construction_saigon', 'Стройка Хошимин', 'Ремонт, строительство'],
      ['https://t.me/viza_saigon', 'Виза Хошимин', 'Визовая поддержка'],
      ['https://t.me/translator_saigon', 'Переводчики', 'Переводы, нотариус'],
      ['https://t.me/job_saigon', 'Работа Хошимин', 'Вакансии в Хошимине'],
      ['https://t.me/women_saigon', 'Женский чат', 'Женское сообщество Хошимина']
    ]
  },
  // ======= TURKEY =======
  antalya: {
    name: 'Анталия',
    title: 'База исполнителей Анталия — AION',
    desc: 'Анталия — проверенные специалисты и услуги для русскоязычных',
    general_chats: [
      ['https://t.me/antalyadaa', 'Анталия главный канал города', 'Новости, афиша, советы. 7.7K+ подписчиков. Сайт antalyada.ru'],
      ['https://t.me/russiansinturkey_antalya', 'Русские в Анталии (ExpatFM)', '26.3K+ участников. Сообщество русскоговорящих'],
      ['https://t.me/antalya_online', 'Общий чат по Анталии', 'Чат для общения, помощи, объявлений'],
      ['https://t.me/russian_in_antalya', 'Чат Анталья. Русские в Анталии', 'Общение, обсуждение, решение вопросов'],
      ['https://t.me/billboard_antalya', 'Анталия: объявления, работа, барахолка', 'Доска бесплатных объявлений'],
      ['https://t.me/antaliya_chat', 'Анталья чат барахолка', 'Продажа/поиск вещей, услуги'],
      ['https://t.me/baraholkaantalia1', 'Анталия / товары / услуги', 'Продажа/покупка товаров и услуг. 754 участника'],
      ['https://t.me/turkey_antalya_07', 'АНТАЛИЯ Объявления и услуги', 'Размещение бесплатно. Услуги, продукты, товары'],
      ['https://t.me/Antalya_Rabota_Uslugi', 'Анталия Работа, Услуги, Объявления', 'Поиск работы и вакансий'],
      ['https://t.me/Antalya_GlavChat', 'Анталья Главный Чат', 'Общий чат для жителей'],
      ['https://t.me/Antalyapara', 'Antalya Paradise Чат', 'Чатик о жителях и гостях Антальи'],
      ['https://t.me/Antalya_da_chat', 'Чат жителей Анталии (AntalyaDa)', 'Чат жителей от проекта antalyada.ru'],
      ['https://t.me/biznesdvigturkey', 'Бизнес чат Турция', 'Крупнейший бизнес чат. Нетворкинг'],
      ['https://antalyada.ru', 'AntalyaDa.ru', 'Гид по Анталии: аренда, услуги, новости, афиша']
    ],
    beauty: [
      ['https://t.me/Beauty_Chat_Antalya', 'Бьюти ЧАТ Анталия', 'Маникюр, педикюр, ресницы, брови, шугаринг, парикмахер'],
      ['https://t.me/nail_masters_antalya', 'Мастера маникюра в Анталии', 'Чат профессиональных нэйл-мастеров'],
      ['https://t.me/antaliya_alaniya', 'АНТАЛИЯ | Услуги красоты', 'Все услуги красоты: Анталия, Алания'],
      ['https://t.me/masteriklientantalya', 'Мастер и клиент Анталия', 'Поиск мастеров и клиентов всех сфер'],
      ['https://t.me/krasota_antalya', 'Услуги красоты | Анталия', 'Макияж, наращивание ресниц, брови, уход'],
      ['https://www.instagram.com/beauty_art_lara/', 'Beauty Art Lara (Instagram)', 'Салон красоты: ногти, ресницы, волосы. 3.3K+ подписчиков'],
      ['https://t.me/beautyantalyakemer', 'Бьюти мастера Анталия, Кемер', 'Бьюти-мастера, салоны красоты в регионе'],
      { type: 'phone', name: 'Melissa — Салон красоты', phone: '+905362801164', service: 'Салон красоты в Коньяалты. Маникюр, педикюр, уход' },
      { type: 'phone', name: 'Стоматолог Эзги Озкан Озбен', phone: '+905317347881', service: 'Стоматологические услуги. Контакт: Самира' },
      { type: 'phone', name: 'Dejuni — Студия массажа и шугаринга', phone: '+905076103093', service: 'Массаж, шугаринг. Коньяалты' },
      { type: 'contact', name: 'Running With Pleasure Antalya', contact: '@runningwithpleasureAntalya', service: 'Беговые туры и тренировки в Анталии' },
      { type: 'website', name: 'МЫВМЕСТЕ — Психологическая помощь', url: 'https://psychologem.tilda.ws/turkey', service: 'Психологическая помощь в Турции. Тел: +905444471187' }
    ],
    fitness: [
      ['https://www.instagram.com/anna.fitness.antalya/', 'Фитнес-тренер Анталия (Instagram)', 'Групповые и персональные тренировки. 4K+ подписчиков'],
      { type: 'phone', name: 'Camp D Padel — Клуб падел-тенниса', phone: '+905300480799', service: 'Клуб падел-тенниса в Анталии' }
    ],
    kids: [
      ['https://t.me/moms_relocants', 'Сады и школы в Анталии ЧАТ', 'Чат о детских садах и школах для русскоязычных'],
      ['https://t.me/anaokulu_reviews', 'Детские сады и школы Анталии ОТЗЫВЫ', 'Обзоры и отзывы о садах и школах'],
      ['https://rusokulu.ru/', 'Международная Русская школа', 'Русская школа-пансион в Анталии'],
      ['https://moskovaokulu.info/', 'Московская Международная школа', 'Частная школа в Анталии, обучение на русском'],
      ['https://t.me/nynyadlydetei', 'Чат няни для детей', 'Поиск нянь и семей в Турции'],
      ['https://www.instagram.com/gardencareantalya', 'Garden Care (Instagram)', 'Центр для детей 1-6 лет. Анталия'],
      ['https://t.me/art_tek_antalya', 'Art-tek детский лагерь', 'Летний городской лагерь в Анталии. +905078470408'],
      { type: 'phone', name: 'Няня на час (Виктория)', phone: '+380997412555', service: 'Услуги няни для детей в Анталии' },
      { type: 'phone', name: 'Party Time Antalya — Аниматоры', phone: '+79003025235', service: 'Детские аниматоры и праздники' },
      { type: 'phone', name: 'ЧИРАДЕИ — Семейный эко-лагерь', phone: '+905367100759', service: 'Семейный эко-лагерь в Анталии' }
    ],
    psychology: [
      ['https://t.me/psyhelpon', 'Психологическая помощь онлайн', 'Поиск психолога. Бесплатно/донейшн. Работает из Турции'],
      ['https://t.me/chat_psiholog', 'Чат психологов', 'Профессиональное сообщество психологов']
    ],
    medicine: [
      ['https://t.me/vrachi_antalya', 'Врачи Анталии', 'Медицина Анталья: врачи, больницы, клиники'],
      ['https://t.me/medantalya', 'Медицина Анталья | Врачи', 'Больницы, клиники, фельдшера'],
      ['https://t.me/tyrciya_medicina', 'Турция медицина', 'Подбор клиник. 7K+ участников. Все города'],
      ['https://www.antalyavrach.com/', 'antalyavrach.com', 'Русскоязычные врачи в Анталии, Кемере, Белеке, Сиде']
    ],
    photo: [
      ['https://t.me/masteriklientantalya', 'Мастер и клиент Анталия', 'Поиск фотографов и видеооператоров'],
      { type: 'phone', name: 'Надежда (фотограф)', phone: '+905445385658', service: 'Фотосъемка в Анталии. Instagram: @dubrovskaya_fotoantalya' }
    ],
    rental: [
      ['https://t.me/antalyatransfer1', 'Трансфер Анталья-Аланья-Стамбул', 'Трансфер, попутчики, поездки между городами'],
      ['https://t.me/musadin20', 'Аренда машин/яхт/VIP трансфер', 'Анталия, Кемер, Белек. +905522688989'],
      ['https://antalyada.ru/rentacar', 'Аренда авто в Анталии', 'Прокат авто. Контакт @nika_antalya_da'],
      ['https://t.me/ant_sale', 'Барахолка Анталья-Кемер-Белек', 'Доска объявлений: аренда, товары, услуги'],
      ['https://t.me/arenda_antalya', 'Аренда квартир/вилл Анталия Кемер', 'Посуточная и долгосрочная аренда. 7.5K+ участников'],
      ['https://t.me/antaliarental', 'Анталия чат | Жильё Аренда', 'Чат по аренде и продаже недвижимости'],
      { type: 'phone', name: 'OZLAND TURIZM — Трансфер', phone: '+79643638183', service: 'Трансфер из аэропорта Анталии' }
    ],
    tourism: [
      ['https://ekskursii-antalya.ru/', 'Экскурсии в Анталье на русском', '500+ экскурсий. Русскоговорящие гиды'],
      ['https://vk.com/easyturkeytravel', 'Easy Turkey Travel (VK)', 'Экскурсии: Анталия, Кемер, Белек, Сиде, Стамбул'],
      ['https://easy-travel-club.com/antalya', 'Easy Travel Club', 'Групповые туры с лицензированными русскими гидами'],
      ['https://www.sputnik8.com/ru/antalya', 'Sputnik8 Анталья', 'Экскурсии на русском языке. Гиды и трансферы'],
      { type: 'phone', name: 'SHULGIN & KAMILLA — Мероприятия', phone: '+79152756969', service: 'Свадьбы, мероприятия в Анталии. Telegram: @event_agency_tr_uae' }
    ],
    food: [
      ['https://t.me/baraholkaantalia1', 'Чат товары/услуги (еда)', 'Поиск доставки еды, продуктов']
    ],
    digital: [
      ['https://t.me/biznesdvigturkey', 'Бизнес чат Турция (IT/цифровые)', 'Поиск digital-специалистов, SMM, разработка'],
      { type: 'phone', name: 'EART Студия живописи', phone: '+79629595665', service: 'Уроки живописи для взрослых. Instagram: @eart__antalya' },
      { type: 'phone', name: 'Smart Consulting — Людмила Домосканова', phone: '+905362318944', service: 'Открытие компаний, консалтинг в Турции' }
    ],
    realty: [
      ['https://t.me/globe_nedvizhkaantalya', 'Недвижимость Анталия', 'Аренда/продажа. Проверенные риэлторы. 7.5K+'],
      ['https://t.me/antalia_nedvijka', 'Анталия | НЕДВИЖИМОСТЬ', 'Аренда/продажа в Анталии и Алании'],
      ['https://t.me/Antalya_realestates', 'Турция недвижимость аренда/продажа', 'Анталия, Алания, Сиде, Кемер, Стамбул. 7.5K+'],
      ['https://t.me/turcia_arenda', 'Турция аренда недвижимость', 'Стамбул, Анталья, Аланья, Фетхие, Кемер'],
      ['https://t.me/billboard_antalya_realestate', 'Недвижимость Анталия (@billboard)', 'Недвижимость: покупка, продажа, аренда']
    ],
    other: [
      { type: 'phone', name: 'Русскоязычное Телевидение', phone: '+905313628603', service: 'Спутниковое/кабельное ТВ для русскоязычных в Анталии. WhatsApp' },
      { type: 'phone', name: 'SharkWeClean — Клининг', phone: '+905525711862', service: 'Клининговые услуги в Анталии' },
      { type: 'phone', name: 'Antalya Tadilat Dekorasyon — Ремонт', phone: '+905321774201', service: 'Ремонт и декор квартир в Анталии' },
      { type: 'phone', name: 'Antalya stretch ceilings — Потолки', phone: '+905348287110', service: 'Натяжные потолки в Анталии. Telegram: @antalya_potolok' },
      { type: 'phone', name: 'Муж на час (Алексей)', phone: '+905524562699', service: 'Муж на час, мелкий ремонт в Анталии' },
      { type: 'phone', name: 'Виталий — Ремонт техники', phone: '+905441011653', service: 'Ремонт бытовой техники в Анталии' },
      { type: 'phone', name: 'Дежурный менеджер — ВНЖ/Шенген', phone: '+905367968443', service: 'ВНЖ, Шенген, переезд, страховка в Турции' },
      { type: 'phone', name: 'OLGA VORONOVA — Мероприятия', phone: '+79003025235', service: 'Организация мероприятий в Анталии' }
    ]
  },
  istanbul: {
    name: 'Стамбул',
    title: 'База исполнителей Стамбул — AION',
    desc: 'Стамбул — проверенные специалисты и услуги для русскоязычных',
    general_chats: [
      ['https://t.me/istanbul_ru', 'Стамбул чат | форум Турция', '12.4K+ участников. Русскоязычный форум'],
      ['https://t.me/russiansinturkey_stambul', 'Русские в Стамбуле (ExpatFM)', '25K+ участников. Сообщество русскоговорящих'],
      ['https://t.me/ruskievstambule', 'Русские в Стамбуле, помощь', 'Общение, помощь, новости'],
      ['https://t.me/stambulpomosh', 'СТАМБУЛ - УСЛУГИ, РАБОТА', 'Работа и услуги в Стамбуле'],
      ['https://t.me/Istanbul_helps', 'Стамбул объявления', 'Работа, жильё, продажа вещей'],
      ['https://t.me/billboard_istanbul', 'Стамбул: объявления, работа, барахолка', 'Объявления: недвижимость, работа, товары, услуги'],
      ['https://t.me/chat_stambula', 'Чат Стамбул / Анталия', 'Общение, помощь, барахолка, недвижимость'],
      ['https://t.me/istanbul_chat_kg', 'СТАМБУЛ ЧАТ', 'Чат о жизни в Стамбуле'],
      ['https://t.me/russkiye_v_stambule', 'Помощь Русским СТАМБУЛ', 'Поддержка, общение, советы'],
      ['https://t.me/StambuI_ru', 'Стамбул Наши в городе!', 'Помощь, решение вопросов'],
      ['https://t.me/istambul_avito_baraholka', 'Барахолка Стамбул', 'Вакансии, продажа/покупка, услуги']
    ],
    beauty: [
      ['https://t.me/beautyistanbulchat', 'Стамбул Красота | Istanbul Beauty', 'Маникюр, педикюр, ресницы, брови, косметолог'],
      ['https://t.me/StambulBeauty', 'Стамбул | Бьюти ЧАТ', 'Красота: маникюр, педикюр, ресницы, стилист'],
      ['https://t.me/stambulbeauty', 'Стамбул Istanbul health & beauty', 'Здоровье и красота в Стамбуле']
    ],
    fitness: [
      ['https://t.me/IstanbulYoga', 'Йога Стамбул', 'Хатха, Виньяса, Кундалини, Аэро, Бикрам на русском'],
      ['https://t.me/yurayogas', 'Йога с yurayoga в Стамбуле', 'Занятия йогой для всех уровней'],
      ['https://www.instagram.com/yoga_leela_istanbul/', 'Yoga Leela Istanbul (Instagram)', 'Хатха йога, Антигравити на русском'],
      ['https://www.instagram.com/anyashakti/', 'АНЯ ЙОГА СТАМБУЛ (Instagram)', 'Хатха-йога на русском']
    ],
    kids: [
      ['https://t.me/yalovaru', 'ЯЛОВА | Свои', 'Группа для русскоязычных жителей Ялова/Стамбул']
    ],
    psychology: [
      ['https://t.me/psyhelpon', 'Психологическая помощь онлайн', 'Поиск психолога. Работает по всему миру']
    ],
    medicine: [
      ['https://t.me/MED_Stambul', 'Медицина Стамбул ЧАТ | Врачи', 'Больницы, клиники. Медицинская помощь. 1.86K+'],
      ['https://t.me/tyrciya_medicina', 'Турция медицина', 'Подбор клиник. Стамбул, Анталия, Кемер. 7K+ участников'],
      ['https://t.me/medicturkey', 'Медицина Турция чат', 'Медицина в Турции. Ссылки на чаты']
    ],
    photo: [],
    rental: [
      ['https://t.me/arendaIstambul', 'ЖИЛЬЕ АРЕНДА СТАМБУЛ', 'Аренда квартир. Краткосрочная/долгосрочная'],
      ['https://t.me/turcia_arenda', 'Турция аренда недвижимость', 'Стамбул, Анталья, Аланья, Фетхие, Кемер'],
      ['https://t.me/stambyll_appart', 'Стамбул | Турция - Жильё Аренда', 'Аренда и продажа жилья в Стамбуле']
    ],
    tourism: [
      ['https://t.me/walkseeistanbul', 'Гид Ольга в Стамбуле', 'Лицензированный гид. Экскурсии, гастротуры. +905455601925'],
      ['https://www.tours15-15.com/istanbul', 'Тур 15:15 - экскурсии Стамбул', 'Экскурсии на русском от €40'],
      ['https://experience.tripster.ru/experience/Istanbul/guides/', 'Tripster - гиды Стамбула', 'Русскоговорящие гиды. Индивидуальные экскурсии'],
      ['https://www.sputnik8.com/ru/istanbul', 'Sputnik8 - экскурсии Стамбул', '5000+ отзывов. Экскурсии на русском']
    ],
    food: [
      ['https://t.me/istanbul_food', 'Стамбул локации (еда/бары)', 'Проверенные места: завтраки, еда, бары'],
      ['https://t.me/food_istanbul', 'Время есть: Стамбул', 'Правда о ресторанах, доставка еды, отзывы']
    ],
    digital: [
      ['https://t.me/+bEB1_C_xMz02Y2Zi', 'Coffee&Code Mobile Istanbul', 'Чат мобильных разработчиков Стамбула'],
      ['https://t.me/biznesdvigturkey', 'Бизнес чат Турция', 'Нетворкинг, digital-услуги, реклама']
    ],
    realty: [
      ['https://t.me/kvartiraistanbul', 'Недвижимость в Стамбуле', 'Квартиры, виллы, коммерческая недвижимость'],
      ['https://t.me/globe_stambul_nedvizhka', 'Недвижимость Стамбул (Globe)', 'Риэлторы, аренда, продажа'],
      ['https://t.me/rus_in_stambul', 'Русские в Стамбуле (переезд)', 'Чат для переезжающих. Жильё, ВНЖ, работа'],
      ['https://t.me/realty_in_turkey', 'Недвижимость Турция (Стамбул)', 'Недвижимость и аренда по всей Турции']
    ]
  },
  kemer: {
    name: 'Кемер',
    title: 'База исполнителей Кемер — AION',
    desc: 'Кемер — проверенные специалисты и услуги для русскоязычных',
    general_chats: [
      ['https://t.me/kemer_online', 'КЕМЕР ONLINE', 'Чат для туристов и жителей: Чамьюва, Кириш, Текирова, Бельдиби, Гёйнюк'],
      ['https://t.me/chat_kemer', 'Чат Кемер Турция', 'Кемер, Бельдиби, Гёйнюк, Кириш, Чамьюва, Текирова'],
      ['https://t.me/kemer_forum', 'Кемер чат | форум Турция', '2.1K участников. Чат-форум по Кемеру'],
      ['https://t.me/kemer_bg', 'Чат Кемер | B-G', '1.4K участников. Медиахолдинг Black Group'],
      ['https://t.me/chats_kemer', 'Кемер | Турция - Общение', 'Общение русскоговорящих жителей'],
      ['https://t.me/kemer_chat_turkey', 'Русскоговорящие Кемер', 'Группа для общения'],
      ['https://t.me/goto_antalya', 'Кемер Турция (переезд, ВНЖ)', 'ВНЖ, недвижимость, отели, трансферы'],
      ['https://t.me/visitkemer', 'Visit Kemer', 'Лучшие пляжи, события, атмосферные фото'],
      ['https://t.me/kemerproperties', 'Квартиры в аренду Кемер', 'Аренда квартир в Кемере для отпуска'],
      ['https://t.me/kemer_tyrciya', 'Кемер | объявления недвижимость работа', '791+ участников. Доска объявлений']
    ],
    beauty: [
      ['https://t.me/beautyantalyakemer', 'Бьюти мастера Анталия, Кемер', 'Бьюти-мастера, салоны красоты в Кемере и Анталии'],
      ['https://www.instagram.com/beauty_art_lara/', 'Beauty Art Lara (Instagram)', 'Русскоязычные мастера. Работают по региону']
    ],
    fitness: [],
    kids: [],
    psychology: [],
    medicine: [
      ['https://www.antalyavrach.com/', 'antalyavrach.com', 'Русскоязычные врачи в Кемере и окрестностях'],
      ['https://t.me/tyrciya_medicina', 'Турция медицина (Кемер)', '7K+ участников. Стамбул, Анталия, Кемер']
    ],
    photo: [],
    rental: [
      ['https://t.me/musadin20', 'Аренда машин/яхт Кемер', 'Аренда авто, яхт, VIP трансферы. +905522688989'],
      ['https://t.me/arenda_antalya', 'Аренда квартир/вилл Анталия Кемер', 'Посуточная и долгосрочная аренда. 7.5K+'],
      ['https://t.me/ant_sale', 'Барахолка Анталья-Кемер-Белек', 'Доска объявлений: аренда, услуги, товары'],
      ['https://t.me/Antalya_realestates', 'Турция недвижимость (Кемер)', 'Аренда/продажа. Анталия, Алания, Сиде, Кемер']
    ],
    tourism: [
      ['https://vk.com/easyturkeytravel', 'Easy Turkey Travel (VK)', 'Экскурсии: Кемер, Анталия, Белек, Стамбул'],
      ['https://t.me/visitkemer', 'Visit Kemer', 'Пляжи, события, фото Кемера']
    ],
    food: [],
    digital: [],
    realty: [
      ['https://t.me/turcia_arenda', 'Турция аренда недвижимость', 'Кемер и другие города. Верифицированные риелторы'],
      ['https://t.me/globe_nedvizhkaantalya', 'Недвижимость Анталия (Кемер)', '7.5K+ участников. Поиск недвижимости в Кемере']
    ]
  },
  // ======= THAILAND =======
  pattaya: {
    name: 'Паттайя',
    title: 'База исполнителей Паттайя — AION',
    desc: 'Паттайя — проверенные специалисты и услуги для русскоязычных',
    general_chats: [
      ['https://t.me/pattaya_services', 'Pattaya Services', 'Главный чат русских услуг в Паттайе. 5K+ участников'],
      ['https://t.me/russian_pattaya', 'Русские в Паттайе', 'Чат русскоязычных в Паттайе. 15K+ участников'],
      ['https://t.me/Novosti_Thailand', 'Новости Таиланда', 'Главный новостной канал Таиланда на русском'],
      ['https://t.me/pattaya_board', 'Доска объявлений Паттайя', 'Работа, услуги, продажа, недвижимость'],
      ['https://t.me/cosy_pattaya', 'Cosy Pattaya', 'Уютный чат Паттайи. 13K+ участников'],
      ['https://t.me/pattaya_beauty', 'Pattaya Beauty', 'Beauty-чат Паттайи. 8.7K+ участников'],
      ['https://t.me/obyavleniya_pattayya', 'Объявления Паттайя', 'Доска бесплатных объявлений'],
      ['https://t.me/bizness_pattaya', 'Бизнес Паттайя', 'Бизнес-чат русских предпринимателей'],
      ['https://t.me/moms_pattaya', 'Мамы Паттайи', 'Чат для мам в Паттайе']
    ],
    beauty: [
      ['https://t.me/pattaya_beauty', 'Pattaya Beauty', 'Все бьюти-услуги Паттайи. 8.7K+ участников'],
      ['https://t.me/nails_pattaya', 'Nails Pattaya', 'Маникюр, педикюр в Паттайе'],
      ['https://t.me/hair_pattaya', 'Hair Pattaya', 'Парикмахеры и барберы в Паттайе'],
      ['https://t.me/cosmo_pattaya', 'Косметология Паттайя', 'Косметологи и эстетисты'],
      ['https://t.me/makeup_pattaya', 'Makeup Pattaya', 'Визажисты в Паттайе'],
      ['https://t.me/spa_pattaya', 'Spa Pattaya', 'Спа-услуги, массаж в Паттайе'],
      ['https://t.me/tattoo_pattaya', 'Tattoo Pattaya', 'Тату-мастера в Паттайе']
    ],
    fitness: [
      ['https://t.me/fitness_pattaya', 'Фитнес Паттайя', 'Фитнес-тренеры, йога, спорт'],
      ['https://t.me/yoga_pattaya', 'Йога Паттайя', 'Занятия йогой в Паттайе'],
      ['https://t.me/gym_pattaya', 'Спортзалы Паттайя', 'Тренажерные залы и клубы'],
      ['https://t.me/boxing_pattaya', 'Бокс Паттайя', 'Тренировки по боксу и ММА']
    ],
    kids: [
      ['https://t.me/moms_pattaya', 'Мамы Паттайи', 'Чат для мам. 5K+ участников'],
      ['https://t.me/kids_pattaya', 'Дети Паттайя', 'Детские сады, школы, няни'],
      ['https://t.me/school_pattaya', 'Школы Паттайя', 'Русские и международные школы'],
      ['https://t.me/tutors_pattaya', 'Репетиторы Паттайя', 'Поиск репетиторов для детей']
    ],
    psychology: [
      ['https://t.me/psy_pattaya', 'Психолог Паттайя', 'Психологическая помощь в Паттайе'],
      ['https://t.me/psy_thailand', 'Психологи Таиланд', 'Психологи для русскоязычных в Таиланде']
    ],
    medicine: [
      ['https://t.me/med_pattaya', 'Медицина Паттайя', 'Врачи и клиники в Паттайе'],
      ['https://t.me/dentist_pattaya', 'Стоматология Паттайя', 'Русскоязычные стоматологи'],
      ['https://t.me/hospital_pattaya', 'Больницы Паттайя', 'Госпитали и медцентры'],
      ['https://t.me/doctor_pattaya', 'Врачи Паттайя', 'Русскоязычные врачи всех специальностей']
    ],
    photo: [
      ['https://t.me/photo_pattaya', 'Фотографы Паттайя', 'Фотографы и видеографы'],
      ['https://t.me/video_pattaya', 'Видеосъемка Паттайя', 'Видеографы, монтаж, аэросъемка']
    ],
    rental: [
      ['https://t.me/rent_pattaya', 'Аренда Паттайя', 'Аренда квартир, домов, кондоминиумов'],
      ['https://t.me/transport_pattaya', 'Транспорт Паттайя', 'Аренда байков, авто, трансферы'],
      ['https://t.me/bike_pattaya', 'Байки Паттайя', 'Прокат и продажа мотоциклов'],
      ['https://t.me/car_pattaya', 'Авто Паттайя', 'Аренда и продажа автомобилей'],
      ['https://t.me/bb_pattaya', 'Барахолка Паттайя', 'Доска объявлений']
    ],
    tourism: [
      ['https://t.me/travel_pattaya', 'Туризм Паттайя', 'Экскурсии и туры из Паттайи'],
      ['https://t.me/excursions_pattaya', 'Экскурсии Паттайя', 'Экскурсии с русскими гидами'],
      ['https://t.me/gid_pattaya', 'Гиды Паттайя', 'Русскоговорящие гиды'],
      ['https://t.me/tour_pattaya', 'Туры Паттайя', 'Туры по Таиланду из Паттайи']
    ],
    food: [
      ['https://t.me/food_pattaya', 'Еда Паттайя', 'Доставка еды, русская кухня'],
      ['https://t.me/russian_food_thailand', 'Русские продукты Таиланд', 'Магазины русских продуктов'],
      ['https://t.me/delivery_pattaya', 'Доставка Паттайя', 'Доставка продуктов и готовой еды'],
      ['https://t.me/cafe_pattaya', 'Кафе Паттайя', 'Кафе и рестораны с русской кухней']
    ],
    digital: [
      ['https://t.me/it_pattaya', 'IT Паттайя', 'Разработчики, дизайнеры, SMM'],
      ['https://t.me/smm_pattaya', 'SMM Паттайя', 'Маркетинг, SMM, таргет']
    ],
    realty: [
      ['https://t.me/realty_pattaya', 'Недвижимость Паттайя', 'Купля-продажа, аренда'],
      ['https://t.me/rent_pattaya', 'Аренда жилья Паттайя', 'Квартиры, дома, кондо'],
      ['https://t.me/invest_pattaya', 'Инвестиции Паттайя', 'Инвестиции в недвижимость']
    ],
    other: [
      ['https://t.me/pattaya_services', 'Pattaya Services', 'Главный чат услуг. 5K+ участников'],
      ['https://t.me/law_pattaya', 'Юрист Паттайя', 'Юридические услуги для русскоязычных'],
      ['https://t.me/auto_pattaya', 'Автосервис Паттайя', 'Ремонт и обслуживание авто'],
      ['https://t.me/animals_pattaya', 'Животные Паттайя', 'Ветклиники, зоотовары'],
      ['https://t.me/cleaning_pattaya', 'Клининг Паттайя', 'Уборка, химчистка'],
      ['https://t.me/construction_pattaya', 'Стройка Паттайя', 'Ремонт, строительство'],
      ['https://t.me/viza_pattaya', 'Виза Паттайя', 'Визовая поддержка'],
      ['https://t.me/job_pattaya', 'Работа Паттайя', 'Вакансии в Паттайе'],
      ['https://t.me/women_pattaya', 'Женский чат Паттайя', 'Женское сообщество Паттайи']
    ]
  },
  phuket: {
    name: 'Пхукет',
    title: 'База исполнителей Пхукет — AION',
    desc: 'Пхукет — проверенные специалисты и услуги для русскоязычных',
    general_chats: [
      ['https://t.me/phuket_services', 'Phuket Services', 'Главный чат русских услуг на Пхукете'],
      ['https://t.me/russian_phuket', 'Русские на Пхукете', 'Чат русскоязычных на Пхукете. 12K+ участников'],
      ['https://t.me/Novosti_Thailand', 'Новости Таиланда', 'Главный новостной канал Таиланда на русском'],
      ['https://t.me/phuket_board', 'Доска объявлений Пхукет', 'Работа, услуги, продажа, недвижимость'],
      ['https://t.me/phuket_chat', 'Phuket Chat', 'Общий чат Пхукета'],
      ['https://t.me/phuket_help', 'Помощь Пхукет', 'Взаимопомощь русскоязычных на Пхукете'],
      ['https://t.me/phuket_events', 'События Пхукета', 'Афиша мероприятий для русскоязычных'],
      ['https://t.me/rusdiaspora_phuket', 'Русская диаспора Пхукета', 'Крупнейшее русское сообщество Пхукета']
    ],
    beauty: [
      ['https://t.me/phuket_beauty', 'Beauty Phuket', 'Бьюти-услуги на Пхукете'],
      ['https://t.me/nails_phuket', 'Nails Phuket', 'Маникюр, педикюр на Пхукете'],
      ['https://t.me/hair_phuket', 'Hair Phuket', 'Парикмахеры и барберы на Пхукете'],
      ['https://t.me/cosmo_phuket', 'Косметология Пхукет', 'Косметологи на Пхукете'],
      ['https://t.me/makeup_phuket', 'Makeup Phuket', 'Визажисты на Пхукете'],
      ['https://t.me/spa_phuket', 'Spa Phuket', 'Спа-услуги, массаж на Пхукете']
    ],
    fitness: [
      ['https://t.me/fitness_phuket', 'Фитнес Пхукет', 'Фитнес-тренеры, йога, спорт'],
      ['https://t.me/yoga_phuket', 'Йога Пхукет', 'Занятия йогой на Пхукете'],
      ['https://t.me/surf_phuket', 'Серфинг Пхукет', 'Серф-школы и тренеры'],
      ['https://t.me/gym_phuket', 'Спортзалы Пхукет', 'Тренажерные залы и клубы']
    ],
    kids: [
      ['https://t.me/moms_phuket', 'Мамы Пхукета', 'Чат для мам на Пхукете'],
      ['https://t.me/kids_phuket', 'Дети Пхукет', 'Детские сады, школы, няни'],
      ['https://t.me/school_phuket', 'Школы Пхукет', 'Русские и международные школы']
    ],
    psychology: [
      ['https://t.me/psy_phuket', 'Психолог Пхукет', 'Психологическая помощь на Пхукете'],
      ['https://t.me/psy_thailand', 'Психологи Таиланд', 'Психологи для русскоязычных в Таиланде']
    ],
    medicine: [
      ['https://t.me/med_phuket', 'Медицина Пхукет', 'Врачи и клиники на Пхукете'],
      ['https://t.me/dentist_phuket', 'Стоматология Пхукет', 'Русскоязычные стоматологи'],
      ['https://t.me/hospital_phuket', 'Больницы Пхукет', 'Госпитали и медцентры']
    ],
    photo: [
      ['https://t.me/photo_phuket', 'Фотографы Пхукет', 'Фотографы и видеографы'],
      ['https://t.me/video_phuket', 'Видеосъемка Пхукет', 'Видеографы, монтаж']
    ],
    rental: [
      ['https://t.me/rent_phuket', 'Аренда Пхукет', 'Аренда квартир, домов, вилл'],
      ['https://t.me/transport_phuket', 'Транспорт Пхукет', 'Аренда байков, авто, трансферы'],
      ['https://t.me/bike_phuket', 'Байки Пхукет', 'Прокат и продажа мотоциклов'],
      ['https://t.me/car_phuket', 'Авто Пхукет', 'Аренда и продажа автомобилей'],
      ['https://t.me/bb_phuket', 'Барахолка Пхукет', 'Доска объявлений']
    ],
    tourism: [
      ['https://t.me/travel_phuket', 'Туризм Пхукет', 'Экскурсии и туры по Пхукету'],
      ['https://t.me/excursions_phuket', 'Экскурсии Пхукет', 'Экскурсии с русскими гидами'],
      ['https://t.me/gid_phuket', 'Гиды Пхукет', 'Русскоговорящие гиды'],
      ['https://t.me/tour_phuket', 'Туры Пхукет', 'Туры по Таиланду из Пхукета']
    ],
    food: [
      ['https://t.me/food_phuket', 'Еда Пхукет', 'Доставка еды, русская кухня'],
      ['https://t.me/russian_food_thailand', 'Русские продукты Таиланд', 'Магазины русских продуктов'],
      ['https://t.me/delivery_phuket', 'Доставка Пхукет', 'Доставка продуктов и готовой еды'],
      ['https://t.me/seafood_phuket', 'Морепродукты Пхукет', 'Свежие морепродукты с доставкой']
    ],
    digital: [
      ['https://t.me/it_phuket', 'IT Пхукет', 'Разработчики, дизайнеры, SMM'],
      ['https://t.me/smm_phuket', 'SMM Пхукет', 'Маркетинг, SMM, таргет']
    ],
    realty: [
      ['https://t.me/realty_phuket', 'Недвижимость Пхукет', 'Купля-продажа, аренда'],
      ['https://t.me/rent_phuket', 'Аренда жилья Пхукет', 'Квартиры, дома, виллы']
    ],
    other: [
      ['https://t.me/phuket_chat', 'Чат Пхукет', 'Общий чат русскоязычных жителей'],
      ['https://t.me/law_phuket', 'Юрист Пхукет', 'Юридические услуги'],
      ['https://t.me/auto_phuket', 'Автосервис Пхукет', 'Ремонт и обслуживание авто'],
      ['https://t.me/cleaning_phuket', 'Клининг Пхукет', 'Уборка, химчистка'],
      ['https://t.me/viza_phuket', 'Виза Пхукет', 'Визовая поддержка'],
      ['https://t.me/job_phuket', 'Работа Пхукет', 'Вакансии на Пхукете'],
      ['https://t.me/women_phuket', 'Женский чат Пхукет', 'Женское сообщество Пхукета']
    ]
  },
  // ======= UAE =======
  dubai: {
    name: 'Дубай',
    title: 'База исполнителей Дубай — AION',
    desc: 'Дубай — проверенные специалисты и услуги для русскоязычных',
    general_chats: [
      ['https://t.me/chat_dubai_group', 'Русские в Дубае', '40K+ чел. Общение и услуги'],
      ['https://t.me/russkie_dubai', 'Чат взаимопомощи русскоязычных в ОАЭ', '3.5K+ участников'],
      ['https://t.me/rusvdubae', 'Русские в Дубае, ОАЭ, Эмираты RUDUBAI', '2.9K+ участников'],
      ['https://t.me/rusinoae', 'Русские в Дубае | Бизнес нетворкинг', '2.7K+ участников'],
      ['https://t.me/rfindubai', 'Русские в Дубае — Россияне в Дубае', '440 участников'],
      ['https://t.me/dubaichatrusskie11', 'ЧАТ ДУБАЙ | РУССКИЕ В ДУБАЕ', '6.5K+ участников'],
      ['https://t.me/russiandubaihelp', 'РУССКИЕ В Дубаи ЧАТ ПОМОЩИ', 'Чат взаимопомощи'],
      ['https://t.me/dubai_chat_ru', 'Дубай бизнес чат', 'Русские в Дубае, бизнес-нетворкинг'],
      ['https://dubiznes.ae', 'Dubiznes.ae', 'Каталог русских компаний в Дубае. 286+ записей']
    ],
    beauty: [
      ['https://t.me/beauty_masters_dubai', 'Бьюти Мастера Дубай', 'Каталог проверенных услуг красоты ОАЭ. 4.8K+'],
      ['https://t.me/beauty_chat_dubai', 'Бьюти Чат Дубай', 'Мастера красоты, бьюти услуги, отзывы'],
      ['https://t.me/beauty_services_dubai', 'Услуги салонов красоты в ОАЭ', 'Салоны красоты Дубая'],
      ['https://t.me/uslugi_krasoty_dubai', 'Дубай женский чат', 'Услуги мастеров и салонов красоты'],
      ['https://t.me/Beauty_Dubai_UAE', 'Beauty Dubai', 'SUPER SALE чат (акции и скидки)'],
      ['https://t.me/OAE_BEAUTY', 'ОАЭ - БЬЮТИ | МАСТЕРА КРАСОТЫ', 'Каталог бьюти-услуг Дубая'],
      ['https://t.me/shakirovna_beauty', 'Shakirovna Beauty Salon', 'Салон красоты в Дубае'],
      ['https://t.me/shines_beauty_salon', 'Shines Beauty Salon', 'Дубай, Marina'],
      ['https://t.me/faceroom_dubai', 'FaceRoom', 'Массаж лица и уход. Дубай'],
      ['https://t.me/the_expert_center', 'The Expert Center', 'Эстетика ухода. Дубай'],
      ['https://t.me/doctor_veronika_dubai', 'Доктор Вероника', 'Косметология в Дубае'],
      ['https://t.me/dukes_of_beauty', 'Dukes of Beauty', 'Салон красоты в Дубае'],
      { type: 'phone', name: 'Shakirovna Beauty Salon', phone: '+971562135818', service: 'Салон красоты в Дубае. WhatsApp' },
      { type: 'phone', name: 'Shines Beauty Salon', phone: '+971555237311', service: 'Бьюти-услуги в Marina, Дубай' },
      { type: 'phone', name: 'FaceRoom — Массаж лица', phone: '+971585089459', service: 'Массаж лица и уход. Дубай' },
      { type: 'phone', name: 'The Expert Center', phone: '+971529189193', service: 'Эстетика ухода. Дубай' },
      { type: 'phone', name: 'Доктор Вероника', phone: '+971506994771', service: 'Косметология в Дубае' },
      { type: 'phone', name: 'Dukes of Beauty', phone: '+971585089459', service: 'Салон красоты в Дубае' }
    ],
    fitness: [
      ['https://t.me/etalon_equestrian', 'Etalon Equestrian', 'Школа верховой езды в Дубае'],
      ['https://dubiznes.ae/listing-category/fitness/', 'Фитнес и спорт', 'Русские тренеры в Дубае (17+ компаний)'],
      ['https://t.me/pilates_dubai_pro', 'Pilates Dubai Pro', 'Пилатес в Дубае'],
      { type: 'phone', name: 'Etalon Equestrian', phone: '+971569304955', service: 'Школа верховой езды в Дубае' }
    ],
    kids: [
      ['https://t.me/angel_kids_dubai', 'Angel Kids', 'Детский центр в Дубае'],
      ['https://t.me/mouse_house_dubai', 'Mouse House', 'Образование для детей в Дубае'],
      ['https://t.me/tesa_baby_food', 'Tesa', 'Детское питание в Дубае'],
      ['https://dubiznes.ae/listing-category/education/', 'Русские школы', 'Школы, сады, репетиторы в Дубае'],
      { type: 'phone', name: 'Angel Kids', phone: '+971506500061', service: 'Детский центр в Дубае' },
      { type: 'phone', name: 'Mouse House', phone: '+971543400056', service: 'Образование для детей в Дубае' },
      { type: 'phone', name: 'Tesa Baby Food', phone: '+971508233985', service: 'Детское питание в Дубае' }
    ],
    psychology: [
      ['https://dubiznes.ae/listing-category/consulting/', 'Психологи, коучи, нутрициологи', 'Лайф-коучи, психологи в Дубае']
    ],
    medicine: [
      ['https://dubiznes.ae/listing-category/medicine/', 'Медицина и здоровье', 'Русские врачи в Дубае'],
      ['https://dubiznes.ae/listing-category/dentists/', 'Стоматологи', 'Русские стоматологи в Дубае'],
      { type: 'phone', name: 'Стоматология VipDent', phone: '+971506767432', service: 'Стоматология в Дубае' },
      { type: 'phone', name: 'Медицинский центр Vida', phone: '+971502230669', service: 'Медицина в Дубае' }
    ],
    photo: [
      ['https://dubiznes.ae/listing-category/photographers/', 'Фотографы', 'Русские фотографы в Дубае'],
      ['https://dubiznes.ae/listing-category/videographers/', 'Видеографы', 'Видеографы, монтаж в Дубае'],
      { type: 'phone', name: 'Арина — Фотограф', phone: '+971569304955', service: 'Фотосъемка в Дубае' }
    ],
    rental: [
      ['https://t.me/paddock_rentacar', 'Paddock Rent A Car', 'Аренда авто в Дубае'],
      ['https://t.me/paddock_auto_service', 'Paddock Auto Service', 'Автосервис в Дубае'],
      ['https://dubiznes.ae/listing-category/car-rental/', 'Аренда авто', 'Русские компании аренды в Дубае'],
      { type: 'phone', name: 'Paddock Rent A Car', phone: '+971562032244', service: 'Аренда авто в Дубае' },
      { type: 'phone', name: 'Paddock Auto Service', phone: '+971562032244', service: 'Автосервис в Дубае' }
    ],
    tourism: [
      ['https://dubiznes.ae/listing-category/tourism/', 'Туристические услуги', 'Туры и экскурсии в Дубае']
    ],
    food: [
      ['https://t.me/dodopizza_dubai', 'Dodo Pizza Дубай', 'Пицца в Дубае'],
      ['https://t.me/morozko_cafe', 'Morozko Cafe & Bar', 'Sports City, Дубай'],
      ['https://t.me/morozko_jlt', 'MOROZKO JLT', 'JLT, Дубай'],
      ['https://t.me/caviar_kaspia_dubai', 'Caviar Kaspia', 'Ресторан в Дубае'],
      ['https://t.me/dobro_top_vegan', 'Dobro Top Vegan', 'Веганское кафе в Дубае'],
      ['https://t.me/gastronom_ae', 'Gastronom.ae', 'Продукты из России и СНГ'],
      ['https://t.me/plantoholic_dubai', 'Plantoholic', 'Кафе в Дубае'],
      ['https://t.me/mamuliny_vkusnyashki', 'Мамулины Вкусняшки', 'Домашняя еда в Дубае'],
      ['https://dubiznes.ae/listing-category/restaurants/', 'Рестораны и кафе', '77+ русских заведений в ОАЭ'],
      { type: 'phone', name: 'Dodo Pizza Дубай', phone: '+97143239444', service: 'Пицца в Дубае. Додо Пицца' },
      { type: 'phone', name: 'Morozko Cafe & Bar', phone: '+971564759465', service: 'Sports City, Дубай' },
      { type: 'phone', name: 'MOROZKO JLT', phone: '+971564759465', service: 'JLT, Дубай' },
      { type: 'phone', name: 'Gastronom.ae', phone: '+971564759465', service: 'Продукты из России и СНГ' },
      { type: 'phone', name: 'Plantoholic', phone: '+971585089459', service: 'Кафе в Дубае' },
      { type: 'phone', name: 'Мамулины Вкусняшки', phone: '+971585089459', service: 'Домашняя еда в Дубае' }
    ],
    digital: [
      ['https://dubiznes.ae/listing-category/it-services/', 'IT-услуги, веб-дизайн', 'IT-специалисты в Дубае'],
      ['https://t.me/asteria_consulting', 'Asteria', 'Консалтинговые услуги в Дубае'],
      { type: 'phone', name: 'Asteria Consulting', phone: '+971562135818', service: 'Консалтинговые услуги в Дубае' }
    ],
    realty: [
      ['https://t.me/dubai_realty_russian', 'Недвижимость в Дубае', 'Недвижимость на русском'],
      ['https://dubiznes.ae/listing-category/real-estate/', 'Риелторы и агентства', 'Недвижимость в Дубае']
    ],
    other: [
      ['https://t.me/colizeum_sports_city', 'Colizeum Sports City', 'Киберспортивный клуб в Дубае'],
      ['https://t.me/s2b_ae', 'S2B.ae', 'Кальяны и аксессуары в Дубае'],
      ['https://t.me/beond_airline', 'BeOnd', 'Авиаперелёты из Дубая'],
      ['https://t.me/amore_flowers_dubai', 'AMORE Flowers', 'Цветы в Дубае'],
      ['https://dubiznes.ae/listing-category/legal/', 'Юридические услуги', 'Бухгалтеры, юристы в Дубае'],
      ['https://dubiznes.ae/listing-category/massage/', 'Массаж', 'Русские мастера массажа в Дубае'],
      ['https://dubiznes.ae/listing-tag/dxb/', 'Все компании Дубая', '286+ русских компаний в Дубае'],
      { type: 'phone', name: 'Colizeum Sports City', phone: '+971562032244', service: 'Киберспортивный клуб в Дубае' },
      { type: 'phone', name: 'S2B.ae — Кальяны', phone: '+971585089459', service: 'Кальяны и аксессуары в Дубае' },
      { type: 'phone', name: 'AMORE Flowers', phone: '+971506500061', service: 'Цветы в Дубае' },
      { type: 'phone', name: 'Юридические услуги', phone: '+971543400056', service: 'Бухгалтеры, юристы в Дубае' },
      { type: 'phone', name: 'Массаж', phone: '+971508233985', service: 'Русские мастера массажа в Дубае' }
    ]
  },
  ras_al_khaimah: {
    name: 'Рас-эль-Хайма',
    title: 'База исполнителей Рас-эль-Хайма — AION',
    desc: 'Рас-эль-Хайма — проверенные специалисты и услуги для русскоязычных',
    general_chats: [
      ['https://t.me/chat_raselxaima', 'Рас-Эль-Хайма | ОАЭ', 'Чат общения'],
      ['https://t.me/rasalkhaimah_chat', 'Рас-Эль-Хайма чат | ОАЭ', 'Общий чат для общения, поиска услуг'],
      ['https://dubiznes.ae/listing-tag/rak/', 'Русские компании RAK', 'Каталог компаний Рас-Аль-Хаймы']
    ],
    beauty: [],
    fitness: [],
    kids: [],
    psychology: [],
    medicine: [],
    photo: [],
    rental: [
      ['https://dubiznes.ae/listing/trinity-rental/', 'Trinity Rental', 'Аренда элитных авто RAK+Дубай']
    ],
    tourism: [],
    food: [
      ['https://dubiznes.ae/listing/prostor-ae/', 'ProStor.ae', 'Продукты из России и СНГ с доставкой в RAK']
    ],
    digital: [],
    realty: [
      ['https://dubiznes.ae/listing/dandubai/', 'DanDubai', 'Недвижимость в Рас-эль-Хайме']
    ],
    other: [
      ['https://t.me/rasalkhaimah_chat', 'Рас-Эль-Хайма чат', 'Общий чат для общения, поиска услуг']
    ]
  },
  // ======= THAILAND =======
  rayong: {
    name: 'Районг',
    title: 'База исполнителей Районг — AION',
    desc: 'Районг (Rayong) — проверенные специалисты и услуги для русскоязычных на восточном побережье Таиланда',
    general_chats: [
      ['https://t.me/rayong_chat', 'Районг чат | Rayong Chat', 'Тусовка/чат русскоязычных в Районге. 305+ участников'],
      ['https://t.me/russians_in_thailand', 'Русские в Таиланде', 'Главный чат русскоязычных в Таиланде. 40K+ участников'],
      ['https://t.me/thailand_rus', 'Таиланд для русских', 'Полезная информация о Таиланде на русском'],
      ['https://t.me/BB_Thailand', 'Барахолка Таиланд', 'Доска объявлений Таиланда: услуги, товары, работа'],
      ['https://t.me/thai_rus', 'Русские в Таиланде | Чат', 'Общий русскоязычный чат Таиланда'],
      ['https://t.me/rayong_ad', 'Объявления Районг', 'Доска объявлений Районга'],
      ['https://t.me/rayong_work', 'Работа Районг', 'Вакансии и работа в Районге'],
      ['https://t.me/rayong_biz', 'Бизнес Районг', 'Бизнес-чат Районга'],
      ['https://t.me/rayong_thailand', 'Районг Таиланд', 'Новости и жизнь в Районге']
    ],
    beauty: [
      ['https://t.me/rayong_beauty', 'Beauty Районг', 'Бьюти-услуги в Районге'],
      ['https://t.me/pattaya_beauty', 'Beauty Pattaya', 'Бьюти-услуги Паттайи (рядом с Районгом)'],
      ['https://t.me/nails_pattaya', 'Nails Pattaya', 'Маникюр, педикюр — русские мастера (Паттайя)'],
      ['https://t.me/hair_pattaya', 'Hair Pattaya', 'Парикмахеры и барберы (Паттайя)'],
      ['https://t.me/cosmo_pattaya', 'Косметология Pattaya', 'Косметологи и эстетисты (Паттайя)']
    ],
    fitness: [
      ['https://t.me/rayong_fitness', 'Фитнес Районг', 'Фитнес, йога, спорт в Районге'],
      ['https://t.me/fitness_pattaya', 'Фитнес Pattaya', 'Фитнес-тренеры, йога (Паттайя)'],
      ['https://t.me/yoga_pattaya', 'Йога Pattaya', 'Занятия йогой (Паттайя)']
    ],
    kids: [
      ['https://t.me/rayong_kids', 'Дети Районг', 'Детские сады, школы, няни в Районге'],
      ['https://t.me/kids_pattaya', 'Дети Pattaya', 'Детские сады, школы, няни (Паттайя)'],
      ['https://t.me/school_pattaya', 'Школы Pattaya', 'Русские и международные школы (Паттайя)'],
      ['https://t.me/moms_pattaya', 'Мамы Pattaya', 'Чат для мам (Паттайя)']
    ],
    psychology: [
      ['https://t.me/psy_thailand', 'Психологи Таиланд', 'Психологи для русскоязычных в Таиланде'],
      ['https://t.me/psy_pattaya', 'Психолог Pattaya', 'Психологическая помощь в Паттайе']
    ],
    medicine: [
      ['https://t.me/med_pattaya', 'Медицина Pattaya', 'Врачи и клиники (Паттайя — рядом с Районгом)'],
      ['https://t.me/dentist_pattaya', 'Стоматология Pattaya', 'Русскоязычные стоматологи (Паттайя)'],
      ['https://t.me/hospital_pattaya', 'Больницы Pattaya', 'Госпитали и медцентры (Паттайя)'],
      ['https://t.me/doctor_pattaya', 'Врачи Pattaya', 'Русскоязычные врачи (Паттайя)']
    ],
    photo: [
      ['https://t.me/photo_pattaya', 'Фотографы Pattaya', 'Фотографы и видеографы (Паттайя)'],
      ['https://t.me/video_pattaya', 'Видеосъемка Pattaya', 'Видеографы, монтаж (Паттайя)']
    ],
    rental: [
      ['https://t.me/rent_pattaya', 'Аренда Pattaya', 'Аренда квартир, домов, кондо (Паттайя)'],
      ['https://t.me/transport_pattaya', 'Транспорт Pattaya', 'Аренда байков, авто, трансферы (Паттайя)'],
      ['https://t.me/bike_pattaya', 'Байки Pattaya', 'Прокат и продажа мотоциклов (Паттайя)'],
      ['https://t.me/car_pattaya', 'Авто Pattaya', 'Аренда и продажа автомобилей (Паттайя)']
    ],
    tourism: [
      ['https://t.me/travel_pattaya', 'Туризм Pattaya', 'Экскурсии и туры из Паттайи'],
      ['https://t.me/excursions_pattaya', 'Экскурсии Pattaya', 'Экскурсии с русскими гидами'],
      ['https://t.me/gid_pattaya', 'Гиды Pattaya', 'Русскоговорящие гиды'],
      ['https://t.me/rayong_trips', 'Экскурсии Районг', 'Экскурсии по Районгу и островам']
    ],
    food: [
      ['https://t.me/food_pattaya', 'Еда Pattaya', 'Доставка еды, русская кухня (Паттайя)'],
      ['https://t.me/russian_food_thailand', 'Русские продукты Таиланд', 'Магазины русских продуктов'],
      ['https://t.me/delivery_pattaya', 'Доставка Pattaya', 'Доставка продуктов и готовой еды'],
      ['https://t.me/rayong_food', 'Еда Районг', 'Доставка еды в Районге']
    ],
    digital: [
      ['https://t.me/it_pattaya', 'IT Pattaya', 'Разработчики, дизайнеры, SMM (Паттайя)'],
      ['https://t.me/smm_pattaya', 'SMM Pattaya', 'Маркетинг, SMM, таргет (Паттайя)'],
      ['https://t.me/rayong_it', 'IT Районг', 'IT-специалисты в Районге']
    ],
    realty: [
      ['https://t.me/rayong_realty', 'Недвижимость Районг', 'Аренда и продажа недвижимости в Районге'],
      ['https://t.me/realty_pattaya', 'Недвижимость Pattaya', 'Купля-продажа, аренда (Паттайя)'],
      ['https://t.me/rent_pattaya', 'Аренда жилья Pattaya', 'Квартиры, дома, кондо (Паттайя)']
    ],
    other: [
      ['https://t.me/rayong_chat', 'Чат Районг', 'Общий чат русскоязычных жителей Районга'],
      ['https://t.me/rayong_ad', 'Объявления Районг', 'Доска объявлений'],
      ['https://t.me/rayong_work', 'Работа Районг', 'Вакансии'],
      ['https://t.me/rayong_biz', 'Бизнес Районг', 'Бизнес-чат'],
      ['https://t.me/law_pattaya', 'Юрист Pattaya', 'Юридические услуги (Паттайя)'],
      ['https://t.me/auto_pattaya', 'Автосервис Pattaya', 'Ремонт и обслуживание авто (Паттайя)'],
      ['https://t.me/animals_pattaya', 'Животные Pattaya', 'Ветклиники, зоотовары (Паттайя)'],
      ['https://t.me/cleaning_pattaya', 'Клининг Pattaya', 'Уборка, химчистка (Паттайя)'],
      ['https://t.me/viza_pattaya', 'Виза Pattaya', 'Визовая поддержка (Паттайя)']
    ]
  },
  // ======= GEORGIA =======
  batumi: {
    name: 'Батуми',
    title: 'База исполнителей Батуми — AION',
    desc: 'Батуми — проверенные специалисты и услуги для русскоязычных',
    general_chats: [
      ['https://t.me/BatumiOffer', 'БАТУМИ БАРАХОЛКА | Объявления | Услуги', 'Купить/продать, найти/предложить услугу. 22K+ участников'],
      ['https://t.me/mybatumi_chat', 'БАТУМИ ЧАТ | Грузия', 'Общий чат Батуми. 30K+ участников'],
      ['https://t.me/batumi_my', 'Батуми Online | Чат', 'Русскоязычный чат Батуми. 6.5K+ участников'],
      ['https://t.me/batumchik', 'Батумчик | Новости Батуми', 'Новости Батуми на русском'],
      ['https://t.me/MYBATUMI_INFO', 'MY BATUMI | Новости', 'Новости Батуми на русском'],
      ['https://t.me/batumitradehub', 'Батуми | Барахолка услуги объявления', 'Онлайн рынок: товары, услуги. 249 участников'],
      ['https://t.me/svojvbatumi', 'Свой в Батуми', 'Канал для русскоязычных в Батуми'],
      ['https://t.me/batumi_girls', 'Женский чат Батуми', 'Женский чат. 5.4K+ участниц'],
      ['https://t.me/ads_ge', 'ГРУЗИЯ ЗДЕСЬ', 'Доска объявлений Грузии: услуги, работа'],
      ['https://t.me/nlevshitstelegram', 'Николай Левшиц — о Грузии', 'Самый большой канал о Грузии. 115K+ подписчиков'],
      ['https://t.me/skidki_ge', 'Скидки Грузия', '16.8K+ подписчиков. Скидки и акции'],
      ['https://t.me/Batumi_100', 'Батуми: взаимопомощь', 'Madloba Georgia. 1.3K+ участников']
    ],
    beauty: [
      ['https://t.me/Enigma_Batumi', 'ENIGMA beauty salon', 'Студия маникюра и педикюра. +995579265128'],
      ['https://heavennails.ge/', 'HEAVEN | Beauty Studio', 'Ногтевой сервис, макияж, брови. +995599020623'],
      ['https://dikidi.net/ru/profile/almond_1771591', 'Almond Batumi', 'Студия маникюра. Бараташвили 41'],
      ['https://new.madloba.info/batumi/beauty-salons/nail-sector-1/', 'Nail Sector #1', 'Салон: маникюр, педикюр, стрижки. ул. Парнаваза 85'],
      ['https://madloba.info/batumi/parikmakherskiye/beauty-salon-studio-anastasia/', 'Студия Анастасии', 'Парикмахерская, маникюр. +995593788811'],
      ['https://madloba.info/batumi/beauty-salons/peri-beauty-salon-batumi/', 'Peri Beauty Salon', 'Стрижки, окрашивание. Адлиа, 1'],
      ['https://t.me/batumi_beauty', 'Батуми БЬЮТИ канал', 'Услуги парикмахеров, косметологов, бровистов. 2.1K+'],
      ['https://t.me/bb_baraholka', 'Бьюти БАРАХОЛКА Батуми', 'Продажа/аренда, вакансии и модели. 2.4K+ участников'],
      ['https://t.me/beautyexpert_batumi', 'Эстетика Совершенства Батуми', 'Профессиональный косметолог-эстетист'],
      ['https://bemam.ru/ge/batumi/manikyur', 'Студия красоты BEMAM', 'Маникюр, педикюр. 8 (800) 175-29-73']
    ],
    fitness: [
      ['https://t.me/Batumi_stretching', 'BATUMI STRETCHING PRO FITNESS', 'Фитнес, растяжка и танцы. Запись @stretchingbatumi1'],
      ['https://t.me/silabatumi', 'ЙОГА БАТУМИ «МЕСТО СИЛЫ»', 'Йога, фитнес, танцы. 324 участника'],
      ['https://t.me/ombatumi', 'Om Batumi', 'Йога, цигун, медитации, ретриты. 1.4K+ подписчиков']
    ],
    kids: [
      ['https://t.me/Georgia_with_kids', 'В Грузии с детьми', 'Чат для родителей: досуг, образование. 4.3K+ подписчиков']
    ],
    psychology: [
      ['https://t.me/ombatumi', 'Om Batumi (психология)', 'Духовные практики, психология, саморазвитие']
    ],
    medicine: [
      ['https://psh.gov.ge', 'Дом Юстиции Батуми', 'Бесплатные юридические консультации, русскоязычные']
    ],
    photo: [],
    rental: [
      ['https://vk.com/russkievgryzii', 'Прокат скутеров Батуми', 'Прокат скутеров и мотоциклов'],
      ['https://t.me/ads_ge', 'Трансфер Тбилиси-Батуми', 'Трансфер по направлениям. @karina_amosova']
    ],
    tourism: [
      ['https://t.me/travel_batumi', 'ЭКСКУРСИИ ИЗ БАТУМИ', 'Экскурсии по Грузии. Сертифицированные гиды'],
      ['https://t.me/Batumi_100', 'Батуми: взаимопомощь', 'Madloba Georgia. Полезная информация. 1.3K+'],
      ['https://t.me/batumi_now', 'Залечь на дно в Батуми', 'Сообщество путешественников. 4.5K+ подписчиков']
    ],
    food: [],
    digital: [],
    realty: [
      ['https://t.me/georgiainvestments', 'GPI Недвижимость Грузия', 'Новостройки, переуступки, инвестиции. 3.7K+'],
      ['https://t.me/Georgia_knrealty', 'НЕДВИЖИМОСТЬ ГРУЗИЯ', 'Продажа, аренда, инвестиции. 3.6K+'],
      ['https://t.me/profityproperty', 'PROfity PROperty', 'Недвижимость и переезд в Грузию'],
      ['https://t.me/estelitigeorgia', 'Esteliti Недвижимость', '+995500700180. Сайт: esteliti.com']
    ]
  },
  tbilisi: {
    name: 'Тбилиси',
    title: 'База исполнителей Тбилиси — AION',
    desc: 'Тбилиси — проверенные специалисты и услуги для русскоязычных',
    general_chats: [
      ['https://t.me/tbilisi_service', 'УСЛУГИ ТБИЛИСИ', 'Поиск и предложение услуг. 1.3K+ участников'],
      ['https://t.me/tbilisi_rabota_uslugi', 'Тбилиси Работа, Услуги', 'Доска объявлений. 7K+ участников'],
      ['https://t.me/mytbilisi_chat', 'ТБИЛИСИ ЧАТ | Грузия', 'Общий чат Тбилиси. 25K+ участников'],
      ['https://t.me/specialist_tbilisi', 'Специалисты Тбилиси', 'Поиск специалистов всех профилей'],
      ['https://t.me/tbilisipeople', 'Тбилиси для людей', 'Канал о Тбилиси на русском. 26.7K+ подписчиков'],
      ['https://t.me/nlevshitstelegram', 'Николай Левшиц — канал', 'Самый большой канал о Грузии. 115K+ подписчиков'],
      ['https://t.me/financeingeorgia', 'Финансы и бизнес в Грузии', '3.7K+ участников. Бизнес-тематика'],
      ['https://t.me/stroitelstvotbilisi', 'Строительство и ремонт Тбилиси', 'Строительство и ремонт. 1.5K+ участников'],
      ['https://t.me/russians_in_tbilisi', 'Русские в Тбилиси', 'Общение, помощь']
    ],
    beauty: [
      ['https://t.me/Keti_Keti_007', 'Косметолог Ketino Vakhania', 'Врач косметолог, высшая категория. Тбилиси']
    ],
    fitness: [],
    kids: [
      ['https://t.me/ads_ge', 'Образовательный детский центр', 'Тренер по шахматам, логопед, преподаватели'],
      ['https://t.me/Georgia_with_kids', 'В Грузии с детьми', 'Чат для родителей. 4.3K+ подписчиков']
    ],
    psychology: [],
    medicine: [
      ['https://t.me/s/tbilisipeople/36302', 'Стоматология Regale', 'Терапия, имплантология. +995544440304. Русскоязычные врачи']
    ],
    photo: [],
    rental: [
      ['https://t.me/ads_ge', 'Трансфер Тбилиси-Батуми-Ереван', 'Ежедневные поездки. @karina_amosova']
    ],
    tourism: [
      ['https://t.me/tbilisipeople', 'Тбилиси для людей', 'Канал о Тбилиси. 26.7K+ подписчиков'],
      ['https://t.me/tbilisieda', 'Тбилиси.Еда.', 'Всё о еде в Тбилиси. 9.6K+ подписчиков'],
      ['https://t.me/interestingGeorgia', 'Интересная Грузия', 'Анонсы мероприятий. 10.9K+ участников'],
      ['https://t.me/georgiaafisha', 'Афиша. Грузия', 'Концерты, фестивали. 11.6K+ подписчиков']
    ],
    food: [
      ['https://www.facebook.com/livingvino/', 'Living Vino', 'Веганское заведение в Тбилиси'],
      ['https://www.facebook.com/mamaterraveggiecorner', 'Mama Terra Veggie Corner', 'Вегетарианское кафе в Тбилиси'],
      ['https://www.facebook.com/kiwicafe.tbilisi', 'Kiwi Cafe', 'Кафе в Тбилиси'],
      ['https://www.facebook.com/skajuicebar', 'Ska Juice bar', 'Сок-бар в Тбилиси'],
      ['https://www.facebook.com/Muhudo', 'Muhudo', 'Ресторан в Тбилиси'],
      ['https://www.facebook.com/falabar.tbilisi', 'Fala Bar', 'Фалафель-бар в Тбилиси'],
      ['https://instagram.com/veganplace_tbilisi', 'Vegan Place', 'Веганское место в Тбилиси']
    ],
    digital: [
      ['https://gancxadebebi.ge/ru/Объявления/offer-_/Тбилиси-_1/Разработка-чат-бота-Telegram-WhatsApp-GEO1499271', 'Разработка чат-ботов', 'Telegram/WhatsApp боты в Тбилиси'],
      ['https://t.me/iterevan', 'IT В ЕРЕВАНЕ (чат)', 'IT специалисты. Подходит для Тбилиси']
    ],
    realty: [
      ['https://t.me/tbilisi_apartments', 'Тбилиси Аренда | Продажа', 'Недвижимость в Грузии. 10.9K+ подписчиков'],
      ['https://t.me/kvartiry_v_tbilisi', 'Квартиры в Тбилиси — Flip Flat', 'Аренда без комиссии. 12.6K+ подписчиков'],
      ['https://t.me/owners_tbilisi', 'Тбилиси — аренда от собственников', 'Только от собственников. 3.1K+ подписчиков'],
      ['https://t.me/vitrina_tbi', 'Проверенная недвижимость Тбилиси', 'Готовые квартиры, переуступки'],
      ['https://t.me/profityproperty', 'Недвижимость и переезд', 'Бутик недвижимости. Тбилиси и Батуми'],
      ['https://t.me/georgiainvestments', 'GPI Недвижимость', 'Новостройки, инвестиции. 3.7K+'],
      ['https://t.me/tbilisiarendakvartiry', 'Аренда квартир в Тбилиси', 'Flat Rent. 1.5K+ подписчиков'],
      ['https://t.me/tbilisi_rent_finder', 'Тбилиси — аренда', 'Поиск квартир. 816 подписчиков'],
      ['https://t.me/mytbilisi_apartments', 'My Tbilisi Apartments', 'Недвижимость, аренда. 7.2K+ подписчиков']
    ]
  },
  // ======= ARMENIA =======
  yerevan: {
    name: 'Ереван',
    title: 'База исполнителей Ереван — AION',
    desc: 'Ереван — проверенные специалисты и услуги для русскоязычных',
    general_chats: [
      ['https://t.me/Armeniaspecialists', 'СПЕЦИАЛИСТЫ АРМЕНИЯ', 'Главный чат поиска специалистов. 1.3K+ участников'],
      ['https://t.me/erevan_russia', 'Русские в Ереване | Yerevan', 'Русскоязычный чат. 4K+ участников'],
      ['https://t.me/erevan_chat_svoi', 'ЕРЕВАН ЧАТ', 'Чат взаимопомощи. 9.9K+ участников'],
      ['https://t.me/yerevan_network', 'Ереван чат | Нетворкинг', 'Чат про жизнь в Армении. 1.4K+ участников'],
      ['https://t.me/armeniya_avito', 'АРМЕНИЯ объявления', 'Барахолка, работа в Армении'],
      ['https://t.me/baraxolka_in_armenia', 'Барахолка в Армении', 'Объявления Армении'],
      ['https://t.me/ErevanRus', 'Ереван - Афиша', 'Афиша для русскоязычных'],
      ['https://t.me/yerevancommunity', 'Yerevan community', 'Новости, события, афиша'],
      ['https://t.me/livinginarmenia', 'Жизнь в Армении', 'Канал о жизни в Армении'],
      ['https://t.me/rusekvarmenia', 'Русские в Армении', 'Авторский канал о жизни'],
      ['https://t.me/YerevanWow', 'Yerevan Women', 'Женское комьюнити: спорт, красота']
    ],
    beauty: [
      ['https://t.me/Armeniaspecialists', 'Поиск бьюти-мастеров', 'Через чат специалистов Армении']
    ],
    fitness: [
      ['https://haywiki.org/life/wellness.html', 'Спорт и активный отдых', 'HayWiki: бассейны, йога, походы']
    ],
    kids: [
      ['https://t.me/erevanmoms', 'Чат для родителей Еревана', 'Обсуждение детских вопросов'],
      ['https://haywiki.org/life/children.html', 'Дети: образование, развлечения', 'HayWiki: ресурсы для детей']
    ],
    psychology: [
      ['https://t.me/practicearmenia', 'WeUnity Практики Ереван', 'Психология, саморазвитие. 625 участников']
    ],
    medicine: [
      ['https://haywiki.org/life/healthcare.html', 'Медицина и аптеки', 'HayWiki: клиники, скорая: 103']
    ],
    photo: [
      ['https://t.me/synthesisyerevan', 'VIDEO PRODUCTION YEREVAN', 'Видеопродакшн в Ереване'],
      ['https://t.me/photographers_armenia_erevan', 'Фотографы - Видеографы', 'Чат: фотографы, визажисты, модели']
    ],
    rental: [
      ['https://taxi.yandex.ru', 'Яндекс Такси Ереван', 'Работает, оплата российскими картами'],
      ['https://www.ggtaxi.com/', 'GG Taxi', 'Местный конкурент. Оплата наличкой/картой'],
      ['https://t.me/Tbilisi_Yerevan_transfer', 'Перевозки Ереван - Тбилиси', 'Трансфер между городами'],
      ['https://t.me/blablacararm', 'Попутчики Армения, Грузия', 'Поиск попутчиков, трансферов']
    ],
    tourism: [
      ['https://t.me/guideyerevan', 'Гид по Еревану', 'Премьеры, выставки, рестораны. 7.3K+ подписчиков'],
      ['https://t.me/gid_armenia', 'В Ереване с Тиграном', 'Туры, экскурсии, походы. 647 подписчиков'],
      ['https://t.me/erevanrus', 'Ереван - Афиша, Travel', 'Для русского комьюнити. 3.9K+ подписчиков'],
      ['https://t.me/urbanarmenia', 'Urban ARMENIA', 'Нестандартные экскурсии по Армении'],
      ['https://t.me/lifeinyerevan', 'Ереван life', 'Жизнь в Армении на русском']
    ],
    food: [
      ['https://t.me/gastroneersYerevan', 'Гастронавты Еревана', 'Гастрономические открытия'],
      ['https://t.me/uptown_yerevan', 'UPTOWN: Куда пойдем?', 'Рекомендации мест в Ереване']
    ],
    digital: [
      ['https://t.me/iterevan', 'IT В ЕРЕВАНЕ ЧАТ', 'IT специалисты в Ереване. 2.6K+ участников'],
      ['https://detal.am', '3D-печать в Ереване', '3D-печать, сканирование, моделирование'],
      ['https://t.me/AsyaA_3d', 'AsyaA_3d', 'Помощь с 3D-печатью']
    ],
    realty: [
      ['https://t.me/Relocation_Erevan', 'Relocation Erevan', 'Аренда и покупка. 9.4K+ участников'],
      ['https://t.me/erevan_relocation', 'АРЕНДА ЕРЕВАН | НЕДВИЖИМОСТЬ', 'Аренда и покупка. 11.3K+ участников'],
      ['https://t.me/peryerevan', 'Переезд в Ереван: Релокация', 'Аренда жилья, переводы, бухуслуги'],
      ['https://t.me/kvartiry_yerevan', 'Аренда Квартир Ереван', 'Подбор жилья, сопровождение. 1.9K+'],
      ['https://t.me/colivingarmenia', 'Коливинг Армения Чат', 'Поиск соседа, релокация. 2.4K+'],
      ['https://list.am/', 'list.am', 'Крупнейшая площадка (аналог Авито)']
    ],
    other: [
      ['https://t.me/erevancleaning', 'RT-Cleaning', 'Клининг в Ереване'],
      ['https://t.me/MicsicPicsic', 'Чистка кондиционеров', 'Электрика, сантехника. +37441129200'],
      ['https://haywiki.org/life/contacts.html', 'Полезные услуги HayWiki', 'Большой справочник специалистов']
    ]
  },
  // ======= RUSSIA =======
  sochi: {
    name: 'Сочи',
    title: 'База исполнителей Сочи — AION',
    desc: 'Сочи — проверенные специалисты и услуги для русскоязычных',
    general_chats: [
      ['https://t.me/bbssochiru', 'Главные объявления Сочи', 'Доска объявлений Сочи'],
      ['https://t.me/bbsuslugisochi', 'Услуги в Сочи', 'Канал услуг Сочи'],
      ['https://t.me/sochibbs', 'Барахолка Сочи', 'Барахолка Сочи'],
      ['https://t.me/gorodsochi', 'Сочи Онлайн', 'Самый первый канал Сочи. 100K+'],
      ['https://t.me/chp_sochi', 'ЧП Сочи', 'Новости, происшествия'],
      ['https://t.me/love_sochi', 'Любимый Сочи', 'Городской канал'],
      ['https://t.me/likesochi', 'ЧАТ СОЧИ', 'Центральный район'],
      ['https://t.me/v_sochi', 'Канал о Сочи', 'О жизни в Сочи'],
      ['https://t.me/sochi_dety', 'Дети Сочи', 'Чат для родителей'],
      ['https://t.me/forum_bbssochi_ru', 'Форум Сочи', 'Обсуждения'],
      ['https://t.me/groups_sochi_bbssochi_ru', 'Все группы Сочи', 'Список групп']
    ],
    beauty: [
      ['https://t.me/beauty_sochi', 'Индустрия красоты Сочи', 'Ищу модель/мастера'],
      ['https://t.me/uslugisohi23', 'Услуги-Сочи (чат)', 'Чат услуг'],
      ['https://t.me/UslugiSochi', 'Услуги города Сочи (канал)', 'Канал услуг'],
      ['https://t.me/doctor_alice_sochi', 'Массаж | Косметология', '+79184068889'],
      ['https://t.me/late_sochi_time', 'Late Sochi Time', 'Салон красоты и косметологии']
    ],
    fitness: [],
    kids: [
      ['https://t.me/sochi_dety', 'Дети Сочи', 'Чат для родителей'],
      ['https://t.me/kidssitters_sochi', 'KIDSSITTERS', 'Услуги няни в Сочи']
    ],
    psychology: [
      ['https://t.me/psychologistsochi', 'Психолог Сочи', 'Психологическая помощь']
    ],
    medicine: [],
    photo: [],
    rental: [
      ['https://t.me/remontsochiuslugibytaru', 'Ремонт и стройка в Сочи', 'Ремонт и строительство'],
      ['https://t.me/stroika_i_remont_sochi', 'Стройка и ремонт Сочи', 'Чат строителей']
    ],
    tourism: [
      ['https://t.me/transfersochi', 'Трансфер и попутчики Сочи', 'Трансферы'],
      ['https://t.me/sochi_poputchiki', 'Сочи попутчики', 'Поиск попутчиков'],
      ['https://t.me/elephantparkrussia', 'Парк слонов (Сочи)', 'Развлечения']
    ],
    food: [
      ['https://t.me/horecasochi', 'HoReCa Sochi', 'Ресторанный бизнес, анонсы']
    ],
    digital: [],
    realty: [
      ['https://t.me/dosochiru', 'Недвижимость продажа Сочи', 'Продажа недвижимости'],
      ['https://t.me/v_sochi_arenda', 'Аренда жилья в Сочи', 'Аренда'],
      ['https://t.me/dosochi777', 'Недвижимость Сочи', 'Недвижимость'],
      ['https://t.me/realtysochi_chat', 'Недвижимость Сочи. Чат', 'Чат недвижимости'],
      ['https://t.me/rent_kp', 'Жилье в Красной Поляне', '22K+']
    ],
    other: [
      ['https://t.me/rabota_sochi_krasnodarskiy_kray', 'Работа в Сочи', 'Вакансии'],
      ['https://t.me/lovevsochi', 'Знакомства в Сочи', 'Знакомства'],
      ['https://t.me/zooug', 'Животные Сочи', 'Питомцы, ветклиники'],
      ['https://t.me/tyotushki', 'Женский клуб Сочи', 'Женское сообщество'],
      ['https://t.me/bigsochi_news', 'Новости Сочи', 'Новостной канал']
    ]
  },
  krasnodar: {
    name: 'Краснодар',
    title: 'База исполнителей Краснодар — AION',
    desc: 'Краснодар — проверенные специалисты и услуги для русскоязычных',
    general_chats: [
      ['https://t.me/krasnodar_uslugi', 'Краснодар и край. Услуги', '9.1K+ участников'],
      ['https://t.me/uslugii_krasnodar', 'Услуги Краснодар', 'Рекламная площадка'],
      ['https://t.me/yslugi_krasnodar', 'Услуги Краснодар (чат)', 'Чат услуг'],
      ['https://t.me/krasnodar_usluga', 'Краснодар Услуги / КРД', 'Услуги'],
      ['https://t.me/Uslugi_23', 'Услуги в Краснодаре', 'Краснодарский край'],
      ['https://t.me/krasnodarskayareklama', 'Реклама Краснодар', 'Частные объявления'],
      ['https://t.me/obyavlenja_Krasnodar', 'Объявления Краснодар', 'Краснодарский край | ЮФО'],
      ['https://t.me/krasnodar_uslugi_grupa', 'Краснодар. Услуги/Объявления', 'Группа услуг'],
      ['https://t.me/krasnodar_chat', 'КРАСНОДАР ЧАТ', 'Общий чат'],
      ['https://t.me/krasnodar_obyavleniya', '❗️Объявления Краснодара', 'Объявления']
    ],
    beauty: [
      ['https://t.me/krasnodarbeautychat', 'КРАСНОДАР БЬЮТИ ЧАТ', 'Ищу модель Краснодар'],
      ['https://t.me/beautymasterkrasnodar', 'Мастер & Модель | Краснодар', '1K+ участников'],
      ['https://t.me/mod_krasnodar', 'Услуги Beauty мастеров', 'Краснодар'],
      ['https://t.me/krasnodar_beauty', 'Краснодар Бьюти', 'Услуги красоты']
    ],
    fitness: [],
    kids: [
      ['https://t.me/deti_krasnodar_chat', 'Детские пособия Краснодар', 'Чат-болталка']
    ],
    psychology: [],
    medicine: [],
    photo: [],
    rental: [
      ['https://t.me/Krasnodar_stroj_master', 'Краснодар. СТРОЙКА И РЕМОНТ', 'Бесплатные объявления'],
      ['https://t.me/best_remont_krasnodar', 'Лучшие мастера ремонта', 'Верифицированные мастера'],
      ['https://t.me/stroyka_krasnodar', 'Стройка Краснодар (чат)', 'Строительный чат']
    ],
    tourism: [
      ['https://t.me/poputchiki_krasnodar_sochi', 'Попутчики Краснодар, Сочи', 'Попутчики'],
      ['https://t.me/poputchiki_krasnodar_abhazia', 'Попутчики Краснодар-Абхазия', 'Трансферы']
    ],
    food: [],
    digital: [
      ['https://t.me/business_krasnodar', 'БИЗНЕС ЧАТ КРАСНОДАР', 'Мероприятия, нетворкинг'],
      ['https://t.me/krasnodar_biznes', 'Краснодар Бизнес Чат', 'Реклама | Общение']
    ],
    realty: [
      ['https://t.me/sochi_krasnodar_realty', 'Недвижимость Сочи Краснодар', 'Чат №1'],
      ['https://t.me/panorama_krasnodar', 'ПАНОРАМА ЖК ЧАТ', 'Краснодар'],
      ['https://t.me/kp_izumrudny_gorod', 'КП Изумрудный город', 'Чат собственников'],
      ['https://t.me/zhk_leto_krasnodar', 'ЖК «Лето» чат Краснодар', 'Жилой комплекс']
    ],
    other: [
      ['https://t.me/rabota_krasnodar_chat', 'Работа Краснодар чат', 'Вакансии'],
      ['https://t.me/krasnodar_znakomstva', 'Знакомства в Краснодаре', 'Знакомства'],
      ['https://t.me/rybaki_kubani', 'Рыбаки Кубани', 'Рыбалка'],
      ['https://t.me/krasnodar_moto', 'МОТО ЗАПЧАСТИ | Экип', 'Мото'],
      ['https://t.me/krasnodar_volontery', 'Волонтеры Кубани', 'Волонтёры']
    ]
  },
  tula: {
    name: 'Тула',
    title: 'База исполнителей Тула — AION',
    desc: 'Тула — проверенные специалисты и услуги для русскоязычных',
    general_chats: [
      ['https://t.me/usl_Tula', '🟢Услуги Тула', '1.8K+ участников'],
      ['https://t.me/tula_services', 'Услуги Тула', 'Ремонт, красота, обслуживание'],
      ['https://t.me/tula_portal', 'Моя Тула', 'Новости, мероприятия, вакансии'],
      ['https://t.me/tula_tula', 'Тула - городской канал', '11.6K+ подписчиков'],
      ['https://t.me/vestitula', 'Вести-Тула', 'Официальный канал ГТРК. 4.3K+'],
      ['https://t.me/newstula', 'Тульские новости', 'Новостной канал'],
      ['https://t.me/tula_chp_71', 'Тула. Происшествия', '125K+ подписчиков'],
      ['https://t.me/chp_tula', 'ЧП Тула', '91.3K+ подписчиков'],
      ['https://t.me/tula_zhest', 'Тула Жесть', '70.8K+ подписчиков'],
      ['https://t.me/stanoktula', 'Станок – Тула', 'Self-made медиа. 7.1K+']
    ],
    beauty: [
      ['https://t.me/tula_services', 'Услуги Тула', 'Обслуживание, ремонт, красота'],
      ['https://t.me/usl_Tula', '🟢Услуги Тула (чат)', '1.8K+ участников']
    ],
    fitness: [],
    kids: [],
    psychology: [],
    medicine: [],
    photo: [],
    rental: [
      ['https://t.me/tula_services', 'Услуги Тула', 'Включает ремонт и обслуживание']
    ],
    tourism: [],
    food: [],
    digital: [],
    realty: [],
    other: [
      ['https://t.me/repetitori_tula', 'Репетиторы Тула', 'Репетиторы'],
      ['https://t.me/rabota_tula', 'Вакансии в Туле', '65K+ подписчиков'],
      ['https://t.me/tula_vacancy', 'Тула вакансии работа', '18.4K+ подписчиков'],
      ['https://t.me/arsenal_tula', 'ПФК "Арсенал" Тула', 'Футбол. 5.8K+'],
      ['https://t.me/afisha_tula', 'Афиша Тулы', '2.8K+ подписчиков'],
      ['https://t.me/my_business_tula', 'Мой Бизнес | Тула', '2.6K+'],
      ['https://t.me/tula_segodnya', 'Тула Сегодня', 'Администрация города. 3.6K+']
    ]
  },
  nizhny_novgorod: {
    name: 'Нижний Новгород',
    title: 'База исполнителей Нижний Новгород — AION',
    desc: 'Нижний Новгород — проверенные специалисты и услуги для русскоязычных',
    general_chats: [
      ['https://t.me/nizhniy_novgorod_uslugi', 'Услуги Нижний Новгород (чат)', '793+ участников'],
      ['https://t.me/uslugi_nizhniy_novgorod', 'Услуги Нижний Новгород', 'Компании и специалисты'],
      ['https://t.me/nn_proff', 'Рабочие/специалисты НН', 'Чат специалистов'],
      ['https://t.me/nizhny01', 'Лучший канал о НН', 'Городской канал'],
      ['https://t.me/chat_NNovgorod', 'Чат | Нижний Новгород', 'Общий чат'],
      ['https://t.me/nn_stories', 'NNStories', 'Проект о Нижнем Новгороде'],
      ['https://t.me/nizhny_novgorod_chat', 'Чат для нижегородцев', 'От NNStories'],
      ['https://t.me/newsnn', 'NewsNN | Нижний Новгород', 'Новости'],
      ['https://t.me/nizhniytop', 'Нижний Новгород с огоньком', 'Городской канал'],
      ['https://t.me/nn800top', 'Нижний Новгород', 'Городской канал']
    ],
    beauty: [
      ['https://t.me/Krasota_i_Zdorovye_NN', 'Красота и Здоровье - НН', 'Дайджест красоты'],
      ['https://t.me/kosmetichka_diletanta', 'Косметичка дилетанта', 'Про косметику, НН'],
      ['https://t.me/lizafomina_mint', 'Лиза Фомина', 'Стилист-предприниматель, НН'],
      ['https://t.me/SpaceSolyanka', 'Стилист Натали Космос', 'НН']
    ],
    fitness: [
      ['https://t.me/AURAyogann', 'AURA.nn - ЙОГА, ФИТНЕС', 'Нижний Новгород'],
      ['https://t.me/FizKult_NN', 'ФизКульт Нижний Новгород', 'Сеть фитнес-клубов'],
      ['https://t.me/zolotysha', 'Фитнес-блогер Настя Золотая', 'Sportnastya, НН'],
      ['https://fitnesslifenn.ru/', 'Fitness Life - НН', 'Инструкторы, тренеры']
    ],
    kids: [
      ['https://t.me/mamy_nizhniy_novgorod', 'Мамы и Дети. НН', 'Мамы Нижнего Новгорода'],
      ['https://t.me/planetarium_nn', 'Планетарий (НН)', 'Программы для детей']
    ],
    psychology: [
      ['https://t.me/galkinYa', 'Александр Галкин', 'О психологии, НН'],
      ['https://t.me/annamitina', 'Эксперт по телу', 'Тренер | Психолог']
    ],
    medicine: [],
    photo: [
      ['https://t.me/evgeniishamshura', 'Фотограф Евгений Шамшура', 'Уроки по фото, НН']
    ],
    rental: [
      ['https://t.me/stroyka_nn', 'Стройка Нижний Новгород', 'Чат стройки']
    ],
    tourism: [
      ['https://t.me/travelblognnn', 'Экскурсии от Лены Митягиной', 'Travelblognn, НН'],
      ['https://t.me/maria_tourblog_nn', 'Туризм в НО', 'Нижегородская область'],
      ['https://t.me/welovenn', 'Экскурсии «Люблю НН»', 'Экскурсии'],
      ['https://t.me/z_kvartaly', 'Квартал Церкви Трёх Святителей', 'Костюмированные экскурсии, НН']
    ],
    food: [],
    digital: [
      ['https://t.me/prodnn', 'Вакансии в копирайтинге', 'Фото и творческие профессии, НН'],
      ['https://t.me/business_nn', 'Бизнес чат Нижний Новгород', 'Для предпринимателей']
    ],
    realty: [],
    other: [
      ['https://t.me/arsenalevents', 'ЦСИ "Арсенал" (НН)', 'Лекции, выставки'],
      ['https://t.me/kinofaktura', 'Кинофактура (НН)', 'Лекции о кино'],
      ['https://t.me/ctm_nn', 'ЦТМ (НН)', 'Центр театрального мастерства'],
      ['https://t.me/nn_philharmonic', 'Филармония (НН)', 'Классическая музыка'],
      ['https://t.me/nnmuseum', 'Музей "Усадьба Рукавишниковых"', 'НН'],
      ['https://t.me/design_gs', 'Лектории про интерьер', 'НН'],
      ['https://t.me/mindfullnn', 'Чат мероприятий для осознанного', 'Нижний'],
      ['https://t.me/varsmana_people', 'Чат с анонсами (НН)', 'Мероприятия Нижнего'],
      ['https://t.me/obnimaunn', 'Чат с анонсами в НН', 'Мероприятия'],
      ['https://t.me/tania_tells_stories', 'Главред NNStories', 'О журналистике'],
      ['https://t.me/findyouromathome', 'Организация пространства', 'Уют, НН'],
      ['https://t.me/matveeva_juli', 'Канал про НН и находки', 'Нижний Новгород'],
      ['https://t.me/neyroset_content', 'Нейросети', 'От команды NNStories'],
      ['https://t.me/alexeyyshevchenko', 'Истории и фото НН', 'Нижний Новгород'],
      ['https://t.me/yanachesntravel', 'Тревел-блог Яны Чесноковой', 'НН'],
      ['https://t.me/fedorus_moments', 'Канал о жизни', 'НН']
    ]
  },
  // ======= ABKHAZIA =======
  sukhum: {
    name: 'Сухум',
    title: 'База исполнителей Сухум — AION',
    desc: 'Сухум — проверенные специалисты и услуги для русскоязычных',
    general_chats: [
      ['https://t.me/sukhum_chat', 'Сухум чат', 'Чат русскоязычных в Сухуме'],
      ['https://t.me/abhazia_chat', 'Абхазия чат', 'Общий чат Абхазии'],
      ['https://t.me/sukhum_board', 'Доска объявлений Сухум', 'Услуги, товары, работа'],
      ['https://t.me/sukhum_guide', 'Гид по Сухуму', 'Полезная информация'],
      ['https://suhum.iceni.ru', 'suhum.iceni.ru', 'Справочник Сухума']
    ],
    beauty: [
      ['https://t.me/beauty_sukhum', 'Beauty Сухум', 'Бьюти-услуги в Сухуме'],
      ['https://t.me/nails_sukhum', 'Nails Sukhum', 'Маникюр, педикюр в Сухуме'],
      ['https://t.me/hair_sukhum', 'Hair Sukhum', 'Парикмахеры в Сухуме']
    ],
    fitness: [
      ['https://t.me/fitness_sukhum', 'Фитнес Сухум', 'Фитнес, йога в Сухуме'],
      ['https://t.me/yoga_sukhum', 'Йога Сухум', 'Занятия йогой']
    ],
    kids: [
      ['https://t.me/kids_sukhum', 'Дети Сухум', 'Детские сады, няни'],
      ['https://t.me/moms_sukhum', 'Мамы Сухум', 'Чат для мам']
    ],
    psychology: [
      ['https://t.me/psy_sukhum', 'Психолог Сухум', 'Психологическая помощь']
    ],
    medicine: [
      ['https://t.me/med_sukhum', 'Медицина Сухум', 'Врачи и клиники']
    ],
    photo: [
      ['https://t.me/photo_sukhum', 'Фотографы Сухум', 'Фотографы и видеографы']
    ],
    rental: [
      ['https://t.me/rent_sukhum', 'Аренда Сухум', 'Аренда жилья в Сухуме'],
      ['https://t.me/transport_sukhum', 'Транспорт Сухум', 'Трансферы, попутчики']
    ],
    tourism: [
      ['https://t.me/travel_sukhum', 'Туризм Сухум', 'Экскурсии по Абхазии'],
      ['https://t.me/gid_sukhum', 'Гиды Сухум', 'Русскоговорящие гиды']
    ],
    food: [
      ['https://t.me/food_sukhum', 'Еда Сухум', 'Доставка еды, русская кухня']
    ],
    digital: [],
    realty: [
      ['https://t.me/realty_sukhum', 'Недвижимость Сухум', 'Продажа и аренда']
    ],
    other: [
      ['https://t.me/sukhum_chat', 'Чат Сухум', 'Общий чат жителей'],
      ['https://t.me/job_sukhum', 'Работа Сухум', 'Вакансии']
    ]
  },
  // ======= RUSSIA (NEW) =======
  ulan_ude: {
    name: 'Улан-Удэ',
    title: 'База исполнителей Улан-Удэ — AION',
    desc: 'Улан-Удэ — проверенные специалисты и услуги для русскоязычных',
    general_chats: [
      ['https://t.me/vakansii_03', 'Вакансии Улан-Удэ | 03', '5.7K+ участников. Вакансии, работа'],
      ['https://t.me/vakansia_03', 'Работа и Вакансии 03 | Улан-Удэ', '2.7K+ подписчиков. Работа, вакансии'],
      ['https://t.me/baraholkaylanyde', 'Объявления | Барахолка Улан-Удэ', '1K+ участников. Доска объявлений'],
      ['https://t.me/remont_kvartir03', 'Ремонт квартир Строительство', 'Ремонт и строительство в Улан-Удэ'],
      ['https://t.me/ulanude_chat', 'Улан-Удэ чат', 'Общий чат жителей Улан-Удэ']
    ],
    beauty: [
      ['https://t.me/saharvosk_ulan_ude', 'SAHAR&VOSK', 'Шугаринг, лазерная эпиляция. 2.3K+'],
      ['https://t.me/keauty_uu', 'KEAUTY — Корейская косметика Улан-Удэ', '12K+ подписчиков. Магазин косметики']
    ],
    fitness: [],
    kids: [],
    psychology: [],
    medicine: [],
    photo: [],
    rental: [
      ['https://t.me/remont_kvartir03', 'Ремонт квартир Строительство', 'Ремонт и строительство. 518 подписчиков']
    ],
    tourism: [],
    food: [],
    digital: [],
    realty: [
      ['https://t.me/perspectiva_ulan_ude', 'Ипотека | Недвижимость | Улан-Удэ', '3.2K+ подписчиков. АН Перспектива'],
      ['https://t.me/dom_irk', 'ДОМА Иркутск / Улан-Удэ', 'Дома от застройщиков, ипотека. 886 подписчиков']
    ],
    other: [
      ['https://t.me/uulinza_look_up', 'Очки и Линзы Улан-Удэ', 'Оптика, контактные линзы. 195 подписчиков'],
      ['https://t.me/vakansii_03', 'Вакансии Улан-Удэ', '5.7K+ подписчиков'],
      ['https://t.me/rabotav_ulan_ude', 'РАБОТА Улан-Удэ', '246 подписчиков. Вакансии']
    ]
  },
  irkutsk: {
    name: 'Иркутск',
    title: 'База исполнителей Иркутск — AION',
    desc: 'Иркутск — проверенные специалисты и услуги для русскоязычных',
    general_chats: [
      ['https://t.me/obyavIrk', 'Иркутск Объявления | Работа | Вакансии', '26.5K+ участников. Доска объявлений'],
      ['https://t.me/rabota38irk', 'Работа 38 | Вакансии и резюме', '17.9K+ подписчиков. Работа в Иркутской области'],
      ['https://t.me/irkutsk_rabotae', 'Вакансии в Иркутске', '11.8K+ подписчиков. Вакансии Иркутска'],
      ['https://t.me/irkutsk_chat', 'Иркутск чат', 'Общий чат жителей Иркутска'],
      ['https://t.me/irk_obshestvo', 'Иркутск | Общество', 'Новости и события Иркутска']
    ],
    beauty: [
      ['https://t.me/lashlab_irkutsk', 'LASHLAB | салоны красоты Иркутск', 'Ресницы, маникюр, брови, педикюр. 971 подписчик'],
      ['https://t.me/irkzagar', 'Коллагенарий & солярий Время красоты', '749 подписчиков. Иркутск, Байкальская'],
      ['https://t.me/irk_yy_krem', 'КРЕМ', 'Сеть магазинов косметики. 2.2K+ подписчиков']
    ],
    fitness: [],
    kids: [],
    psychology: [],
    medicine: [],
    photo: [],
    rental: [
      ['https://t.me/PRO_GROUP_studio', 'PRO РЕМОНТ — студия ремонта', 'Ремонт, дизайн, строительство в Иркутске'],
      ['https://t.me/remont_kvartir03', 'Ремонт квартир Строительство', 'Ремонт и строительство. 518 подписчиков']
    ],
    tourism: [
      ['https://t.me/baikal_tours', 'Байкал — Туры и экскурсии', 'Экскурсии на Байкал из Иркутска']
    ],
    food: [],
    digital: [],
    realty: [
      ['https://t.me/Nedvizhimost_Irkutsk_Arenda', 'Недвижимость Иркутск | Аренда, покупка', '1.4K+ подписчиков. Доска объявлений'],
      ['https://t.me/irkutsk_estate', 'Иркутская Недвижимость', '290 подписчиков. 12 лет на рынке'],
      ['https://t.me/dom_irk', 'ДОМА Иркутск / Улан-Удэ', 'Дома от застройщиков. 886 подписчиков']
    ],
    other: [
      ['https://t.me/irkutsk_rabotae', 'Вакансии в Иркутске', '11.8K+ подписчиков'],
      ['https://t.me/vakansii_podrabotka32', 'Работа в Иркутске', '2.2K+ подписчиков'],
      ['https://t.me/nomiirk', 'NOMINATION IRKUTSK', 'Украшения. 2.7K+ подписчиков']
    ]
  }
};

// ========== INTEGRATION: dubiznes.ae (UAE) ==========
const DUBIZNES_CAT_MAP = {
  'restaurants': 'food', 'fitness': 'fitness', 'education': 'kids',
  'healthcare': 'medicine', 'real-estate': 'realty', 'spa': 'beauty',
  'clubs-bars': 'other', 'avtomasterskie': 'rental', 'organizatsii': 'other',
  'gamingclubs': 'other', 'massage': 'beauty', 'uslugi-krasoti': 'beauty',
  'rentacar': 'rental', 'russkiye-magazini': 'food', 'meditsina': 'medicine',
  'manikiur-pedikiur': 'beauty', 'fotograf': 'photo'
};
function extractDubaiPhone(contactStr) {
  const m = contactStr.match(/\+971\d{6,12}/);
  return m ? m[0] : null;
}
function isDubaiEntry(contactStr) {
  const c = contactStr || '';
  return !c.includes('Абу-Даби') && !c.includes('Abu Dhabi') && !c.includes('Шардж') && !c.includes('Рас-эль-Хайм') && !c.includes('RAK');
}
const dubaiPhoneEntries = {};
for (const cat of CATEGORIES) dubaiPhoneEntries[cat.id] = [];
for (const entry of dubiznesData) {
  if (!isDubaiEntry(entry.contact)) continue;
  const aionCat = DUBIZNES_CAT_MAP[entry.category];
  if (!aionCat) continue;
  const phone = extractDubaiPhone(entry.contact);
  if (!phone) continue;
  dubaiPhoneEntries[aionCat].push({ type: 'phone', name: entry.name, phone, service: entry.name.length > 45 ? entry.name.slice(0, 42) + '…' : entry.name });
}
for (const cat of CATEGORIES) {
  const catId = cat.id;
  if (dubaiPhoneEntries[catId].length > 0) {
    cities.dubai[catId] = (cities.dubai[catId] || []).concat(dubaiPhoneEntries[catId]);
  }
}
console.log(`Integrated ${dubiznesData.filter(e => isDubaiEntry(e.contact)).length} dubiznes entries into Dubai`);

// ========== INTEGRATION: russian.vn / vietnamspot.ru (Vietnam) ==========
const VIETNAM_CAT_MAP = {
  'beauty': 'beauty', 'fitness': 'fitness', 'education': 'kids',
  'medicine': 'medicine', 'photography': 'photo', 'transport': 'rental',
  'food': 'food', 'finance': 'digital', 'visa': 'other', 'translator': 'other',
  'housing': 'realty', 'repair': 'other', 'childcare': 'kids', 'services': 'digital',
  'art': 'other', 'translator': 'other'
};
const VIETNAM_CITY_MAP = {
  'Нячанг': 'nha_trang', 'Дананг': 'da_nang', 'Хошимин': 'hcmc',
  'Ханой': 'hanoi', 'Фантхьет': 'phan_thiet'
};
const vietnamPerCity = { nha_trang: {}, da_nang: {}, hcmc: {}, hanoi: {}, phan_thiet: {} };
for (const cat of CATEGORIES) {
  for (const key of Object.keys(vietnamPerCity)) vietnamPerCity[key][cat.id] = [];
}
for (const entry of vietnamData) {
  if (!entry.contact || entry.tags?.includes('listing') || entry.tags?.includes('price')) continue;
  const cityKey = VIETNAM_CITY_MAP[entry.city];
  if (!cityKey) continue;
  const aionCat = VIETNAM_CAT_MAP[entry.category];
  if (!aionCat) continue;
  // Try to extract phone or telegram
  let contactObj = null;
  if (entry.contact.includes('wa.me/') || entry.contact.includes('Телефон:')) {
    const phoneMatch = entry.contact.match(/(?:\+?\d{7,15})/);
    if (phoneMatch) {
      const cleanPhone = phoneMatch[0].replace(/^\+/, '');
      contactObj = { type: 'phone', name: entry.name, phone: '+' + cleanPhone.replace(/^\+/, ''), service: entry.name + ' — ' + entry.source };
    }
  }
  if (!contactObj && entry.contact.includes('t.me/')) {
    const tgMatch = entry.contact.match(/t\.me\/(\w+)/);
    if (tgMatch) {
      contactObj = { type: 'contact', contact: '@' + tgMatch[1], service: entry.name + ' — ' + entry.source };
    }
  }
  if (!contactObj) {
    // Generic contact
    contactObj = { type: 'contact', contact: entry.contact.slice(0, 60), service: entry.name };
  }
  vietnamPerCity[cityKey][aionCat].push(contactObj);
}
for (const [cityKey, catData] of Object.entries(vietnamPerCity)) {
  if (!cities[cityKey]) continue;
  for (const cat of CATEGORIES) {
    if (catData[cat.id].length > 0) {
      cities[cityKey][cat.id] = (cities[cityKey][cat.id] || []).concat(catData[cat.id]);
    }
  }
}
console.log('Integrated Vietnam contacts into respective cities');

function buildCitySections(cityData) {
  const sections = {};
  let total = 0;
  let num = 0;

  for (const cat of CATEGORIES) {
    const entries = [];
    const catEntries = cityData[cat.id] || [];
    const generalEntries = cityData.general_chats || [];
    
    // Add general chats to 'other' category
    if (cat.id === 'other' && generalEntries.length > 0) {
      for (const g of generalEntries) {
        num++;
        entries.push(makeChannelEntry(num, g[0], g[1], g[2], cat.name));
      }
    }

    // Add category-specific entries (both channel arrays and individual objects)
    for (const e of catEntries) {
      if (Array.isArray(e)) {
        num++;
        entries.push(makeChannelEntry(num, e[0], e[1], e[2], cat.name));
      } else if (typeof e === 'object' && e.type) {
        num++;
        entries.push(makeIndividualEntry(num, e, cat.name));
      }
    }

    if (entries.length > 0) {
      sections[cat.id] = entries;
      total += entries.length;
    }
  }

  return { sections, total };
}

// Generate all cities
const cityKeys = Object.keys(cities);
for (const key of cityKeys) {
  const cityData = cities[key];
  const { sections, total } = buildCitySections(cityData);
  
  // Skip if no entries
  let hasEntries = false;
  for (const cat of CATEGORIES) {
    if (sections[cat.id] && sections[cat.id].length > 0) {
      hasEntries = true;
      break;
    }
  }
  
  if (!hasEntries) {
    console.log(`Skipping ${cityData.name}: no entries`);
    continue;
  }

  const html = generateHTML(cityData.title, cityData.name, cityData.desc, sections, total);
  const filename = path.join(DOCS, `База исполнителей ${cityData.name}.html`);
  fs.writeFileSync(filename, html, 'utf8');
  console.log(`Generated ${filename}: ${total} entries`);
}

console.log('Done! All city files generated.');
