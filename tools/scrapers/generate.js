const fs = require('fs');
const data = JSON.parse(fs.readFileSync('C:/AION/russian_service_providers_turkey.json', 'utf8'));

const CATEGORY_EMOJI = {beauty:'💅',fitness:'🏋️',kids:'👶',psychology:'🧠',medicine:'🩺',photo_video:'📸',rental_transport:'🚗',tourism:'🏝️',food:'🍽️',digital:'💻',realty:'🏠'};
const CATEGORY_RU = {beauty:'Красота',fitness:'Фитнес',kids:'Дети',psychology:'Психология',medicine:'Медицина',photo_video:'Фото/Видео',rental_transport:'Аренда/Транспорт',tourism:'Туризм',food:'Еда',digital:'Цифровые услуги',realty:'Недвижимость'};

function esc(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

function genCity(city) {
  let h = `<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Русскоязычные специалисты - ${esc(city.name_ru)}</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#f5f5f5;color:#333}
.container{max-width:1100px;margin:0 auto;padding:20px}
h1{font-size:28px;margin-bottom:5px;color:#1a1a2e}
.sub{font-size:16px;color:#666;margin-bottom:20px}
h2.sec{font-size:22px;margin:30px 0 15px;padding-bottom:8px;border-bottom:3px solid #e94560;color:#1a1a2e}
.card{background:#fff;border-radius:10px;padding:15px;margin-bottom:10px;box-shadow:0 2px 5px rgba(0,0,0,.08)}
.card:hover{transform:translateY(-2px);box-shadow:0 4px 10px rgba(0,0,0,.12)}
.card a{color:#e94560;text-decoration:none;font-weight:600;font-size:16px}
.card a:hover{text-decoration:underline}
.card .d{color:#555;font-size:14px;margin-top:5px;line-height:1.4}
.badge{display:inline-block;background:#eee;padding:2px 8px;border-radius:4px;font-size:11px;color:#666;margin-right:8px}
.grid2{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:10px}
.grid3{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:10px}
.toc{background:#fff;border-radius:10px;padding:20px;margin:20px 0;box-shadow:0 2px 5px rgba(0,0,0,.08)}
.toc a{color:#e94560;text-decoration:none;display:block;padding:4px 0}
.toc a:hover{text-decoration:underline}
.stats{display:flex;gap:15px;flex-wrap:wrap;margin:15px 0}
.stat{background:#e94560;color:#fff;padding:10px 20px;border-radius:8px;font-size:14px}
.foot{text-align:center;color:#999;font-size:12px;margin:40px 0 20px}
@media(max-width:600px){.grid2,.grid3{grid-template-columns:1fr}.container{padding:10px}}
</style>
</head>
<body>
<div class="container">
<h1>${esc(city.name_ru)} (${esc(city.name_tr)})</h1>
<p class="sub">${esc(city.description)}</p>`;

  let tg = city.general_resources.length;
  let tc = Object.values(city.categories).reduce((a,b) => a+b.length, 0);
  h += `<div class="stats"><div class="stat">📋 Общих: ${tg}</div><div class="stat">📌 Специалистов: ${tc}</div><div class="stat">🏷️ Категорий: ${Object.keys(city.categories).length}</div></div>`;

  h += `<div class="toc"><strong>📑 Содержание:</strong><br><a href="#general">📋 Общие ресурсы</a>`;
  for (let [k,v] of Object.entries(city.categories)) {
    if (v.length) h += `<a href="#cat-${k}">${CATEGORY_EMOJI[k]||'📌'} ${CATEGORY_RU[k]||k} (${v.length})</a>`;
  }
  h += `</div>`;

  h += `<h2 class="sec" id="general">📋 Общие ресурсы (${tg})</h2><div class="grid2">`;
  for (let r of city.general_resources) {
    let t = (r.type||'').replace(/_/g,' ').replace(/\b\w/g, c => c.toUpperCase());
    h += `<div class="card"><span class="badge">${t}</span><a href="${esc(r.link)}" target="_blank">${esc(r.name)}</a><div class="d">${esc(r.description)}</div></div>`;
  }
  h += `</div>`;

  for (let [k,entries] of Object.entries(city.categories)) {
    if (!entries.length) continue;
    let ru = CATEGORY_RU[k]||k, em = CATEGORY_EMOJI[k]||'📌';
    h += `<h2 class="sec" id="cat-${k}">${em} ${ru} (${entries.length})</h2><div class="grid3">`;
    for (let e of entries) {
      h += `<div class="card"><a href="${esc(e.link)}" target="_blank">${esc(e.name)}</a><div class="d">${esc(e.description)}</div></div>`;
    }
    h += `</div>`;
  }

  h += `<div class="foot">Сгенерировано из поисковых данных © 2026</div></div></body></html>`;
  return h;
}

function genIndex(data) {
  let h = `<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>Русскоязычные специалисты в Турции</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:#f5f5f5;color:#333}
.container{max-width:1100px;margin:0 auto;padding:20px}
h1{font-size:28px;margin-bottom:5px;color:#1a1a2e}
.sub{font-size:16px;color:#666;margin-bottom:30px}
.cc{background:#fff;border-radius:12px;padding:25px;margin-bottom:20px;box-shadow:0 3px 10px rgba(0,0,0,.1)}
.cc h2{font-size:24px;margin-bottom:5px}
.cc .desc{color:#666;margin-bottom:15px}
.cs{display:flex;gap:10px;flex-wrap:wrap;margin:10px 0}
.cs span{background:#f0f0f0;padding:5px 12px;border-radius:6px;font-size:13px}
.btn{display:inline-block;background:#e94560;color:#fff;padding:10px 25px;border-radius:8px;text-decoration:none;font-weight:600;margin-top:10px}
.btn:hover{background:#d63850}
.cross{background:#fff;border-radius:10px;padding:20px;margin-top:20px}
.cross h3{margin-bottom:10px}
.cross-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:10px}
.ci{padding:8px 0;border-bottom:1px solid #eee}
.ci:last-child{border-bottom:none}
.ci a{color:#e94560;text-decoration:none}
.ci a:hover{text-decoration:underline}
.ci .d{color:#666;font-size:13px}
.foot{text-align:center;color:#999;font-size:12px;margin:40px 0}
</style>
</head>
<body>
<div class="container">
<h1>🇷🇺 Русскоязычные специалисты в Турции</h1>
<p class="sub">Проверенные Telegram-каналы, чаты, сайты и контакты по 3 городам: Анталия, Стамбул, Кемер</p>`;

  let total = 0;
  for (let city of data.cities) {
    total += city.general_resources.length + Object.values(city.categories).reduce((a,b) => a+b.length, 0);
    let cs = Object.values(city.categories).reduce((a,b) => a+b.length, 0);
    h += `<div class="cc"><h2>${city.name_ru} (${city.name_tr})</h2><p class="desc">${city.description}</p><div class="cs"><span>📋 Ресурсов: ${city.general_resources.length}</span><span>📌 Специалистов: ${cs}</span><span>🏷️ Категорий: ${Object.keys(city.categories).length}</span></div><a class="btn" href="${city.name.toLowerCase()}.html">Открыть → ${city.name_ru}</a></div>`;
  }

  h += `<p style="text-align:center;color:#999;margin:20px 0;">Всего записей: <strong>${total}</strong></p>`;

  h += `<div class="cross"><h3>🌍 Ресурсы по всей Турции</h3><div class="cross-grid">`;
  for (let entries of Object.values(data.cross_city_resources)) {
    for (let e of entries) {
      h += `<div class="ci"><a href="${esc(e.link)}" target="_blank">${esc(e.name)}</a><div class="d">${esc(e.description)}</div></div>`;
    }
  }
  h += `</div></div>`;
  h += `<div class="foot">© 2026. Данные из открытых источников. Перед использованием проверяйте актуальность.</div></div></body></html>`;
  return h;
}

// Generate files
let idx = genIndex(data);
fs.writeFileSync('C:/AION/index.html', idx, 'utf8');
console.log('✓ index.html');

for (let city of data.cities) {
  let fn = `C:/AION/${city.name.toLowerCase()}.html`;
  fs.writeFileSync(fn, genCity(city), 'utf8');
  console.log(`✓ ${city.name.toLowerCase()}.html`);
}
console.log('\nDone!');
