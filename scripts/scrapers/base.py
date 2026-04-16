from abc import ABC, abstractmethod


class BaseScraper(ABC):
    """Every site-specific scraper inherits from this."""

    domains: list[str] = []

    @abstractmethod
    def scrape_product(self, url: str) -> dict:
        """Full product scrape from the primary reference link.

        Returns dict with keys:
            name (str|None), description (str|None), specs (str|None),
            images (list[str]), price (float|None), currency (str)
        """

    @abstractmethod
    def scrape_price(self, url: str) -> dict:
        """Lightweight price-only scrape for secondary links.

        Returns dict with keys:
            price (float|None), currency (str)
        """
