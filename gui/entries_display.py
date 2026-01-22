from io import StringIO


class EntryFormatter:
    @staticmethod
    def format_entry_html(buffer: StringIO, heading: str, entry: dict):
        buffer.write(f"<h2>{heading}</h2><br>\n<div align='left' style='white-space: pre-wrap;'>\n")
        for key, value in entry.items():
            buffer.write(f">>> {key}: {value}<br><br>")
        buffer.write(f"\n</div><hr><br>")

    @classmethod
    def format_day_entries_html(cls, date: str, entries: dict):
        buffer = StringIO()
        buffer.write(f"<h2>Entries from {date}</h2><br>")
        for subject, books in entries.items():
            buffer.write(f"<h2>{subject}<h2>")
            for book, sessions in books.items():
                buffer.write(f"<h2>{book}<h2><br>")
                for session, session_details in sessions.items():
                    cls.format_entry_html(buffer, session, session_details)
        return buffer.getvalue()

    @classmethod
    def format_dict_entries_html(cls, title: str, entries_dict: dict):
        buffer = StringIO()
        buffer.write(f"<h2>{title}: {len(entries_dict)}</h2><br>")
        for i, (key, entry) in enumerate(entries_dict.items(), 1):
            buffer.write(f"<h2>Entry no. {i}<h2><br>")
            cls.format_entry_html(buffer, key, entry.to_dict())
        return buffer.getvalue()