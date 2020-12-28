from selenium.webdriver.remote.webdriver import WebDriver
from ..interfaces import ElementParsers, ElementClasses
from ..utils.element_parsing import parse_quotes, parse_players

BWIN_URLS = [
        "https://sports.bwin.it/it/sports/calcio-4/scommesse/italia-20/serie-a-42",
        "https://sports.bwin.it/it/sports/calcio-4/scommesse/italia-20/serie-b-57",
        "https://sports.bwin.it/it/sports/calcio-4/scommesse/inghilterra-14/premier-league-46",
        "https://sports.bwin.it/it/sports/calcio-4/scommesse/spagna-28/laliga-16108",
        "https://sports.bwin.it/it/sports/calcio-4/scommesse/francia-16/ligue-1-4131",
        "https://sports.bwin.it/it/sports/calcio-4/scommesse/germania-17/bundesliga-43",
        "https://sports.bwin.it/it/sports/calcio-4/scommesse/europa-7/champions-league-0:3",
        "https://sports.bwin.it/it/sports/calcio-4/scommesse/europa-7/uefa-europa-league-0:5"
        ]

def get_matches(driver: WebDriver):
        elements = driver.find_elements_by_class_name("grid-event-wrapper")
        matches = dict()
        for element in elements: 
                try: 
                        team1, team2, *quotes = element.text.split("\n")
                        teams = (team1, team2)
                        quotes = [float(quote) for quote in quotes[-3:]]
                        print(teams, quotes)
                        matches[teams] = quotes
                except Exception:
                        print(f"Unable to parse: {element.text}") 
                        continue
        return matches, elements[-1] if elements else None

bwin_element_parsers = ElementParsers(parse_players, parse_quotes)
bwin_element_classes = ElementClasses("participants-pair-game", "grid-group-container")
