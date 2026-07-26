const contacts = [
  // ========================
  // 1. КРАСОТА / ЗДОРОВЬЕ
  // ========================
  {
    name: "Melissa - Салон красоты",
    contact: "WhatsApp: +905362801164",
    category: "beauty",
    tags: ["phone", "whatsapp"],
  },
  {
    name: "Melissa - Салон красоты",
    contact: "Instagram: @melissa_salon_antalya (профиль на сайте)",
    category: "beauty",
    tags: ["instagram"],
  },
  {
    name: "Melissa - Салон красоты",
    contact: "Адрес: Ataturk Bulv 18, Of.3, Pinarbasi Mah, Konyaalti, Antalya",
    category: "beauty",
    tags: ["address"],
  },
  {
    name: "Стоматолог Эзги Озкан Озбен",
    contact: "WhatsApp: +905317347881 (Самира)",
    category: "beauty",
    tags: ["phone", "whatsapp"],
  },
  {
    name: "Стоматолог Эзги Озкан Озбен",
    contact: "Instagram: @dt.ezgiozkanozben",
    category: "beauty",
    tags: ["instagram"],
  },
  {
    name: "Стоматолог Эзги Озкан Озбен",
    contact: "Адрес: Arapsuyu mahallesi, Atatürk Blv., Gökay Plaza No:23 Kat:4 daire:14, 07070 Konyaaltı/Antalya",
    category: "beauty",
    tags: ["address"],
  },
  {
    name: "Running With Pleasure Antalya",
    contact: "Instagram: @running_with_pleasure_tur_eng",
    category: "beauty",
    tags: ["instagram"],
  },
  {
    name: "Running With Pleasure Antalya",
    contact: "Telegram: @runningwithpleasureAntalya",
    category: "beauty",
    tags: ["telegram"],
  },
  {
    name: "Running With Pleasure Antalya",
    contact: "Сайт: enjoytherunintheworld.com/run21day_antalya",
    category: "beauty",
    tags: ["website"],
  },
  {
    name: "МЫВМЕСТЕ - Психологическая помощь",
    contact: "Телефон: +905444471187",
    category: "beauty",
    tags: ["phone"],
  },
  {
    name: "МЫВМЕСТЕ - Психологическая помощь",
    contact: "Сайт: psychologistem.tilda.ws/turkey",
    category: "beauty",
    tags: ["website"],
  },
  {
    name: "Dejuni - Студия массажа и шугаринга",
    contact: "Телефон: +905076103093",
    category: "beauty",
    tags: ["phone"],
  },
  {
    name: "Dejuni - Студия массажа и шугаринга",
    contact: "Instagram: профиль на сайте",
    category: "beauty",
    tags: ["instagram"],
  },
  {
    name: "Dejuni - Студия массажа и шугаринга",
    contact: "Адрес: Коньяалты, Лиман Махаллеси, 32 улица д.14, 3 этаж, 6 кабинет",
    category: "beauty",
    tags: ["address"],
  },

  // ========================
  // 2. ДЕТИ
  // ========================
  {
    name: "Няня на час (Виктория)",
    contact: "WhatsApp: +380997412555",
    category: "children",
    tags: ["phone", "whatsapp"],
  },
  {
    name: "Party Time Antalya - Аниматоры",
    contact: "Телефон: +79003025235",
    category: "children",
    tags: ["phone"],
  },
  {
    name: "Party Time Antalya - Аниматоры",
    contact: "Instagram: профиль на сайте",
    category: "children",
    tags: ["instagram"],
  },
  {
    name: "ЧИРАДЕИ - Семейный эко-лагерь",
    contact: "Телефон: +905367100759",
    category: "children",
    tags: ["phone"],
  },
  {
    name: "ЧИРАДЕИ - Семейный эко-лагерь",
    contact: "Instagram: профиль на сайте",
    category: "children",
    tags: ["instagram"],
  },

  // ========================
  // 3. ДОМ / РЕМОНТ / БЫТ
  // ========================
  {
    name: "Русскоязычное Телевидение",
    contact: "WhatsApp: +905313628603",
    category: "housemaster",
    tags: ["phone", "whatsapp"],
  },
  {
    name: "SharkWeClean - Клининг",
    contact: "WhatsApp: +905525711862",
    category: "housemaster",
    tags: ["phone", "whatsapp"],
  },
  {
    name: "SharkWeClean - Клининг",
    contact: "Instagram: @shark.weclean",
    category: "housemaster",
    tags: ["instagram"],
  },
  {
    name: "Antalya Tadilat Dekorasyon (Ремонт и декор)",
    contact: "WhatsApp: +905321774201",
    category: "housemaster",
    tags: ["phone", "whatsapp"],
  },
  {
    name: "Antalya Tadilat Dekorasyon (Ремонт и декор)",
    contact: "Сайт: antalyatadilatdekorasyon.com.tr",
    category: "housemaster",
    tags: ["website"],
  },
  {
    name: "Antalya stretch ceilings (Натяжные потолки)",
    contact: "Телефон / WhatsApp: +905348287110",
    category: "housemaster",
    tags: ["phone", "whatsapp"],
  },
  {
    name: "Antalya stretch ceilings (Натяжные потолки)",
    contact: "Instagram: @antalya_potolok",
    category: "housemaster",
    tags: ["instagram"],
  },
  {
    name: "Antalya stretch ceilings (Натяжные потолки)",
    contact: "Telegram: @antalya_potolok / @antalya_potolki",
    category: "housemaster",
    tags: ["telegram"],
  },
  {
    name: "Antalya stretch ceilings (Натяжные потолки)",
    contact: "Сайт: antalya-potolok.com",
    category: "housemaster",
    tags: ["website"],
  },
  {
    name: "Муж на час (Алексей)",
    contact: "WhatsApp: +905524562699",
    category: "housemaster",
    tags: ["phone", "whatsapp"],
  },
  {
    name: "Виталий - Ремонт бытовой техники",
    contact: "Телефон: +905441011653",
    category: "housemaster",
    tags: ["phone"],
  },

  // ========================
  // 4. ОТДЫХ / РАЗВЛЕЧЕНИЯ
  // ========================
  {
    name: "SHULGIN & KAMILLA (Организация свадеб/мероприятий)",
    contact: "Telegram: @event_agency_tr_uae",
    category: "entertainment",
    tags: ["telegram"],
  },
  {
    name: "SHULGIN & KAMILLA (Организация свадеб/мероприятий)",
    contact: "Instagram: @shulgin.kamilla",
    category: "entertainment",
    tags: ["instagram"],
  },
  {
    name: "SHULGIN & KAMILLA (Организация свадеб/мероприятий)",
    contact: "WhatsApp: +79152756969",
    category: "entertainment",
    tags: ["phone", "whatsapp"],
  },
  {
    name: "Camp D Padel",
    contact: "WhatsApp: +905300480799",
    category: "entertainment",
    tags: ["phone", "whatsapp"],
  },
  {
    name: "Camp D Padel",
    contact: "Instagram: @campdpadel",
    category: "entertainment",
    tags: ["instagram"],
  },

  // ========================
  // 5. РАБОТА / БИЗНЕС
  // ========================
  {
    name: "OLGA VORONOVA (Организация мероприятий)",
    contact: "WhatsApp: +79003025235",
    category: "job",
    tags: ["phone", "whatsapp"],
  },
  {
    name: "OLGA VORONOVA (Организация мероприятий)",
    contact: "Instagram: @ola.ptichka",
    category: "job",
    tags: ["instagram"],
  },
  {
    name: "Smart Consulting / Людмила Домосканова (Открытие компаний)",
    contact: "Телефон: +905362318944",
    category: "job",
    tags: ["phone"],
  },
  {
    name: "Smart Consulting / Людмила Домосканова (Открытие компаний)",
    contact: "Instagram: профиль на сайте",
    category: "job",
    tags: ["instagram"],
  },

  // ========================
  // 6. ОБУЧЕНИЕ ДЛЯ ВЗРОСЛЫХ
  // ========================
  {
    name: "EART Студия живописи",
    contact: "WhatsApp: +79629595665",
    category: "adult_education",
    tags: ["phone", "whatsapp"],
  },
  {
    name: "EART Студия живописи",
    contact: "Instagram: @eart__antalya",
    category: "adult_education",
    tags: ["instagram"],
  },
  {
    name: "EART Студия живописи",
    contact: "Сайт: olha-antalya.wfolio.pro/disk/studiya-zhivopisi",
    category: "adult_education",
    tags: ["website"],
  },

  // ========================
  // 7. ФОТО / ВИДЕО
  // ========================
  {
    name: "Надежда (фотограф)",
    contact: "WhatsApp: +905445385658",
    category: "photo",
    tags: ["phone", "whatsapp"],
  },
  {
    name: "Надежда (фотограф)",
    contact: "Instagram: @dubrovskaya_fotoantalya",
    category: "photo",
    tags: ["instagram"],
  },

  // ========================
  // 8. ЮРИДИЧЕСКИЕ УСЛУГИ / ВНЖ
  // ========================
  {
    name: "Дежурный менеджер (Шенген / ВНЖ / переезд / страховка)",
    contact: "WhatsApp: +905367968443",
    category: "docs",
    tags: ["phone", "whatsapp"],
  },

  // ========================
  // 9. ТРАНСПОРТ
  // ========================
  {
    name: "OZLAND TURIZM (Трансфер из аэропорта)",
    contact: "Телефон: +79643638183",
    category: "transport",
    tags: ["phone"],
  },
];

export default contacts;
