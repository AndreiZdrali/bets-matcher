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

class BetfairLive(ScrapperBase):
    def __init__(self, driver):
        super().__init__(driver)

    def get_all_tennis_events(self):
        pass

    def _load_all_events(self):
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "mod-event-line")))
        time.sleep(3)

    def _is_live(self, event_html):
        #e live cu verde si minute + scor
        if event_html.find("div", {"class": "middle-label"}):
            return True
        
        time_text = event_html.find("div", {"class": "label"})
        if not time_text:
            return False
        
        #e live cu verde
        if time_text == "Live":
            return True
        
        #urmeaza sa inceapa dar apare pe live
        if time_text in ["Începe în curând", "Începe în 5'", "Începe în 4'", "Începe în 3'"]:
            return True
        
        return False


    def get_all_football_events(self, page=1):
        self.driver.get(SiteFootballURLs.BETFAIRLIVE + f"/{page}")
        #sorteaza dupa timp, nu cred ca trb refresh pt ca seteaza inainte de fetch
        self.driver.execute_script("localStorage.setItem(\"coupon.group-by\", \"time\")")
        #self.driver.refresh()

        self._load_all_events()

        bs = BeautifulSoup(self.driver.page_source, "html.parser")

        next_page = False
        for event_html in bs.findAll("tr", {"ng-if": "event.isReady && event.isVisible"}):
            if self._is_live(event_html):
                try:
                    nume = event_html.find("ul", {"class": "runners"})
                    lay_buttons = event_html.findAll("button", {"class": "lay"})
                    cote = [x.find("label") for x in lay_buttons]
                    url = event_html.find("a")["href"]

                    [nume1, nume2] = [x.text for x in nume.findAll("li", {"class": "name"})]
                    [cota1, cotax, cota2] = [float(x.text.strip()) for x in cote]

                    event = FootballEvent(SiteNames.BETFAIRLIVE, nume1, nume2, cota1, cotax, cota2)
                    event.url = event_html.find("a")["href"]

                    self.add_if_not_included_football(event)
                    next_page = True
                except:
                    continue
        
        if next_page:
            self.get_all_football_events(page + 1)
