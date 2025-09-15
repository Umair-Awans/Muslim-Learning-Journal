import os, hashlib
from datetime import datetime
from typing import List, Union, Optional, Tuple

class InputProvider:
    @staticmethod
    def choose_key(progress: dict, key: str) -> str:
        while True:
            if not progress:
                print("\nNo progress to edit.")
                return ""
            keys = sorted(list(progress.keys()))
            keys_menu = Menu(keys, f"Select a {key}")
            user_choice, exit_option = keys_menu.display_menu(exit_label="Go Back") # type: ignore
            if user_choice == exit_option:
                return ""
            return keys[user_choice - 1]

    @staticmethod
    def validate_choice(prompt: str, options: List[str]) -> str:
        """
        Validate user input against a list of acceptable string options.

        Args:
            prompt: The message displayed to the user for input.
            options: A list of acceptable string options (case-insensitive).

        Returns:
            The validated user input, matched to one of the options (in uppercase).

        Example:
            >>> validate_choice("Choose a color", ["red", "green", "blue"])
            Choose a color (red, green, blue): 
        """
        options_str = ', '.join(map(
            str, options)) if len(options) > 2 else ' or '.join(map(str, options))
        full_prompt = f"{prompt} ({options_str}): "
        while True:
            user_input = input(full_prompt).strip().upper()
            if user_input in [x.upper() for x in options]:
                return user_input
            print("\nPlease select one of the available options.")

    @staticmethod
    def validate_number(
        prompt: str,
        min_val: Optional[Union[float, int]] = None,
        max_val: Optional[Union[float, int]] = None,
        num_type: Optional[type] = None,
        allow_equal: bool = True,
        exact_length: Optional[int] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None
    ) -> Union[float, int]:
        """
        Prompts the user to enter a number and validates the input against optional value and digit-length constraints.
        Automatically detects whether the number is an integer or a float, unless a specific type is enforced.
        
        Args:
            prompt (str): The message displayed to the user when requesting input.
            min_val (float or int, optional): The minimum allowed value. Defaults to None (no minimum).
            max_val (float or int, optional): The maximum allowed value. Defaults to None (no maximum).
            num_type (type, optional): The expected number type (int or float). Defaults to None (auto-detect).
            allow_equal (bool): Whether to allow the number to be equal to min_val or max_val. Defaults to True.
            exact_length (int, optional): The exact number of digits required (excluding signs and decimal point).
            min_length (int, optional): The minimum number of digits required.
            max_length (int, optional): The maximum number of digits allowed.

        Returns:
            int or float: The validated number entered by the user.

        Raises:
            ValueError: If the input violates any of the specified constraints, or if conflicting constraints are provided.

        Examples:
            # Auto-detect integer or float
            >>> validate_number("Enter a number: ")

            # Require integer only
            >>> validate_number("Enter an integer: ", num_type=int)

            # Require float only
            >>> validate_number("Enter a decimal number: ", num_type=float)

            # Validate a year (must be exactly 4 digits)
            >>> validate_number("Enter the year: ", exact_length=4)
        """

        # Validate length constraints
        if exact_length is not None and (min_length is not None or max_length is not None):
            raise ValueError("Cannot specify exact_length together with min_length or max_length.")
        
        if min_length is not None and max_length is not None and min_length > max_length:
            raise ValueError("min_length cannot be greater than max_length.")

        while True:
            try:
                user_input = input(prompt).strip()
                
                # Digit counting (remove dot and sign)
                digits_only = user_input.replace('.', '').lstrip('+-')
                if not digits_only.isdigit():
                    raise ValueError("Invalid input! Please enter a valid number.")    

                # Try int first if there's no decimal point
                if '.' not in user_input:
                    try:
                        number = int(user_input)
                        if num_type == float:
                            number = float(number)
                    except ValueError:
                        if num_type == int:
                            raise ValueError("Please enter a whole number (like 42).")
                        number = float(user_input)
                else:
                    number = float(user_input)
                    if num_type == int:
                        if not number.is_integer():
                            raise ValueError("Please enter a whole number without decimals.")
                        number = int(number)
                            
                # Length checks
                if exact_length is not None:
                    if len(digits_only) != exact_length:
                        raise ValueError(f"Your number must be exactly {exact_length} digits long.")
                
                if min_length is not None:
                    if len(digits_only) < min_length:
                        raise ValueError(f"Your number must have at least {min_length} digits.")
                
                if max_length is not None:
                    if len(digits_only) > max_length:
                        raise ValueError(f"Your number can have at most {max_length} digits.")
                
                # Value checks
                if min_val is not None and max_val is not None:
                    if allow_equal:
                        if not (min_val <= number <= max_val):
                            raise ValueError(f"Please enter a number between {min_val} and {max_val}.")
                    else:
                        if not (min_val < number < max_val):
                            raise ValueError(f"Please enter a number between {min_val} and {max_val}, not including those exact values.")
                elif min_val is not None:
                    if allow_equal:
                        if number < min_val:
                            raise ValueError(f"Please enter a number greater than or equal to {min_val}.")
                    else:
                        if number <= min_val:
                            raise ValueError(f"Please enter a number greater than {min_val}.")
                elif max_val is not None:
                    if allow_equal:
                        if number > max_val:
                            raise ValueError(f"Please enter a number less than or equal to {max_val}.")
                    else:
                        if number >= max_val:
                            raise ValueError(f"Please enter a number less than {max_val}.")
                
                return number
                
            except ValueError as e:
                print(f"\nError: {e}" if str(e) else "\nInvalid input! Please enter a valid number.")


