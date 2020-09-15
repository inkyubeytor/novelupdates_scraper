from typing import Optional
from datetime import date

import pypub


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
        self.contents = pypub.create_chapter_from_url(self.link)
