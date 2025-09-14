from unittest.mock import patch
from dataclasses import dataclass
from core_utils import CliInputCollector


class DataCarrier:
    def __init__(self):
        self.common_raw_data: dict = {}
        self.raw_data: dict = {}
        self.common_data: dict = {}
        self.data: dict = {}


class CliDataCollector:
    """Uses CliInputCollector methods to collect input and store the data."""
        
    @staticmethod    
    def collect_common_data(carrier: DataCarrier, args: dict):
        carrier.common_data["book"] = args["book"]
        carrier.common_data["pages"], carrier.common_data["total_pages"] = CliInputCollector.get_entry_range("page")
        carrier.common_data["time_spent"] = CliInputCollector.get_time_spent(args["book"])
        carrier.common_data["notes"] = CliInputCollector.get_notes()
        carrier.common_data["reading_mode"] = CliInputCollector.get_reading_mode()
        carrier.common_data["revision"] = CliInputCollector.get_revision()    
    
    @classmethod
    def collect_Quran_data(cls, carrier: DataCarrier, args: dict):
        if "Tafseer" in args["book"]:
            carrier.data["Surah"] = CliInputCollector.get_entry_range("Surah", 114)[0]
            carrier.data["Ayah"], carrier.data["total_Aayat"] = CliInputCollector.get_entry_range("Ayah")
        carrier.data["Ruku"], carrier.data["total_Ruku"] = CliInputCollector.get_entry_range("Ruku (Para)")
        cls.collect_common_data(carrier, args)
        return True, ""
    
    @classmethod
    def collect_other_data(cls, carrier: DataCarrier, args: dict):
        carrier.data["unit"] = CliInputCollector.get_entry_range("unit")[0]
        carrier.data["chapter"] = CliInputCollector.get_chapter()
        cls.collect_common_data(carrier, args)
        return True, ""


class EntryFactory:
    """Uses a DataCollector instance to gather and store data, then creates and returns an entry object."""
    
    @staticmethod
    def make_Quran_entry(args: dict, data_collector=CliDataCollector):
        carrier = DataCarrier()
        valid, msg = data_collector.collect_Quran_data(carrier, args)
        if not valid:
            return None, msg
        if "Tafseer" in args["book"]:
            return TafseerEntry(**carrier.common_data, **carrier.data), "Success"
        else:
            return TilawatEntry(**carrier.common_data, **carrier.data), "Success"

    @staticmethod
    def make_other_entry(args: dict, data_collector=CliDataCollector):
        carrier = DataCarrier()
        valid, msg = data_collector.collect_other_data(carrier, args)
        if not valid:
            return None, msg
        return OtherEntry(**carrier.common_data, **carrier.data), "Success"


class CliEntryEditor:
    def __init__(self, entry):
        self.entry = entry
    
    def edit_field(self, field: str) -> None:
        edit_map = {
            "Surah": lambda: setattr(self.entry, "Surah_number", CliInputCollector.get_entry_range("Surah", 114)[0]),
            "Ayah": lambda: (lambda v: setattr(self.entry, "Ayah", v[0]) or setattr(self.entry, "total_Aayat", v[1]))(CliInputCollector.get_entry_range("Ayah")),
            "Ruku (Para)": lambda: (lambda v: setattr(self.entry, "Ruku", v[0]) or setattr(self.entry, "total_Ruku", v[1]))(CliInputCollector.get_entry_range("Ruku (Para)")),
            "Unit": lambda: setattr(self.entry, "unit", CliInputCollector.get_entry_range("unit")[0]),
            "Chapter": lambda: setattr(self.entry, "chapter", CliInputCollector.get_chapter()),
            "Page": lambda: (lambda v: setattr(self.entry, "pages", v[0]) or setattr(self.entry, "total_pages", v[1]))(CliInputCollector.get_entry_range("page")),
            "Time Spent": lambda: setattr(self.entry, "time_spent", CliInputCollector.get_time_spent(self.entry.book)),
            "Notes": lambda: setattr(self.entry, "notes", CliInputCollector.get_notes()),
            "Reading Mode": lambda: setattr(self.entry, "reading_mode", CliInputCollector.get_reading_mode()),
            "Revision": lambda: setattr(self.entry, "revision", CliInputCollector.get_revision()),
        }
        if field in edit_map:
            edit_map[field]()


@dataclass
class CommonEntry:
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

    def to_dict(self) -> dict:
        data = {"Ruku (Para)": self.Ruku, "Total Ruku": self.total_Ruku}
        data.update(super().to_dict())
        return data

    @classmethod
    def from_dict(cls, book: str, data: dict, child_entries: tuple = ()):
        return super().from_dict(book, data, (data.get("Ruku (Para)", "0"), data.get("Total Ruku", 0)) + child_entries)
        

@dataclass
class TafseerEntry(TilawatEntry):
    Surah_number: str
    Ayah: str
    total_Aayat: int

    def to_dict(self) -> dict:
        data = {
            "Surah": self.Surah_number,
            "Ayah": self.Ayah,
            "Total Aayat": self.total_Aayat
        }
        data.update(super().to_dict())
        return data

    @classmethod
    def from_dict(cls, book: str, data: dict):
        return super().from_dict(book, data, (data.get("Surah", "0"), data.get("Ayah", "0"), data.get("Total Aayat", 0)))
        

@dataclass
class OtherEntry(CommonEntry):
    unit: str
    chapter: str 

    def to_dict(self) -> dict:
        data = {"Book": self.book, "Unit": self.unit, "Chapter": self.chapter}
        data.update(super().to_dict())
        return data

    @classmethod
    def from_dict(cls, book: str, data: dict):
        return super().from_dict(book, data, (data.get("Unit", "0"), data.get("Chapter", "N/A")))


# Tester
if __name__ == "__main__":
    inputs = [
        "1",    # Unit 1
        "1",    # Unit 2
        "Chapter",  # chapter
        "1",             # Page start
        "5",             # Page end
        "45",         # Time spent
        "Important notes",  # Notes
        "n",       # Reading mode
        "n"            # Revision
    ]

    with patch("builtins.input", side_effect=inputs):
        entry, msg = EntryFactory.make_other_entry({"book":"My Book"})
        if entry:
            print("\n=== OtherEntry Test ===\n")
            print(entry)
            print(entry.to_dict())
            print("\n=========================\n")
