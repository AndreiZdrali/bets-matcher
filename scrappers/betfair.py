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

class Betfair(ScrapperBase):
    def __init__(self, driver):
        super().__init__(driver)

    def _load_all_events(self):
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "mod-event-line")))
        time.sleep(1.2) #era 2

    def _is_live_tennis(self, event_html):
        #e live cu verde si scor
        if event_html.find("div", {"class": "scores"}):
            return True

        time_text = event_html.find("span", {"class": "label"}).text
        
        #e live cu verde
        if time_text == "Live":
            return True
        
        #urmeaza sa inceapa dar apare pe live
        if time_text in ["Începe în curând", "Începe în 6'" "Începe în 5'", "Începe în 4'", "Începe în 3'"]:
            return True
        
        return False

    def _is_live_football(self, event_html):
        #e live cu verde si minute + scor
        if event_html.find("div", {"class": "middle-label"}):
            return True
        
        time_text = event_html.find("span", {"class": "label"}).text
        
        #e live cu verde
        if time_text == "Live":
            return True
        
        #urmeaza sa inceapa dar apare pe live
        if time_text in ["Începe în curând", "Începe în 5'", "Începe în 4'", "Începe în 3'"]:
            return True
        
        return False

    def get_all_tennis_events(self, days=0, page=1):

        day_to_scan = "today"
        if days == 1:
            day_to_scan = "tomorrow"
        elif days >= 2:
            day_to_scan = "future"
        
        self.driver.get(SiteTennisURLs.BETFAIR + f"/{day_to_scan}/{page}")
        #sorteaza dupa timp, nu cred ca trb refresh pt ca seteaza inainte de fetch
        self.driver.execute_script("localStorage.setItem(\"coupon.group-by\", \"time\")")
        self.driver.execute_script("localStorage.setItem(\"marketRefreshRate\", 1)")

        time.sleep(0.2)
        self.driver.refresh() #ca sa fie cotele actualizate

        self._load_all_events()

        bs = BeautifulSoup(self.driver.page_source, "html.parser")

        for event_html in bs.findAll("tr", {"ng-if": "event.isReady && event.isVisible"}):
            try:
                if not self._is_live_tennis(event_html):
                    nume = event_html.find("ul", {"class": "runners"})
                    lay_buttons = event_html.findAll("button", {"class": "lay"})
                    cote = [x.find("label") for x in lay_buttons]

                    [nume1, nume2] = [x.text for x in nume.findAll("li", {"class": "name"})]
                    [cota1, cota2] = [float(x.text.strip()) for x in cote]

                    event = TennisEvent(SiteNames.BETFAIR, nume1, nume2, cota1, cota2)
                    event.url = event_html.find("a")["href"]

                    self.add_if_not_included_tennis(event)
            except:
                continue
        
        if page >= len(bs.findAll("li", {"class": "coupon-page-navigation__bullet"})):
            return

        self.get_all_tennis_events(days, page + 1)

    def get_all_football_events(self, days=0, page=1):
        day_to_scan = "today"
        if days == 1:
            day_to_scan = "tomorrow"
        elif days >= 2:
            day_to_scan = "future"
        
        self.driver.get(SiteFootballURLs.BETFAIR + f"/{day_to_scan}/{page}")
        #sorteaza dupa timp, nu cred ca trb refresh pt ca seteaza inainte de fetch
        self.driver.execute_script("localStorage.setItem(\"coupon.group-by\", \"time\")")
        self.driver.execute_script("localStorage.setItem(\"marketRefreshRate\", 1)")
        
        time.sleep(0.2)
        self.driver.refresh() #ca sa fie cotele actualizate

        self._load_all_events()

        bs = BeautifulSoup(self.driver.page_source, "html.parser")

        for event_html in bs.findAll("tr", {"ng-if": "event.isReady && event.isVisible"}):
            try:
                if not self._is_live_football(event_html):
                    nume = event_html.find("ul", {"class": "runners"})
                    lay_buttons = event_html.findAll("button", {"class": "lay"})
                    cote = [x.find("label") for x in lay_buttons]

                    [nume1, nume2] = [x.text for x in nume.findAll("li", {"class": "name"})]
                    [cota1, cotax, cota2] = [float(x.text.strip()) for x in cote]

                    event = FootballEvent(SiteNames.BETFAIR, nume1, nume2, cota1, cotax, cota2)
                    event.url = event_html.find("a")["href"]

                    self.add_if_not_included_football(event)
            except:
                continue

        if page >= len(bs.findAll("li", {"class": "coupon-page-navigation__bullet"})):
            return

        self.get_all_football_events(days, page + 1)


