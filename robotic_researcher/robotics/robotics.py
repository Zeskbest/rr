"""
Main processing module.
"""
import datetime
from typing import List, Callable, Optional, Iterable

import click
from RPA.Browser.Selenium import Selenium
from selenium.webdriver.common.by import By

from .exceptions import CannotFind, WayFailed
from .selenium_utils import SeleniumWrapMixin
from .speaker import CanSpeakMixin

# seconds, how much to wait for internal Wikipedia search
SLEEP_TIMEOUT = 3


class Robot(CanSpeakMixin, SeleniumWrapMixin):
    """
    The main processing class.
    Attributes:
        br: Selenium browser wrap
        name: its name
    """

    def __init__(self):
        self.br = Selenium()
        self.name = "Scientist Seeker 2k23"

    def shutdown(self) -> None:
        """Must be called for graceful shutdown"""
        self.br.driver.close()

    def simple_way(self, scientist: str) -> None:
        """
        Tries to guess webpage (should work with SCIENTISTS variable).
        Args:
            scientist: scientist name
        Raises:
            WayFailed if unsuccessful
        """
        scientist_name_in_url = "_".join(scientist.split(" "))
        url = f"https://en.wikipedia.org/wiki/{scientist_name_in_url}"
        self.open_webpage(url)
        self.assert_page_correctness(scientist)

    def difficult_way(self, scientist: str) -> None:
        """
        Googles for a webpage (works with most typos).
        Args:
            scientist: scientist name
        Raises:
            WayFailed if unsuccessful
        """
        scientist = "+".join(scientist.split(" "))
        url = f"https://www.google.com/search" f"?q=site:en.wikipedia.org+{scientist}" f"&btnI=I%27m+Feeling+Lucky"
        self.open_webpage(url)
        allow_redirect_button = self.br.driver.find_element(By.XPATH, "/html/body/div[2]/a[1]")
        with self.wait_driver_to_change_url():
            allow_redirect_button.click()
        self.assert_page_correctness(scientist)

    def very_difficult_way(self, scientist: str) -> None:
        """
        An interactive cmd representation for a Wikipedia search page.
        Args:
            scientist: scientist name
        Raises:
            WayFailed if unsuccessful
        """

        def run_search() -> None:
            """Run wikipedia Search. Sometimes redirects to the target page."""
            search_field = self.br.driver.find_element(By.XPATH, '//*[@id="searchInput"]')
            search_field.send_keys(*scientist)
            with self.wait_driver_to_change_url():
                search_field.submit()

        def choose_link() -> bool:
            """
            Ask user to choose an option from the wiki search page.
            Returns:
                whether this function is needed to be retried
            Raises:
                CannotFind if there is no way
            """
            wiki_advice = self.br.driver.find_elements(By.XPATH, '//*[@id="mw-search-DYM-suggestion"]')
            search_results = self.br.driver.find_elements(
                By.XPATH, '//*[@id="mw-content-text"]/div/div[2]/ul/li/table/tbody/tr/td[2]/div[1]/a'
            )
            links = wiki_advice + search_results
            if not links:
                raise CannotFind(scientist)

            def validator(x: str):
                if not x.isdigit():
                    raise click.BadParameter(f"x is not a digit")
                if not 0 <= int(x) <= len(links):
                    raise click.BadParameter(f"should be between [1, {len(links)}]")
                return int(x)

            choice = "\n".join([f"{num + 1}) {link.text}" for num, link in enumerate(links)] + ["0) :exit:\n"])
            num = click.prompt(f"Which of the following do you choose?\n{choice}", type=int, value_proc=validator)
            if num == 0:
                raise CannotFind(scientist)

            rechoose = len(wiki_advice) and num == 1
            with self.wait_driver_to_change_url():
                links[num - 1].click()
            return rechoose

        run_search()
        self.br.driver.implicitly_wait(SLEEP_TIMEOUT)
        if "index.php" not in self.br.driver.current_url:
            # seems, we are no longer on the search page
            return
        choose_again = choose_link()
        if choose_again:
            self.br.driver.implicitly_wait(SLEEP_TIMEOUT)
            choose_link()

    def find_page(self, scientist) -> None:
        """
        Find the needed page
        Args:
            scientist: scientist name
        Raises:
            CannotFind if there is literally no way
        """
        # ways: List[Callable[[str], None]] = [self.simple_way, self.difficult_way, self.very_difficult_way]
        ways: List[Callable[[str], None]] = [self.simple_way, self.very_difficult_way]  # google shows capcha
        for way in ways:
            try:
                way(scientist)
                break
            except WayFailed:
                continue
        else:
            raise CannotFind(scientist)

    def print_data(self) -> None:
        """
        Print info from the page.
        """

        def get_bdate() -> datetime.date:
            """
            Get the birthdate from the web page.
            Returns:
                birthdate
            """
            born_span = self.br.driver.find_element(By.XPATH, '//table/tbody/tr/th[text()="Born"]/../td/span')
            born = born_span.find_element(By.CLASS_NAME, "bday")
            self.br.driver.execute_script("arguments[0].style = '';", born_span)  # remove display:none
            return datetime.datetime.strptime(born.text, "%Y-%m-%d").date()

        def get_ddate() -> Optional[datetime.date]:
            """
            Get the death date from the web page if exists.
            Returns:
                death date
            """
            died_spans = self.br.driver.find_elements(By.XPATH, '//table/tbody/tr/th[text()="Died"]/../td/span')
            if not died_spans:
                return None
            assert len(died_spans) == 1
            died = died_spans[0]
            self.br.driver.execute_script("arguments[0].style = '';", died)  # remove display:none
            return datetime.datetime.strptime(died.text, "(%Y-%m-%d)").date()

        def calculate_age(date1: datetime.date, date2: Optional[datetime.date]) -> int:
            """
            Calculate age.
            Args:
                date1: birthdate
                date2: death date

            Returns:
                amount of years
            """
            if date2 is None:
                date2 = datetime.datetime.now().date()
            age = date2.year - date1.year
            # whether birthday wasn't celebrated:
            months = date2.month < date1.month
            days = date2.month == date1.month and date2.day < date1.day
            if months or days:
                age -= 1
            if age > 125:
                raise RuntimeError("Impossible")
            return age

        def get_first_paragraph() -> Iterable[str]:
            """
            Get the first page paragraph: before the first <h2> header.
            Yields:
                first part of the page

            """
            path = "//div[@class='mw-parser-output']/h2[1]/preceding-sibling::p"
            first_ps = self.br.driver.find_elements(By.XPATH, path)
            yield "Article:"
            for p in first_ps:
                yield p.text.strip()
                yield "\n\n"

        bdate = get_bdate()
        ddate = get_ddate()
        age = calculate_age(bdate, ddate)
        print(f"\nThe scientist was born on {bdate.strftime('%d %B %Y')}")
        if ddate is not None:
            print(f"The scientist died on     {ddate.strftime('%d %B %Y')}")
        print(f"The age of the scientist is {age}")

        text = get_first_paragraph()
        click.prompt("\nTo read article press Enter", default="ok", show_default=False)
        click.echo_via_pager(text)

    def run(self, scientist: str) -> None:
        """
        Robot Entrypoint.

        Args:
            scientist: expected scientist arg
        Raises:
            CannotFind if the task is impossible
        """

        self.find_page(scientist)
        self.print_data()
