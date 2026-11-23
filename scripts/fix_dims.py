from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent if HERE.name == "scripts" else HERE
if (ROOT / "web-rediseno").is_dir():
    ROOT = ROOT / "web-rediseno"
SIZES = {
    "assets/guitarra-derecha.webp": (1024, 1835),
    "assets/guitarra-izquierda.webp": (1024, 1835),
    "assets/clavijero.webp": (1024, 1835),
    "assets/marca.webp": (1200, 896),
    "assets/logo.webp": (520, 388),
}

for path in sorted(ROOT.glob("*.html")):
    text = path.read_text(encoding="utf-8")
    original = text

    def repl(match):
        tag = match.group(0)
        src = re.search(r'src="(assets/[^"]+\.webp)"', tag)
        if src and src.group(1) in SIZES:
            w, h = SIZES[src.group(1)]
            tag = re.sub(r'width="\d+"', f'width="{w}"', tag, count=1)
            tag = re.sub(r'height="\d+"', f'height="{h}"', tag, count=1)
        return tag

    text = re.sub(r"<img\b[^>]*>", repl, text)
    if text != original:
        path.write_text(text, encoding="utf-8")
        print("actualizado", path.name)
print("listo")
