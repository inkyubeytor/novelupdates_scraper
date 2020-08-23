from typing import Optional


class Page:
    """
    Represents a single translation of a chapter.
    """
    def __init__(self, link: str) -> None:
        """
        Initializes a new page.
        :param link: A link to the page.
        """
        self.link = link
        self.contents = None

    def get(self, no_cache: bool) -> str:
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
        raise NotImplementedError
