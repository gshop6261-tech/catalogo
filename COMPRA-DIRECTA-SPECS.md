# COMPRA DIRECTA · Global Shop
## Especificaciones Técnicas Completas para Desarrollo

---

## 1. DESCRIPCIÓN DEL PROYECTO

**Nombre:** Compra Directa by Global Shop  
**Tipo:** Catálogo digital de ventas con panel de administración  
**Canal principal:** WhatsApp Business  
**Mercado:** Argentina (AMBA + Interior del país)  
**Número WhatsApp:** +54 9 11 5412-5271  

---

## 2. ARQUITECTURA GENERAL

El sistema se compone de tres módulos:

### 2.1 Catálogo público (`index.html`)
- Página web responsive optimizada para mobile
- Sin login requerido para el cliente
- Todos los botones abren WhatsApp con mensaje pre-escrito
- Debe funcionar como PWA (Progressive Web App) para instalarse en el celular

### 2.2 Panel de administración (`admin.html`)
- Acceso con contraseña (solo Rubén y su equipo)
- Alta, baja y modificación de productos
- Actualización de precios en tiempo real
- Gestión de banners del hero carousel
- Vista previa del catálogo antes de publicar

### 2.3 Calculadora de precios (`calculadora.html`)
- Uso interno del equipo de ventas
- Calcula precio final en pesos automáticamente
- Cotización del dólar en tiempo real
- Acceso con contraseña

---

## 3. DISEÑO Y UX

