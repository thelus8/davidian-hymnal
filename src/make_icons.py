# Regenerates icons/ from the PDF's cover page. Needs: pip install pymupdf pillow
# Usage: python3 src/make_icons.py "Davidian Songs - New purple cover.pdf"
import sys, pathlib, fitz
from PIL import Image
out = pathlib.Path(__file__).parent.parent / 'icons'
out.mkdir(exist_ok=True)
pix = fitz.open(sys.argv[1])[0].get_pixmap(dpi=200)
img = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
w, h = img.size
# square centred on the "THE DAVIDIAN HYMNAL" lettering (~37% down the cover)
side = int(w * 0.66); cx, cy = w // 2, int(h * 0.37)
crop = img.crop((cx - side // 2, cy - side // 2, cx + side // 2, cy + side // 2))
for s, name in [(512, 'icon-512.png'), (192, 'icon-192.png'), (180, 'apple-touch-icon.png')]:
    crop.resize((s, s), Image.LANCZOS).save(out / name)
# maskable: same art shrunk into the 80% safe zone on the cover's dark ground
bg = Image.new('RGB', (512, 512), (22, 13, 27))
bg.paste(crop.resize((410, 410), Image.LANCZOS), (51, 51))
bg.save(out / 'icon-maskable-512.png')
