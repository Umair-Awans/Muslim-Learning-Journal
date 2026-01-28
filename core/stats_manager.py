from core.data_manager import DataManager
from core.core_services import DateManager, CoreHelpers


class StatsAggregator:
    def __init__(self, data_manager: DataManager) -> None:
        self.data = data_manager
        self.stats_today = None

    def calculate_stats_today(self):
        today = DateManager.get_date_today()
        if today in self.data.entry_log:
            self.stats_today = self.get_entries_mins_pages(today)
        else:
            self.stats_today = (0, 0, 0)

    def calculate_all_time_stats(self):
        all_time_stats = {}
        for date, progress_date in self.data.entry_log.items():
            for subject, progress_subject in progress_date.items():
                for book, progress_book in progress_subject.items():
                    CoreHelpers.set_defaults_for_stats(all_time_stats, subject, book)    
                    all_time_stats[subject][book].setdefault("Minutes", 0)
                    all_time_stats[subject][book]["Total Entries"] += len(progress_book)
                    all_time_stats[subject][book]["Entry Dates"].append(date)
                    for _, progress_entry in progress_book.items():
                        all_time_stats[subject][book]["Minutes"] += CoreHelpers.convert_time_to_mins(progress_entry["Time Spent"])
                        all_time_stats[subject][book]["Pages"] += progress_entry["Total Pages"]
        all_time_stats = CoreHelpers.dict_sort(all_time_stats)
        for subject, dict_subject in all_time_stats.items():
            all_time_stats[subject] = CoreHelpers.dict_sort(all_time_stats[subject])
            for book, dict_book in all_time_stats[subject].items():
                dict_book["Time Spent"] = CoreHelpers.format_time(dict_book["Minutes"])
                dict_book.pop("Minutes")
        self.data.update_stats(all_time_stats)

    def get_entries_mins_pages(self, date: str):
        total_minutes = 0
        total_pages = 0
        total_entries = 0
        for subject, dict_subject in self.data.entry_log[date].items():
            for book, book_entry in dict_subject.items():
                total_entries += len(book_entry)
                for session, session_entry in book_entry.items():
                    time_spent, entry_pages = session_entry["Time Spent"], session_entry["Total Pages"]
                    total_minutes += CoreHelpers.convert_time_to_mins(time_spent)
                    total_pages += entry_pages
        return (total_entries, total_minutes, total_pages)


class StatsUpdater:
    def __init__(self, data_manager: DataManager) -> None:
        self.data = data_manager

    def add_stats(self, entry):
        subject = entry.subject
        book = entry.book
        entry_dict = entry.to_dict()
        CoreHelpers.set_defaults_for_stats(self.data.stats, subject, book)
        self.data.stats = CoreHelpers.dict_sort(self.data.stats)
        self.data.stats[subject] = CoreHelpers.dict_sort(self.data.stats[subject])

        self.data.stats[subject][book]["Total Entries"] += 1

        if self.data.date_today not in self.data.stats[subject][book]["Entry Dates"]:
            self.data.stats[subject][book]["Entry Dates"].append(self.data.date_today)
            
        self.data.stats[subject][book]["Pages"] += entry_dict["Total Pages"]

        all_time_minutes = CoreHelpers.convert_time_to_mins(self.data.stats[subject][book]["Time Spent"])
        entry_minutes = CoreHelpers.convert_time_to_mins(entry_dict["Time Spent"])
        self.data.stats[subject][book]["Time Spent"] = CoreHelpers.format_time(all_time_minutes + entry_minutes)

    def update_entry_pages(self, details, entry_pages, add = False):
        if add:
            self.data.stats[details[0]][details[1]]["Pages"] += entry_pages
        else:
            self.data.stats[details[0]][details[1]]["Pages"] -= entry_pages

    def update_entry_minutes(self, details, entry_time_spent, add = False):
        temp_total_minutes = CoreHelpers.convert_time_to_mins(self.data.stats[details[0]][details[1]]["Time Spent"])
        if add:
            temp_total_minutes += CoreHelpers.convert_time_to_mins(entry_time_spent)
        else:
            temp_total_minutes -= CoreHelpers.convert_time_to_mins(entry_time_spent)
        self.data.stats[details[0]][details[1]]["Time Spent"] = CoreHelpers.format_time(temp_total_minutes)

    def update_stats(self, details: tuple, values: tuple, field: str="", date: str=""):
        """ details contains: subject and book
            if field: (used while editing)
                values contains: old and New values
            else: (used while deleting)
                values contains: old values for (pages, time_spent)"""

        if field == "Page":
            self.update_entry_pages(details, values[0]) # Removes old Values
            self.update_entry_pages(details, values[1], add=True) # Adds new Values
        elif field == "Time Spent":
            self.update_entry_minutes(details, values[0])
            self.update_entry_minutes(details, values[1], add=True)
        else: # No field arg means entry has been deleted
            self.update_entry_pages(details, values[0])
            self.update_entry_minutes(details, values[1])
            self.data.stats[details[0]][details[1]]["Total Entries"] -= 1
            if len(self.data.entry_log[date][details[0]][details[1]]) <= 1:
                self.data.stats[details[0]][details[1]]["Entry Dates"].remove(date)

    def delete_stats(self, day: str):
        for subject, subject_entries in self.data.entry_log[day].items():
            for book, book_entries in subject_entries.items():
                if day in self.data.stats[subject][book]["Entry Dates"]:
                    self.data.stats[subject][book]["Entry Dates"].remove(day)
                    self.data.stats[subject][book]["Total Entries"] -= len(book_entries)
                    for entry_details in book_entries.values():
                        self.update_entry_pages(self.data.stats, (subject, book), entry_details["Total Pages"])
                        self.update_entry_minutes(self.data.stats, (subject, book), entry_details["Time Spent"])
    
    def change_subject(self, book: str, old_subject: str, new_subject: str):
        """This method can be used to change the subject of a book"""

        for date, progress_date in self.data.entry_log.items():

            if old_subject not in progress_date:
                continue
            if book not in progress_date[old_subject]:
                continue

            progress_date.setdefault(new_subject, {})
            progress_date[new_subject][book] = progress_date[old_subject][book]
            progress_date[old_subject].pop(book)

            if not progress_date[old_subject]:
                progress_date.pop(old_subject)


