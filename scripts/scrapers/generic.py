"""Generic scraper that works with any e-commerce site using Open Graph,
JSON-LD, meta tags, and common HTML patterns."""

import json
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from .base import BaseScraper

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9,es;q=0.8",
}

TIMEOUT = 20


def _fetch(url: str) -> BeautifulSoup:
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    return BeautifulSoup(resp.content, "html.parser")


def _og(soup: BeautifulSoup, prop: str) -> str | None:
    tag = soup.find("meta", property=f"og:{prop}")
    if tag:
        return tag.get("content", "").strip() or None
    return None


def _jsonld_products(soup: BeautifulSoup) -> list[dict]:
    results = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get("@type") == "Product":
                    results.append(item)
        elif isinstance(data, dict):
            if data.get("@type") == "Product":
                results.append(data)
            elif "@graph" in data:
                for item in data["@graph"]:
                    if isinstance(item, dict) and item.get("@type") == "Product":
                        results.append(item)
    return results


def _extract_price_from_jsonld(product: dict) -> tuple[float | None, str]:
    offers = product.get("offers", {})
    if isinstance(offers, list):
        offers = offers[0] if offers else {}
    price = offers.get("price")
    currency = offers.get("priceCurrency", "USD")
    if price is not None:
        try:
            return float(price), currency
        except (ValueError, TypeError):
            pass
    return None, "USD"


def _extract_price_from_meta(soup: BeautifulSoup) -> tuple[float | None, str]:
    for selector in [
        {"itemprop": "price"},
        {"property": "product:price:amount"},
        {"name": "twitter:data1"},
    ]:
        tag = soup.find("meta", selector)
        if tag and tag.get("content"):
            try:
                val = re.sub(r"[^\d.]", "", tag["content"])
                return float(val), "USD"
            except (ValueError, TypeError):
                continue

    for el in soup.select('[itemprop="price"]'):
        content = el.get("content") or el.get_text()
        if content:
            try:
                val = re.sub(r"[^\d.]", "", content)
                return float(val), "USD"
            except (ValueError, TypeError):
                continue

    return None, "USD"


def _extract_rich_description(soup: BeautifulSoup) -> str | None:
    """Extract structured description from common product page patterns.
    Preserves paragraphs and bullet points using \\n separators."""
    selectors = [
        '[itemprop="description"]',
        '.product-description',
        '#product-description',
        '.description',
        '#description',
        '.product-details',
        '.product-info-description',
        '.tab-description',
        '[data-tab="description"]',
        '.product_description',
        'section.description',
        '.product-long-description',
    ]
    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            text = _html_block_to_text(el).strip()
            if len(text) >= 80:
                return text[:2000]
    return None


def _html_block_to_text(el) -> str:
    """Convert an HTML element to plain text preserving paragraph/list structure."""
    parts = []

    def _walk(node):
        if not hasattr(node, 'name'):
            # text node
            t = str(node)
            if t.strip():
                parts.append(t.strip())
            return
        tag = node.name
        if tag in ('script', 'style', 'noscript'):
            return
        if tag in ('p', 'h2', 'h3', 'h4', 'h5'):
            text = node.get_text(separator=' ', strip=True)
            if text:
                if parts and not parts[-1].endswith('\n'):
                    parts.append('\n')
                parts.append(text)
                parts.append('\n')
        elif tag in ('ul', 'ol'):
            if parts and not parts[-1].endswith('\n'):
                parts.append('\n')
            for li in node.find_all('li', recursive=False):
                text = li.get_text(separator=' ', strip=True)
                if text:
                    parts.append(f'• {text}')
                    parts.append('\n')
        elif tag == 'br':
            parts.append('\n')
        elif tag == 'li':
            pass  # handled by ul/ol above
        else:
            for child in node.children:
                _walk(child)

    for child in el.children:
        _walk(child)

    # Collapse excessive blank lines
    text = ''.join(parts)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def _extract_images(soup: BeautifulSoup, base_url: str) -> list[str]:
    images = []
    seen = set()

    og_image = _og(soup, "image")
    if og_image:
        images.append(og_image)
        seen.add(og_image)

    jsonld_products = _jsonld_products(soup)
    for prod in jsonld_products:
        img = prod.get("image")
        if isinstance(img, str) and img not in seen:
            images.append(img)
            seen.add(img)
        elif isinstance(img, list):
            for i in img:
                url = i if isinstance(i, str) else i.get("url", "")
                if url and url not in seen:
                    images.append(url)
                    seen.add(url)

    for img_tag in soup.select("img[src]"):
        src = img_tag.get("data-src") or img_tag.get("src", "")
        if not src or src.startswith("data:"):
            continue
        full = urljoin(base_url, src)
        width = img_tag.get("width", "0")
        height = img_tag.get("height", "0")
        try:
            if int(width) >= 200 or int(height) >= 200:
                if full not in seen:
                    images.append(full)
                    seen.add(full)
        except (ValueError, TypeError):
            if full not in seen:
                images.append(full)
                seen.add(full)

    return images[:10]


class GenericScraper(BaseScraper):
    """Fallback scraper using Open Graph, JSON-LD, and meta tags."""

    domains = []

    def scrape_product(self, url: str) -> dict:
        soup = _fetch(url)

        name = _og(soup, "title")
        description = _og(soup, "description")
        specs = None

        jsonld = _jsonld_products(soup)
        if jsonld:
            ld = jsonld[0]
            name = name or ld.get("name")
            description = description or ld.get("description")

        # Try to get a richer description with paragraphs/bullets from the page HTML
        rich_desc = _extract_rich_description(soup)
        if rich_desc:
            description = rich_desc

        if not name:
            title_tag = soup.find("title")
            name = title_tag.get_text().strip() if title_tag else None

        price, currency = None, "USD"
        if jsonld:
            price, currency = _extract_price_from_jsonld(jsonld[0])
        if price is None:
            price, currency = _extract_price_from_meta(soup)

        images = _extract_images(soup, url)

        return {
            "name": name,
            "description": description,
            "specs": specs,
            "images": images,
            "price": price,
            "currency": currency,
        }

    def scrape_price(self, url: str) -> dict:
        soup = _fetch(url)

        jsonld = _jsonld_products(soup)
        if jsonld:
            price, currency = _extract_price_from_jsonld(jsonld[0])
            if price is not None:
                return {"price": price, "currency": currency}

        price, currency = _extract_price_from_meta(soup)
        return {"price": price, "currency": currency}
