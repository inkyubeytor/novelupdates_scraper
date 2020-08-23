from typing import Dict

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
