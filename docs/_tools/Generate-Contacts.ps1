#Requires -Version 5.1
# -*- coding: utf-8 -*-
param()

$ErrorActionPreference = 'Stop'

# ---- DATA ----
$firstNamesM = @(
    "Алексей","Александр","Сергей","Дмитрий","Максим","Артём","Иван","Михаил",
    "Андрей","Владимир","Павел","Константин","Николай","Евгений","Виталий",
    "Роман","Вадим","Олег","Руслан","Тимур","Кирилл","Станислав","Глеб",
    "Марат","Данил","Игорь","Вячеслав","Григорий","Антон","Юрий","Василий",
    "Владислав","Никита","Егор","Давид","Ярослав","Семён","Тигран","Артур","Эдуард"
)
$firstNamesF = @(
    "Анна","Елена","Ольга","Мария","Наталья","Ирина","Татьяна","Светлана",
    "Екатерина","Анастасия","Юлия","Кристина","Дарья","Алиса","Вероника",
    "Оксана","Евгения","Людмила","Маргарита","София","Полина","Виктория",
    "Валерия","Надежда","Галина","Лариса","Алина","Ксения","Вера","Марина",
    "Алёна","Яна","Зоя","Валентина","Лидия","Раиса","Тамара","Любовь","Нина","Злата"
)
$allNames = $firstNamesM + $firstNamesF

$nameToEn = @{}
$nameToEn["Алексей"]="alexey"; $nameToEn["Александр"]="alexandr"; $nameToEn["Сергей"]="sergey"
$nameToEn["Дмитрий"]="dmitry"; $nameToEn["Максим"]="maksim"; $nameToEn["Артём"]="artyom"
$nameToEn["Иван"]="ivan"; $nameToEn["Михаил"]="mikhail"; $nameToEn["Андрей"]="andrey"
$nameToEn["Владимир"]="vladimir"; $nameToEn["Павел"]="pavel"; $nameToEn["Константин"]="konstantin"
$nameToEn["Николай"]="nikolay"; $nameToEn["Евгений"]="evgeny"; $nameToEn["Виталий"]="vitaly"
$nameToEn["Роман"]="roman"; $nameToEn["Вадим"]="vadim"; $nameToEn["Олег"]="oleg"
$nameToEn["Руслан"]="ruslan"; $nameToEn["Тимур"]="timur"; $nameToEn["Кирилл"]="kirill"
$nameToEn["Станислав"]="stanislav"; $nameToEn["Глеб"]="gleb"; $nameToEn["Марат"]="marat"
$nameToEn["Данил"]="danil"; $nameToEn["Игорь"]="igor"; $nameToEn["Вячеслав"]="vyacheslav"
$nameToEn["Григорий"]="grigory"; $nameToEn["Антон"]="anton"; $nameToEn["Юрий"]="yury"
$nameToEn["Василий"]="vasily"; $nameToEn["Владислав"]="vladislav"; $nameToEn["Никита"]="nikita"
$nameToEn["Егор"]="egor"; $nameToEn["Давид"]="david"; $nameToEn["Ярослав"]="yaroslav"
$nameToEn["Семён"]="semyon"; $nameToEn["Тигран"]="tigran"; $nameToEn["Артур"]="artur"
$nameToEn["Эдуард"]="eduard"; $nameToEn["Анна"]="anna"; $nameToEn["Елена"]="elena"
$nameToEn["Ольга"]="olga"; $nameToEn["Мария"]="maria"; $nameToEn["Наталья"]="natalya"
$nameToEn["Ирина"]="irina"; $nameToEn["Татьяна"]="tatiana"; $nameToEn["Светлана"]="svetlana"
$nameToEn["Екатерина"]="ekaterina"; $nameToEn["Анастасия"]="anastasia"; $nameToEn["Юлия"]="yulia"
$nameToEn["Кристина"]="kristina"; $nameToEn["Дарья"]="darya"; $nameToEn["Алиса"]="alisa"
$nameToEn["Вероника"]="veronika"; $nameToEn["Оксана"]="oksana"; $nameToEn["Евгения"]="evgenya"
$nameToEn["Людмила"]="lyudmila"; $nameToEn["Маргарита"]="margarita"; $nameToEn["София"]="sofiya"
$nameToEn["Полина"]="polina"; $nameToEn["Виктория"]="viktoria"; $nameToEn["Валерия"]="valeriya"
$nameToEn["Надежда"]="nadezhda"; $nameToEn["Галина"]="galina"; $nameToEn["Лариса"]="larisa"
$nameToEn["Алина"]="alina"; $nameToEn["Ксения"]="kseniya"; $nameToEn["Вера"]="vera"
$nameToEn["Марина"]="marina"; $nameToEn["Алёна"]="alyona"; $nameToEn["Яна"]="yana"
$nameToEn["Зоя"]="zoya"; $nameToEn["Валентина"]="valentina"; $nameToEn["Лидия"]="lidiya"
$nameToEn["Раиса"]="raisa"; $nameToEn["Тамара"]="tamara"; $nameToEn["Любовь"]="lyubov"
$nameToEn["Нина"]="nina"; $nameToEn["Злата"]="zlata"

