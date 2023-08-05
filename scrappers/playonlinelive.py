from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from events import TennisEvent, FootballEvent
from sites import SiteNames, SiteTennisURLs, SiteFootballURLs
from scrappers.scrapper import ScrapperBase
import time

class PlayOnlineLive(ScrapperBase):
    def __init__(self, driver):
        super().__init__(driver)

    def get_all_tennis_events(self):
        pass

    def _load_all_events(self):
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "odds-container")))
        for _ in range(100):
            self.driver.execute_script("window.scrollBy(0, 200)")
            time.sleep(0.05)

    def get_all_football_events(self):
        self.driver.get(SiteFootballURLs.PLAYONLINELIVE)
        self._load_all_events()

        bs = BeautifulSoup(self.driver.page_source, "html.parser")
        table = bs.find("div", {"class": "table"}) #primul tabel e fotbal

        for event_html in table.findAll("div", {"class": "table-row"}):
            try:
                nume = event_html.find("span", {"class": "match-title-text"})
                cote = event_html.findAll("span", {"class": "value"})

                [nume1, nume2] = nume.text.split(" - ")
                [cota1, cotax, cota2] = [float(x.text.strip()) for x in cote]
                
                event = FootballEvent(SiteNames.PLAYONLINELIVE, nume1, nume2, cota1, cotax, cota2)

                self.add_if_not_included_football(event)
            #da ValueError daca sunt pariurile blocate
            except ValueError as e:
                continue