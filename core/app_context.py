import os, pathlib
from core.data_manager import DataManager
from core.stats_manager import StatsManager
from core.core_services import PasswordManager


class AppContext:
    def __init__(self):
        self.app_name = "Muslim Learning Journal"
        self.version = "Version: 1.0"
        
        self.path_password_file = './data/password.txt'
        self.path_json = "./data/learning_data.json"
        self.path_md = "./data/Journal.md"


        self.data_manager = DataManager(self.path_json, self.path_md)
        self.stats_manager = StatsManager(self.data_manager)
        self.password_manager = PasswordManager(self.path_password_file)
        self.unsaved_entries = {}

        self.stats_manager.cache_builder.build_subjects_cache()
        self.stats_manager.aggregator.calculate_all_time_stats()
    
    def add_entry_to_log(self, entry):
        self.data_manager.add_entry(entry)
        self.stats_manager.on_entry_added(entry)
        count = 1
        key = f"{entry.subject}\n{entry.book}\nEntry no.{count}"
        while key in self.unsaved_entries:
            count += 1 
            key = f"{entry.subject}\n{entry.book}\nEntry no.{count}"
        self.unsaved_entries[key] = entry

    def save_progress_to_files(self):
        return_code = self.data_manager.save_data_to_files()
        if return_code == 0:
            self.clear_unsaved_entries()
        return return_code    

    def clear_unsaved_entries(self):
        self.unsaved_entries.clear()
    
    def about(self) -> str:
        return (
        f"{self.app_name}\n"
        f"{self.version}\n\n"
        "A simple journal to track Qur'an and other learning activities.\n"
        "Created to help maintain consistency and motivation."
    )

    def open_journal(self):
        path = pathlib.Path(self.path_md)
        if not path.exists():
            raise FileNotFoundError("Journal file not found")
        os.startfile(path)

    def change_path_md(self, file_path):
        self.path_md = file_path
        return self.data_manager.save_md_as(file_path)