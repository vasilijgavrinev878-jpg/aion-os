import fs from 'fs';

// Original data (from category pages)
const origData = JSON.parse(fs.readFileSync('C:/AION/dubiznes_data.json', 'utf8'));

// New phone data
const phoneData = JSON.parse(fs.readFileSync('C:/AION/dubiznes_final_clean.json', 'utf8'));

// Build lookup by normalized name
function normalize(str) {
  return str.toLowerCase()
    .replace(/['']/g, "'")
    .replace(/[""]/g, '"')
    .replace(/[—–-]/g, ' ')
    .replace(/[^a-zа-яё0-9\s]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

const phoneLookup = {};
phoneData.forEach(p => {
  phoneLookup[normalize(p.name)] = p.contact;
});

// Also match by URL slug from the raw results
const rawResults = JSON.parse(fs.readFileSync('C:/AION/dubiznes_phone_results.json', 'utf8'));
const urlLookup = {};
rawResults.forEach(r => {
  if (r.phones && r.phones.length > 0) {
    const slug = r.url.replace('https://dubiznes.ae/listing/', '').replace('/', '');
    urlLookup[slug] = r.phones.map(p => 'Телефон: ' + p).join(', ');
  }
});

// Merge: add phone to original data items
let matched = 0;
let unmatched = 0;

const merged = origData.map(item => {
  const normName = normalize(item.name);
  
  // Try direct name match
  let phone = phoneLookup[normName];
  
  if (phone) {
    matched++;
  } else {
    // Try URL slug match - derive slug from name
    // This is approximate since slugs are unpredictable
    unmatched++;
  }
  
  return {
    name: item.name,
    address: item.contact,
    category: item.category,
    phone: phone || null,
    tags: phone ? [...item.tags, 'phone'] : item.tags
  };
});

// Also add items from phone data that weren't in original
const origNames = new Set(origData.map(i => normalize(i.name)));
const newItems = [];
phoneData.forEach(p => {
  if (!origNames.has(normalize(p.name))) {
    newItems.push({
      name: p.name,
      address: null,
      category: 'unknown',
      phone: p.contact,
      tags: ['phone']
    });
  }
});

// Output summary
const withPhone = merged.filter(m => m.phone);
const withoutPhone = merged.filter(m => !m.phone);

console.log('=== MERGE RESULTS ===');
console.log('Original businesses:', origData.length);
console.log('Phone data entries:', phoneData.length);
console.log('Name-matched:', matched);
console.log('Unmatched (no phone in orig):', withoutPhone.length);
console.log('New items (phone only, not in orig):', newItems.length);
console.log('Total with phones:', withPhone.length + newItems.length);

// Save combined result
const combined = [...merged, ...newItems];
const combinedWithPhone = combined.filter(c => c.phone);

let js = '// Dubiznes.ae - Combined business data with phone numbers\n';
js += '// Total: ' + combinedWithPhone.length + ' businesses with phones\n\n';
js += 'const dubiznesData = [\n\n';

combinedWithPhone.forEach((item, i) => {
  const contact = item.phone + (item.address ? ' | ' + item.address : '');
  js += `  { name: ${JSON.stringify(item.name)}, contact: ${JSON.stringify(contact)}, category: ${JSON.stringify(item.category || 'unknown')}, tags: ${JSON.stringify(item.tags)} },\n`;
});

js += '];\n\n';
js += 'module.exports = dubiznesData;\n';

fs.writeFileSync('dubiznes_combined_data.js', js, 'utf8');
fs.writeFileSync('dubiznes_combined_data.json', JSON.stringify(combinedWithPhone, null, 2), 'utf8');

console.log('\nSaved to: dubiznes_combined_data.js and dubiznes_combined_data.json');

// Show unmatched original entries
console.log('\n=== ORIGINAL BUSINESSES WITHOUT PHONE ===');
withoutPhone.forEach(item => {
  console.log(`  ${item.name} (${item.category})`);
});
