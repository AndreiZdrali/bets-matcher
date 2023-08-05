import hashlib
import re
import utils

class Event:
    def __init__(self, site):
        self.site = site
        self.time = None
        #sa diferentieze meciurile cand le reia pe unele site-uri; vezi scrapper.py -> not_included_tennis()
        self.hash = None
        self.team1 = None
        self.team2 = None
        self.team1_norm = None
        self.team2_norm = None
        self.odds1 = None
        self.odds2 = None
        self.url = None

    def __str__(self):
        return f"{self.team1}: {self.odds1}\n{self.team2}: {self.odds2}"

    def swap_teams(self):
        utils.swap(self.team1, self.team2)
        utils.swap(self.team1_norm, self.team2_norm)
        utils.swap(self.odds1, self.odds2)

    def normalize_teams(self, length_threshold = 1):
        #POSIBIL SA DISPARA MULTE MATCH-URI DIN CAUZA ASTA
        blacklist = ["fc", "u20", "u21"] #lower pt ca compar cu lower
        #len(x) > 1 ca sa nu ia si prescurtarile la meciurile duble gen R. Nadal
        self.team1_norm = [x for x in self.team1.lower().replace("/", " ").replace(".", " ").replace("-", " ")\
            .split() if len(x) > length_threshold and x not in blacklist]
        self.team2_norm = [x for x in self.team2.lower().replace("/", " ").replace(".", " ").replace("-", " ")\
            .split() if len(x) > length_threshold and x not in blacklist]

class TennisEvent(Event):
    def __init__(self, site: str, team1: str, team2: str, odds1: float, odds2: float):
        super().__init__(site)
        self.team1 = team1
        self.team2 = team2
        self.odds1 = odds1
        self.odds2 = odds2

    def get_hash(self):
        if self.hash is None:
            self.hash = hashlib.md5(f"{self.team1}{self.team2}{self.odds1}{self.odds2}".encode()).hexdigest()
        return self.hash

class FootballEvent(Event):
    def __init__(self, site: str, team1: str, team2: str, odds1: float, oddsx: float, odds2: float):
        super().__init__(site)
        self.team1 = team1
        self.team2 = team2
        self.odds1 = odds1
        self.oddsx = oddsx
        self.odds2 = odds2
        self.odds1x = round((odds1 * oddsx) / (odds1 + oddsx), 2)
        self.oddsx2 = round((oddsx * odds2) / (oddsx + odds2), 2)
        self.odds12 = round((odds1 * odds2) / (odds1 + odds2), 2)

    def __str__(self):
        return f"{self.team1}: {self.odds1}\nEgal: {self.oddsx}\n{self.team2}: {self.odds2}" +\
            f"\n1X: {self.odds1x} | X2: {self.oddsx2} | 12: {self.odds12}"

    def swap_teams(self):
        utils.swap(self.team1, self.team2)
        utils.swap(self.team1_norm, self.team2_norm)
        utils.swap(self.odds1, self.odds2)
        utils.swap(self.odds1x, self.oddsx2)

    def get_hash(self):
        if self.hash is None:
            self.hash = hashlib.md5(f"{self.team1}{self.team2}{self.odds1}{self.oddsx}{self.odds2}".encode()).hexdigest()
        return self.hash

    #in caz de orice, asta exista aici
    def _update_double_chance(self):
        self.odds1x = (self.odds1 * self.oddsx) / (self.odds1 + self.oddsx)
        self.oddsx2 = (self.oddsx * self.odds2) / (self.oddsx + self.odds2)
        self.odds12 = (self.odds1 * self.odds2) / (self.odds1 + self.odds2)