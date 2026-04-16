#!/usr/bin/env python3
"""
One-shot migration: converts admin.html export JSON to data/productos.json format.
Usage:
  python scripts/migrate_to_json.py                    # uses DEFAULT data
  python scripts/migrate_to_json.py export.json        # uses exported file from admin.html
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "data" / "productos.json"


def migrate_product(p: dict) -> dict:
    img = p.get("img")
    return {
        **p,
        "images": [img] if img else [],
        "referenceLinks": [],
        "status": "enriched",
        "enrichError": None,
    }


def build_default() -> dict:
    products = [
        {"id": 1, "cat": "Celulares", "name": "iPhone 15 Pro 256GB", "sub": "256GB · Titanio · 6.1\" · USB-C", "desc": "Chip A17 Pro, cámara 48MP, Dynamic Island, USB-C.", "img": None, "badge": "Top ventas", "badgeColor": "#25D366", "icon": "📱", "ars": "1450000", "usd": 550, "activo": True, "fechaAlta": "2026-04-01", "priceHistory": [{"ars": "1450000", "date": "2026-04-01"}]},
        {"id": 2, "cat": "Celulares", "name": "Samsung Galaxy S24 128GB", "sub": "128GB · Phantom Black · 6.2\" · IP68", "desc": "Galaxy AI, cámara 50MP, Snapdragon 8 Gen 3.", "img": None, "badge": "Nuevo", "badgeColor": "#5856D6", "icon": "📲", "ars": "980000", "usd": 320, "activo": True, "fechaAlta": "2026-04-05", "priceHistory": [{"ars": "980000", "date": "2026-04-05"}]},
        {"id": 3, "cat": "Smart TV", "name": "Smart TV Samsung 55\" 4K QLED", "sub": "55\" · 4K UHD · QLED · Tizen", "desc": "Crystal 4K, HDR10+, 3x HDMI, streaming nativo.", "img": None, "badge": "Oferta", "badgeColor": "#FF3B30", "icon": "📺", "ars": "650000", "usd": 210, "activo": True, "fechaAlta": "2026-03-20", "priceHistory": [{"ars": "650000", "date": "2026-03-20"}]},
        {"id": 4, "cat": "Audio", "name": "AirPods Pro 2da Gen (USB-C)", "sub": "USB-C · ANC · MagSafe", "desc": "Cancelación activa de ruido, chip H2, 30h de batería.", "img": None, "badge": "Premium", "badgeColor": "#FF9500", "icon": "🎧", "ars": "320000", "usd": 110, "activo": True, "fechaAlta": "2026-04-01", "priceHistory": [{"ars": "320000", "date": "2026-04-01"}]},
        {"id": 5, "cat": "Computación", "name": "MacBook Air M2 8GB/256GB", "sub": "M2 · 8GB · 256GB SSD · 13.6\"", "desc": "Chip M2, Liquid Retina, 18h batería, sin ventiladores.", "img": None, "badge": "Destacado", "badgeColor": "#007AFF", "icon": "💻", "ars": None, "usd": 780, "activo": True, "fechaAlta": "2026-04-10", "priceHistory": []},
        {"id": 6, "cat": "Hogar", "name": "Robot Aspirador Xiaomi S10", "sub": "4000 Pa · LiDAR · Trapeado", "desc": "Navegación LiDAR, 4000Pa, trapeado simultáneo, app Mi Home.", "img": None, "badge": "Nuevo", "badgeColor": "#34C759", "icon": "🤖", "ars": "280000", "usd": 90, "activo": True, "fechaAlta": "2026-04-12", "priceHistory": [{"ars": "280000", "date": "2026-04-12"}]},
    ]

    banners = [
        {"id": 1, "tag": "✨ Importación directa", "title": "Celulares", "accent": "premium", "sub": "iPhone, Samsung y más. Originales.", "cta": "Ver celulares ↓", "filter": "Celulares", "grad": "linear-gradient(135deg,#080e1e 0%,#0f1e38 60%,#162960 100%)", "emoji": "📱", "activo": True},
        {"id": 2, "tag": "🔥 Los más pedidos", "title": "Smart TV", "accent": "4K Ultra HD", "sub": "Samsung, LG y Hisense. 55\" y 65\".", "cta": "Ver Smart TVs ↓", "filter": "Smart TV", "grad": "linear-gradient(135deg,#080f0a 0%,#0c2212 60%,#103a1a 100%)", "emoji": "📺", "activo": True},
        {"id": 3, "tag": "🎵 Audio premium", "title": "Sonido que", "accent": "enamora", "sub": "AirPods, JBL y headphones premium.", "cta": "Ver Audio ↓", "filter": "Audio", "grad": "linear-gradient(135deg,#130828 0%,#220e45 60%,#31186a 100%)", "emoji": "🎧", "activo": True},
        {"id": 4, "tag": "🇦🇷 Todo Argentina", "title": "Compra", "accent": "directo", "sub": "Envíos AMBA e interior del país.", "cta": "Consultar 💬", "filter": "", "grad": "linear-gradient(135deg,#101010 0%,#1a1a1a 60%,#232323 100%)", "emoji": "🛒", "activo": True},
    ]

    categories = [
        {"id": "celulares", "name": "Celulares", "icon": "📱", "subtypes": [{"id": "slim", "label": "Caja slim (sin cargador)"}, {"id": "gruesa", "label": "Caja gruesa (con cargador)"}], "rules": [{"subtype": "slim", "type": "price", "op": "<=", "val": 300, "margin": 8, "add": 6}, {"subtype": "slim", "type": "price", "op": ">", "val": 300, "margin": 8, "add": 0}, {"subtype": "gruesa", "type": "price", "op": "<=", "val": 300, "margin": 10, "add": 4}, {"subtype": "gruesa", "type": "price", "op": ">", "val": 300, "margin": 10, "add": 0}]},
        {"id": "smart-tv", "name": "Smart TV", "icon": "📺", "subtypes": [{"id": "chico", "label": "Chico"}, {"id": "grande", "label": "Grande"}], "rules": [{"subtype": "chico", "type": "none", "val": 0, "margin": 20, "add": 0}, {"subtype": "grande", "type": "none", "val": 0, "margin": 25, "add": 0}]},
        {"id": "audio", "name": "Audio", "icon": "🎧", "subtypes": [{"id": "unico", "label": "Único"}], "rules": [{"subtype": "unico", "type": "none", "val": 0, "margin": 20, "add": 0}]},
        {"id": "computacion", "name": "Computación", "icon": "💻", "subtypes": [{"id": "unico", "label": "Único"}], "rules": [{"subtype": "unico", "type": "none", "val": 0, "margin": 20, "add": 0}]},
        {"id": "accesorios", "name": "Accesorios", "icon": "🎒", "subtypes": [{"id": "unico", "label": "Único"}], "rules": [{"subtype": "unico", "type": "none", "val": 0, "margin": 20, "add": 0}]},
        {"id": "hogar", "name": "Hogar", "icon": "🏠", "subtypes": [{"id": "unico", "label": "Único"}], "rules": [{"subtype": "unico", "type": "none", "val": 0, "margin": 25, "add": 0}]},
    ]

    return {
        "products": products,
        "banners": banners,
        "settings": {
            "whatsapp": "5491154125271",
            "dollarManual": None,
            "dollarAuto": None,
            "dollarUpdated": None,
            "categories": categories,
        },
    }


def main():
    if len(sys.argv) > 1:
        src = Path(sys.argv[1])
        if not src.exists():
            print(f"Error: {src} not found")
            sys.exit(1)
        with open(src, encoding="utf-8") as f:
            raw = json.load(f)
        if "products" in raw:
            data = raw
        elif isinstance(raw, list):
            data = {"products": raw, "banners": [], "settings": {}}
        else:
            data = raw
    else:
        print("No export file provided, using DEFAULT data from admin.html")
        data = build_default()

    data["products"] = [migrate_product(p) for p in data["products"]]
    now = datetime.now(timezone.utc).isoformat()
    data["lastSync"] = now
    data["lastPriceCheck"] = now

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Migrated {len(data['products'])} products to {OUTPUT}")


if __name__ == "__main__":
    main()
