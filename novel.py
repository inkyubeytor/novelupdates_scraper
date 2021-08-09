from typing import List, Tuple, Any, Dict
from datetime import datetime, date
from multiprocessing.pool import ThreadPool
from collections import defaultdict
from functools import partial
import builtins

import pypub
import cloudscraper
from bs4 import BeautifulSoup, NavigableString, Tag

from page import Page

THREAD_COUNT = 4


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

        self.soup = self._get_source(self.link)
        self._scrape_metadata()
        self._init_chapters()

    @staticmethod
    def _get_source(link) -> BeautifulSoup:
        """
        Requests novelupdates page and stores within object.
        :return: None.
        """
        response = cloudscraper.create_scraper().get(link)
        return BeautifulSoup(response.text, "lxml")

    def _scrape_metadata(self) -> None:
        """
        Scrapes the metadata from the novel homepage.
        :return: None.
        """
        self.metadata: Dict[str, Any] = {
            "title": self.soup.find("div", {"class": "seriestitlenu"}).text,
            "description": "".join(
                p.string for p in
                self.soup.find("div", {"id": "editdescription"}).children
            ),
            "genres": self._list_sidebar("seriesgenre"),
            "tags": self._list_sidebar("showtags"),
            "languages": self._list_sidebar("showlang"),
            "authors": self._list_sidebar("showauthors"),
            "artists": self._list_sidebar("showartists"),
            "year": self.soup.find("div", {"id": "edityear"}).text,
            "original_publishers": self._list_sidebar("showopublisher"),
            "english_publishers": self._list_sidebar("showepublisher"),
            "is_translated": self.soup.find("div", {
                "id": "showtranslated"}).text.strip(), "status": list(
                self.soup.find("div", {"id": "editstatus"}).stripped_strings),
            "licensed": self.soup.find("div",
                                       {"id": "showlicensed"}).text.strip(),
            "names": list(
                self.soup.find("div",
                               {"id": "editassociated"}).stripped_strings),
            "novel_type": self.soup.find("div",
                                         {"id": "showtype"}).text.strip(),
            "related": self._get_related()
        }

    def _list_sidebar(self, tag_id: str) -> List[str]:
        return [ele.string for ele in
                self.soup.find("div", {"id": tag_id}).children
                if ele not in {None, "\n", " "} and ele.string is not None]

    def _get_related(self) -> List[str]:
        ele = self.soup.find("div", {"class": "two-thirds"}).div.div
        children = [str(e) if type(e) == NavigableString else e.text
                    for e in ele.children]
        children = [e.strip('\n') for e in children]
        children = list(filter(len, children))
        children = children[children.index("Related Series") + 1:]
        children = children[:children.index("Recommendations")]
        return [children[2 * i] + children[2 * i + 1]
                for i in range(len(children) // 2)]

    def _init_chapters(self) -> None:
        """
        Initializes the chapter list.
        :return: None.
        """
        try:
            max_page = max(int(a.text) for a in self.soup.find(
                "div", {"class": "digg_pagination"}).contents
                if a.text.isdigit())
        except AttributeError:
            max_page = 1

        def thread_fn(i: int) -> BeautifulSoup:
            soup = self._get_source(f"{self.link}?pg={i}")
            return soup.find("table", {"id": "myTable"}).tbody

        with ThreadPool(THREAD_COUNT) as p:
            tables = p.map(thread_fn, range(1, max_page + 1))

        scraped_table: List[Tuple[date, str, str, str]] = []
        for table in tables:
            for row in table.find_all("tr"):
                data = [d for d in row.children if type(d) is Tag]
                d = datetime.strptime(data[0].text.strip(), "%m/%d/%y").date()
                tr = self._parse_chapter_name(data[1].a.string)
                ch = data[2].a.string
                link = f"http:{data[2].a['href']}"
                scraped_table.append((d, tr, ch, link))

        self.chapter_list: List[Page] = \
            [Page(d, tr, ch, link) for (d, tr, ch, link) in
             reversed(scraped_table)]

    @staticmethod
    def _parse_chapter_name(name: str) -> str:
        """
        Parses a chapter name into a dictionary key/ebook chapter name.
        :param name: The name to parse.
        :return: The cleaned chapter name.
        """
        return name

    def collect(self, path: str, no_cache: bool = False) -> str:
        """
        Scrapes a novel to a given output directory.
        :param path: The output directory.
        :param no_cache: Whether to force rescraping of cached chapters.
        :return: The name of the EPUB file.
        """
        epub = pypub.Epub(
            self.metadata["title"],
            creator=", ".join(self.metadata["authors"] +
                              self.metadata["artists"]),
            language=", ".join(self.metadata["languages"]),
            rights=self.metadata["licensed"],
            publisher=", ".join(self.metadata["original_publishers"] +
                                self.metadata["english_publishers"]))
        translator_dict = defaultdict(lambda: [])
        for i, p in enumerate(self.chapter_list):
            translator_dict[p.translator].append((i, p))
        chapter_data = []
        chapters = set()
        for t in sorted(list(translator_dict.values()), key=len, reverse=True):
            for i, p in t:
                if p.name not in chapters:
                    chapter_data.append((i, p))
                    chapters.add(p.name)
        chapter_data.sort(key=lambda x: x[0])

        with ThreadPool(THREAD_COUNT) as p:
            pages = p.map(lambda x: x[1].get(no_cache=no_cache), chapter_data)

        for c in pages:
            epub.add_chapter(c)

        # TODO: Submit PR to pypub fork and replace this atrocious workaround
        # Replace open function temporarily to affect library behavior
        old_open = open

        def new_open(*args, **kwargs):
            utf8_open = partial(old_open, encoding="utf-8")
            try:
                return utf8_open(*args, **kwargs)
            except ValueError:
                return old_open(*args, **kwargs)

        builtins.open = new_open

        epub.create_epub(path)

        # Restore old open function
        builtins.open = old_open

        return f"{epub.title}.epub"