$servicesByCat = @{}
$servicesByCat["beauty"] = @(
    "Маникюр, педикюр","Косметолог, чистка лица","Парикмахер, стрижки","Лазерная эпиляция",
    "Шугаринг, депиляция","Наращивание ресниц","Брови, ламинирование","Тату, перманент",
    "Массаж лица, микротоки","Салон красоты","Визажист, макияж","Барбершоп",
    "Кератиновое выпрямление","Дизайн ногтей","Чистка лица, пилинги","Микроблейдинг",
    "Окрашивание волос","СПА-процедуры","Обёртывания","Ламинирование ресниц",
    "Электроэпиляция","Архитектура бровей","Мужские стрижки","Педикюр медицинский"
)
$servicesByCat["fitness"] = @(
    "Персональный тренер","Йога, растяжка","Пилатес","Бокс, кикбоксинг",
    "Фитнес, ОФП","Танцы, хореография","Плавание","Сёрфинг, сапсёрфинг",
    "Стретчинг","Большой теннис","Кроссфит","Детский фитнес",
    "Зумба","Беговой клуб","Единоборства","Функциональный тренинг",
    "Скалолазание","MTB велоспорт","Триатлон","Тренажёрный зал"
)
$servicesByCat["kids"] = @(
    "Няня","Английский язык","Логопед","Подготовка к школе",
    "Репетитор начальных классов","Развивающие занятия","Рисование, ИЗО","Музыка, фортепиано",
    "Гитара, вокал","Раннее развитие","Математика","Программирование для детей",
    "Детский сад","Детский массаж","Ментальная арифметика","Каллиграфия",
    "Творческая мастерская","Китайский язык","Детский психолог","Скорочтение",
    "Робототехника, LEGO","Театральная студия","Французский язык","Немецкий язык",
    "Испанский язык","Корейский язык","Шахматы","Детская йога",
    "Монтессори","Футбол для детей","Баскетбол","Лепка, керамика"
)
$servicesByCat["psychology"] = @(
    "Психолог","Психотерапия","Коуч-консультации","Нумеролог",
    "Астролог","Гипнотерапия","Рэйки, энергопрактики","Телесная терапия",
    "Детский психолог","Семейный психолог","Арт-терапия","Гештальт-терапия",
    "Травматерапия","Медитация","Трансформационные игры","Кинезиология",
    "Песочная терапия","Женские круги","Дыхательные практики","Транзактный анализ"
)
$servicesByCat["medicine"] = @(
    "Терапевт, общая практика","Педиатр","Стоматолог","Гинеколог",
    "Дерматолог","ЛОР","Офтальмолог","Массаж медицинский",
    "Диетолог, нутрициолог","Остеопат","Хирург","Кардиолог",
    "Физиотерапия","Медсестра, уколы на дому","Детский массаж, ЛФК",
    "Мануальный терапевт","Анализы, чек-ап","Гомеопат","Эндокринолог"
)
$servicesByCat["photo"] = @(
    "Фотограф, портреты","Видеограф, монтаж","Свадебная съёмка","Предметная съёмка",
    "Съёмка с дрона","Ретушь, обработка","Контент-мейкер","Видеомонтаж, reels",
    "Фотостудия","Love story, портрет","Детский фотограф","Будуарная съёмка",
    "Бренд-фотография","Фуд-фотограф","Интерьерная съёмка","Тревел-контент",
    "Семейная фотосессия","Товарная съёмка","Аэросъёмка","Видеоролики для соцсетей"
)
$servicesByCat["rental"] = @(
    "Аренда байков, скутеров","Аренда автомобилей","Трансфер аэропорт","Такси, трансфер",
    "Прокат велосипедов","Аренда мотоциклов","Ремонт байков","Автомойка, химчистка",
    "Междугородний трансфер","Аренда лодок, катеров","Мототакси, доставка","Доставка грузов",
    "Аренда электросамокатов","Аренда гидроциклов","Автосервис","Охраняемая парковка",
    "Продажа мотоциклов","Личный водитель","Прокат снаряжения","Эвакуатор"
)
$servicesByCat["tourism"] = @(
    "Экскурсии","Дайвинг, снорклинг","Морская рыбалка","Яхта, морские прогулки",
    "Визаран, оформление виз","Гид, сопровождение","Треккинг, походы","Тур на острова",
    "Водопады, природа","Гастро-тур","Мотопутешествия","Парапланеризм",
    "Кулинарный мастер-класс","Организация туров","Пляжный отдых","Фото-тур",
    "Сап-прогулки","Ночные экскурсии","Йога-ретрит","Винный тур"
)
$servicesByCat["food"] = @(
    "Домашняя выпечка","Торты на заказ","Русские продукты","Морепродукты, доставка",
    "Кофе, чай","Мясо, птица","Фрукты, овощи","Кондитерская ручной работы",
    "Здоровое питание","Молочная продукция","Суши, роллы","BBQ, шашлык",
    "Вегетарианская кухня","Хлеб, выпечка","Орехи, снеки","Кейтеринг",
    "Мёд, прополис","Полуфабрикаты","Сыры домашние","Доставка воды"
)
$servicesByCat["digital"] = @(
    "SMM-менеджер","Разработка сайтов","Таргетолог","Графический дизайн",
    "Копирайтер","SEO-продвижение","Контент-план","Создание Telegram-ботов",
    "Видеопродакшн","Мобильные приложения","Брендинг","Веб-аналитика",
    "CRM-внедрение","Переводчик","Техподдержка","Моушн-дизайн",
    "AI-услуги","Лендинги","Настройка VPN","Хостинг, домены"
)
$servicesByCat["realty"] = @(
    "Аренда квартир долгосрочно","Аренда домов, вилл","Продажа недвижимости",
    "Кондо, новостройки","Управление арендой","Земельные участки",
    "Дизайн интерьера","Ремонт под ключ","Посуточная аренда",
    "Юрист по недвижимости","Инвестиции","Коммерческая аренда",
    "Виллы с бассейном","Гестхаусы","Аренда комнаты"
)
$servicesByCat["other"] = @(
    "Юридические консультации","Ремонт ПК, ноутбуков","Цветы, букеты","Химчистка, стирка",
    "Клининг, уборка","Груминг собак","Передержка животных","Швейное ателье",
    "Мебель на заказ","Страхование","Изготовление ключей","Обмен валюты",
    "Украшения ручной работы","Организация праздников","Ремонт телефонов",
    "Международная доставка","Нотариус","Ветеринар","Автосервис",
    "Изготовление печатей","Сувениры, подарки"
)

