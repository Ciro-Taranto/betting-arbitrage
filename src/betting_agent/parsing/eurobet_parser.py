import re
from selenium.webdriver.remote.webdriver import WebDriver
from ..interfaces import ElementClasses, ElementParsers
from ..utils.element_parsing import parse_players, parse_quotes

EUROBET_URLS = [
        "https://www.eurobet.it/it/scommesse/#!/manifestazione/serie-a-serie-b/",
        "https://www.eurobet.it/it/scommesse/#!/calcio/ing-premier-league/",
        "https://www.eurobet.it/it/scommesse/#!/manifestazione/liga-e-ligue-1-in-diretta-streaming-33/",
        "https://www.eurobet.it/it/scommesse/#!/manifestazione/top-calcio-altri-paesi/"
        "https://www.eurobet.it/it/scommesse/#!/manifestazione/champions-europa-league/",
        ]

def parse_players(players):
        teams = players.split("-")
        return tuple(team.strip() for team in teams)

def get_matches(driver: WebDriver):
        elements = driver.find_elements_by_css_selector("div[class*=event-row]")
        matches = dict()
        pattern = re.compile("\d+/\d+\n\d{2}:\d{2}")
        for element in elements: 
                try:    
                        element_text = element.text
                        if pattern.match(element_text):
                                _, _, teams, *quotes = element_text.split("\n")
                        else: 
                                _, teams, *quotes = element.text.split("\n")
                        teams = tuple(team.strip() for team in teams.split("-"))
                        quotes = [float(quote) for quote in quotes[:3]]
                        print(teams, quotes)
                        matches[teams] = quotes
                except Exception:
                        print(f"Unable to parse: {element.text}") 
                        continue
        return matches, elements[-1] if len(elements) > 0 else None


eurobet_element_parsers =  ElementParsers(parse_players, parse_quotes)
eurobet_element_classes = ElementClasses("event-players", "group-quote-new")
