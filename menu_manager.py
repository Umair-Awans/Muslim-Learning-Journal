from copy import deepcopy
from core_utils import (validate_choice, validate_number, DateManager, Menu)
from file_manager import DataManager
from progress_tools import ProgressEditor, ProgressDisplay, ProgressLogger
from stats_manager import StatsManager

class Menus:
    @staticmethod
    def edit_progress_menu(data: DataManager) -> None:
        date_opt = int(
            validate_number(
                "\nWould you like to edit today's entries or previous entries?\n1. Today's entries\n2. Previous entries\n\nYour choice: ",
                1, 2))
        if date_opt == 1:
            date = DateManager.get_date_today()
        else:
            print("\nEnter the date you wish to edit entries for:")
            date = DateManager.get_date_from_user()
        if date in data.dict_main:
            progress_copy = deepcopy(data.dict_main[date])
            ProgressEditor.edit_progress(progress_copy)
            data.update_dict_main(date, progress_copy)
        else:
            print(
                f"No entries found for {'today' if date_opt == 1 else date}.")

    @staticmethod
    def view_progress_menu(data: DataManager) -> None:
        date_opt = int(
            validate_number(
                "\nWould you like to view today's entries or previous entries?\n1. Today's entries\n2. Previous entries\n\nYour choice: ",
                1, 2))
        if date_opt == 1:
            date = DateManager.get_date_today()
        else:
            print("\nEnter the date you wish to view entries for:")
            date = DateManager.get_date_from_user()
        if date in data.dict_main:
            ProgressDisplay.display_entries_all(data.dict_main[date], date)
        else:
            print(
                f"No entries found for {'today' if date_opt == 1 else date}. Please try another date."
            )

    @staticmethod
    def exit_program(data: DataManager) -> bool:
        confirmation = validate_choice(
            "\nAny unsaved changes will be lost. Are you sure you want to exit?.",
            ["Y", "N"])
        if confirmation == "Y":
            if not "Al-Qur'an (Tafseer)" in data.progress_today:
                print(ProgressLogger.Quran.get_random_quote())
            if not data.progress_today:
                print("\nNo progress today! Another day wasted.\n")
            else:
                print("\nHave a nice day!\n")
        return confirmation == "Y"

    @classmethod
    def main_menu(cls) -> None:
        print("\n<><><>__( Learning Journal )__<><><>\n")
        data = DataManager()
        MENU_ITEMS = [
            "Al-Qur'an (Tafseer)", "Al-Qur'an (Manzil)", "Other Categories",
            "Save Changes", "View Entries", "Edit Entries", "Delete Entries"
        ]
        main_menu = Menu(MENU_ITEMS)
        StatsManager.get_weekly_report(data)
        while True:
            user_choice, exit_option = main_menu.display_menu()
            if user_choice == exit_option:
                if cls.exit_program(data):
                    return
            elif user_choice == 1:
                ProgressLogger.Quran.log_Quran_progress(data)
            elif user_choice == 2:
                ProgressLogger.Quran.log_Quran_progress(data, "Manzil")
            elif user_choice == 3:
                ProgressLogger.OtherCategories.log_other_progress(data)
            elif user_choice == 4:
                data.save_progress_to_files()
            elif user_choice == 5:
                cls.view_progress_menu(data)
            elif user_choice == 6:
                cls.edit_progress_menu(data)
            elif user_choice == 7:
                ProgressEditor.delete_progress(data)