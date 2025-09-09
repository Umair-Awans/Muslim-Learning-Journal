from datetime import datetime
from entries import TafseerEntry, TilawatEntry, OtherEntry
from file_manager import DataManager
from core_utils import DateManager, Utilities


class StatsManager:
    weekly_report = {}

    @classmethod
    def display_stats(cls, data: DataManager):
        title = "Weekly Report"
        duration = "week"        
        if not cls.weekly_report:
            cls.generate_weekly_report(data)
        tuples = list(cls.weekly_report.values())
        minutes_spent = [x for x, y in tuples]
        total_minutes = sum(minutes_spent)
        
        total_time = Utilities.format_time(total_minutes)
        prompts = [
            f"\nYou spent a total of {total_time} on learning activities during the previous {duration} (excluding today).\n",
            f"\nNo learning activity was recorded during the previous {duration} (excluding today).\n"
        ]
        index = 0 if total_minutes > 0 else 1
        print(f"\n-------------( {title} )-------------\n")
        print(prompts[index])

    @classmethod
    def display_plot(cls, data: DataManager):
        title = "Weekly Report"
        if not cls.weekly_report:
            print("\nGenerating Weekly Report. Please wait.....")
            cls.generate_weekly_report(data)        
        print("\nLoading the plot. Please wait.....")
        import matplotlib.pyplot as plt
        dates = list(cls.weekly_report.keys())
        tuples = list(cls.weekly_report.values())
        minutes_spent = [x for x, y in tuples]
        pages_read = [y for x, y in tuples]
        total_minutes = sum(minutes_spent)        
        total_time = Utilities.format_time(total_minutes)
        plt.style.use('seaborn')
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(dates, minutes_spent, linewidth=3, marker='o', label='Minutes Spent')
        ax.plot(dates, pages_read, linewidth=3, marker='o', label='Pages Read')
        ax.legend()
        ax.set_title(f"{title} (Total Time: {total_time})", fontsize=15)
        ax.set_xlabel("Date", fontsize=14)
        ax.set_ylabel("Minutes / Pages", fontsize=14)
        ax.tick_params(axis='both', labelsize=10)
        fig.autofmt_xdate()
        
        plt.tight_layout()
        plt.show(block=False)
        plt.pause(0.001)

    @staticmethod
    def get_last_seven_days() -> list:
        today = datetime.today()
        month = today.strftime("%b")
        day = today.day
        num_month = today.month
        year = today.year
        last_month_days = None
        if day <= 7:
            last_month_num = (num_month - 2) % 12 + 1
            if num_month == 1:
                year -= 1
            month, last_month_days = DateManager.get_month_and_days(
                last_month_num, year)
            day = (last_month_days + day) - 7
        else:
            day -= 7
        last_seven_days = []
        for _ in range(7):
            date = f"{day:02}-{month}-{year}"
            last_seven_days.append(date)
            day += 1
            if last_month_days and day > last_month_days:
                day = 1
                year = year + 1 if last_month_num == 12 else year # type: ignore
                month, _ = DateManager.get_month_and_days(num_month, year)
                last_month_days = None
        return last_seven_days

    @classmethod
    def generate_weekly_report(cls, data: DataManager):
        for date in cls.get_last_seven_days():
            total_pages = 0
            total_minutes = 0
            if date in data.entry_log:
                for subject, dict_subject in data.entry_log[date].items():
                    for book, book_entry in dict_subject.items():
                        for session, session_entry in book_entry.items():
                            time_spent, entry_pages = cls.extract_time_spent(subject, book, session_entry)
                            total_minutes += Utilities.convert_time_to_mins(time_spent)
                            total_pages += entry_pages
            cls.weekly_report[date] = (total_minutes, total_pages)

    @classmethod
    def extract_time_spent(cls, subject, book, session_entry):
        map_dict = {
            "Al-Qur'an (Tafseer)": TafseerEntry.from_dict,
            "Al-Qur'an (Tilawat)": TilawatEntry.from_dict
        }
        if subject in map_dict:
            entry = map_dict[subject](subject, session_entry)
        else:
            entry = OtherEntry.from_dict(book, session_entry)
        return entry.time_spent, entry.total_pages

    @classmethod
    def build_subjects_cache(cls, data: DataManager) -> None:
        all_time_subjects = {}
        for dict_ in data.entry_log.values():
            cls.extract_subjects(dict_, all_time_subjects)
        cls.extract_subjects(data.progress_today, all_time_subjects)
        all_time_subjects = Utilities.dict_sort(all_time_subjects)
        data.update_cache(all_time_subjects)

    @classmethod
    def extract_subjects(cls, dict_: dict, all_time_subjects: dict) -> None:
        for subject, subject_data in dict_.items():
            if subject in ["Al-Qur'an (Tilawat)", "Al-Qur'an (Tafseer)"]:
                continue
            all_time_subjects.setdefault(subject, [])
            for book in subject_data:
                if book not in all_time_subjects[subject]:
                    all_time_subjects[subject].append(book)
            all_time_subjects[subject].sort()        

    @classmethod
    def calculate_stats(cls, data: DataManager):
        all_time_stats = {}
        for date, progress_date in data.entry_log.items():
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
        data.update_stats(all_time_stats)