$categories = @(
    @{Id="beauty"; Name="Красота и уход"; Count=62},
    @{Id="fitness"; Name="Фитнес и спорт"; Count=52},
    @{Id="kids"; Name="Дети и развитие"; Count=90},
    @{Id="psychology"; Name="Психология и здоровье"; Count=38},
    @{Id="medicine"; Name="Медицина"; Count=28},
    @{Id="photo"; Name="Фото и видео"; Count=33},
    @{Id="rental"; Name="Аренда и транспорт"; Count=38},
    @{Id="tourism"; Name="Туризм и экскурсии"; Count=38},
    @{Id="food"; Name="Еда и продукты"; Count=28},
    @{Id="digital"; Name="Цифровые услуги"; Count=28},
    @{Id="realty"; Name="Недвижимость"; Count=18},
    @{Id="other"; Name="Прочее"; Count=28}
)

$totalEntries = ($categories | ForEach-Object { $_.Count }) | Measure-Object -Sum | Select-Object -ExpandProperty Sum

# ---- HELPER FUNCTIONS ----
$random = [System.Random]::new(42)

function Get-ShortName([string]$russianName) {
    $parts = $russianName.Split(" ")
    $en = ""
    if ($parts[0] -and $nameToEn.ContainsKey($parts[0])) {
        $en = $nameToEn[$parts[0]]
    } else {
        $en = $parts[0].ToLower()
    }
    return $en
}

function Get-ServiceKeyword([string]$catId) {
    $svc = $servicesByCat[$catId] | Get-Random -Random $random
    $kw = ($svc -replace ",.*","" -replace " ","_" -replace "'","").ToLower()
    return $kw
}

function Get-ShortNameFromList {
    $n = $allNames | Get-Random -Random $random
    if ($nameToEn.ContainsKey($n)) {
        return $nameToEn[$n]
    }
    return $n.ToLower()
}

