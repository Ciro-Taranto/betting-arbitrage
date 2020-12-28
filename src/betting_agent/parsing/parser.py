import os

import time
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from typing import List, Callable, Tuple, Dict
from ..interfaces import Waits
from .bwin_parser import BWIN_URLS
from .bwin_parser import get_matches as get_bwin_matches
from .eurobet_parser import EUROBET_URLS
from .eurobet_parser import get_matches as get_eurobet_matches
from .matchpoint_parser import MatchpointParser


class Parser:
    def __init__(
        self,
        urls: List[str],
        get_matches: Callable,  
        shelf_location: str,
        waits: Waits = Waits(), 
        debug: bool = False,
    ):
        self.urls = urls
        self.get_matches = get_matches
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
        

    def _parse_url(self, driver: WebDriver, url: str):
        print(f"Parsing: {url}")
        driver.get(url)
        matches = dict()
        last_item = None
        scroll_location = 0
        while True: 
            new_matches, new_last_item = self.get_matches(driver)
            matches.update(new_matches)
            if last_item == new_last_item: 
                break 
            last_item = new_last_item
             
            scroll_location += 400
            driver.execute_script(f"window.scrollTo(0, {scroll_location})")
            time.sleep(self.waits.explicit)
            
        print(f"All data parsed for {url}")
        return matches
        
    @classmethod
    def get_bwin_parser(cls, shelf_location: str, waits: Waits = Waits(), **kwargs):
        return cls(BWIN_URLS, get_bwin_matches, shelf_location=shelf_location, waits=waits, **kwargs)

    @classmethod
    def get_eurobet_parser(cls, shelf_location: str, waits: Waits = Waits(explicit=10.), **kwargs):
        return cls(EUROBET_URLS, get_eurobet_matches, shelf_location=shelf_location,
            waits=waits, **kwargs)

    @classmethod
    def get_matchpoint_parser(cls, shelf_location: str, waits: Waits = Waits(), **kwargs):
        return MatchpointParser(shelf_location=shelf_location, waits=waits)