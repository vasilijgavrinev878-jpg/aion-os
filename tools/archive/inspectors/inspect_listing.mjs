import fs from 'fs';
const html = fs.readFileSync('C:/AION/listing_1.html', 'utf8');

// Title
const title = html.match(/<title>([^<]+)<\/title>/);
console.log('Title:', title ? title[1] : 'none');

// H1 tags
const h1s = html.match(/<h1[^>]*>[\s\S]*?<\/h1>/g);
console.log('H1s:', h1s ? h1s.map(h => h.replace(/<[^>]+>/g, '').trim()) : 'none');

// Look for phone numbers near +971
const phoneSection = html.match(/\+971[0-9\s\-\(\)]{7,15}/g);
console.log('Phone matches:', phoneSection);

// Look for tel: links
const tels = html.match(/tel:\+?[0-9\-]{7,15}/g);
console.log('Tel links:', tels);

// Look for phone-related divs/classes
const phoneDivs = html.match(/<div[^>]*phone[^>]*>[\s\S]{0,200}?<\/div>/gi);
console.log('Phone divs:', phoneDivs ? phoneDivs.slice(0,3) : 'none');

// Look for "Телефон" text context
const phoneLabel = html.match(/[Тт]елефон[^<]{0,100}/g);
console.log('Phone labels:', phoneLabel);

// Look for wp-block or hp-block that contains phone
const hpBlocks = html.match(/hp-listing__attribute[^>]*>[\s\S]{0,300}?<\/div>/g);
if (hpBlocks) {
  hpBlocks.forEach((b, i) => {
    if (b.includes('971') || b.includes('phone') || b.includes('тел')) {
      console.log(`HP block ${i}:`, b.replace(/<[^>]+>/g, ' ').trim().substring(0, 200));
    }
  });
}
