from copy import deepcopy
from core.data_manager import DataManager
from core.entries import TafseerEntry, TilawatEntry, OtherEntry
from core.core_utils import Utilities
from cli.menu import Menu
from cli.cli_workflow import CliEntryPrompts
from cli.cli_display import CliProgressDisplay
from cli.cli_prompt import CliPrompt

class CliEntryEditor:
    def __init__(self, entry):
        self.entry = entry
    
    def edit_field(self, field: str) -> None:
        edit_map = {
            "Surah": lambda: setattr(self.entry, "Surah", CliEntryPrompts.get_entry_range("Surah", 114)[0]),
            "Ayah": lambda: (lambda v: setattr(self.entry, "Ayah", v[0]) or setattr(self.entry, "total_Aayat", v[1]))(CliEntryPrompts.get_entry_range("Ayah")),
            "Ruku (Para)": lambda: (lambda v: setattr(self.entry, "Ruku", v[0]) or setattr(self.entry, "total_Ruku", v[1]))(CliEntryPrompts.get_entry_range("Ruku (Para)")),
            "Unit": lambda: setattr(self.entry, "unit", CliEntryPrompts.get_entry_range("unit")[0]),
            "Chapter": lambda: setattr(self.entry, "chapter", CliEntryPrompts.get_chapter()),
            "Page": lambda: (lambda v: setattr(self.entry, "pages", v[0]) or setattr(self.entry, "total_pages", v[1]))(CliEntryPrompts.get_entry_range("page")),
            "Time Spent": lambda: setattr(self.entry, "time_spent", CliEntryPrompts.get_time_spent(self.entry.book)),
            "Notes": lambda: setattr(self.entry, "notes", CliEntryPrompts.get_notes()),
            "Reading Mode": lambda: setattr(self.entry, "reading_mode", CliEntryPrompts.get_reading_mode()),
            "Revision": lambda: setattr(self.entry, "revision", CliEntryPrompts.get_revision()),
        }
        if field in edit_map:
            edit_map[field]()

            
class CliProgressEditor:
    @staticmethod
    def pop_empty_dicts(dict_: dict, dict1: str, dict2: str) -> None:
        if not dict_[dict1][dict2]:
            dict_[dict1].pop(dict2)
            if not dict_[dict1]:
                dict_.pop(dict1)

    @classmethod
    def update_entry_pages(cls, details, entry_pages, stats, add = False):
        if add:
            stats[details[0]][details[1]]["Pages"] += entry_pages
        else:
            stats[details[0]][details[1]]["Pages"] -= entry_pages

    @classmethod
    def update_entry_minutes(cls, details, entry_time_spent, stats, add = False):
        temp_total_minutes = Utilities.convert_time_to_mins(stats[details[0]][details[1]]["Time Spent"])
        if add:
            temp_total_minutes += Utilities.convert_time_to_mins(entry_time_spent)
        else:
            temp_total_minutes -= Utilities.convert_time_to_mins(entry_time_spent)
        stats[details[0]][details[1]]["Time Spent"] = Utilities.format_time(temp_total_minutes)

    @classmethod
    def update_stats(cls, details: tuple, editor, stats: dict, field: str="", date: str=""):
        if field == "Page":
            cls.update_entry_pages(details, editor.entry.total_pages, stats)
            editor.edit_field(field)
            cls.update_entry_pages(details, editor.entry.total_pages, stats, add=True)
        elif field == "Time Spent":
            cls.update_entry_minutes(details, editor.entry.time_spent, stats)
            editor.edit_field(field)
            cls.update_entry_minutes(details, editor.entry.time_spent, stats, add=True)
        else:
            cls.update_entry_pages(details, editor.entry.total_pages, stats)
            cls.update_entry_minutes(details, editor.entry.time_spent, stats)
            stats[details[0]][details[1]]["Entry Dates"].remove(date)
            
    @classmethod
    def edit_subject(cls, details: tuple, editable_entries: list, entry_instance, data: DataManager):
        editor = CliEntryEditor(entry=entry_instance)
        entries_menu = Menu(editable_entries, details[2])
        while True:
            user_choice, exit_option = entries_menu.display_menu() # type: ignore
            if user_choice == exit_option:
                return
            field = editable_entries[user_choice - 1]
            if field in ["Page", "Time Spent"]:
                stats = deepcopy(data.stats)
                cls.update_stats(details, editor, stats, field)
                data.update_stats(stats)
            else:
                editor.edit_field(field)
            print(f"\n{field} updated!\n")
        
    @classmethod
    def edit_progress(cls, progress: dict, data: DataManager, date: str) -> None:
        while True:
            if not progress:
                print("\nNo progress to edit.")
                return            
            subject = CliPrompt.choose_key(progress, "Subject")
            if not subject:
                if CliPrompt.validate_choice("\nBack to Main Menu? ", ["Y", "N"]) == "Y":
                    return
            book_title = "Para" if subject in ["Al-Qur'an (Tilawat)", "Al-Qur'an (Tafseer)"] else "Book"
            book_name = CliPrompt.choose_key(progress[subject], book_title)
            if not book_name:
                continue                
            session = CliPrompt.choose_key(progress[subject][book_name], "Session")
            if not session:
                continue                
            dict_to_edit = progress[subject][book_name][session]
            if subject == "Al-Qur'an (Tafseer)":
                entry_instance = TafseerEntry.from_dict(subject, book_name, dict_to_edit)
            elif subject == "Al-Qur'an (Tilawat)":
                entry_instance = TilawatEntry.from_dict(subject, book_name, dict_to_edit)
            else:
                entry_instance = OtherEntry.from_dict(subject, book_name, dict_to_edit)
            title = f"{book_name} ( {session} )"
            CliProgressDisplay.display_entries(title, entry_instance.to_dict())
            next_choice = CliPrompt.validate_number(
                f"\nOptions:\n1. Edit details\n2. Remove all entries for {title}\n\nYour Choice: ",
                1, 2)
            details = (subject, book_name, session)
            if next_choice == 1:
                editable_entries = [e for e in dict_to_edit if e not in ["Book", "Total Pages", "Total Aayat", "Total Ruku"]]
                cls.edit_subject(details, editable_entries, entry_instance, data)
                progress[subject][book_name][session] = entry_instance.to_dict()
            else:
                if CliPrompt.validate_choice(
                    f"\nAre you sure you want to delete all entries for {title}?",
                    ["Y", "N"]) == "Y":
                    progress[subject][book_name].pop(session)
                    cls.pop_empty_dicts(progress, subject, book_name)
                    stats = deepcopy(data.stats)
                    cls.update_stats(details, entry_instance, stats, date=date)                    
                    data.update_stats(stats)