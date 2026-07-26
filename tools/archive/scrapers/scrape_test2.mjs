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
  let m = html.match(/<title>([^<]+) - dubiznes\.ae<\/title>/);
  if (m) return m[1].split(' - ')[0].trim();
  m = html.match(/<h1[^>]*>[\s\S]*?<span>([^<]+)<\/span><\/h1>/);
  if (m) return m[1].trim();
  m = html.match(/<h1 class="[^"]*hp-listing__title[^"]*"[^>]*>([^<]+)<\/h1>/);
  if (m) return m[1].trim();
  return null;
}

async function testCategory(cat) {
  console.log(`\n=== Testing category: ${cat} ===`);
  const allUrls = [];
  let page = 1;
  let hasMore = true;
  
  while (hasMore) {
    const url = page === 1
      ? `https://dubiznes.ae/listing-category/${cat}/`
      : `https://dubiznes.ae/listing-category/${cat}/page/${page}/`;
    
    console.log(`  Page ${page}: ${url}`);
    const html = await fetch(url);
    
    // Check for rel next
    const nextMatch = html.match(/<link rel="next"[^>]*href="([^"]+)"/);
    const nextUrl = nextMatch ? nextMatch[1] : null;
    console.log(`  rel=next URL: ${nextUrl}`);
    
    const urls = extractListingUrls(html);
    urls.forEach(u => { if (!allUrls.includes(u)) allUrls.push(u); });
    console.log(`  Listings on this page: ${urls.length}`);
    
    if (nextUrl && nextUrl.includes(`/page/${page + 1}/`)) {
      page++;
    } else {
      hasMore = false;
    }
    
    await new Promise(r => setTimeout(r, 300));
  }
  
  console.log(`\nTotal listings for ${cat}: ${allUrls.length}`);
  allUrls.forEach(u => console.log(`  ${u}`));
  
  // Test phone extraction on first 3
  console.log(`\n--- Phone extraction test (first 3) ---`);
  for (let i = 0; i < Math.min(3, allUrls.length); i++) {
    console.log(`\n[${i+1}] ${allUrls[i]}`);
    try {
      const html = await fetch(allUrls[i]);
      const name = extractName(html);
      const phones = findPhoneNumbers(html);
      console.log(`  Name: ${name}`);
      console.log(`  Phones: ${phones.length > 0 ? phones.join(', ') : 'NONE'}`);
    } catch (e) {
      console.log(`  Error: ${e.message}`);
    }
    await new Promise(r => setTimeout(r, 1500));
  }
}

testCategory('restaurants').catch(e => console.error('FATAL:', e));
