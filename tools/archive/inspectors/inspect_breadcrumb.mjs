import fs from 'fs';
const html = fs.readFileSync('C:/AION/listing_1.html', 'utf8');

// Find breadcrumb nav
const navMatch = html.match(/<nav[^>]*>[\s\S]{0,2000}?<\/nav>/);
if (navMatch) {
  const nav = navMatch[0];
  // Extract all spans
  const spans = [...nav.matchAll(/<span[^>]*>([^<]+)<\/span>/g)];
  console.log('Breadcrumb spans:');
  spans.forEach((s, i) => console.log(`  ${i}: "${s[1]}"`));
}

// Find all span texts on the page
const pageSpans = [...html.matchAll(/<span[^>]*>([^<]+)<\/span>/g)];
const allTexts = pageSpans.map(s => s[1].trim()).filter(t => t.length > 0 && t.length < 100);
// Show unique non-trivial texts
const unique = [...new Set(allTexts)];
console.log('\nAll unique span texts on page:');
unique.forEach(t => console.log(`  "${t}"`));

// Find og:title
const og = html.match(/<meta property="og:title"[^>]*content="([^"]+)"/);
console.log('\nOG title:', og ? og[1] : 'none');

// Title tag
const title = html.match(/<title>([^<]+)<\/title>/);
console.log('Title:', title ? title[1] : 'none');
