import random
from entries import TafseerEntry, TilawatEntry, OtherEntry
from file_manager import DataManager
from stats_manager import StatsManager
from core_utils import (Validation, PasswordManager, DateManager,
                        validate_choice, validate_number, Menu)


class ProgressLogger:
    class Quran:
        @staticmethod
        def get_random_quote() -> str:
            quotes = [
                "\nA day without Qur'an is a day Wasted.",
                "\nEven a small step with the Qur'an brightens the day.",
                "\nRemember, a day without Qur'an feels incomplete."
            ]
            motivation = "\n\nREAD! even if just ONE LETTER. Don't waste this day."
            return random.choice(quotes) + motivation

        @classmethod
        def log_Quran_progress(cls,
                                  data: DataManager,
                                  method: str = "Tafseer") -> None:
            method_full = f"Al-Qur'an ({method})"
            print(f"\n<><><>__( {method_full} )__<><><>")
            while True:
                Para_number = Validation.get_first_and_last("Para", 30)[0]
                Para = f"Para no. {Para_number}"
                if method == "Tafseer":
                    entry = TafseerEntry.from_user_input(method_full)
                else:
                    entry = TilawatEntry.from_user_input(method_full)                
                data.append_entry(method_full, Para, entry.to_dict())
                if validate_choice(
                    f"\nDo you want to add another {method_full} entry to the log?", ["Y", "N"]) == "N":
                    return


    class OtherSubjects: 

        @classmethod
        def get_subject_books(cls) -> tuple:
            if StatsManager.get_all_time_subjects():
                subjects_list = [
                    "New Subject",
                    *StatsManager.get_all_time_subjects().keys()
                ]
                subjects_menu = Menu(subjects_list, "Select a Subject")
                user_choice = subjects_menu.display_menu(show_exit=False)
                if user_choice != 1:
                    subject = subjects_list[user_choice - 1] # type: ignore
                    return subject, StatsManager.get_all_time_subjects(
                    )[subject]
            while True:
                subject = input("\nEnter a subject name: ").strip()
                subject = "Qur'an" if subject == "Al-Qur'an (Tafseer)" else subject
                if subject:
                    return subject, None
                print("\nSubject cannot be blank.")

        @classmethod
        def get_book_name(cls, subject: str, books_list: list) -> str:
            if books_list:
                books_menu_list = ["New Book", *books_list]
                books_menu = Menu(books_menu_list, "Select a book")
                user_choice = books_menu.display_menu(show_exit=False)
                if user_choice != 1:
                    return books_menu_list[user_choice - 1] # type: ignore
            while True:
                book = input(
                    f"Enter the \"{subject}\" book or material title: ").strip()
                if book:
                    return book
                print("\nBook title cannot be blank.")

        @classmethod
        def get_and_add_progress(cls, data: DataManager) -> None:
            StatsManager.build_subjects_cache(data)
            subject, books_list = cls.get_subject_books()
            print(f"\n<><><>__(<<[ {subject} ]>>)__<><><>\n")
            book_name = cls.get_book_name(subject, books_list)
            print(f"\n<><><>__(<< {book_name} >>)__<><><>\n")
            entry = OtherEntry.from_user_input(book_name)
            data.append_entry(subject, book_name, entry.to_dict())

        @classmethod
        def log_other_progress(cls, data: DataManager) -> None:
            while True:
                cls.get_and_add_progress(data)
                if validate_choice(
                    "\nWould you like to add another entry to today's log?",
                    ["Y", "N"]) == "N":
                    return


