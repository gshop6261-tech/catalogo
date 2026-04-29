# GlobalShop Catalog - Cloud Memory

**Última actualización:** 2026-04-29 10:20 GMT-3

## Estado del Proyecto

### Stack Tecnológico
- **Frontend:** HTML5 + CSS3 + Vanilla JS (no frameworks)
- **Backend:** Python (scripts/scrapers), GitHub Actions (CI/CD)
- **Data:** JSON (`data/productos.json`, `data/import-schedules.json`)
- **Hosting:** GitHub Pages (index.html), Admin panel (admin.html)
- **Scraping:** Playwright (headless browser para Atacado Connect), BeautifulSoup (fallback)

---

## Arquitectura del Proyecto

### Estructura de Directorios
```
.
├── index.html                  # Catálogo público (3,414 líneas)
├── admin.html                  # Panel administrativo (3,967 líneas)
├── sw.js                       # Service Worker
├── data/
│   ├── productos.json          # Datos de productos (master)
│   ├── import-schedules.json   # Configuración de scraping
│   └── [fallbacks...]
├── scripts/
│   ├── scrapers/
│   │   ├── atacado.py          # Scraper principal (Atacado Connect)
│   │   └── [otros scrapers]
│   ├── import_category.py      # Importador de categorías
│   └── requirements.txt        # Dependencias Python
├── images/
│   └── productos/              # Imágenes por ID (almacenadas en git)
└── .github/workflows/
    ├── import-category.yml     # Ejecuta import_category.py
    ├── check-price.yml         # Valida precios antes de importar
    ├── enrich.yml              # Enriquece datos de productos
    └── [otros workflows]
```

---

## Funcionalidades Implementadas

### Catálogo Público (index.html)
✅ **Paginación:** 20/50/100 productos por página (defecto 20)
✅ **Búsqueda:** Búsqueda real-time con debounce 180ms
✅ **Categorías:** Sistema de categorías dinámicas + subcategorías
✅ **Filtros:** Estado (activo/inactivo), precio, disponibilidad
✅ **Carrito:** Integración WhatsApp (modal con resumen)
✅ **Slider:** Hero section con 4 imágenes rotativas (3s intervalo)
✅ **Responsivo:** Mobile-first design, se adapta a todos los tamaños

### Admin Panel (admin.html)
✅ **CRUD Productos:** Crear, leer, actualizar, eliminar
✅ **Paginación:** 20/50/100 productos por página (defecto 20)
✅ **Búsqueda + Filtros:** Por nombre, categoría, estado (activo/inactivo)
✅ **Gestión de Precios:** Edición de precios ARS/USD, historial de cambios
✅ **Tokens Deactivation:** Marcar productos como "deactivation-metadata" 
✅ **Autenticación:** Auth local (email + pin almacenados en localStorage)
✅ **Importación:** Importar desde URL JSON o archivo
✅ **Exportación:** Descargar JSON de productos

### Scraping & Importación
✅ **Atacado Connect Scraper:** Playwright headless browser, paginación de 113 páginas (~2,256 productos)
✅ **Categoría Scraper:** Scrape dinámica de categorías (scrape_category() en atacado.py)
✅ **import_category.py:** Importador automático de categorías + validación de precios
✅ **GitHub Actions:** Workflows que ejecutan import_category.py en horarios programados
✅ **Validación:** check-price.yml verifica precios antes de hacer merge

---

## Procesos Clave

### Flujo de Importación de Productos
1. **Configuración:** `data/import-schedules.json` define qué categorías scrapearpor cuándo
2. **Scraping:** `import_category.py` ejecuta `scrape_category(category_name)` desde `atacado.py`
3. **Validación:** Compara precios vs. mercado, detecta outliers
4. **Almacenamiento:** Actualiza `data/productos.json` y guarda imágenes en `images/productos/{id}/`
5. **Deploy:** GitHub Actions crea commit automático y push a main

### Configuración de Scrapers (import-schedules.json)
```json
{
  "celulares": { "url": "...", "nextRun": "2026-04-29T16:30:00Z", "interval": 86400 },
  "belleza": { "url": "...", "nextRun": "2026-04-30T08:00:00Z", "interval": 172800 }
}
```

### Workflows GitHub Actions
| Workflow | Trigger | Función |
|----------|---------|---------|
| `import-category.yml` | Cron + manual | Ejecuta import_category.py |
| `check-price.yml` | Automático (antes de merge) | Valida precios |
| `enrich.yml` | Manual | Enriquece metadata de productos |

---

## Schema de Datos (Producto)

