#!/usr/bin/env python3
"""Check prices on reference links for all enriched products.
Runs on a cron schedule (every 4 hours via GitHub Actions).
Updates costs and sell prices if changes are detected."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "productos.json"

sys.path.insert(0, str(ROOT / "scripts"))

from scrapers.registry import get_scraper
from utils.pricing import average_cost, calculate_sell_price


def load_data() -> dict:
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_data(data: dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def check_product_prices(product: dict, categories: list[dict]) -> bool:
    """Check all reference links for price changes. Returns True if any changed."""
    links = product.get("referenceLinks", [])
    if not links:
        return False

    now = datetime.now(timezone.utc).isoformat()
    changed = False

    for link in links:
        url = link.get("url")
        if not url:
            continue

        old_price = link.get("price")
        try:
            scraper = get_scraper(url)
            result = scraper.scrape_price(url)
            new_price = result.get("price")
            link["lastChecked"] = now

            if new_price is not None and new_price != old_price:
                print(f"  Price changed on {url}: {old_price} -> {new_price}")
                link["price"] = new_price
                link["currency"] = result.get("currency", "USD")
                changed = True
        except Exception as e:
            print(f"  Warning: failed to check {url}: {e}")

    if not changed:
        return False

    old_usd = product.get("usd")
    new_avg = average_cost(links)
    if new_avg is not None and new_avg != old_usd:
        product["usd"] = new_avg
        print(f"  Cost updated: {old_usd} -> {new_avg}")

        if product.get("cat"):
            sell = calculate_sell_price(
                new_avg,
                product["cat"],
                product.get("calcSub", "unico"),
                product.get("weight", 0) or 0,
                categories,
            )
            if sell is not None:
                old_sell = product.get("usdSell")
                product["usdSell"] = round(sell, 2)
                print(f"  Sell price updated: {old_sell} -> {product['usdSell']}")

        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if not product.get("priceHistory"):
            product["priceHistory"] = []
        product["priceHistory"].append({
            "usd": new_avg,
            "date": today,
        })

    return True


def main():
    data = load_data()
    products = data.get("products", [])
    categories = data.get("settings", {}).get("categories", [])

    candidates = [
        p for p in products
        if p.get("status") == "enriched" and p.get("referenceLinks")
    ]

    if not candidates:
        print("No enriched products with reference links to check.")
        return

    print(f"Checking prices for {len(candidates)} product(s)...")
    changes = 0
    for p in candidates:
        print(f"\n{p['name']} (id={p['id']})")
        if check_product_prices(p, categories):
            changes += 1

    data["lastPriceCheck"] = datetime.now(timezone.utc).isoformat()
    save_data(data)

    print(f"\nDone: {changes} product(s) with price changes out of {len(candidates)}")

    # Git commit/push is handled by the GitHub Actions workflow step


if __name__ == "__main__":
    main()