### 3.1 Estilo visual
- **Referencia:** Shopify / tiendas premium
- **Fondo:** Blanco / gris claro (#f5f5f7) — NO fondo negro
- **Acento principal:** Verde WhatsApp (#25D366)
- **Fuente:** Inter (Google Fonts)
- **Estilo:** Limpio, moderno, legible, con vida — NO oscuro ni básico

### 3.2 Estructura del catálogo público

```
[HERO CAROUSEL]         ← banners de productos, pasan solos cada 4.5s
[TRUST BAR]             ← barra animada con mensajes de confianza
[HEADER STICKY]         ← logo + buscador + filtros de categoría + botón WhatsApp
[GRID DE PRODUCTOS]     ← tarjetas de productos
[SECCIÓN COMO FUNCIONA] ← pasos del proceso
[FORMAS DE PAGO]        ← iconos y métodos
[ENVÍOS]                ← info de entrega
[GARANTÍA]              ← política completa
[FOOTER]                ← datos de contacto
[BARRA FIJA INFERIOR]   ← botón consultar siempre visible
```

### 3.3 Hero Carousel
- Imágenes de fondo de pantalla completa (100% ancho)
- Altura: 220px mobile / 400px desktop
- Filtro de oscuridad: máximo 30% (que se vean bien las imágenes)
- Texto sobre la imagen: tag + título + subtítulo + botón CTA amarillo (#FFD600)
- Navegación: flechas laterales + dots inferiores
- Auto-play: cada 4.5 segundos
- Administrable desde el panel

### 3.4 Tarjetas de producto
```
[IMAGEN DEL PRODUCTO]   ← 160px alto, object-fit: contain, fondo blanco
[BADGE opcional]        ← Nuevo / Oferta / Top ventas / Premium / Destacado
[CATEGORÍA]
[NOMBRE]
[SPECS CORTOS]
[DESCRIPCIÓN]
[PRECIO EN PESOS]       ← o "Consultar" si no tiene precio cargado
[BOTÓN WHATSAPP]        ← abre WA con mensaje pre-escrito
```

---

## 4. CATEGORÍAS DE PRODUCTOS

- Celulares
- Smart TV
- Audio
- Computación
- Accesorios
- Hogar
- (Administrable — se pueden agregar desde el panel)

---

## 5. CAMPOS DE CADA PRODUCTO

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | número | Único, autoincrementable |
| cat | texto | Categoría del producto |
| name | texto | Nombre completo |
| sub | texto | Specs cortos (ej: 512GB · 12GB RAM · 6.8") |
| desc | texto | Descripción breve de beneficios |
| img | texto | URL de imagen o base64 |
| badge | texto / null | Etiqueta visible en la tarjeta |
| badgeColor | hex | Color del badge |
| icon | emoji | Respaldo si no carga la imagen |
| ars | texto / null | Precio en pesos. null = "Consultar" |
| usd | número | Costo en USD (solo visible en panel admin) |
| activo | boolean | true = visible en catálogo |
| fechaAlta | fecha | Registro automático |

---

## 6. FORMAS DE PAGO

- Efectivo
- Transferencia bancaria
- MercadoPago
- USDT (cripto)
- Tarjetas: NO disponible por ahora

**Sin recargos ni descuentos por método de pago.**

---

## 7. PROCESO DE ENTREGA

1. Cliente elige producto y consulta por WhatsApp
2. Confirma el pago
3. Se procesa el pedido
4. En **5 días hábiles** el producto está listo
5. Se envía **foto del producto embalado** con los datos del comprador
6. Despacho según zona

**AMBA:** Entrega a domicilio o punto de encuentro según zona  
**Interior del país:** Envío por correo o encomienda  
**Costo de envío:** A cargo del comprador — se abona en destino o en sucursal

---

## 8. POLÍTICA DE GARANTÍA Y DEVOLUCIONES

### Devoluciones
- Plazo: **3 días hábiles** desde la recepción
- El producto debe estar en las **mismas condiciones** que fue entregado
- Se reintegra el costo del producto — el flete **NO** se reintegra
- La foto del embalaje es el registro oficial del estado al momento de entrega

### Garantía por falla
- Plazo: **90 días** desde la entrega
- Cubre: defectos de fábrica únicamente
- NO cubre: productos usados, golpeados o con signos de uso
- Resolución: cambio directo — nosotros resolvemos primero
- Evaluación: departamento técnico interno
- Marcas con garantía internacional (Apple, Samsung, etc.): se gestiona con el centro de servicio autorizado

---

## 9. CALCULADORA DE PRECIOS (USO INTERNO)

### 9.1 Fórmulas por categoría

#### Celulares ≤ U$D 300
| Tipo | Fórmula |
|------|---------|
| Caja slim (sin cargador) | (costo + U$D 6) × cotización × 1.08 |
| Caja gruesa (con cargador) | (costo + U$D 4) × cotización × 1.10 |

#### Celulares > U$D 300
| Tipo | Fórmula |
|------|---------|
| Caja slim | costo × cotización × 1.08 |
| Caja gruesa | costo × cotización × 1.10 |

#### Electrónica / Audio / Accesorios
| Tipo | Fórmula |
|------|---------|
| Chico (caja zapatilla) | costo × cotización × 1.20 |
| Grande (robot vacuum+) | costo × cotización × 1.25 |

#### Hogar
| Tipo | Fórmula |
|------|---------|
| Todo | costo × cotización × 1.25 |

> **NOTA:** Los porcentajes ya incluyen flete + ganancia. No se aplica ningún factor adicional.  
> El precio final se redondea al 100 más cercano hacia arriba.

### 9.2 Cotización del dólar
- Se trae automáticamente de `https://dolarapi.com/v1/dolares/blue`
- Fallback: `https://api.bluelytics.com.ar/v2/latest`
- Se muestra como "Dólar" sin especificar tipo
- Campo manual editable como respaldo si no hay conexión
- Se actualiza cada 5 minutos

---

## 10. PANEL DE ADMINISTRACIÓN

### 10.1 Acceso
- URL: `/admin`
- Contraseña: definida por Rubén al momento del deploy
- Sin registro público — solo acceso interno

### 10.2 Funcionalidades requeridas

#### Gestión de productos
- [ ] Listar todos los productos (activos e inactivos)
- [ ] Agregar producto nuevo (formulario con todos los campos)
- [ ] Editar producto existente
- [ ] Activar / desactivar producto (sin borrar)
- [ ] Subir imagen del producto
- [ ] Vista previa de cómo queda la tarjeta antes de guardar

#### Gestión de precios
- [ ] Actualizar precio en pesos (ars) de cualquier producto
- [ ] Marcar precio como "Consultar" (null)
- [ ] Actualización masiva de precios (cuando cambia el dólar)
- [ ] Historial de cambios de precio por producto

#### Gestión de banners
- [ ] Agregar banner al hero carousel
- [ ] Subir imagen del banner
- [ ] Editar texto, tag y link del botón CTA
- [ ] Reordenar banners (drag & drop)
- [ ] Activar / desactivar banner

#### Dashboard
- [ ] Total de productos activos por categoría
- [ ] Últimos productos agregados
- [ ] Cotización del dólar en tiempo real

---

## 11. FORMULARIO DE REGISTRO DE CLIENTES

### 11.1 Campos del formulario
- Nombre y apellido *
- WhatsApp *
- Zona / Localidad *
- Tipo de cliente: Particular / Comercio / Revendedor *
- Producto de interés (opcional)
- ¿Cómo nos conociste? (opcional)

### 11.2 Aviso de privacidad
Texto a mostrar antes del envío:

> "Tus datos son confidenciales. Global Shop no los comparte con terceros ni los utiliza con fines comerciales ajenos a tu compra. Solo los usamos para mantenerte informado de nuestros productos y novedades. Podés solicitar la eliminación de tus datos en cualquier momento escribiéndonos por WhatsApp."

### 11.3 Funcionamiento
- Al enviar el formulario se abre WhatsApp con todos los datos pre-escritos
- Los datos llegan al número +54 9 11 5412-5271
- En el panel admin se pueden ver todos los registros
- Exportable a CSV para campañas de difusión

---

## 12. TRUST BAR (BARRA ANIMADA)

Mensajes que corren en loop:
- 🚚 Envíos a todo el país
- ✅ Productos originales
- 💬 Atención por WhatsApp
- ⚡ 5 días hábiles
- 🔒 Compra segura
- 🌎 Importación directa
- 🔄 Cambio directo en garantía
- 📸 Foto del embalaje incluida
- 💵 Efectivo · Transferencia · MP · USDT

---

## 13. MENSAJE DE WHATSAPP POR PRODUCTO

Cuando el cliente toca "Quiero este producto":

```
Hola! Me interesa [NOMBRE DEL PRODUCTO]. 
¿Cuál es el precio y disponibilidad?
```

Cuando el cliente toca "Consultar" (general):
```
Hola! Quiero consultar el catálogo 🛒
```

---

## 14. DEPLOY Y HOSTING

### Opción recomendada: GitHub Pages (gratuito)
1. Crear repositorio público en github.com
2. Subir `index.html` (renombrar desde compra-directa.html)
3. Activar GitHub Pages en Settings → Pages
4. URL resultante: `https://USUARIO.github.io/catalogo`

### URL final se usa en:
- Perfil de WhatsApp Business como sitio web
- Mensajes automáticos de bienvenida
- Respuestas rápidas del equipo de ventas
- Estados de WhatsApp
- Grupos de clientes

---

## 15. ARCHIVOS ENTREGADOS

| Archivo | Descripción |
|---------|-------------|
| `compra-directa.html` | Catálogo público completo con banners, productos, formas de pago, garantía |
| `calculadora.html` | Calculadora de precios con dólar en tiempo real |
| `INSTRUCCIONES.html` | Manual de operación para el equipo |
| `COMPRA-DIRECTA-SPECS.md` | Este documento — specs completas para el programador |

---

## 16. STACK TECNOLÓGICO ACTUAL

- HTML5 puro
- CSS3 (sin frameworks)
- JavaScript vanilla (sin librerías)
- Sin backend ni base de datos — todo client-side
- Compatible con todos los navegadores modernos

### Stack sugerido para el panel de administración
- **Frontend:** React o HTML/JS puro
- **Backend:** Node.js + Express o Firebase
- **Base de datos:** Firebase Firestore (recomendado por simplicidad) o SQLite
- **Hosting:** GitHub Pages (catálogo) + Railway o Render (panel admin)
- **Imágenes:** Cloudinary (hosting gratuito de imágenes)

---

## 17. NOTAS IMPORTANTES PARA EL PROGRAMADOR

1. **Las fórmulas de precios son confidenciales** — no deben ser visibles en el código del cliente. Solo en el panel admin con contraseña.

2. **El porcentaje de ganancia (10% en electro)** está hardcodeado en la calculadora. No debe aparecer en ninguna pantalla pública.

3. **Los precios en USD de los productos** son de uso interno. El catálogo público solo muestra el precio en pesos o "Consultar".

4. **La procedencia de los productos** (Paraguay, Brasil, China, Miami) no debe mencionarse en ningún lugar del catálogo público.

5. **Las imágenes de los banners** están actualmente en base64 dentro del HTML. Para producción se recomienda subirlas a Cloudinary y referenciarlas por URL.

6. **El número de WhatsApp** está hardcodeado como `5491154125271` en múltiples lugares del HTML. Al migrar al panel, debe ser una variable global configurable.

---

*Documento generado por Claude (Anthropic) en sesión de trabajo con Rubén — Global Shop Argentina*  
*Fecha: Abril 2026*
