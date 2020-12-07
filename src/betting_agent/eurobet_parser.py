import time
from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from sport_betting.utils.teams_name_parsing import TEAM_DUPLICATE_NAMES


def parse_teams(team: str):
    # team = team.lower()
    # punctuation = " -"
    # for sign in punctuation:
    #     team = team.replace(sign, "")
    team = TEAM_DUPLICATE_NAMES.get(team, team)
    return team


def parse_players(players: List[str]):
    players = [player.text.split("\n") for player in players]
    players = [tuple(parse_teams(team) for team in teams) for teams in players]
    return players


def parse_quotes(all_quotes: str):
    return [tuple(float(x12) for x12 in quotes.text.split('\n')) for quotes in all_quotes]


def _get_matches(driver, url):
    players = driver.find_elements_by_class_name("event-players")
    teams = parse_players(players)
    quotes = parse_quotes(driver.find_elements_by_class_name(
        "group-quote-new"))
    print(f"Last match: teams: {' vs '.join(teams[-1])}, quotes={quotes[-1]}.")
    if len(teams) != len(quotes):
        raise RuntimeError(f'Cannot parse!')
    return players, teams, quotes


def _parse_eurobet_url_2(driver, url, retries: int = 10):
    print(f'Parsing: {url}')
    driver.get(url)
    time.sleep(20.)
    matches = dict()
    try:
        players, teams, quotes = _get_matches(driver, url)
    except RuntimeError as err:
        if retries - 1 < 0:
            raise RuntimeError(
                f"Unable to get same length of quotes for {url}")
        return _parse_eurobet_url_2(driver, url, retries=retries-1)
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


def parse_eurobet():
    URLS = ["https://www.eurobet.it/it/scommesse/#!/manifestazione/champions-europa-league/",
            "https://www.eurobet.it/it/scommesse/#!/manifestazione/serie-a-serie-b/",
            "https://www.eurobet.it/it/scommesse/#!/calcio/ing-premier-league/",
            "https://www.eurobet.it/it/scommesse/#!/manifestazione/liga-e-ligue-1-in-diretta-streaming-33/",
            "https://www.eurobet.it/it/scommesse/#!/manifestazione/top-calcio-altri-paesi/"]
    matches = dict()
    try:
        driver = webdriver.Chrome()
        driver.implicitly_wait(10.)
        for url in URLS:
            matches.update(_parse_eurobet_url_2(driver, url))
    finally:
        driver.close()
    for k, v in matches.items():
        if sum([1. / x for x in v]) < 1.01:
            print(k, v)

    print(min([sum([1. / x for x in v]) for v in matches.values()]))
    return matches


if __name__ == "__main__":
    parse_eurobet()
