from typing import Dict, Optional

from page import Page


class Chapter:
    """
    Represents a chapter of a novel.
    """
    def __init__(self, translations: Dict[str, str]) -> None:
        """
        Initializes a new Chapter.
        :param translations: A dict containing translator name keys and
        translation link values.
        :return: None.
        """
        self.translations = {translator: Page(link)
                             for translator, link in translations.items()}

    def scrape(self, translator: Optional[str], no_cache: bool):
        """
        Downloads the chapter data for the novel.
        :param translator: The translator to prefer, or None.
        :param no_cache: Whether to force rescraping of cached chapters.
        :return: None.
        """
        raise NotImplementedError
