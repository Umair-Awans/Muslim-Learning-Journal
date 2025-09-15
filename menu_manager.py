from copy import deepcopy
from core_utils import (InputProvider, DateManager, Menu, PasswordManager, DeleteController)
from file_manager import DataManager
from progress_tools import ProgressEditor, ProgressDisplay, ProgressLogger
from stats_manager import StatsManager


class StatsDisplay:
    @staticmethod
    def display_plot(stats: StatsManager):
        if not hasattr(stats, "weekly_total_time"):
            stats.compute_weekly_stats()
        print("\nLoading the plot. Please wait.....")
        import matplotlib.pyplot as plt
        title = "Weekly Report"
        plt.style.use('seaborn')
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(stats.weekly_dates, stats.weekly_minutes_spent, linewidth=3, marker='o', label='Minutes Spent')
        ax.plot(stats.weekly_dates, stats.weekly_pages_read, linewidth=3, marker='o', label='Pages Read')
        ax.legend()
        ax.set_title(f"{title} (Total Time: {stats.weekly_total_time})", fontsize=15)
        ax.set_xlabel("Date", fontsize=14)
        ax.set_ylabel("Minutes / Pages", fontsize=14)
        ax.tick_params(axis='both', labelsize=10)
        fig.autofmt_xdate()
        
        plt.tight_layout()
        plt.show(block=False)
        plt.pause(0.001)

    @staticmethod
    def show_weekly_stats(stats: StatsManager):
        print(stats.get_weekly_summary())


class Menus:
    @classmethod
    def save_progress(cls, data_manager: DataManager):
        return_code =  data_manager.save_progress_to_files()
        if return_code == 0:
            print("\nProgress saved successfully!")
        elif return_code == 1:
            print("\nCould not save JSON file.")
        elif return_code == 2:
            print("\nCould not save Markdown file.")

    @staticmethod
    def edit_progress_menu(data_manager: DataManager) -> None:
        date_opt = int(
            InputProvider.validate_number(
                "\nWould you like to edit today's entries or previous entries?\n1. Today's entries\n2. Previous entries\n\nYour choice: ",
                1, 2))
        if date_opt == 1:
            date = DateManager.get_date_today()
        else:
            print("\nEnter the date you wish to edit entries for:")
            date = DateManager.get_date_from_user()
        if date in data_manager.entry_log:
            progress_copy = deepcopy(data_manager.entry_log[date])
            ProgressEditor.edit_progress(progress_copy, data_manager, date)
            data_manager.update_entry_log(date, progress_copy)
        else:
            print(
                f"No entries found for {'today' if date_opt == 1 else date}.")

    @staticmethod
    def view_progress_menu(data_manager: DataManager) -> None:
        date_opt = int(
            InputProvider.validate_number(
                "\nWould you like to view today's entries or previous entries?\n1. Today's entries\n2. Previous entries\n\nYour choice: ",
                1, 2))
        if date_opt == 1:
            date = DateManager.get_date_today()
        else:
            print("\nEnter the date you wish to view entries for:")
            date = DateManager.get_date_from_user()
        entries = data_manager.get_entries_from_date(date)
        if entries:
            ProgressDisplay.display_entries_all(entries, date)
        else:
            print(
                f"No entries found for {'today' if date_opt == 1 else date}. Please try another date."
            )
    
    @staticmethod
    def delete_progress_menu(data_manager: DataManager) -> None:
        what_to_del = InputProvider.validate_number(
            f"\nDelete Options:\n\n1. {DeleteController.DEL_OPTIONS[0]}\n2. {DeleteController.DEL_OPTIONS[1]}\n3. {DeleteController.DEL_OPTIONS[2]}\n\nYour choice: ",
            1, 3)
        if InputProvider.validate_choice(
            f"\nAre you sure you want to {DeleteController.DEL_OPTIONS[int(what_to_del) - 1].lower()}?",
            ["Y", "N"]) == "N":
            return
        if what_to_del == 1:
            today = DateManager.get_date_today()
            print(DeleteController.delete_day(today, data_manager)[1])
        elif what_to_del == 2:
            date = DateManager.get_date_from_user()
            print(DeleteController.delete_day(date, data_manager)[1])
        else:
            password = input("\nEnter Your Password: ").strip()
            print(DeleteController.delete_all(password, data_manager)[1])

    @staticmethod
    def exit_program(data_manager: DataManager) -> bool:
        confirmation = InputProvider.validate_choice(
            "\nAny unsaved changes will be lost. Are you sure you want to exit?",
            ["Y", "N"])
        if confirmation == "Y":
            if not "Al-Qur'an (Tafseer)" in data_manager.progress_today:
                print(ProgressLogger.Quran.get_random_quote())
            if not data_manager.progress_today:
                print("\nNo progress today! Another day wasted.\n")
            else:
                print("\nHave a nice day!\n")
        return confirmation == "Y"

    @classmethod
    def main_menu(cls) -> None:
        print("\n<><><>__( Muslim Learning Journal )__<><><>\n")
        data_manager = DataManager()
        stats_manager = StatsManager(data_manager)
        StatsDisplay.show_weekly_stats(stats_manager)
        stats_manager.build_subjects_cache()
        stats_manager.calculate_stats()
        
        MENU_ITEMS = [
            "Al-Qur'an (Tafseer)", "Al-Qur'an (Tilawat)", "Log Other Subjects",
            "Save Progress", "View Entries", "Edit Entries", "Delete Entries", "Check Weekly Report"
        ]
        main_menu = Menu(MENU_ITEMS)
        
        while True:
            user_choice, exit_option = main_menu.display_menu() # type: ignore
            if user_choice == exit_option:
                if cls.exit_program(data_manager):
                    return
            elif user_choice == 1:
                ProgressLogger.Quran.log_Quran_progress(data_manager)
            elif user_choice == 2:
                ProgressLogger.Quran.log_Quran_progress(data_manager, "Tilawat")
            elif user_choice == 3:
                ProgressLogger.OtherSubjects.log_other_progress(data_manager)
            elif user_choice == 4:
                cls.save_progress(data_manager)
            elif user_choice == 5:
                cls.view_progress_menu(data_manager)
            elif user_choice == 6:
                cls.edit_progress_menu(data_manager)
            elif user_choice == 7:
                cls.delete_progress_menu(data_manager)
            elif user_choice == 8:
                StatsDisplay.display_plot(stats_manager)
