import os, hashlib, random
from datetime import datetime


class DataCarrier:
    def __init__(self):
        self.common_raw_data: dict = {}
        self.raw_data: dict = {}
        self.data_final: dict = {}
    
    def clear_all(self):
        self.common_raw_data.clear()
        self.raw_data.clear()
        self.data_final.clear()


class PasswordManager:
    def __init__(self, path_password_file: str) -> None:
        self.password_file = path_password_file

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def store_password(self, password: str):
        try:
            hashed = self.hash_password(password)
            with open(self.password_file, "w") as file:
                file.write(hashed)
                return True, "Password has been set and stored securely."
        except IOError as e:
            return False, str(e)
    
    def set_password(self, password: str, confirm_password: str):
        if len(password) < 6:
            return False, "Password needs to be at least 6 characters long"
        if password != confirm_password:
            return False, "Passwords do not match. Enter again"
        return self.store_password(password)

    def is_password_set(self) -> bool:
        return os.path.exists(self.password_file) and os.path.getsize(self.password_file) > 0

    def verify_password(self, password: str) -> bool:
        try:
            with open(self.password_file, 'r') as file:
                hashed_password = file.read().strip()
            return self.hash_password(password) == hashed_password
        except Exception:
            return False


class DateManager:
    @staticmethod
    def get_day_today() -> str:
        return datetime.today().strftime("%A")

    @staticmethod
    def get_date_today() -> str:
        return datetime.today().strftime("%d-%b-%Y")

    @staticmethod
    def get_current_time() -> str:
        return datetime.now().strftime("%I:%M:%S %p")

    @staticmethod
    def is_leap_year(year: int) -> bool:
        """Return True if the given year is a leap year, else False."""
        return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0 

    @classmethod
    def get_month_and_days(cls, number: int, year: int) -> tuple:        
        months_days_map = {
            "Jan": 31,
            "Feb": 28 if not cls.is_leap_year(year) else 29,
            "Mar": 31,
            "Apr": 30,
            "May": 31,
            "Jun": 30,
            "Jul": 31,
            "Aug": 31,
            "Sep": 30,
            "Oct": 31,
            "Nov": 30,
            "Dec": 31
        }
        months_names = list(months_days_map.keys())
        return months_names[number - 1], months_days_map[months_names[number -
                                                                      1]]

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


class CoreHelpers:
    @staticmethod
    def get_motivational_quote() -> str:
        quotes = [
            "\nA day without Qur'an is a day Wasted.",
            "\nEven a small step with the Qur'an brightens the day.",
            "\nRemember, a day without Qur'an feels incomplete."
        ]
        motivation = "\n\nREAD! even if just ONE LETTER. Don't waste this day."
        return random.choice(quotes) + motivation
        
    @staticmethod
    def extract_sort_key(book_title: str):
        try:
            # Try extracting number from end
            num = int(book_title.split()[-1])
            return (0, num)  # 0 = numeric books, then sort by number
        except ValueError:
            return (1, book_title.lower())  # 1 = text-only books, then sort alphabetically

    @classmethod
    def dict_sort(cls, dict_: dict) -> dict:
        return dict(sorted((dict_.items()), key=lambda x: cls.extract_sort_key(x[0])))

    @staticmethod
    def set_defaults_for_stats(dict_stats: dict, subject: str, book: str) -> None:
        dict_stats.setdefault(subject, {}).setdefault(book, {})
        dict_stats[subject][book].setdefault("Pages", 0)
        dict_stats[subject][book].setdefault("Time Spent", "")
        dict_stats[subject][book].setdefault("Total Entries", 0)
        dict_stats[subject][book].setdefault("Entry Dates", [])    
                
    @staticmethod
    def get_time_str(hours, minutes) -> str:
        total_time = ""
        if hours:
            total_time += f"{hours} hr(s) "
        if minutes:
            total_time += f"{minutes} min(s)"
        return total_time.strip() if total_time else "0 min(s)"

    @classmethod
    def format_time(cls, total_minutes: int) -> str:
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return cls.get_time_str(hours, minutes)
    
    @classmethod
    def convert_time_to_mins(cls, time_spent) -> int:
        total_minutes = 0
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


class ProgressRules:
    """Backend helpers for progress tracking."""

    @staticmethod
    def get_str_and_total(start_entry, last_entry):
        """
        Convert start/last entries into a string representation and total count.
        
        Rules:
        - If only one entry is given → use that as the string, total = 1.
        - If both are given:
            * If equal → just that number, total = 1.
            * If int → inclusive count.
            * If float → difference, rounded to 1 decimal.
        - If neither is given → empty string, total = 0.
        """
        # Case: only one provided
        if not start_entry:
            return str(last_entry), 1
        if not last_entry:
            return str(start_entry), 1

        # Case: both provided
        if start_entry == last_entry:
            return str(start_entry), 1

        entry_str = f"{start_entry} - {last_entry}"

        if isinstance(start_entry, float) or isinstance(last_entry, float):
            total = round(last_entry - start_entry, 1)
            total = int(total) if total == int(total) else total
        else:
            total = last_entry - start_entry + 1  # inclusive range
        return entry_str, total


class DeleteController:
    DEL_OPTIONS = [
        "Delete today's entries", "Delete entries from another day", "Delete all recorded entries"
    ]

    @staticmethod
    def delete_day(date: str, context):
        if date in context.data_manager.entry_log:
            context.stats_manager.delete_stats(date)
        return context.data_manager.delete_data(date=date)

    @staticmethod
    def delete_all_with_password_check(password: str, context):
        if not context.password_manager.verify_password(password):
            return False, "WRONG PASSWORD!"
        return context.data_manager.delete_data(delete_all_progress=True)