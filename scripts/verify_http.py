"""Verifica que todas las imágenes referenciadas se sirven por HTTP con estado 200."""
from pathlib import Path
import re
import urllib.request

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent if HERE.name == "scripts" else HERE
if (ROOT / "web-rediseno").is_dir():
    ROOT = ROOT / "web-rediseno"
BASE = "http://localhost:8123"

for page in sorted(ROOT.glob("*.html")):
    refs = set()
    text = page.read_text(encoding="utf-8")
    for rel in re.findall(r'(?:src|href)="(assets/[^"]+\.(?:webp|png|jpg))"', text):
        refs.add(rel)
    bad = []
    for rel in refs:
        try:
            req = urllib.request.Request(BASE + "/" + rel, method="HEAD")
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status != 200:
                    bad.append((rel, resp.status))
        except Exception as exc:
            bad.append((rel, str(exc)))
    print(f"{page.name}: {len(refs)} imágenes, {len(bad)} fallos", bad[:3] if bad else "")
