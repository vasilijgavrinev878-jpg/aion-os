import fs from 'fs';
const data = JSON.parse(fs.readFileSync('C:/AION/dubiznes_phone_results.json', 'utf8'));

const badNames = data.filter(r => r.name === 'Отправить письмо');
const goodNames = data.filter(r => r.name !== 'Отправить письмо' && r.name !== null);
console.log('Total:', data.length);
console.log('Good names:', goodNames.length);
console.log('Bad names (null or "Отправить письмо"):', data.length - goodNames.length);

// Show a few good names
console.log('\nSample good names:');
goodNames.slice(0, 10).forEach(r => console.log(`  ${r.name}`));
