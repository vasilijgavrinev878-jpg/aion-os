import fs from 'fs';

const results = JSON.parse(fs.readFileSync('C:/AION/dubiznes_phone_results.json', 'utf8'));

function decodeEntities(str) {
  return str
    .replace(/&#8212;/g, '—')
    .replace(/&#038;/g, '&')
    .replace(/&#8211;/g, '–')
    .replace(/&#8220;/g, '"')
    .replace(/&#8221;/g, '"')
    .replace(/&#171;/g, '"')
    .replace(/&#187;/g, '"')
    .replace(/&#8217;/g, "'")
    .replace(/&#8230;/g, '...')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>');
}

const formatPhone = (phone) => 'Телефон: ' + phone;

const cleanResults = results
  .filter(r => r.phones && r.phones.length > 0)
  .map(r => ({
    name: decodeEntities(r.name),
    contact: r.phones.map(formatPhone).join(', '),
    url: r.url,
    tags: ['phone']
  }));

// Write JSON
fs.writeFileSync('dubiznes_final_clean.json', JSON.stringify(cleanResults, null, 2), 'utf8');

// Write JS module
let js = '// Dubiznes.ae - Businesses with phone numbers\n';
js += '// Source: https://dubiznes.ae\n';
js += '// Total: ' + cleanResults.length + ' businesses\n\n';
js += 'const dubiznesPhones = [\n\n';

cleanResults.forEach((r, i) => {
  js += `  // ===== ${r.name} =====\n`;
  js += `  { name: ${JSON.stringify(r.name)}, contact: ${JSON.stringify(r.contact)}, tags: ["phone"] },\n\n`;
});

js += '];\n\n';
js += 'if (typeof module !== "undefined" && module.exports) {\n';
js += '  module.exports = dubiznesPhones;\n';
js += '}\n';

fs.writeFileSync('dubiznes_phones_final.js', js, 'utf8');

console.log('=== FINAL RESULTS ===');
console.log('Total businesses with phones:', cleanResults.length);
console.log('');
console.log('Sample entries:');
cleanResults.slice(0, 5).forEach(r => console.log(`  ${r.name}: ${r.contact}`));
console.log('');
console.log('Last 3 entries:');
cleanResults.slice(-3).forEach(r => console.log(`  ${r.name}: ${r.contact}`));
console.log('');
console.log('Saved to:');
console.log('  dubiznes_final_clean.json');
console.log('  dubiznes_phones_final.js');
