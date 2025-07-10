from unittest.mock import patch
from dataclasses import dataclass
from core_utils import Validation

@dataclass
class CommonEntry:
    book: str
    pages: str
    total_pages: int
    time_spent: str
    notes: str
    reading_mode: str
    revision: str

    @staticmethod
    def get_pages():
        return Validation.get_first_and_last("page")

    @staticmethod
    def get_time_spent(book):
        return Validation.get_time_spent(book)

    @staticmethod
    def get_notes():
        return input("\nAny additional notes? (optional): ").strip() or "N/A"

    @staticmethod
    def get_reading_mode():
        return Validation.get_reading_mode()

    @staticmethod
    def get_revision():
        return Validation.get_revision()

    def __str__(self):
        return f"{self.book}: {self.pages} pages, {self.time_spent} spent"

    def edit_field(self, field: str) -> None:
        edit_map = {
            "Page": lambda: (lambda val: setattr(self, "pages", val[0]) or setattr(self, "total_pages", val[1]))(self.get_pages()),
            "Time Spent": lambda: setattr(self, "time_spent", self.get_time_spent(self.book)),
            "Notes": lambda: setattr(self, "notes", self.get_notes()),
            "Reading Mode": lambda: setattr(self, "reading_mode", self.get_reading_mode()),
            "Revision": lambda: setattr(self, "revision", self.get_revision()),
        }
        if field in edit_map:
            edit_map[field]()

    def to_dict(self) -> dict:
        return {
            "Page": self.pages,
            "Total Pages": self.total_pages,
            "Time Spent": self.time_spent,
            "Notes": self.notes,
            "Reading Mode": self.reading_mode,
            "Revision": self.revision
        }

    @classmethod
    def from_user_input(cls, book: str, child_entries: tuple = ()) :
        pages, total_pages = cls.get_pages()
        return cls(book, pages, total_pages, cls.get_time_spent(book), cls.get_notes(),
                cls.get_reading_mode(), cls.get_revision(), *child_entries)

    @classmethod
    def from_dict(cls, book: str, data: dict, child_entries: tuple):
        return cls(
            book,
            data.get("Page", '0'),
            data.get("Total Pages", 0),
            data.get("Time Spent", 'N/A'),
            data.get("Notes", 'N/A'),
            data.get("Reading Mode", 'N/A'),
            data.get("Revision", 'N/A'),
            *child_entries
        )


@dataclass
class TilawatEntry(CommonEntry):
    Ruku: str
    total_Ruku: int

    @staticmethod
    def get_Ruku():
        return Validation.get_first_and_last("Ruku (Para)")

    def edit_field(self, field: str) -> None:
        if field == "Ruku (Para)":
            self.Ruku, self.total_Ruku = self.get_Ruku()
        else:
            super().edit_field(field)

    def to_dict(self) -> dict:
        data = {"Ruku (Para)": self.Ruku, "Total Ruku": self.total_Ruku}
        data.update(super().to_dict())
        return data

    @classmethod
    def from_user_input(cls, book: str, child_entries: tuple = ()):
        return super().from_user_input(book, cls.get_Ruku() + child_entries)

    @classmethod
    def from_dict(cls, book: str, data: dict, child_entries: tuple = ()):
        return super().from_dict(book, data, (data.get("Ruku (Para)", "0"), data.get("Total Ruku", 0)) + child_entries)
        
@dataclass
class TafseerEntry(TilawatEntry):
    Surah_number: str
    Ayah: str
    total_Aayat: int

    @staticmethod
    def get_Surah():
        return Validation.get_first_and_last("Surah", 114)

    @staticmethod
    def get_Aayat():
        return Validation.get_first_and_last("Ayah")

    def edit_field(self, field: str) -> None:
        if field == "Surah":
            self.Surah_number, _ = self.get_Surah()
        elif field == "Ayah":
            self.Ayah, self.total_Aayat = self.get_Aayat()
        else:
            super().edit_field(field)

    def to_dict(self) -> dict:
        data = {
            "Surah": self.Surah_number,
            "Ayah": self.Ayah,
            "Total Aayat": self.total_Aayat
        }
        data.update(super().to_dict())
        return data

    @classmethod
    def from_user_input(cls, book: str):
        return super().from_user_input(book, (cls.get_Surah()[0], *cls.get_Aayat())) 

    @classmethod
    def from_dict(cls, book: str, data: dict):
        return super().from_dict(book, data, (data.get("Surah", "0"), data.get("Ayah", "0"), data.get("Total Aayat", 0)))
        
@dataclass
class OtherEntry(CommonEntry):
    unit: str
    chapter: str

    @staticmethod
    def get_unit():
        return Validation.get_first_and_last("unit")

    @staticmethod
    def get_chapter():
        return input("\nEnter chapter name (optional): ").strip() or "N/A"

    def edit_field(self, field: str) -> None:
        if field == "Unit":
            self.unit, _ = self.get_unit()
        elif field == "Chapter":
            self.chapter = self.get_chapter()
        else:
            super().edit_field(field)

    def to_dict(self) -> dict:
        data = {"Book": self.book, "Unit": self.unit, "Chapter": self.chapter}
        data.update(super().to_dict())
        return data

    @classmethod
    def from_user_input(cls, book: str):
        return super().from_user_input(book, (cls.get_unit()[0], cls.get_chapter()))

    @classmethod
    def from_dict(cls, book: str, data: dict):
        return super().from_dict(book, data, (data.get("Unit", "0"), data.get("Chapter", "N/A")))


# Tester
if __name__ == "__main__":
    inputs = [
        "1",             # Page start
        "5",             # Page end
        "45",         # Time spent
        "Important notes",  # Notes
        "n",       # Reading mode
        "n"            # Revision
    ]

    with patch("builtins.input", side_effect=inputs):
        entry = CommonEntry.from_user_input("My Book")
        print("\n=== Common Entry Test ===\n")
        print(entry)
        print(entry.to_dict())
        print("\n=========================\n")
