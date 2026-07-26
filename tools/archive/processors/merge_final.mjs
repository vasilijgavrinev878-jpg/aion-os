import fs from 'fs';

const origData = JSON.parse(fs.readFileSync('C:/AION/dubiznes_data.json', 'utf8'));
const phoneData = JSON.parse(fs.readFileSync('C:/AION/dubiznes_final_clean.json', 'utf8'));
const rawResults = JSON.parse(fs.readFileSync('C:/AION/dubiznes_phone_results.json', 'utf8'));

function normalize(str) {
  return str.toLowerCase()
    .replace(/['']/g, "'")
    .replace(/[""]/g, '"')
    .replace(/[—–-]/g, ' ')
    .replace(/[^a-zа-яё0-9\s]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

function fuzzyMatch(name1, name2) {
  const n1 = normalize(name1);
  const n2 = normalize(name2);
  if (n1 === n2) return true;
  // Check if one starts with the other
  if (n1.startsWith(n2) || n2.startsWith(n1)) return true;
  // Check word overlap
  const words1 = n1.split(' ');
  const words2 = n2.split(' ');
  const common = words1.filter(w => words2.includes(w));
  return common.length >= Math.min(words1.length, words2.length) * 0.7;
}

// Build URL slug lookup for phone data
const slugPhoneMap = {};
rawResults.forEach(r => {
  if (r.phones && r.phones.length > 0) {
    const slug = r.url.replace('https://dubiznes.ae/listing/', '').replace('/', '');
    slugPhoneMap[slug] = r.phones.map(p => 'Телефон: ' + p).join(', ');
  }
});

// Also build phone-by-name from raw (with decoded names)
const rawNameMap = {};
rawResults.forEach(r => {
  if (r.phones && r.phones.length > 0 && r.name && r.name !== 'Отправить письмо') {
    rawNameMap[normalize(r.name)] = r.phones.map(p => 'Телефон: ' + p).join(', ');
  }
});

// First pass - direct match
const merged = origData.map(item => {
  const normName = normalize(item.name);
  let phone = null;
  
  // Check clean phone data
  const cleanMatch = phoneData.find(p => normalize(p.name) === normName);
  if (cleanMatch) phone = cleanMatch.contact;
  
  // Check raw results name map
  if (!phone && rawNameMap[normName]) phone = rawNameMap[normName];
  
  return {
    name: item.name,
    address: item.contact,
    category: item.category,
    phone: phone,
    tags: phone ? [...item.tags, 'phone'] : item.tags,
    normName: normName
  };
});

// Second pass - fuzzy match for remaining
const noPhone = merged.filter(m => !m.phone);
console.log('Entries without phone after exact match:', noPhone.length);

noPhone.forEach(item => {
  // Try fuzzy match with phone data
  const found = phoneData.find(p => fuzzyMatch(item.name, p.name));
  if (found) {
    item.phone = found.contact;
    if (!item.tags.includes('phone')) item.tags.push('phone');
    console.log(`  FUZZY MATCH: "${item.name}" -> "${found.name}"`);
  } else {
    // Try matching by slug derived from name
    const expectedSlug = normalize(item.name).replace(/\s+/g, '-');
    const foundBySlug = Object.keys(slugPhoneMap).find(slug => {
      const slugNorm = slug.replace(/-/g, '');
      const nameNorm = expectedSlug.replace(/-/g, '');
      return slugNorm.includes(nameNorm) || nameNorm.includes(slugNorm);
    });
    if (foundBySlug) {
      item.phone = slugPhoneMap[foundBySlug];
      if (!item.tags.includes('phone')) item.tags.push('phone');
      console.log(`  SLUG MATCH: "${item.name}" -> slug "${foundBySlug}"`);
    }
  }
});

// Final stats
const withPhone = merged.filter(m => m.phone);
const stillNoPhone = merged.filter(m => !m.phone);

console.log('\n=== FINAL MERGE ===');
console.log('Total with phone:', withPhone.length);
console.log('Still without phone:', stillNoPhone.length);
console.log('\nStill missing:');
stillNoPhone.forEach(item => {
  console.log(`  ${item.name} (${item.category})`);
});

// Save
const output = withPhone.map(({name, address, category, phone, tags}) => ({
  name, address, category, phone, tags
}));

fs.writeFileSync('dubiznes_final_with_categories.json', JSON.stringify(output, null, 2), 'utf8');

let js = '// Dubiznes.ae - All businesses with phone numbers\n';
js += '// Total: ' + output.length + '\n\n';
js += 'const dubiznesData = [\n\n';
output.forEach((item, i) => {
  const contact = item.phone + (item.address ? ' | ' + item.address : '');
  js += `  { name: ${JSON.stringify(item.name)}, contact: ${JSON.stringify(contact)}, category: ${JSON.stringify(item.category)}, tags: ${JSON.stringify(item.tags)} },\n`;
});
js += '];\n\n';
js += 'module.exports = dubiznesData;\n';
fs.writeFileSync('dubiznes_final_with_categories.js', js, 'utf8');

console.log('\nSaved to dubiznes_final_with_categories.json and .js');
console.log('\n=== FULL LISTING ===');
output.forEach((item, i) => {
  const contact = item.phone + (item.address ? ' | ' + item.address : '');
  console.log((i+1) + '. ' + item.name + ': ' + contact);
});
