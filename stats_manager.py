from datetime import datetime
from entries import TafseerEntry, TilawatEntry, OtherEntry
from file_manager import DataManager
from core_utils import DateManager


class StatsManager:
    __all_time_subjects = {}

    @classmethod
    def get_all_time_subjects(cls) -> dict:
        return cls.__all_time_subjects

    @classmethod
    def clear_cache(cls) -> None:
        cls.__all_time_subjects.clear()

    @classmethod
    def build_subjects_cache(cls, data: DataManager) -> None:
        if not data.all_time_subjects:
            for dict_ in data.dict_main.values():
                cls.extract_subjects(dict_, data)
            cls.extract_subjects(data.progress_today, data)
        else:
            cls.extract_subjects(data.progress_today, data)

    @classmethod
    def extract_subjects(cls, dict_: dict, data: DataManager) -> None:
        for subject, subject_data in dict_.items():
            if subject in ["Al-Qur'an (Tilawat)", "Al-Qur'an (Tafseer)"]:
                continue
            data.all_time_subjects.setdefault(subject, [])
            for book in subject_data:
                if book not in data.all_time_subjects[subject]:
                    data.all_time_subjects[subject].append(book)
            data.all_time_subjects[subject].sort()

    @staticmethod
    def format_time(total_minutes: int) -> str:
        hours = f"{total_minutes//60} hr(s)" if total_minutes // 60 > 0 else ""
        minutes = f"{total_minutes%60} min(s)" if total_minutes % 60 > 0 else ""
        total_time = (hours + " " + minutes).strip()
        return total_time if total_time else "0 min(s)"
    
    @classmethod
    def convert_time_to_mins(cls, total_minutes, time_spent) -> int:
        if "hr(s)" in time_spent:
            hours = int(time_spent.split("hr(s)")[0].strip())
            total_minutes += (hours * 60)
        if "min(s)" in time_spent:
            mins = time_spent.split("min(s)")[0].strip()
            if "hr(s)" in mins:
                mins = mins.split("hr(s)")[1].strip()
            mins = int(mins)
            total_minutes += mins
        return total_minutes

    @classmethod
    def display_stats(cls,
                      total_minutes: int,
                      title: str = "Weekly Report",
                      duration: str = "week"):
        print(f"\n-------------( {title} )-------------\n")
        total_time = cls.format_time(total_minutes)
        prompts = [
            f"\nYou spent a total of {total_time} on learning activities over the past {duration}.\n",
            f"\nNo learning activity was recorded for this {duration}.\n"
        ]
        index = 0 if total_time != "0 min(s)" else 1
        print(prompts[index])

    @staticmethod
    def get_last_seven_days() -> list:
        num_day = int(datetime.today().strftime("%d"))
        month = datetime.today().strftime("%b")
        num_month = int(datetime.today().strftime("%m"))
        year = int(datetime.today().strftime("%Y"))
        last_month_days = 0
        if num_day <= 7:
            if num_month == 1:
                last_month_num = 12
                year -= 1
            else:
                last_month_num = num_month - 1
            month, last_month_days = DateManager.get_month_and_days(
                last_month_num, year)
            num_day = (last_month_days + num_day) - 7
        else:
            num_day -= 7
        last_seven_days = []
        for _ in range(7):
            date = f"{num_day}-{month}-{year}"
            last_seven_days.append(date)
            num_day += 1
            if last_month_days and num_day == last_month_days:
                num_day = 1
                year = year + 1 if last_month_num == 12 else year  # type: ignore
                month, _ = DateManager.get_month_and_days(num_month, year)
        return last_seven_days

    @classmethod
    def get_weekly_report(cls, data: DataManager):
        total_minutes = 0
        for date in cls.get_last_seven_days():
            if date in data.dict_main:
                for subject, dict_subject in data.dict_main[date].items():
                    time_spent = cls.extract_time_spent(subject, dict_subject)
                    total_minutes = cls.convert_time_to_mins(
                        total_minutes, time_spent)
        cls.display_stats(total_minutes)

    @classmethod
    def extract_time_spent(cls, subject, dict_subject):
        map_dict = {
            "Al-Qur'an (Tafseer)": TafseerEntry.from_dict,
            "Al-Qur'an (Tilawat)": TilawatEntry.from_dict
        }
        for book, book_entry in dict_subject.items():
            for session, session_entry in book_entry.items():
                if subject in map_dict:
                    entry = map_dict[subject](subject, session_entry)
                else:
                    entry = OtherEntry.from_dict(book, session_entry)
                time_spent = entry.time_spent
        return time_spent  # type: ignore

    @classmethod
    def temporary_backfill(cls, data: DataManager):
        all_time = {}
        for date, progress_date in data.dict_main.items():
            for subject, progress_subject in progress_date.items():
                all_time.setdefault(subject, {})
                for book, progress_book in progress_subject.items():
                    all_time[subject].setdefault(book, {})
                    all_time[subject][book].setdefault("Minutes", 0)
                    all_time[subject][book].setdefault("Pages", 0)
                    all_time[subject][book].setdefault("Time Spent", "")
                    all_time[subject][book].setdefault("Entry Dates", [])
                    all_time[subject][book]["Entry Dates"].append(date)
                    for entry, progress_entry in progress_book.items():
                        all_time[subject][book]["Minutes"] = cls.convert_time_to_mins(
                            all_time[subject][book]["Minutes"], progress_entry["Time Spent"])
                        all_time[subject][book]["Pages"] += progress_entry["Total Pages"]
        all_time = dict(sorted(all_time.items()))
        for subject, dict_subject in all_time.items():
            temp = sorted((dict_subject.items()), key=lambda x: cls.extract_sort_key(x[0]))
            all_time[subject] = dict(temp)
            for book, dict_book in all_time[subject].items():
                dict_book["Time Spent"] = cls.format_time(dict_book["Minutes"])
                dict_book.pop("Minutes")
        data.stats = all_time

    @staticmethod
    def extract_sort_key(book_title: str):
        try:
            # Try extracting number from end
            num = int(book_title.split()[-1])
            return (0, num)  # 0 = numeric books, then sort by number
        except ValueError:
            return (1, book_title.lower())  # 1 = text-only books, then sort alphabetically
