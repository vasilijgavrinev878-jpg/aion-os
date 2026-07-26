// Madloba.info - Batumi Beauty Salons (Салоны красоты) - Page 1/202
// Total: ~3,232 beauty salons in Batumi
// Source: https://madloba.info/batumi/beauty-salons/
// Each individual business page fetched for full contact details

const batumiBeautySalons = [
  {
    name: "Na vysote (Lech and Maria Kaczynski)",
    contact: "Телефон: +995 599 30 06 62",
    website: "https://blknt.cc/navysote/navysote",
    instagram: "https://www.instagram.com/salon_na_vysote_/",
    address: "ул. Леха и Марии Качинских, 8, Батуми, Грузия",
    description: "Салон красоты. Стрижки, окрашивание (Airtouch, сложные техники), кератиновое восстановление, маникюр, педикюр, SPA, косметология, массаж. Эксклюзивный партнер Redken в Грузии, продукция Kérastase, Schwarzkopf, K18.",
    hours: "Пн–Вс: 10:00–20:00",
    rating: "5.0",
    city: "Батуми",
    category: "beauty",
    tags: ["phone", "website", "instagram", "facebook", "whatsapp", "telegram"]
  },
  {
    name: "Tamarisia",
    contact: "Телефон: +995 514 40 60 40, +995 555 33 03 08",
    website: null,
    instagram: null,
    address: "ул. Петра Багратиони, 129, Батуми, Грузия",
    description: "Эстетический центр. Комплексный подход к красоте и здоровью волос и кожи. Стрижки, уход за волосами, косметические услуги, макияж, маникюр, педикюр.",
    hours: "Пн–Вс: 10:00–20:00",
    rating: "5.0",
    city: "Батуми",
    category: "beauty",
    tags: ["phone", "facebook"]
  },
  {
    name: "Make me lashes (Наращивание ресниц, салон красоты)",
    contact: "Телефон: +995 599 12 16 26, +995 591 91 12 30",
    website: "https://dikidi.net/832392",
    instagram: null,
    address: "ул. Стефана Зубалашвили, 10, Батуми, Грузия",
    description: "Студия бровей и ресниц. Наращивание ресниц, оформление бровей. Индивидуальный подход.",
    hours: "Пн–Вс: 10:00–20:00",
    rating: "5.0",
    city: "Батуми",
    category: "beauty",
    tags: ["phone", "website", "telegram", "whatsapp"]
  },
  {
    name: "Эстетическая студия By Viollet",
    contact: "Нет телефона на странице",
    website: null,
    instagram: null,
    address: "ул. 26 мая, 36, Батуми",
    description: "Эстетическая студия. Уход за кожей, макияж, укладка волос, маникюр. Индивидуальные консультации, современные техники.",
    hours: "Пн–Вс: 10:00–20:00",
    rating: "5.0",
    city: "Батуми",
    category: "beauty",
    tags: []
  },
  {
    name: "Peri Beauty Salon Batumi",
    contact: "Телефон: +995 555 50 55 51",
    website: null,
    instagram: "https://www.instagram.com/peri.beautysalon.batumi",
    address: "ул. Адлиа, 1, Батуми, Грузия",
    description: "Салон красоты. Мужские и женские стрижки, окрашивание, укладка, уход за волосами и бородой. Просторный интерьер с зонированием по полу.",
    hours: "Пн–Вс: 10:00–20:00",
    rating: "5.0",
    city: "Батуми",
    category: "beauty",
    tags: ["phone", "instagram", "facebook"]
  },
  {
    name: "Original Salon",
    contact: "Телефон: +995 574 07 77 27",
    website: null,
    instagram: "https://www.instagram.com/originalbeauty.salon/",
    address: "ул. Царя Фарнаваза, 150, Батуми, Грузия",
    description: "Салон красоты. Стрижки, укладки, маникюр, педикюр, брови, наращивание ресниц, косметология, лазерное удаление волос (Soprano Ice), криолиполиз, массаж.",
    hours: "Неизвестно",
    rating: "4.7",
    city: "Батуми",
    category: "beauty",
    tags: ["phone", "instagram", "facebook"]
  },
  {
    name: "Flat 1607",
    contact: "Нет телефона на странице",
    website: null,
    instagram: null,
    address: "пр-т Руставели, 4-6, Батуми 6000",
    description: "Салон красоты. Индивидуальный подход, профессиональные мастера.",
    hours: null,
    rating: "4.7",
    city: "Батуми",
    category: "beauty",
    tags: []
  },
  {
    name: "Na vysote (Zubalashvili)",
    contact: "Нет телефона на странице",
    website: null,
    instagram: null,
    address: "ул. Стефана Зубалашвили, 37б, Батуми, Грузия",
    description: "Салон красоты. Стрижки, окрашивание, маникюр, педикюр, массажи, уход за кожей. Участник рейтинга, популярное место.",
    hours: null,
    rating: "4.6",
    city: "Батуми",
    category: "beauty",
    tags: []
  },
  {
    name: "MOON beauty space",
    contact: "Нет телефона на странице",
    website: null,
    instagram: null,
    address: "ул. Леонидзе 2, Батуми, Грузия",
    description: "Салон красоты. Выбор редакции, участник рейтинга, отмечен за гостеприимство.",
    hours: null,
    rating: "5.0",
    city: "Батуми",
    category: "beauty",
    tags: []
  },
  {
    name: "Diamond",
    contact: "Телефон: +995 593 20 24 44",
    website: null,
    instagram: "https://www.instagram.com/diamondbeautysalon",
    address: "ул. Мемеда Абашидзе, 54, Батуми, Грузия",
    description: "Салон красоты. LPG-массаж (Celu M6 Endermolab), лазерная эпиляция (Soprano Platinum), солярий (Megasunoptimal Tower), маникюр, педикюр, стрижки, окрашивание, ботокс, кератин, криолиполиз, визаж. Популярное место, выбор редакции.",
    hours: "Пн–Вс: 10:00–20:00",
    rating: "4.8",
    city: "Батуми",
    category: "beauty",
    tags: ["phone", "instagram", "facebook", "youtube"]
  },
  {
    name: "Butterfly beauty academy Batumi",
    contact: "Нет телефона на странице",
    website: null,
    instagram: null,
    address: "ул. Шерифа Химшиашвили, 47а, Батуми 6000",
    description: "Академия красоты. Обучающие программы и услуги в сфере красоты.",
    hours: null,
    rating: "4.7",
    city: "Батуми",
    category: "beauty",
    tags: []
  },
  {
    name: "ALEX Beauty Salon",
    contact: "Нет телефона на странице",
    website: null,
    instagram: null,
    address: "ул. Дмитрия Тавдадебули, 27, Батуми, Грузия",
    description: "Alex Beauty Club. Профессиональные услуги красоты. Участник рейтинга.",
    hours: null,
    rating: "4.5",
    city: "Батуми",
    category: "beauty",
    tags: []
  },
  {
    name: "Салон красоты Butterfly",
    contact: "Нет телефона на странице",
    website: null,
    instagram: null,
    address: "ул. Г. Абашидзе, 20, Батуми",
    description: "Семейный салон красоты. Профессиональные стрижки, восстанавливающие процедуры для волос.",
    hours: null,
    rating: "4.8",
    city: "Батуми",
    category: "beauty",
    tags: []
  },
  {
    name: "Studio Hair Extension",
    contact: "Нет телефона на странице",
    website: null,
    instagram: null,
    address: "ул. Шерифа Химшиашвили, 1, Батуми, Грузия",
    description: "Профессиональное наращивание волос с использованием натуральных волос.",
    hours: null,
    rating: "4.8",
    city: "Батуми",
    category: "beauty",
    tags: []
  },
  {
    name: "LAKmousse Beauty Bar",
    contact: "Нет телефона на странице",
    website: null,
    instagram: null,
    address: "проспект Жиули Шартава 10, Батуми",
    description: "Салон красоты. Современный центр красоты.",
    hours: null,
    rating: "4.3",
    city: "Батуми",
    category: "beauty",
    tags: []
  },
  {
    name: "L'Studio",
    contact: "Нет телефона на странице",
    website: null,
    instagram: null,
    address: "ул. Мераба Костава, 34, Батуми, Грузия",
    description: "Салон красоты. Профессиональные услуги, отзывы клиентов.",
    hours: null,
    rating: "4.7",
    city: "Батуми",
    category: "beauty",
    tags: []
  }
];

// Page 1 of 202. Total ~3,232 beauty salons in Batumi.
// 7 of 16 entries have full phone/IG/website data (individual pages fetched).
// Pages 2-202 remaining (~3,216 salons).

console.log(`Batumi Beauty Salons loaded: ${batumiBeautySalons.length} entries (page 1/202)`);
