from core.data_manager import DataManager
from core.entries import EntryFactory, DataCarrier
from core.core_utils import Utilities, ProgressUtils
from cli.cli_prompt import CliPrompt
from cli.menu import Menu


class CliEntryPrompts:
    @staticmethod
    def get_entry_range(entry: str, limit=None) -> tuple:
        start_entry = CliPrompt.validate_number(f"\nEnter the starting {entry} number: ",
                                      max_val=limit)
        last_entry = CliPrompt.validate_number(f"Enter the last {entry} number: ",
                                     start_entry)
        return ProgressUtils.get_str_and_total(start_entry, last_entry)

    @staticmethod
    def get_time_spent(book: str):
        mins_spent = CliPrompt.validate_number(
            f"\nEnter the time spent on {book} in this session (in minutes): ")
        return Utilities.format_time(int(mins_spent))

    @staticmethod
    def get_notes():
        return input("\nAny additional notes? (optional): ").strip() or "N/A"

    @staticmethod
    def get_revision() -> str:
        if CliPrompt.validate_choice(
            f"\nDid you revise anything in this session?",
            ["Y", "N"]) == "N":
            return "No"

        return input(
            f"\nPlease enter the revision details (optional): "
        ).strip() or "Revised previous content"

    @staticmethod
    def get_reading_mode() -> str:
        return "Sequential" if CliPrompt.validate_choice(
            "\nAre you reading sequentially?", ["Y", "N"]) == "Y" else "Random"

    @staticmethod
    def get_chapter():
        return input("\nEnter chapter name (optional): ").strip() or "N/A"


class CliDataCollector:
    """Uses CliEntryPrompts methods to collect input and store the data."""
    def __init__(self) -> None:
        self.carrier = DataCarrier()

    def collect_common_data(self, context: dict):
        self.carrier.common_data["subject"] = context["subject"]
        self.carrier.common_data["book"] = context["book"]
        self.carrier.common_data["pages"], self.carrier.common_data["total_pages"] = CliEntryPrompts.get_entry_range("page")
        self.carrier.common_data["time_spent"] = CliEntryPrompts.get_time_spent(context["book"])
        self.carrier.common_data["notes"] = CliEntryPrompts.get_notes()
        self.carrier.common_data["reading_mode"] = CliEntryPrompts.get_reading_mode()
        self.carrier.common_data["revision"] = CliEntryPrompts.get_revision()    
    
    def collect_Quran_data(self, context: dict):
        Para_number = CliEntryPrompts.get_entry_range("Para", 30)[0]
        context["book"] = f"Para no. {Para_number}"
        if "Tafseer" in context["subject"]:
            self.carrier.data["Surah"] = CliEntryPrompts.get_entry_range("Surah", 114)[0]
            self.carrier.data["Ayah"], self.carrier.data["total_Aayat"] = CliEntryPrompts.get_entry_range("Ayah")
        self.carrier.data["Ruku"], self.carrier.data["total_Ruku"] = CliEntryPrompts.get_entry_range("Ruku (Para)")
        self.collect_common_data(context)
        return True, ""
    
    def collect_other_data(self, context: dict):
        self.carrier.data["unit"] = CliEntryPrompts.get_entry_range("unit")[0]
        self.carrier.data["chapter"] = CliEntryPrompts.get_chapter()
        self.collect_common_data(context)
        return True, ""


class CliWorkflow:
    @staticmethod
    def log_Quran_progress(data: DataManager, method: str = "Tafseer") -> None:
        method_full = f"Al-Qur'an ({method})"
        print(f"\n<><><>__( {method_full} )__<><><>")
        while True:
            data_collector = CliDataCollector()
            valid, msg = data_collector.collect_Quran_data({"subject": method_full})                
            if not valid:
                print(msg)
                return
            entry = EntryFactory.make_Quran_entry(data_collector.carrier)
            data.add_entry(entry)
            if CliPrompt.validate_choice(
                f"\nDo you want to add another {method_full} entry to the log?", ["Y", "N"]) == "N":
                return

    @staticmethod
    def choose_subject(data: DataManager) -> tuple:
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
            if subject:
                return (subject, data.all_time_subjects.get(subject))
            print("\nSubject cannot be blank.")

    @staticmethod
    def choose_book(subject: str, books_list: list) -> str:
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
        subject, books_list = cls.choose_subject(data)
        print(f"\n<><><>__(<<[ {subject} ]>>)__<><><>\n")
        book = cls.choose_book(subject, books_list)
        print(f"\n<><><>__(<< {book} >>)__<><><>\n")
        data_collector = CliDataCollector()
        valid, msg = data_collector.collect_other_data({"subject": subject, "book": book})
        if not valid:
            print(msg)
            return
        entry = EntryFactory.make_other_entry(data_collector.carrier)
        data.add_entry(entry)

    @classmethod
    def log_other_progress(cls, data: DataManager) -> None:
        while True:
            cls.get_and_add_progress(data)
            if CliPrompt.validate_choice(
                "\nWould you like to add another entry to today's log?",
                ["Y", "N"]) == "N":
                return
