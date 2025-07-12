import json
from core_utils import DateManager, Utilities

class FileManager:
    @staticmethod
    def load_file(file_path_json: str) -> dict:
        try:
            with open(file_path_json, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @staticmethod
    def save_entries_as_md(dict_entries: dict, file_path_md: str) -> None:
        """
        Save learning entries to a Markdown file with formatted sections for Qur'an and other subjects.

        Args:
            dict_entries (dict): Dictionary containing learning entries data
            file_path_md (str): string containing MD file path 
        """        
        try:
            with open(file_path_md, 'w') as file:
                if not dict_entries:
                    file.write("")
                else:
                    for date, record in dict_entries.items():
                        file.write(f"# {date}\n\n")
                        for subject, books in record.items():
                            file.write(f"## {subject}\n\n")
                            for book_name, sessions in books.items():                                    
                                file.write(f"### {book_name}\n")
                                for session, session_details in sessions.items():
                                    file.write(f"\n#### {session}\n\n")
                                    for key, value in session_details.items():
                                        file.write(f"- **{key}:** {value}\n")
                                file.write("\n")

                        # Add daily summary if needed
                        file.write("---\n\n")  # Horizontal rule for separation between dates
        except IOError:
            print(
                "\nCouldn't create markdown file. Please check file permissions or disk space.\n"
            )

    @staticmethod
    def save_to_json(dict_: dict, file_path_json: str) -> None:
        try:
            with open(file_path_json, 'w') as file:
                json.dump(dict_, file, indent=4)
                print("\nProgress saved successfully!")
        except IOError as e:
            print(f"\nError: {e}")


class DataManager:
    def __init__(self) -> None:
        self.__FILE_JSON = './data/learning_data.json'
        self.date_today = DateManager.get_date_today()
        self.data = FileManager.load_file(self.__FILE_JSON)
        self.entry_log = self.data.get("Entry Log", {})
        self.all_time_subjects = self.data.get("All Time Subjects", {})
        self.stats = self.data.get("Statistics", {})
        self.progress_today = self.entry_log.get(self.date_today, {})

    @property
    def FILE_MD(self) -> str:
        return "./data/Journal.md"

    @property
    def file_dict(self) -> dict:
        return {
                    "Entry Log": self.entry_log,
                    "All Time Subjects": self.all_time_subjects,
                    "Statistics": self.stats
                }

    def append_entry(self, subject: str, book_name: str, entry_dict: dict) -> None:
        self.progress_today.setdefault(subject, {}).setdefault(book_name, {})
        entry = f"Entry {DateManager.get_current_time()}"
        self.progress_today[subject][book_name][entry] = entry_dict
        self.add_to_cache(subject, book_name)
        self.add_stats(subject, book_name, entry_dict)
        self.update_entry_log("", {})

    def add_to_cache(self, subject, book_name):
        if subject not in ["Al-Qur'an (Tafseer)", "Al-Qur'an (Tilawat)"]:
            self.all_time_subjects.setdefault(subject, [])
            self.all_time_subjects = dict(sorted(self.all_time_subjects.items(), key=lambda item: item[0].lower()))
            if book_name not in self.all_time_subjects[subject]:
                self.all_time_subjects[subject].append(book_name)
                self.all_time_subjects[subject].sort()

    def add_stats(self, subject, book_name, entry_dict: dict):
        self.stats.setdefault(subject, {}).setdefault(book_name, {})
        self.stats = dict(sorted(self.stats.items(), key=lambda item: item[0].lower()))
        self.stats[subject] = dict(sorted(self.stats[subject].items(), key=lambda item: item[0].lower()))
        self.stats[subject][book_name].setdefault("Pages", 0)
        self.stats[subject][book_name].setdefault("Time Spent", "")
        self.stats[subject][book_name].setdefault("Entry Dates", [])

        self.stats[subject][book_name]["Pages"] += entry_dict["Total Pages"]

        all_time_minutes = Utilities.convert_time_to_mins(self.stats[subject][book_name]["Time Spent"])
        entry_minutes = Utilities.convert_time_to_mins(entry_dict["Time Spent"])
        self.stats[subject][book_name]["Time Spent"] = Utilities.format_time(all_time_minutes + entry_minutes)

        if self.date_today not in self.stats[subject][book_name]["Entry Dates"]:
            self.stats[subject][book_name]["Entry Dates"].append(self.date_today)

    def update_cache(self, cache: dict) -> None:
        self.all_time_subjects = cache
        
    def update_stats(self, stats: dict) -> None:
        self.stats = stats

    def update_entry_log(self, date: str, entries: dict) -> None:
        date = date or DateManager.get_date_today()
        entries = entries or self.progress_today
        if entries:
            self.entry_log[date] = entries
        elif date in self.entry_log and not self.entry_log[date]:
            self.entry_log.pop(date)

    def delete_stats(self, day: str):
        from progress_tools import ProgressEditor
        for subject, subject_entries in self.entry_log[day].items():
            for book, book_entries in subject_entries.items():
                if day in self.stats[subject][book]["Entry Dates"]:
                    self.stats[subject][book]["Entry Dates"].remove(day)
                    for entry_details in book_entries.values():
                        ProgressEditor.update_entry_pages((subject, book), entry_details["Total Pages"], self.stats)
                        ProgressEditor.update_entry_minutes((subject, book), entry_details["Time Spent"], self.stats)
                    
    def delete_progress(self, day: str):
        if day == "ALL_TIME":
            self.entry_log.clear()
            self.stats.clear()
        elif day in self.entry_log:
            self.delete_stats(day)
            self.entry_log.pop(day)

    def save_progress_to_files(self):
        FileManager.save_to_json(self.file_dict, self.__FILE_JSON)
        FileManager.save_entries_as_md(self.entry_log, self.FILE_MD)

