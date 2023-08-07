from sites import BetTypes

#aproape inutil
def swap(first, second):
    first, second = second, first

def check_event_odds_bounds(event, lower, upper):
    if event.bettype == BetTypes.BET_1 and (event.event_bookie.odds1 < lower or event.event_bookie.odds1 > upper):
        return False
    if event.bettype == BetTypes.BET_X and (event.event_bookie.oddsx < lower or event.event_bookie.oddsx > upper):
        return False
    if event.bettype == BetTypes.BET_2 and (event.event_bookie.odds2 < lower or event.event_bookie.odds2 > upper):
        return False
    return True

    return not (event.bettype == BetTypes.BET_1 and (event.event_bookie.odds1 < lower or event.event_bookie.odds1 > upper) or\
                event.bettype == BetTypes.BET_X and (event.event_bookie.oddsx < lower or event.event_bookie.oddsx > upper) or\
                event.bettype == BetTypes.BET_2 and (event.event_bookie.odds2 < lower or event.event_bookie.odds2 > upper))