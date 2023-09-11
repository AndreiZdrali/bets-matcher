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

class Stanleybet(ScrapperBase):
    def __init__(self, driver):
        super().__init__(driver)
        self.sitename = SiteNames.STANLEYBET

    def get_all_tennis_events(self):
        self.driver.get(SiteTennisURLs.STANLEYBET)

        time.sleep(5)

        tennis_xpath = "//i[@class='icon-sport-tennis']"
        WebDriverWait(self.driver, 200).until(EC.element_to_be_clickable((By.XPATH, tennis_xpath))).click()

        toate_xpath = "//*[@id=\"app\"]/div/div/div[1]/div[1]/div/div[1]/div[1]/div[1]/div/span"
        WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((By.XPATH, toate_xpath))).click()

        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "event-container")))
        time.sleep(2)

        bs = BeautifulSoup(self.driver.page_source, "html.parser")
        print(len(bs.findAll("div", {"class": "event-continer"})))