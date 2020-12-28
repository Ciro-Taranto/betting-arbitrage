from typing import Callable, NamedTuple

class ElementParsers(NamedTuple):
    teams: Callable 
    quotes: Callable

class ElementClasses(NamedTuple):
    teams: str 
    quotes: str

class Waits(NamedTuple):
    implicit: float = 10. 
    explicit: float = 5. 
