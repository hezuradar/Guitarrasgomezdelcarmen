# Guitarras Gómez del Carmen

Sitio estático del taller de lutería Gómez del Carmen (La Torre de Esteban Hambrán, Toledo). Rediseño editorial con todo el contenido original: guitarras, proceso de construcción, guitarristas, servicios de barnizado y reparación, agradecimientos y noticias.

## Páginas

| Archivo | Contenido |
|---|---|
| `index.html` | Inicio, «Sobre mí» y guitarras destacadas |
| `productos.html` | Catálogo de guitarras flamencas y clásicas |
| `construccion.html` | Construcción artesanal |
| `guitarristas.html` | Fotos y vídeos agrupados por intérprete |
| `servicio.html` | Barnizado y reparación |
| `agradecimientos.html` | Agradecimientos |
| `blog-cartuja.html` | Noticia: Cartuja Center de Sevilla |
| `blog-primera-noche.html` | Noticia: primera noche en un concierto |
| `contacto.html` | Contacto (formulario estático con `mailto:`) |

## Estructura

```
.
├── *.html            Páginas del sitio
├── css/styles.css    Sistema de diseño y estilos
├── js/main.js        Menú móvil, lightbox, reveal y año actual
├── assets/           Imágenes WebP (logo, guitarras y fotos en img/)
└── scripts/          Scripts de optimización y verificación
```

No hay backend ni dependencias de compilación: es HTML, CSS y JavaScript puro. Las fuentes se cargan desde Google Fonts (`Cormorant Garamond` + `Manrope`).

## Ver el sitio en local

```bash
python -m http.server 8123
```

Abre <http://localhost:8123/>. Si ya habías visitado la página, recarga con **Ctrl+F5** para evitar la caché del navegador.

## Publicar con GitHub Pages

1. En el repositorio: **Settings → Pages**.
2. **Build and deployment → Source: Deploy from a branch**.
3. Selecciona la rama `main` y la carpeta `/ (root)`, y guarda.
4. La URL será `https://hezuradar.github.io/Guitarrasgomezdelcarmen/`.

El sitio usa rutas relativas, así que funciona tanto en la raíz como en una subcarpeta de Pages.

## Imágenes

Todas las imágenes servidas son WebP locales (158 archivos válidos, ~9,6 MB en total). Los PNG originales de `assets/` se conservan como copia de seguridad, pero **no se cargan** desde el HTML. Las fotos del antiguo CDN externo se descargaron y optimizaron, de modo que el sitio no depende de `primary.jwwb.nl`.

Para regenerarlas o verificarlas (requiere Python 3 y Pillow):

```bash
pip install Pillow
python scripts/optimize_images.py   # convierte PNG/fotos a WebP y reescribe el HTML
python scripts/fix_dims.py          # corrige width/height de las imágenes locales
python scripts/verify_images.py     # comprueba referencias y validez de los WebP
python scripts/verify_http.py       # comprueba HTTP 200 (con el servidor en :8123)
```

## Contacto

- Correo: <mailto:macose_to@yahoo.es>
- Teléfono / WhatsApp: <tel:+34687407964>
- Dirección: Mártires 31, 45920 La Torre de Esteban Hambrán (Toledo)
- Redes: Instagram, Facebook, YouTube y WhatsApp (enlaces en el pie de todas las páginas)
