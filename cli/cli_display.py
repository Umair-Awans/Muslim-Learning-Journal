        
    
class CliProgressDisplay:

    @staticmethod
    def display_entries(heading: str, progress: dict) -> None:
        print(f"\n---------( {heading} )---------\n")
        for key, value in progress.items():
            print(f">>> {key}: {value}")

    @classmethod
    def display_entries_all(cls, progress: dict, day: str) -> None:
        print(f"\n<><><>--( Entries from {day} )--<><><>\n")
        if not progress:
            print(f">>> No entries recorded for {day}.")
            return
        for subject, books in progress.items():
            print(f"\n-----[<<( {subject} )>>]-----\n")
            for book, sessions in books.items():
                print(f"\n<><><>------[ {book} ]------<><><>\n")
                for session, session_details in sessions.items():
                    cls.display_entries(session, session_details)