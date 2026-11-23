"""Optimiza todas las imágenes del rediseño a WebP y reescribe el HTML.

Uso: python optimize_images.py
- Convierte los PNG locales de assets/ a WebP (redimensionados a tamaño de pantalla ~2x).
- Descarga las imágenes remotas de primary.jwwb.nl, las convierte a WebP y las guarda en assets/img/.
- Reescribe src/href en los HTML, añade width/height (evita CLS) y decoding="async".
"""

from __future__ import annotations

import hashlib
import html as html_mod
import io
import re
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from PIL import Image, ImageOps

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent if HERE.name == "scripts" else HERE
if (ROOT / "web-rediseno").is_dir():  # también funciona desde la carpeta de trabajo original
    ROOT = ROOT / "web-rediseno"
ASSETS = ROOT / "assets"
REMOTE_DIR = ASSETS / "img"
REMOTE_DIR.mkdir(parents=True, exist_ok=True)
HTML_FILES = sorted(ROOT.glob("*.html"))

REMOTE_RE = re.compile(r'https://primary\.jwwb\.nl[^"\'\s<>]+')

# PNG locales: ancho máximo en px (suficiente para pantallas 2x) y calidad
LOCAL_SPECS = {
    "logo.png": {"width": 520, "lossless": True},
    "marca.png": {"width": 1200, "lossless": False, "quality": 92},
    "clavijero.png": {"width": 1024, "lossless": False, "quality": 90},
    "guitarra-derecha.png": {"width": 1024, "lossless": False, "quality": 90},
    "guitarra-izquierda.png": {"width": 1024, "lossless": False, "quality": 90},
}


def kb(n: int) -> str:
    return f"{n / 1024:,.0f} KB"


def optimize_local() -> dict[str, str]:
    """PNG -> WebP. Devuelve mapping nombre_original -> ruta webp relativa."""
    mapping: dict[str, str] = {}
    print("== Imágenes locales ==")
    for name, spec in LOCAL_SPECS.items():
        src = ASSETS / name
        if not src.exists():
            print(f"  ! No existe {name}")
            continue
        out = ASSETS / (src.stem + ".webp")
        with Image.open(src) as img:
            img = ImageOps.exif_transpose(img).convert("RGBA")
            original_size = img.size
            if img.width > spec["width"]:
                img.thumbnail((spec["width"], 100_000), Image.LANCZOS)
            if spec.get("lossless"):
                img.save(out, "WEBP", lossless=True, method=6)
            else:
                img.save(
                    out,
                    "WEBP",
                    quality=spec.get("quality", 90),
                    method=6,
                    exact=True,
                )
        mapping[name] = f"assets/{out.name}"
        before, after = src.stat().st_size, out.stat().st_size
        print(
            f"  {name}: {original_size[0]}x{original_size[1]} -> "
            f"{img.size[0]}x{img.size[1]}  {kb(before)} -> {kb(after)} "
            f"({100 - after * 100 / before:.1f}% menos)"
        )
    return mapping


def collect_remote_urls() -> set[str]:
    urls: set[str] = set()
    for path in HTML_FILES:
        text = path.read_text(encoding="utf-8")
        for raw in REMOTE_RE.findall(text):
            urls.add(html_mod.unescape(raw))
    return urls


def asset_name(url: str) -> str:
    path = urllib.parse.urlsplit(url).path
    filename = path.rsplit("/", 1)[-1] or "imagen.jpg"
    stem = re.sub(r"[^A-Za-z0-9._-]+", "-", Path(filename).stem)[:48]
    digest = hashlib.md5(url.encode("utf-8")).hexdigest()[:8]
    return f"{stem}-{digest}.webp"


def download(url: str) -> bytes:
    last: Exception | None = None
    for _ in range(3):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
                },
            )
            with urllib.request.urlopen(req, timeout=45) as resp:
                return resp.read()
        except Exception as exc:  # reintento
            last = exc
    raise RuntimeError(f"No se pudo descargar {url}: {last}")


def optimize_remote(url: str) -> tuple[str, str, tuple[int, int], int, int]:
    data = download(url)
    name = asset_name(url)
    out = REMOTE_DIR / name
    with Image.open(io.BytesIO(data)) as raw:
        img = ImageOps.exif_transpose(raw).convert("RGB")
        size = img.size
        img.save(out, "WEBP", quality=88, method=6)
    return url, f"assets/img/{name}", size, len(data), out.stat().st_size


def main() -> None:
    local_map = optimize_local()

    urls = collect_remote_urls()
    print(f"\n== Imágenes remotas: {len(urls)} URLs únicas ==")

    records: dict[str, tuple[str, tuple[int, int], int, int]] = {}
    failed: list[str] = []
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = {pool.submit(optimize_remote, u): u for u in urls}
        for i, future in enumerate(as_completed(futures), 1):
            url = futures[future]
            try:
                url, rel, size, before, after = future.result()
                records[url] = (rel, size, before, after)
            except Exception as exc:
                failed.append(str(exc))
            if i % 20 == 0 or i == len(urls):
                print(f"  procesadas {i}/{len(urls)}")

    total_before = sum(v[2] for v in records.values())
    total_after = sum(v[3] for v in records.values())
    print(
        f"  total remoto: {kb(total_before)} -> {kb(total_after)} "
        f"({100 - total_after * 100 / total_before:.1f}% menos)"
    )
    if failed:
        print("  FALLOS:")
        for err in failed:
            print("   ", err)

    # Mapping con URL codificada y decodificada para reescribir HTML
    rewrite: dict[str, tuple[str, tuple[int, int]]] = {}
    for url, (rel, size, _, _) in records.items():
        rewrite[url] = (rel, size)
        rewrite[html_mod.escape(url, quote=True)] = (rel, size)

    def replace_img(match: re.Match[str]) -> str:
        tag = match.group(0)
        src_match = re.search(r'\bsrc="([^"]+)"', tag)
        if not src_match:
            return tag
        key = src_match.group(1)
        if key not in rewrite:
            return tag
        rel, (w, h) = rewrite[key]
        tag = tag.replace(f'src="{key}"', f'src="{rel}"')
        if "decoding=" not in tag:
            tag = tag.replace("<img ", '<img decoding="async" ', 1)
        if re.search(r"\bwidth=", tag) is None:
            tag = tag.replace("<img ", f'<img width="{w}" height="{h}" ', 1)
        return tag

    def replace_anchor(match: re.Match[str]) -> str:
        tag = match.group(0)
        href_match = re.search(r'\bhref="([^"]+)"', tag)
        if not href_match:
            return tag
        key = href_match.group(1)
        if key not in rewrite:
            return tag
        rel, _ = rewrite[key]
        return tag.replace(f'href="{key}"', f'href="{rel}"')

    print("\n== Reescritura de HTML ==")
    for path in HTML_FILES:
        text = path.read_text(encoding="utf-8")
        original = text
        text = re.sub(r"<img\b[^>]*>", replace_img, text)
        text = re.sub(r"<a\b[^>]*>", replace_anchor, text)
        # PNG locales -> WebP
        for name, rel in local_map.items():
            text = text.replace(f"assets/{name}", rel)
        if text != original:
            path.write_text(text, encoding="utf-8")
            print(f"  {path.name}: actualizado")
        else:
            print(f"  {path.name}: sin cambios")

    print("\nListo.")


if __name__ == "__main__":
    main()
