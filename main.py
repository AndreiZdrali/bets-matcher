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
from scrappers.vulkanbet import VulkanBet, VulkanBetLive
from scrappers.maxbet import Maxbet, MaxbetLive
from sites import BetTypes, SiteNames, SiteType
from matcher import Matcher
from exchange_matcher import ExchangeMatcher
import threading, settings, utils, time, os

BG_RUNNING = False #DE SCAPAT

#CHESTII CA SA ARATE RESTUL INGRIJIT
class _Website:
    def __init__(self, scrapper, sitename, sitetype, has_prematch, has_live, live_scrapper = None):
        self.scrapper = scrapper
        self.sitename = sitename
        self.sitetype = sitetype
        self.has_prematch = has_prematch
        self.has_live = has_live
        self.live_scrapper = live_scrapper

def _get_bookie_list():
    bookies = []
    bookies.append(_Website(Superbet, SiteNames.SUPERBET, SiteType.BOOKIE, True, False))
    bookies.append(_Website(Efbet, SiteNames.EFBET, SiteType.BOOKIE, True, False))
    bookies.append(_Website(CasaPariurilor, SiteNames.CASAPARIURILOR, SiteType.BOOKIE, True, False))
    bookies.append(_Website(Stanleybet, SiteNames.STANLEYBET, SiteType.BOOKIE, False, False))
    bookies.append(_Website(PlayOnline, SiteNames.PLAYONLINE, SiteType.BOOKIE, True, True, PlayOnlineLive))
    bookies.append(_Website(VulkanBet, SiteNames.VULKANBET, SiteType.BOOKIE, False, True, VulkanBetLive))
    bookies.append(_Website(Maxbet, SiteNames.MAXBET, SiteType.BOOKIE, False, True, MaxbetLive))
    return bookies

def _get_exchange_list():
    exchanges = []
    exchanges.append(_Website(Purebet, SiteNames.PUREBET, SiteType.EXCHANGE, True, False))
    exchanges.append(_Website(Betfair, SiteNames.BETFAIR, SiteType.EXCHANGE, True, True, BetfairLive))
    return exchanges
#GATA

BOOKIE_LIST = _get_bookie_list()
EXCHANGE_LIST = _get_exchange_list()

def get_scrappers(live):
    bookie_text, exchange_text = settings.SETTINGS["bookie"], settings.SETTINGS["exchange"]
    
    bookie = list(filter(lambda x: x.sitename.strip().lower() == bookie_text.strip().lower(), BOOKIE_LIST))
    if len(bookie) == 0:
        print(f"Invalid '{bookie_text}' bookie. Use 'set bookie [bookie]' to select the bookie. Use 'help' to see all available bookies.")
        return None
    
    exchange = list(filter(lambda x: x.sitename.strip().lower() == exchange_text.strip().lower(), EXCHANGE_LIST))
    if len(exchange) == 0:
        print(f"Invalid '{exchange_text}' bookie. Use 'set exchange [exchange]' to select the bookie. Use 'help' to see all available exchanges.")
        return None
    
    bookie, exchange = bookie[0], exchange[0]
    bookie_scrapper, exchange_scrapper = bookie.scrapper, exchange.scrapper
    
    if settings.SETTINGS["day"] == -1:
        if not bookie.has_live:
            print(f"Bookie '{bookie.sitename}' does not support live.")
            return None
        bookie_scrapper = bookie.live_scrapper
        if not exchange.has_live:
            print(f"Exchange '{exchange.sitename}' does not support live.")
            return None
        exchange_scrapper = exchange.live_scrapper
    else:
        if not bookie.has_prematch:
            print(f"Bookie '{bookie.sitename}' does not support prematch.")
            return None
        if not exchange.has_prematch:
            print(f"Exchange '{exchange.sitename}' does not support prematch.")
            return None
    
    return (bookie_scrapper, exchange_scrapper)

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

def handle_help_command(args=None):
    if args == "commands":
        print("exit")
        print("run")
        print("bgrun")
        print("settings")
        print("bookie")
        print("exchange")
        print("set")
        print("exit")
        print("jlkfsadjflksajflksadjfsa")
    elif args == "sites":
        print(f"Available bookies: {', '.join([x.sitename for x in BOOKIE_LIST])}")
        print(f"Available exchanges: {', '.join([x.sitename for x in EXCHANGE_LIST])}")
    else:
        print("Use 'help [commands/sites]' for more information.")

def handle_home_command(driver_bookie, driver_exchange):
    driver_bookie.get("https://www.google.com")
    driver_exchange.get("https://www.google.com")

def handle_clear_command():
    os.system("cls" if os.name == "nt" else "clear")

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

def handle_run_command(driver_bookie, driver_exchange, bookie, exchange, sport_type, day):
    result_dict = {} #ca sa iau val din thread-uri
    #sitename e doar ca sa caute in dictionar, nu are defapt legatura cu numele
    scrapper_bookie, sitename_bookie = bookie, SiteType.BOOKIE
    scrapper_exchange, sitename_exchange = exchange, SiteType.EXCHANGE

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

    bookiedriver = webdriver.Chrome(service=settings.SELENIUM_SERVICE, options=settings.SELENIUM_OPTIONS)
    exchangedriver = webdriver.Chrome(service=settings.SELENIUM_SERVICE, options=settings.SELENIUM_OPTIONS)

    bookiedriver.minimize_window()
    exchangedriver.minimize_window()

    threads = []

    while True:
        user_input = input(">>> ")

        if user_input == "exit":
            break

        elif user_input.split()[0] == "help":
            _, *args = user_input.split()
            if len(args) > 1:
                print("Invalid 'help' format.")
                continue
            handle_help_command(args[0] if args else None)

        elif user_input == "home":
            handle_home_command(bookiedriver, exchangedriver)

        elif user_input == "cls" or  user_input == "clear":
            handle_clear_command()

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

            scrappers = get_scrappers(settings.SETTINGS["day"])
            if not scrappers:
                continue #get_scrappers da si print la problema, aici continue si atat
            bookie, exchange = scrappers[0], scrappers[1]
            
            matcher = handle_run_command(bookiedriver, exchangedriver, bookie, exchange, settings.SETTINGS["sport"], settings.SETTINGS["day"])
            for e in matcher.all_pairs:
                if utils.check_event_odds_bounds(e, settings.SETTINGS["min_odds"], settings.SETTINGS["max_odds"]):
                    print_event(e)

            if settings.SETTINGS["autoclear"]:
                handle_clear_command()

            if settings.SETTINGS["autohome"]:
                handle_home_command(bookiedriver, exchangedriver)
            
        elif user_input.split()[0] == "bgrun":
            print("Inca nu e gata, calmeaza-te")
            continue

            _, *args = user_input.split()
            if len(args) != 1:
                print("Invalid 'bgrun' format. Usage: bgrun [start/stop].")
            else:
                handle_bgrun_command(args[0], threads)
            
        else:
            print(f"Invalid '{user_input.split()[0]}' command. Use 'help' to see all commands.")

    exit(0)

if __name__ == "__main__":
    main()