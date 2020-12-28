from betting_agent.parsing.parser import Parser

SHELF_LOCATION = "/home/andreeas/Shelves/betting"

matchpoint_parser = Parser.get_matchpoint_parser(shelf_location=SHELF_LOCATION)
print(matchpoint_parser.parse())

eurobet_parser = Parser.get_eurobet_parser(shelf_location=SHELF_LOCATION, debug=True)
print(eurobet_parser.parse())

bwin_parser = Parser.get_bwin_parser(shelf_location=SHELF_LOCATION, debug=True)
print(bwin_parser.parse())
