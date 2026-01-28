import os, json, zipfile
from core.core_services import DateManager
from core.entries import CommonEntry
from core.exceptions import DataCorruptionError


class FileManager:
    @staticmethod
    def load_file(file_path_json: str):
        try:
            with open(file_path_json, 'r', encoding="utf-8") as file:
                return json.load(file)
        except (FileNotFoundError):
            return {}
        except json.JSONDecodeError as e:
            raise DataCorruptionError(file_path=file_path_json) from e

    @staticmethod
    def save_to_md(dict_entries: dict, file_path_md: str):
        """
        Save learning entries to a Markdown file with formatted sections for Qur'an and other subjects.

        Args:
            dict_entries (dict): Dictionary containing learning entries data
            file_path_md (str): string containing MD file path 
        """        
        try:
            with open(file_path_md, 'w', encoding="utf-8") as file:
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
            return True, "Saved successfully"
        except Exception as e:
            return False, str(e)

    @staticmethod
    def save_to_json(dict_: dict, file_path_json: str):
        try:
            with open(file_path_json, 'w', encoding="utf-8") as file:
                json.dump(dict_, file, indent=4, ensure_ascii=False)
            return True, "Saved successfully"
        except Exception as e:
            return False, str(e)


class DataManager:
    def __init__(self, path_json: str, path_md: str) -> None:
        self._path_json = path_json
        self.path_md = path_md
        self.data = FileManager.load_file(self._path_json)
        self.extract_data()
        self.sync_data_today()

    @property
    def file_dict(self) -> dict:
        return {
                "Entry Log": self.entry_log,
                "All Time Subjects": self.all_time_subjects,
                "Statistics": self.stats
            }
    
    def extract_data(self):
        self.entry_log = self.data.get("Entry Log", {})
        self.all_time_subjects = self.data.get("All Time Subjects", {})
        self.stats = self.data.get("Statistics", {})

    def update_date_today(self):
        self.date_today = DateManager.get_date_today()

    def sync_data_today(self):
        self.update_date_today()
        self.progress_today = self.entry_log.get(self.date_today, {})

    def add_entry(self, entry: CommonEntry) -> None:
        self.sync_data_today()
        entry_time = f"Entry {DateManager.get_current_time()}"
        self.progress_today.setdefault(entry.subject, {}).setdefault(entry.book, {})
        self.progress_today[entry.subject][entry.book][entry_time] = entry.to_dict()
        self.update_entry_log("", {})

    def update_cache(self, cache: dict) -> None:
        self.all_time_subjects = cache
        
    def update_stats(self, stats: dict) -> None:
        self.stats = stats

    def update_entry_log(self, date: str, entries: dict) -> None:
        date = date or self.date_today
        entries = entries or self.progress_today
        if entries:
            self.entry_log[date] = entries
        elif date in self.entry_log and not self.entry_log[date]:
            self.entry_log.pop(date)
    
    def get_books_list(self, subject: str):
        return self.all_time_subjects.get(subject, [])

    def get_all_subjects(self):
        return self.all_time_subjects.keys()

    def get_entries_from_date(self, date: str):
        return self.entry_log.get(date, {})
                    
    def delete_data(self, date: str = "None", delete_all_progress: bool = False):
        """"This method is not to be used directly. Use DeleteController's methods to access this."""

        if delete_all_progress:
            self.entry_log.clear()
            self.stats.clear()
            return True, "All data deleted successfully!"
        elif date in self.entry_log:
            self.entry_log.pop(date)
            return True, f"All entries from {date if date != self.date_today else f'today ({date})'} deleted successfully!"
            
        return False, f"No entries recorded for {date if date != self.date_today else f'today ({date})'}."
        
    def save_data_to_files(self) -> int:
        if not FileManager.save_to_json(self.file_dict, self._path_json)[0]:
            return 1
        if not FileManager.save_to_md(self.entry_log, self.path_md)[0]:
            return 2
        return 0

    def save_md_as(self, file_path: str):
        self.path_md = file_path
        FileManager.save_to_json(self.file_dict, self._path_json)
        return FileManager.save_to_md(self.entry_log, self.path_md)

    def backup_data(self, backup_dir: str):
        path_backup = os.path.join(backup_dir, f"learning_backup_{DateManager.get_timestamp()}.zip")
        try:
            with zipfile.ZipFile(path_backup, "w", zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(self._path_json, arcname="learning_data.json")
        except OSError as e:
            return False, f"Backup failed: {e}"
        return True, "Backup successful!"

    def restore_data(self, zip_path: str) -> tuple:
        try:
            with zipfile.ZipFile(zip_path, "r") as zipf:
                data_bytes = zipf.read("learning_data.json")
                data = json.loads(data_bytes.decode("utf-8"))
                if not data: 
                    return False, "Backup file is empty."
                self.data = data
                self.extract_data()
        except zipfile.BadZipFile as e:
            return False, f"Invalid ZIP file: {e}"
        except (KeyError, OSError) as e:
            return False, "Backup archive does not contain valid data."
        except json.JSONDecodeError as e:
            return False, f"Data Corrupted: {e}"
        return True, "Restoration successful!"

