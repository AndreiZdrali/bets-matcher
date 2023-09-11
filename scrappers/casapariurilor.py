from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from events import TennisEvent, FootballEvent
from sites import SiteNames, SiteTennisURLs, SiteFootballURLs, Days
from scrappers.scrapper import ScrapperBase
import time
import datetime

class CasaPariurilor(ScrapperBase):
    def __init__(self, driver):
        super().__init__(driver)
        self.sitename = SiteNames.CASAPARIURILOR

    def _load_all_events(self, timeout = 2):
        page_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(timeout)
            new_page_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_page_height <= page_height:
                break
            page_height = new_page_height

    def get_all_tennis_events(self):
        self.driver.get(SiteTennisURLs.CASAPARIURILOR)

        self._load_all_events()

        bs = BeautifulSoup(self.driver.page_source, "html.parser")
        for event_html in bs.findAll("tr", {"class": "tablesorter-hasChildRow"}):
            tds = event_html.select("td") #primele 3 sunt nume, cota1, cota2

            [nume1, nume2] = [x.strip() for x in tds[0].select("span")[0].text.split(" - ")]
            [cota1, cota2] = [float(x.text.strip()) for x in tds[1:3]]

            event = TennisEvent(SiteNames.CASAPARIURILOR, nume1, nume2, cota1, cota2)

            self.add_if_not_included_tennis(event)

    def get_all_football_events(self):
        """INCREDIBIL DE INEFICIENT, MAI BINE get_football_events_by_day"""
        self.driver.get(SiteFootballURLs.CASAPARIURILOR)

        self._load_all_events(3)

        bs = BeautifulSoup(self.driver.page_source, "html.parser")
        for event_html in bs.findAll("tr", {"class": "tablesorter-hasChildRow"}):
            tds = event_html.select("td") #primele 3 sunt nume, cota1, cota2

            [nume1, nume2] = [x.strip() for x in tds[0].select("span")[0].text.split(" - ")]
            [cota1, cotax, cota2] = [float(x.text.strip()) for x in tds[1:4]]

            event = FootballEvent(SiteNames.CASAPARIURILOR, nume1, nume2, cota1, cotax, cota2)
            
            self.add_if_not_included_football(event)

    def get_football_events_by_day(self, date: datetime.date = Days.GET_TODAY()):
        year = f"{date.year}"
        month = f"0{date.month}" if date.month <= 9 else f"{date.month}"
        day = f"0{date.day}" if date.day <= 0 else f"{date.day}"
        self.driver.get(SiteFootballURLs.CASAPARIURILOR + f"?selectDates=1&date={year}-{month}-{day}")

        self._load_all_events(3)

        bs = BeautifulSoup(self.driver.page_source, "html.parser")
        for event_html in bs.findAll("tr", {"class": "tablesorter-hasChildRow"}):
            tds = event_html.select("td") #primele 3 sunt nume, cota1, cota2

            [nume1, nume2] = [x.strip() for x in tds[0].select("span")[0].text.split(" - ")]
            [cota1, cotax, cota2] = [float(x.text.strip()) for x in tds[1:4]]

            event = FootballEvent(SiteNames.CASAPARIURILOR, nume1, nume2, cota1, cotax, cota2)
            #!!!!!!!!!! SA FAC AICI SA IA COTELE DIRECT
            #event.odds1x = ...

            self.add_if_not_included_football(event)