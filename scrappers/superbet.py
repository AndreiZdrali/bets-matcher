from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from events import TennisEvent, FootballEvent
from sites import SiteNames, SiteTennisURLs, SiteFootballURLs
from scrappers.scrapper import ScrapperBase

class Superbet(ScrapperBase):
    def __init__(self, driver):
        super().__init__(driver)

    def get_all_tennis_events(self):
        self.driver.get(SiteTennisURLs.SUPERBET)
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "primary-market__wrapper")))
        
        current_scroll = 0
        while current_scroll < self.driver.execute_script("return document.body.scrollHeight"):
            bs = BeautifulSoup(self.driver.page_source, "html.parser")
            for event_html in bs.findAll("div", {"class": "event-row-container"}):
                try:
                    nume1 = event_html.find("span", {"class": "event-summary__competitors-team1"}).text.strip()
                    nume2 = event_html.find("span", {"class": "event-summary__competitors-team2"}).text.strip()
                    [cota1, cota2] = [float(x.text.strip()) for x in event_html.select("span.value.new.actionable")]

                    event = TennisEvent(SiteNames.SUPERBET, nume1, nume2, cota1, cota2)

                    self.add_if_not_included_tennis(event)
                except:
                    continue
                self.driver.execute_script("window.scrollBy(0, 100)")
                current_scroll += 100

    def get_all_football_events(self):
        self.driver.get(SiteFootballURLs.SUPERBET)
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "primary-market__wrapper")))
        
        current_scroll = 0
        while current_scroll < self.driver.execute_script("return document.body.scrollHeight"):
            bs = BeautifulSoup(self.driver.page_source, "html.parser")
            for event_html in bs.findAll("div", {"class": "event-row-container"}):
                try:
                    nume1 = event_html.find("span", {"class": "event-summary__competitors-team1"}).text.strip()
                    nume2 = event_html.find("span", {"class": "event-summary__competitors-team2"}).text.strip()
                    [cota1, cotax, cota2] = [float(x.text.strip()) for x in event_html.select("span.value.new.actionable")]
                    event = FootballEvent(SiteNames.SUPERBET, nume1, nume2, cota1, cotax, cota2)

                    self.add_if_not_included_football(event)
                except:
                    continue
                self.driver.execute_script("window.scrollBy(0, 100)")
                current_scroll += 100