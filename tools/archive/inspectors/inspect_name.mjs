import fs from 'fs';
const html = fs.readFileSync('C:/AION/listing_1.html', 'utf8');

// Try different name patterns
const title = html.match(/<title>([^<]+)<\/title>/);
console.log('Title:', title ? title[1] : 'none');

const og = html.match(/<meta property="og:title"[^>]*content="([^"]+)"/);
console.log('OG title:', og ? og[1] : 'none');

const breadcrumb = html.match(/<nav[^>]*>[\s\S]{0,500}?<\/nav>/);
if (breadcrumb) {
  const spans = breadcrumb[0].match(/<span[^>]*>([^<]+)<\/span>/g);
  if (spans) {
    console.log('Breadcrumb spans:', spans.map(s => s.replace(/<[^>]*>/g, '').trim()));
  }
}

// Look for listing title in the main content area
const mainContent = html.match(/<div class="hp-page__content">[\s\S]{0,2000}?<\/div>/);
if (mainContent) {
  const h1s = mainContent[0].match(/<h1[^>]*>[\s\S]*?<\/h1>/g);
  if (h1s) console.log('Content H1s:', h1s.map(h => h.replace(/<[^>]*>/g, '').trim()));
}

// Check any h1 with class containing title
const allH1s = html.match(/<h1[^>]*>[\s\S]{0,200}?<\/h1>/g);
if (allH1s) {
  allH1s.forEach((h, i) => {
    console.log(`H1 #${i}:`, h.replace(/<[^>]*>/g, '').trim().substring(0, 100));
  });
}
