from core.core_services import DataCarrier, CoreHelpers, ProgressRules
from core.entries import TafseerEntry, TilawatEntry, OtherEntry


class PairFieldsValidation:
    @staticmethod
    def both_fields_empty(field_name: str, field1, field2):
        if not field1 and not field2:
            return False, f"Can't leave {field_name} fields empty."
        return True, ""

    @staticmethod
    def are_fields_in_order(field_name: str, field1, field2):
        if field1 and field2 and not field1 <= field2:
            return False, f"{field_name}: 'From' field must be smaller than 'To' field"
        return True, ""

    @classmethod
    def verify_range_fields(cls, field_name: str, field1, field2):
        valid, msg = cls.both_fields_empty(field_name, field1, field2)
        if not valid:
            return False, msg
        return cls.are_fields_in_order(field_name, field1, field2)

    @classmethod
    def validate_pair_fields(cls, pair_fields: list):
        for field_name, field1, field2 in pair_fields:
            ok, msg = cls.verify_range_fields(field_name, field1, field2)
            if not ok:
                return False, msg
        return True, ""


class GuiDataProcessor:
    @staticmethod
    def stoi(data: dict):
        for key in data.keys():
            if not "from" in key and not "to" in key:
                continue
            data[key] = float(data[key] or "0")
            if data[key] == int(data[key]):
                data[key] = int(data[key])    

    @staticmethod
    def finalize_common_data(book: str, carrier):
        page_from = carrier.common_raw_data["page_from"]
        page_to = carrier.common_raw_data["page_to"]
        hours = carrier.common_raw_data["hours"]
        minutes = carrier.common_raw_data["minutes"]
        notes = carrier.common_raw_data["notes"].rstrip() or "N/A"
        reading_mode = "Sequential" if carrier.common_raw_data["reading_mode"] else "Random"
        revision = carrier.common_raw_data["revision"].rstrip() or "No"
        pages, total_pages = ProgressRules.get_str_and_total(page_from, page_to)
        time_spent = CoreHelpers.get_time_str(hours, minutes)
        carrier.data_final.update({
                "subject": carrier.raw_data["subject"],
                "book": book,
                "pages": pages,
                "total_pages": total_pages,
                "time_spent": time_spent,
                "notes": notes,
                "reading_mode": reading_mode,
                "revision": revision
            })
        return True

    @classmethod
    def process_common_data(cls, carrier):
        cls.stoi(carrier.common_raw_data)
        valid, msg = PairFieldsValidation.validate_pair_fields([("Page", carrier.common_raw_data["page_from"], carrier.common_raw_data["page_to"])])
        if not valid:
            return False, msg
        return PairFieldsValidation.both_fields_empty("Time Spent", carrier.common_raw_data["hours"], carrier.common_raw_data["minutes"])

    @classmethod
    def finalize_Quran_data(cls, carrier):
        Para = ProgressRules.get_str_and_total(carrier.raw_data["Para_from"], carrier.raw_data["Para_to"])[0]
        Ruku, total_Ruku = ProgressRules.get_str_and_total(carrier.raw_data["Ruku_from"], carrier.raw_data["Ruku_to"])
        Para = f"Para no. {Para}"
        carrier.data_final = {"Ruku": Ruku, "total_Ruku": total_Ruku}
        if "Surah_from" in carrier.raw_data:
            Surah_from = carrier.raw_data["Surah_from"]
            Surah_to = carrier.raw_data["Surah_to"]
            Ayah_from = carrier.raw_data["Ayah_from"]
            Ayah_to = carrier.raw_data["Ayah_to"]
            carrier.data_final["Surah"] = ProgressRules.get_str_and_total(Surah_from, Surah_to)[0]
            carrier.data_final["Ayah"], carrier.data_final["total_Aayat"] = ProgressRules.get_str_and_total(Ayah_from, Ayah_to)
        return cls.finalize_common_data(Para, carrier)

    @classmethod
    def process_Quran_data(cls, carrier):
        cls.stoi(carrier.raw_data)
        pairs = []
        pairs.append(("Para", carrier.raw_data["Para_from"], carrier.raw_data["Para_to"]))
        if "Surah_from" in carrier.raw_data:
            pairs.append(("Surah", carrier.raw_data["Surah_from"], carrier.raw_data["Surah_to"]))
            pairs.append(("Ayah", carrier.raw_data["Ayah_from"], carrier.raw_data["Ayah_to"]))
        pairs.append(("Ruku", carrier.raw_data["Ruku_from"], carrier.raw_data["Ruku_to"]))
        valid, msg = PairFieldsValidation.validate_pair_fields(pairs)
        if not valid:
            return False, msg
        valid, msg = cls.process_common_data(carrier)
        if not valid:
            return False, msg
        return cls.finalize_Quran_data(carrier), "Failed to save data"

    @classmethod
    def finalize_other_data(cls, carrier):
        subject = carrier.raw_data["subject"].strip()
        book = carrier.raw_data["book"].strip()

        if not subject or not book:
            return False, "Can't leave Subject or Book field empty"

        carrier.data_final["unit"] = ProgressRules.get_str_and_total(carrier.raw_data["unit_from"], carrier.raw_data["unit_to"])[0]
        carrier.data_final["chapter"] = carrier.raw_data["chapter"].strip() or "N/A"
        return cls.finalize_common_data(book, carrier)

    @classmethod
    def process_other_data(cls, carrier):
        cls.stoi(carrier.raw_data)
        pairs = [("Unit", carrier.raw_data["unit_from"], carrier.raw_data["unit_to"])]
        valid, msg = PairFieldsValidation.validate_pair_fields(pairs)
        if not valid:
            return False, msg
        valid, msg = cls.process_common_data(carrier)
        if not valid:
            return False, msg
        return cls.finalize_other_data(carrier), "Failed to save data"


class GuiWorkflow:
    def __init__(self, app_context) -> None:
        self.app_context = app_context
        self.carrier = DataCarrier()
        self.entry = None
        
    def collect_data_make_entry(self, specific_input: dict, common_input: dict, add_entry: bool = True):
        self.carrier.raw_data = specific_input
        self.carrier.common_raw_data = common_input
        if "Al Qur'an" in specific_input["entry_type"]:
            valid, msg = GuiDataProcessor.process_Quran_data(self.carrier)
            if not valid:
                return valid, msg
            if "Tafseer" in self.carrier.data_final["subject"]:
                self.entry = TafseerEntry(**self.carrier.data_final)
            else:
                self.entry = TilawatEntry(**self.carrier.data_final)
        else:
            valid, msg = GuiDataProcessor.process_other_data(self.carrier)
            if not valid:
                return valid, msg
            self.entry = OtherEntry(**self.carrier.data_final)
        if add_entry:
            self.app_context.add_entry_to_log(self.entry)
        return True, "Operation successful!"