```json
{
  "id": 100,
  "name": "iPhone 15 Pro",
  "cat": "Celulares",
  "publicSub": "Apple",           // Subcategoría pública
  "sub": "Smartphones Premium",   // Categoría interna (no pública)
  "desc": "Descripción del producto",
  "icon": "📱",
  "img": "URL de imagen principal",
  "images": ["url1", "url2"],     // Array de imágenes
  "ars": "500000",                // Precio en pesos
  "usd": "1200",                  // Costo USD (interno)
  "usdSell": "1500",              // Precio venta USD
  "activo": true,
  "badge": "Oferta",
  "badgeColor": "#FF6B6B",
  "status": "active",             // "pending" | "error" | "active"
  "deactivation_metadata": {}     // Metadata para desactivación
}
```

---

## Notas Importantes (⚠️ Gotchas)

### Scraping Atacado Connect
- ❌ **NO usar `?page=N` en URLs:** El servidor devuelve siempre los mismos 20 productos
- ✅ **USAR Playwright headless:** Espera el JS rendering completo (networkidle + domcontentloaded)
- ⏱️ **Timeout:** 45-60s por página (son lentos)
- 📊 **Paginación:** 113 páginas × 20 productos = ~2,256 artículos

### Precios
- **ARS:** Mostrados en catálogo (precio comprador)
- **USD:** Costo interno + margin = usdSell (si existe)
- ⚠️ **Validación:** check-price.yml detecta si ARS es outlier respecto a USD

### Imagenes
- Se guardan en `images/productos/{id}/` 
- **Formato:** JPEG de URLs scrapeadas
- **Limite:** GitHub LFS si excede 100MB

### Autenticación Admin
- Email/PIN almacenados en localStorage (NO en server)
- ⚠️ **INSEGURO para producción:** Considerar OAuth/JWT en futuro
- Session timeout: Manual (sin logout automático)

---

## Cambios Recientes (Abril 2026)

### 2026-04-29 (Hoy)
- ✅ **Paginación:** Implementada en index.html (20/50/100) + admin.html
- ✅ **Selector visual:** Integrado en grid-meta (catálogo) y toolbar (admin)
- ✅ **Navegación:** Botones prev/next + números de página con "…" en rangos largos
- ✅ **Reset automático:** Página 1 cuando cambian búsqueda/categoría/filtros

### 2026-04-28
- ✅ Playwright scraper: Función `scrape_category()` reescrita para paginación real
- ✅ `import_category.py`: Importador automático con validación de precios
- ✅ `import-category.yml`: Workflow que ejecuta importador en horarios programados
- ✅ `data/import-schedules.json`: Configuración centralizada de categorías a scrapearp

### 2026-04-27
- ✅ Vendor feature: Plan + arquitectura diseñada (no implementada)
- ✅ Security: Auth fixes + XSS prevention

---

## TODO / Próximas Acciones

### High Priority
- [ ] Probar paginación en navegador (golden path + edge cases)
- [ ] Validar que scroll a catalogo funciona suave
- [ ] Revisar responsive en mobile (pantalla pequeña)

### Medium Priority
- [ ] OAuth/JWT para admin panel (reemplazar localStorage)
- [ ] Caché local (IndexedDB) para productos
- [ ] Optimizar imágenes (WebP, lazy loading mejorado)

### Low Priority (Tech Debt)
- [ ] Refactor state management (podría usar Zustand si crece)
- [ ] Separar JS en módulos (actualmente todo en <script> inline)
- [ ] Migrar a TypeScript
- [ ] Tests (Jest, Playwright E2E)

---

## Optimización de Tokens

**Para futuras sesiones:** SIEMPRE leer `cloud.md` ANTES de hacer análisis del código.

### Lo que ya sabemos (evitar re-leer):
- ✅ Estructura HTML: 3400+ líneas (usar smart_outline en lugar de Read)
- ✅ Schemas de datos: Documentados aquí ↑
- ✅ Workflows: Listados en tabla arriba ↑
- ✅ Procesos: Paso a paso documentado aquí ↑

### Lo que probablemente necesitaremos investigar:
- Cambios en `productos.json` (leer antes de cualquier edit)
- Nuevos scrapers (leer requirements.txt + script)
- Bugs específicos (usar Grep + smart_search)

---

## Comandos Útiles

```bash
# Scraping
python scripts/scrapers/atacado.py  # Test del scraper
python scripts/import_category.py --dry-run  # Test sin guardar

# Git
git log --oneline | head -20
git status

# Local testing (si hay server)
python -m http.server 8000
```

---

## Contacto / Dueño
**Usuario:** ShopyGlobal  
**Email:** shopyglobalarg@gmail.com  
**Git:** main branch  
**Notas:** Proyecto activo, cambios semanales
