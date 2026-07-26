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

function extractPhoneNumbers(html) {
  const phones = [];
  const phoneRegex = /(?:\+971|0)[0-9\s\-\(\)]{7,15}/g;
  const matches = html.match(phoneRegex) || [];
  matches.forEach(p => {
    const clean = p.trim().replace(/\s+/g, ' ').replace(/[()]/g, '');
    if (!phones.includes(clean)) phones.push(clean);
  });
  return phones;
}

function extractName(html) {
  const m = html.match(/<h1[^>]*>([^<]+)<\/h1>/);
  return m ? m[1].trim() : null;
}

async function scrapeCategoryPage(url) {
  console.log(`Fetching: ${url}`);
  const html = await fetch(url);
  const urls = extractListingUrls(html);
  console.log(`  Found ${urls.length} listing URLs`);
  const pageMatch = html.match(/page\/(\d+)\//);
  const currentPage = pageMatch ? parseInt(pageMatch[1]) : 1;
  const hasNext = html.includes(`/page/${currentPage + 1}/`);
  return { urls, hasNext, nextPage: currentPage + 1 };
}

async function main() {
  // Test with 3 categories first
  const testCats = ['restaurants', 'fitness', 'clubs-bars'];
  const allUrls = [];
  
  for (const cat of testCats) {
    let page = 1;
    let hasMore = true;
    while (hasMore) {
      const url = page === 1
        ? `https://dubiznes.ae/listing-category/${cat}/`
        : `https://dubiznes.ae/listing-category/${cat}/page/${page}/`;
      try {
        const result = await scrapeCategoryPage(url);
        result.urls.forEach(u => {
          if (!allUrls.includes(u)) allUrls.push(u);
        });
        hasMore = result.hasNext;
        page = result.nextPage;
        await new Promise(r => setTimeout(r, 300));
      } catch (e) {
        console.log(`  Error: ${e.message}`);
        hasMore = false;
      }
    }
  }
  
  console.log(`\nTotal unique URLs: ${allUrls.length}`);
  allUrls.forEach(u => console.log(u));
  
  // Now scrape first 6 listing pages for phone numbers
  console.log('\n--- Scraping listing pages ---');
  for (let i = 0; i < Math.min(6, allUrls.length); i++) {
    console.log(`\n[${i+1}] Fetching: ${allUrls[i]}`);
    try {
      const html = await fetch(allUrls[i]);
      const name = extractName(html);
      const phones = extractPhoneNumbers(html);
      console.log(`  Name: ${name}`);
      console.log(`  Phones: ${phones.length > 0 ? phones.join(', ') : 'NONE'}`);
      // Save to file for inspection
      fs.writeFileSync(`listing_${i+1}.html`, html);
    } catch (e) {
      console.log(`  Error: ${e.message}`);
    }
    await new Promise(r => setTimeout(r, 1500));
  }
}

main().catch(e => console.error(e));
