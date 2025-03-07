from scrappers.scrapper import ScrapperBase
from events import Event
from sites import Sports, BetTypes
from matcher import Matcher
import settings

class ExchangeMatcher(Matcher):
    """ casa prima, exchange-ul al doilea """
    def __init__(self, bookie: ScrapperBase, exchange: ScrapperBase):
        self.bookie = bookie
        self.exchange = exchange
        self.tennis_pairs: list[ExchangeEventPair] = []
        self.football_pairs: list[ExchangeEventPair] = []
        self.all_pairs: list[ExchangeEventPair] = []

    #cred ca trb lucrat la formula la comisioane
    @staticmethod
    def calculate_roi(odds_back: float, odds_lay: float, commission_back: float = 0, commission_lay: float = 0):
        stake_back = settings.SETTINGS["stake_back"] #100 ca sa lucram in procente
        #stake_lay = odds_back * stake_back / (odds_lay - commission_lay)
        #profit = stake_lay * (1 - commission_lay) - stake_back
        #return (stake_back, stake_lay, profit)

        stake_lay = stake_back * ((odds_back - 1) * (1 - commission_back) + 1) / (odds_lay - commission_lay)

        profit = stake_lay * (1 - commission_lay) - stake_back

        return (stake_back, stake_lay, profit)

    def match_tennis_events(self):
        for e in self.bookie.tennis_events:
            e.normalize_teams(2)
        for e in self.exchange.tennis_events:
            e.normalize_teams(2)

        min_roi = settings.SETTINGS["min_roi"]
        max_roi = settings.SETTINGS["max_roi"]
        commission_back = settings.SETTINGS["commission_back"]
        commission_lay = settings.SETTINGS["commission_lay"]

        for event_bookie in self.bookie.tennis_events:
            for event_exchange in self.exchange.tennis_events:
                if Matcher._check_if_events_match(event_bookie, event_exchange):
                    (stake_back, stake_lay, roi) = ExchangeMatcher.calculate_roi(event_bookie.odds1, event_exchange.odds1, commission_back, commission_lay)
                    if roi > min_roi and roi < max_roi:
                        self.add_tennis_event_pair(ExchangeEventPair(Sports.TENNIS, event_bookie, event_exchange, stake_back, stake_lay, BetTypes.BET_1, roi))

                    (stake_back, stake_lay, roi) = ExchangeMatcher.calculate_roi(event_bookie.odds2, event_exchange.odds2, commission_back, commission_lay)
                    if roi > min_roi and roi < max_roi:
                        self.add_tennis_event_pair(ExchangeEventPair(Sports.TENNIS, event_bookie, event_exchange, stake_back, stake_lay, BetTypes.BET_2, roi))

    def match_football_events(self):
        for e in self.bookie.football_events:
            e.normalize_teams(2)
        for e in self.exchange.football_events:
            e.normalize_teams(2)

        min_roi = settings.SETTINGS["min_roi"]
        max_roi = settings.SETTINGS["max_roi"]
        commission_back = settings.SETTINGS["commission_back"]
        commission_lay = settings.SETTINGS["commission_lay"]

        for event_bookie in self.bookie.football_events:
            for event_exchange in self.exchange.football_events:
                if Matcher._check_if_events_match(event_bookie, event_exchange):
                    (stake_back, stake_lay, roi) = ExchangeMatcher.calculate_roi(event_bookie.odds1, event_exchange.odds1, commission_back, commission_lay)
                    if roi > min_roi and roi < max_roi:
                        #TODO: sa fac bettype-uri specifice de contra
                        self.add_football_event_pair(ExchangeEventPair(Sports.FOOTBALL, event_bookie, event_exchange, stake_back, stake_lay, BetTypes.BET_1, roi))

                    (stake_back, stake_lay, roi) = ExchangeMatcher.calculate_roi(event_bookie.oddsx, event_exchange.oddsx, commission_back, commission_lay)
                    if roi > min_roi and roi < max_roi:
                        self.add_football_event_pair(ExchangeEventPair(Sports.FOOTBALL, event_bookie, event_exchange, stake_back, stake_lay, BetTypes.BET_X, roi))

                    (stake_back, stake_lay, roi) = ExchangeMatcher.calculate_roi(event_bookie.odds2, event_exchange.odds2, commission_back, commission_lay)
                    if roi > min_roi and roi < max_roi:
                        self.add_football_event_pair(ExchangeEventPair(Sports.FOOTBALL, event_bookie, event_exchange, stake_back, stake_lay, BetTypes.BET_2, roi))

class ExchangeEventPair:
    def __init__(self, sport, event_bookie: Event, event_exchange: Event, stake_back: float, stake_lay: float, bettype, roi: float):
        self.sport = sport
        self.event_bookie = event_bookie
        self.event_exchange = event_exchange
        self.stake_back = stake_back
        self.stake_lay = stake_lay
        self.bettype = bettype
        self.roi = roi

    def __str__(self):
        return f"{self.roi} | {self.sport} | {self.bettype}" +\
            f"\n{self.event_bookie.site}\n{self.event_bookie}\nSTAKE: {self.stake_back}" +\
            "\n--------------" +\
            f"\n{self.event_exchange.site}\n{self.event_exchange}\nSTAKE: {self.stake_lay} (CONTRA)" +\
            f"\nhttps://www.betfair.ro/exchange/plus/{self.event_exchange.url}" if self.event_exchange.url else ""
    
    def short_str(self):
        res = ""
        res += f"> {'{:.2f}'.format(self.roi)} < | {self.event_bookie.site} - {self.event_exchange.site} | STAKE: {self.stake_back}"
        res += f"\n1: {self.event_bookie.team1}: {self.event_bookie.odds1} - {self.event_exchange.team1}: {self.event_exchange.odds1}"
        res += f" <-- STAKE: {'{:.2f}'.format(self.stake_lay)}" if self.bettype == BetTypes.BET_1 else ""

        res += f"\nX: Egal: {self.event_bookie.oddsx} - Egal: {self.event_exchange.oddsx}" if self.sport == Sports.FOOTBALL else ""
        res += f" <-- STAKE: {'{:.2f}'.format(self.stake_lay)}" if self.bettype == BetTypes.BET_X else ""

        res += f"\n2: {self.event_bookie.team2}: {self.event_bookie.odds2} - {self.event_exchange.team2}: {self.event_exchange.odds2}"
        res += f" <-- STAKE: {'{:.2f}'.format(self.stake_lay)}" if self.bettype == BetTypes.BET_2 else ""
        return res