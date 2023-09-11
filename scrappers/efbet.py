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

class Efbet(ScrapperBase):
    def __init__(self, driver):
        super().__init__(driver)
        self.sitename = SiteNames.EFBET

    def _load_all_events_beta(self):
        # WebDriverWait(self.driver, 20).until(EC.none_of(
        #     EC.presence_of_all_elements_located((By.XPATH, "//*[contains(text(), 'Se încarcă datele, așteptați...')]"))
        #     ))

        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "container-placeholder"))) #posibil schimbat

        #pe efbet containerele care merg extinse au o clasa numita "container"; si "expanded" daca sunt extinse
        bs = BeautifulSoup(self.driver.page_source, "html.parser")
        
        current_scroll = 0
        while current_scroll < self.driver.execute_script("return document.body.scrollHeight"):
            expandables = [x for x in bs.findAll("div", {"class": "container"}) if "expanded" not in x["class"]]
            for container in expandables:
                WebDriverWait(self.driver, 20)\
                    .until(EC.element_to_be_clickable((By.CSS_SELECTOR, self._get_css_path(container)))).click()
                time.sleep(0.5)

            self.driver.execute_script("window.scrollBy(0, 100)")
            current_scroll += 100

    def _load_all_events(self):
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Se încarcă datele, așteptați...')]")))
        for _ in range(100):
            self.driver.execute_script("window.scrollBy(0, 100)")
            time.sleep(0.1)

    def get_all_tennis_events(self):
        self.driver.get(SiteTennisURLs.EFBET)

        for _ in range(10):
            try:
                WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "wgtennis"))).click()
                break
            except:
                time.sleep(0.5)

        self._load_all_events()

        bs = BeautifulSoup(self.driver.page_source, "html.parser")
        for event_html in bs.findAll("tr", {"class": ["row0", "row1"]}):
            try:
                hrefs = event_html.select("a")

                [nume1, nume2] = hrefs[0].text.split(" vs ")
                [cota1, cota2] = [float(x.text.strip()) for x in hrefs[1:3]]

                event = TennisEvent(SiteNames.EFBET, nume1, nume2, cota1, cota2)
                self.add_if_not_included_tennis(event)
            except:
                continue

    def get_all_football_events(self):
        self.driver.get(SiteFootballURLs.EFBET)

        for _ in range(10):
            try:
                WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "wgfootball"))).click()
                break
            except:
                time.sleep(0.5)

        self._load_all_events()

        bs = BeautifulSoup(self.driver.page_source, "html.parser")
        for event_html in bs.findAll("tr", {"class": ["row0", "row1"]}):
            try:
                hrefs = event_html.select("a")

                [nume1, nume2] = hrefs[0].text.split(" vs ")
                [cota1, cotax, cota2] = [float(x.text.strip()) for x in hrefs[1:4]]

                event = FootballEvent(SiteNames.EFBET, nume1, nume2, cota1, cotax, cota2)
                self.add_if_not_included_football(event)
            except:
                continue