
class ProgressEditor:
    @staticmethod
    def pop_empty_dicts(progress: dict, subject: str, book: str) -> None:
        if not progress[subject][book]:
            progress[subject].pop(book)
            if not progress[subject]:
                progress.pop(subject)


