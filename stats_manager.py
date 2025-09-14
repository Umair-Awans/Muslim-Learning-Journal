from datetime import datetime
from entries import TafseerEntry, TilawatEntry, OtherEntry
from file_manager import DataManager
from core_utils import DateManager, Utilities


class StatsManager:
    def __init__(self, data: DataManager):
        self.data = data
        self.weekly_report = {}

    def compute_weekly_stats(self):
        if not self.weekly_report:
            self.generate_weekly_report()
        self.weekly_dates = list(self.weekly_report.keys())
        progress = list(self.weekly_report.values())

        self.weekly_minutes_spent = [x for x, y in progress]
        self.weekly_pages_read = [y for x, y in progress]
        self.weekly_total_minutes = sum(self.weekly_minutes_spent)        
        self.weekly_total_time = Utilities.format_time(self.weekly_total_minutes)

    def get_weekly_summary(self) -> str:
        if not hasattr(self, "weekly_total_time"):
            self.compute_weekly_stats()

        title = "\n-------------( Weekly Report )-------------\n"
        prompts = [
            f"\nYou spent a total of {self.weekly_total_time} on learning activities during the previous week (excluding today).\n",
            "\nNo learning activity was recorded during the previous week (excluding today).\n"
        ]
        index = 0 if self.weekly_total_minutes > 0 else 1
        return title + prompts[index]

    def generate_weekly_report(self):
        for date in DateManager.get_last_seven_days():
            total_pages = 0
            total_minutes = 0
            if date in self.data.entry_log:
                for subject, dict_subject in self.data.entry_log[date].items():
                    for book, book_entry in dict_subject.items():
                        for session, session_entry in book_entry.items():
                            time_spent, entry_pages = self.extract_time_spent(subject, book, session_entry)
                            total_minutes += Utilities.convert_time_to_mins(time_spent)
                            total_pages += entry_pages
            self.weekly_report[date] = (total_minutes, total_pages)

    @staticmethod
    def extract_time_spent(subject, book, session_entry):
        map_dict = {
            "Al-Qur'an (Tafseer)": TafseerEntry.from_dict,
            "Al-Qur'an (Tilawat)": TilawatEntry.from_dict
        }
        if subject in map_dict:
            entry = map_dict[subject](subject, session_entry)
        else:
            entry = OtherEntry.from_dict(book, session_entry)
        return entry.time_spent, entry.total_pages

    def build_subjects_cache(self) -> None:
        all_time_subjects = {}
        for data_one_day in self.data.entry_log.values():
            self.extract_subjects(data_one_day, all_time_subjects)
        self.extract_subjects(self.data.progress_today, all_time_subjects)
        all_time_subjects = Utilities.dict_sort(all_time_subjects)
        self.data.update_cache(all_time_subjects)

    @staticmethod
    def extract_subjects(data_one_day: dict, all_time_subjects: dict) -> None:
        for subject, subject_data in data_one_day.items():
            if subject in ["Al-Qur'an (Tilawat)", "Al-Qur'an (Tafseer)"]:
                continue
            all_time_subjects.setdefault(subject, [])
            for book in subject_data:
                if book not in all_time_subjects[subject]:
                    all_time_subjects[subject].append(book)
            all_time_subjects[subject].sort()        

    def calculate_stats(self):
        all_time_stats = {}
        for date, progress_date in self.data.entry_log.items():
            for subject, progress_subject in progress_date.items():
                for book, progress_book in progress_subject.items():
                    Utilities.set_defaults_for_stats(all_time_stats, subject, book)    
                    all_time_stats[subject][book].setdefault("Minutes", 0)
                    all_time_stats[subject][book]["Entry Dates"].append(date)
                    for _, progress_entry in progress_book.items():
                        all_time_stats[subject][book]["Minutes"] += Utilities.convert_time_to_mins(progress_entry["Time Spent"])
                        all_time_stats[subject][book]["Pages"] += progress_entry["Total Pages"]
        all_time_stats = Utilities.dict_sort(all_time_stats)
        for subject, dict_subject in all_time_stats.items():
            all_time_stats[subject] = Utilities.dict_sort(all_time_stats[subject])
            for book, dict_book in all_time_stats[subject].items():
                dict_book["Time Spent"] = Utilities.format_time(dict_book["Minutes"])
                dict_book.pop("Minutes")
        self.data.update_stats(all_time_stats)

