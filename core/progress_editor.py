from core.core_services import CoreHelpers

class ProgressEditor:
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
        temp_total_minutes = CoreHelpers.convert_time_to_mins(stats[details[0]][details[1]]["Time Spent"])
        if add:
            temp_total_minutes += CoreHelpers.convert_time_to_mins(entry_time_spent)
        else:
            temp_total_minutes -= CoreHelpers.convert_time_to_mins(entry_time_spent)
        stats[details[0]][details[1]]["Time Spent"] = CoreHelpers.format_time(temp_total_minutes)

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