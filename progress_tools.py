import random
from copy import deepcopy
from entries import TafseerEntry, TilawatEntry, OtherEntry
from file_manager import DataManager
from core_utils import (Validation, Utilities, validate_choice,
                        validate_number, Menu)


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
        def get_subject_books(cls, data: DataManager) -> tuple:
            if data.all_time_subjects:
                subjects_list = [
                    "Add a New Subject",
                    *data.all_time_subjects.keys()
                ]
                subjects_menu = Menu(subjects_list, "Select a Subject")
                user_choice = subjects_menu.display_menu(show_exit=False)
                if user_choice != 1:
                    subject = subjects_list[user_choice - 1] # type: ignore
                    return subject, data.all_time_subjects[subject]
            while True:
                subject = input("\nEnter a subject name: ").strip()
                subject = "Qur'an" if subject == "Al-Qur'an (Tafseer)" else subject
                if subject:
                    return subject, None
                print("\nSubject cannot be blank.")

        @classmethod
        def get_book_name(cls, subject: str, books_list: list) -> str:
            if books_list:
                books_menu_list = ["Add a New Book", *books_list]
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
            subject, books_list = cls.get_subject_books(data)
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
    @classmethod
    def update_entry_pages(cls, details, entry_pages, stats, add = False):
        if not add:
            stats[details[0]][details[1]]["Pages"] -= entry_pages
        else:
            stats[details[0]][details[1]]["Pages"] += entry_pages

    @classmethod
    def update_entry_minutes(cls, details, entry_time_spent, stats, add = False):
        temp_total_minutes = Utilities.convert_time_to_mins(stats[details[0]][details[1]]["Time Spent"])
        if not add:
            temp_total_minutes -= Utilities.convert_time_to_mins(entry_time_spent)
        else:
            temp_total_minutes += Utilities.convert_time_to_mins(entry_time_spent)
        stats[details[0]][details[1]]["Time Spent"] = Utilities.format_time(temp_total_minutes)

    @classmethod
    def update_stats(cls, details: tuple, entry_instance, stats: dict, field: str="", date: str=""):
        if field == "Pages":
            cls.update_entry_pages(details, entry_instance.total_pages, stats)
            entry_instance.edit_field(field)
            cls.update_entry_pages(details, entry_instance.total_pages, stats, add=True)
        elif field == "Time Spent":
            cls.update_entry_minutes(details, entry_instance.time_spent, stats)
            entry_instance.edit_field(field)
            cls.update_entry_minutes(details, entry_instance.time_spent, stats, add=True)
        else:
            cls.update_entry_pages(details, entry_instance.total_pages, stats)
            cls.update_entry_minutes(details, entry_instance.time_spent, stats)
            stats[details[0]][details[1]]["Entry Dates"].remove(date)
            
    @classmethod
    def edit_subject(cls, details: tuple, editable_entries: list, entry_instance, data: DataManager):
        entries_menu = Menu(editable_entries, details[2])
        while True:
            user_choice, exit_option = entries_menu.display_menu() # type: ignore
            if user_choice == exit_option:
                return
            field = editable_entries[user_choice - 1]
            if field in ["Pages", "Time Spent"]:
                stats = deepcopy(data.stats)
                cls.update_stats(details, entry_instance, stats, field)
                data.update_stats(stats)
            else:
                entry_instance.edit_field(field)
            print(f"\n{field} updated!\n")
        
    @classmethod
    def edit_progress(cls, progress: dict, data: DataManager, date: str) -> None:
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
            details = (subject, book_name, session)
            if next_choice == 1:
                editable_entries = [e for e in dict_to_edit if e not in ["Book", "Total Pages", "Total Aayat", "Total Ruku"]]
                cls.edit_subject(details, editable_entries, entry_instance, data)
                progress[subject][book_name][session] = entry_instance.to_dict()
            else:
                if validate_choice(
                    f"\nAre you sure you want to delete all entries for {title}?",
                    ["Y", "N"]) == "Y":
                    progress[subject][book_name].pop(session)
                    Utilities.pop_empty_dicts(progress, subject, book_name)
                    stats = deepcopy(data.stats)
                    cls.update_stats(details, entry_instance, stats, date=date)                    
                    data.update_stats(stats)

    
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

