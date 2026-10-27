# Re-extracts songs.json and cover.jpg from the PDF. Overwrites any hand edits in songs.json.
# Needs: pip install pymupdf
# Usage: python3 src/parse.py "Davidian Songs - New purple cover.pdf"
import fitz, re, json, sys, pathlib
here = pathlib.Path(__file__).parent
d = fitz.open(sys.argv[1])
clean = lambda s: s.replace('\xa0', ' ').replace('\t', ' ').strip()

# Index titles (page 2): entries start with "N." and may wrap onto following lines
index = {}
cur = None
for l in d[2].get_text().split('\n')[1:]:
    l = clean(l)
    if not l or l == 'INDEX': continue
    m = re.match(r'^(\d+)\.\s*(.*)$', l)
    if m: cur = int(m.group(1)); index[cur] = m.group(2)
    elif cur: index[cur] += ' ' + l

songs = []
for pi in range(3, 54):
    lines = [clean(l) for l in d[pi].get_text().split('\n')]
    lines = [l for l in lines if l]
    num = int(lines[0])
    body = lines[1:]
    # some pages carry a doubled text layer: every body line appears twice in a row
    i = body.index(next(l for l in body if l.isupper() and len(l) > 4))
    pre = body[1:i]
    if len(pre) % 2 == 0 and all(pre[k] == pre[k + 1] for k in range(0, len(pre), 2)):
        body = [body[0]] + pre[::2] + body[i:]
    # title line = last line with letters all uppercase and no digits
    ti = max(i for i, l in enumerate(body)
             if len(re.sub(r'[^A-Za-z]', '', l)) >= 4 and not re.search(r'[a-z0-9]', l))
    caps_title = body[ti].rstrip(' ,-')
    scripture, tune = [], ''
    for l in body[ti + 1:]:
        if re.search(r'\d', l): scripture.append(l)
        else: tune = l.strip('() ')
    sections = []
    for l in body[:ti]:
        if re.fullmatch(r'\d+\.?', l): sections.append({'label': l.rstrip('.'), 'lines': []})
        elif l.lower() == 'chorus': sections.append({'label': 'Chorus', 'lines': []})
        else: sections[-1]['lines'].append(l)
    songs.append({'n': num, 'title': index.get(num, caps_title.title()), 'caps': caps_title,
                  'ref': '; '.join(scripture), 'tune': tune, 'sections': sections})

assert [s['n'] for s in songs] == list(range(1, 52))
json.dump(songs, open(here / 'songs.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for s in songs: print(s['n'], '|', s['title'], '|', s['caps'], '|', s['ref'], '|', s['tune'], '|', [x['label'] for x in s['sections']])

# cover image
pix = d[0].get_pixmap(dpi=110); pix.save(str(here / 'cover.jpg'), jpg_quality=80)
print(pix.width, pix.height)