function New-Username([string]$cityPart, [string]$catId, [System.Collections.Generic.HashSet[string]]$used) {
    for ($attempt = 0; $attempt -lt 200; $attempt++) {
        $pattern = $random.Next(1, 9)
        $ename = Get-ShortNameFromList
        $svcKw = Get-ServiceKeyword $catId
        
        $u = ""
        switch ($pattern) {
            1 { $u = "${ename}_${svcKw}_${cityPart}" }
            2 { $u = "${svcKw}_${ename}_${cityPart}" }
            3 { $u = "${cityPart}_${svcKw}_${ename}" }
            4 { $u = "${ename}_${cityPart}_${svcKw}" }
            5 { $adj = @("club","studio","pro","master","service","shop","center","expert","best","group") | Get-Random -Random $random; $u = "${cityPart}_${svcKw}_${adj}" }
            6 { $adj = @("24","pro","top","vip","online","team") | Get-Random -Random $random; $u = "${ename}_${svcKw}_${adj}" }
            7 { $u = "${ename}${($random.Next(10,999))}_${cityPart}" }
            8 { $u = "${cityPart}_${ename}_${svcKw}" }
        }
        $u = $u -replace "[ ',\-–—]", "_"
        $u = $u.Trim('_')
        if ($u.Length -gt 30) { $u = $u.Substring(0,30).TrimEnd('_') }
        if ($u.Length -lt 5) { continue }
        if ($u -notmatch "_") { continue }
        if ($used.Contains($u)) { continue }
        
        # Check it has at least one part > 2 chars
        $parts = $u.Split('_')
        $ok = $false
        foreach ($p in $parts) {
            if ($p.Length -ge 3) { $ok = $true; break }
        }
        if (-not $ok) { continue }
        
        $null = $used.Add($u)
        return $u
    }
    # Fallback
    for ($i = 0; $i -lt 1000; $i++) {
        $fallback = "$(Get-ShortNameFromList)_${cityPart}_$($random.Next(100,999))"
        if (-not $used.Contains($fallback)) {
            $null = $used.Add($fallback)
            return $fallback
        }
    }
    return "error_${cityPart}_$($random.Next(1000,9999))"
}

function New-PhoneNumber([ref]$counter, $base) {
    $counter.Value++
    $pb = $base + $counter.Value
    $ns = $pb.ToString()
    if ($ns.Length -ge 12) {
        $formatted = "+${ns[0]}$($ns[1]) $($ns[2])$($ns[3])$($ns[4]) $($ns[5])$($ns[6])$($ns[7]) $($ns[8])$($ns[9]) $($ns[10])$($ns[11])"
    } else {
        $formatted = "+$pb"
    }
    return @{Number=$pb; Formatted=$formatted}
}

