from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from events import TennisEvent, FootballEvent
from sites import SiteNames, SiteTennisURLs, SiteFootballURLs
import requests
from scrappers.scrapper import ScrapperBase

class Purebet(ScrapperBase):
    def __init__(self):
        super().__init__()

    def get_all_tennis_events(self):
        pass

    def get_all_football_events(self):
        r = requests.get(SiteFootballURLs.PUREBET)
        json_data = r.json()["soccer"]

        for league in json_data:
            for event_json in json_data[league]:
                nume1, nume2 = event_json["homeTeam"], event_json["awayTeam"]
                cote = event_json["full_time_result"]
                cota1 = cote["home"]["Lay"]["highestOdds"]
                cotax = cote["draw"]["Lay"]["highestOdds"]
                cota2 = cote["away"]["Lay"]["highestOdds"]

                event = FootballEvent(SiteNames.PUREBET, nume1, nume2, cota1, cotax, cota2)

                self.add_football(event)