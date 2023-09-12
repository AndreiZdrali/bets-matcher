from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from events import TennisEvent, FootballEvent
from sites import SiteNames, SiteTennisURLs, SiteFootballURLs
from scrappers.scrapper import ScrapperBase
from datetime import datetime, timedelta
import time, requests

class VulkanBet(ScrapperBase):
    def __init__(self, driver):
        super().__init__(driver)
        self.sitename = SiteNames.VULKANBET

class VulkanBetLive(VulkanBet):
    def __init__(self, driver):
        super().__init__(driver)
        self.sitename = SiteNames.VULKANBETLIVE

    def _load_all_events(self):
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "__app-MatchInfo-competitors")))
        for _ in range(100):
            self.driver.execute_script("window.scrollBy(0, 200)")
            time.sleep(0.05)

    def get_all_tennis_events(self):
        self.driver.get(SiteTennisURLs.VULKANBETLIVE)
        self._load_all_events()

        bs = BeautifulSoup(self.driver.page_source, "html.parser")
        for event_html in bs.findAll("div", {"class": "__app-MultimarketMatchRow-container"}):
            try:
                nume = event_html.findAll("div", {"class": "__app-Competitor-name"})
                cote = event_html.findAll("div", {"class": "__app-MarketDefault-odd-container"})

                [nume1, nume2] = [x.text.strip() for x in nume]
                [cota1, cota2] = [float(x.text.strip()) for x in cote[0:2]]

                event = TennisEvent(self.sitename, nume1, nume2, cota1, cota2)

                self.add_if_not_included_tennis(event)
            #da ValueError daca sunt pariurile blocate
            except ValueError as e:
                continue

    def get_all_football_events(self):
        self.driver.get(SiteFootballURLs.VULKANBETLIVE)
        self._load_all_events()

        bs = BeautifulSoup(self.driver.page_source, "html.parser")
        for event_html in bs.findAll("div", {"class": "__app-MultimarketMatchRow-container"}):
            try:
                nume = event_html.findAll("div", {"class": "__app-Competitor-name"})
                cote = event_html.findAll("div", {"class": "__app-MarketDefault-odd-container"})

                [nume1, nume2] = [x.text.strip() for x in nume]
                [cota1, cotax, cota2] = [float(x.text.strip()) for x in cote[0:3]]

                event = FootballEvent(self.sitename, nume1, nume2, cota1, cotax, cota2)

                self.add_if_not_included_football(event)
            #da ValueError daca sunt pariurile blocate
            except ValueError as e:
                continue