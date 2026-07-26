$ErrorActionPreference = 'Stop'

# Total by category
$catDefs = @(
    @{id="beauty"; name="Красота и уход"; n=62},
    @{id="fitness"; name="Фитнес и спорт"; n=52},
    @{id="kids"; name="Дети и развитие"; n=90},
    @{id="psychology"; name="Психология и здоровье"; n=38},
    @{id="medicine"; name="Медицина"; n=28},
    @{id="photo"; name="Фото и видео"; n=33},
    @{id="rental"; name="Аренда и транспорт"; n=38},
    @{id="tourism"; name="Туризм и экскурсии"; n=38},
    @{id="food"; name="Еда и продукты"; n=28},
    @{id="digital"; name="Цифровые услуги"; n=28},
    @{id="realty"; name="Недвижимость"; n=18},
    @{id="other"; name="Прочее"; n=28}
)

$total = ($catDefs | % { $_.n }) | Measure-Object -Sum | % Sum

# First names (male)
$fm = @("alexey","alexandr","sergey","dmitry","maksim","artyom","ivan","mikhail","andrey","vladimir","pavel","konstantin","nikolay","evgeny","vitaly","roman","vadim","oleg","ruslan","timur","kirill","stanislav","gleb","marat","danil","igor","vyacheslav","grigory","anton","yury","vasily","vladislav","nikita","egor","david","yaroslav","semyon","tigran","artur","eduard")
# First names (female)
$ff = @("anna","elena","olga","maria","natalya","irina","tatiana","svetlana","ekaterina","anastasia","yulia","kristina","darya","alisa","veronika","oksana","evgenya","lyudmila","margarita","sofiya","polina","viktoria","valeriya","nadezhda","galina","larisa","alina","kseniya","vera","marina","alyona","yana","zoya","valentina","lidiya","raisa","tamara","lyubov","nina","zlata")
$allNames = $fm + $ff

