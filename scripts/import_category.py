#!/usr/bin/env python3
"""Import all products from an Atacado category URL as pending entries.

Usage:
    python scripts/import_category.py \
        --url "https://atacadoconnect.com/categoria/beleza" \
        --cat "Belleza" \
        --calc-sub "cera" \
        [--badge "a pedido"] \
        [--badge-color "#FF9500"] \
        [--dry-run]
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "productos.json"

sys.path.insert(0, str(ROOT / "scripts"))

from scrapers.atacado import AtacadoScraper


def load_data() -> dict:
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_data(data: dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def build_existing_urls(products: list[dict]) -> set[str]:
    """Retorna set de todas las URLs ya presentes en referenceLinks."""
    return {
        link["url"].rstrip("/")
        for p in products
        for link in p.get("referenceLinks", [])
        if link.get("url")
    }


def make_pending_product(
    url: str,
    price: float,
    pid: int,
    cat: str,
    calc_sub: str,
    badge: str,
    badge_color: str,
    today: str,
) -> dict:
    return {
        "id": pid,
        "cat": cat,
        "calcSub": calc_sub,
        "name": "",
        "sub": "",
        "desc": "",
        "img": "",
        "images": [],
        "badge": badge,
        "badgeColor": badge_color,
        "icon": "📦",
        "ars": None,
        "usd": None,
        "usdSell": None,
        "weight": None,
        "activo": True,
        "fechaAlta": today,
        "priceHistory": [],
        "referenceLinks": [
            {
                "url": url,
                "price": price,
                "currency": "USD",
                "isPrimary": True,
                "lastChecked": datetime.now(timezone.utc).isoformat(),
            }
        ],
        "status": "pending",
        "enrichError": None,
        "verifyPrice": True,
    }


def main():
    parser = argparse.ArgumentParser(description="Import products from Atacado category")
    parser.add_argument("--url", required=True, help="URL de categoría Atacado")
    parser.add_argument("--cat", required=True, help="Categoría del catálogo")
    parser.add_argument("--calc-sub", required=True, help="calcSub para precio")
    parser.add_argument("--badge", default="a pedido", help="Badge del producto")
    parser.add_argument("--badge-color", default="#FF9500", help="Color del badge")
    parser.add_argument("--dry-run", action="store_true", help="No escribir cambios")
    args = parser.parse_args()

    data = load_data()
    products = data["products"]

    # Validar categoría
    valid_cats = {c["name"] for c in data.get("settings", {}).get("categories", [])}
    if args.cat not in valid_cats:
        print(f"Error: '{args.cat}' no válida. Disponibles: {sorted(valid_cats)}")
        sys.exit(1)

    scraper = AtacadoScraper()

    # 1. Obtener todos los links de la categoría
    print(f"Scraping categoría: {args.url}")
    product_urls = scraper.scrape_category(args.url)
    print(f"URLs encontradas: {len(product_urls)}")

    # 2. Filtrar duplicados
    existing = build_existing_urls(products)
    new_urls = [u for u in product_urls if u not in existing]
    skipped_dup = len(product_urls) - len(new_urls)

    if skipped_dup > 0:
        print(f"Duplicados (ya existen): {skipped_dup}")

    # 3. Verificar precio de cada URL nueva antes de cargar
    today = datetime.now().strftime("%Y-%m-%d")
    current_id = max((p["id"] for p in products), default=0) + 1
    added = []
    skipped_no_price = 0

    print(f"\nVerificando precios de {len(new_urls)} productos nuevos...")
    for url in new_urls:
        try:
            result = scraper.scrape_price(url)
            price = result.get("price") if result else None
        except Exception as e:
            print(f"  [ERROR] Error al verificar precio de {url}: {e}")
            price = None

        if price is None:
            print(f"  [SKIP] Sin precio: {url}")
            skipped_no_price += 1
            continue

        print(f"  [OK] precio={price} USD")
        p = make_pending_product(
            url, price, current_id, args.cat, args.calc_sub,
            args.badge, args.badge_color, today
        )
        added.append(p)
        if not args.dry_run:
            products.append(p)
        current_id += 1

    print(f"\n{'='*60}")
    print(f"Resultado:")
    print(f"  Agregados:           {len(added)}")
    print(f"  Skipped (dup):       {skipped_dup}")
    print(f"  Skipped (sin precio): {skipped_no_price}")
    print(f"{'='*60}")

    if args.dry_run:
        print("\n[DRY RUN] No se escribio nada.")
        return

    if added:
        save_data(data)
        print(f"\n[OK] {len(added)} productos guardados. IDs asignados: {added[0]['id']} - {added[-1]['id']}")
    else:
        print("\nNo habia productos nuevos con precio para agregar.")


if __name__ == "__main__":
    main()
