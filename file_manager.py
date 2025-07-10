import json
from core_utils import DateManager

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
    def save_to_json(dict_entries: dict, file_path_json: str) -> None:
        try:
            with open(file_path_json, 'w') as file:
                json.dump(dict_entries, file, indent=4)
                print("\nProgress saved successfully!")
        except IOError as e:
            print(f"\nError: {e}")


class DataManager:
    def __init__(self) -> None:
        self.__FILE_JSON = './data/Learning_Journal.json'
        self.dict_main = FileManager.load_file(self.__FILE_JSON)
        self.progress_today = self.dict_main.get(DateManager.get_date_today(), {})

    @property
    def FILE_MD(self) -> str:
        return self.__FILE_JSON.replace(".json", ".md")

    def append_entry(self, subject: str, book_name: str, entry_dict: dict) -> None:
        self.progress_today.setdefault(subject, {}).setdefault(book_name, {})
        entry = f"Entry {DateManager.get_current_time()}"
        self.progress_today[subject][book_name][entry] = entry_dict       
        self.update_dict_main("", {})

    def update_dict_main(self, date: str, entries: dict) -> None:
        date = date or DateManager.get_date_today()
        entries = entries or self.progress_today
        if entries:
            self.dict_main[date] = entries
        elif date in self.dict_main and not self.dict_main[date]:
            self.dict_main.pop(date)

    def delete_progress(self, day: str):
        if day == "ALL_TIME":
            self.dict_main.clear()
        elif day in self.dict_main:
            self.dict_main.pop(day)

    def save_progress_to_files(self):
        FileManager.save_to_json(self.dict_main, self.__FILE_JSON)
        FileManager.save_entries_as_md(self.dict_main, self.FILE_MD)

