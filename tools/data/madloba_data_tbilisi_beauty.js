// Madloba.info - Tbilisi Beauty Salons (Салоны красоты) - Page 1/84
// Total: ~1,344 beauty salons in Tbilisi
// Source: https://madloba.info/tbilisi/salony-krasoty/
// Each individual business page fetched for full contact details

const tbilisiBeautySalons = [
  {
    name: "Botanique",
    contact: "Телефон: +995 555 56 85 85",
    website: "http://www.taplink.cc/botaniquebeauty.ge",
    instagram: "https://www.instagram.com/botaniquenail/",
    address: "пр-т Ильи Чавчавадзе 37, Тбилиси, Грузия",
    description: "Маникюрный салон. Специалисты используют только одноразовые инструменты, после каждого посетителя дезинфицируют помещение. Нейл-мастера, парикмахеры-стилисты и косметологи.",
    hours: "Пн–Вс: 10:00–21:00",
    rating: "5.0",
    city: "Тбилиси",
    category: "beauty",
    tags: ["phone", "website", "instagram", "facebook"]
  },
  {
    name: "FERO",
    contact: "Телефон: +995 591 04 39 46",
    website: null,
    instagram: "https://instagram.com/fero_tbilisi",
    address: "ул. Шроши, 6, Тбилиси, Грузия",
    description: "Салон красоты - парикмахерские услуги для мужчин и женщин, маникюр и педикюр, массажи и уход за кожей.",
    hours: "Пн–Вс: 10:00–20:00",
    rating: "5.0",
    city: "Тбилиси",
    category: "beauty",
    tags: ["phone", "instagram"]
  },
  {
    name: "G.Bar Tbilisi",
    contact: "Телефон: +995 591 02 62 02",
    website: "https://gbar.ge/",
    instagram: "https://www.instagram.com/g.bar.tbilisi",
    address: "ул. Владимира Кавсадзе, 3, Тбилиси, Грузия",
    description: "Сеть салонов красоты из 27 точек в 9 странах. Укладки, стрижки, плетение кос, макияж, маникюр, моделирование бровей.",
    hours: "Пн–Вс: 09:00–21:00",
    rating: "4.7",
    city: "Тбилиси",
    category: "beauty",
    tags: ["phone", "website", "instagram", "facebook", "youtube"]
  },
  {
    name: "LORO",
    contact: "Телефон: +995 597 05 41 46",
    website: "http://loro-salon.com/",
    instagram: "https://www.instagram.com/lorosalon",
    address: "ул. Закария Палиашвили, 60, Тбилиси, Грузия",
    description: "Салон красоты - стрижки, укладки, современные техники окрашивания, профессиональный макияж, перманентный макияж, маникюр. Курсы визажа.",
    hours: "Пн–Вс: 08:00–23:30",
    rating: "4.7",
    city: "Тбилиси",
    category: "beauty",
    tags: ["phone", "website", "instagram", "facebook", "whatsapp"]
  },
  {
    name: "London Premium",
    contact: "Телефон: +995 577 33 12 14, +995 322 77 49 85",
    website: null,
    instagram: null,
    address: "просп. Монаха Габриэля Салоса, 32, Тбилиси, Грузия",
    description: "Многопрофильный салон красоты. Микроблейдинг бровей, пилинг, вакуумный и лимфодренажный массаж, кавитация, RF-лифтинг, перманентный макияж, кератиновое восстановление волос, диодная эпиляция.",
    hours: "Пн–Вс: 10:00–21:00",
    rating: "4.8",
    city: "Тбилиси",
    category: "beauty",
    tags: ["phone", "facebook"]
  },
  {
    name: "Chiqo",
    contact: "Телефон: +995 558 35 39 32, +995 322 96 51 32",
    website: "https://beauty-salon-chiqo.business.site/",
    instagram: "https://www.instagram.com/saloni_chiqo/",
    address: "ул. Бакинская 20, Тбилиси, Грузия",
    description: "Салон красоты - стрижка, укладка, уход за лицом, маникюр, педикюр, восковая эпиляция. Косметические продукты премиум-класса.",
    hours: "Пн–Вс: 10:00–20:00",
    rating: "5.0",
    city: "Тбилиси",
    category: "beauty",
    tags: ["phone", "website", "instagram", "facebook"]
  },
  {
    name: "Say Yes Beauty Space",
    contact: "Телефон: +995 593 61 69 89",
    website: null,
    instagram: "https://instagram.com/say_yes_beauty",
    address: "ул. Михаила Бурдзгла, 72, Тбилиси, Грузия",
    description: "Салон красоты - услуги по уходу за кожей лица и тела, стилем волос, маникюром и педикюром. Свадебные и вечерние образы.",
    hours: "Пн–Вс: 10:00–21:00",
    rating: "4.9",
    city: "Тбилиси",
    category: "beauty",
    tags: ["phone", "instagram"]
  },
  {
    name: "United",
    contact: null,
    website: null,
    instagram: null,
    address: "ул. Цотнэ Дадиани, 106, Тбилиси, Грузия",
    description: "Парикмахерская с футбольной тематикой. Стрижки для детей и взрослых.",
    rating: "4.8",
    city: "Тбилиси",
    category: "beauty",
    tags: []
  },
  {
    name: "Time of Beauty",
    contact: null,
    website: null,
    instagram: null,
    address: "пр-т Важи Пшавелы, 14А, Тбилиси, Грузия",
    description: "Салон красоты - услуги от ведущих стилистов и косметологов. Маникюр, педикюр, косметология.",
    rating: "5.0",
    city: "Тбилиси",
    category: "beauty",
    tags: []
  },
  {
    name: "Just you",
    contact: null,
    website: null,
    instagram: null,
    address: "ул. Университетская, 24, Тбилиси, Грузия",
    description: "Салон красоты с индивидуальным подходом.",
    rating: "4.7",
    city: "Тбилиси",
    category: "beauty",
    tags: []
  },
  {
    name: "MELANGE ACADEMY",
    contact: null,
    website: null,
    instagram: null,
    address: "пр-кт. Важи Пшавелы, 37, Тбилиси, Грузия",
    description: "Школа красоты, основана в 2006 году. Официальный представитель брендов.",
    rating: "4.6",
    city: "Тбилиси",
    category: "beauty",
    tags: []
  },
  {
    name: "Лаборатория красоты Escorpio",
    contact: null,
    website: null,
    instagram: null,
    address: "ул. Ивана Джавахишвили, 71, Тбилиси, Грузия",
    description: "Салон красоты - качественный уход в уютной обстановке.",
    rating: "4.8",
    city: "Тбилиси",
    category: "beauty",
    tags: []
  },
  {
    name: "Iveria Care Saburtalo",
    contact: null,
    website: null,
    instagram: null,
    address: "0160, Тбилиси, р-н Ваке-Сабуртало, ул. Шартава 35",
    description: "Универсальная студия красоты и ухода за собой в районе Ваке-Сабуртало.",
    rating: "4.5",
    city: "Тбилиси",
    category: "beauty",
    tags: []
  },
  {
    name: "L'Academie",
    contact: null,
    website: null,
    instagram: null,
    address: "ул. Иовела Кутателадзе, 1А, Тбилиси, Грузия",
    description: "Салон красоты - широкий спектр услуг по уходу за внешностью.",
    rating: "4.7",
    city: "Тбилиси",
    category: "beauty",
    tags: []
  },
  {
    name: "Sunstudio",
    contact: null,
    website: null,
    instagram: null,
    address: "0162, Тбилиси, р-н Ваке-Сабуртало, пр-кт Ильи Чавчавадзе 39b",
    description: "Салон красоты - косметические услуги, включая солярий.",
    rating: "5.0",
    city: "Тбилиси",
    category: "beauty",
    tags: []
  },
  {
    name: "Women's club",
    contact: null,
    website: null,
    instagram: null,
    address: "ул. Е. Такаишвили, 1, Тбилиси, Грузия",
    description: "Центр красоты для девушек.",
    rating: "4.9",
    city: "Тбилиси",
    category: "beauty",
    tags: []
  }
];

module.exports = tbilisiBeautySalons;
console.log(`Tbilisi Beauty Salons: ${tbilisiBeautySalons.length} entries exported`);
console.log(`Page 1/84 - ${84 * 16} total salons estimated`);
