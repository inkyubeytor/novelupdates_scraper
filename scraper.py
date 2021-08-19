from bs4 import BeautifulSoup
import cloudscraper


class Scraper:
    def __init__(self) -> None:
        self.scraper = cloudscraper.create_scraper()

    def scrape(self, link) -> BeautifulSoup:
        d = self.scraper.get(link).text.encode("utf-8")
        return BeautifulSoup(d, "lxml")