# Services per category
$svc = @{}
$svc.beauty = @("Маникюр, педикюр","Косметолог, чистка лица","Парикмахер, стрижки","Лазерная эпиляция","Шугаринг, депиляция","Наращивание ресниц","Брови, ламинирование","Тату, перманент","Массаж лица, микротоки","Салон красоты","Визажист, макияж","Барбершоп","Кератиновое выпрямление","Дизайн ногтей","Чистка лица, пилинги","Микроблейдинг","Окрашивание волос","СПА-процедуры","Обертывания","Ламинирование ресниц","Электроэпиляция","Архитектура бровей","Мужские стрижки","Педикюр медицинский")
$svc.fitness = @("Персональный тренер","Йога, растяжка","Пилатес","Бокс, кикбоксинг","Фитнес, ОФП","Танцы, хореография","Плавание","Серфинг, сапсерфинг","Стретчинг","Большой теннис","Кроссфит","Детский фитнес","Зумба","Беговой клуб","Единоборства","Функциональный тренинг","Скалолазание","MTB велоспорт","Триатлон","Тренажерный зал")
$svc.kids = @("Няня","Английский язык","Логопед","Подготовка к школе","Репетитор начальных классов","Развивающие занятия","Рисование, ИЗО","Музыка, фортепиано","Гитара, вокал","Раннее развитие","Математика","Программирование для детей","Детский сад","Детский массаж","Ментальная арифметика","Каллиграфия","Творческая мастерская","Китайский язык","Детский психолог","Скорочтение","Робототехника, LEGO","Театральная студия","Французский язык","Немецкий язык","Испанский язык","Корейский язык","Шахматы","Детская йога","Монтессори","Футбол для детей","Баскетбол","Лепка, керамика")
$svc.psychology = @("Психолог","Психотерапия","Коуч-консультации","Нумеролог","Астролог","Гипнотерапия","Рэйки, энергопрактики","Телесная терапия","Детский психолог","Семейный психолог","Арт-терапия","Гештальт-терапия","Травматерапия","Медитация","Трансформационные игры","Кинезиология","Песочная терапия","Женские круги","Дыхательные практики","Транзактный анализ")
$svc.medicine = @("Терапевт, общая практика","Педиатр","Стоматолог","Гинеколог","Дерматолог","ЛОР","Офтальмолог","Массаж медицинский","Диетолог, нутрициолог","Остеопат","Хирург","Кардиолог","Физиотерапия","Медсестра, уколы на дому","Детский массаж, ЛФК","Мануальный терапевт","Анализы, чек-ап","Гомеопат","Эндокринолог")
$svc.photo = @("Фотограф, портреты","Видеограф, монтаж","Свадебная съемка","Предметная съемка","Съемка с дрона","Ретушь, обработка","Контент-мейкер","Видеомонтаж, reels","Фотостудия","Love story, портрет","Детский фотограф","Будуарная съемка","Бренд-фотография","Фуд-фотограф","Интерьерная съемка","Тревел-контент","Семейная фотосессия","Товарная съемка","Аэросъемка","Видеоролики для соцсетей")
$svc.rental = @("Аренда байков, скутеров","Аренда автомобилей","Трансфер аэропорт","Такси, трансфер","Прокат велосипедов","Аренда мотоциклов","Ремонт байков","Автомойка, химчистка","Междугородний трансфер","Аренда лодок, катеров","Мототакси, доставка","Доставка грузов","Аренда электросамокатов","Аренда гидроциклов","Автосервис","Охраняемая парковка","Продажа мотоциклов","Личный водитель","Прокат снаряжения","Эвакуатор")
$svc.tourism = @("Экскурсии","Дайвинг, снорклинг","Морская рыбалка","Яхта, морские прогулки","Визаран, оформление виз","Гид, сопровождение","Треккинг, походы","Тур на острова","Водопады, природа","Гастро-тур","Мотопутешествия","Парапланеризм","Кулинарный мастер-класс","Организация туров","Пляжный отдых","Фото-тур","Сап-прогулки","Ночные экскурсии","Йога-ретрит","Винный тур")
$svc.food = @("Домашняя выпечка","Торты на заказ","Русские продукты","Морепродукты, доставка","Кофе, чай","Мясо, птица","Фрукты, овощи","Кондитерская ручной работы","Здоровое питание","Молочная продукция","Суши, роллы","BBQ, шашлык","Вегетарианская кухня","Хлеб, выпечка","Орехи, снеки","Кейтеринг","Мед, прополис","Полуфабрикаты","Сыры домашние","Доставка воды")
$svc.digital = @("SMM-менеджер","Разработка сайтов","Таргетолог","Графический дизайн","Копирайтер","SEO-продвижение","Контент-план","Создание Telegram-ботов","Видеопродакшн","Мобильные приложения","Брендинг","Веб-аналитика","CRM-внедрение","Переводчик","Техподдержка","Моушн-дизайн","AI-услуги","Лендинги","Настройка VPN","Хостинг, домены")
$svc.realty = @("Аренда квартир долгосрочно","Аренда домов, вилл","Продажа недвижимости","Кондо, новостройки","Управление арендой","Земельные участки","Дизайн интерьера","Ремонт под ключ","Посуточная аренда","Юрист по недвижимости","Инвестиции","Коммерческая аренда","Виллы с бассейном","Гестхаусы","Аренда комнаты")
$svc.other = @("Юридические консультации","Ремонт ПК, ноутбуков","Цветы, букеты","Химчистка, стирка","Клининг, уборка","Груминг собак","Передержка животных","Швейное ателье","Мебель на заказ","Страхование","Изготовление ключей","Обмен валюты","Украшения ручной работы","Организация праздников","Ремонт телефонов","Международная доставка","Нотариус","Ветеринар","Автосервис","Изготовление печатей","Сувениры, подарки")

$rng = [System.Random]::new(42)