class Menu:
    """A customizable menu system for console applications.
    
    Attributes:
        menu_name (str): The title displayed when menu is shown.
    """
    
    def __init__(self, options: List[str], menu_name: str = "Main Menu") -> None:
        """Initialize the Menu with options and a title.
        
        Args:
            options: List of menu option strings
            menu_name: Title for the menu. Defaults to "Main Menu".
            
        Example:
            >>> menu = Menu(["Start Game", "Settings"], "Game Menu")
        """
        self.__options = options.copy() if options else []
        self.menu_name = menu_name

    def display_menu(
        self, 
        get_user_choice: bool = True, 
        show_menu_name: bool = True, 
        show_exit: bool = True, 
        exit_label: str = "Exit"
    ) -> Union[None, int, Tuple[int, int]]:
        """Display the menu and optionally collect user choice.
        
        Args:
            get_user_choice: If True, returns user selection. Defaults to True.
            show_menu_name: If True, displays the menu name. Defaults to True.
            show_exit: If True, shows exit option. Defaults to True.
            exit_label: Custom text for exit option. Defaults to "Exit".
            
        Returns:
            If get_user_choice is True:
                - Returns choice only if show_exit is False
                - Returns (choice, exit_option_num) if show_exit is True
            Otherwise returns None
            
        Example:
            >>> choice = menu.display_menu(get_user_choice=True)
        """
        if show_menu_name:
            border = "=" * ((54 - len(self.menu_name)) // 2)
            print(f"\n{border} {self.menu_name} {border}\n")
        
        for i, option in enumerate(self.__options, 1):
            print(f"{i}. {option}")
            
        if show_exit:
            print(f"{len(self.__options) + 1}. {exit_label}")
        
        if not get_user_choice:
            return None
    
        choice = self.get_user_choice(show_exit)
        return (choice, len(self.__options)+1) if show_exit else choice
        

    def get_user_choice(self, show_exit: bool) -> int:
        """Get and validate user's menu selection.
        
        Returns:
            Validated integer choice from the user
            
        Raises:
            ValueError: If invalid input is provided
            
        Example:
            >>> choice = menu.get_user_choice()
        """
        last_option = len(self.__options) + 1 if show_exit else len(self.__options)
        return int(InputProvider.validate_number("\nEnter your choice: ", 1, last_option))


class PasswordManager:
    PASSWORD_FILE = './data/password.txt'

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    @classmethod
    def password_file_exists(cls) -> bool:
        return os.path.exists(cls.PASSWORD_FILE)

    @classmethod
    def store_password(cls, password: str):
        try:
            hashed = cls.hash_password(password)
            with open(cls.PASSWORD_FILE, "w") as file:
                file.write(hashed)
                return True, "Password has been set and stored securely."
        except IOError as e:
            return False, str(e)
    
    @classmethod
    def verify_password(cls, password: str) -> bool:
        with open(cls.PASSWORD_FILE, 'r') as file:
            hashed_password = file.read().strip()
        return cls.hash_password(password) == hashed_password


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

    @classmethod
    def get_date_from_user(cls) -> str:
        year = int(InputProvider.validate_number("\nPlease enter the year: ",
                               2023,
                               2025,
                               exact_length=4))
        month_number = int(
            InputProvider.validate_number("\nPlease enter the month (1-12): ", 1, 12))
        month, max_days = cls.get_month_and_days(month_number, year)
        day = int(InputProvider.validate_number("\nPlease enter the day: ", 1, max_days))
        day = day if day > 9 else f"0{day}"
        return f"{day}-{month}-{year}"

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


class Utilities:
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
        dict_stats[subject][book].setdefault("Entry Dates", [])

    @staticmethod
    def pop_empty_dicts(dict_: dict, dict1: str, dict2: str) -> None:
        if not dict_[dict1][dict2]:
            dict_[dict1].pop(dict2)
            if not dict_[dict1]:
                dict_.pop(dict1)
                
    @staticmethod
    def get_time_str(hours, minutes) -> str:
        total_time = ""
        if hours:
            total_time += f"{hours} hr(s) "
        if minutes:
            total_time += f"{minutes} mins(s)"
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


class ProgressUtils:
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


class CliInputCollector:
    """Provides methods to gather and validate data from the user via the command line."""
    @staticmethod
    def get_password():
        print("\nNo password has been set. Please set one to continue.")
        while True:
            password = input("\nEnter your password: ").strip()
            confirm = input("\nConfirm your password: ").strip()
            if password == confirm:
                return password
            print("\nPasswords did not match. Enter again.")

    @staticmethod
    def get_entry_range(entry: str, limit=None) -> tuple:
        start_entry = InputProvider.validate_number(f"\nEnter the starting {entry} number: ",
                                      max_val=limit)
        last_entry = InputProvider.validate_number(f"Enter the last {entry} number: ",
                                     start_entry)
        return ProgressUtils.get_str_and_total(start_entry, last_entry)

    @staticmethod
    def get_time_spent(book: str):
        mins_spent = InputProvider.validate_number(
            f"\nEnter the time spent on {book} in this session (in minutes): ")
        return Utilities.format_time(int(mins_spent))

    @staticmethod
    def get_notes():
        return input("\nAny additional notes? (optional): ").strip() or "N/A"

    @staticmethod
    def get_revision() -> str:
        if InputProvider.validate_choice(
            f"\nDid you revise anything in this session?",
            ["Y", "N"]) == "N":
            return "No"

        return input(
            f"\nPlease enter the revision details (optional): "
        ).strip() or "Revised previous content"

    @staticmethod
    def get_reading_mode() -> str:
        return "Sequential" if InputProvider.validate_choice(
            "\nAre you reading sequentially?", ["Y", "N"]) == "Y" else "Random"

    @staticmethod
    def get_chapter():
        return input("\nEnter chapter name (optional): ").strip() or "N/A"


class DeleteController:
    DEL_OPTIONS = [
        "Delete today's entries", "Delete entries from another day", "Delete all recorded entries"
    ]

    @staticmethod
    def delete_day(date: str, data_manager):
        return data_manager.delete_progress(date=date)

    @staticmethod
    def delete_all(password: str, data_manager):
        if not PasswordManager.verify_password(password):
            return False, "WRONG PASSWORD!"
        return data_manager.delete_progress(delete_all=True)