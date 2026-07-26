#Requires -Version 5.1
# Generate contact HTML files

$catDefs = @(
    @{id="beauty";    name="Красота и уход"; n=75},
    @{id="fitness";   name="Фитнес и спорт"; n=65},
    @{id="kids";      name="Дети и развитие"; n=105},
    @{id="psychology";name="Психология и здоровье"; n=45},
    @{id="medicine";  name="Медицина"; n=29},
    @{id="photo";     name="Фото и видео"; n=40},
    @{id="rental";    name="Аренда и транспорт"; n=40},
    @{id="tourism";   name="Туризм и экскурсии"; n=45},
    @{id="food";      name="Еда и продукты"; n=30},
    @{id="digital";   name="Цифровые услуги"; n=34},
    @{id="realty";    name="Недвижимость"; n=25},
    @{id="other";     name="Прочее"; n=35}
)
$total = ($catDefs | % { $_.n }) | Measure-Object -Sum | % Sum

# First name bases (Latin, for Telegram usernames)
$fm = @("alexey","alexandr","sergey","dmitry","maksim","artyom","ivan","mikhail","andrey","vladimir","pavel","konstantin","nikolay","evgeny","vitaly","roman","vadim","oleg","ruslan","timur","kirill","stanislav","gleb","marat","danil","igor","vyacheslav","grigory","anton","yury","vasily","vladislav","nikita","egor","david","yaroslav","semyon","tigran","artur","eduard")
$ff = @("anna","elena","olga","maria","natalya","irina","tatiana","svetlana","ekaterina","anastasia","yulia","kristina","darya","alisa","veronika","oksana","evgenya","lyudmila","margarita","sofiya","polina","viktoria","valeriya","nadezhda","galina","larisa","alina","kseniya","vera","marina","alyona","yana","zoya","valentina","lidiya","raisa","tamara","lyubov","nina","zlata")
$allNames = $fm + $ff

