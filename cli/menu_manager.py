import sys
from copy import deepcopy
from core.app_context import AppContext
from core.data_manager import DataManager
from core.core_services import (DateManager, CoreHelpers, DeleteController)
from core.exceptions import DataCorruptionError
from cli.cli_workflow import CliWorkflow
from cli.cli_prompt import CliPrompt
from cli.cli_editor import CliProgressEditor
from cli.cli_display import CliProgressDisplay
from cli.menu import Menu

class Menus:
    @classmethod
    def save_progress(cls, context: AppContext):
        return_code =  context.save_progress_to_files()
        if return_code == 0:
            print("\nProgress saved successfully!")
        elif return_code == 1:
            print("\nERROR! Could not save JSON file.")
        elif return_code == 2:
            print("\nERROR! Could not save Markdown file.")

    @staticmethod
    def edit_progress_menu(data_manager: DataManager) -> None:
        date_opt = int(
            CliPrompt.validate_number(
                "\nWould you like to edit today's entries or previous entries?\n1. Today's entries\n2. Previous entries\n\nYour choice: ",
                1, 2))
        if date_opt == 1:
            date = DateManager.get_date_today()
        else:
            print("\nEnter the date you wish to edit entries for:")
            date = CliPrompt.get_date_from_user()
        if date in data_manager.entry_log:
            progress_copy = deepcopy(data_manager.entry_log[date])
            CliProgressEditor.edit_progress(progress_copy, data_manager, date)
            data_manager.update_entry_log(date, progress_copy)
        else:
            print(f"No entries found for {'today' if date_opt == 1 else date}.")

    @staticmethod
    def view_progress_menu(data_manager: DataManager) -> None:
        date_opt = int(
            CliPrompt.validate_number(
                "\nWould you like to view today's entries or previous entries?\n1. Today's entries\n2. Previous entries\n\nYour choice: ",
                1, 2))
        if date_opt == 1:
            date = DateManager.get_date_today()
        else:
            print("\nEnter the date you wish to view entries for:")
            date = CliPrompt.get_date_from_user()
        entries = data_manager.get_entries_from_date(date)
        if entries:
            CliProgressDisplay.display_entries_all(entries, date)
        else:
            print(
                f"No entries found for {'today' if date_opt == 1 else date}. Please try another date."
            )
    
    @staticmethod
    def delete_progress_menu(context: AppContext) -> None:
        what_to_del = CliPrompt.validate_number(
            f"\nDelete Options:\n\n1. {DeleteController.DEL_OPTIONS[0]}\n2. {DeleteController.DEL_OPTIONS[1]}\n3. {DeleteController.DEL_OPTIONS[2]}\n\nYour choice: ",
            1, 3)
        if CliPrompt.validate_choice(
            f"\nAre you sure you want to {DeleteController.DEL_OPTIONS[int(what_to_del) - 1].lower()}?",
            ["Y", "N"]) == "N":
            return
        if what_to_del == 1:
            today = DateManager.get_date_today()
            print(DeleteController.delete_day(today, context)[1])
        elif what_to_del == 2:
            date = CliPrompt.get_date_from_user()
            print(DeleteController.delete_day(date, context)[1])
        else:
            password = input("\nEnter Your Password: ").strip()
            print(DeleteController.delete_all_with_password_check(password, context)[1])

    @staticmethod
    def exit_program(data_manager: DataManager) -> bool:
        confirmation = CliPrompt.validate_choice(
            "\nAny unsaved changes will be lost. Are you sure you want to exit?",
            ["Y", "N"])
        if confirmation == "Y":
            if not "Al-Qur'an (Tafseer)" in data_manager.progress_today:
                print(CoreHelpers.get_motivational_quote())
            if not data_manager.progress_today:
                print("\nNo progress today! Another day wasted.\n")
            else:
                print("\nHave a nice day!\n")
        return confirmation == "Y"

    @classmethod
    def main_menu(cls, context: AppContext) -> None:
        print("\n<><><>__( Muslim Learning Journal )__<><><>\n")
                
        print("\n-------------( Weekly Report )-------------\n")
        print(context.stats_manager.get_weekly_summary())
        
        MENU_ITEMS = [
            "Al-Qur'an (Tafseer)", "Al-Qur'an (Tilawat)", "Log Other Subjects",
            "Save Progress", "View Entries", "Edit Entries", "Delete Entries", "Check Weekly Report"
        ]
        main_menu = Menu(MENU_ITEMS)
        
        while True:
            user_choice, exit_option = main_menu.display_menu() # type: ignore
            if user_choice == exit_option:
                if cls.exit_program(context.data_manager):
                    return
            elif user_choice == 1:
                CliWorkflow.log_Quran_progress(context)
            elif user_choice == 2:
                CliWorkflow.log_Quran_progress(context, "Tilawat")
            elif user_choice == 3:
                CliWorkflow.log_other_progress(context)
            elif user_choice == 4:
                cls.save_progress(context)
            elif user_choice == 5:
                cls.view_progress_menu(context.data_manager)
            elif user_choice == 6:
                cls.edit_progress_menu(context.data_manager)
            elif user_choice == 7:
                cls.delete_progress_menu(context)
            elif user_choice == 8:
                print("\nLoading the plot. Please wait.....")
                context.stats_manager.display_plot_weekly()


def main():

    try:
        context = AppContext()
    except DataCorruptionError as e:
        print(f"ERROR:\n{e}\n\nDetails: {e.__cause__}")
        sys.exit(1)

    if not context.password_manager.is_password_set():
        CliPrompt.get_and_set_password(context.password_manager)
        
    Menus.main_menu(context)
