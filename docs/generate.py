#!/usr/bin/env python3
"""Scan docs/ subdirectories and embed data directly into index.html.

Usage: python generate.py

This script:
1. Reads categories.json for category definitions
2. Scans each subdirectory for .html and .csv files
3. Compares with previous manifest to detect changes
4. Replaces the CATEGORIES array in index.html with current data
5. Saves new manifest for next comparison

The resulting index.html is fully self-contained (no external deps).
"""
import json, os, sys, re
from datetime import datetime

# Force UTF-8 for Windows console (emojis in output)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE = os.path.dirname(os.path.abspath(__file__))
CATEGORIES_PATH = os.path.join(BASE, 'categories.json')
INDEX_PATH = os.path.join(BASE, 'index.html')
MANIFEST_PATH = os.path.join(BASE, '_manifest.json')
HISTORY_PATH = os.path.join(BASE, '_history.json')
API_CONFIG_PATH = os.path.join(BASE, 'api_config.json')
MAX_HISTORY_DAYS = 30  # keep history entries for this many days

def load_categories():
    with open(CATEGORIES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_text_preview(filepath):
    """Extract plain text from HTML file for search indexing."""
    if not filepath.endswith('.html'):
        return ''
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            html = f.read()
    except (UnicodeDecodeError, OSError):
        return ''
    # Remove style/script blocks
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL|re.IGNORECASE)
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL|re.IGNORECASE)
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', html)
    # Decode common HTML entities
    for e, c in [('&nbsp;',' '),('&amp;','&'),('&lt;','<'),('&gt;','>'),('&quot;','"'),('&#39;',"'")]:
        text = text.replace(e, c)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text[:1500]

def scan_all_docs(categories):
    """Scan all category directories and return a flat dict {relpath: mtime}
    and a structured output list with text previews."""
    manifest = {}  # { 'category/file.html': mtime }
    output = []
    total = 0
    has_text = 0

    for cat in categories:
        dir_path = os.path.join(BASE, cat['dir'])
        docs = []
        if os.path.isdir(dir_path):
            for name in sorted(os.listdir(dir_path)):
                if not (name.endswith('.html') or name.endswith('.csv')):
                    continue
                fp = os.path.join(dir_path, name)
                mtime = int(os.path.getmtime(fp))
                relpath = f"{cat['dir']}/{name}"
                manifest[relpath] = mtime
                text = extract_text_preview(fp)
                if text: has_text += 1
                docs.append({'name': name, 'mtime': mtime, 'text': text})
        # Sort by mtime descending (newest first)
        docs.sort(key=lambda f: -f['mtime'])
        output.append({
            'id': cat['id'],
            'dir': cat['dir'],
            'emoji': cat['emoji'],
            'title': cat['title'],
            'docs': docs
        })
        total += len(docs)
        print(f"  {cat['dir']}/: {len(docs)} docs")

    print(f"  📝 Text indexed for {has_text}/{total} docs")
    return manifest, output, total

def detect_changes(new_manifest, old_manifest):
    """Compare new and old manifests.
    Returns (added, removed, modified) tuples."""
    if old_manifest is None:
        return [], [], []  # First run — no comparison

    old_keys = set(old_manifest.keys())
    new_keys = set(new_manifest.keys())

    added = sorted(new_keys - old_keys)
    removed = sorted(old_keys - new_keys)

    modified = []
    for key in old_keys & new_keys:
        if new_manifest[key] != old_manifest[key]:
            # mtime changed = file was modified
            old_dt = datetime.fromtimestamp(old_manifest[key])
            new_dt = datetime.fromtimestamp(new_manifest[key])
            modified.append((key, old_dt, new_dt))

    return added, removed, modified


def _find_json_end(html, start):
    """Find the end of a JSON value starting at `start`.
    Handles nested arrays/objects and strings with escaped quotes."""
    stack = []
    i = start
    in_string = False
    escape = False
    while i < len(html):
        c = html[i]
        if escape:
            escape = False
            i += 1
            continue
        if c == '\\':
            escape = True
            i += 1
            continue
        if in_string:
            if c == '"':
                in_string = False
            i += 1
            continue
        if c == '"':
            in_string = True
            i += 1
            continue
        if c in '[{':
            stack.append(c)
            i += 1
            continue
        if c in ']}':
            if not stack:
                return i
            stack.pop()
            if not stack:
                return i + 1  # Include the closing bracket
            i += 1
            continue
        i += 1
    return i

def load_api_config():
    """Read API config from api_config.json, return empty dict if not found."""
    if not os.path.exists(API_CONFIG_PATH):
        return {}
    try:
        with open(API_CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}

