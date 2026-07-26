import https from 'https';
import fs from 'fs';

function fetchFirstChunk(url, maxBytes = 10240) {
  return new Promise((resolve, reject) => {
    const req = https.get(url, { 
      headers: { 
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Range': 'bytes=0-' + (maxBytes - 1)
      } 
    }, res => {
      let d = '';
      res.on('data', c => { d += c; if (d.length >= maxBytes) req.destroy(); });
      res.on('end', () => resolve(d));
      res.on('close', () => resolve(d));
    });
    req.on('error', reject);
    req.on('abort', () => resolve(''));  // handle destroy
  });
}

function extractName(html) {
  try {
    // Try breadcrumb with vnsco-breadcrumbs class first
    const bcMatch = html.match(/<nav[^>]*class="[^"]*vnsco-breadcrumbs[^"]*"[^>]*>[\s\S]{0,500}?<\/nav>/);
    if (bcMatch) {
      const spans = bcMatch[0].match(/<span[^>]*>([^<]+)<\/span>/g);
      if (spans) {
        const texts = spans.map(s => s.replace(/<[^>]*>/g, '').trim()).filter(t => t !== '\u2192');
        if (texts.length > 0) return texts[texts.length - 1];
      }
    }
  } catch(e) {}
  
  try {
    // Fallback to title/og:title
    const titleMatch = html.match(/<title>([^<]+)<\/title>/);
    if (titleMatch) {
      let t = titleMatch[1]
        .replace(/ - dubiznes\.ae$/, '')
        .replace(/ — dubiznes\.ae$/, '');
      // Take everything before " - " or " — " or " в Дубае" or " в ОАЭ"
      const parts = t.split(/ — | - | в Дубае| в ОАЭ| в самом сердце/);
      return parts[0].trim();
    }
  } catch(e) {}
  
  return null;
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

function decodeHtmlEntities(str) {
  return str
    .replace(/&#8212;/g, '\u2014')
    .replace(/&#038;/g, '&')
    .replace(/&#8211;/g, '\u2013')
    .replace(/&#8220;/g, '\u201c')
    .replace(/&#8221;/g, '\u201d')
    .replace(/&#8230;/g, '\u2026')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>');
}

async function main() {
  const urls = JSON.parse(fs.readFileSync('dubiznes_listing_urls.json', 'utf8'));
  console.log('Re-extracting names and phones from', urls.length, 'listings...\n');
  
  const results = [];
  for (let i = 0; i < urls.length; i++) {
    const url = urls[i];
    const slug = url.replace('https://dubiznes.ae/listing/', '').replace('/', '');
    process.stdout.write('[' + (i + 1) + '/' + urls.length + '] ' + slug + '... ');
    
    try {
      // Fetch first 10KB to get head/title/breadcrumb
      const html = await fetchFirstChunk(url);
      if (!html) throw new Error('Failed to fetch');
      
      const name = extractName(html);
      const phones = findPhoneNumbers(html);
      const cleanName = name ? decodeHtmlEntities(name) : slug;
      
      results.push({ name: cleanName, url, phones });
      console.log(phones.length > 0 ? phones.join(', ') : '(no phone)');
    } catch (e) {
      console.log('ERROR: ' + e.message);
      results.push({ name: slug, url, phones: [] });
    }
  }

  // Build output
  const withPhones = results.filter(r => r.phones.length > 0);
  
  console.log('\n=== RESULTS ===');
  console.log('Scraped:', results.length, 'With phones:', withPhones.length);
  
  // Save as JSON
  fs.writeFileSync('dubiznes_final_results.json', JSON.stringify(withPhones, null, 2), 'utf8');
  
  // Also save as JS for easy import
  let jsContent = 'const dubiznesData = [\n';
  withPhones.forEach((r, i) => {
    const phoneStr = r.phones.map(p => 'Телефон: ' + p).join(', ');
    jsContent += `  { name: ${JSON.stringify(r.name)}, contact: ${JSON.stringify(phoneStr)}, tags: ["phone"] },\n`;
  });
  jsContent += '];\n\nconsole.log("Total businesses:", dubiznesData.length);\n';
  jsContent += 'const fs = require("fs");\n';
  jsContent += 'fs.writeFileSync("dubiznes_final_data.json", JSON.stringify(dubiznesData, null, 2));\n';
  
  fs.writeFileSync('dubiznes_final_data.js', jsContent, 'utf8');
  
  console.log('\nSaved to dubiznes_final_results.json and dubiznes_final_data.js');
  console.log('\n=== NAME / PHONE PAIRS ===');
  withPhones.forEach((r, i) => {
    console.log((i + 1) + '. ' + r.name + ': ' + r.phones.join(', '));
  });
}

main().catch(e => console.error('FATAL:', e));
