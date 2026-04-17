"""Maps URL domains to the appropriate scraper class."""

from urllib.parse import urlparse

from .base import BaseScraper
from .atacado import AtacadoScraper
from .generic import GenericScraper
from .mobilezone import MobilezoneScraper

_REGISTRY: list[type[BaseScraper]] = [
    AtacadoScraper,
    MobilezoneScraper,
]

_fallback = GenericScraper()


def get_scraper(url: str) -> BaseScraper:
    domain = urlparse(url).netloc.lower().removeprefix("www.")
    for cls in _REGISTRY:
        if domain in cls.domains:
            return cls()
    return _fallback