class ProgressEditor:

    @staticmethod
    def pop_empty_dicts(main_dict: dict, dict1: str, dict2: str = ""):

        def pop_first_dict(main_dict: dict, dict1: str):
            if not main_dict[dict1]:
                main_dict.pop(dict1)

        if dict2:
            if not main_dict[dict1][dict2]:
                main_dict[dict1].pop(dict2)
            pop_first_dict(main_dict, dict1)
        else:
            pop_first_dict(main_dict, dict1)

    @classmethod
    def edit_subject(cls, subject: str, editable_entries: list, entry_instance):
        entries_menu = Menu(editable_entries, subject)
        while True:
            user_choice, exit_option = entries_menu.display_menu() # type: ignore
            if user_choice == exit_option:
                return
            field = editable_entries[user_choice - 1]
            entry_instance.edit_field(field)
            print(f"\n{field} updated!\n")

    @classmethod
    def edit_progress(cls, progress: dict) -> None:
        while True:
            if not progress:
                print("\nNo progress to edit.")
                return            
            subject = Validation.get_a_key(progress, "Subject")
            if not subject:
                if validate_choice("\nBack to Main Menu? ", ["Y", "N"]) == "Y":
                    return
            book_title = "Para" if subject in ["Al-Qur'an (Tilawat)", "Al-Qur'an (Tafseer)"] else "Book"
            book_name = Validation.get_a_key(progress[subject], book_title)
            if not book_name:
                continue                
            session = Validation.get_a_key(progress[subject][book_name], "Session")
            if not session:
                continue                
            dict_to_edit = progress[subject][book_name][session]
            if subject == "Al-Qur'an (Tafseer)":
                entry_instance = TafseerEntry.from_dict(book_name, dict_to_edit)
            elif subject == "Al-Qur'an (Tilawat)":
                entry_instance = TilawatEntry.from_dict(book_name, dict_to_edit)
            else:
                entry_instance = OtherEntry.from_dict(book_name, dict_to_edit)
            title = f"{book_name} ( {session} )"
            ProgressDisplay.display_entries(title, entry_instance.to_dict())

            next_choice = validate_number(
                f"\nOptions:\n1. Edit details\n2. Remove all entries for {title}\n\nYour Choice: ",
                1, 2)
            if next_choice == 1:
                editable_entries = [e for e in dict_to_edit if e not in ["Book", "Total Pages", "Total Aayat", "Total Ruku"]]
                cls.edit_subject(session, editable_entries, entry_instance)
                progress[subject][book_name][session] = entry_instance.to_dict()
            else:
                if validate_choice(
                    f"\nAre you sure you want to delete all entries for {title}?",
                    ["Y", "N"]) == "Y":
                    if session:
                        progress[subject][book_name].pop(session)
                        cls.pop_empty_dicts(progress, subject, book_name)
                    else:
                        progress[subject].pop(book_name)
                        cls.pop_empty_dicts(progress, subject)
                    StatsManager.clear_cache()

    @staticmethod
    def delete_progress(data: DataManager) -> None:
        del_menu_options = [
            "Delete today's progress", "Delete all recorded progress"
        ]
        what_to_del = validate_number(
            f"\nDelete Options:\n\n1. {del_menu_options[0]}\n2. {del_menu_options[1]}\n\nYour choice: ",
            1, 2)
        confirm_del = validate_choice(
            f"\nAre you sure you want to {del_menu_options[int(what_to_del) - 1]}?",
            ["Y", "N"])
        if confirm_del == "Y":
            if what_to_del == 1:
                data.delete_progress(DateManager.get_date_today())
            else:
                password = input("\nEnter Your Password: ")
                if PasswordManager.verify_password(password):
                    data.delete_progress("ALL_TIME")
                    StatsManager.clear_cache()
                    print("\nAll data deleted successfully!")
                else:
                    print("\nWRONG PASSWORD!")

class ProgressDisplay:

    @staticmethod
    def display_entries(heading: str, progress: dict) -> None:
        print(f"\n---------( {heading} )---------\n")
        for key, value in progress.items():
            print(f">>> {key}: {value}")

    @classmethod
    def display_entries_all(cls, progress: dict, day: str) -> None:
        print(f"\n<><><>--( Entries from {day} )--<><><>\n")
        if not progress:
            print(f">>> No entries recorded for {day}.")
            return
        for subject, books in progress.items():
            print(f"\n-----[<<( {subject} )>>]-----\n")
            for book, sessions in books.items():
                print(f"\n<><><>------[ {book} ]------<><><>\n")
                for session, session_details in sessions.items():
                    cls.display_entries(session, session_details)

