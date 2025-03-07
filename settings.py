from selenium.webdriver.chrome.service import Service
from selenium import webdriver
import json, os

#aici ca sa fie accesbil mai lejer peste tot
SETTINGS = {

}

SELENIUM_SERVICE = Service(fr"{os.getcwd()}\chromedriver.exe")
SELENIUM_OPTIONS = webdriver.ChromeOptions()
_brave_path = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
if os.path.exists(_brave_path):
    SELENIUM_OPTIONS.binary_location = _brave_path

default_settings = {
    "stake_back": 100,
    "bookie": "PlayOnline",
    "exchange": "Betfair",
    "sport": "f",
    "day": -1, #-1 = live, 0 = today, 1 = tomorrow...
    "min_roi": -10,
    "max_roi": 1000000000,
    "min_odds": 1.7,
    "max_odds": 1000,
    "commission_back": 0.03,
    "commission_lay": 0.065,
    "bgrun_interval": 30,
    "compact_output": 1,
    "autohome": 1,
    "autoclear": 0
}

settings_file = "settings.json"

def load_settings(filename=settings_file):
    global SETTINGS
    try:
        with open(filename, "r") as file:
            SETTINGS = json.load(file)

            for key in default_settings:
                if key not in SETTINGS:
                    SETTINGS[key] = default_settings[key]

    except FileNotFoundError:
        print(f"Settings file '{filename}' not found. Using default settings.")
        SETTINGS = default_settings
    
    save_settings(filename)

def save_settings(filename=settings_file):
    global SETTINGS
    with open(filename, "w") as file:
        json.dump(SETTINGS, file, indent=2)