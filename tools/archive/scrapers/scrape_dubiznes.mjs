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
  // Look for phone patterns: +971..., 0XX..., tel: links
  const phones = [];
  // Match +971... numbers
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
  console.log(`Fetching category: ${url}`);
  const html = await fetch(url);
  const urls = extractListingUrls(html);
  console.log(`  Found ${urls.length} listing URLs`);
  
  // Check for pagination
  const pageMatch = html.match(/page\/(\d+)\//);
  const currentPage = pageMatch ? parseInt(pageMatch[1]) : 1;
  const hasNext = html.includes(`/page/${currentPage + 1}/`);
  
  return { urls, hasNext, nextPage: currentPage + 1 };
}

async function scrapeListingPage(url) {
  try {
    const html = await fetch(url);
    const name = extractName(html);
    const phones = extractPhoneNumbers(html);
    return { url, name, phones, success: true };
  } catch (e) {
    return { url, name: null, phones: [], success: false, error: e.message };
  }
}

// Category pages to scrape
const categories = [
  'restaurants',
  'fitness',
  'education',
  'healthcare',
  'real-estate',
  'spa',
  'clubs-bars',
  'avtomasterskie-i-deteiling',
  'organizatsii',
  'gamingclubs',
  'massage',
  'uslugi-krasoti-v-oae',
  'rentacar',
  'russkiye-magazini-v-oae',
  'meditsina',
  'it-uslugi',
  'manikiur-pedikiur',
  'fotograf'
];

async function main() {
  const allListingUrls = [];
  
  // Step 1: Collect all listing URLs from category pages
  for (const cat of categories) {
    let page = 1;
    let hasMore = true;
    while (hasMore) {
      const url = page === 1
        ? `https://dubiznes.ae/listing-category/${cat}/`
        : `https://dubiznes.ae/listing-category/${cat}/page/${page}/`;
      try {
        const result = await scrapeCategoryPage(url);
        result.urls.forEach(u => {
          if (!allListingUrls.includes(u)) allListingUrls.push(u);
        });
        hasMore = result.hasNext;
        page = result.nextPage;
        // Small delay to be polite
        await new Promise(r => setTimeout(r, 500));
      } catch (e) {
        console.log(`  Error fetching ${url}: ${e.message}`);
        hasMore = false;
      }
    }
  }
  
  console.log(`\nTotal unique listing URLs found: ${allListingUrls.length}`);
  fs.writeFileSync('dubiznes_listing_urls.json', JSON.stringify(allListingUrls, null, 2));
  
  // Step 2: Scrape first 30 listing pages for phone numbers
  const results = [];
  const toScrape = allListingUrls.slice(0, 30);
  for (let i = 0; i < toScrape.length; i++) {
    console.log(`Scraping [${i + 1}/${toScrape.length}]: ${toScrape[i]}`);
    const result = await scrapeListingPage(toScrape[i]);
    results.push(result);
    if (result.phones.length > 0) {
      console.log(`  Name: ${result.name}, Phones: ${result.phones.join(', ')}`);
    } else {
      console.log(`  Name: ${result.name}, No phones found`);
    }
    // Be polite - delay between requests
    await new Promise(r => setTimeout(r, 1000));
  }
  
  // Save results
  fs.writeFileSync('dubiznes_phone_results.json', JSON.stringify(results, null, 2));
  
  // Summary
  const withPhones = results.filter(r => r.phones.length > 0);
  console.log(`\n=== SUMMARY ===`);
  console.log(`Total listings scraped: ${results.length}`);
  console.log(`Listings with phones: ${withPhones.length}`);
  console.log(`Listings without phones: ${results.length - withPhones.length}`);
  withPhones.forEach(r => {
    console.log(`\n${r.name}:`);
    r.phones.forEach(p => console.log(`  ${p}`));
  });
}

main().catch(e => console.error(e));
