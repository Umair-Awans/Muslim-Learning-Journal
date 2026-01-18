from core.data_manager import DataManager
from core.stats_manager import StatsManager


class AppContext:
    def __init__(self):
        self.data_manager = DataManager()
        self.stats_manager = StatsManager(self.data_manager)
