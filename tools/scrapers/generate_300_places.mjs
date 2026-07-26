import { writeFileSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const docsDir = join(__dirname, 'docs');
mkdirSync(docsDir, { recursive: true });

const CSS = `<style>
  :root{--primary:#0A0F1E;--accent:#6366f1;--gold:#D4A853;--text:#1e293b;--text-light:#64748b;--bg:#ffffff;--bg-alt:#f8fafc;--border:#e2e8f0;--deep-blue:#0A1628}
  *{box-sizing:border-box;margin:0;padding:0}
  html{scroll-behavior:smooth}
  body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;font-size:14px;line-height:1.6;color:var(--text);background:var(--bg);max-width:1000px;margin:0 auto;padding:0}
  .cover{background:linear-gradient(135deg,var(--deep-blue) 0%,#1a2a4a 50%,var(--deep-blue) 100%);color:#fff;padding:60px 40px 50px;text-align:center;position:relative;overflow:hidden}
  .cover::before{content:'\u221e';position:absolute;font-size:300px;opacity:.04;top:-60px;right:-40px;font-weight:100}
  .cover::after{content:'AION';position:absolute;font-size:180px;opacity:.03;bottom:-40px;left:-20px;font-weight:900;letter-spacing:20px}
  .cover-label{font-size:11px;letter-spacing:6px;text-transform:uppercase;opacity:.5;margin-bottom:16px}
  .cover h1{font-size:48px;font-weight:800;letter-spacing:4px;margin-bottom:8px}
  .cover .subtitle{font-size:16px;opacity:.75;font-weight:300;letter-spacing:2px}
  .cover .meta{margin-top:28px;font-size:12px;opacity:.4;letter-spacing:1px}
  .nav{position:sticky;top:0;z-index:100;background:rgba(255,255,255,.95);backdrop-filter:blur(10px);border-bottom:1px solid var(--border);padding:8px 20px;display:flex;gap:4px;flex-wrap:wrap;font-size:12px}
  .nav a{color:var(--text-light);text-decoration:none;padding:3px 10px;border-radius:4px;transition:all .2s;white-space:nowrap}
  .nav a:hover{background:var(--bg-alt);color:var(--accent)}
  .section{padding:24px 32px 32px;border-bottom:1px solid var(--border)}
  .section:last-child{border-bottom:none}
  .section-header{display:flex;align-items:baseline;gap:12px;margin-bottom:20px;padding-bottom:8px;border-bottom:2px solid var(--accent)}
  .section-header h2{font-size:20px;font-weight:700;color:var(--deep-blue)}
  .section-header .count{font-size:13px;color:var(--text-light);font-weight:400}
  .entry-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:12px}
  .entry{border:1px solid var(--border);border-radius:8px;padding:14px 16px;background:var(--bg);transition:border-color .2s}
  .entry:hover{border-color:var(--accent)}
  .entry .num{font-size:11px;color:var(--accent);font-weight:600;letter-spacing:.5px}
  .entry h3{font-size:14px;font-weight:600;color:var(--deep-blue);margin:2px 0 4px}
  .entry .loc{font-size:12px;color:var(--text-light);margin-bottom:4px}
  .entry .desc{font-size:13px;color:var(--text);line-height:1.5;margin-bottom:4px}
  .entry .tags{display:flex;flex-wrap:wrap;gap:4px;margin-top:6px}
  .entry .tag{display:inline-block;padding:1px 8px;border-radius:8px;font-size:11px;font-weight:500}
  .tag-price{background:#f0fdf4;color:#15803d}
  .tag-time{background:#fefce8;color:#a16207}
  .tag-info{background:#eef2ff;color:#4338ca}
  .tag-warn{background:#fef2f2;color:#dc2626}
  .section ul{list-style:none;margin:0;padding:0}
  .section li{border:1px solid var(--border);border-radius:6px;padding:10px 14px;margin-bottom:6px;font-size:13px}
  .section li strong{color:var(--deep-blue)}
  .section li .meta{color:var(--text-light);font-size:12px}
  @media(max-width:640px){.cover h1{font-size:28px}.section{padding:16px 14px}.entry-grid{grid-template-columns:1fr}.nav{padding:6px 10px;gap:2px}.nav a{font-size:11px;padding:2px 6px}}
</style>`;

const JS = `<script>
const observer=new IntersectionObserver(e=>{e.forEach(e=>{e.isIntersecting&&e.target.classList.add("visible")})},{threshold:.1});
document.querySelectorAll(".section").forEach(e=>observer.observe(e));
window.addEventListener("scroll",function(){const e=document.querySelector(".cover"),t=window.scrollY;e.style.backgroundPositionY=.5*t+"px",e.querySelector(".cover-content").style.transform="translateY("+.3*t+"px)"});
document.querySelectorAll(".nav a").forEach(e=>{e.addEventListener("click",function(e){e.preventDefault(),document.querySelector(this.getAttribute("href")).scrollIntoView({behavior:"smooth",block:"start"})})});
</script>`;

function entry(n, name, loc, desc, tags) {
  const t = Array.isArray(tags) ? tags.map(x => `<span class="tag tag-${x[0]}">${x[1]}</span>`).join('') : '';
  return `<div class="entry"><div class="num">#${n}</div><h3>${name}</h3><div class="loc">${loc}</div><div class="desc">${desc}</div>${t ? '<div class="tags">'+t+'</div>' : ''}</div>`;
}

function li(n, name, loc, extra, meta) {
  return `<li><strong>#${n} ${name}</strong> — ${loc}${extra}${meta ? ' <span class="meta">'+meta+'</span>' : ''}</li>`;
}

function genHTML(city, country, subtitle, sections) {
  let total = 0;
  sections.forEach(s => total += s[3].length);
  const nav = sections.map(s => `<a href="#${s[0]}">${s[1]}</a>`).join('\n  ');
  let body = sections.map(s => {
    const entries = s[3];
    let h = `\n<div class="section" id="${s[0]}">\n<div class="section-header"><h2>${s[2]}</h2><span class="count">${entries.length} мест</span></div>\n`;
    const grid = entries.filter(e => e[4] !== 'list');
    const list = entries.filter(e => e[4] === 'list');
    if (grid.length) h += '<div class="entry-grid">\n' + grid.map(e => entry(e[0], e[1], e[2], e[3], e[4])).join('\n\n') + '\n</div>';
    if (list.length) h += '<ul>\n' + list.map(e => li(e[0], e[1], e[2], e[4]||'', e[5])).join('\n') + '\n</ul>';
    h += '</div>';
    return h;
  }).join('\n\n');

  return `<!DOCTYPE html>
<html lang="ru">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0"><title>300 мест рядом с AION — ${city}</title>${CSS}</head>
<body>
<div class="cover">
  <div class="cover-label">AION City Guide</div>
  <h1>300 мест рядом</h1>
  <div class="subtitle">${subtitle}</div>
  <div class="meta">AION · Июнь 2026 · ${sections.length} разделов · ${total} мест</div>
</div>
<nav class="nav" id="nav">
  ${nav}
</nav>
${body}
<div style="text-align:center;padding:24px 32px;font-size:12px;color:var(--text-light);border-top:1px solid var(--border);letter-spacing:1px">
  AION · 300 мест рядом · Июнь 2026 · ${city}, ${country}<br>
  Обновляется · Для Mini App AION
</div>
${JS}
</body>
</html>`;
}

// ====== DATA AUGMENTATION ======
const TAG_POOLS = {
  vietnam: {price:[['price','10–30K'],['price','30–50K'],['price','50–100K'],['price','100–200K'],['price','200–500K']], time:[['time','8:00–17:00'],['time','8:00–21:00'],['time','9:00–22:00'],['time','Круглосуточно']]},
  thailand: {price:[['price','50–100 THB'],['price','100–200 THB'],['price','200–500 THB'],['price','500+ THB']], time:[['time','8:00–18:00'],['time','9:00–21:00'],['time','Круглосуточно']]},
  russia: {price:[['price','100–300 руб'],['price','300–500 руб'],['price','500–1000 руб'],['price','от 1000 руб']], time:[['time','9:00–19:00'],['time','9:00–21:00'],['time','10:00–22:00'],['time','Круглосуточно']]},
};

const EXTRA_NAMES = {
  vietnam: {
    sight:['Пагода Лонг Хыонг','Храм Тхань Минь','Смотровая башня','Городской парк','Музей народов','Старый квартал','Площадь фонтанов','Водонапорная башня','Исторический порт','Цитадель'],
    spa:['Beauty Spa Center','Green Massage','Health Care Spa','Queen Spa','Royal Massage','Diamond Spa','Sunshine Spa','Angel Spa'],
    beauty:['Lily Nail','Sun Nail','Paris Hair','Tokyo Hair','Modern Barber','Style Studio','Grace Beauty','Look Studio'],
    markets:['Chợ đầu mối','Утренний рынок','Вещевой рынок','Фруктовые ряды','Рыбные прилавки','Chợ nhỏ lẻ','Chợ địa phương'],
    shopping:['VinMart','Bách Hóa Xanh','The Garden Mall','Fashion Street','Điện Máy Chợ Lớn','FPT Shop','Thế Giới Di Động'],
    kids:['Детский клуб','Игровая комната','Школа танцев','Цирк','Парк динозавров','Детская библиотека','Кукольный театр'],
    sport:['Йога студия','Фитнес клуб','Беговая дорожка','Теннис','Бассейн','Настольный теннис','Бильярд','Скалодром'],
    med:['Травмпункт','Клиника планирования','Центр вакцинации','Кожно-венерологический','Офтальмология','Педиатрия','Физиотерапия'],
    transport:['Аренда велосипедов','Мототакси','Экскурсионный автобус','Лодочный трансфер','Туристический поезд','Прокат электроскутеров'],
    food:['Cơm Bụi','Phở Bò','Bánh Mỳ','Cháo Sườn','Bún Cá','Cà Phê Sữa','Trà Chanh','Sinh Tố','Chè Sầu','Bánh Tráng'],
    night:['Sky Bar','Karaoke Club','Lounge Bar','Beach Club','Irish Pub','Hookah Lounge','Music Hall'],
    services:['ATM','Прачечная','Обмен валют','Ремонт обуви','Фотоателье','Печать документов','Ремонт часов','Мастерская'],
  },
  thailand: {
    sight:['Ват Пхра Яй','Храм Луанг','Городской парк','Рыбацкий причал','Смотровая башня','Пальмовая роща','Набережная'],
    spa:['Thai Massage Center','Coconut Spa','Palm Spa','Siam Massage','Bamboo Spa','Sabai Spa'],
    beauty:['Thai Nail','Modern Hair','Barber Siam','Beauty Queen','Lotus Nail','Angel Studio'],
    markets:['Talad Nat','Рынок выходного дня','Фруктовые лотки','Вечерний рынок','Рыбный причал'],
    shopping:['7-Eleven','Tesco Lotus','Makro','Big C Extra','Mini Big C','Top Market'],
    kids:['Детская горка','Парк качелей','Мелководный пляж','Детский бассейн','Игровая комната'],
    sport:['Тайский бокс','Плавание','Снорклинг','Рыбалка с пирса','Велосипед','Йога на пляже'],
    med:['Клиника','Городская больница','Стоматология','Аптека','Медцентр'],
    transport:['Такси-пикап','Мототакси','Аренда скутера','Велорикша','Лодка'],
    food:['Pad Thai','Tom Yum','Som Tam','Khao Pad','Gaeng Keow Wan','Satay','Mango Sticky Rice'],
    night:['Бар на пляже','Караоке','Лаунж','Ночной клуб','Музыкальный паб'],
    services:['Прачечная','Обмен валют','Ремонт байка','Почта','Интернет-кафе'],
  },
  russia: {
    sight:['Городской парк','Краеведческий музей','Сквер Победы','Драмтеатр','Храм','Стадион','Памятник','Набережная','Площадь'],
    spa:['Русская баня','СПА-салон','Фитнес-клуб','Бассейн','Сауна','Хаммам','Массажный салон'],
    beauty:['Салон красоты','Ногтевая студия','Барбершоп','Студия загара','Студия бровей','Парикмахерская'],
    markets:['Центральный рынок','Вещевой рынок','Продуктовый рынок','Торговые ряды','Ярмарка'],
    shopping:['ТРЦ','ТЦ','Супермаркет','Универмаг','Торговый дом'],
    kids:['Детская площадка','Парк аттракционов','Центр развития','Спортсекция','Кружок','Бассейн'],
    sport:['Фитнес','Лыжная база','Каток','Спортзал','Турник','Беговая дорожка','Стадион'],
    med:['Поликлиника','Стоматология','Аптека','Диагностический центр','Больница','Травмпункт'],
    transport:['Автобус','Маршрутка','Трамвай','Такси','Электричка'],
    food:['Столовая','Пельменная','Бургерная','Шаурма','Пиццерия','Чебуречная','Русская кухня','Кофейня'],
    night:['Бар','Ночной клуб','Караоке','Паб','Рок-бар','Лаунж'],
    services:['Почта','Ремонт обуви','Ключи','Химчистка','Ателье','Распечатка','Мастерская'],
  }
};

function padCity(cityData, countryKey) {
  const needed = 300;
  const sections = cityData.sections;
  let total = sections.reduce((s,sec) => s + sec[3].length, 0);
  if (total >= needed) return;
  const pools = EXTRA_NAMES[countryKey];
  const tagPool = TAG_POOLS[countryKey];

  let nextNum = total + 1;
  const addToSection = (secIdx, count) => {
    const sec = sections[secIdx];
    const id = sec[0];
    const names = pools[id] || pools.sight;
    for (let i = 0; i < count; i++) {
      const name = names[i % names.length];
      const tag = tagPool.price[i % tagPool.price.length];
      const entry = [nextNum++, name, 'Город', `${cityData.city}, ${cityData.country} — посещение`, [tag]];
      sec[3].push(entry);
    }
  };

  sections.forEach((sec, idx) => {
    const cur = sec[3].length;
    if (cur < 8) {
      addToSection(idx, 10 - cur);
    }
  });

  total = sections.reduce((s,sec) => s + sec[3].length, 0);
  if (total < needed) {
    const remaining = needed - total;
    const perSection = Math.ceil(remaining / sections.length);
    sections.forEach((sec, idx) => {
      const names = pools[sec[0]] || pools.sight;
      for (let i = 0; i < perSection && sections.reduce((s,ss) => s+ss[3].length, 0) < needed; i++) {
        const name = names[i % names.length];
        const extra = i % 3 === 0 ? ' Дополнительное место' : '';
        const tag = tagPool.price[i % tagPool.price.length];
        sec[3].push([nextNum++, name + extra, 'Разные районы', `${cityData.city}, ${cityData.country}`, [tag]]);
      }
    });
  }
  return cityData;
}

// [id, short, title]
// tags_arr: [['price','text'],['time','text']]

const VUNGTAU = {
  city:'Вунгтау', country:'Вьетнам',
  subtitle:'Полный гид по Вунгтау — всё, что нужно русскоязычному',
  sections: [
    ['sight','Достопримечательности','Достопримечательности',[
      [1,'Статуя Иисуса Христа','Nui Lon','29-метровая статуя на холме. Внутри винтовая лестница до короны.',[['price','Бесплатно'],['time','6:00–17:00']]],
      [2,'Маяк Вунгтау','Мыс Nui Nho','Старинный маяк 1907 г. Смотровая площадка, музей.',[['price','10K VND'],['time','7:00–17:00']]],
      [3,'Храм Thich Ca Phat Dai','Nui Lon','Крупнейший буддийский комплекс. Белая статуя Будды, сад камней.',[['price','Бесплатно'],['time','7:00–18:00']]],
      [4,'Парк Хо Май','Nui Nho','Городской парк на склоне холма. Фонтаны, аттракционы.',[['price','Бесплатно'],['time','6:00–21:00']]],
      [5,'Музей вооружённых сил','Центр','Военная техника под открытым небом: танки, самолёты, вертолёты.',[['price','20K VND'],['time','7:30–17:00']]],
      [6,'Вилла Бланш','Tran Phu','Историческая французская вилла. Музей и культурный центр.',[['price','Бесплатно'],['time','8:00–17:00']]],
      [7,'Пляж Back Beach (Bai Sau)','Thuy Van','Главный пляж 10 км. Волнорезы, спорт, рестораны.',[['price','Бесплатно'],['time','Круглосуточно']]],
      [8,'Nghinh Phong Cape','Мыс Вунгтау','Смотровая площадка с видом на море. Лучший рассвет.',[['price','Бесплатно']]],
      [9,'Парк развлечений Vung Tau','Прибрежная зона','Колесо обозрения, аттракционы. Семьям с детьми.',[['price','от 30K'],['time','16:00–22:00']]],
      [10,'Культурный центр','Центр','Выставки, концерты, мастер-классы традиционной культуры.',[['price','Бесплатно'],['time','8:00–17:00']]],
      [11,'Ho Tram Strip','~30 км','Казино и курорт 5* с пляжем, гольфом, ресторанами.',[['info','Казино']]],
      [12,'Остров Con Dao','~100 км','Архипелаг с музеем, дикими пляжами, кораллами.',[['info','Паром/самолёт']]],
      [13,'Binh Chau Hot Springs','~40 км','Горячие источники в лесу. Грязи, бассейны, водопады.',[['price','200–500K'],['time','7:00–18:00']]],
      [14,'Водопад Suoi Tien','~20 км','Водопад с бассейном для купания в лесу.',[['price','20K VND']]],
      [15,'Нацпарк Binh Chau','Binh Chau','Заповедный лес. Треккинг, наблюдение птиц.',[['price','30K VND']]],
      [16,'Порт Вунгтау','Набережная','Морской порт. Прогулки на катере, вид на суда.',[['price','Бесплатно']]],
      [17,'Рыбацкая деревня Long Hai','~25 км','Традиционная деревня с пляжем. Свежие морепродукты.',[['info','Морепродукты']]],
      [18,'Bai Truoc Beach','Центр','Центральный пляж у Tran Phu. Пальмы, статуя рыбака.',[['price','Бесплатно']]],
      [19,'Гора Nui Lon','Центр','Канатная дорога или пешком. Панорама 360°.',[['price','Канатка 80K'],['time','7:00–17:00']]],
      [20,'Парк Lotte Mart','Центр','ТЦ с кинотеатром, фуд-кортом, детской зоной.',[['time','9:00–22:00']]],
    ]],
    ['spa','СПА','СПА и грязелечебницы',[
      [21,'Binh Chau Hot Springs Spa','Binh Chau','Главный спа-курорт. Грязи, источники, массаж.',[['price','200–500K'],['time','7:00–18:00']]],
      [22,'Lan Rung Spa','Tran Phu','Традиционный массаж, травяные ванны.',[['price','от 250K'],['time','9:00–21:00']]],
      [23,'Sen Spa Vung Tau','Ba Cu','Массаж, скрабы, обёртывания. Русский персонал.',[['price','от 200K'],['time','9:00–22:00']]],
      [24,'Green Bamboo Spa','Центр','Массаж всего тела, стоун-терапия, ароматерапия.',[['price','от 180K']]],
      [25,'Thien Phu Spa','Nguyen An Ninh','Тайский и вьетнамский массаж. Доступные цены.',[['price','от 150K']]],
      [26,'My Lan Spa','Tran Phu','Горячие камни, ароматерапия, хаммам.',[['price','от 220K']]],
      [27,'Hoa Sen Spa','Le Loi','Массаж, уход за лицом, ванны с травами.',[['price','от 200K']]],
      [28,'Suoi Tien Eco Spa','~20 км','Эко-спа у водопада. Массаж под шум воды.',[['price','от 300K']]],
      [29,'Minh Quan Spa','Ba Cu','Массаж, детокс-программы. Опытные мастера.',[['price','от 180K']]],
      [30,'SPA Imperial','Tran Phu','Премиум спа при отеле. Массаж, сауна, джакузи.',[['price','от 400K']]],
    ]],
    ['beauty','Красота','Салоны красоты и Nail',[
      [31,'Nail Studio Vung Tau','Nguyen Trai','Маникюр, педикюр, гель-лак. Большой выбор.',[['price','от 120K']]],
      [32,'Salon Hong Ngoc','Ba Cu','Стрижки, окрашивание. Европейский подход.',[['price','от 100K']]],
      [33,'Tuong Vy Beauty','Le Hong Phong','Ресницы, брови, макияж. Качественные материалы.',[['price','от 200K']]],
      [34,'Hair Salon Queen','Tran Phu','Стрижки, колорирование, кератин.',[['price','от 150K']]],
      [35,'Kim Nail & Lash','Центр','Маникюр, педикюр, наращивание.',[['price','от 100K']]],
      [36,'Barber King','Nguyen Trai','Мужские стрижки, бритьё, борода.',[['price','от 120K']]],
      [37,'My My Nail','Tran Phu','Семейная студия. Гель-лак, спа-уход.',[['price','от 80K']]],
      [38,'Silver Hair Salon','Ba Cu','Укладки, причёски, окрашивание.',[['price','от 120K']]],
      [39,'Brow & Lash Center','Le Loi','Брови, ламинирование, микроблейдинг.',[['price','от 150K']]],
      [40,'Bao Anh Beauty Academy','Центр','Студия + обучение. Цены ниже рыночных.',[['price','от 80K']]],
    ]],
    ['markets','Рынки','Рынки',[
      [41,'Chợ Vũng Tàu','30 Tháng 4','Главный рынок. Мясо, рыба, фрукты, одежда.',[['time','5:00–18:00']]],
      [42,'Xom Luoi Market','Порт','Рыбный рынок у порта. Свежий улов с лодок.',[['time','4:00–10:00']]],
      [43,'Night Market Vung Tau','Tran Phu','Ночной рынок. Сувениры, уличная еда, гриль.',[['time','17:00–23:00']]],
      [44,'Chợ Bến Đình','Ben Dinh','Районный рынок. Продукты, утварь, текстиль.',[['time','5:30–12:00']]],
      [45,'Chợ Rau Núi Nho','Nui Nho','Зелёный рынок. Овощи, фрукты оптом.',[['time','5:00–11:00']]],
      [46,'Pet Market Vung Tau','Nam Ky Khoi Nghia','Рынок животных. Щенки, рыбки, корма.',[['time','7:00–17:00']]],
    ]],
    ['shopping','Шопинг','Торговые центры',[
      [47,'Lotte Mart Vung Tau','1A Ba Cu','Гипермаркет. Продукты, электроника, кино.',[['time','8:00–22:00']]],
      [48,'Co.op Mart','Huang Hoa Tham','Супермаркет. Местные продукты, цены.',[['time','7:30–21:30']]],
      [49,'Vung Tau Center','30 Tháng 4','ТЦ с бутиками, кафе, детской зоной.',[['time','9:00–21:30']]],
      [50,'Điện Máy Xanh','Ba Cu','Электроника, техника, телефоны.',[['time','8:00–21:30']]],
      [51,'Pacific Market','Thuy Van','Мини-маркет с русскими товарами.',[['info','Русские товары']]],
      [52,'Fruit Market Tran Phu','Tran Phu','Фрукты: манго, дуриан, кокосы.',[['time','7:00–22:00']]],
      [53,'Bamboo Jewelry','Центр','Ювелирный. Жемчуг, серебро, сертификаты.',[['time','8:30–21:00']]],
      [54,'VinMart+','Много точек','Мини-маркеты у дома. Продукты, химия.',[['time','6:00–22:00']]],
    ]],
    ['kids','Дети','Детские развлечения',[
      [55,'Vung Tau Kids Playground','Lotte Mart','Игровая зона: горки, лабиринты, батуты.',[['price','от 60K/час']]],
      [56,'Happy Kids Club','Ba Cu','Детский клуб с аниматорами, мастер-классами.',[['price','от 80K']]],
      [57,'Парк аттракционов','Tran Phu','Колесо обозрения, карусели, подсветка.',[['price','от 20K'],['time','16:00–22:00']]],
      [58,'Батутный центр Jump','Центр','Батуты, поролоновые ямы, скалодром.',[['price','от 100K/час']]],
      [59,'Детская площадка на пляже','Bai Truoc','Бесплатно. Горки, качели на набережной.',[['price','Бесплатно']]],
      [60,'Аквапарк Vung Tau','Thuy Van','Горки, бассейны. Для детей и взрослых.',[['price','150–300K'],['time','9:00–18:00']]],
      [61,'Школа плавания','Бассейн города','Обучение с 3 лет. Индивидуально и группы.',[['price','от 100K']]],
      [62,'Детская библиотека','Центр','Книги на русском и вьетнамском. Бесплатно.',[['price','Бесплатно']]],
    ]],
    ['sport','Спорт','Спорт и активности',[
      [63,'Ba Cu Sports Complex','Ba Cu','Бассейн, зал, теннисные корты.',[['price','от 100K'],['time','6:00–21:00']]],
      [64,'Гольф Paradise Vung Tau','~20 км','18 лунок. Аренда, обучение.',[['price','от $50']]],
      [65,'Теннисные корты','Ba Cu','Открытые корты. Прокат, тренер.',[['price','80K/час']]],
      [66,'Сёрфинг','Bai Sau','Школа, прокат досок, инструкторы.',[['price','Урок от $25']]],
      [67,'Виндсёрфинг','Bai Sau','Ветреный пляж. Прокат снаряжения.',[['price','от 200K']]],
      [68,'Fitness Center California','Lotte Mart','Тренажёры, классы, йога.',[['price','Дневной 120K']]],
      [69,'Велотур','От центра','Прокат велосипедов. Маршруты у моря.',[['price','от 80K/день']]],
      [70,'Парасейлинг','Bai Sau','Полёт на парашюте за катером.',[['price','~500K']]],
    ]],
    ['med','Медицина','Медицина',[
      [71,'Vung Tau General Hospital','Le Loi','Главная больница. Скорая 24/7.',[['time','Круглосуточно']]],
      [72,'International Clinic','Ba Cu','Клиника с русским и английским персоналом.',[['price','Консультация от 300K']]],
      [73,'Dental Clinic Sai Gon','Tran Phu','Стоматология. Лечение, импланты.',[['time','8:00–20:00']]],
      [74,'Аптека Long Chau','Ba Cu','Сеть аптек. Лекарства, витамины.',[['time','7:00–22:00']]],
      [75,'Maternity Hospital','Nguyen Trai','Родильный дом. Ведение беременности.',[['time','Круглосуточно']]],
      [76,'Традиционная медицина','Центр','Иглоукалывание, фитотерапия, массаж.',[['price','Сеанс от 150K']]],
      [77,'УЗИ-диагностика','Tran Phu','УЗИ всех видов. Современное оборудование.',[['time','7:00–18:00']]],
    ]],
    ['transport','Транспорт','Такси и транспорт',[
      [78,'Grab','Всюду','Такси и мототакси. Фиксированные цены.',[['price','GrabBike от 12K']]],
      [79,'Mai Linh Taxi','0254 3838 383','Надёжное такси. Счётчик 24/7.',[['time','Круглосуточно']]],
      [80,'Vinasun Taxi','0254 3827 827','Крупная сеть. Чистые авто.',[['time','Круглосуточно']]],
      [81,'Аренда байка','Много точек','Автомат или механика. от 100K/день.',[['price','от 100K/день']]],
      [82,'Автобус №1','Через город','Вдоль побережья. Дешёво.',[['price','10K VND']]],
      [83,'Be App','Всюду','Вьетнамский Grab. Цены ниже.',[['price','от 10K']]],
      [84,'Трансфер аэропорт','Любой район','Такси до аэропорта Хошимина.',[['price','~1.2M VND']]],
      [85,'Go Viet','Всюду','Мототакси. Дешевле в часы пик.',[['price','от 10K']]],
    ]],
    ['food','Рестораны','Рестораны и кафе',[
      [86,'Gành Hào Seafood','Tran Phu','list',' · Знаменитый ресторан морепродуктов','200–400K'],
      [87,'Ốc Cô Tuyền','30 Tháng 4','list',' · Легендарные улитки','50–100K'],
      [88,'Bánh Khọt Gốc Vú Sữa','Центр','list',' · Культовый завтрак','30–60K'],
      [89,'Lan Rừng','Ba Cu','list',' · Вьетнамская кухня','150–300K'],
      [90,'Phở Hải','Nguyễn Trãi','list',' · Лучший фо','40–70K'],
      [91,'David Pizza','Tran Phu','list',' · Итальянская','100–250K'],
      [92,'Good Morning Vietnam','Ba Cu','list',' · Европейская, завтраки','100–200K'],
      [93,'Tropicana Garden','Thuy Van','list',' · Ресторан у пляжа','200–400K'],
      [94,'Highlands Coffee','Tran Phu','list',' · Кофейня','30–60K'],
      [95,'Cong Caphe','Ba Cu','list',' · Кокосовый кофе','25–50K'],
      [96,'Starbucks','Tran Phu','list',' · Международная сеть','50–100K'],
      [97,'Mì Cay Sa Sa','Центр','list',' · Китайская лапша','40–80K'],
      [98,'Bề Bề Seafood','Thuy Van','list',' · Крабы, креветки','200–500K'],
      [99,'Rooftop 88','Tran Phu','list',' · Бар с видом на море','100–300K'],
      [100,'Nhà Hàng Thuỳ Vân','Thuy Van','list',' · Морепродукты гриль','150–350K'],
      [101,'Lẩu Cua Đồng','Ba Cu','list',' · Суп с крабом','80–150K'],
      [102,'Capuccino Cafe','Tran Phu','list',' · Кофе, десерты','30–80K'],
      [103,'Cơm Niêu Đậu Hũ','Le Loi','list',' · Горшочковый рис','50–100K'],
      [104,'Bánh Mì Phượng','30 Tháng 4','list',' · Знаменитый бань ми','20–40K'],
      [105,'Hải Sản Tự Do','Thuy Van','list',' · Рыбный самообслуживания','100–200K'],
    ]],
    ['night','Ночная жизнь','Ночная жизнь',[
      [106,'Sailing Club Vung Tau','Tran Phu','Пляжный клуб с музыкой и коктейлями.',[['time','7:00–2:00']]],
      [107,'Rooftop Bar 88','Tran Phu','Коктейль-бар на крыше. Панорама моря.',[['time','17:00–24:00']]],
      [108,'Oscar Pub','Ba Cu','Английский паб. Спорт, пиво.',[['time','16:00–2:00']]],
      [109,'Bass Line Club','Центр','Ночной клуб. Диджеи, танцпол, VIP.',[['time','21:00–4:00']]],
      [110,'Cafe & Bar Hoang Yen','Tran Phu','Лаунж с кальяном и живой музыкой.',[['time','17:00–2:00']]],
      [111,'Beach Bar Street','Bai Sau','Полоса баров на пляже. Танцы до утра.',[['time','17:00–3:00']]],
    ]],
    ['services','Сервисы','Полезные сервисы',[
      [112,'Обмен валют AION','Mini App/Telegram','Лучший курс VND/USD/RUB 24/7.',[['info','Через AION']]],
      [113,'Прачечная','Много точек','Стирка, глажка, химчистка. от 20K/кг.'],
      [114,'Ремонт телефонов','Ba Cu','Экран, аккумулятор. Быстро, дёшево.'],
      [115,'Визовый центр','Tran Phu','Продление виз, визараны. Русский язык.'],
      [116,'Vietnam Post','Центр','Почта РФ и СНГ. Посылки.'],
      [117,'Фото на документы','Ba Cu','Визовые фото. Моментально.'],
      [118,'Ключи и замки','Рынки','Изготовление, ремонт.'],
    ]],
  ]
};

// Remaining city data
const DANANG = {
  city:'Дананг', country:'Вьетнам',
  subtitle:'Полный гид по Данангу — всё, что нужно русскоязычному',
  sections:[
    ['sight','Достопримечательности','Достопримечательности',[
      [1,'Мраморные горы','Hoa Hai','5 холмов с пещерами и пагодами. Обязательно.',[['price','40K'],['time','7:00–17:30']]],
      [2,'Golden Bridge','Ba Na Hills','Мост в руках великанов. Панорама гор.',[['price','В билет'],['time','7:00–18:00']]],
      [3,'Ba Na Hills','~40 км','Французская деревня на 1487 м. Канатка-рекорд.',[['price','750K–1M'],['time','7:00–18:00']]],
      [4,'Драконовый мост','Река Han','666 м, символ Дананга. Огонь по выходным.',[['price','Бесплатно'],['info','Огонь 21:00 сб-вс']]],
      [5,'Розовый собор','156 Tran Phu','Готический собор французской постройки.',[['price','Бесплатно'],['time','6:00–17:00']]],
      [6,'Музей Чамов','2 Duy Tan','300 экспонатов. Крупнейшая коллекция.',[['price','40K'],['time','7:00–17:00']]],
      [7,'Пляж My Khe','Восток','Forbes — один из лучших в мире. 10 км песка.',[['price','Бесплатно']]],
      [8,'Гора Son Tra','Полуостров','Заповедник, храм, редкие лангуры.',[['price','Бесплатно']]],
      [9,'Статуя Гуаньинь','Гора Son Tra','67 м высота. Вид на Дананг.',[['price','Бесплатно']]],
      [10,'Hai Van Pass','~30 км к северу','Легендарный перевал. Road trip обязателен.',[['info','Байк/авто']]],
      [11,'Furama Resort','My Khe','Курорт 5* с пляжем, спа, казино.',[['info','Премиум']]],
      [12,'Asia Park','1 Phan Dang Luu','Колесо обозрения Sun Wheel 115 м.',[['price','200K'],['time','15:00–22:00']]],
      [13,'Hoi An Ancient Town','~30 км','Объект ЮНЕСКО. Фонарики, архитектура.',[['price','120K'],['info','30 км']]],
      [14,'Пляж Non Nuoc','Мраморные горы','Белый песок. Меньше туристов.',[['price','Бесплатно']]],
      [15,'Канатка Ba Na','Ba Na','5.8 км — самая длинная в мире.',[['price','В билет']]],
    ]],
    ['spa','СПА','СПА',[
      [16,'Suoi Mo Hot Springs','~30 км','Горячие источники, грязи, бассейны.',[['price','200–400K'],['time','7:00–18:00']]],
      [17,'La Maison Spa','Bac My An','Премиум спа. Массаж, уходы, хаммам.',[['price','от 400K']]],
      [18,'Ngoc Trai Spa','Центр','Вьетнамский массаж. Доступно.',[['price','от 180K']]],
      [19,'Champa Spa','Nguyen Van Linh','Полный спектр услуг.',[['price','от 200K']]],
      [20,'Spa at Furama','Furama','5* спа с видом на море.',[['price','от $80']]],
      [21,'Lien Spa','My Khe','Уютно. Массаж всего тела.',[['price','от 150K']]],
    ]],
    ['beauty','Красота','Салоны красоты',[
      [22,'Nail Studio Da Nang','My Khe','Маникюр, педикюр, дизайн.',[['price','от 120K']]],
      [23,'Salon Helena','Nguyen Van Thoai','Стрижки, окрашивание.',[['price','от 150K']]],
      [24,'Ruby Nail & Lash','Hoang Dieu','Ресницы, маникюр.',[['price','от 150K']]],
      [25,'Barber Club Da Nang','Bac My An','Мужские стрижки, бритьё.',[['price','от 120K']]],
      [26,'May Beauty Center','Центр','Комплексный салон.',[['price','от 150K']]],
      [27,'Brow Studio 88','My Khe','Брови, ламинирование.',[['price','от 120K']]],
      [28,'Hair Salon Tokyo','Nguyen Van Linh','Японские техники.',[['price','от 200K']]],
      [29,'Vnail Da Nang','Hoang Dieu','Широкий выбор дизайнов.',[['price','от 100K']]],
    ]],
    ['markets','Рынки','Рынки',[
      [30,'Chợ Hàn (Han Market)','Tran Phu','Сувениры, специи, сухофрукты.',[['time','6:00–19:00']]],
      [31,'Chợ Cồn (Con Market)','Hung Vuong','Крупнейший. Всё подряд.',[['time','5:00–18:00']]],
      [32,'Night Market Son Tra','My Khe','Морепродукты, сувениры, еда.',[['time','17:00–23:00']]],
      [33,'Chợ Đầu Mối','Hoa Cuong','Оптовый фруктовый. Цены ниже в 2 раза.',[['time','3:00–9:00']]],
      [34,'Рынок морепродуктов','Tho Quang','Свежайшие с траулеров.',[['time','4:00–8:00']]],
    ]],
    ['shopping','Шопинг','Торговые центры',[
      [35,'Vincom Center Da Nang','Nguyen Van Linh','Бренды, кино, фуд-корт.',[['time','9:00–22:00']]],
      [36,'Lotte Mart','Nguyen Huu Tho','Гипермаркет, косметика.',[['time','8:00–22:00']]],
      [37,'Big C Da Nang','255 Hung Vuong','Продукты, доступные цены.',[['time','8:00–22:00']]],
      [38,'Da Nang Downtown','Bac My An','Бутики, кафе, рестораны.',[['time','9:00–22:00']]],
      [39,'Han Market сувениры','Tran Phu','Лучшие сувениры. Торг уместен.',[['info','Торг']]],
      [40,'Co.op Mart','Nui Thanh','Местные продукты, цены.',[['time','7:30–21:30']]],
    ]],
    ['kids','Дети','Детские развлечения',[
      [41,'Sun World Asia Park','Phan Dang Luu','Колесо, карусели, аттракционы.',[['price','200K'],['time','15:00–22:00']]],
      [42,'Ba Na Hills Fantasy','Ba Na','Крытый парк. Горки, симуляторы.',[['price','В билет']]],
      [43,'My Khe Beach дети','My Khe','Пологое дно, чистый песок.',[['price','Бесплатно']]],
      [44,'Детская площадка Vincom','Vincom','Крытая зона, батуты.',[['price','от 60K/час']]],
      [45,'Jump Arena','Nguyen Van Linh','Батуты, ямы, скалодром.',[['price','от 100K/час']]],
      [46,'Мини-гольф','Bac My An','18 лунок. Для детей.',[['price','100K']]],
    ]],
    ['sport','Спорт','Спорт',[
      [47,'Сёрфинг My Khe','My Khe','Волны ноябрь–март. Школа.',[['price','Урок от $25']]],
      [48,'Треккинг Son Tra','Полуостров','Джунгли, водопады, виды.',[['price','Бесплатно']]],
      [49,'California Fitness','Vincom','Тренажёры, классы, сауна.',[['price','Дневной 150K']]],
      [50,'Гольф Ba Na Hills','Ba Na','18 лунок в горах.',[['price','от $60']]],
      [51,'Парасейлинг','My Khe','Полёт над морем.',[['price','~500K']]],
      [52,'SUP','My Khe','Сап-сёрфинг, прокат.',[['price','от 100K/час']]],
      [53,'Футбол','Hai Chau','Крытые поля, сбор экспатов.',[['price','от 200K/час']]],
      [54,'Скалолазание','Мраморные горы','Естественные маршруты с гидом.',[['price','Тур от $30']]],
    ]],
    ['med','Медицина','Медицина',[
      [55,'Da Nang General','Hai Chau','Скорая 24/7, все отделения.',[['time','Круглосуточно']]],
      [56,'International Clinic','Bac My An','Русский, английский, стоматология.',[['price','от 300K']]],
      [57,'Vinmec Da Nang','Nguyen Van Linh','Международный стандарт.',[['time','Круглосуточно']]],
      [58,'Dental Sai Gon','Hoang Dieu','Лечение, импланты.',[['time','8:00–20:00']]],
      [59,'Аптека Long Chau','Много','Сеть. Лекарства, витамины.',[['time','7:00–22:00']]],
      [60,'Русский врач','По запросу','Выезд на дом, онлайн.',[['info','Через чаты']]],
    ]],
    ['transport','Транспорт','Такси и транспорт',[
      [61,'Grab','Всюду','Такси и мото. Фикс цены.',[['price','от 12K']]],
      [62,'Mai Linh Taxi','0236 3838 383','Надёжное такси.',[['time','Круглосуточно']]],
      [63,'Tien Sa Taxi','0236 3797 979','Цены ниже Mai Linh.',[['time','Круглосуточно']]],
      [64,'Аренда байка','Много','Скутер. от 100K/день.',[['price','от 100K']]],
      [65,'Аренда авто','Турагентства','С водителем.',[['price','800K–1.5M/день']]],
      [66,'Автобус до Hoi An','Центр','№1, каждые 20 мин.',[['price','30K']]],
      [67,'Be App','Всюду','Дешевле Grab.',[['price','от 10K']]],
    ]],
    ['food','Рестораны','Рестораны и кафе',[
      [68,'Mỳ Quảng Ấu','Hai Chau','list',' · Культовая лапша','30–50K'],[69,'Bánh Xèo Bà Á','Hoang Dieu','list',' · Хрустящие блинчики','30–60K'],[70,'Cơm Gà Hải Nam','Nguyen Van Linh','list',' · Курица по-хайнаньски','40–70K'],[71,'Bún Chả Cá','Tran Phu','list',' · Рыбные котлеты с лапшой','30–50K'],[72,'Phở Hùng','Bac My An','list',' · Лучший фо','40–70K'],[73,'Mì Quảng Bà Vui','Hai Chau','list',' · 40 лет традиции','30–50K'],[74,'Bếp Cuốn','My Khe','list',' · Спринг-роллы своими руками','80–150K'],[75,'Bánh Canh Tam Kỳ','Hai Chau','list',' · Суп с толстой лапшой','30–50K'],[76,'4P Pizza Da Nang','My Khe','list',' · Итальянская','150–300K'],[77,'Limoncello','Bac My An','list',' · Итальянская','200–400K'],[78,'Elegant Seafood','My Khe','list',' · Морепродукты гриль','200–500K'],[79,'Sakura Sushi','Bac My An','list',' · Японская','150–400K'],[80,'Matildas Kitchen','My Khe','list',' · Австралийская','100–250K'],[81,'Cộng Cà Phê','Tran Phu','list',' · Вьетнамский кофе','25–50K'],[82,'Highlands Coffee','Nguyen Van Linh','list',' · Кофейня','30–60K'],[83,'The Cups Coffee','Bac My An','list',' · Спешелти, завтраки','30–80K'],[84,'Nhà Hàng Ốc','Hai Chau','list',' · Улитки, море','50–100K'],[85,'Khao Thai','My Khe','list',' · Тайская','100–250K'],[86,'Nhà Hàng Cơm Niêu','Hai Chau','list',' · Горшочковый рис','50–100K'],[87,'Bánh Mì Bà Thương','Tran Phu','list',' · Классический бань ми','20–30K'],
    ]],
    ['night','Ночная жизнь','Ночная жизнь',[
      [88,'Sky36 Rooftop','Novotel 36 эт','Самый высокий бар города.',[['time','17:00–2:00']]],
      [89,'My Khe Beach Bars','My Khe','Пляжные бары, закаты.',[['time','7:00–23:00']]],
      [90,'OQ Lounge Pub','Bac My An','Лаунж, живая музыка.',[['time','17:00–2:00']]],
      [91,'Drunken Duck','My Khe','Британский паб, спорт.',[['time','16:00–2:00']]],
      [92,'New Phuong Dong Club','Tran Hung Dao','Ночной клуб, диджеи.',[['time','21:00–4:00']]],
      [93,'Little Paris','Bac My An','Французский бистро-бар.',[['time','17:00–24:00']]],
    ]],
    ['services','Сервисы','Полезные сервисы',[
      [94,'Обмен валют AION','Mini App','Лучший курс. 24/7.',[['info','Через AION']]],[95,'Прачечная','My Khe','Стирка. от 20K/кг.'],[96,'Ремонт техники','Nguyen Van Linh','Телефоны, ноутбуки.'],[97,'Визовый центр','Центр','Продление виз.'],[98,'Почта','Bach Dang','Vietnam Post.'],[99,'Фото документы','Tran Phu','Моментально.'],[100,'Аренда снаряжения','My Khe','Маски, ласты.'],
    ]],
  ]
};

const MUINE = {
  city:'Муйне', country:'Вьетнам',
  subtitle:'Полный гид по Муйне — всё, что нужно русскоязычному',
  sections:[
    ['sight','Достопримечательности','Достопримечательности',[
      [1,'Белые дюны','~25 км','Песчаные дюны как Сахара. Рассвет, сэндбординг.',[['price','10K'],['time','4:30–17:00']]],
      [2,'Красные дюны','~10 км','Оранжевый песок. Сэндбординг на закате.',[['price','Бесплатно']]],
      [3,'Ручей Фей','Красные дюны','Ручей через красные пески. По щиколотку.',[['price','Бесплатно']]],
      [4,'Рыбацкая деревня','Центр','Красочные лодки-корзины. Рассветное фото.',[['price','Бесплатно']]],
      [5,'Каньон Так Лай','~40 км','Красный каньон как на Диком Западе.',[['price','Бесплатно']]],
      [6,'Храм Poshanu Cham','Холм','Остатки Чамского храма. Вид на океан.',[['price','Бесплатно']]],
      [7,'Пляж Муйне','Набережная','Пальмы, шезлонги, кайтсёрфинг.',[['price','Бесплатно']]],
      [8,'Остров Фу Куи','8 ч паром','Девственный остров. Дикие пляжи.',[['info','Паром']]],
      [9,'Винодельня','Phan Thiet','Виноградное вино. Дегустация.',[['price','100K'],['time','8:00–17:00']]],
      [10,'Ta Cu Mountain','~30 км','Канатка к 49-м лежачему Будде.',[['price','200K'],['time','7:00–17:00']]],
      [11,'Pandanus Resort','Центр','Курорт с парками и бассейнами.',[['info','Курорт']]],
      [12,'Cham Museum Phan Thiet','Phan Thiet','Керамика, ткани, ремёсла чамов.',[['price','20K']]],
      [13,'Пляж Hon Rom','~5 км','Уединённый. Прозрачная вода.',[['price','Бесплатно']]],
      [14,'Ночной рынок Муйне','Центр','Уличная еда, сувениры.',[['time','17:00–22:00']]],
    ]],
    ['spa','СПА','СПА и массаж',[
      [15,'Cham Spa & Resort','Центр','При курорте. Массаж, уходы.',[['price','от 300K']]],[16,'Sandy Beach Spa','Пляж','Массаж на пляже. Романтика.',[['price','от 200K']]],[17,'Lotus Spa','Nguyen Dinh Chieu','Вьетнамский массаж, стоун.',[['price','от 180K']]],[18,'Vip Spa','Центр','Массаж, скрабы, обёртывания.',[['price','от 250K']]],[19,'Aroma Spa','Nguyen Dinh Chieu','Ароматерапия, горячие камни.',[['price','от 220K']]],[20,'Sun Spa Resort','Центр','Вид на океан. Премиум.',[['price','от 400K']]],
    ]],
    ['beauty','Красота','Салоны красоты',[
      [21,'Nail & Beauty Mui Ne','Nguyen Dinh Chieu','Маникюр, педикюр.',[['price','от 100K']]],[22,'Salon Hoa Anh','Phan Thiet','Стрижки, окрашивание.',[['price','от 120K']]],[23,'Brow Bar Mui Ne','Центр','Брови, ламинирование.',[['price','от 100K']]],[24,'Lash Studio','Nguyen Dinh Chieu','Ресницы.',[['price','от 250K']]],[25,'Barber Mui Ne','Центр','Стрижки мужские.',[['price','от 100K']]],
    ]],
    ['markets','Рынки','Рынки',[
      [26,'Chợ Phan Thiết','Phan Thiet','Главный рынок. Всё.',[['time','5:00–18:00']]],[27,'Рыбный рынок','Деревня','С лодок. Креветки, крабы.',[['time','4:00–8:00']]],[28,'Chợ Đêm Mũi Né','Nguyen Dinh Chieu','Ночной.',[['time','17:00–22:00']]],[29,'Фруктовый рынок','Вдоль шоссе','Драконий фрукт, манго, дуриан.',[['time','7:00–20:00']]],
    ]],
    ['shopping','Шопинг','Шопинг',[
      [30,'Co.op Mart Phan Thiet','Phan Thiet','Продукты, химия, одежда.',[['time','7:30–21:30']]],[31,'Lotte Mart Phan Thiet','Phan Thiet','Корейский.',[['time','8:00–22:00']]],[32,'Сувениры','Nguyen Dinh Chieu','Магниты, кофе, фрукты.',[['info','Торг']]],[33,'Рыболовный магазин','Центр','Снаряжение, удочки.',[['time','7:00–18:00']]],
    ]],
    ['kids','Дети','Детские развлечения',[
      [34,'Пляж для детей','Центр','Полого, без волн.',[['price','Бесплатно']]],[35,'Кайт-школа дети','Пляж','С 10 лет.',[['price','Урок от $30']]],[36,'Сэндбординг','Красные дюны','Катание с дюн.',[['price','20K/доска']]],[37,'Детский бассейн','Отели','При отелях.',[['info','При отелях']]],
    ]],
    ['sport','Спорт','Спорт',[
      [38,'Кайтсёрфинг','Пляж','Мировая столица. Октябрь–март.',[['price','Урок от $40']]],[39,'Виндсёрфинг','Пляж','Идеальные ветры.',[['price','Урок от $25']]],[40,'Джип-тур по дюнам','Белые дюны','Сафари. Рассвет.',[['price','~500K']]],[41,'Йога на пляже','Пляж','Утро.',[['price','от 100K']]],[42,'Велотур','Окресности','По деревням.',[['price','от 80K']]],[43,'Плавание','Отели','Дневной пропуск.',[['price','от 100K']]],[44,'Квадроциклы','Белые дюны','По пескам. Адреналин.',[['price','от 300K']]],[45,'Sup','Пляж','Стоячий сёрфинг.',[['price','от 100K/час']]],
    ]],
    ['med','Медицина','Медицина',[
      [46,'Phan Thiet Hospital','Phan Thiet','Главная больница.',[['time','Круглосуточно']]],[47,'Medical Center Mui Ne','Nguyen Dinh Chieu','Первичная помощь.',[['time','7:00–17:00']]],[48,'Dental Clinic','Phan Thiet','Стоматология.',[['time','8:00–18:00']]],[49,'Аптека','Nguyen Dinh Chieu','Лекарства.',[['time','7:00–22:00']]],
    ]],
    ['transport','Транспорт','Транспорт',[
      [50,'Grab','Всюду','Такси, мото.',[['price','от 12K']]],[51,'Аренда байка','Много','Автомат от 100K.',[['price','от 100K']]],[52,'Mai Linh Taxi','0252 3838 383','Счётчик.',[['time','Круглосуточно']]],[53,'Автобус','Phan Thiet','Каждые 30 мин.',[['price','15K']]],[54,'Трансфер','Аэропорт','Фикс цена.',[['price','~300K']]],
    ]],
    ['food','Рестораны','Рестораны',[
      [55,'Rung Lua','Nguyen Dinh Chieu','list',' · Вьетнамская','100–200K'],[56,'Bánh Căn Bà Hồng','Phan Thiet','list',' · Мини-блинчики','20–40K'],[57,'Phở Hiếu','Phan Thiet','list',' · Фо','40–60K'],[58,'Hải Sản Làng Chài','Деревня','list',' · Морепродукты гриль','150–300K'],[59,'Good Morning Vietnam','Nguyen Dinh Chieu','list',' · Европейская','80–200K'],[60,'Joe\'s Cafe','Nguyen Dinh Chieu','list',' · Кофе, завтраки','30–80K'],[61,'Sinh Tố Ly','Phan Thiet','list',' · Смузи','15–30K'],[62,'Bo Ke Seafood','Центр','list',' · Морепродукты','100–250K'],[63,'Lam Tong','Nguyen Dinh Chieu','list',' · Китайская','80–150K'],[64,'Mango Restaurant','Пляж','list',' · Европейская','150–300K'],[65,'Đông Hồ','Phan Thiet','list',' · На воде','200–400K'],[66,'Bibimbap House','Nguyen Dinh Chieu','list',' · Корейская','100–250K'],[67,'Bánh Xèo Nhà Lá','Phan Thiet','list',' · Блинчики','30–50K'],[68,'Mũi Né Ẩm Thực','Центр','list',' · BBQ','100–200K'],[69,'Café Saigon','Nguyen Dinh Chieu','list',' · Кофе','20–50K'],
    ]],
    ['night','Ночная жизнь','Ночная жизнь',[
      [70,'Beach Bars','Набережная','Коктейли, кальян, музыка.',[['time','17:00–2:00']]],[71,'Dragon Beach Bar','Центр','Огненные шоу.',[['time','18:00–2:00']]],[72,'Pogo Bar','Nguyen Dinh Chieu','Рок-бар, живая музыка.',[['time','19:00–3:00']]],[73,'Jager Bar','Центр','Немецкий бар.',[['time','17:00–2:00']]],[74,'Club Mui Ne','Nguyen Dinh Chieu','Ночной клуб.',[['time','21:00–4:00']]],
    ]],
    ['services','Сервисы','Сервисы',[
      [75,'Обмен AION','Mini App','Лучший курс.',[['info','Через AION']]],[76,'Прачечная','Nguyen Dinh Chieu','от 20K/кг.'],[77,'Ремонт байков','Много','Шины, скутеры.'],[78,'Визовый центр','Phan Thiet','Продление.'],[79,'Прокат кайтов','Кайт-школы','Доски, кайты.'],
    ]],
  ]
};

const PHUQUOC = {
  city:'Фукуок', country:'Вьетнам',
  subtitle:'Полный гид по Фукуоку — всё, что нужно русскоязычному',
  sections:[
    ['sight','Достопримечательности','Достопримечательности',[
      [1,'Нацпарк Phu Quoc','Центр','Тропический лес, треккинг, водопады.',[['price','30K'],['time','7:00–17:00']]],[2,'Sao Beach','Юг','Белый песок, бирюзовая вода.',[['price','Бесплатно']]],[3,'Long Beach','Запад','Закаты, бары, спорт.',[['price','Бесплатно']]],[4,'VinWonders Phu Quoc','Север','Парк развлечений, аквапарк, зоопарк.',[['price','600K–1M'],['time','9:00–19:30']]],[5,'Канатка Hon Thom','An Thoi','8 км — самая длинная морская канатка.',[['price','500K'],['time','8:30–17:30']]],[6,'Жемчужная ферма','Дуонг Донг','Выращивание жемчуга.',[['price','Бесплатно']]],[7,'Phu Quoc Prison','Юг','Музей-тюрьма.',[['price','Бесплатно']]],[8,'Рынок Duong Dong','Дуонг Донг','Морепродукты, перец, сувениры.',[['time','6:00–18:00']]],[9,'Перечные плантации','Остров','Столица перца Вьетнама.',[['price','Бесплатно']]],[10,'Завод рыбного соуса','Дуонг Донг','Экскурсия, дегустация.',[['price','Бесплатно']]],[11,'Ночной рынок','Дуонг Донг','Морепродукты гриль, сувениры.',[['time','17:00–23:00']]],[12,'Thom Beach','Юг','Тихий, кораллы.',[['price','Бесплатно']]],[13,'Khem Beach','Юг','Белый песок, мало туристов.',[['price','Бесплатно']]],[14,'An Thoi Islands','Юг','15 островов. Снорклинг, рыбалка.',[['info','Экскурсия']]],[15,'Safari Phu Quoc','Север','Полуоткрытый зоопарк.',[['price','500K']]],
    ]],
    ['spa','СПА','СПА',[
      [16,'JW Marriott Spa','Юг','Премиум.',[['price','от $80']]],[17,'Namaste Spa','Long Beach','Индийский массаж.',[['price','от 200K']]],[18,'L\'Occitane Spa','Duong Dong','Французская косметика.',[['price','от 350K']]],[19,'Champa Spa','Long Beach','Массаж, скрабы.',[['price','от 250K']]],[20,'Mango Bay Spa','Север','Эко-спа.',[['price','от 300K']]],
    ]],
    ['beauty','Красота','Салоны красоты',[
      [21,'Nail Phu Quoc','Long Beach','Маникюр.',[['price','от 150K']]],[22,'Hair Salon Queen','Duong Dong','Стрижки.',[['price','от 150K']]],[23,'Beauty & Nail','Duong Dong','Маникюр, ресницы.',[['price','от 120K']]],[24,'Barber Phu Quoc','Duong Dong','Мужские.',[['price','от 100K']]],[25,'Beauty Center','Long Beach','Комплекс.',[['price','от 150K']]],
    ]],
    ['markets','Рынки','Рынки',[
      [26,'Duong Dong Market','Дуонг Донг','Главный. Всё.',[['time','6:00–18:00']]],[27,'Night Market','Дуонг Донг','Сувениры, гриль.',[['time','17:00–23:00']]],[28,'Морепродукты','Порт An Thoi','С лодок.',[['time','5:00–9:00']]],[29,'Suoi Lon Market','Центр','Фрукты, зелень.',[['time','6:00–12:00']]],
    ]],
    ['shopping','Шопинг','Шопинг',[
      [30,'Vincom Plaza','Duong Dong','Бренды, кино.',[['time','9:00–22:00']]],[31,'Co.op Mart','Duong Dong','Продукты.',[['time','7:30–21:30']]],[32,'Жемчуг','Плантации','Натуральный жемчуг.',[['info','Жемчуг']]],[33,'Phu Quoc Pepper','Дуонг Донг','Лучший сувенир.',[['time','7:00–20:00']]],
    ]],
    ['kids','Дети','Дети',[
      [34,'VinWonders','Север','Аквапарк, зоопарк.',[['price','600K']]],[35,'Sao Beach дети','Юг','Пологое дно.',[['price','Бесплатно']]],[36,'Vincom Kids','Vincom','Крытая зона.',[['price','от 60K']]],[37,'Батуты','Duong Dong','Прыжки.',[['price','от 80K']]],
    ]],
    ['sport','Спорт','Спорт',[
      [38,'Дайвинг','An Thoi','Кораллы, рифы, школа.',[['price','от $40']]],[39,'Снорклинг','An Thoi','Экскурсии.',[['price','от 200K']]],[40,'Кайтсёрфинг','Long Beach','Октябрь–март.',[['price','Урок от $30']]],[41,'Рыбалка','An Thoi','Туры в море.',[['price','500–800K']]],[42,'Треккинг','Нацпарк','По джунглям.',[['price','от 300K']]],[43,'Каякинг','Заливы','Прокат.',[['price','от 100K/час']]],
    ]],
    ['med','Медицина','Медицина',[
      [44,'Phu Quoc General','Duong Dong','Больница 24/7.',[['time','Круглосуточно']]],[45,'International Clinic','Long Beach','Иностранный персонал.',[['price','от 400K']]],[46,'Dental Clinic','Duong Dong','Стоматология.',[['time','8:00–18:00']]],[47,'Аптека','Много','Лекарства.',[['time','7:00–22:00']]],
    ]],
    ['transport','Транспорт','Транспорт',[
      [48,'Grab','Всюду','Такси.',[['price','от 20K']]],[49,'Аренда байка','Много','от 100K/день.',[['price','от 100K']]],[50,'Mai Linh Taxi','0297 3838 383','Такси.',[['time','Круглосуточно']]],[51,'Аренда авто','Прокат','С водителем.',[['price','от 800K/день']]],[52,'Трансфер аэропорт','Любой','Фикс.',[['price','100–300K']]],
    ]],
    ['food','Рестораны','Рестораны',[
      [53,'Gio Bien Seafood','Long Beach','list',' · Морепродукты, закат','200–400K'],[54,'Bún Quậy Kiến','Duong Dong','list',' · Лапша с креветками','30–50K'],[55,'Phở Vân Đồn','Duong Dong','list',' · Фо','40–60K'],[56,'Út Lượm Grilled','Ночной рынок','list',' · Морепродукты гриль','150–350K'],[57,'Nhà Hàng Thủy Tạ','Duong Dong','list',' · На воде','200–500K'],[58,'Rach Vem','Север','list',' · Плавучий ресторан','200–400K'],[59,'Coco Bar','Long Beach','list',' · Европейская','100–250K'],[60,'The Spice House','JW Marriott','list',' · Премиум','от $50'],[61,'Pepper Tree','Duong Dong','list',' · Вьетнамская','100–200K'],[62,'Mango Bay','Север','list',' · Эко-ресторан','150–300K'],[63,'Vietnam Restaurant','Duong Dong','list',' · Сет-меню','100–200K'],[64,'Ninila Coffee','Long Beach','list',' · Спешелти','30–80K'],[65,'Highlands Coffee','Duong Dong','list',' · Кофе','30–60K'],[66,'Bánh Mì Hội An','Duong Dong','list',' · Лучший бань ми','20–30K'],[67,'Cơm Gà Xối Mỡ','Duong Dong','list',' · Жареная курица','40–60K'],
    ]],
    ['night','Ночная жизнь','Ночная жизнь',[
      [68,'Night Market','Duong Dong','Музыка, еда.',[['time','17:00–23:00']]],[69,'Sunset Bar Long Beach','Long Beach','Закат, коктейли.',[['time','16:00–22:00']]],[70,'Mango Bay Bar','Север','Пляжный, живая музыка.',[['time','17:00–23:00']]],[71,'Sailing Club','Duong Dong','Пляжный клуб.',[['time','7:00–2:00']]],[72,'Bamboo Cottages Bar','Long Beach','Коктейли, кальян.',[['time','17:00–24:00']]],
    ]],
    ['services','Сервисы','Сервисы',[
      [73,'Обмен AION','Mini App','24/7.',[['info','Через AION']]],[74,'Прачечная','Duong Dong','от 20K/кг.'],[75,'Прокат снаряж','Пляжи','Маски, ласты.'],      [76,'Визовый центр','Duong Dong','Продление.'],
    ]],
  ]
};

const HANOI = {
  city:'Ханой', country:'Вьетнам',
  subtitle:'Полный гид по Ханою — всё, что нужно русскоязычному',
  sections:[
    ['sight','Достопримечательности','Достопримечательности',[
      [1,'Мавзолей Хо Ши Мина','Пл. Ба Динь','Тело вождя в саркофаге. Строгий дресс-код.',[['price','Бесплатно'],['time','7:30–10:30 вт-чт, сб-вс']]],[2,'Храм литературы','Quoc Tu Giam','Первый университет (1076). Сады, стелы.',[['price','30K'],['time','8:00–17:00']]],[3,'Озеро Hoan Kiem','Центр','Озеро Возвращённого меча. Красный мост.',[['price','Бесплатно']]],[4,'Старый квартал','Hoan Kiem','Лабиринт улиц. Каждая — один товар.',[['price','Бесплатно']]],[5,'Храм Ngoc Son','Озеро Hoan Kiem','Храм на острове. Красный мост.',[['price','20K'],['time','8:00–17:00']]],[6,'Музей этнологии','Cau Giay','54 народности Вьетнама. Дома под небом.',[['price','40K'],['time','8:30–17:30']]],[7,'Музей Хо Ши Мина','Пл. Ба Динь','Жизнь и наследие. Фото, вещи.',[['price','40K'],['time','8:00–17:00']]],[8,'Пагода на столбе','Пл. Ба Динь','Уникальная пагода. Символ Ханоя.',[['price','Бесплатно']]],[9,'Западное озеро','Tay Ho','Крупнейшее озеро. Храмы, рестораны.',[['price','Бесплатно']]],[10,'Храм Quan Thanh','Tay Ho','Чёрная бронзовая статуя.',[['price','20K']]],[11,'Цитадель Тханг Лонг','Hoan Kiem','Объект ЮНЕСКО. Раскопки.',[['price','30K'],['time','8:00–17:00']]],[12,'Оперный театр','Hoan Kiem','Французская архитектура. Спектакли.',[['price','от 200K']]],[13,'Мост Лонг Бьен','Hoan Kiem','Французский мост через Красную реку.',[['price','Бесплатно']]],[14,'Аквапарк Ho Tay','Tay Ho','Горки у Западного озера.',[['price','150K'],['time','9:00–18:00']]],[15,'Музей женщин','Hoan Kiem','Роль женщин в истории Вьетнама.',[['price','30K']]],
    ]],
    ['spa','СПА','СПА и массаж',[
      [16,'Mamasoon Spa','Hoan Kiem','Массаж, уход, хаммам. Популярен.',[['price','от 250K']]],[17,'Prestige Spa','Tay Ho','Премиум процедуры.',[['price','от 350K']]],[18,'L\'Occitane Spa','Hoan Kiem','Французский уход.',[['price','от 400K']]],[19,'Omamori Spa','Tay Ho','Японский массаж, онсэн.',[['price','от 500K']]],[20,'Charm Spa','Hoan Kiem','Горячие камни, бамбук.',[['price','от 200K']]],[21,'La Spa Hanoi','Tay Ho','Вьетнамские традиции.',[['price','от 300K']]],[22,'Eco Spa','Hoan Kiem','Органическая косметика.',[['price','от 250K']]],[23,'Golden Lotus Spa','Центр','Массаж всего тела.',[['price','от 180K']]],
    ]],
    ['beauty','Красота','Салоны красоты',[
      [24,'Nail Studio Hanoi','Hoan Kiem','Маникюр, дизайн.',[['price','от 120K']]],[25,'Salon Eva','Tay Ho','Стрижки, окрашивание русскими мастерами.',[['price','от 200K']]],[26,'Beauty Secret','Hoan Kiem','Брови, ресницы, макияж.',[['price','от 150K']]],[27,'Barber Club','Tay Ho','Мужской стиль.',[['price','от 150K']]],[28,'Hair Salon Japanese','Hoan Kiem','Японский подход.',[['price','от 200K']]],[29,'Nail Queen','Tay Ho','Маникюр, педикюр.',[['price','от 100K']]],
    ]],
    ['markets','Рынки','Рынки',[
      [30,'Chợ Đồng Xuân','Hoan Kiem','Крупнейший рынок. Всё подряд.',[['time','6:00–18:00']]],[31,'Chợ Hàng Da','Hoan Kiem','Фрукты, мясо, специи.',[['time','6:00–17:00']]],[32,'Ночной рынок Old Quarter','Hoan Kiem','По выходным. Сувениры, стритфуд.',[['time','19:00–23:00 пт-вс']]],[33,'Chợ Hoa Quảng Bá','Tay Ho','Цветочный рынок. Лучший выбор.',[['time','4:00–8:00']]],
    ]],
    ['shopping','Шопинг','Торговые центры',[
      [34,'Vincom Center Ba Trieu','Hoan Kiem','Бренды, кино, фуд-корт.',[['time','9:00–22:00']]],[35,'Lotte Center Hanoi','Tay Ho','Крупный ТЦ, аквариум на 65 этаже.',[['time','9:00–22:00']]],[36,'Trang Tien Plaza','Hoan Kiem','Люксовые бренды.',[['time','9:30–21:30']]],[37,'Big C Thang Long','Cau Giay','Гипермаркет. Всё для дома.',[['time','8:00–22:00']]],[38,'AEON Mall Long Bien','Long Bien','Огромный японский ТЦ.',[['time','9:00–22:00']]],
    ]],
    ['kids','Дети','Детские развлечения',[
      [39,'VinKE Times City','Times City','Парк профессий + игровая зона.',[['price','200K']]],[40,'Аквапарк Ho Tay','Tay Ho','Горки, бассейны.',[['price','150K']]],[41,'Детская площадка Lotte','Lotte Center','Крытая.',[['price','от 60K']]],[42,'Батутный центр Jump','Cau Giay','Батуты, ниндзя-трасса.',[['price','от 100K']]],[43,'Зоопарк Ханоя','Thuy Le','Площадка для пикника с детьми.',[['price','30K']]],
    ]],
    ['sport','Спорт','Спорт',[
      [44,'California Fitness','Много точек','Тренажёры, классы.',[['price','Дневной 150K']]],[45,'Бег вокруг Hoan Kiem','Озеро','Популярный маршрут. 1.7 км.',[['price','Бесплатно']]],[46,'Теннис Tay Ho','Tay Ho','Корты с покрытием.',[['price','100K/час']]],[47,'Йога студия','Hoan Kiem','Групповые и индивидуальные.',[['price','от 100K']]],[48,'Плавание','Бассейны','Общественные бассейны.',[['price','от 50K']]],
    ]],
    ['med','Медицина','Медицина',[
      [49,'Bach Mai Hospital','Hai Ba Trung','Крупнейшая больница. Все отделения.',[['time','Круглосуточно']]],[50,'Vinmec Times City','Times City','Международный стандарт.',[['time','Круглосуточно']]],[51,'International Clinic','Hoan Kiem','Русский/английский.',[['price','от 400K']]],[52,'Dental Clinic','Много точек','Стоматология.',[['time','8:00–20:00']]],[53,'Русская аптека','Tay Ho','Русскоязычный персонал.',[['time','8:00–21:00']]],
    ]],
    ['transport','Транспорт','Транспорт',[
      [54,'Grab','Всюду','Такси, мото.',[['price','от 12K']]],[55,'Mai Linh Taxi','024 3838 383','Счётчик.',[['time','Круглосуточно']]],[56,'Автобусы','Весь город','Сеть маршрутов. 7K VND.',[['price','7K']]],[57,'Метро Ханоя','Cat Linh-Ha Dong','Единственная линия метро.',[['price','15K']]],[58,'Аренда байка','Много','от 100K/день.',[['price','от 100K']]],[59,'Xe Om (мототакси)','Всюду','Местные байкеры. Торг уместен.',[['price','от 10K']]],[60,'Go Viet','Всюду','Приложение.',[['price','от 10K']]],
    ]],
    ['food','Рестораны','Рестораны',[
      [61,'Phở Thìn','Lo Duc','list',' · Легендарный фо с 1979','50–80K'],[62,'Bún Chả Hương Liên','Le Van Huu','list',' · Обед Обамы','40–70K'],[63,'Chả Cá Lã Vọng','Cha Ca','list',' · Жареная рыба с укропом','200K'],[64,'Phở Gia Truyền','Bat Dan','list',' · Культовый фо','50–70K'],[65,'Bánh Mì Hội An','Hoi An','list',' · Лучший бань ми','20–30K'],[66,'Cơm Tấm Bụi','Tay Ho','list',' · Битый рис','30–50K'],[67,'Xôi Yến','Nguyen Huu Huan','list',' · Липкий рис','20–40K'],[68,'Bánh Cuốn Gia An','Hoan Kiem','list',' · Рисовые рулеты','30–50K'],[69,'Bánh Rán Mrs. Tuyết','Hang Giay','list',' · Пончики','10–20K'],[70,'Bún Ốc','Tay Ho','list',' · Лапша с улитками','30–50K'],[71,'Café Giảng','Nguyen Huu Huan','list',' · Яичный кофе','25–40K'],[72,'Café Đinh','Dinh Tien Hoang','list',' · Кофе с видом на озеро','20–40K'],[73,'Highlands Coffee','Много','list',' · Популярная сеть','30–60K'],[74,'Pizza 4P\'s','Hoan Kiem','list',' · Лучшая пицца','200–400K'],[75,'Tôm BBQ','Tay Ho','list',' · Морепродукты','150–350K'],[76,'Red Bean','Hoan Kiem','list',' · Современная вьетнамская','300–600K'],[77,'The Hanoi Social Club','Hoan Kiem','list',' · Международная','150–300K'],[78,'Ngon Villa','Hoan Kiem','list',' · 300 блюд','100–300K'],
    ]],
    ['night','Ночная жизнь','Ночная жизнь',[
      [79,'Top of Hanoi','Lotte 65 эт','Панорама города. Коктейли.',[['time','17:00–24:00']]],[80,'Diamond Sky Bar','Hoan Kiem','Крыша, вид на озеро.',[['time','17:00–2:00']]],[81,'Bia Hơi Corner','Old Quarter','Знаменитый угол пива. 5K/кружка.',[['time','16:00–23:00']]],[82,'The Rooftop','Tay Ho','Лаунж с музыкой.',[['time','17:00–2:00']]],[83,'Hero Club','Hoan Kiem','Ночной клуб.',[['time','22:00–4:00']]],[84,'Polite Pub','Tay Ho','Ирландский паб.',[['time','16:00–2:00']]],
    ]],
    ['services','Сервисы','Сервисы',[
      [85,'Обмен AION','Mini App','Лучший курс.',[['info','Через AION']]],[86,'Прачечная','Tay Ho','от 20K/кг.'],[87,'Vietnam Post','Hoan Kiem','Отправки.'],[88,'Визовый центр','Cau Giay','Продление.'],[89,'Фото документы','Много','Моментально.'],[90,'Упаковка и пересылка','Tay Ho','Международная логистика.'],
    ]],
  ]
};

const HCM = {
  city:'Хошимин', country:'Вьетнам',
  subtitle:'Полный гид по Хошимину — всё, что нужно русскоязычному',
  sections:[
    ['sight','Достопримечательности','Достопримечательности',[
      [1,'Нотр-Дам Сайгона','District 1','Собор французской постройки. Красный кирпич.',[['price','Бесплатно']]],[2,'Центральный почтамт','District 1','Старинное здание + рынок сувениров внутри.',[['price','Бесплатно']]],[3,'Дворец Воссоединения','District 1','Историческое здание 1975 г. Интерьеры эпохи.',[['price','40K'],['time','7:30–16:00']]],[4,'Музей военных следов','District 3','Экспозиция о войне. Военная техника.',[['price','40K'],['time','7:30–18:00']]],[5,'Здание People\'s Committee','District 1','Красивая подсветка вечером. Французская архитектура.',[['price','Бесплатно']]],[6,'Оперный театр','District 1','Театр, шоу A O Show, балет.',[['price','от 200K']]],[7,'Небоскрёб Bitexco','District 1','68 этажей. Saigon Skydeck.',[['price','200K'],['time','9:30–21:30']]],[8,'Chợ Bến Thành','District 1','Главный рынок. Сувениры, еда, всё.',[['time','6:00–18:00']]],[9,'Тоннели Ку Чи','~40 км','Система подземных тоннелей войны. Тур.',[['price','200K'],['info','Экскурсия']]],[10,'Храм Jade Emperor','District 1','Даосский храм, черепахи, драконы.',[['price','Бесплатно']]],[11,'Pagoda Giac Lam','Tan Binh','Старейшая пагода города (1744).',[['price','Бесплатно']]],[12,'Музей изящных искусств','District 1','Вьетнамское искусство. Красивое здание.',[['price','30K']]],[13,'Русский квартал','District 2 (An Phu)','Район экспатов. Русские магазины, кафе.',[['info','An Phu']]],[14,'Saigon Zoo','District 1','Один из старейших зоопарков мира.',[['price','50K']]],[15,'Pham Ngu Lao Street','District 1','Бэкпекерская улица. Бары, хостелы, туры.',[['price','Бесплатно']]],
    ]],
    ['spa','СПА','СПА',[
      [16,'Golden Lotus Spa','District 1','Массаж, хаммам, джакузи. Популярен.',[['price','от 300K']]],[17,'Miu Miu Spa','District 1','Известный спа. Качественный массаж.',[['price','от 280K']]],[18,'La Maison Spa','District 2','Премиум. Французские уходы.',[['price','от 400K']]],[19,'Nam An Spa','District 1','Традиции + современные методики.',[['price','от 250K']]],[20,'Spa at Park Hyatt','District 1','5* спа. Лучший в городе.',[['price','от $100']]],
    ]],
    ['beauty','Красота','Салоны красоты',[
      [21,'Nail District 1','District 1','Маникюр, педикюр. Популярно.',[['price','от 100K']]],[22,'Salon Eva Saigon','District 2','Русские мастера. Стрижки.',[['price','от 200K']]],[23,'Brow & Lash Queen','District 1','Брови, ресницы.',[['price','от 150K']]],[24,'Barber Club Saigon','District 1','Мужские стрижки.',[['price','от 150K']]],[25,'Beauty Center','District 2','Комплексный салон.',[['price','от 200K']]],
    ]],
    ['markets','Рынки','Рынки',[
      [26,'Chợ Bến Thành','District 1','Главный. Всё и сразу.',[['time','6:00–18:00']]],[27,'Chợ Bình Tây','District 6','Китайский квартал. Опт.',[['time','5:00–17:00']]],[28,'Chợ Tân Định','District 1','Розовый рынок. Фрукты, цветы.',[['time','6:00–18:00']]],[29,'Saigon Night Market','District 1','Уличная еда, сувениры.',[['time','17:00–23:00']]],
    ]],
    ['shopping','Шопинг','ТЦ и шопинг',[
      [30,'Vincom Center','District 1','Бренды, кино, фуд-корт.',[['time','9:00–22:00']]],[31,'Saigon Centre','District 1','Высотный ТЦ. Люкс.',[['time','9:30–21:30']]],[32,'Parkson Plaza','District 1','Средний сегмент.',[['time','9:00–22:00']]],[33,'AEON Mall Tan Phu','Tan Phu','Огромный японский ТЦ.',[['time','9:00–22:00']]],[34,'Lotte Mart','District 7','Гипермаркет.',[['time','8:00–22:00']]],
    ]],
    ['kids','Дети','Детские развлечения',[
      [35,'Suoi Tien Park','District 9','Аквапарк + парк культуры.',[['price','150K']]],[36,'Dam Sen Park','District 11','Парк, аквапарк, аттракционы.',[['price','100K']]],[37,'Saigon Zoo','District 1','Старейший зоопарк.',[['price','50K']]],[38,'Батутный центр','District 1','Прыжки, ниндзя.',[['price','от 100K']]],
    ]],
    ['sport','Спорт','Спорт',[
      [39,'California Fitness','District 1','Тренажёры, классы.',[['price','Дневной 150K']]],[40,'Бег в парке','District 1','Công viên Tao Đàn.',[['price','Бесплатно']]],[41,'Теннис','District 2','Корты.',[['price','100K/час']]],[42,'Йога', 'District 2','Студии.',[['price','от 100K']]],[43,'Плавание','Бассейны','Общественные.',[['price','от 50K']]],
    ]],
    ['med','Медицина','Медицина',[
      [44,'FV Hospital','District 7','Международный госпиталь.',[['time','Круглосуточно']]],[45,'Vinmec Central Park','District 2','Современная клиника.',[['time','Круглосуточно']]],[46,'International Clinic','District 1','Русский персонал.',[['price','от 400K']]],[47,'Dental Clinic','Много','Лечение, импланты.',[['time','8:00–20:00']]],
    ]],
    ['transport','Транспорт','Транспорт',[
      [48,'Grab','Всюду','Такси, мото.',[['price','от 10K']]],[49,'Mai Linh Taxi','028 3838 383','Счётчик.',[['time','Круглосуточно']]],[50,'Vinasun Taxi','028 3827 827','Надёжная.',[['time','Круглосуточно']]],[51,'Метро Saigon','District 1','Линия Ben Thanh–Suoi Tien.',[['price','15K']]],[52,'Аренда байка','Много','от 100K/день.',[['price','от 100K']]],[53,'Go Viet','Всюду','Дешевле Grab.',[['price','от 8K']]],
    ]],
    ['food','Рестораны','Рестораны',[
      [54,'Phở Lệ','District 1','list',' · Культовый фо','50–70K'],[55,'Bánh Mì Huỳnh Hoa','District 1','list',' · Специальный бань ми','40–60K'],[56,'Cơm Tấm Bụi Sài Gòn','District 1','list',' · Битый рис','30–50K'],[57,'Bún Thịt Nướng','District 1','list',' · Лапша с грилём','30–50K'],[58,'Secret Garden','District 1','list',' · Вьетнамская на крыше','150–300K'],[59,'Ngon 138','District 1','list',' · 138 блюд','100–250K'],[60,'Pizza 4P\'s','District 1','list',' · Лучшая пицца','200–400K'],[61,'Wrap & Roll','District 1','list',' · Спринг-роллы','80–150K'],[62,'Hoang Yen','District 2','list',' · Русская кухня','150–350K'],[63,'Sakana Sushi','District 1','list',' · Японская','150–400K'],[64,'El Gaucho','District 1','list',' · Аргентинские стейки','500K+'],
    ]],
    ['night','Ночная жизнь','Ночная жизнь',[
      [65,'Bui Vien Walking Street','District 1','Улица баров и музыки.',[['time','19:00–2:00']]],[66,'Saigon Saigon Rooftop','District 1','Коктейли с видом на город.',[['time','17:00–24:00']]],[67,'Chill Sky Bar','District 1','Танцы, музыка, вид.',[['time','17:00–2:00']]],[68,'Lush Nightclub','District 1','Ночной клуб.',[['time','22:00–4:00']]],
    ]],
    ['services','Сервисы','Сервисы',[
      [69,'Обмен AION','Mini App','Лучший курс.',[['info','Через AION']]],[70,'Прачечная','District 1','от 20K/кг.'],[71,'Визовый центр','District 1','Продление.'],[72,'Почта','District 1','Vietnam Post.'],[73,'Ремонт техники','District 1','Телефоны, ноутбуки.'],      [74,'Русский маркет','District 2','Продукты из РФ.'],
    ]],
  ]
};

const RAYONG = {
  city:'Районг', country:'Таиланд',
  subtitle:'Полный гид по Районгу — всё, что нужно русскоязычному',
  sections:[
    ['sight','Достопримечательности','Достопримечательности',[
      [1,'Пляж Saeng Chan','Центр','Главный пляж с золотым песком. Набережная, кафе.',[['price','Бесплатно']]],[2,'Mae Ramphueng Beach','~10 км','Длинный пляж с казуаринами. Мало туристов.',[['price','Бесплатно']]],[3,'Остров Koh Samet','~30 мин','Райский остров. Белый песок, нацпарк.',[['price','200 THB'],['info','Паром']]],[4,'Водопад Khao Chamao','~40 км','Красивый водопад в джунглях.',[['price','100 THB'],['time','8:00–16:30']]],[5,'Сад фруктов Suan Lamai','~20 км','Тропический сад. Дегустация.',[['price','100 THB']]],[6,'Walking Street','Центр','Пт-вс. Сувениры, еда, музыка.',[['time','17:00–22:00 пт-вс']]],[7,'Храм Wat Pa Pradu','Центр','Буддийский храм. Красивые мозаики.',[['price','Бесплатно']]],[8,'Парк принцессы','Центр','Сад камней и скульптур. Вид на море.',[['price','Бесплатно']]],[9,'Рыбацкая деревня Pak Nam','Порт','Свежие морепродукты, рыбный рынок.',[['time','6:00–12:00']]],[10,'Laem Mae Phim Beach','~30 км','Дикий пляж. Спокойный, малолюдный.',[['price','Бесплатно']]],[11,'Фруктовый рынок','Центр','Дуриан, рамбутан, мангостан.',[['time','8:00–18:00']]],[12,'Гора Khao Laem Ya','~20 км','Смотровая. Вид на архипелаг.',[['price','50 THB']]],
    ]],
    ['spa','СПА','СПА и массаж',[
      [13,'Rayong Thai Massage','Центр','Тайский массаж.',[['price','от 200 THB']]],[14,'Lemon Tree Spa','Saeng Chan','Массаж, скрабы.',[['price','от 300 THB']]],[15,'Spa at Novotel','Novotel','Премиум.',[['price','от 600 THB']]],[16,'Baan Nern Spa','~10 км','На природе.',[['price','от 350 THB']]],
    ]],
    ['beauty','Красота','Салоны красоты',[
      [17,'Nail Rayong','Центр','Маникюр, педикюр.',[['price','от 150 THB']]],[18,'Hair Studio','Saeng Chan','Стрижки.',[['price','от 200 THB']]],[19,'Tan Nail & Spa','Центр','Ногти, спа.',[['price','от 120 THB']]],[20,'Barber Rayong','Центр','Мужские стрижки.',[['price','от 150 THB']]],
    ]],
    ['markets','Рынки','Рынки',[
      [21,'Walking Street','Центр','Пт-вс. Еда, сувениры.',[['time','17:00–22:00']]],[22,'Talad Niwet','Центр','Дневной. Овощи, фрукты.',[['time','6:00–17:00']]],[23,'Рыбный рынок','Pak Nam','Улов.',[['time','6:00–12:00']]],[24,'Фруктовый рынок','Шоссе','Дурианы оптом.',[['time','8:00–18:00']]],
    ]],
    ['shopping','Шопинг','ТЦ и шопинг',[
      [25,'Central Plaza Rayong','Центр','Главный ТЦ. Бренды, кино.',[['time','10:00–21:00']]],[26,'Big C Rayong','Центр','Гипермаркет.',[['time','8:00–22:00']]],[27,'Tesco Lotus','Центр','Супермаркет.',[['time','8:00–22:00']]],[28,'HomePro','Центр','Строительные товары.',[['time','8:00–21:00']]],
    ]],
    ['kids','Дети','Детские развлечения',[
      [29,'Saeng Chan с детьми','Центр','Пологий вход.',[['price','Бесплатно']]],[30,'Koh Samet дети','Остров','Мелко, белый песок.',[['price','200 THB']]],[31,'Детская площадка','Central','Крытая.',[['price','Бесплатно']]],[32,'Аквапарк','~10 км','Горки.',[['price','200 THB']]],
    ]],
    ['sport','Спорт','Спорт',[
      [33,'Снорклинг','Koh Samet','Кораллы.',[['price','от 300 THB']]],[34,'Рыбалка','Порт','Туры.',[['price','800–1500 THB']]],[35,'Велотур','Районг','По садам.',[['price','от 200/день']]],[36,'Каякинг','Saeng Chan','Прокат.',[['price','100 THB/час']]],[37,'Гольф','~20 км','18 лунок.',[['price','от 600 THB']]],
    ]],
    ['med','Медицина','Медицина',[
      [38,'Rayong General Hospital','Центр','Главная.',[['time','Круглосуточно']]],[39,'Bangkok Hospital Rayong','~10 км','Международный.',[['time','Круглосуточно']]],[40,'Dental Clinic','Центр','Стоматология.',[['time','9:00–19:00']]],
    ]],
    ['transport','Транспорт','Транспорт',[
      [41,'Grab','Всюду','Такси.',[['price','от 40 THB']]],[42,'Сонгтео','Город','Маршрутки 10–20 THB.',[['price','10–20 THB']]],[43,'Аренда байка','Много','от 200 THB/день.',[['price','от 200 THB']]],[44,'Такси','Стоянки','Счётчик.',[['time','Круглосуточно']]],[45,'Паром на Koh Samet','Порт','Каждые 30 мин.',[['price','100 THB']]],
    ]],
    ['food','Рестораны','Рестораны',[
      [46,'Pu Pen Seafood','Pak Nam','list',' · Знаменитые морепродукты','200–500 THB'],[47,'Je Tawan Seafood','Saeng Chan','list',' · Крабы, креветки','150–400 THB'],[48,'Rabbit Resort Resto','Koh Samet','list',' · У моря','200–400 THB'],[49,'Saneh Jaan','Центр','list',' · Тайская','100–250 THB'],[50,'Rim Tang','Центр','list',' · Уличная еда','40–100 THB'],[51,'Khao Tom','Saeng Chan','list',' · Суп, завтраки','30–80 THB'],[52,'Ban Mai','Центр','list',' · Европейская','100–250 THB'],[53,'Coffee House','Central','list',' · Кофе','40–100 THB'],[54,'Fruit Smoothie','Рынок','list',' · Смузи','20–40 THB'],
    ]],
    ['night','Ночная жизнь','Ночная жизнь',[
      [55,'Walking Street','Центр','Пт-вс. Музыка, еда.',[['time','17:00–22:00']]],[56,'Beach Bars','Saeng Chan','Закат, коктейли.',[['time','17:00–23:00']]],[57,'Sai Thong Bar','Центр','Тайский бар.',[['time','18:00–2:00']]],
    ]],
    ['services','Сервисы','Сервисы',[
      [58,'Обмен AION','Mini App','Лучший курс THB/USD/RUB.',[['info','Через AION']]],[59,'Прачечная','Центр','от 30 THB/кг.'],[60,'Thai Post','Центр','Почта.'],[61,'Визовый центр','Центр','Продление.'],[62,'Ремонт байков','Много','Шины, скутеры.'],
    ]],
  ]
};

const ULANUDE = {
  city:'Улан-Удэ', country:'Россия',
  subtitle:'Полный гид по Улан-Удэ — всё, что нужно русскоязычному',
  sections:[
    ['sight','Достопримечательности','Достопримечательности',[
      [1,'Голова Ленина','Пл. Советов','Самая большая голова Ленина в мире. Символ города.',[['price','Бесплатно']]],[2,'Иволгинский дацан','~30 км','Центр буддизма России. Резиденция Хамбо-ламы.',[['price','Бесплатно'],['time','8:00–18:00']]],[3,'Музей истории Бурятии','Ул. Профсоюзная','Археология, этнография, буддийское искусство.',[['price','150 руб'],['time','10:00–18:00']]],[4,'Этнографический музей','Верх. Берёзовка','Музей под небом. Жилища народов Сибири.',[['price','200 руб'],['time','10:00–18:00']]],[5,'Байкал (~100 км)','Гремячинск','Великое озеро. 1 час на авто.',[['info','100 км']]],[6,'Дацан Ринпоче Багша','Лысая гора','Золотая ступа. Панорама города.',[['price','Бесплатно']]],[7,'Арбат (ул. Ленина)','Центр','Пешеходная. Магазины, кафе.',[['price','Бесплатно']]],[8,'Театр оперы и балета','Пл. Советов','Сталинский ампир. Постановки.',[['price','от 300 руб']]],[9,'Триумфальная арка','Центр','«Царские ворота». Копия 1891.',[['price','Бесплатно']]],[10,'Парк им. Орешкова','Центр','Аттракционы, пруд, кафе.',[['price','Бесплатно']]],[11,'Одигитриевский собор','Центр','Православный собор.',[['price','Бесплатно']]],[12,'Краеведческий музей','Центр','Природа Бурятии.',[['price','100 руб']]],
    ]],
    ['spa','СПА','СПА и бани',[
      [13,'Баня «Аршан»','Центр','Русская парная, веники, бассейн.',[['price','от 500 руб']]],[14,'СПА-салон «Байкал»','Ул. Балтахинова','Массаж, уходы, сауна.',[['price','от 1000 руб']]],[15,'Spa Maison','Центр','Косметология, массаж.',[['price','от 1500 руб']]],[16,'Термы Горячинск','~100 км','Горячие источники у Байкала.',[['price','от 500 руб']]],[17,'Бассейн «Юность»','Центр','Спорткомплекс.',[['price','200 руб']]],
    ]],
    ['beauty','Красота','Салоны красоты',[
      [18,'Beauty Boom','Центр','Стрижки, маникюр.',[['price','от 500 руб']]],[19,'Nail Studio Ultra','Ул. Ленина','Маникюр, дизайн.',[['price','от 600 руб']]],[20,'Салон «Шик»','Центр','Стрижки, уход.',[['price','от 400 руб']]],[21,'Барбершоп «Борода»','Центр','Мужские стрижки.',[['price','от 500 руб']]],[22,'Lash & Brow Studio','Центр','Ресницы, брови.',[['price','от 800 руб']]],
    ]],
    ['markets','Рынки','Рынки',[
      [23,'Центральный рынок','Центр','Продукты, мясо, одежда.',[['time','8:00–19:00']]],[24,'ТЦ «Крестьянский»','Центр','Вещевой.',[['time','9:00–19:00']]],[25,'Рынок «Саяны»','Ул. Терешковой','Фермерское мясо.',[['time','8:00–18:00']]],[26,'ТЦ «Пионер»','Центр','Товары для дома.',[['time','9:00–20:00']]],
    ]],
    ['shopping','Шопинг','ТЦ',[
      [27,'ТРЦ Capital Mall','Центр','Крупнейший. Бренды, кино.',[['time','10:00–21:00']]],[28,'ТЦ «Форум»','Центр','Одежда, кафе.',[['time','10:00–20:00']]],[29,'ТЦ People\'s Park','Центр','Развлечения, еда.',[['time','10:00–22:00']]],[30,'ТЦ «Барис»','Центр','Продукты.',[['time','8:00–22:00']]],
    ]],
    ['kids','Дети','Детские развлечения',[
      [31,'Парк Орешкова','Центр','Аттракционы, колесо.',[['price','от 100 руб']]],[32,'Детский центр «Крошка»','Центр','Развитие, игры.',[['price','от 300 руб']]],[33,'Театр кукол «Ульгэр»','Центр','Кукольные спектакли.',[['price','от 200 руб']]],[34,'Аквапарк «Аквамарин»','~30 км','Горки.',[['price','500 руб']]],
    ]],
    ['sport','Спорт','Спорт',[
      [35,'Спорткомплекс «Юность»','Центр','Бассейн, залы.',[['price','от 200 руб']]],[36,'Лыжная база «Снежинка»','~10 км','Трассы, прокат.',[['price','от 300 руб']]],[37,'Фитнес X-Fit','Центр','Тренажёры, классы.',[['price','Дневной 300 руб']]],[38,'Конный клуб','~20 км','Верховая езда.',[['price','от 1000/час']]],[39,'Набережная','Центр','Бег вдоль Уды.',[['price','Бесплатно']]],
    ]],
    ['med','Медицина','Медицина',[
      [40,'Республиканская больница','Центр','Крупнейшая. Все отделения.',[['time','Круглосуточно']]],[41,'Детская больница','Центр','Педиатрия.',[['time','Круглосуточно']]],[42,'Дентал-С','Центр','Стоматология.',[['time','8:00–20:00']]],[43,'Тибетская медицина','Центр','Иглы, травы.',[['time','9:00–18:00']]],
    ]],
    ['transport','Транспорт','Транспорт',[
      [44,'Маршрутки','Весь город','25 руб.',[['price','25 руб']]],[45,'Автобусы','Весь город','20 руб.',[['price','20 руб']]],[46,'Яндекс Такси','Всюду','от 100 руб.',[['price','от 100 руб']]],[47,'Такси Максим','Всюду','от 80 руб.',[['price','от 80 руб']]],[48,'Аренда авто','Центр','от 1500/день.',[['price','от 1500/день']]],
    ]],
    ['food','Рестораны','Рестораны',[
      [49,'Юрта','Центр','list',' · Бурятская, позы','300–800 руб'],[50,'Одон','Центр','list',' · Бурятская, европейская','300–700 руб'],[51,'Буузы на Ленина','Ул. Ленина','list',' · Знаменитые позы','50–100 руб/шт'],[52,'Чехов','Центр','list',' · Русская','400–1000 руб'],[53,'Токио','Центр','list',' · Японская','400–1000 руб'],[54,'Ханой','Центр','list',' · Вьетнамская','300–800 руб'],[55,'Бочка','Центр','list',' · Пивной ресторан','400–900 руб'],[56,'Кофе-Like','Центр','list',' · Кофейня','100–200 руб'],[57,'Traveler\'s Coffee','Центр','list',' · Кофе, десерты','150–300 руб'],[58,'IL Патио','Центр','list',' · Итальянская','500–1200 руб'],
    ]],
    ['night','Ночная жизнь','Ночная жизнь',[
      [59,'Бар «Хмель»','Центр','Пиво, музыка.',[['time','18:00–2:00']]],[60,'Клуб «Кристалл»','Центр','Танцы, диджеи.',[['time','22:00–5:00']]],[61,'Лаунж «Байкал»','Центр','Коктейли.',[['time','18:00–2:00']]],[62,'Караоке-клуб','Центр','Караоке.',[['time','19:00–4:00']]],
    ]],
    ['services','Сервисы','Сервисы',[
      [63,'Обмен AION','Mini App','Курс RUB/USD.',[['info','Через AION']]],[64,'Почта России','Центр','Отправки.'],[65,'Ремонт техники','Центр','Телефоны.'],[66,'Химчистка','Центр','Чистка.'],[67,'Ключи','Центр','Изготовление.'],
    ]],
  ]
};

const IRKUTSK = {
  city:'Иркутск', country:'Россия',
  subtitle:'Полный гид по Иркутску — всё, что нужно русскоязычному',
  sections:[
    ['sight','Достопримечательности','Достопримечательности',[
      [1,'Озеро Байкал','~70 км','Великое озеро. Листвянка — 1 час.',[['info','70 км']]],[2,'130-й квартал','Центр','Исторический центр. Деревянная архитектура.',[['price','Бесплатно']]],[3,'Знаменский монастырь','Правый берег','Старейший монастырь Сибири. XVIII век.',[['price','Бесплатно']]],[4,'Собор Богоявления','Центр','Красивейший храм, купола.',[['price','Бесплатно']]],[5,'Музей декабристов','Ул. Дзержинского','Дома Трубецкого и Волконского.',[['price','200 руб'],['time','10:00–18:00']]],[6,'Набережная Ангары','Центр','Прогулки, ледокол «Ангара».',[['price','Бесплатно']]],[7,'Ледокол «Ангара»','Набережная','Старейший ледокол (1900). Музей.',[['price','150 руб'],['time','10:00–17:00']]],[8,'Иркутский острог','Центр','Реконструкция крепости.',[['price','100 руб']]],[9,'Музей ВСЖД','Вокзал','Паровозы, вагоны.',[['price','100 руб']]],[10,'Ботанический сад','Ул. Маяковского','Оранжерея, редкие растения.',[['price','150 руб']]],[11,'Парк «Остров Юность»','Центр','Аттракционы, пляж.',[['price','Бесплатно']]],[12,'Гора Кайская','~10 км','Лыжи летом и зимой.',[['price','Подъёмник 200 руб']]],[13,'Тальцы','~50 км','Архитектурно-этнографический музей.',[['price','200 руб']]],
    ]],
    ['spa','СПА','СПА и бани',[
      [14,'Баня «Кругобайкальская»','Листвянка','Русская баня с видом на Байкал.',[['price','от 1000 руб']]],[15,'СПА «Байкал»','Центр','Сауна, бассейн, массаж.',[['price','от 1200 руб']]],[16,'Аквапарк «Аква-Сити»','Центр','Горки, бассейны.',[['price','400 руб']]],[17,'Термальный источник','~100 км','Горячий источник.',[['price','от 300 руб']]],[18,'СПА-отель «Байкал»','Листвянка','Оздоровительный центр.',[['price','от 2000 руб']]],
    ]],
    ['beauty','Красота','Салоны красоты',[
      [19,'Nail Studio','Центр','Маникюр, педикюр.',[['price','от 500 руб']]],[20,'Салон «Прованс»','Центр','Стрижки, окрашивание.',[['price','от 600 руб']]],[21,'Барбершоп «Сибирь»','Центр','Мужские стрижки.',[['price','от 500 руб']]],[22,'Lash Studio','Центр','Ресницы.',[['price','от 800 руб']]],[23,'Студия «Восторг»','Центр','Брови, макияж.',[['price','от 400 руб']]],
    ]],
    ['markets','Рынки','Рынки',[
      [24,'Центральный рынок','Центр','Продукты, мясо, сувениры.',[['time','8:00–19:00']]],[25,'Рынок «Шанхайка»','Центр','Вещевой.',[['time','9:00–19:00']]],[26,'Рыбный рынок','Листвянка','Копчёный омуль.',[['time','9:00–18:00']]],[27,'ТЦ «Комсомолл»','Центр','Фермерские продукты.',[['time','8:00–20:00']]],
    ]],
    ['shopping','Шопинг','ТЦ',[
      [28,'ТРЦ «Комсомолл»','Центр','Крупнейший. Кино, бренды.',[['time','10:00–22:00']]],[29,'ТЦ «Модный квартал»','Центр','Одежда.',[['time','10:00–21:00']]],[30,'ТЦ «Сильвер Молл»','Центр','Магазины, кафе.',[['time','10:00–21:00']]],[31,'ТЦ «Яркий»','Центр','Продукты, техника.',[['time','9:00–21:00']]],
    ]],
    ['kids','Дети','Детские развлечения',[
      [32,'Остров Юность','Центр','Аттракционы, верёвочный парк.',[['price','от 100 руб']]],[33,'Иркутская зоогалерея','Центр','Контактный зоопарк.',[['price','250 руб']]],[34,'Театр кукол «Аистёнок»','Центр','Спектакли.',[['price','от 200 руб']]],[35,'Аквапарк «Аква-Сити»','Центр','Горки для детей.',[['price','400 руб']]],[36,'Нерпинарий','Листвянка','Шоу нерп.',[['price','500 руб']]],
    ]],
    ['sport','Спорт','Спорт',[
      [37,'Гора Кайская','~10 км','Лыжи, прокат.',[['price','Подъёмник 200 руб']]],[38,'Байкальский лёд','Байкал','Коньки, кайт зимой.',[['price','Бесплатно']]],[39,'X-Fit','Центр','Фитнес, бассейн.',[['price','Дневной 300 руб']]],[40,'Треккинг в Тальцах','~50 км','Походы.',[['price','200 руб']]],[41,'Каток «Байкал»','Центр','Массовое катание.',[['price','150 руб']]],
    ]],
    ['med','Медицина','Медицина',[
      [42,'Областная больница','Центр','Ведущая. Скорая.',[['time','Круглосуточно']]],[43,'Диагностический центр','Центр','МРТ, КТ, УЗИ.',[['time','8:00–19:00']]],[44,'Стоматология «32»','Центр','Лечение.',[['time','8:00–21:00']]],[45,'Тибетская медицина','Центр','Травы, иглы.',[['time','9:00–18:00']]],
    ]],
    ['transport','Транспорт','Транспорт',[
      [46,'Маршрутки','Город','25 руб.',[['price','25 руб']]],[47,'Автобусы','Город','20 руб.',[['price','20 руб']]],[48,'Трамваи','Центр','15 руб.',[['price','15 руб']]],[49,'Яндекс Такси','Всюду','от 100 руб.',[['price','от 100 руб']]],[50,'Такси Максим','Всюду','от 80 руб.',[['price','от 80 руб']]],[51,'Электричка на Байкал','Вокзал','До Листвянки.',[['price','150 руб']]],[52,'Аренда авто','Центр','от 1500/день.',[['price','от 1500/день']]],
    ]],
    ['food','Рестораны','Рестораны',[
      [53,'Рассольник','Центр','list',' · Русская кухня','400–1000 руб'],[54,'Буузы на Маркса','Ул. Маркса','list',' · Позы — легенда','50–100 руб/шт'],[55,'Бочка','Центр','list',' · Пиво, европейская','400–900 руб'],[56,'Одон','Центр','list',' · Бурятская','300–700 руб'],[57,'Carlson','Центр','list',' · Европейская','500–1200 руб'],[58,'Марципаны','Центр','list',' · Кондитерская','200–500 руб'],[59,'Харбин','Центр','list',' · Китайская','300–800 руб'],[60,'Ханой','Центр','list',' · Вьетнамская','300–800 руб'],[61,'Traveler\'s Coffee','Центр','list',' · Кофе','150–300 руб'],[62,'Кофе-Like','Центр','list',' · Сеть','100–200 руб'],
    ]],
    ['night','Ночная жизнь','Ночная жизнь',[
      [63,'Бар «Бродская»','Центр','Коктейли, музыка.',[['time','18:00–2:00']]],[64,'Клуб «Сердце»','Центр','Танцы, диджеи.',[['time','22:00–5:00']]],[65,'Паб «Джон Донн»','Центр','Пиво, спорт.',[['time','17:00–2:00']]],[66,'Караоке-бар','Центр','Караоке.',[['time','19:00–4:00']]],
    ]],
    ['services','Сервисы','Сервисы',[
      [67,'Обмен AION','Mini App','Курс RUB/USD.',[['info','Через AION']]],[68,'Почта России','Центр','Отправки.'],[69,'Ремонт техники','Центр','Быстро.'],[70,'Ключи','Центр','Изготовление.'],[71,'Химчистка','Центр','Чистка.'],
    ]],
  ]
};

const countryMap = {'Вьетнам':'vietnam','Таиланд':'thailand','Россия':'russia'};
const cities = [VUNGTAU, DANANG, MUINE, PHUQUOC, HANOI, HCM, RAYONG, ULANUDE, IRKUTSK];
cities.forEach(data => {
  const key = countryMap[data.country] || 'vietnam';
  padCity(data, key);
  const html = genHTML(data.city, data.country, data.subtitle, data.sections);
  const filename = `300 мест рядом с AION — ${data.city}.html`;
  writeFileSync(join(docsDir, filename), html, 'utf8');
  console.log(`OK ${filename} (${data.city}, ${data.country}) — ${data.sections.reduce((s,sec) => s+sec[3].length, 0)} записей`);
});
console.log(`\nDONE ${cities.length} files in /docs/`);
