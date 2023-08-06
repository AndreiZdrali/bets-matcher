from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from scrappers.scrapper import ScrapperBase
from scrappers.purebet import Purebet
from scrappers.betfairlive import BetfairLive
from scrappers.superbet import Superbet
from scrappers.efbet import Efbet
from scrappers.casapariurilor import CasaPariurilor
from scrappers.stanleybet import Stanleybet
from scrappers.playonlinelive import PlayOnlineLive
from sites import BetTypes, SiteNames
from matcher import Matcher
from exchange_matcher import ExchangeMatcher
import threading, settings, utils, time

BG_RUNNING = False

def get_site_football_events(result_dict, driver, sitename, site: ScrapperBase):
    scrapper = site(driver)
    scrapper.get_all_football_events()
    result_dict[sitename] = scrapper

def handle_help_command():
    print("help")
    print("run")
    print("bgrun")
    print("settings")
    print("set")
    print("exit")
    print("jlkfsadjflksajflksadjfsa")

def handle_set_command(key, val):
    if key not in settings.SETTINGS:
        print(f"Invalid '{key}' key. Use 'settings' to see all avaiable settings.")
        return
    
    try:
        key_type = type(settings.SETTINGS[key])
        settings.SETTINGS[key] = key_type(val)
        settings.save_settings()
    except:
        print(f"Invalid value type. Key '{key}' is of type {key_type}.")

def handle_settings_command():
    print("{")
    for key in settings.SETTINGS:
        val = settings.SETTINGS[key]
        print(f"  '{key}': " + (f"'{val}'" if type(val) == str else f"{val}" ) + ",")
    print("}")

def handle_run_command(driver_bookie, driver_exchange):
    result_dict = {} #ca sa iau val din thread-uri
    thread_playonlinelive = threading.Thread(target=get_site_football_events, args=[result_dict, driver_bookie, SiteNames.PLAYONLINELIVE, PlayOnlineLive])
    thread_betfair = threading.Thread(target=get_site_football_events, args=[result_dict, driver_exchange, SiteNames.BETFAIRLIVE, BetfairLive])

    thread_playonlinelive.start()
    thread_betfair.start()
    thread_playonlinelive.join()
    thread_betfair.join()

    playonlinelive = result_dict[SiteNames.PLAYONLINELIVE]
    betfair = result_dict[SiteNames.BETFAIRLIVE]

    matcher = ExchangeMatcher(playonlinelive, betfair)
    matcher.match_football_events(roi_threshold=settings.SETTINGS["min_roi"])
    matcher.sort_football_games_by_roi()

    return matcher

def handle_bgrun_command(command, threads):
    global BG_RUNNING
    if command == "start":
        if len(threads) != 0:
            print(f"Already running in background. Use 'bgrun stop' to stop.")
        else:
            BG_RUNNING = True
            threads.append(threading.Thread(target=bgrun_thread))
            threads[0].start()
            time.sleep(2) #ca sa arate bine
            print(f"Running in background with refresh interval {settings.SETTINGS['bgrun_interval']} seconds.")

    elif command == "stop":
        if len(threads) == 0:
            print(f"Not running in background. Use 'bgrun start' to start.")
        else:
            BG_RUNNING = False
            threads[0].join()
            threads.clear()

def bgrun_thread():
    playonlinelivedriver = webdriver.Chrome(service=settings.SELENIUM_SERVICE, options=settings.SELENIUM_OPTIONS)
    betfairlivedriver = webdriver.Chrome(service=settings.SELENIUM_SERVICE, options=settings.SELENIUM_OPTIONS)

    while True:
        global BG_RUNNING
        if not BG_RUNNING:
            playonlinelivedriver.quit()
            betfairlivedriver.quit()
            break
        start_time = time.time()
        
        matcher = handle_run_command(playonlinelivedriver, betfairlivedriver)
        for e in matcher.football_pairs:
            if utils.check_event_odds_bounds(e, settings.SETTINGS["min_odds"], settings.SETTINGS["max_odds"]):
                pass
            
        while True:
            print("another one")
            time.sleep(1)
            if not BG_RUNNING:
                break
            current_time = time.time()
            elapsed_time = current_time - start_time
            if elapsed_time >= settings.SETTINGS["bgrun_interval"]:
                break

    print("Thread exited.")

def main():
    settings.load_settings("settings.json") #incarca in SETTINGS din settings.py

    betfairlivedriver = webdriver.Chrome(service=settings.SELENIUM_SERVICE, options=settings.SELENIUM_OPTIONS)
    playonlinelivedriver = webdriver.Chrome(service=settings.SELENIUM_SERVICE, options=settings.SELENIUM_OPTIONS)

    threads = []

    while True:
        user_input = input(">>> ")

        if user_input == "exit":
            break

        elif user_input.split()[0] == "set":
            _, *args = user_input.split()
            if len(args) != 2:
                print("Invalid 'set' format. Usage: set [setting_name] [value].")
            else:
                handle_set_command(args[0], args[1])

        elif user_input == "settings":
            handle_settings_command()

        elif user_input == "run":
            matcher = handle_run_command(playonlinelivedriver, betfairlivedriver)

            for e in matcher.football_pairs:
                if utils.check_event_odds_bounds(e, settings.SETTINGS["min_odds"], settings.SETTINGS["max_odds"]):
                    print(e)
                    print("==============")
            
        elif user_input.split()[0] == "bgrun":
            _, *args = user_input.split()
            if len(args) != 1:
                print("Invalid 'bgrun' format. Usage: bgrun [start/stop].")
            else:
                handle_bgrun_command(args[0], threads)
            

        else:
            print(f"Invalid {user_input.split()[0]} command. Use 'help' to see all commands.")

    exit(0)

if __name__ == "__main__":
    main()