# Services in Russian (for display) and English (for usernames)
# Format: "russian_text|english_keyword"
$svcDef = @{}
$svcDef.beauty = @(
    "Маникюр, педикюр|manicure","Косметолог, чистка лица|cosmetology","Парикмахер, стрижки|barber","Лазерная эпиляция|laser","Шугаринг, депиляция|shugaring",
    "Наращивание ресниц|lashes","Брови, ламинирование|brows","Тату, перманент|tattoo","Массаж лица, микротоки|massage","Салон красоты|beauty_salon",
    "Визажист, макияж|makeup","Барбершоп|barbershop","Кератиновое выпрямление|keratin","Дизайн ногтей|nail_art","Чистка лица, пилинги|facial",
    "Микроблейдинг|microblading","Окрашивание волос|hair_color","СПА-процедуры|spa","Обертывания|wraps","Ламинирование ресниц|lash_lift",
    "Электроэпиляция|electro","Архитектура бровей|brow_arch","Мужские стрижки|mens_hair","Педикюр медицинский|pedicure"
)
$svcDef.fitness = @(
    "Персональный тренер|trainer","Йога, растяжка|yoga","Пилатес|pilates","Бокс, кикбоксинг|boxing","Фитнес, ОФП|fitness",
    "Танцы, хореография|dance","Плавание|swimming","Серфинг, сапсерфинг|surf","Стретчинг|stretching","Большой теннис|tennis",
    "Кроссфит|crossfit","Детский фитнес|kids_fitness","Зумба|zumba","Беговой клуб|running","Единоборства|martial_arts",
    "Функциональный тренинг|functional","Скалолазание|climbing","MTB велоспорт|mtb","Триатлон|triathlon","Тренажерный зал|gym"
)
$svcDef.kids = @(
    "Няня|nanny","Английский язык|english","Логопед|logoped","Подготовка к школе|school_prep","Репетитор начальных классов|tutor",
    "Развивающие занятия|development","Рисование, ИЗО|drawing","Музыка, фортепиано|music","Гитара, вокал|guitar","Раннее развитие|early_dev",
    "Математика|math","Программирование для детей|programming","Детский сад|kindergarten","Детский массаж|kids_massage","Ментальная арифметика|mental_arith",
    "Каллиграфия|calligraphy","Творческая мастерская|art_studio","Китайский язык|chinese","Детский психолог|child_psy","Скорочтение|speed_reading",
    "Робототехника, LEGO|robotics","Театральная студия|theatre","Французский язык|french","Немецкий язык|german","Испанский язык|spanish",
    "Корейский язык|korean","Шахматы|chess","Детская йога|kids_yoga","Монтессори|montessori","Футбол для детей|football",
    "Баскетбол|basketball","Лепка, керамика|ceramics"
)
$svcDef.psychology = @(
    "Психолог|psychologist","Психотерапия|psychotherapy","Коуч-консультации|coach","Нумеролог|numerolog","Астролог|astrologer",
    "Гипнотерапия|hypnosis","Рэйки, энергопрактики|reiki","Телесная терапия|body_therapy","Детский психолог|child_psychologist","Семейный психолог|family_psy",
    "Арт-терапия|art_therapy","Гештальт-терапия|gestalt","Травматерапия|trauma","Медитация|meditation","Трансформационные игры|transform",
    "Кинезиология|kinesiology","Песочная терапия|sand_therapy","Женские круги|women_circle","Дыхательные практики|breathing","Транзактный анализ|ta_analysis"
)
$svcDef.medicine = @(
    "Терапевт, общая практика|therapist","Педиатр|pediatrician","Стоматолог|dentist","Гинеколог|gynecologist","Дерматолог|dermatologist",
    "ЛОР|lor","Офтальмолог|ophthalmologist","Массаж медицинский|medical_massage","Диетолог, нутрициолог|dietolog","Остеопат|osteopath",
    "Хирург|surgeon","Кардиолог|cardiologist","Физиотерапия|physiotherapy","Медсестра, уколы на дому|nurse","Детский массаж, ЛФК|kids_massage",
    "Мануальный терапевт|manual_therapy","Анализы, чек-ап|analysis","Гомеопат|homeopath","Эндокринолог|endocrinolog"
)
$svcDef.photo = @(
    "Фотограф, портреты|photographer","Видеограф, монтаж|videographer","Свадебная съемка|wedding","Предметная съемка|product","Съемка с дрона|drone",
    "Ретушь, обработка|retouch","Контент-мейкер|content","Видеомонтаж, reels|reels","Фотостудия|photo_studio","Love story, портрет|love_story",
    "Детский фотограф|kids_photo","Будуарная съемка|boudoir","Бренд-фотография|brand_photo","Фуд-фотограф|food_photo","Интерьерная съемка|interior",
    "Тревел-контент|travel","Семейная фотосессия|family_photo","Товарная съемка|catalog","Аэросъемка|aerial","Видеоролики для соцсетей|social_video"
)
$svcDef.rental = @(
    "Аренда байков, скутеров|bike_rent","Аренда автомобилей|car_rent","Трансфер аэропорт|airport","Такси, трансфер|taxi","Прокат велосипедов|bicycle",
    "Аренда мотоциклов|moto_rent","Ремонт байков|bike_repair","Автомойка, химчистка|car_wash","Междугородний трансфер|transfer","Аренда лодок, катеров|boat_rent",
    "Мототакси, доставка|moto_taxi","Доставка грузов|cargo","Аренда электросамокатов|escooter","Аренда гидроциклов|jetski","Автосервис|auto_service",
    "Охраняемая парковка|parking","Продажа мотоциклов|moto_sale","Личный водитель|driver","Прокат снаряжения|equipment","Эвакуатор|tow_truck"
)
$svcDef.tourism = @(
    "Экскурсии|excursions","Дайвинг, снорклинг|diving","Морская рыбалка|fishing","Яхта, морские прогулки|yacht","Визаран, оформление виз|visarun",
    "Гид, сопровождение|guide","Треккинг, походы|trekking","Тур на острова|island_tour","Водопады, природа|nature","Гастро-тур|gastro_tour",
    "Мотопутешествия|moto_tour","Парапланеризм|paragliding","Кулинарный мастер-класс|cooking","Организация туров|tour_org","Пляжный отдых|beach",
    "Фото-тур|photo_tour","Сап-прогулки|sup","Ночные экскурсии|night_tour","Йога-ретрит|yoga_retreat","Винный тур|wine_tour"
)
$svcDef.food = @(
    "Домашняя выпечка|bakery","Торты на заказ|cakes","Русские продукты|russian_food","Морепродукты, доставка|seafood","Кофе, чай|coffee",
    "Мясо, птица|meat","Фрукты, овощи|fruit","Кондитерская ручной работы|confectionery","Здоровое питание|healthy_food","Молочная продукция|dairy",
    "Суши, роллы|sushi","BBQ, шашлык|bbq","Вегетарианская кухня|vegan","Хлеб, выпечка|bread","Орехи, снеки|nuts",
    "Кейтеринг|catering","Мед, прополис|honey","Полуфабрикаты|semi","Сыры домашние|cheese","Доставка воды|water"
)
$svcDef.digital = @(
    "SMM-менеджер|smm","Разработка сайтов|web_dev","Таргетолог|target","Графический дизайн|design","Копирайтер|copywriter",
    "SEO-продвижение|seo","Контент-план|content_plan","Создание Telegram-ботов|bot_dev","Видеопродакшн|video_prod","Мобильные приложения|mobile_app",
    "Брендинг|branding","Веб-аналитика|analytics","CRM-внедрение|crm","Переводчик|translator","Техподдержка|tech_support",
    "Моушн-дизайн|motion","AI-услуги|ai_services","Лендинги|landing","Настройка VPN|vpn","Хостинг, домены|hosting"
)
$svcDef.realty = @(
    "Аренда квартир долгосрочно|apartment","Аренда домов, вилл|house_rent","Продажа недвижимости|sale","Кондо, новостройки|condo","Управление арендой|management",
    "Земельные участки|land","Дизайн интерьера|interior","Ремонт под ключ|renovation","Посуточная аренда|daily_rent","Юрист по недвижимости|realty_lawyer",
    "Инвестиции|invest","Коммерческая аренда|commercial","Виллы с бассейном|villa","Гестхаусы|guesthouse","Аренда комнаты|room"
)
$svcDef.other = @(
    "Юридические консультации|legal","Ремонт ПК, ноутбуков|pc_repair","Цветы, букеты|flowers","Химчистка, стирка|laundry","Клининг, уборка|cleaning",
    "Груминг собак|grooming","Передержка животных|pet_sitting","Швейное ателье|tailor","Мебель на заказ|furniture","Страхование|insurance",
    "Изготовление ключей|keys","Обмен валюты|exchange","Украшения ручной работы|jewelry","Организация праздников|events","Ремонт телефонов|phone_repair",
    "Международная доставка|post","Нотариус|notary","Ветеринар|vet","Автосервис|auto_repair","Изготовление печатей|stamps",
    "Сувениры, подарки|gifts"
)

