import datetime

class SiteNames:
    PUREBET = "Purebet"
    BETFAIRLIVE = "Betfair Live"
    SUPERBET = "Superbet"
    EFBET = "Efbet"
    CASAPARIURILOR = "Casa Pariurilor"
    STANLEYBET = "Stanleybet"
    MRBIT = "Mr Bit"
    UNIBET = "Unibet"
    PLAYONLINELIVE = "Play Online Live"

#EFBET, STANLEY, MRBIT mai intai intra pe site si dupa merge la categoria lui

class SiteTennisURLs:
    PUREBET = "https://api.purebet.io/pbapi?sport=tennis"
    SUPERBET = "https://superbet.ro/pariuri-sportive/tenis"
    EFBET = "https://www.efbet.ro"
    CASAPARIURILOR = "https://www.casapariurilor.ro/pariuri-online/tenis"
    STANLEYBET = "https://www.stanleybet.ro/pariuri-sportive"
    MRBIT = "https://mrbit.ro/en/betting"
    PLAYONLINELIVE = "https://online.excelbet.ro/pariuri/live"

class SiteFootballURLs:
    PUREBET = "https://api.purebet.io/pbapi?sport=soccer"
    BETFAIRLIVE = "https://www.betfair.ro/exchange/plus/ro/fotbal-pariuri-1"
    SUPERBET = "https://superbet.ro/pariuri-sportive/fotbal"
    EFBET = "https://www.efbet.ro"
    CASAPARIURILOR = "https://www.casapariurilor.ro/pariuri-online/fotbal"
    PLAYONLINELIVE = "https://online.excelbet.ro/pariuri/live"

class Days:
    GET_TODAY = lambda: datetime.date.today()
    GET_TOMORROW = lambda: datetime.date.today() + datetime.timedelta(days=1)

class Sports:
    FOOTBALL = "Football"
    TENNIS = "Tennis"

class BetTypes:
    BET_1 = "1"
    BET_X = "X"
    BET_2 = "2"
    BET_1X = "1X"
    BET_X2 = "X2"
    BET_12 = "12"
