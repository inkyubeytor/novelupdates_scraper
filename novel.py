from typing import List, Optional

import pypub
import cloudscraper
from bs4 import BeautifulSoup, NavigableString

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

        self._get_source()
        self._scrape_metadata()
        self._init_chapters()

    def _get_source(self) -> None:
        """
        Requests novelupdates page and stores within object.
        :return: None.
        """
        response = cloudscraper.create_scraper().get(self.link)
        self.soup = BeautifulSoup(response.text, "lxml")

    def _scrape_metadata(self) -> None:
        """
        Scrapes the metadata from the novel homepage.
        :return: None.
        """
        # Title
        self.title: str = \
            self.soup.find("div", {"class": "seriestitlenu"}).text

        # Description
        self.description: str = "".join(
            p.string for p in
            self.soup.find("div", {"id": "editdescription"}).children
        )

        # Genre
        self.genres: List[str] = self._list_sidebar("seriesgenre")

        # Tags
        self.tags: List[str] = self._list_sidebar("showtags")

        # Languages
        self.languages: List[str] = self._list_sidebar("showlang")

        # Authors
        self.authors: List[str] = self._list_sidebar("showauthors")

        # Artists
        self.artists: List[str] = self._list_sidebar("showartists")

        # Year
        self.year: int = int(self.soup.find("div", {"id": "edityear"}).text)

        # Original Publishers
        self.orig_publishers: List[str] = self._list_sidebar("showopublisher")

        # English Publishers
        self.eng_publishers: List[str] = self._list_sidebar("showepublisher")

        # Completely Translated
        self.is_translated: str = \
            self.soup.find("div", {"id": "showtranslated"}).text.strip()

        # Status in COO
        self.status: List[str] = list(
            self.soup.find("div", {"id": "editstatus"}).stripped_strings)

        # Licensed
        self.licensed: str = \
            self.soup.find("div", {"id": "showlicensed"}).text.strip()

        # Associated Names
        self.names: List[str] = list(
            self.soup.find("div", {"id": "editassociated"}).stripped_strings)

        # Type
        self.novel_type: str = \
            self.soup.find("div", {"id": "showtype"}).text.strip()

        # Related Series
        ele = self.soup.find("div", {"class": "two-thirds"}).div.div
        children = [str(e) if type(e) == NavigableString else e.text
                    for e in ele.children]
        children = [e.strip('\n') for e in children]
        children = list(filter(len, children))
        children = children[children.index("Related Series") + 1:]
        children = children[:children.index("Recommendations")]
        self.related: List[str] = [children[2 * i] + children[2 * i + 1]
                                   for i in range(len(children) // 2)]

    def _list_sidebar(self, tag_id: str) -> List[str]:
        return [ele.string for ele in
                self.soup.find("div", {"id": tag_id}).children
                if ele not in {None, "\n", " "} and ele.string is not None]

    def _init_chapters(self) -> None:
        """
        Initializes the chapter list.
        :return: None.
        """
        self.chapters: List[Chapter] = []
        raise NotImplementedError

    def collect(self, path: str, translator: Optional[str] = None,
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