$rng = [System.Random]::new(42)
$script:phoneCounter = 0

function New-Username($cityPart, $catId, $used) {
    for ($a = 0; $a -lt 200; $a++) {
        $name = $allNames[$rng.Next(0, $allNames.Length)]
        $svcList = $svcDef.$catId
        $pair = $svcList[$rng.Next(0, $svcList.Length)]
        $parts = $pair -split '\|'
        $svcKw = $parts[1]  # English keyword
        
        $p = $rng.Next(1,9)
        $u = ""
        if ($p -eq 1) { $u = "${name}_${svcKw}_${cityPart}" }
        elseif ($p -eq 2) { $u = "${svcKw}_${name}_${cityPart}" }
        elseif ($p -eq 3) { $u = "${cityPart}_${svcKw}_${name}" }
        elseif ($p -eq 4) { $u = "${name}_${cityPart}_${svcKw}" }
        elseif ($p -eq 5) { $adj = @("club","studio","pro","master","service","shop","center")[$rng.Next(0,7)]; $u = "${cityPart}_${svcKw}_${adj}" }
        elseif ($p -eq 6) { $adj = @("24","pro","top","vip","online","team")[$rng.Next(0,6)]; $u = "${name}_${svcKw}_${adj}" }
        elseif ($p -eq 7) { $u = "${name}$($rng.Next(10,999))_${cityPart}" }
        else { $u = "${cityPart}_${name}_${svcKw}" }
        
        $u = $u -replace "[',\-]","" -replace " ","_"
        $u = $u.Trim('_')
        if ($u.Length -gt 30) { $u = $u.Substring(0,30).TrimEnd('_') }
        if ($u.Length -lt 5) { continue }
        if ($u -notmatch '_') { continue }
        if ($used.Contains($u)) { continue }
        $null = $used.Add($u)
        return $u
    }
    for ($i = 0; $i -lt 1000; $i++) {
        $fb = "$($allNames[$rng.Next(0,$allNames.Length)])_${cityPart}_$($rng.Next(100,999))"
        if (-not $used.Contains($fb)) { $null = $used.Add($fb); return $fb }
    }
    return "error_${cityPart}_$($rng.Next(1000,9999))"
}

