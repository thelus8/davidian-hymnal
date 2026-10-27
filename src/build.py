# Builds the site at the repository root from template.html + songs.json + cover.jpg.
# Usage: python3 src/build.py   (standard library only)
import json, base64, pathlib, hashlib, shutil, re
here = pathlib.Path(__file__).parent
root = here.parent
songs = json.load(open(here / 'songs.json', encoding='utf-8'))
cover = 'data:image/jpeg;base64,' + base64.b64encode((here / 'cover.jpg').read_bytes()).decode()
html = (here / 'template.html').read_text(encoding='utf-8')
html = html.replace('__SONGS__', json.dumps(songs, ensure_ascii=False)).replace('__COVER__', cover)

head = '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<link rel="manifest" href="manifest.webmanifest">
<meta name="theme-color" content="#160d1b">
<link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="Hymnal">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}</style>
</head><body>'''
(root / 'index.html').write_text(head + html + '</body></html>', encoding='utf-8')
shutil.copy(here / 'manifest.webmanifest', root)

# The cache name changes whenever the page or worker changes, so installed copies update on their next online launch.
sw = (here / 'sw.js').read_text(encoding='utf-8')
version = 'hymnal-' + hashlib.sha1((html + sw).encode()).hexdigest()[:10]
font_css = re.search(r'href="(https://fonts.googleapis.com/css2[^"]+)"', html).group(1).replace('&amp;', '&')
(root / 'sw.js').write_text(sw.replace('__VERSION__', version).replace('__FONT_CSS__', font_css), encoding='utf-8')
print(f'built {len(songs)} songs, cache {version}')
