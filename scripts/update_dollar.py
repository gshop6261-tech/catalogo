#!/usr/bin/env python3
"""Fetch dollar blue quote and update settings.dollarAuto in productos.json.
Runs every 30 minutes via GitHub Actions."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "productos.json"

PRIMARY_URL = "https://dolarapi.com/v1/dolares/blue"
FALLBACK_URL = "https://api.bluelytics.com.ar/v2/latest"


def fetch_dollar() -> float | None:
    try:
        r = requests.get(PRIMARY_URL, timeout=15)
        r.raise_for_status()
        venta = r.json().get("venta")
        if venta:
            return float(venta)
    except Exception as e:
        print(f"  Primary failed ({PRIMARY_URL}): {e}")

    try:
        r = requests.get(FALLBACK_URL, timeout=15)
        r.raise_for_status()
        blue = r.json().get("blue", {}).get("value_sell")
        if blue:
            return float(blue)
    except Exception as e:
        print(f"  Fallback failed ({FALLBACK_URL}): {e}")

    return None


def main() -> int:
    rate = fetch_dollar()
    if rate is None:
        print("Could not fetch dollar rate from any source.")
        return 1

    with open(DATA_FILE, encoding="utf-8") as f:
        data = json.load(f)

    settings = data.setdefault("settings", {})
    old_rate = settings.get("dollarAuto")

    settings["dollarAuto"] = rate
    settings["dollarUpdated"] = datetime.now(timezone.utc).isoformat()

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    if old_rate != rate:
        print(f"Dollar updated: {old_rate} -> {rate}")
    else:
        print(f"Dollar unchanged: {rate}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