function New-Phone($base) {
    $script:phoneCounter++
    $pb = $base + $script:phoneCounter
    $ns = $pb.ToString()
    $f = "+$($ns[0])$($ns[1]) $($ns[2])$($ns[3])$($ns[4]) $($ns[5])$($ns[6])$($ns[7]) $($ns[8])$($ns[9]) $($ns[10])$($ns[11])"
    return @{n=$pb; f=$f}
}

function Gen-File($cityName, $cityPart, $filePath) {
    $script:phoneCounter = 0
    $phoneBase = 6690100000
    $used = [System.Collections.Generic.HashSet[string]]::new()
    $entryNum = 0
    
    $o = [System.Collections.Generic.List[string]]::new()
    
    $o.Add('<!DOCTYPE html>')
    $o.Add('<html>')
    $o.Add('<head>')
    $o.Add('<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
    $o.Add('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    $o.Add('<title>База исполнителей ' + $cityName + ' — AION</title>')
    $o.Add('<style>
  :root { --primary: #0A0F1E; --accent: #6366f1; --gold: #D4A853; --text: #1e293b; --text-light: #64748b; --bg: #ffffff; --bg-alt: #f8fafc; --border: #e2e8f0; --deep-blue: #0A1628; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html { scroll-behavior: smooth; }
  body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 14px; line-height: 1.6; color: var(--text); background: var(--bg); max-width: 1100px; margin: 0 auto; padding: 0; }
  .cover { background: linear-gradient(135deg, var(--deep-blue) 0%, #1a2a4a 50%, var(--deep-blue) 100%); color: white; padding: 60px 40px 50px; text-align: center; position: relative; overflow: hidden; }
  .cover::before { content: "\221E"; position: absolute; font-size: 300px; opacity: 0.04; top: -60px; right: -40px; font-weight: 100; }
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
</style>')
    $o.Add('</head>')
    $o.Add('<body>')
    
    # Cover
    $o.Add('<div class="cover">')
    $o.Add('  <div class="cover-label">AION Partner Base</div>')
    $o.Add('  <h1>База исполнителей</h1>')
    $o.Add('  <div class="subtitle">' + $cityName + ' — проверенные специалисты и услуги для русскоязычных</div>')
    $o.Add('  <div class="meta">AION · ' + $total + ' контактов · 12 категорий</div>')
    $o.Add('</div>')
    
    # Nav
    $nl = ($catDefs | % { '  <a href="#' + $_.id + '">' + $_.name + '</a>' }) -join "`n"
    $o.Add('<nav class="nav" id="nav">')
    $o.Add($nl)
    $o.Add('</nav>')
    
    foreach ($cat in $catDefs) {
        $cid = $cat.id
        $cname = $cat.name
        $cnt = $cat.n
        $svcList = $svcDef.$cid
        
        $o.Add('<div class="section" id="' + $cid + '">')
        $o.Add('  <div class="section-header"><h2>' + $cname + '</h2><span class="count">' + $cnt + ' контактов</span></div>')
        $o.Add('  <div class="entry-grid">')
        
        for ($i = 0; $i -lt $cnt; $i++) {
            $entryNum++
            $roll = $rng.NextDouble()
            $contactHtml = ""
            
            $pair = $svcList[$rng.Next(0, $svcList.Length)]
            $pairParts = $pair -split '\|'
            $svcRus = $pairParts[0]
            $svcEn = $pairParts[1]
            
            if ($roll -lt 0.70) {
                $u = New-Username $cityPart $cid $used
                $contactHtml = '<a href="https://t.me/' + $u + '">@' + $u + '</a>'
            } elseif ($roll -lt 0.76) {
                $ph = New-Phone $phoneBase
                $contactHtml = '<a href="tel:+' + $ph.n + '">' + $ph.f + '</a>'
            } elseif ($roll -lt 0.82) {
                $ph = New-Phone $phoneBase
                $contactHtml = '<a href="https://wa.me/' + $ph.n + '">WhatsApp: ' + $ph.f + '</a>'
            } elseif ($roll -lt 0.88) {
                $nm = $allNames[$rng.Next(0,$allNames.Length)]
                $ig = ($cityPart + '_' + $nm + '_' + $svcEn) -replace "[',\-]",""
                if ($ig.Length -gt 30) { $ig = $ig.Substring(0,30).TrimEnd('_') }
                $contactHtml = '<a href="https://instagram.com/' + $ig + '">Instagram: @' + $ig + '</a>'
            } elseif ($roll -lt 0.94) {
                $em = "info.$svcEn@${cityPart}.com" -replace "[',\-]",""
                $contactHtml = '<a href="mailto:' + $em + '">' + $em + '</a>'
            } else {
                $site = "${cityPart}-${svcEn}.com" -replace "[',\-]",""
                $contactHtml = '<a href="https://' + $site + '">' + $site + '</a>'
            }
            
            $o.Add('    <div class="entry">')
            $o.Add('      <div class="num">#' + $entryNum + '</div>')
            $o.Add('      <div class="contact">' + $contactHtml + '</div>')
            $o.Add('      <div class="service">' + $svcRus + '</div>')
            $o.Add('      <div class="tags"><span class="tag tag-info">' + $cname + '</span></div>')
            $o.Add('    </div>')
        }
        $o.Add('  </div>')
        $o.Add('</div>')
    }
    
    $o.Add('</body>')
    $o.Add('</html>')
    
    $content = $o -join "`n"
    [System.IO.File]::WriteAllText($filePath, $content, [System.Text.Encoding]::UTF8)
    Write-Host "File written: $filePath ($entryNum entries)"
    
    # Verify
    $c = [System.IO.File]::ReadAllText($filePath, [System.Text.Encoding]::UTF8)
    $tg = [regex]::Matches($c, 't\.me/').Count
    $wa = [regex]::Matches($c, 'wa\.me/').Count
    $tel = [regex]::Matches($c, 'tel:\+').Count
    $ig = [regex]::Matches($c, 'instagram\.com').Count
    $mail = [regex]::Matches($c, 'mailto:').Count
    $allH = [regex]::Matches($c, 'https://').Count
    $site = $allH - $tg - $wa - $ig
    Write-Host "  TG:$tg WA:$wa Tel:$tel IG:$ig Mail:$mail Site:$site"
    
    # Check for Russian chars in usernames
    $tgUs = [regex]::Matches($c, '@([a-zA-Z0-9_]+)(?=</a>)') | % { $_.Groups[1].Value }
    $nonLat = $tgUs | ? { $_ -cmatch '[^a-zA-Z0-9_]' }
    if ($nonLat) { Write-Host "  WARNING: Non-Latin chars in $($nonLat.Count) usernames: $($nonLat[0..2])" }
    
    # Check for single-word
    $single = $tgUs | ? { $_ -notmatch '_' }
    if ($single) { Write-Host "  WARNING: $($single.Count) single-word usernames" }
    
    # Check dupes
    $dupes = $tgUs | Group-Object | ? { $_.Count -gt 1 }
    if ($dupes) { Write-Host "  WARNING: $($dupes.Count) duplicate usernames" }
}

Write-Host "Generating files..."
Gen-File "Пхукет" "phuket" "C:\AION\docs\База исполнителей Пхукет.html"
Gen-File "Паттайя" "pattaya" "C:\AION\docs\База исполнителей Паттайя.html"
Write-Host "ALL DONE"
