from typing import Optional


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
        self.link = link
        self._scrape_metadata()
        self._init_chapters()

    def _scrape_metadata(self) -> None:
        """
        Scrapes the metadata from the novel homepage.
        :return: None.
        """
        raise NotImplementedError

    def _init_chapters(self) -> None:
        """
        Initializes the chapter list.
        :return: None.
        """
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
        self._scrape_chapters(translator, no_cache)
        self._build_novel(path)

    def _scrape_chapters(self, translator: Optional[str], no_cache: bool) -> \
            None:
        """
        Downloads the chapter data for the novel.
        :param translator: The translator to prefer, or None.
        :param no_cache: Whether to force rescraping of cached chapters.
        :return: None.
        """
        raise NotImplementedError

    def _build_novel(self, path: str) -> None:
        """
        Builds an ebook for the given novel.
        :param path: The directory in which to create the ebook.
        :return: None.
        """
        raise NotImplementedError
