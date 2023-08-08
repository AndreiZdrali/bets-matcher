from events import TennisEvent, FootballEvent
from selenium import webdriver

class ScrapperBase:
    def __init__(self, driver=None):
        self.driver: webdriver.Chrome = driver
        self.tennis_events: list[TennisEvent] = []
        self.football_events: list[FootballEvent] = []

    @staticmethod
    def _get_element(node):
        length = len(list(node.previous_siblings)) + 1
        if (length) > 1:
            return '%s:nth-child(%s)' % (node.name, length)
        else:
            return node.name

    @staticmethod
    def _get_css_path(node):
        path = [ScrapperBase._get_element(node)]
        for parent in node.parents:
            if parent.name == 'body':
                break
            path.insert(0, ScrapperBase._get_element(parent))

        return ' > '.join(path)
    
    #DOAR PT SITE-URILE CU API
    def add_tennis(self, event):
        self.tennis_events.append(event)

    #DOAR PT SITE-URILE CU API
    def add_football(self, event):
        self.football_events.append(event)

    def not_included_tennis(self, event):
        for e in self.tennis_events:
            if e.get_hash() == event.get_hash():
                return False
        return True

    def add_if_not_included_tennis(self, event):
        if self.not_included_tennis(event):
            self.tennis_events.append(event)

    def not_included_football(self, event):
        for e in self.football_events:
            if e.get_hash() == event.get_hash():
                return False
        return True

    def add_if_not_included_football(self, event):
        if self.not_included_football(event):
            self.football_events.append(event)

    def get_all_tennis_events(self, days=0):
        raise NotImplementedError

    def get_all_football_events(self, days=0):
        raise NotImplementedError
