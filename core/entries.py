from unittest.mock import patch
from dataclasses import dataclass


@dataclass
class CommonEntry:
    subject: str
    book: str
    pages: str
    total_pages: int
    time_spent: str
    notes: str
    reading_mode: str
    revision: str

    def __str__(self):
        return f"{self.book}: {self.pages} pages, {self.time_spent} spent"

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
    def from_dict(cls, subject: str, book: str, data: dict, child_entries: tuple):
        return cls(
            subject,
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

    def to_dict(self) -> dict:
        data = {"Ruku (Para)": self.Ruku, "Total Ruku": self.total_Ruku}
        data.update(super().to_dict())
        return data

    @classmethod
    def from_dict(cls, subject: str, book: str, data: dict, child_entries: tuple = ()):
        return super().from_dict(subject, book, data, (data.get("Ruku (Para)", "0"), data.get("Total Ruku", 0)) + child_entries)
        

@dataclass
class TafseerEntry(TilawatEntry):
    Surah: str
    Ayah: str
    total_Aayat: int

    def to_dict(self) -> dict:
        data = {
            "Surah": self.Surah,
            "Ayah": self.Ayah,
            "Total Aayat": self.total_Aayat
        }
        data.update(super().to_dict())
        return data

    @classmethod
    def from_dict(cls, subject: str, book: str, data: dict):
        return super().from_dict(subject, book, data, (data.get("Surah", "0"), data.get("Ayah", "0"), data.get("Total Aayat", 0)))
        

@dataclass
class OtherEntry(CommonEntry):
    unit: str
    chapter: str 

    def to_dict(self) -> dict:
        data = {"Book": self.book, "Unit": self.unit, "Chapter": self.chapter}
        data.update(super().to_dict())
        return data

    @classmethod
    def from_dict(cls, subject: str, book: str, data: dict):
        return super().from_dict(subject, book, data, (data.get("Unit", "0"), data.get("Chapter", "N/A")))


# Tester
# if __name__ == "__main__":
#     inputs = [
#         "1",    # Unit 1
#         "1",    # Unit 2
#         "Chapter",  # chapter
#         "1",             # Page start
#         "5",             # Page end
#         "45",         # Time spent
#         "Important notes",  # Notes
#         "n",       # Reading mode
#         "n"            # Revision
#     ]

#     with patch("builtins.input", side_effect=inputs):
#         entry, msg = EntryFactory.make_other_entry()
#         if entry:
#             print("\n=== OtherEntry Test ===\n")
#             print(entry)
#             print(entry.to_dict())
#             print("\n=========================\n")
