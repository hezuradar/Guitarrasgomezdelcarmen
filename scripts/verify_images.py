from pathlib import Path
import re
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent if HERE.name == "scripts" else HERE
if (ROOT / "web-rediseno").is_dir():
    ROOT = ROOT / "web-rediseno"

missing = []
refs = 0
sizes = {}
for path in sorted(ROOT.glob("*.html")):
    text = path.read_text(encoding="utf-8")
    for attr in ("src", "href"):
        for rel in re.findall(rf'\b{attr}="(assets/[^"]+\.(?:webp|png|jpg))"', text):
            refs += 1
            f = ROOT / rel
            if not f.exists():
                missing.append((path.name, rel))
            else:
                sizes[rel] = f.stat().st_size

print(f"Referencias locales: {refs}")
print(f"Archivos WebP en assets/img: {len(list((ROOT/'assets'/'img').glob('*.webp')))}")
print(f"Tamaño total imágenes servidas: {sum(sizes.values())/1024/1024:.2f} MB")
if missing:
    print("FALTAN:")
    for m in missing[:30]:
        print(" ", m)
else:
    print("Sin referencias rotas.")

webp = list((ROOT / "assets").rglob("*.webp"))
bad = []
for f in webp:
    try:
        with Image.open(f) as im:
            im.verify()
    except Exception as exc:
        bad.append((f.name, str(exc)))
print(f"WebP válidos: {len(webp) - len(bad)}/{len(webp)}")
if bad:
    print("INVALIDOS:", bad[:10])
