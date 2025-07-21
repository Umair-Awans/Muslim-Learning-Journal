from datetime import datetime
from entries import TafseerEntry, TilawatEntry, OtherEntry
from file_manager import DataManager
from core_utils import DateManager, Utilities


class StatsManager:  

    @classmethod
    def display_stats(cls,
                      total_minutes: int,
                      title: str = "Weekly Report",
                      duration: str = "week"):
        print(f"\n-------------( {title} )-------------\n")
        total_time = Utilities.format_time(total_minutes)
        prompts = [
            f"\nYou spent a total of {total_time} on learning activities during the previous {duration} (excluding today).\n",
            f"\nNo learning activity was recorded during the previous {duration} (excluding today).\n"
        ]
        index = 0 if total_minutes > 0 else 1
        print(prompts[index])

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
    def get_weekly_report(cls, data: DataManager):
        total_minutes = 0
        for date in cls.get_last_seven_days():
            if date in data.entry_log:
                for subject, dict_subject in data.entry_log[date].items():
                    for book, book_entry in dict_subject.items():
                        for _, session_entry in book_entry.items():
                            time_spent = cls.extract_time_spent(subject, book, session_entry)
                            total_minutes += Utilities.convert_time_to_mins(time_spent)
        cls.display_stats(total_minutes)

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
        return entry.time_spent

    @classmethod
    def build_subjects_cache(cls, data: DataManager) -> None:
        all_time_subjects = {}
        for dict_ in data.entry_log.values():
            cls.extract_subjects(dict_, all_time_subjects)
        cls.extract_subjects(data.progress_today, all_time_subjects)
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
        all_time = {}
        for date, progress_date in data.entry_log.items():
            for subject, progress_subject in progress_date.items():
                all_time.setdefault(subject, {})
                for book, progress_book in progress_subject.items():
                    all_time[subject].setdefault(book, {})
                    all_time[subject][book].setdefault("Minutes", 0)
                    all_time[subject][book].setdefault("Pages", 0)
                    all_time[subject][book].setdefault("Time Spent", "")
                    all_time[subject][book].setdefault("Entry Dates", [])
                    all_time[subject][book]["Entry Dates"].append(date)
                    for _, progress_entry in progress_book.items():
                        all_time[subject][book]["Minutes"] += Utilities.convert_time_to_mins(progress_entry["Time Spent"])
                        all_time[subject][book]["Pages"] += progress_entry["Total Pages"]
        all_time = dict(sorted(all_time.items()))
        for subject, dict_subject in all_time.items():
            temp = sorted((dict_subject.items()), key=lambda x: cls.extract_sort_key(x[0]))
            all_time[subject] = dict(temp)
            for book, dict_book in all_time[subject].items():
                dict_book["Time Spent"] = Utilities.format_time(dict_book["Minutes"])
                dict_book.pop("Minutes")
        data.update_stats(all_time)

    @staticmethod
    def extract_sort_key(book_title: str):
        try:
            # Try extracting number from end
            num = int(book_title.split()[-1])
            return (0, num)  # 0 = numeric books, then sort by number
        except ValueError:
            return (1, book_title.lower())  # 1 = text-only books, then sort alphabetically
