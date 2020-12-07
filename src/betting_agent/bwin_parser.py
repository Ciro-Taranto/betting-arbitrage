import time
import re
from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from sport_betting.utils.teams_name_parsing import TEAM_DUPLICATE_NAMES


URLS = ["https://sports.bwin.it/it/sports/calcio-4/scommesse/italia-20/serie-a-42",
        "https://sports.bwin.it/it/sports/calcio-4/scommesse/italia-20/serie-b-57",
        "https://sports.bwin.it/it/sports/calcio-4/scommesse/inghilterra-14/premier-league-46",
        "https://sports.bwin.it/it/sports/calcio-4/scommesse/spagna-28/laliga-16108",
        "https://sports.bwin.it/it/sports/calcio-4/scommesse/francia-16/ligue-1-4131",
        "https://sports.bwin.it/it/sports/calcio-4/scommesse/germania-17/bundesliga-43",
        "https://sports.bwin.it/it/sports/calcio-4/scommesse/europa-7/champions-league-0:3",
        "https://sports.bwin.it/it/sports/calcio-4/scommesse/europa-7/uefa-europa-league-0:5"
        ]


def parse_teams(team: str):
    # team = team.lower()
    # punctuation = " -"
    # for sign in punctuation:
    #     team = team.replace(sign, "")
    team = TEAM_DUPLICATE_NAMES.get(team, team)
    return team


def parse_players(players: List[str]):
    pattern = re.compile("\S+\n\S+")
    players = [pattern.match(player.text) for player in players]
    players = [player[0] for player in players if player]
    for i, player in enumerate(players):
        print(i, player.replace("\n", "vs"))
    players = [tuple(teams.split("\n")) for teams in players]
    return players


def parse_quotes(quotes: str):
    pattern = re.compile("^\d+.\d{2}\n\d+.\d{2}\n\d+.\d{2}")
    quotes = [pattern.match(quote.text) for quote in quotes]
    quotes = [quote[0] for quote in quotes if quote]
    return [tuple(float(x12) for x12 in quotes.split('\n')) for quotes in quotes]


def _get_matches(driver, url):
    players_class_name = "participants-pair-game"
    results_class_name = "grid-group-container"
    players = driver.find_elements_by_class_name(players_class_name)
    quotes = driver.find_elements_by_class_name(results_class_name)
    teams = parse_players(players)
    quotes = parse_quotes(quotes)
    print(f"Last match: teams: {' vs '.join(teams[-1])}, quotes={quotes[-1]}.")
    if len(teams) != len(quotes):
        for i, team in enumerate(teams):
            print(i, team)
        for i, quote in enumerate(quotes):
            print(i, quote)
        print(len(teams))
        print(len(quotes))
        raise RuntimeError(f'Cannot parse!')
    return players, teams, quotes


def _parse_bwin_url(driver, url, retries: int = 10):
    print(f'Parsing: {url}')
    driver.get(url)
    time.sleep(20.)
    matches = dict()
    try:
        players, teams, quotes = _get_matches(driver, url)
    except RuntimeError as err:
        raise RuntimeError from err
        # if retries - 1 < 0:
        #         f"Unable to get same length of quotes for {url}")
        # return _parse_bwin_url(driver, url, retries = retries-1)
    matches.update(dict(zip(teams, quotes)))
    while True:
        print(f"Scrolling down and parsing again")
        last_item = players[-1]
        last_item.location_once_scrolled_into_view
        time.sleep(2.)
        try:
            players, teams, quotes = _get_matches(driver, url)
        except RuntimeError as exc:
            if retries - 1 < 0:
                raise RuntimeError(
                    f"Unable to get same length of quotes for {url}")
            return _parse_eurobet_url_2(driver, url, retries=retries-1)
        if last_item.text == players[-1].text:
            print(f"All data parsed for {url}")
            break
        matches.update(dict(zip(teams, quotes)))

    return matches


def parse_bwin():
    matches = dict()

    try:
        driver = webdriver.Chrome()
        driver.implicitly_wait(10.)
        for url in URLS:
            matches.update(_parse_bwin_url(driver, url))

    finally:
        driver.close()

    return matches


if __name__ == "__main__":
    parse_bwin()
