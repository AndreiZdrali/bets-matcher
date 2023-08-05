from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from scrappers.purebet import Purebet
from scrappers.betfairlive import BetfairLive
from scrappers.superbet import Superbet
from scrappers.efbet import Efbet
from scrappers.casapariurilor import CasaPariurilor
from scrappers.stanleybet import Stanleybet
from scrappers.playonlinelive import PlayOnlineLive
from sites import Days, BetTypes
from matcher import Matcher
from exchange_matcher import ExchangeMatcher
import datetime

class Settings:
    roi_threshold = -10
    min_odds = 1.9

ser = Service(r"C:\Users\Andrei\source\Python\bets-matcher\chromedriver.exe")
opts = webdriver.ChromeOptions()
opts.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

driver = webdriver.Chrome(service=ser, options=opts)

betfair = BetfairLive(driver)
betfair.get_all_football_events()

playonlinelive = PlayOnlineLive(driver)
playonlinelive.get_all_football_events()

lista_case = [playonlinelive]
for i in range(len(lista_case)):
    matcher = ExchangeMatcher(lista_case[i], betfair)
    matcher.match_football_events(roi_threshold=Settings.roi_threshold)
    matcher.sort_football_games_by_roi()
    for e in matcher.football_pairs:
        if e.bettype == BetTypes.BET_1 and e.event_bookie.odds1 < Settings.min_odds or\
            e.bettype == BetTypes.BET_X and e.event_bookie.oddsx < Settings.min_odds or\
            e.bettype == BetTypes.BET_2 and e.event_bookie.odds2 < Settings.min_odds:
            continue
        print(e)
        print("==============")

# lista_case = [superbet]
# for i in range(len(lista_case) - 1):
#     for j in range(i + 1, len(lista_case)):
#         matcher = Matcher(lista_case[i], lista_case[j])
#         matcher.match_football_events()
#         matcher.sort_football_games_by_roi()
#         for e in matcher.football_pairs:
#             print(e)
#             print("==============")