import fs from 'fs';
const html = fs.readFileSync('C:/AION/listing_1.html', 'utf8');

// Try breadcrumb with specific class
const bc = html.match(/<nav[^>]*class="[^"]*vnsco-breadcrumbs[^"]*"[^>]*>[\s\S]{0,500}?<\/nav>/);
if (bc) {
  console.log('Found breadcrumb nav');
  const spans = bc[0].match(/<span[^>]*>([^<]+)<\/span>/g);
  if (spans) {
    const texts = spans.map(s => s.replace(/<[^>]*>/g, '').trim()).filter(t => t !== '→');
    console.log('Breadcrumb texts:', texts);
    console.log('Last text (name):', texts[texts.length - 1]);
  }
}

// Try h1 with hp-listing__title class
const hpTitle = html.match(/<h1[^>]*class="[^"]*hp-listing__title[^"]*"[^>]*>([^<]+)<\/h1>/);
console.log('HP title class:', hpTitle ? hpTitle[1] : 'none');

// Try .hp-listing__title in any tag
const anyTitle = html.match(/hp-listing__title[^>]*>([^<]+)</);
console.log('Any hp-listing__title:', anyTitle ? anyTitle[1] : 'none');
