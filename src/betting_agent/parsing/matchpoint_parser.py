from typing import List
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from selenium.webdriver.chrome.options import Options
from ..interfaces import Waits
import time
import shelve 


class MatchpointParser:
    urls = ["https://www.sisal.it/scommesse-matchpoint?filtro=0&schede=man:1:22,man:1:21,man:1:18,man:1:153,man:1:86,man:1:79,man:1:14,man:1:4", 
            ]
    
    def __init__(self, shelf_location: str, waits: Waits = Waits()):
        self.waits = waits
        self.shelf_location = shelf_location

    def parse(self):
        matches = dict()
        driver = webdriver.Chrome()
        driver.implicitly_wait(self.waits.implicit)
        try:
            for url in self.urls: 
                matches.update(self._parse_url(driver, url))
        finally: 
            driver.quit()
        return matches

    def _parse_url(self, driver: WebDriver, url: str):
        print(f'Parsing: {url}') 
        matches = dict()        
        driver.get(url)
        time.sleep(self.waits.explicit)
        with shelve.open(self.shelf_location) as shelf: 
            known_teams: set = shelf.get("known_teams", set())
        elements = driver.find_elements_by_css_selector("div[class*=TabellaEsitiRow]")
        print(len(elements))
        for element in elements:   
            teams, _, *quotes = element.text.split("\n")
            print(teams, quotes)
            try:
                teams = tuple(team.strip() for team in teams.split("-"))
                known_teams = known_teams.union(teams)
                quotes = [float(val) for val in quotes[:3]]
                matches[teams] = quotes
            except: 
                continue
        with shelve.open(self.shelf_location) as shelf: 
            shelf['kwnown_teams'] = known_teams
        print(f"Parsed {len(matches)} matches.")
        print(f"last parsed match: {matches[list(matches.keys())[-1]]}")
        return matches

