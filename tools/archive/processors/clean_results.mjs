import fs from 'fs';

// Load the scraped phone results
const results = JSON.parse(fs.readFileSync('C:/AION/dubiznes_phone_results.json', 'utf8'));

// Decode HTML entities
function decodeHtmlEntities(str) {
  return str
    .replace(/&#8212;/g, '\u2014')
    .replace(/&#038;/g, '&')
    .replace(/&#8211;/g, '\u2013')
    .replace(/&#8220;/g, '\u201c')
    .replace(/&#8221;/g, '\u201d')
    .replace(/&#8230;/g, '\u2026')
    .replace(/&#\d+;/g, '')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>');
}

function extractNameFromTitle(title) {
  if (!title) return null;
  let t = title.replace(/ - dubiznes\.ae$/i, '');
  // Remove location suffix
  t = t.replace(/ в Дубае.*$/, '');
  t = t.replace(/ в ОАЭ.*$/, '');
  t = t.replace(/ в самом сердце ОАЭ.*$/, '');
  t = t.replace(/ — высокая паназиатская кухня.*$/, '');
  t = t.replace(/ — новое лицо премиального фитнеса/, '');
  t = t.replace(/ — гармония ухода и атмосферы/, '');
  t = t.replace(/ — гастрономия нового уровня/, '');
  t = t.split(' — ')[0].trim();
  t = t.split(' - ')[0].trim();
  return t;
}

// Category mapping - infer from URL patterns or use the existing mapping
function inferCategory(url) {
  const slug = url.replace('https://dubiznes.ae/listing/', '').replace('/', '');
  // Map slugs to categories based on existing data
  return '';
}

// Build final output
const output = results
  .filter(r => r.phones && r.phones.length > 0)
  .map(r => ({
    name: r.name && r.name !== 'Отправить письмо' 
      ? decodeHtmlEntities(r.name) 
      : extractNameFromTitle(r.name) || r.url.replace('https://dubiznes.ae/listing/', '').replace('/', ''),
    contact: 'Телефон: ' + r.phones.join(', '),
    url: r.url,
    tags: ['phone']
  }));

// Write cleaned results
fs.writeFileSync('dubiznes_phones_cleaned.json', JSON.stringify(output, null, 2), 'utf8');

console.log('=== CLEANED RESULTS ===');
console.log('Total with phones:', output.length);

// Group by first few digits for summary
const summary = {};
output.forEach(r => {
  const phone = r.contact.replace('Телефон: ', '');
  const prefix = phone.substring(0, 7);
  summary[prefix] = (summary[prefix] || 0) + 1;
});

output.forEach((r, i) => {
  console.log(`${i + 1}. ${r.name}: ${r.contact}`);
});

console.log('\n=== DONE ===');
console.log('Saved to dubiznes_phones_cleaned.json');
