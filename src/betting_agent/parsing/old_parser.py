import os

import time
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from typing import List, Callable, NamedTuple
import shelve
from functools import update_wrapper
from ..interfaces import ElementParsers, ElementClasses, Waits
from .bwin_parser import BWIN_URLS, bwin_element_parsers, bwin_element_classes
from .eurobet_parser import EUROBET_URLS, eurobet_element_classes, eurobet_element_parsers
from .matchpoint_parser import MatchpointParser

class ostinate_retry: 
    RETRIES = 10 
    WAIT = 0.1 
    def __init__(self, funct: Callable): 
        self.funct = funct
        self.retries = self.RETRIES 
        self.wait = self.WAIT
        update_wrapper(self.funct, self.__call__)

    def __call__(self, *args, **kwargs):
        try:
            ret = self.funct(*args, **kwargs)
            self.wait = self.WAIT 
            self.retries = self.RETRIES
            return ret
        except RuntimeError as exc:
            if self.retries < 0: 
                raise RuntimeError from exc
            self.retries -= 1 
            self.wait *= 2. 
            time.sleep(self.wait)
            return self.__call__(*args, **kwargs)


class Parser:
    def __init__(
        self,
        urls: List[str],
        element_parsers: ElementParsers, 
        element_classes: ElementClasses, 
        shelf_location: str,
        waits: Waits = Waits(), 
        debug: bool = False,
    ):
        self.urls = urls
        self.element_parsers = element_parsers
        self.element_classes = element_classes
        self.shelf_location = shelf_location
        self.waits = waits
        self.debug = debug 
        shelf_dir = os.path.split(self.shelf_location)[0]
        os.makedirs(shelf_dir, exist_ok=True)

    def parse(self):
        matches = dict()

        try:
            driver = webdriver.Chrome()
            driver.implicitly_wait(self.waits.implicit)
            for url in self.urls:
                try: 
                    matches.update(self._parse_url(driver, url))
                except Exception as exc:
                    print(exc) 
                    continue
        finally:
            driver.close()
        return matches
        

    def _parse_url(self, driver: WebDriver, url: str, retries: int = 10):
        print(f"Parsing: {url}")
        driver.get(url)
        time.sleep(self.waits.explicit)
        matches = dict()
        last_item = None
        while True: 
            parsing_results = self._get_matches(driver, self.element_classes, self._parse_players, self._parse_quotes)
            if parsing_results is None:
                break
            players, teams, quotes = parsing_results 
            matches.update(dict(zip(teams, quotes)))
            if last_item == players[-1]: 
                break 
            last_item == players[-1]
            time.sleep(self.waits.explicit)
            
        print(f"All data parsed for {url}")
        return matches
        
    @staticmethod
    @ostinate_retry
    def _get_matches(driver: WebDriver, element_classes,
            parse_players, parse_quotes):
        players = driver.find_elements_by_class_name(element_classes.teams)
        for player in players: 
            print(player.text)
        quotes = driver.find_elements_by_class_name(element_classes.quotes)
        if len(players) == len(quotes) == 0: 
            return [], [], []
        teams = parse_players(players)
        quotes = parse_quotes(quotes)
        if len(teams) != len(quotes):
            raise RuntimeError(f"Cannot parse!")
        print(f"Last match: teams: {' vs '.join(teams[-1])}, quotes={quotes[-1]}.")
        return players, teams, quotes

    def _parse_players(self, players: List[WebElement]):
        teams = list() 
        with shelve.open(self.shelf_location) as shelf:
            known_teams = shelf.get("known-teams", set()) 
        for player in players: 
            if len(player.text) > 0:
                teams_pair = tuple(self.element_parsers.teams(player.text))
                known_teams = known_teams.union(teams_pair)
            else: 
                teams_text = player.get_attribute("textContent").strip()
                words = teams_text.split(" ")
                for i in range(1, len(words) - 1): 
                    first_team = " ".join(words[:i])
                    second_team = " ".join(words[i:])
                    if first_team in known_teams or second_team in known_teams: 
                        teams_pair = (first_team, second_team)
                        break 
                teams_pair = tuple(words)
            teams.append(teams_pair)
        with shelve.open(self.shelf_location) as shelf: 
            shelf["known-teams"] = known_teams
        return teams

    def _parse_quotes(self, quotes: List[WebElement]):
        return self.element_parsers.quotes(quotes)

    @classmethod
    def get_bwin_parser(cls, shelf_location: str, waits: Waits = Waits(), **kwargs):
        return cls(BWIN_URLS, bwin_element_parsers, bwin_element_classes, shelf_location=shelf_location, waits=waits, **kwargs)

    @classmethod
    def get_eurobet_parser(cls, shelf_location: str, waits: Waits = Waits(), **kwargs):
        return cls(EUROBET_URLS, eurobet_element_parsers, eurobet_element_classes, shelf_location=shelf_location,
            waits=waits, **kwargs)

    @classmethod
    def get_matchpoint_parser(cls, shelf_location: str, waits: Waits = Waits(), **kwargs):
        return MatchpointParser(shelf_location=shelf_location, waits=waits)