from typing import Dict, Optional

from page import Page

import pypub


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
        assert(len(translations) > 0)
        self.translations: Dict[str, Page] = {
            translator: Page(link) for translator, link in translations.items()
        }

    def scrape(self, translator: Optional[str], no_cache: bool) -> \
            pypub.Chapter:
        """
        Returns the chapter data for the novel.
        :param translator: The translator to prefer, or None.
        :param no_cache: Whether to force rescraping of cached chapters.
        :return: The scraped chapter given the parameters.
        """
        try:
            page = self.translations[translator]
        except KeyError:
            # Pick first page in dictionary
            page = next(iter(self.translations.values()))
        return page.get(no_cache)