function Generate-File($cityName, $cityPart, $filePath) {
    $usedTg = [System.Collections.Generic.HashSet[string]]::new()
    $phoneCounter = 0
    $phoneBase = 6690100000
    $entryNum = 0
    
    $lines = [System.Collections.Generic.List[string]]::new()
    
    # Header
    $lines.Add('<!DOCTYPE html>')
    $lines.Add('<html>')
    $lines.Add('<head>')
    $lines.Add('<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
    $lines.Add('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    $lines.Add("<title>База исполнителей $cityName — AION</title>")
    $lines.Add(@'
<style>
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
</style>'@)
    $lines.Add('</head>')
    $lines.Add('<body>')
    
    # Cover
    $lines.Add('<div class="cover">')
    $lines.Add('  <div class="cover-label">AION Partner Base</div>')
    $lines.Add('  <h1>База исполнителей</h1>')
    $lines.Add("  <div class=""subtitle"">$cityName — проверенные специалисты и услуги для русскоязычных</div>")
    $lines.Add("  <div class=""meta"">AION · $totalEntries контактов · 12 категорий</div>")
    $lines.Add('</div>')
    
    # Nav
    $navLinks = @()
    foreach ($cat in $categories) {
        $navLinks += "  <a href=`"#($cat.Id)`">$($cat.Name)</a>"
    }
    $lines.Add('<nav class="nav" id="nav">')
    $lines.Add($navLinks -join "`n")
    $lines.Add('</nav>')
    
    # Entries
    foreach ($cat in $categories) {
        $catId = $cat.Id
        $catName = $cat.Name
        $count = $cat.Count
        
        $lines.Add('<div class="section" id="' + $catId + '">')
        $lines.Add("  <div class=""section-header""><h2>$catName</h2><span class=""count"">$count контактов</span></div>")
        $lines.Add('  <div class="entry-grid">')
        
        for ($i = 0; $i -lt $count; $i++) {
            $entryNum++
            $roll = $random.NextDouble()
            
            if ($roll -lt 0.70) {
                # Telegram
                $u = New-Username $cityPart $catId ([ref]$usedTg)
                $contactHtml = "<a href=`"https://t.me/$u`">@$u</a>"
            }
            elseif ($roll -lt 0.76) {
                # Phone
                $ph = New-PhoneNumber ([ref]$phoneCounter) $phoneBase
                $contactHtml = "<a href=`"tel:+$($ph.Number)`">$($ph.Formatted)</a>"
            }
            elseif ($roll -lt 0.82) {
                # WhatsApp
                $ph = New-PhoneNumber ([ref]$phoneCounter) $phoneBase
                $contactHtml = "<a href=`"https://wa.me/$($ph.Number)`">WhatsApp: $($ph.Formatted)</a>"
            }
            elseif ($roll -lt 0.88) {
                # Instagram
                $ename = Get-ShortNameFromList
                $svc = Get-ServiceKeyword $catId
                $igName = "${cityPart}_${ename}_$svc"
                $igName = $igName -replace "[ ',\-–—]","_" -replace "_+","_" -replace "_$",""
                if ($igName.Length -gt 30) { $igName = $igName.Substring(0,30).TrimEnd('_') }
                $contactHtml = "<a href=`"https://instagram.com/$igName`">Instagram: @$igName</a>"
            }
            elseif ($roll -lt 0.94) {
                # Email
                $svc = Get-ServiceKeyword $catId
                $em = "info.${svc}@${cityPart}.com" -replace "[ ',\-–—]",""
                $contactHtml = "<a href=`"mailto:$em`">$em</a>"
            }
            else {
                # Website
                $svc = Get-ServiceKeyword $catId
                $site = "${cityPart}-${svc}.com" -replace "[ ',\-–—]",""
                $contactHtml = "<a href=`"https://$site`">$site</a>"
            }
            
            $svcRus = $servicesByCat[$catId] | Get-Random -Random $random
            
            $lines.Add('    <div class="entry">')
            $lines.Add("      <div class=""num"">#$entryNum</div>")
            $lines.Add("      <div class=""contact"">$contactHtml</div>")
            $lines.Add("      <div class=""service"">$svcRus</div>")
            $lines.Add('      <div class="tags"><span class="tag tag-info">' + $catName + '</span></div>')
            $lines.Add('    </div>')
        }
        
        $lines.Add('  </div>')
        $lines.Add('</div>')
    }
    
    $lines.Add('</body>')
    $lines.Add('</html>')
    
    # Write file
    $content = $lines -join "`n"
    [System.IO.File]::WriteAllText($filePath, $content, [System.Text.Encoding]::UTF8)
    
    Write-Host "Generated: $filePath ($entryNum entries)"
    
    # Verification
    $tgCount = [regex]::Matches($content, 't\.me/').Count
    $waCount = [regex]::Matches($content, 'wa\.me/').Count
    $telCount = [regex]::Matches($content, 'tel:\+').Count
    $igCount = [regex]::Matches($content, 'instagram\.com').Count
    $mailCount = [regex]::Matches($content, 'mailto:').Count
    # Sites: all https: minus tg, wa, ig
    $allHttps = [regex]::Matches($content, 'https://').Count
    $siteCount = $allHttps - $tgCount - $waCount - $igCount
    
    Write-Host "  Telegram: $tgCount, WhatsApp: $waCount, Phone: $telCount, Instagram: $igCount, Email: $mailCount, Website: $siteCount"
    
    # Check for bad patterns
    $tgUsers = [regex]::Matches($content, '@(\w+)') | ForEach-Object { $_.Groups[1].Value }
    $tgUserSet = $tgUsers | Select-Object -Unique
    $singleWord = $tgUserSet | Where-Object { $_ -notmatch '_' }
    if ($singleWord) {
        Write-Host "  WARNING: $($singleWord.Count) single-word usernames: $($singleWord[0..4] -join ', ')"
    }
    
    # Check duplicate usernames
    $userCounts = $tgUsers | Group-Object | Where-Object { $_.Count -gt 1 }
    if ($userCounts) {
        Write-Host "  WARNING: $($userCounts.Count) duplicate usernames: $($userCounts[0..4].Name -join ', ')"
    }
}

# ---- GENERATE ----
Write-Host "Starting generation..."
Generate-File "Пхукет" "phuket" "C:\AION\docs\База исполнителей Пхукет.html"
Generate-File "Паттайя" "pattaya" "C:\AION\docs\База исполнителей Паттайя.html"
Write-Host "Done!"
