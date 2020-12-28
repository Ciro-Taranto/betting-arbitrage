from betting_agent.parsing.parser import Parser
from betting_agent.analyzing.tools import find_best_quotes, compute_sure_probability
import shelve
from argparse import ArgumentParser 


parser = ArgumentParser()
parser.add_argument("--update", required=False, action="store_true")
args = parser.parse_args()

SHELF_LOCATION = "/home/andreeas/Shelves/betting"
all_quotes = dict()

eurobet_parser = Parser.get_eurobet_parser(shelf_location=SHELF_LOCATION, debug=True)
bwin_parser = Parser.get_bwin_parser(shelf_location=SHELF_LOCATION, debug=True)
matchpoint_parser = Parser.get_matchpoint_parser(shelf_location=SHELF_LOCATION)

with shelve.open(SHELF_LOCATION) as shelf:
    if "matchpoint" not in shelf or args.update:
        shelf["matchpoint"] = matchpoint_parser.parse()
    all_quotes["matchpoint"] = shelf["matchpoint"]
    if "eurobet" not in shelf or args.update:
        shelf["eurobet"] = eurobet_parser.parse()
    all_quotes["eurobet"] = shelf["eurobet"]
    if "bwin" not in shelf or args.update: 
        shelf["bwin"] = bwin_parser.parse()
    all_quotes["bwin"] = shelf["bwin"] 


best_quotes = find_best_quotes(all_quotes)
with shelve.open(SHELF_LOCATION) as shelf: 
    shelf["best_quotes"] = best_quotes

sorted_quotes = compute_sure_probability(best_quotes)
for key, value in sorted_quotes.items(): 
    print(key, value)


#_bettingfrontendscheda_desktop-scheda-react-root > div > div:nth-child(1) > div > div.Collapsible__CollapsibleWrapper-sc-1p1kix4-0.ixSVzc > div.TabellaEsitiScrollingAreaWrapper-sc-11bzuc7-0.iXdguK > div > div.TabellaEsitiWrapper-sc-10r57w5-0.bVCIEV > div:nth-child(3)