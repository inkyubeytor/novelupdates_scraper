from typing import Optional
from datetime import date
import re

import pypub
import cloudscraper
from bs4 import BeautifulSoup


class Page:
    """
    Represents a single translation of a chapter.
    """
    def __init__(self, pub: date, translator: str, name: str, link: str) \
            -> None:
        """
        Initializes a new page.
        :param pub: The date the page was released.
        :param translator: The name of the page translator.
        :param name: The name of the chapter.
        :param link: A link to the page.
        """
        self.date: date = pub
        self.translator: str = translator
        self.name: str = name
        self.link: str = link
        self.contents: Optional[pypub.Chapter] = None

    def get(self, no_cache: bool = False) -> pypub.Chapter:
        """
        Returns page data, scraping it if it is not available.
        :param no_cache: Whether to force rescraping of cached chapters.
        :return: If the page is already scraped, returns the scraped data, else
        scrapes the data and returns it.
        """
        if self.contents is None or no_cache:
            self._scrape()
        return self.contents

    def _scrape(self) -> None:
        """
        Downloads the page data and scrapes text.
        :return: None.
        """
        soup = BeautifulSoup(
            cloudscraper.create_scraper().get(self.link).text.encode("utf-8"),
            "lxml")

        for i in soup.find_all("img"):
            i.decompose()
        for s in soup.find_all("script"):
            s.decompose()

        data = str(soup.decode("utf-8", "ignore"))
        self.contents = pypub.create_chapter_from_string(data, title=self.name)
