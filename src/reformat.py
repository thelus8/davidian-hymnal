# Fills each verse and chorus in songs.json with "flow": the printed lines regrouped into 2-4 longer lines
# (by how much text there is), with capitals the PDF added only because a line started there made lower case.
# The app shows "flow" by default and "lines" under Line breaks > As printed.
#
# Usage:
#   python3 src/reformat.py          fill sections that have no "flow" yet (keeps hand edits)
#   python3 src/reformat.py --all    redo every section
import json, re, sys, pathlib

here = pathlib.Path(__file__).parent
path = here / 'songs.json'
songs = json.load(open(path, encoding='utf-8'))
redo_all = '--all' in sys.argv

# Words that keep their capital wherever they fall: names, titles for God, and pronouns for God
KEEP = {
    'i', 'o', 'god', 'lord', 'jesus', 'christ', 'father', 'lamb', 'shepherd', 'spirit', 'savior', 'maker', 'king',
    'he', 'him', 'his', 'thy', 'thee', 'thou', 'thine', 'rod', 'word', 'bible', 'scriptures', 'revelation',
    'zion', 'davidian', 'davidians', 'davidia', 'david', 'israel', 'isr’el', 'jacob', 'jacobs', 'elijah', 'moses',
    'jerusalem', 'canaan', 'edom', 'bozrah', 'egypt', 'assyria', 'achan', 'achor', 'gideons', 'gideon', 'saul',
    'esaus', 'jezreel', 'ammi', 'emanuel', 'imanuel', 'gentiles', 'pentecost', 'midianitish', 'mt', 'loud', 'latter',
    'promised',
}
SENTENCE_END = re.compile(r'[.!?]["”’)]?$')

def base(word):
    return re.sub(r'(’s|\'s|’ll|\'ll)$', '', word.lower())

def tidy_caps(text):
    # ROD, GOD -> Rod, God; collapse runs of spaces
    text = re.sub(r"\b([A-Z]{2,}(?:’S|'S)?)\b", lambda m: m.group(1).capitalize(), text)
    return re.sub(r'\s+', ' ', text).strip()

def first_word(line):
    m = re.match(r"[^A-Za-z]*([A-Za-z’']+)", line)
    return m.group(1) if m else ''

def lower_first(text):
    """Lower-case the first word unless it is a name or a word for God."""
    m = re.match(r"([^A-Za-z]*)([A-Za-z’']+)(.*)", text, re.S)
    if not m: return text
    lead, word, rest = m.groups()
    if '“' in lead or '"' in lead: return text   # a quotation keeps its capital
    if word[0].isupper() and not word.isupper() and base(word) not in KEEP:
        return lead + word[0].lower() + word[1:] + rest
    return text

def join(prev, line):
    """Append a printed line to the text before it, lower-casing a first word that was only capitalized by the line break."""
    line = line.strip()
    if prev and not SENTENCE_END.search(prev): line = lower_first(line)
    return (prev + ' ' + line).strip() if prev else line

def break_cost(line, nxt):
    """How bad it is to end a line after `line` when `nxt` comes next."""
    line = line.rstrip()
    if SENTENCE_END.search(line): return 0
    if re.search(r'[;:]["”’)]?$', line): return .05
    # a printed line that starts with a capital is a likely phrase start, a comma a likely pause
    w = first_word(nxt)
    capital_next = bool(w) and w[0].isupper() and base(w) not in KEEP
    comma = bool(re.search(r',["”’)]?$', line))
    if capital_next and comma: return .1
    if capital_next: return .6
    if comma: return .8
    return 2     # mid-phrase: avoid

def regroup(lines):
    lines = [tidy_caps(l) for l in lines]
    total = sum(len(l) for l in lines)
    k = 2 if total < 120 else 3 if total < 230 else 4
    k = max(1, min(k, len(lines)))
    ideal = total / k
    n = len(lines)
    # best[i][g] = lowest cost to split lines[:i] into g groups
    INF = float('inf')
    best = [[INF] * (k + 1) for _ in range(n + 1)]
    back = [[0] * (k + 1) for _ in range(n + 1)]
    best[0][0] = 0
    for i in range(1, n + 1):
        for g in range(1, k + 1):
            for j in range(g - 1, i):
                if best[j][g - 1] == INF: continue
                size = sum(len(l) for l in lines[j:i]) + (i - j - 1)
                cost = best[j][g - 1] + (size / ideal - 1) ** 2 + (break_cost(lines[i - 1], lines[i]) if i < n else 0)
                if cost < best[i][g]: best[i][g], back[i][g] = cost, j
    groups, i = [], n
    for g in range(k, 0, -1):
        j = back[i][g]
        groups.append(lines[j:i]); i = j
    out = []
    for g in groups[::-1]:
        text = ''
        for l in g: text = join(text, l)
        # a capital only where a sentence starts
        if out and not SENTENCE_END.search(out[-1]): text = lower_first(text)
        elif text: text = text[0].upper() + text[1:]
        out.append(text)
    return out

changed = 0
for s in songs:
    for sec in s['sections']:
        if redo_all or 'flow' not in sec:
            sec['flow'] = regroup(sec['lines']); changed += 1
json.dump(songs, open(path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(f'reformatted {changed} verses and choruses')
