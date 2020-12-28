import re
from typing import List
from selenium.webdriver.remote.webelement import WebElement

TEAM_DUPLICATE_NAMES = dict()

def parse_players(players: str, separator: str = "\n"):
    # pattern = re.compile("\S+\n\S+")
    return players.split("\n")


def parse_quotes(quotes: List[WebElement]):
    pattern = re.compile("\d+.\d{2}")
    quote_values = list()
    for quote in quotes:
        all_matches = pattern.findall(quote.get_attribute("textContent"))
        if len(all_matches) >= 3: 
            quote_values.append([float(val) for val in all_matches[:3]]) 
    return quote_values
