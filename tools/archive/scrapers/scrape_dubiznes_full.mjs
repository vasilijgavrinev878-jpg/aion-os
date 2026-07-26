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
  const regex = /href="(https:\/\/dubiznes\.ae\/listing\/[^\/]+)"/g;
  const urls = [...html.matchAll(regex)].map(m => m[1]);
  return [...new Set(urls)];
}

function findPhoneNumbers(html) {
  const phones = [];
  // Look for tel:+971... patterns (most accurate)
  const telRegex = /tel:\+?971([0-9\-]{7,12})/g;
  let m;
  while ((m = telRegex.exec(html)) !== null) {
    const num = '+971' + m[1].replace(/-/g, '');
    if (!phones.includes(num)) phones.push(num);
  }
  // Also look for direct +971 numbers
  const directRegex = /(\+971[0-9]{7,12})/g;
  while ((m = directRegex.exec(html)) !== null) {
    if (!phones.includes(m[1])) phones.push(m[1]);
  }
  return phones;
}

function extractName(html) {
  const m = html.match(/<title>([^<]+) - dubiznes\.ae<\/title>/);
  if (m) return m[1].replace(/ в Дубае.*$/, '').trim();
  const m2 = html.match(/<h1[^>]*>[\s\S]*?<span[^>]*>([^<]+)<\/span><\/h1>/);
  if (m2) return m2[1].trim();
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
    
    console.log(`  Fetching category page ${page}...`);
    const html = await fetch(url);
    const urls = extractListingUrls(html);
    urls.forEach(u => { if (!allUrls.includes(u)) allUrls.push(u); });
    
    // Check for next page
    const nextLink = html.match(/<link rel="next"[^>]*href="([^"]+)"/);
    if (nextLink && nextLink[1].includes(`/page/${page + 1}/`)) {
      hasMore = true;
      page++;
    } else {
      hasMore = false;
    }
    
    await new Promise(r => setTimeout(r, 500));
  }
  
  return allUrls;
}

async function main() {
  // Categories from the menu
  const categories = [
    'restaurants', 'fitness', 'education', 'healthcare', 'real-estate',
    'spa', 'clubs-bars', 'avtomasterskie-i-deteiling', 'organizatsii',
    'gamingclubs', 'massage', 'uslugi-krasoti-v-oae', 'rentacar',
    'russkiye-magazini-v-oae', 'meditsina', 'it-uslugi', 'manikiur-pedikiur', 'fotograf'
  ];
  
  // Step 1: Collect all listing URLs
  const allListingUrls = [];
  for (const cat of categories) {
    console.log(`\nCategory: ${cat}`);
    const urls = await scrapeAllPages(cat);
    console.log(`  Total: ${urls.length} listings`);
    urls.forEach(u => { if (!allListingUrls.includes(u)) allListingUrls.push(u); });
  }
  
  console.log(`\n\nTotal unique listing URLs: ${allListingUrls.length}`);
  fs.writeFileSync('dubiznes_listing_urls.json', JSON.stringify(allListingUrls, null, 2));
  
  // Step 2: Scrape each listing for phone numbers
  const results = [];
  for (let i = 0; i < allListingUrls.length; i++) {
    const url = allListingUrls[i];
    process.stdout.write(`[${i + 1}/${allListingUrls.length}] ${url.replace('https://dubiznes.ae/listing/', '')}... `);
    
    try {
      const html = await fetch(url);
      const name = extractName(html);
      const phones = findPhoneNumbers(html);
      
      results.push({
        name: name || url.replace('https://dubiznes.ae/listing/', '').replace(/\/$/, ''),
        url: url,
        phones: phones,
        hasPhone: phones.length > 0
      });
      
      if (phones.length > 0) {
        console.log(` PHONE: ${phones.join(', ')}`);
      } else {
        console.log(' no phone');
      }
    } catch (e) {
      console.log(` ERROR: ${e.message}`);
      results.push({ name: url, url, phones: [], hasPhone: false, error: e.message });
    }
    
    await new Promise(r => setTimeout(r, 1500));
  }
  
  console.log(`\n\n=== RESULTS ===`);
  const withPhones = results.filter(r => r.hasPhone);
  console.log(`Total: ${results.length}, With phones: ${withPhones.length}, Without: ${results.length - withPhones.length}`);
  
  withPhones.forEach(r => {
    console.log(`\n${r.name}`);
    r.phones.forEach(p => console.log(`  ${p}`));
  });
  
  fs.writeFileSync('dubiznes_phone_results.json', JSON.stringify(results, null, 2));
}

main().catch(e => console.error('FATAL:', e));
