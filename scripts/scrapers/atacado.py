"""Scraper for atacadoconnect.com — Brazilian wholesale perfume/electronics site.

Structure:
- JSON-LD Product with price in USD and description in HTML
- Images at cdn.atacadoconnect.com/produtos/<id>/
- Price also in spans with class 'page-module__P-0F3q__priceValue'
- Product ID extracted from URL path (last segment)
"""

import json
import re
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup

from .base import BaseScraper

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}

TIMEOUT = 20


def _fetch(url: str) -> tuple[BeautifulSoup, str]:
    resp = requests.get(url, headers=HEADERS, cookies={"currency": "Peso"}, timeout=TIMEOUT)
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or "utf-8"
    return BeautifulSoup(resp.text, "html.parser"), resp.text


def _get_product_id(url: str) -> str | None:
    """Extract product ID from URL like .../1354300"""
    parts = urlparse(url).path.rstrip("/").split("/")
    for part in reversed(parts):
        if part.isdigit():
            return part
    return None


def _get_jsonld(soup: BeautifulSoup) -> dict | None:
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
            if isinstance(data, dict) and data.get("@type") == "Product":
                return data
        except (json.JSONDecodeError, TypeError):
            continue
    return None


def _clean_html(html_str: str) -> str:
    """Strip HTML tags from description."""
    soup = BeautifulSoup(html_str, "html.parser")
    return soup.get_text(separator=" ").strip()


def _extract_spanish_desc(page_text: str) -> str | None:
    """Extract Spanish description from embedded JS data (descricao_longa_es field).

    The field is inside a double-escaped JSON string, so quotes appear as \\" and
    HTML tags as \\u003c / \\u003e.
    """
    match = re.search(
        r'descricao_longa_es\\*"\\*:\s*\\*"(.*?)\\*"(?:\s*[,}\\])',
        page_text,
        re.DOTALL,
    )
    if not match:
        return None
    raw = match.group(1)
    raw = raw.replace("\\u003c", "<").replace("\\u003e", ">")
    raw = raw.replace("\\n", " ").replace('\\"', '"').replace("\\\\", "\\")
    return _clean_html(raw) or None


class AtacadoScraper(BaseScraper):
    """Scraper for atacadoconnect.com"""

    domains = ["atacadoconnect.com", "www.atacadoconnect.com"]

    def scrape_product(self, url: str) -> dict:
        soup, page_text = _fetch(url)
        product_id = _get_product_id(url)
        jsonld = _get_jsonld(soup)

        name = None
        description = None
        specs = None
        price = None
        currency = "USD"
        images = []

        # Prefer Spanish description from embedded JS data
        description = _extract_spanish_desc(page_text)

        if jsonld:
            name = jsonld.get("name")
            if not description:
                raw_desc = jsonld.get("description", "")
                description = _clean_html(raw_desc) if raw_desc else None
            offers = jsonld.get("offers", {})
            if isinstance(offers, list):
                offers = offers[0] if offers else {}
            try:
                price = float(offers.get("price", 0)) or None
            except (ValueError, TypeError):
                price = None
            currency = offers.get("priceCurrency", "USD")
            img = jsonld.get("image")
            if img:
                images.append(img)

        if not name:
            h1 = soup.find("h1")
            if h1:
                name = h1.get_text().strip()

        if not description:
            og_desc = soup.find("meta", property="og:description")
            if og_desc:
                description = og_desc.get("content", "").strip()

        cdn_base = f"https://cdn.atacadoconnect.com/produtos/{product_id}/" if product_id else ""
        if cdn_base:
            seen = set(images)
            for img_tag in soup.find_all("img", src=True):
                src = img_tag["src"]
                if cdn_base in src and src not in seen:
                    if "/capa/" not in src:
                        images.append(src)
                        seen.add(src)

        if not images:
            og_img = soup.find("meta", property="og:image")
            if og_img and og_img.get("content"):
                images.append(og_img["content"])

        return {
            "name": name,
            "description": description,
            "specs": specs,
            "images": images,
            "price": price,
            "currency": currency,
        }

    def scrape_price(self, url: str) -> dict:
        soup, _ = _fetch(url)
        jsonld = _get_jsonld(soup)

        if jsonld:
            offers = jsonld.get("offers", {})
            if isinstance(offers, list):
                offers = offers[0] if offers else {}
            try:
                price = float(offers.get("price", 0)) or None
                currency = offers.get("priceCurrency", "USD")
                if price:
                    return {"price": price, "currency": currency}
            except (ValueError, TypeError):
                pass

        for span in soup.find_all("span", class_=re.compile("priceValue")):
            text = span.get_text().strip()
            parent_text = span.parent.get_text() if span.parent else ""
            if "U$" in parent_text or "USD" in parent_text:
                try:
                    val = text.replace(".", "").replace(",", ".")
                    return {"price": float(val), "currency": "USD"}
                except ValueError:
                    continue

    def scrape_category(self, url: str) -> list[str]:
        """Navega todas las páginas de la categoría y retorna URLs de productos únicos."""
        product_urls: list[str] = []
        seen: set[str] = set()
        base_url = url.rstrip("/")
        page = 1

        while page <= 50:
            page_url = base_url if page == 1 else f"{base_url}?page={page}"
            print(f"  Fetching category page {page}: {page_url}")
            soup, _ = _fetch(page_url)

            new_count = 0
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if "/produto/" in href or "/product/" in href:
                    abs_url = urljoin(page_url, href).split("?")[0].split("#")[0].rstrip("/")
                    if abs_url not in seen:
                        seen.add(abs_url)
                        product_urls.append(abs_url)
                        new_count += 1

            next_link = soup.find("a", class_="next") or soup.find("a", rel="next")
            if not next_link or new_count == 0:
                break
            page += 1

        print(f"  Found {len(product_urls)} products across {page} page(s)")
        return product_urls

        return {"price": None, "currency": "USD"}
