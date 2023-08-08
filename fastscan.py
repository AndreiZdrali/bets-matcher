from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from scrappers.purebet import Purebet
from scrappers.betfair import BetfairLive
from scrappers.superbet import Superbet
from scrappers.efbet import Efbet
from scrappers.casapariurilor import CasaPariurilor
from scrappers.stanleybet import Stanleybet
from scrappers.playonline import PlayOnlineLive
from sites import Days, BetTypes
from matcher import Matcher
from exchange_matcher import ExchangeMatcher
import threading, settings

class Settings:
    roi_threshold = -10
    min_odds = 1.7

settings.load_settings() #ca sa mearga

def get_betfair_events(result_event):
    ser = Service(r"C:\Users\Andrei\source\Python\bets-matcher\chromedriver.exe")
    opts = webdriver.ChromeOptions()
    opts.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

    driver = webdriver.Chrome(service=ser, options=opts)

    betfairlive = BetfairLive(driver)
    betfairlive.get_all_tennis_events() #football

    result_event['betfairlive'] = betfairlive

def get_playonlinelive_events(result_event):
    ser = Service(r"C:\Users\Andrei\source\Python\bets-matcher\chromedriver.exe")
    opts = webdriver.ChromeOptions()
    opts.binary_location = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

    driver = webdriver.Chrome(service=ser, options=opts)

    playonlinelive = PlayOnlineLive(driver)
    playonlinelive.get_all_tennis_events() #football

    result_event['playonlinelive'] = playonlinelive

result_dict = {}
thread_betfair = threading.Thread(target=get_betfair_events, args=[result_dict])
thread_playonlinelive = threading.Thread(target=get_playonlinelive_events, args=[result_dict])

thread_betfair.start()
thread_playonlinelive.start()
thread_betfair.join()
thread_playonlinelive.join()

betfair = result_dict['betfairlive']
playonlinelive = result_dict['playonlinelive']

lista_case = [playonlinelive]
for i in range(len(lista_case)):
    matcher = ExchangeMatcher(lista_case[i], betfair)
    matcher.match_tennis_events()
    matcher.sort_tennis_events_by_roi()
    for e in matcher.tennis_pairs: #football
        if e.bettype == BetTypes.BET_1 and e.event_bookie.odds1 < Settings.min_odds or\
            e.bettype == BetTypes.BET_2 and e.event_bookie.odds2 < Settings.min_odds:
            #e.bettype == BetTypes.BET_X and e.event_bookie.oddsx < Settings.min_odds or\
            continue
        print(e.short_str())
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