class WeeklyStatsService:
    def __init__(self, stats_manager) -> None:
        self.stats = stats_manager
        self.data = self.stats.data
        self.weekly_report = {}
        self.weekly_entries_made = []
        self.weekly_minutes_spent = []
        self.weekly_pages_read = []
        self.weekly_total_minutes = 0
        self.weekly_total_time = 0

    def compute_weekly_stats(self):
        if not self.weekly_report:
            self.generate_weekly_report()
        self.weekly_dates = list(self.weekly_report.keys())
        progress = list(self.weekly_report.values())

        self.weekly_entries_made = [x for x, y, z in progress]
        self.weekly_minutes_spent = [y for x, y, z in progress]
        self.weekly_pages_read = [z for x, y, z in progress]
        self.weekly_total_minutes = sum(self.weekly_minutes_spent)        
        self.weekly_total_time = CoreHelpers.format_time(self.weekly_total_minutes)

    def get_weekly_summary(self) -> str:
        if not self.weekly_report:
            self.compute_weekly_stats()

        prompts = [
            f"\nYou spent a total of {self.weekly_total_time} on learning activities during the previous week (excluding today).\n",
            "\nNo learning activity was recorded during the previous week (excluding today).\n"
        ]
        index = 0 if self.weekly_total_minutes > 0 else 1
        return prompts[index]

    def generate_weekly_report(self):
        for date in DateManager.get_last_seven_days():
            if date in self.data.entry_log:
                self.weekly_report[date] = self.stats.aggregator.get_entries_mins_pages(date)
            else:
                self.weekly_report[date] = (0, 0, 0)
    

class CacheBuilder:
    def __init__(self, data_manager: DataManager) -> None:
        self.data = data_manager

    def update_on_entry(self, subject, book_name):
        if subject in ["Al-Qur'an (Tafseer)", "Al-Qur'an (Tilawat)"]:
            return
        self.data.all_time_subjects.setdefault(subject, [])
        self.data.all_time_subjects = CoreHelpers.dict_sort(self.data.all_time_subjects)
        if book_name not in self.data.all_time_subjects[subject]:
            self.data.all_time_subjects[subject].append(book_name)
            self.data.all_time_subjects[subject].sort()

    def build_subjects_cache(self) -> None:
        all_time_subjects = {}
        for data_one_day in self.data.entry_log.values():
            self.extract_subjects(data_one_day, all_time_subjects)
        self.extract_subjects(self.data.progress_today, all_time_subjects)
        all_time_subjects = CoreHelpers.dict_sort(all_time_subjects)
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


class StatsPlotter:
    def __init__(self, stats_manager) -> None:
        self.stats = stats_manager
        
    def display_plot_weekly(self):
        if not self.stats.weekly_stats.weekly_report:
            self.stats.weekly_stats.compute_weekly_stats()
        import matplotlib.pyplot as plt
        title = "Weekly Report"
        plt.style.use('seaborn')
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(self.stats.weekly_stats.weekly_dates, self.stats.weekly_stats.weekly_minutes_spent, linewidth=3, marker='o', label='Minutes Spent')
        ax.plot(self.stats.weekly_stats.weekly_dates, self.stats.weekly_stats.weekly_pages_read, linewidth=3, marker='o', label='Pages Read')
        ax.legend()
        ax.set_title(f"{title} (Total Time: {self.stats.weekly_stats.weekly_total_time})", fontsize=15)
        ax.set_xlabel("Date", fontsize=14)
        ax.set_ylabel("Minutes / Pages", fontsize=14)
        ax.tick_params(axis='both', labelsize=10)
        fig.autofmt_xdate()
        
        plt.tight_layout()
        plt.show(block=False)
        plt.pause(0.001)


class StatsManager:
    def __init__(self, data_manager: DataManager):
        self.data = data_manager
        self.updater = StatsUpdater(data_manager)
        self.aggregator = StatsAggregator(data_manager)
        self.cache_builder = CacheBuilder(data_manager)
        self.weekly_stats = WeeklyStatsService(self)
        self.plotter = StatsPlotter(self)

    def on_entry_added(self, entry):
        self.updater.add_stats(entry)
        self.cache_builder.update_on_entry(entry.subject, entry.book)