def inject_into_html(output, total, categories, history):
    """Replace markers in index.html with current data."""
    data_json = json.dumps(output, ensure_ascii=False, indent=2)
    history_json = json.dumps(history, ensure_ascii=False, indent=2)
    api_config = load_api_config()
    api_json = json.dumps(api_config, ensure_ascii=False, indent=2)

    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        html = f.read()

    # Replace CATEGORIES
    cat_marker = 'const CATEGORIES_PLACEHOLDER = true; // marker for generate.py\nlet CATEGORIES ='
    if cat_marker not in html:
        print("ERROR: Could not find CATEGORIES_PLACEHOLDER marker in index.html")
        sys.exit(1)
    idx = html.find(cat_marker)
    json_start = html.find('[', idx)
    if json_start == -1:
        print("ERROR: Could not find JSON array start for CATEGORIES")
        sys.exit(1)
    json_end = _find_json_end(html, json_start)
    cats_replacement = f"const CATEGORIES_PLACEHOLDER = true; // marker for generate.py\nlet CATEGORIES = {data_json};"
    remaining = html[json_end:]
    best_pos = len(remaining)
    for kw in ['\nconst ', '\nlet ', '\n// ', '\nfunction ', '\ndocument.']:
        pos = remaining.find(kw)
        if pos >= 0 and pos < best_pos:
            best_pos = pos
    if best_pos < len(remaining):
        remaining = remaining[best_pos:]
    html = html[:idx] + cats_replacement + remaining

    # Replace HISTORY
    hist_marker = 'const HISTORY_PLACEHOLDER = true; // marker for generate.py\nlet HISTORY ='
    if hist_marker not in html:
        print("ERROR: Could not find HISTORY_PLACEHOLDER marker in index.html")
        sys.exit(1)
    idx = html.find(hist_marker)
    json_start = html.find('[', idx)
    if json_start == -1:
        print("ERROR: Could not find JSON array start for HISTORY")
        sys.exit(1)
    json_end = _find_json_end(html, json_start)
    hist_replacement = f"const HISTORY_PLACEHOLDER = true; // marker for generate.py\nlet HISTORY = {history_json};"
    remaining = html[json_end:]
    best_pos = len(remaining)
    for kw in ['\n// ', '\nfunction ', '\ndocument.', '\nlet viewer', '\n</script>']:
        pos = remaining.find(kw)
        if pos >= 0 and pos < best_pos:
            best_pos = pos
    if best_pos < len(remaining):
        remaining = remaining[best_pos:]
    html = html[:idx] + hist_replacement + remaining

    # Replace API_CONFIG — inject before the AI CHAT section
    chat_marker = '// ─── AI CHAT (free, no API) ────────────────────────────────────'
    if chat_marker in html:
        idx = html.find(chat_marker)
        api_block = f"""// ─── API CONFIG (auto-generated) ──────────────────────────────────
let API_CONFIG = {api_json};

"""
        # Remove previous API_CONFIG injection if exists
        prev_marker = '// ─── API CONFIG (auto-generated) ──────────────────────────────────'
        if prev_marker in html:
            prev_idx = html.find(prev_marker)
            # Find end of this block (up to the chat marker)
            next_chat = html.find('// ─── AI CHAT', prev_idx)
            if next_chat >= 0:
                html = html[:prev_idx] + html[next_chat:]
                idx = html.find(chat_marker)
        html = html[:idx] + api_block + html[idx:]
        has_key = bool(api_config.get('api_key') and api_config['api_key'] != 'sk-or-v1-xxxxxxxxxxxxxxxxxxxx')
        print(f"  🔑 API config injected ({'has key' if has_key else 'no key'})")
    else:
        print("  ⚠️  AI CHAT section not found in index.html (skip)")

    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n  ✅ Готово! {total} docs across {len(categories)} categories written to index.html")

def save_manifest(manifest):
    with open(MANIFEST_PATH, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2, sort_keys=True)


def load_manifest():
    if not os.path.exists(MANIFEST_PATH):
        return None
    try:
        with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def load_history():
    """Load the persistent change history."""
    if not os.path.exists(HISTORY_PATH):
        return []
    try:
        with open(HISTORY_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def save_history(history):
    """Save history, pruning entries older than MAX_HISTORY_DAYS."""
    cutoff = datetime.now().timestamp() - (MAX_HISTORY_DAYS * 86400)
    history = [h for h in history if datetime.fromisoformat(h['date']).timestamp() > cutoff]
    with open(HISTORY_PATH, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
    return history


def append_history(history, added, removed, modified):
    """Append a new change entry if there were any changes."""
    if not added and not removed and not modified:
        return history
    entry = {
        'date': datetime.now().isoformat(seconds=True),
        'added': [format_label(p) for p in added],
        'removed': [format_label(p) for p in removed],
        'modified': [format_label(p) for p in modified]
    }
    history.append(entry)
    return history


def format_label(path):
    """Strip dir prefix and .html/.csv from a relpath for display."""
    name = path.split('/', 1)[-1] if '/' in path else path
    name = name.replace('.html', '').replace('.csv', '')
    return name


def print_changes(added, removed, modified):
    """Print a human-readable change summary."""
    if not added and not removed and not modified:
        print()
        print(f"  📭 Изменений не обнаружено")
        return

    print()
    print(f"  {'='*50}")
    print(f"  📋  Лог изменений")
    print(f"  {'='*50}")

    if added:
        print(f"\n  🟢  Добавлено ({len(added)}):")
        for path in added:
            print(f"      📄 {format_label(path)}")

    if removed:
        print(f"\n  🔴  Удалено ({len(removed)}):")
        for path in removed:
            print(f"      🗑️  {format_label(path)}")

    if modified:
        print(f"\n  🟡  Изменено ({len(modified)}):")
        for path, old_dt, new_dt in modified:
            label = format_label(path)
            old_str = old_dt.strftime('%d.%m.%Y %H:%M')
            new_str = new_dt.strftime('%d.%m.%Y %H:%M')
            print(f"      📝 {label}")

    print()
    print(f"  {'='*50}")


def generate():
    categories = load_categories()

    # Load previous manifest (if exists)
    old_manifest = load_manifest()

    # Load persistent history
    history = load_history()

    # Scan current state
    print("  🔍 Сканирую docs/...")
    new_manifest, output, total = scan_all_docs(categories)

    # Detect and print changes
    added, removed, modified = detect_changes(new_manifest, old_manifest)
    print_changes(added, removed, modified)

    # Append to history if changes detected
    history = append_history(history, added, removed, modified)

    # Save persistent history on disk (pruned)
    history = save_history(history)

    # Inject into HTML - both categories AND history
    inject_into_html(output, total, categories, history)

    # Save manifest for next comparison
    save_manifest(new_manifest)

    return total, len(added), len(removed), len(modified)


if __name__ == '__main__':
    generate()
