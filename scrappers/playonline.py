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

class PlayOnline(ScrapperBase):
    def __init__(self, driver):
        super().__init__(driver)
        self.sitename = SiteNames.PLAYONLINE

    #https://sportsbook-sm-distribution-api.nsoft.com/api/v1/events?filter[from]=2023-08-09T00:00:00&filter[to]=2023-08-09T23:59:59&filter[sportId]=18&timezone=Europe%2FBucharest&language=%7B%22default%22:%22ro%22,%22events%22:%22ro%22,%22category%22:%22ro%22,%22sport%22:%22ro%22,%22tournament%22:%22ro%22,%22market%22:%22ro%22,%22marketGroup%22:%22ro%22%7D&dataFormat=%7B%22default%22:%22object%22,%22events%22:%22array%22,%22markets%22:%22array%22,%22outcomes%22:%22array%22%7D&companyUuid=04301c5a-6b6c-4694-aaf5-f81bf665498c&deliveryPlatformId=3&shortProps=1
    def get_all_tennis_events(self, days=0):
        day_to_scan = datetime.now() + timedelta(days=days)
        from_time = day_to_scan.strftime('%Y-%m-%d') + "T00:00:00"
        to_time = day_to_scan.strftime('%Y-%m-%d') + "T23:59:59"
        id = 78
        api_query = f"/events?filter[from]={from_time}&filter[to]={to_time}&filter[sportId]={id}&timezone=Europe%2FBucharest&language=%7B%22default%22:%22ro%22,%22events%22:%22ro%22,%22category%22:%22ro%22,%22sport%22:%22ro%22,%22tournament%22:%22ro%22,%22market%22:%22ro%22,%22marketGroup%22:%22ro%22%7D&dataFormat=%7B%22default%22:%22object%22,%22events%22:%22array%22,%22markets%22:%22array%22,%22outcomes%22:%22array%22%7D&companyUuid=04301c5a-6b6c-4694-aaf5-f81bf665498c&deliveryPlatformId=3&shortProps=1"

        r = requests.get(SiteTennisURLs.PLAYONLINE + api_query)
        json_data = r.json()["data"]["events"]
        mappings = r.json()["data"]["_mapping"]

        m_name = mappings["event"]["name"] # j
        m_markets = mappings["event"]["markets"] # o
        m_outcomes = mappings["market"]["outcomes"] # h
        m_bettype = mappings["outcome"]["name"] # e
        m_odds = mappings["outcome"]["odd"] # g

        #try aici pt ca nu mereu sunt disponibile 12
        for event_json in json_data:
            try:
                nume = event_json[m_name]
                cote = event_json[m_markets][0][m_outcomes] #posibil sa nu existe

                if cote[0][m_bettype] != "1" and cote[1][m_bettype] != "2": #daca prima nu e 12
                    continue

                [nume1, nume2] = nume.split(" - ")
                [cota1, cota2] = [cote[0][m_odds], cote[1][m_odds]]

                event = TennisEvent(SiteNames.PLAYONLINE, nume1, nume2, cota1, cota2)
                
                self.add_tennis(event)
            except:
                continue

    def get_all_football_events(self, days=0):
        day_to_scan = datetime.now() + timedelta(days=days)
        from_time = day_to_scan.strftime('%Y-%m-%d') + "T00:00:00"
        to_time = day_to_scan.strftime('%Y-%m-%d') + "T23:59:59"
        id = 18
        api_query = f"/events?filter[from]={from_time}&filter[to]={to_time}&filter[sportId]={id}&timezone=Europe%2FBucharest&language=%7B%22default%22:%22ro%22,%22events%22:%22ro%22,%22category%22:%22ro%22,%22sport%22:%22ro%22,%22tournament%22:%22ro%22,%22market%22:%22ro%22,%22marketGroup%22:%22ro%22%7D&dataFormat=%7B%22default%22:%22object%22,%22events%22:%22array%22,%22markets%22:%22array%22,%22outcomes%22:%22array%22%7D&companyUuid=04301c5a-6b6c-4694-aaf5-f81bf665498c&deliveryPlatformId=3&shortProps=1"

        r = requests.get(SiteFootballURLs.PLAYONLINE + api_query)
        json_data = r.json()["data"]["events"]
        mappings = r.json()["data"]["_mapping"]

        m_name = mappings["event"]["name"] # j
        m_markets = mappings["event"]["markets"] # o
        m_outcomes = mappings["market"]["outcomes"] # h
        m_bettype = mappings["outcome"]["name"] # e
        m_odds = mappings["outcome"]["odd"] # g

        #posibil sa trb un try aici pt cand nu sunt cote de 1x2
        for event_json in json_data:
            try:
                nume = event_json[m_name]
                cote = event_json[m_markets][0][m_outcomes]

                #nu stiu daca prima e mereu 1x2
                if cote[0][m_bettype] != "1" and cote[1][m_bettype].lower() != "x" and cote[2][m_bettype] != "2":
                    continue

                [nume1, nume2] = nume.split(" - ")
                [cota1, cotax, cota2] = [cote[0][m_odds], cote[1][m_odds], cote[2][m_odds]]

                event = FootballEvent(SiteNames.PLAYONLINE, nume1, nume2, cota1, cotax, cota2)

                self.add_football(event)
            except:
                continue

class PlayOnlineLive(PlayOnline):
    def __init__(self, driver):
        super().__init__(driver)
        self.sitename = SiteNames.PLAYONLINELIVE

    def _load_all_events(self):
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "odds-container")))
        for _ in range(100):
            self.driver.execute_script("window.scrollBy(0, 200)")
            time.sleep(0.05)

    def get_all_tennis_events(self):
        self.driver.get(SiteFootballURLs.PLAYONLINELIVE)
        self._load_all_events()

        bs = BeautifulSoup(self.driver.page_source, "html.parser")
        tables = bs.findAll("div", {"class": "table"})

        table = None
        for t in tables:
            table_title = t.find("div", {"class": "table-title"}).text
            if table_title.strip() == "Tenis":
                table = t
                break

        if table is None:
            return

        for event_html in table.findAll("div", {"class": "table-row"}):
            try:
                nume = event_html.find("span", {"class": "match-title-text"})
                cote = event_html.findAll("span", {"class": "value"})

                [nume1, nume2] = nume.text.split(" - ")
                [cota1, cota2] = [float(x.text.strip()) for x in cote]
                
                event = TennisEvent(self.sitename, nume1, nume2, cota1, cota2)

                self.add_if_not_included_tennis(event)
            #da ValueError daca sunt pariurile blocate
            except ValueError as e:
                continue

    def get_all_football_events(self):
        self.driver.get(SiteFootballURLs.PLAYONLINELIVE)
        self._load_all_events()

        bs = BeautifulSoup(self.driver.page_source, "html.parser")
        tables = bs.findAll("div", {"class": "table"})

        table = None
        for t in tables:
            table_title = t.find("div", {"class": "table-title"}).text
            if table_title.strip() == "Fotbal":
                table = t
                break

        if table is None:
            return

        for event_html in table.findAll("div", {"class": "table-row"}):
            try:
                nume = event_html.find("span", {"class": "match-title-text"})
                cote = event_html.findAll("span", {"class": "value"})

                [nume1, nume2] = nume.text.split(" - ")
                [cota1, cotax, cota2] = [float(x.text.strip()) for x in cote]
                
                event = FootballEvent(self.sitename, nume1, nume2, cota1, cotax, cota2)

                self.add_if_not_included_football(event)
            #da ValueError daca sunt pariurile blocate
            except ValueError as e:
                continue