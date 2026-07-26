import re

with open('База исполнителей Анталия.html', 'r', encoding='utf-8') as f:
    content = f.read()

resources = [
    'russiansinturkey_antalya',
    'krasota_antalya',
    'masteriklientantalya',
    'russkayaantalya',
]

# Collect all unique fake usernames/emails starting with ant_
fake_patterns = set()
for m in re.finditer(r'@ant_\w+|ant\.\d+@gmail\.com|instagram\.com/ant_\w+', content):
    fake_patterns.add(m.group())

# Also collect sequential wa.me numbers
for m in re.finditer(r'wa\.me/90\d{2,5}', content):
    fake_patterns.add(m.group())

print(f"Found {len(fake_patterns)} unique fake patterns")

# For each pattern, find its full contact div line and replace
fake_entries = []
for m in re.finditer(
    r'<div class="contact"><a href="[^"]+">([^<]+)</a></div>',
    content
):
    link_text = m.group(1)
    if link_text.startswith('@ant_') or link_text.startswith('ant_') or 'ant.' in link_text and '@gmail.com' in link_text:
        fake_entries.append((m.group(0), link_text))
    elif re.match(r'90 \d{2,5}', link_text):
        fake_entries.append((m.group(0), link_text))

print(f"Found {len(fake_entries)} fake contact entries")

# Replace each
count = 0
for old_contact, link_text in fake_entries:
    res = resources[count % len(resources)]
    new_contact = f'<div class="contact"><a href="https://t.me/{res}">@{res}</a></div>'
    content = content.replace(old_contact, new_contact, 1)
    count += 1

print(f"Replaced {count} fake contacts")

with open('База исполнителей Анталия.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done!")
