from typing import List, Dict, Tuple

worse_quotes = lambda: [(.99, "None")] * 3


def _compare(quotes: Tuple[float, float, float],
        best_quotes: List[Tuple[float, str]],
        broker_name: str):
    for i, (quote, best_quote) in enumerate(zip(quotes, best_quotes)): 
        if quote >= best_quote[0]: 
            best_quotes[i] = (quote, broker_name)
    return best_quotes


def find_best_quotes(collected_quotes: Dict[str, Dict[Tuple, Tuple[float, float, float]]]): 
    all_matches = set()
    for dico in collected_quotes.values(): 
        all_matches = all_matches.union(set(dico))
    all_quotes = dict()
    for match in all_matches:
        best_quotes = worse_quotes()
        for broker_name, quotes in collected_quotes.items():
            if match in quotes:
                best_quotes = _compare(quotes[match], best_quotes, broker_name)
        all_quotes[match] = best_quotes
    return all_quotes


def compute_sure_probability(best_quotes: dict):
    for match, quotes in best_quotes.items():
        sure_event_probability = sum(map(lambda x: 1. / x[0], quotes))
        best_quotes[match] = (sure_event_probability, quotes)
    return dict(sorted(best_quotes.items(), key=lambda item: item[1]))

