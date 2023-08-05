from scrappers.scrapper import ScrapperBase
from events import Event
from sites import Sports, BetTypes

class Matcher:
    def __init__(self, site1: ScrapperBase, site2: ScrapperBase):
        self.site1 = site1
        self.site2 = site2
        self.tennis_pairs: list[EventPair] = []
        self.football_pairs: list[EventPair] = []

    #presupune ca echipele sunt in aceeasi ordine
    @staticmethod
    def _check_if_tennis_events_match(event1: Event, event2: Event):
        #sa nu dea match la solo si echipe
        if event1.team1.count("/") != event2.team1.count("/"):
            return False

        #daca echipele sunt in aceeasi ordine
        m = 0
        for name in event1.team1_norm:
            if name in event2.team1_norm:
                m += 1
                break
        for name in event1.team2_norm:
            if name in event2.team2_norm:
                m += 1
                break
        if m == 2:
            return True

        #daca echipele sunt invers
        m = 0
        for name in event1.team1_norm:
            if name in event2.team2_norm:
                m += 1
                break
        for name in event1.team2_norm:
            if name in event2.team1_norm:
                m += 1
                break
        if m == 2:
            event2.swap_teams()
            return True

        return False

    #formule aparent complet gresite
    @staticmethod
    def calculate_roi(odds1: float, odds2: float):
        stake = 100 #ca sa lucram in procente
        arbitrage_team1 = 1 / odds1
        arbitrage_team2 = 1 / odds2
        arbitrage = arbitrage_team1 + arbitrage_team2

        profit = stake / arbitrage - stake #pt ca lucram in procente

        stake_team1 = stake * arbitrage_team1 / arbitrage
        stake_team2 = stake * arbitrage_team2 / arbitrage

        return (stake_team1, stake_team2, profit)

    def add_tennis_event_pair(self, pair):
        self.tennis_pairs.append(pair)

    def add_football_event_pair(self, pair):
        self.football_pairs.append(pair)

    def _sort_pairs(self, lst, reverse = False):
        lst.sort(key=lambda x: x.roi, reverse=reverse)

    def sort_tennis_games_by_roi(self, reverse = False):
        self._sort_pairs(self.tennis_pairs, reverse=reverse)

    def sort_football_games_by_roi(self, reverse = False):
        self._sort_pairs(self.football_pairs, reverse=reverse)

    def match_tennis_events(self, roi_threshold = -3):
        for e in self.site1.tennis_events:
            e.normalize_teams()
        for e in self.site2.tennis_events:
            e.normalize_teams()

        for event1 in self.site1.tennis_events:
            for event2 in self.site2.tennis_events:
                if Matcher._check_if_tennis_events_match(event1, event2):
                    #conteaza ordinea la odds
                    #1 cu 2
                    (stake1, stake2, roi) = Matcher.calculate_roi(event1.odds1, event2.odds2)
                    if roi > roi_threshold:
                        self.add_tennis_event_pair(EventPair(Sports.TENNIS, event1, event2, stake1, stake2, BetTypes.BET_1, BetTypes.BET_2, roi))

                    #2 cu 1
                    (stake1, stake2, roi) = Matcher.calculate_roi(event1.odds2, event2.odds1)
                    if roi > roi_threshold:
                        self.add_tennis_event_pair(EventPair(Sports.TENNIS, event1, event2, stake1, stake2, BetTypes.BET_2, BetTypes.BET_1, roi))

    def match_football_events(self, roi_threshold = -3):
        for e in self.site1.football_events:
            e.normalize_teams(2)
        for e in self.site2.football_events:
            e.normalize_teams(2)

        for event1 in self.site1.football_events:
            for event2 in self.site2.football_events:
                if Matcher._check_if_tennis_events_match(event1, event2): #probabil merge si la fotbal asta
                    #1X cu 2
                    (stake1, stake2, roi) = Matcher.calculate_roi(event1.odds1x, event2.odds2)
                    if roi > roi_threshold:
                        self.add_football_event_pair(EventPair(Sports.FOOTBALL, event1, event2, stake1, stake2, BetTypes.BET_1X, BetTypes.BET_2, roi))

                    #2 cu 1X
                    (stake1, stake2, roi) = Matcher.calculate_roi(event1.odds2, event2.odds1x)
                    if roi > roi_threshold:
                        self.add_football_event_pair(EventPair(Sports.FOOTBALL, event1, event2, stake1, stake2, BetTypes.BET_2, BetTypes.BET_1X, roi))

                    #1 cu X2
                    (stake1, stake2, roi) = Matcher.calculate_roi(event1.odds1, event2.oddsx2)
                    if roi > roi_threshold:
                        self.add_football_event_pair(EventPair(Sports.FOOTBALL, event1, event2, stake1, stake2, BetTypes.BET_1, BetTypes.BET_X2, roi))

                    #X2 cu 1
                    (stake1, stake2, roi) = Matcher.calculate_roi(event1.oddsx2, event2.odds1)
                    if roi > roi_threshold:
                        self.add_football_event_pair(EventPair(Sports.FOOTBALL, event1, event2, stake1, stake2, BetTypes.BET_X2, BetTypes.BET_1, roi))

                    #12 cu X
                    (stake1, stake2, roi) = Matcher.calculate_roi(event1.odds12, event2.oddsx)
                    if roi > roi_threshold:
                        self.add_football_event_pair(EventPair(Sports.FOOTBALL, event1, event2, stake1, stake2, BetTypes.BET_12, BetTypes.BET_X, roi))

                    #X cu 12
                    (stake1, stake2, roi) = Matcher.calculate_roi(event1.oddsx, event2.odds12)
                    if roi > roi_threshold:
                        self.add_football_event_pair(EventPair(Sports.FOOTBALL, event1, event2, stake1, stake2, BetTypes.BET_X, BetTypes.BET_12, roi))

class EventPair:
    def __init__(self, sport, event1: Event, event2: Event, stake1: float, stake2: float, bettype1, bettype2, roi: float):
        self.sport = sport
        self.event1 = event1
        self.event2 = event2
        self.stake1 = stake1
        self.stake2 = stake2
        self.bettype1 = bettype1
        self.bettype2 = bettype2
        self.roi = roi

    def __str__(self):
        return f"{self.roi} | {self.bettype1} la {self.event1.site} - {self.bettype2} la {self.event2.site}" +\
            f"\n{self.event1.site}\n{self.event1}\nSTAKE: {self.stake1}" +\
            "\n--------------" +\
            f"\n{self.event2.site}\n{self.event2}\nSTAKE: {self.stake2}"