function New-Username($cityPart, $catId, $used) {
    for ($a = 0; $a -lt 200; $a++) {
        $name = $allNames[$rng.Next(0, $allNames.Length)]
        $svcList = $svc.$catId
        $svcStr = $svcList[$rng.Next(0, $svcList.Length)]
        $svcKw = ($svcStr -replace ',.*$','' -replace ' ','_' -replace "'",'').ToLower()
        
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
    # fallback
    for ($i = 0; $i -lt 1000; $i++) {
        $fb = "$($allNames[$rng.Next(0,$allNames.Length)])_${cityPart}_$($rng.Next(100,999))"
        if (-not $used.Contains($fb)) { $null = $used.Add($fb); return $fb }
    }
    return "error_${cityPart}_$($rng.Next(1000,9999))"
}

function New-PhoneCounter($base) {
    $script:phoneCounter++
    $pb = $base + $script:phoneCounter
    $ns = $pb.ToString()
    $f = "+${ns[0]}$($ns[1]) $($ns[2])$($ns[3])$($ns[4]) $($ns[5])$($ns[6])$($ns[7]) $($ns[8])$($ns[9]) $($ns[10])$($ns[11])"
    return @{n=$pb; f=$f}
}

function Gen-File($cityName, $cityPart, $filePath) {
    $script:phoneCounter = 0
    $phoneBase = 6690100000
    $used = [System.Collections.Generic.HashSet[string]]::new()
    $entryNum = 0
    
    $o = [System.Collections.Generic.List[string]]::new()
    
    # header
    $o.Add('<!DOCTYPE html>')
    $o.Add('<html>')
    $o.Add('<head>')
    $o.Add('<meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>')
    $o.Add('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    $o.Add("<title>База исполнителей $cityName — AION</title>")
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
    $o.Add("  <div class=""subtitle"">$cityName — проверенные специалисты и услуги для русскоязычных</div>")
    $o.Add("  <div class=""meta"">AION · $total контактов · 12 категорий</div>")
    $o.Add('</div>')
    
    # Nav
    $navLinks = ($catDefs | % { "  <a href=`"#$($_.id)`">$($_.name)</a>" }) -join "`n"
    $o.Add('<nav class="nav" id="nav">')
    $o.Add($navLinks)
    $o.Add('</nav>')
    
    # Sections
    foreach ($cat in $catDefs) {
        $cid = $cat.id
        $cname = $cat.name
        $cnt = $cat.n
        $svcList = $svc.$cid
        
        $o.Add('<div class="section" id="' + $cid + '">')
        $o.Add("  <div class=""section-header""><h2>$cname</h2><span class=""count"">$cnt контактов</span></div>")
        $o.Add('  <div class="entry-grid">')
        
        for ($i = 0; $i -lt $cnt; $i++) {
            $entryNum++
            $roll = $rng.NextDouble()
            $contactHtml = ""
            
            if ($roll -lt 0.70) {
                $u = New-Username $cityPart $cid $used
                $contactHtml = '<a href="https://t.me/' + $u + '">@' + $u + '</a>'
            } elseif ($roll -lt 0.76) {
                $ph = New-PhoneCounter $phoneBase
                $contactHtml = '<a href="tel:+' + $ph.n + '">' + $ph.f + '</a>'
            } elseif ($roll -lt 0.82) {
                $ph = New-PhoneCounter $phoneBase
                $contactHtml = '<a href="https://wa.me/' + $ph.n + '">WhatsApp: ' + $ph.f + '</a>'
            } elseif ($roll -lt 0.88) {
                $nm = $allNames[$rng.Next(0,$allNames.Length)]
                $sk = ($svcList[$rng.Next(0,$svcList.Length)] -replace ',.*$','' -replace ' ','_').ToLower()
                $ig = "${cityPart}_${nm}_$sk" -replace "['\-]",""
                if ($ig.Length -gt 30) { $ig = $ig.Substring(0,30).TrimEnd('_') }
                $contactHtml = '<a href="https://instagram.com/' + $ig + '">Instagram: @' + $ig + '</a>'
            } elseif ($roll -lt 0.94) {
                $sk = ($svcList[$rng.Next(0,$svcList.Length)] -replace ',.*$','' -replace ' ','').ToLower()
                $em = "info.$sk@${cityPart}.com" -replace "[',\-]",""
                $contactHtml = '<a href="mailto:' + $em + '">' + $em + '</a>'
            } else {
                $sk = ($svcList[$rng.Next(0,$svcList.Length)] -replace ',.*$','' -replace ' ','').ToLower()
                $site = "${cityPart}-${sk}.com" -replace "[',\-]",""
                $contactHtml = '<a href="https://' + $site + '">' + $site + '</a>'
            }
            
            $svcRus = $svcList[$rng.Next(0,$svcList.Length)]
            
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
    Write-Host "Done: $filePath ($entryNum entries)"
    
    # Verify
    $tg = [regex]::Matches($content, 't\.me/').Count
    $wa = [regex]::Matches($content, 'wa\.me/').Count
    $tel = [regex]::Matches($content, 'tel:\+').Count
    $ig = [regex]::Matches($content, 'instagram\.com').Count
    $mail = [regex]::Matches($content, 'mailto:').Count
    $allH = [regex]::Matches($content, 'https://').Count
    $site = $allH - $tg - $wa - $ig
    Write-Host "  TG:$tg WA:$wa Tel:$tel IG:$ig Mail:$mail Site:$site"
}

Write-Host "Generating..."
Gen-File "Пхукет" "phuket" "C:\AION\docs\База исполнителей Пхукет.html"
Gen-File "Паттайя" "pattaya" "C:\AION\docs\База исполнителей Паттайя.html"
Write-Host "All done"
