from typing import List, Optional

import pypub
import cloudscraper
from bs4 import BeautifulSoup

from chapter import Chapter


class Novel:
    """
    Represents a novel.
    """

    def __init__(self, link: str) -> None:
        """
        Initializes a new novel.
        :param link: Link to the novelupdates source page for the novel.
        :return None.
        """
        self.link: str = link
        response = cloudscraper.create_scraper().get(self.link)
        # TODO: Error handling on failed request
        soup = BeautifulSoup(response.text, "lxml")
        self._scrape_metadata(soup)
        self._init_chapters(soup)

    def _scrape_metadata(self, soup: BeautifulSoup) -> None:
        """
        Scrapes the metadata from the novel homepage.
        :return: None.
        """
        # Title
        self.title: str = soup.find("div", {"class": "seriestitlenu"}).string

        # Description
        self.description: str = "".join(
            p.string for p in
            soup.find("div", {"id": "editdescription"}).children
        )

        # Genre
        self.genres: List[str] = self._list_sidebar("seriesgenre", soup)

        # Tags
        self.tags: List[str] = self._list_sidebar("showtags", soup)

        # Languages
        self.languages: List[str] = self._list_sidebar("showlang", soup)

        # Authors
        self.authors: List[str] = self._list_sidebar("showauthors", soup)

        # Artists
        self.artists: List[str] = self._list_sidebar("showartists", soup)

        # Year
        self.year: int = int(soup.find("div", {"id": "edityear"}).string)

        # Original Publisher
        self.orig_publishers : List[str] = \
            self._list_sidebar("showopublisher", soup)

        # TODO: Type, Status in COO, Licensed, Completely Translated,
        #  English Publisher, Associated Names, Related Series

        print(self.orig_publishers)
        raise NotImplementedError

    @staticmethod
    def _list_sidebar(tag_id: str, soup: BeautifulSoup) -> List[str]:
        return [ele.string for ele in soup.find("div", {"id": tag_id}).children
                if ele not in {None, "\n", " "} and ele.string is not None]

    def _init_chapters(self, soup: BeautifulSoup) -> None:
        """
        Initializes the chapter list.
        :return: None.
        """
        self.chapters: List[Chapter] = []
        raise NotImplementedError

    def scrape(self, path: str, translator: Optional[str] = None,
               no_cache: bool = False) -> None:
        """
        Scrapes a novel to a given output directory.
        :param path: The output directory.
        :param translator: The translator to prefer, or None.
        :param no_cache: Whether to force rescraping of cached chapters.
        :return: None.
        """
        # TODO: pass in metadata here
        epub = pypub.Epub(self.title)
        chapter_data = [c.scrape(translator, no_cache) for c in self.chapters]
        for c in chapter_data:
            epub.add_chapter(c)
        epub.create_epub(path)
