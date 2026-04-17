#!/usr/bin/env python3
"""Enrich pending products: scrape info from reference links, download images,
calculate average cost, and optionally commit+push."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "productos.json"

sys.path.insert(0, str(ROOT / "scripts"))

from scrapers.registry import get_scraper
from utils.images import download_images
from utils.pricing import average_cost, calculate_sell_price


def load_data() -> dict:
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_data(data: dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def enrich_product(product: dict, categories: list[dict]) -> None:
    links = product.get("referenceLinks", [])
    if not links:
        product["status"] = "error"
        product["enrichError"] = "No reference links provided"
        return

    primary = next((l for l in links if l.get("isPrimary")), links[0])
    now = datetime.now(timezone.utc).isoformat()

    print(f"  Scraping primary: {primary['url']}")
    scraper = get_scraper(primary["url"])

    try:
        info = scraper.scrape_product(primary["url"])
    except Exception as e:
        product["status"] = "error"
        product["enrichError"] = f"Scrape failed: {e}"
        return

    if info.get("description") and not product.get("desc"):
        product["desc"] = info["description"][:2000]

    if info.get("price") is not None:
        primary["price"] = info["price"]
        primary["currency"] = info.get("currency", "USD")
    primary["lastChecked"] = now

    for link in links:
        if link is primary:
            continue
        print(f"  Scraping secondary: {link['url']}")
        try:
            sec_scraper = get_scraper(link["url"])
            price_info = sec_scraper.scrape_price(link["url"])
            if price_info.get("price") is not None:
                link["price"] = price_info["price"]
                link["currency"] = price_info.get("currency", "USD")
            link["lastChecked"] = now
        except Exception as e:
            print(f"    Warning: failed to scrape price from {link['url']}: {e}")

    avg = average_cost(links)
    if avg is not None:
        product["usd"] = avg

    if product.get("usd") and product.get("cat"):
        sell = calculate_sell_price(
            product["usd"],
            product["cat"],
            product.get("calcSub", "unico"),
            product.get("weight", 0) or 0,
            categories,
        )
        if sell is not None:
            product["usdSell"] = round(sell, 2)

    if info.get("images"):
        print(f"  Downloading {len(info['images'])} images...")
        saved = download_images(info["images"], product["id"], ROOT)
        if saved:
            product["images"] = saved
            product["img"] = saved[0]

    product["status"] = "enriched"
    product["enrichError"] = None
    print(f"  Enriched: {product['name']} (USD {product.get('usd')})")


def main():
    data = load_data()
    products = data.get("products", [])
    categories = data.get("settings", {}).get("categories", [])

    pending = [p for p in products if p.get("status") == "pending"]
    if not pending:
        print("No pending products to enrich.")
        return

    print(f"Found {len(pending)} pending product(s)")
    for p in pending:
        print(f"\nProcessing: {p['name']} (id={p['id']})")
        enrich_product(p, categories)

    data["lastSync"] = datetime.now(timezone.utc).isoformat()
    save_data(data)

    enriched_count = sum(1 for p in pending if p.get("status") == "enriched")
    error_count = sum(1 for p in pending if p.get("status") == "error")
    print(f"\nDone: {enriched_count} enriched, {error_count} errors")

    # Git commit/push is handled by the GitHub Actions workflow step


if __name__ == "__main__":
    main()
