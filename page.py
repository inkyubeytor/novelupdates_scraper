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

    def scrape(self) -> None:
        """
        Downloads the page data and scrapes text.
        :return: None.
        """
        raise NotImplementedError