class BetfairLive(Betfair):
    def __init__(self, driver):
        super().__init__(driver)

    def get_all_tennis_events(self, page=1):
        self.driver.get(SiteTennisURLs.BETFAIRLIVE + f"/{page}")
        #sorteaza dupa timp, nu cred ca trb refresh pt ca seteaza inainte de fetch
        self.driver.execute_script("localStorage.setItem(\"coupon.group-by\", \"time\")")
        self.driver.execute_script("localStorage.setItem(\"marketRefreshRate\", 1)")

        time.sleep(0.2)
        self.driver.refresh() #ca sa fie cotele actualizate

        self._load_all_events()

        bs = BeautifulSoup(self.driver.page_source, "html.parser")

        next_page = False
        for event_html in bs.findAll("tr", {"ng-if": "event.isReady && event.isVisible"}):
            try:
                if self._is_live_tennis(event_html):
                    nume = event_html.find("ul", {"class": "runners"})
                    lay_buttons = event_html.findAll("button", {"class": "lay"})
                    cote = [x.find("label") for x in lay_buttons]

                    [nume1, nume2] = [x.text for x in nume.findAll("li", {"class": "name"})]
                    [cota1, cota2] = [float(x.text.strip()) for x in cote]

                    event = TennisEvent(SiteNames.BETFAIRLIVE, nume1, nume2, cota1, cota2)
                    event.url = event_html.find("a")["href"]

                    self.add_if_not_included_tennis(event)
                    next_page = True
            except:
                continue
        
        if next_page and page < len(bs.findAll("li", {"class": "coupon-page-navigation__bullet"})):
            self.get_all_tennis_events(page + 1)

    def get_all_football_events(self, page=1):
        self.driver.get(SiteFootballURLs.BETFAIRLIVE + f"/{page}")
        #sorteaza dupa timp, nu cred ca trb refresh pt ca seteaza inainte de fetch
        self.driver.execute_script("localStorage.setItem(\"coupon.group-by\", \"time\")")
        self.driver.execute_script("localStorage.setItem(\"marketRefreshRate\", 1)")
        
        time.sleep(0.2)
        self.driver.refresh() #ca sa fie cotele actualizate

        self._load_all_events()

        bs = BeautifulSoup(self.driver.page_source, "html.parser")

        next_page = False
        for event_html in bs.findAll("tr", {"ng-if": "event.isReady && event.isVisible"}):
            try:
                if self._is_live_football(event_html):
                    nume = event_html.find("ul", {"class": "runners"})
                    lay_buttons = event_html.findAll("button", {"class": "lay"})
                    cote = [x.find("label") for x in lay_buttons]

                    [nume1, nume2] = [x.text for x in nume.findAll("li", {"class": "name"})]
                    [cota1, cotax, cota2] = [float(x.text.strip()) for x in cote]

                    event = FootballEvent(SiteNames.BETFAIRLIVE, nume1, nume2, cota1, cotax, cota2)
                    event.url = event_html.find("a")["href"]

                    self.add_if_not_included_football(event)
                    next_page = True
            except:
                continue
        
        if next_page and page < len(bs.findAll("li", {"class": "coupon-page-navigation__bullet"})):
            self.get_all_football_events(page + 1)
