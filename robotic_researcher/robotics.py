import atexit
import datetime
from typing import List, Callable, Optional, Iterable

import click
from RPA.Browser.Selenium import Selenium
from selenium.webdriver.common.by import By

br = Selenium(auto_close=True)
atexit.register(br.close_all_browsers)


class WayFailed(Exception):
    pass


class CannotFind(Exception):
    pass


class Robot:
    def __init__(self, name):
        self.name = name

    def open_webpage(self, webpage: str):
        if not br.get_browser_ids():
            br.open_available_browser()
        br.go_to(webpage)
        pass

    def assert_page_correctness(self, scientist: str):
        if br.does_page_contain("Wikipedia does not have an article with this exact name."):
            raise WayFailed
        element = br.driver.find_element(By.XPATH, "/html/body/div[2]/div/div[3]/main/header/h1/span")  # page name
        if scientist not in element.text:
            if click.prompt(f'Are you looking for this web page "{element.text}"?', type=bool, default='n'):
                return
            raise WayFailed

    def simple_way(self, scientist_name: str):
        scientist_name = "_".join(scientist_name.split(' '))
        url = f"https://en.wikipedia.org/wiki/{scientist_name}"
        self.open_webpage(url)
        self.assert_page_correctness(scientist_name)

    def difficult_way(self, scientist_name: str):
        scientist_name = "+".join(scientist_name.split(' '))
        url = f'https://www.google.com/search' \
              f'?q=site:en.wikipedia.org+{scientist_name}' \
              f'&btnI=I%27m+Feeling+Lucky'
        self.open_webpage(url)
        allow_redirect_button = br.driver.find_element(By.XPATH, "/html/body/div[2]/a[1]")
        allow_redirect_button.click()
        self.assert_page_correctness(scientist_name)

    def very_difficult_way(self, scientist_name: str):
        def run_search():
            search_field = br.driver.find_element(By.XPATH, '//*[@id="searchInput"]')
            search_field.send_keys(*scientist_name)
            search_field.submit()

        def choose_link() -> bool:
            wiki_advice = br.driver.find_elements(By.XPATH, '//*[@id="mw-search-DYM-suggestion"]')
            search_results = br.driver.find_elements(By.XPATH,
                                                     '//*[@id="mw-content-text"]/div[4]/div[2]/ul/li/table/tbody/tr/td[2]/div[1]/a')
            links = wiki_advice + search_results

            def validator(x: str):
                if not x.isdigit():
                    raise click.BadParameter(f"x is not a digit")
                if not 0 <= int(x) <= len(links):
                    raise click.BadParameter(f"should be between [1, {len(links)}]")
                return int(x)

            choice = "\n".join([f"{num + 1}) {link.text}" for num, link in enumerate(links)] + ["0) :exit"])
            num = click.prompt(f"Which of the following do you choose?\n{choice}", type=int, value_proc=validator)
            if num == 0:
                raise CannotFind(scientist_name)

            rechoose = len(wiki_advice) and num == 1
            links[num - 1].click()
            return rechoose

        run_search()
        br.driver.implicitly_wait(3)  # TODO
        choose_again = choose_link()
        if choose_again:
            br.driver.implicitly_wait(3)  # TODO
            choose_link()

    def scientist_info(self, scientist: str):
        def find_page():
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

        def print_data():
            def get_bdate() -> datetime.date:
                born_span = br.driver.find_element(By.XPATH, '//table/tbody/tr/th[text()="Born"]/../td/span')
                born = born_span.find_element(By.CLASS_NAME, 'bday')
                br.driver.execute_script("arguments[0].style = '';", born_span)  # remove display:none
                return datetime.datetime.strptime(born.text, "%Y-%M-%d").date()

            def get_ddate() -> Optional[datetime.date]:
                died_spans = br.driver.find_elements(By.XPATH, '//table/tbody/tr/th[text()="Died"]/../td/span')
                if not died_spans:
                    return None
                assert len(died_spans) == 1
                died = died_spans[0]
                br.driver.execute_script("arguments[0].style = '';", died)  # remove display:none
                return datetime.datetime.strptime(died.text, "(%Y-%M-%d)").date()

            def get_age(date1: datetime.date, date2: Optional[datetime.date]) -> int:
                if date2 is None:
                    date2 = datetime.datetime.now().date()
                age = date2.year - date1.year - 1
                # whether birthday already was:
                months = date1.month < date2.month
                days = date2.month == date1.month and date1.day <= date2.day
                if months or days:
                    age += 1
                if age > 125:
                    raise RuntimeError("Impossible")
                return age

            def get_first_paragraph() -> Iterable[str]:
                path = "//div[@class='mw-parser-output']/h2[1]/preceding-sibling::p"
                first_ps = br.driver.find_elements(By.XPATH, path)
                yield "Article:"
                for p in first_ps:
                    yield p.text
                    yield "\n\n"

            bdate = get_bdate()
            ddate = get_ddate()
            age = get_age(bdate, ddate)
            click.prompt(f"His age is {age} years", default="ok")

            text = get_first_paragraph()
            click.echo_via_pager(text)

        find_page()
        print_data()

    def say_hello(self):
        print("Hello, my name is " + self.name)

    def say_wait(self):
        print("Please wait...")

    def say_goodbye(self):
        print("Goodbye, my name is " + self.name)
