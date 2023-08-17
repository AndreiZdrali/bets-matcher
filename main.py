from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from scrappers.scrapper import ScrapperBase
from scrappers.purebet import Purebet
from scrappers.betfair import Betfair, BetfairLive
from scrappers.superbet import Superbet
from scrappers.efbet import Efbet
from scrappers.casapariurilor import CasaPariurilor
from scrappers.stanleybet import Stanleybet
from scrappers.playonline import PlayOnline, PlayOnlineLive
from sites import BetTypes, SiteNames
from matcher import Matcher
from exchange_matcher import ExchangeMatcher
import threading, settings, utils, time

BG_RUNNING = False #DE SCAPAT

def get_site_events(result_dict, driver, site: ScrapperBase, sitename, sports, day):
    scrapper = site(driver)
    if 'f' in sports:
        if day == -1:
            scrapper.get_all_football_events() #daca e live nu are day
        else:
            scrapper.get_all_football_events(day)
    if 't' in sports:
        if day == -1:
            scrapper.get_all_tennis_events()
        else:
            scrapper.get_all_tennis_events(day)
    result_dict[sitename] = scrapper

def print_event(e):
    if not settings.SETTINGS["compact_output"]:
        print(e)
        print("==============")
    else:
        print(e.short_str())
        print("============================")

def handle_help_command():
    print("help")
    print("run")
    print("bgrun")
    print("settings")
    print("set")
    print("exit")
    print("jlkfsadjflksajflksadjfsa")

def handle_home_command(driver_bookie, driver_exchange):
    driver_bookie.get("https://www.google.com")
    driver_exchange.get("https://www.google.com")

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

def handle_run_command(driver_bookie, driver_exchange, sport_type, day):
    result_dict = {} #ca sa iau val din thread-uri
    scrapper_bookie, sitename_bookie = PlayOnlineLive, SiteNames.PLAYONLINELIVE
    scrapper_exchange, sitename_exchange = BetfairLive, SiteNames.BETFAIRLIVE

    if day != -1:
        scrapper_bookie, sitename_bookie = PlayOnline, SiteNames.PLAYONLINE
        scrapper_exchange, sitename_exchange = Betfair, SiteNames.BETFAIR

    thread_bookie = threading.Thread(target=get_site_events, args=[result_dict, driver_bookie, scrapper_bookie, sitename_bookie, sport_type, day])
    thread_exchange = threading.Thread(target=get_site_events, args=[result_dict, driver_exchange, scrapper_exchange, sitename_exchange, sport_type, day])

    thread_bookie.start()
    thread_exchange.start()
    thread_bookie.join()
    thread_exchange.join()

    bookie = result_dict[sitename_bookie]
    exchange = result_dict[sitename_exchange]

    matcher = ExchangeMatcher(bookie, exchange)
    matcher.match_football_events()
    matcher.match_tennis_events()
    matcher.sort_all_events_by_roi()

    return matcher

#IN LUCRU ===========
def handle_bgrun_command(command, threads): #TODO: multiprocessing in loc de threading
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
#IN LUCRU ===========

def main():
    settings.load_settings() #incarca in SETTINGS din settings.py

    betfairlivedriver = webdriver.Chrome(service=settings.SELENIUM_SERVICE, options=settings.SELENIUM_OPTIONS)
    playonlinelivedriver = webdriver.Chrome(service=settings.SELENIUM_SERVICE, options=settings.SELENIUM_OPTIONS)

    threads = []

    while True:
        user_input = input(">>> ")

        if user_input == "exit":
            break

        elif user_input == "help":
            handle_help_command()

        elif user_input == "home":
            handle_home_command(betfairlivedriver, playonlinelivedriver)

        elif user_input.split()[0] == "set":
            _, *args = user_input.split()
            if len(args) != 2:
                print("Invalid 'set' format. Usage: set [setting_name] [value].")
            else:
                handle_set_command(args[0], args[1])

        elif user_input == "settings":
            handle_settings_command()

        elif user_input == "run":
            if len(list(filter(lambda x: x in settings.SETTINGS["sport"], ['f', 't']))) == 0: #cam complex si degeaba
                print(f"No sports selected. Use 'set sport [f/t/ft]' to select the sports.")
                continue

            matcher = handle_run_command(playonlinelivedriver, betfairlivedriver, settings.SETTINGS["sport"], settings.SETTINGS["day"])
            for e in matcher.all_pairs:
                if utils.check_event_odds_bounds(e, settings.SETTINGS["min_odds"], settings.SETTINGS["max_odds"]):
                    print_event(e)

            if settings.SETTINGS["autohome"]:
                handle_home_command(betfairlivedriver, playonlinelivedriver)
            
        elif user_input.split()[0] == "bgrun":
            print("Inca nu e gata, calmeaza-te")
            continue

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