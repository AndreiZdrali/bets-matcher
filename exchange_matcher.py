from scrappers.scrapper import ScrapperBase
from events import Event
from sites import Sports, BetTypes
from matcher import Matcher

class ExchangeMatcher(Matcher):
    """ casa prima, exchange-ul al doilea """
    def __init__(self, bookie: ScrapperBase, exchange: ScrapperBase):
        self.bookie = bookie
        self.exchange = exchange
        self.tennis_pairs: list[ExchangeEventPair] = []
        self.football_pairs: list[ExchangeEventPair] = []

    #cred ca trb lucrat la formula la comisioane
    @staticmethod
    def calculate_roi(odds_back: float, odds_lay: float, commission_back: float = 0.03, commission_lay: float = 0.065):
        stake_back = 100 #ca sa lucram in procente
        #stake_lay = odds_back * stake_back / (odds_lay - commission_lay)
        #profit = stake_lay * (1 - commission_lay) - stake_back
        #return (stake_back, stake_lay, profit)

        stake_lay = stake_back * ((odds_back - 1) * (1 - commission_back) + 1) / (odds_lay - commission_lay)

        profit = stake_lay * (1 - commission_lay) - stake_back

        return (stake_back, stake_lay, profit)

    def match_tennis_events(self, roi_treshold = -3):
        pass

    def match_football_events(self, roi_threshold=-3):
        for e in self.bookie.football_events:
            e.normalize_teams(2)
        for e in self.exchange.football_events:
            e.normalize_teams(2)

        for event_bookie in self.bookie.football_events:
            for event_exchange in self.exchange.football_events:
                if Matcher._check_if_tennis_events_match(event_bookie, event_exchange): #merge si la fotbal
                    #event2 e meciul de pe exchange
                    (stake_back, stake_lay, roi) = ExchangeMatcher.calculate_roi(event_bookie.odds1, event_exchange.odds1)
                    if roi > roi_threshold:
                        #TODO: sa fac bettype-uri specifice de contra
                        self.add_football_event_pair(ExchangeEventPair(Sports.FOOTBALL, event_bookie, event_exchange, stake_back, stake_lay, BetTypes.BET_1, roi))

                    (stake_back, stake_lay, roi) = ExchangeMatcher.calculate_roi(event_bookie.oddsx, event_exchange.oddsx)
                    if roi > roi_threshold:
                        self.add_football_event_pair(ExchangeEventPair(Sports.FOOTBALL, event_bookie, event_exchange, stake_back, stake_lay, BetTypes.BET_X, roi))

                    (stake_back, stake_lay, roi) = ExchangeMatcher.calculate_roi(event_bookie.odds2, event_exchange.odds2)
                    if roi > roi_threshold:
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
        return f"{self.roi} | {self.bettype}" +\
            f"\n{self.event_bookie.site}\n{self.event_bookie}\nSTAKE: {self.stake_back}" +\
            "\n--------------" +\
            f"\n{self.event_exchange.site}\n{self.event_exchange}\nSTAKE: {self.stake_lay} (CONTRA) <--" +\
            f"\nhttps://www.betfair.ro/exchange/plus/{self.event_exchange.url}" if self.event_exchange.url else ""