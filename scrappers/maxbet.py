from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from events import TennisEvent, FootballEvent
from sites import SiteNames, SiteTennisURLs, SiteFootballURLs
from scrappers.scrapper import ScrapperBase
from datetime import datetime, timedelta
import time, requests

class Maxbet(ScrapperBase):
    def __init__(self, driver):
        super().__init__(driver)
        self.sitename = SiteNames.MAXBET

class MaxbetLive(Maxbet):
    def __init__(self, driver):
        super().__init__(driver)
        self.sitename = SiteNames.MAXBETLIVE

    def _load_page_tennis(self):
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "icon-sport-5")))
        self.driver.find_element(By.CLASS_NAME, "icon-sport-5").click()
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "match-bet-outcome-value")))
        time.sleep(1)

    def _load_page_football(self):
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "icon-sport-1")))
        self.driver.find_element(By.CLASS_NAME, "icon-sport-1").click()
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "match-bet-outcome-value")))
        time.sleep(1)

    def get_all_tennis_events(self):
        self.driver.get(SiteTennisURLs.MAXBETLIVE)
        self._load_page_tennis()

        bs = BeautifulSoup(self.driver.page_source, "html.parser")

        #CSS selector pentru div-ul scrollable
        container_selector = "#app > div > div > div.header-body-content-wrapper > div.body-content > div.content > div > div > div.__panel"

        current_scroll = 0
        while current_scroll < self.driver.execute_script(f"return document.querySelector(\"{container_selector}\").scrollHeight"):
            bs = BeautifulSoup(self.driver.page_source, "html.parser")

            for event_html in bs.findAll("div", {"class": "match-row"}):
                try:
                    nume = event_html.findAll("div", {"class": "team-details"})
                    cote = event_html.findAll("div", {"class": "match-bet-outcome-value"})

                    [nume1, nume2] = [x.text.strip() for x in nume[0:2]]
                    [cota1, cota2] = [float(x.text.strip()) for x in cote[0:2]]

                    event = TennisEvent(self.sitename, nume1, nume2, cota1, cota2)

                    self.add_if_not_included_tennis(event)
                except:
                    continue
            self.driver.execute_script(f"document.querySelector(\"{container_selector}\").scrollTop += 400")
            current_scroll += 400
            time.sleep(0.5)

    def get_all_football_events(self):
        self.driver.get(SiteFootballURLs.MAXBETLIVE)
        self._load_page_football()

        bs = BeautifulSoup(self.driver.page_source, "html.parser")

        #CSS selector pentru div-ul scrollable
        container_selector = "#app > div > div > div.header-body-content-wrapper > div.body-content > div.content > div > div > div.__panel"

        current_scroll = 0
        while current_scroll < self.driver.execute_script(f"return document.querySelector(\"{container_selector}\").scrollHeight"):
            bs = BeautifulSoup(self.driver.page_source, "html.parser")

            for event_html in bs.findAll("div", {"class": "match-row"}):
                try:
                    nume = event_html.findAll("div", {"class": "team-details"})
                    cote = event_html.findAll("div", {"class": "match-bet-outcome-value"})

                    [nume1, nume2] = [x.text.strip() for x in nume[0:2]]
                    [cota1, cotax, cota2] = [float(x.text.strip()) for x in cote[0:3]]

                    event = FootballEvent(self.sitename, nume1, nume2, cota1, cotax, cota2)

                    self.add_if_not_included_football(event)
                except:
                    continue
            self.driver.execute_script(f"document.querySelector(\"{container_selector}\").scrollTop += 400")
            current_scroll += 400
            time.sleep(0.5)