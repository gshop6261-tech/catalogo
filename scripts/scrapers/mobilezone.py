"""Scraper for mobilezone.com.py — Paraguayan electronics retailer (SPA).

The public site is a React/Vite SPA so HTML scraping is not viable.
Instead, this scraper hits the backend JSON API that the SPA itself consumes:
    GET https://products-api-dns.mobilezone.com.py/api/products/{internal_id}

The internal_id is the last numeric segment of the public URL:
    https://www.mobilezone.com.py/product/1122596 -> 1122596

Images live at:
    https://images.mobilezone.com.br/s3-images/image/<url_image>
"""

import html
import re
from urllib.parse import quote, urlparse

import requests
from bs4 import BeautifulSoup

from .base import BaseScraper

API_BASE = "https://products-api-dns.mobilezone.com.py/api/products"
IMAGE_BASE = "https://images.mobilezone.com.br/s3-images/image/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "es-PY,es;q=0.9,en;q=0.8",
    "Referer": "https://www.mobilezone.com.py/",
    "Origin": "https://www.mobilezone.com.py",
}

TIMEOUT = 20


def _get_product_id(url: str) -> str | None:
    """Extract internal_id from URL like https://www.mobilezone.com.py/product/1122596"""
    parts = urlparse(url).path.rstrip("/").split("/")
    for part in reversed(parts):
        if part.isdigit():
            return part
    return None


def _fetch_api(internal_id: str) -> dict:
    resp = requests.get(f"{API_BASE}/{internal_id}", headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def _build_image_url(rel_path: str) -> str:
    return IMAGE_BASE + quote(rel_path, safe="/")


def _clean_description(raw: str | None) -> str | None:
    """Decode HTML entities and strip tags; return None if empty after cleaning."""
    if not raw:
        return None
    decoded = html.unescape(raw)
    text = BeautifulSoup(decoded, "html.parser").get_text(separator=" ").strip()
    text = re.sub(r"\s+", " ", text)
    return text or None


def _build_specs(details: list[dict], brands: list[dict]) -> str | None:
    """Build multiline bullet list from productHasDetails + brand."""
    lines = []
    if brands:
        brand_name = brands[0].get("name_py") or brands[0].get("name_br")
        if brand_name:
            lines.append(f"• Marca: {brand_name.strip()}")
    for d in details or []:
        detail = d.get("detail") or {}
        label = (detail.get("name_py") or detail.get("name_br") or "").strip()
        value = (d.get("name_py") or d.get("name_br") or "").strip()
        if label and value:
            lines.append(f"• {label}: {value}")
    return "\n".join(lines) if lines else None


def _compose_description(desc_text: str | None, specs_text: str | None) -> str | None:
    """Description goes first; specs below under 'Características:'.
    If no description, specs become the description. If neither, return None."""
    if desc_text and specs_text:
        return f"{desc_text}\n\nCaracterísticas:\n{specs_text}"
    if desc_text:
        return desc_text
    if specs_text:
        return f"Características:\n{specs_text}"
    return None


class MobilezoneScraper(BaseScraper):
    """Scraper for mobilezone.com.py via its public JSON API.

    Prices are always in USD (Paraguay's tourism regime / decreto).
    """

    domains = ["mobilezone.com.py", "www.mobilezone.com.py"]

    def scrape_product(self, url: str) -> dict:
        internal_id = _get_product_id(url)
        if not internal_id:
            return {
                "name": None, "description": None, "specs": None,
                "images": [], "price": None, "currency": "USD",
            }

        data = _fetch_api(internal_id)

        name = (data.get("name_py") or "").strip() or None
        desc_text = _clean_description(data.get("description_py"))
        specs_text = _build_specs(
            data.get("productHasDetails") or [],
            data.get("productHasBrands") or [],
        )
        description = _compose_description(desc_text, specs_text)

        images = []
        for img in data.get("productHasImages") or []:
            rel = img.get("url_image")
            if rel:
                images.append(_build_image_url(rel))

        price = None
        raw_price = data.get("price")
        if raw_price is not None:
            try:
                price = float(raw_price) or None
            except (ValueError, TypeError):
                price = None

        return {
            "name": name,
            "description": description,
            "specs": specs_text,
            "images": images,
            "price": price,
            "currency": "USD",
        }

    def scrape_price(self, url: str) -> dict:
        internal_id = _get_product_id(url)
        if not internal_id:
            return {"price": None, "currency": "USD"}
        try:
            data = _fetch_api(internal_id)
        except requests.HTTPError:
            return {"price": None, "currency": "USD"}

        raw_price = data.get("price")
        if raw_price is None:
            return {"price": None, "currency": "USD"}
        try:
            return {"price": float(raw_price) or None, "currency": "USD"}
        except (ValueError, TypeError):
            return {"price": None, "currency": "USD"}
