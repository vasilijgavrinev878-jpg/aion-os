import https from 'https';
import fs from 'fs';

function fetch(url) {
  return new Promise((resolve, reject) => {
    https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' } }, res => {
      let d = '';
      res.on('data', c => d += c);
      res.on('end', () => resolve(d));
    }).on('error', reject);
  });
}

function extractListingUrls(html) {
  const regex = /href="(https:\/\/dubiznes\.ae\/listing\/[^\/]+\/)"/g;
  const urls = [...html.matchAll(regex)].map(m => m[1]);
  return [...new Set(urls)];
}

function findPhoneNumbers(html) {
  const phones = [];
  const telRegex = /tel:\+?971([0-9\-]{7,12})/g;
  let m;
  while ((m = telRegex.exec(html)) !== null) {
    const num = '+971' + m[1].replace(/-/g, '');
    if (!phones.includes(num)) phones.push(num);
  }
  const directRegex = /(\+971[0-9]{7,12})/g;
  while ((m = directRegex.exec(html)) !== null) {
    if (!phones.includes(m[1])) phones.push(m[1]);
  }
  return phones;
}

function extractName(html) {
  // Try breadcrumb with vnsco-breadcrumbs class
  const bcNav = html.match(/<nav[^>]*class="[^"]*vnsco-breadcrumbs[^"]*"[^>]*>[\s\S]{0,500}?<\/nav>/);
  if (bcNav) {
    const spans = bcNav[0].match(/<span[^>]*>([^<]+)<\/span>/g);
    if (spans) {
      const texts = spans.map(s => s.replace(/<[^>]*>/g, '').trim()).filter(t => t !== '\u2192');
      if (texts.length > 0) return texts[texts.length - 1];
    }
  }
  // Fallback to title
  const titleMatch = html.match(/<title>([^<]+)<\/title>/);
  if (titleMatch) {
    let t = titleMatch[1].replace(/ - dubiznes\.ae$/i, '');
    t = t.replace(/\s*[—–-]\s*.*$/, '');
    t = t.replace(/ в Дубае.*$/, '');
    t = t.replace(/ в ОАЭ.*$/, '');
    t = t.replace(/ в самом сердце.*$/, '');
    return t.trim();
  }
  return null;
}

async function scrapeAllPages(cat) {
  const allUrls = [];
  let page = 1;
  let hasMore = true;
  while (hasMore) {
    const url = page === 1
      ? `https://dubiznes.ae/listing-category/${cat}/`
      : `https://dubiznes.ae/listing-category/${cat}/page/${page}/`;
    const html = await fetch(url);
    const urls = extractListingUrls(html);
    urls.forEach(u => { if (!allUrls.includes(u)) allUrls.push(u); });
    const nextLink = html.match(/<link rel="next"[^>]*href="([^"]+)"/);
    if (nextLink && nextLink[1].includes('/page/' + (page + 1) + '/')) {
      page++;
    } else {
      hasMore = false;
    }
  }
  return allUrls;
}

async function main() {
  const categories = [
    'restaurants', 'fitness', 'education', 'healthcare', 'real-estate',
    'spa', 'clubs-bars', 'avtomasterskie-i-deteiling', 'organizatsii',
    'gamingclubs', 'massage', 'uslugi-krasoti-v-oae', 'rentacar',
    'russkiye-magazini-v-oae', 'meditsina', 'it-uslugi', 'manikiur-pedikiur', 'fotograf'
  ];

  // Step 1: Collect all listing URLs
  const allListingUrls = [];
  for (const cat of categories) {
    process.stdout.write( cat + '... ');
    const urls = await scrapeAllPages(cat);
    console.log(urls.length);
    urls.forEach(u => { if (!allListingUrls.includes(u)) allListingUrls.push(u); });
  }
  console.log('\nTotal unique URLs:', allListingUrls.length);
  fs.writeFileSync('dubiznes_listing_urls.json', JSON.stringify(allListingUrls, null, 2));

  // Step 2: Scrape each listing
  const results = [];
  for (let i = 0; i < allListingUrls.length; i++) {
    const url = allListingUrls[i];
    const slug = url.replace('https://dubiznes.ae/listing/', '').replace('/', '');
    process.stdout.write('[' + (i + 1) + '/' + allListingUrls.length + '] ' + slug + '... ');
    try {
      const html = await fetch(url);
      const name = extractName(html);
      const phones = findPhoneNumbers(html);
      results.push({ name: name || slug, url, phones });
      console.log(phones.length > 0 ? phones.join(', ') : '(no phone)');
    } catch (e) {
      console.log('ERROR: ' + e.message);
      results.push({ name: slug, url, phones: [] });
    }
  }

  console.log('\n=== RESULTS ===');
  const withPhones = results.filter(r => r.phones.length > 0);
  console.log('Scraped:', results.length, 'With phones:', withPhones.length);
  withPhones.forEach(r => console.log(r.name + ': ' + r.phones.join(', ')));
  fs.writeFileSync('dubiznes_phone_results.json', JSON.stringify(results, null, 2));
  console.log('\nSaved to dubiznes_phone_results.json');
}

main().catch(e => console.error('FATAL:', e));
