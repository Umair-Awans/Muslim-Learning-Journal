import json
from core_utils import DateManager, Utilities

class FileManager:
    @staticmethod
    def load_file(file_path_json: str) -> dict:
        try:
            with open(file_path_json, 'r', encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @staticmethod
    def save_to_md(dict_entries: dict, file_path_md: str) -> bool:
        """
        Save learning entries to a Markdown file with formatted sections for Qur'an and other subjects.

        Args:
            dict_entries (dict): Dictionary containing learning entries data
            file_path_md (str): string containing MD file path 
        """        
        try:
            with open(file_path_md, 'w', encoding="utf-8") as file:
                if not dict_entries:
                    file.write("")
                else:
                    for date, record in dict_entries.items():
                        file.write(f"# {date}\n\n")
                        for subject, books in record.items():
                            file.write(f"## {subject}\n\n")
                            for book_name, sessions in books.items():                                    
                                file.write(f"### {book_name}\n")
                                for session, session_details in sessions.items():
                                    file.write(f"\n#### {session}\n\n")
                                    for key, value in session_details.items():
                                        file.write(f"- **{key}:** {value}\n")
                                file.write("\n")

                        # Add daily summary if needed
                        file.write("---\n\n")  # Horizontal rule for separation between dates
            return True
        except Exception:
            return False

    @staticmethod
    def save_to_json(dict_: dict, file_path_json: str) -> bool:
        try:
            with open(file_path_json, 'w', encoding="utf-8") as file:
                json.dump(dict_, file, indent=4, ensure_ascii=False)
            return True
        except Exception:
            return False


class DataManager:
    def __init__(self) -> None:
        self.__FILE_JSON = "./data/learning_data.json"
        self.FILE_MD = "./data/Journal.md"
        self.data = FileManager.load_file(self.__FILE_JSON)
        self.entry_log = self.data.get("Entry Log", {})
        self.all_time_subjects = self.data.get("All Time Subjects", {})
        self.stats = self.data.get("Statistics", {})
        self.sync_data_today()       

    @property
    def file_dict(self) -> dict:
        return {
                    "Entry Log": self.entry_log,
                    "All Time Subjects": self.all_time_subjects,
                    "Statistics": self.stats
                }

    def update_date_today(self):
        self.date_today = DateManager.get_date_today()

    def sync_data_today(self):
        self.update_date_today()
        self.progress_today = self.entry_log.get(self.date_today, {})

    def add_entry(self, subject: str, book_name: str, entry_dict: dict) -> None:
        self.sync_data_today()
        entry = f"Entry {DateManager.get_current_time()}"
        self.progress_today.setdefault(subject, {}).setdefault(book_name, {})
        self.progress_today[subject][book_name][entry] = entry_dict
        self.add_to_cache(subject, book_name)
        self.add_stats(subject, book_name, entry_dict)
        self.update_entry_log("", {})

    def add_to_cache(self, subject, book_name):
        if subject in ["Al-Qur'an (Tafseer)", "Al-Qur'an (Tilawat)"]:
            return
        self.all_time_subjects.setdefault(subject, [])
        self.all_time_subjects = Utilities.dict_sort(self.all_time_subjects)
        if book_name not in self.all_time_subjects[subject]:
            self.all_time_subjects[subject].append(book_name)
            self.all_time_subjects[subject].sort()

    def add_stats(self, subject, book_name, entry_dict: dict):
        Utilities.set_defaults_for_stats(self.stats, subject, book_name)
        self.stats = Utilities.dict_sort(self.stats)
        self.stats[subject] = Utilities.dict_sort(self.stats[subject])

        if self.date_today not in self.stats[subject][book_name]["Entry Dates"]:
            self.stats[subject][book_name]["Entry Dates"].append(self.date_today)
            
        self.stats[subject][book_name]["Pages"] += entry_dict["Total Pages"]

        all_time_minutes = Utilities.convert_time_to_mins(self.stats[subject][book_name]["Time Spent"])
        entry_minutes = Utilities.convert_time_to_mins(entry_dict["Time Spent"])
        self.stats[subject][book_name]["Time Spent"] = Utilities.format_time(all_time_minutes + entry_minutes)


    def update_cache(self, cache: dict) -> None:
        self.all_time_subjects = cache
        
    def update_stats(self, stats: dict) -> None:
        self.stats = stats

    def update_entry_log(self, date: str, entries: dict) -> None:
        date = date or self.date_today
        entries = entries or self.progress_today
        if entries:
            self.entry_log[date] = entries
        elif date in self.entry_log and not self.entry_log[date]:
            self.entry_log.pop(date)

    def get_entries_from_date(self, date: str):
        return self.entry_log.get(date, {})

    def delete_stats(self, day: str):
        from progress_tools import ProgressEditor
        for subject, subject_entries in self.entry_log[day].items():
            for book, book_entries in subject_entries.items():
                if day in self.stats[subject][book]["Entry Dates"]:
                    self.stats[subject][book]["Entry Dates"].remove(day)
                    for entry_details in book_entries.values():
                        ProgressEditor.update_entry_pages((subject, book), entry_details["Total Pages"], self.stats)
                        ProgressEditor.update_entry_minutes((subject, book), entry_details["Time Spent"], self.stats)
                    
    def delete_progress(self, date: str = "None", delete_all: bool = False):
        if delete_all:
            self.entry_log.clear()
            self.stats.clear()
            return True, "All data deleted successfully!"
        elif date in self.entry_log:
            self.delete_stats(date)
            self.entry_log.pop(date)
            return True, f"All entries from {date if date != DateManager.get_date_today() else f'today ({date})'} deleted successfully!"
        return False, f"No entries recorded for {date if date != DateManager.get_date_today() else f'today ({date})'}."
        

    def save_progress_to_files(self):
        if not FileManager.save_to_json(self.file_dict, self.__FILE_JSON):
            return 1
        if not FileManager.save_to_md(self.entry_log, self.FILE_MD):
            return 2
        return 0

