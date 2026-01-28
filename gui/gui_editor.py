from PyQt5.QtWidgets import QInputDialog
from core.core_services import DeleteController
from core.entries import TafseerEntry, TilawatEntry, OtherEntry
from core.progress_editor import ProgressEditor
from gui.dialogs import QDialog, MsgDialogs, DateDialog, EditorDialog
from gui.gui_forms import OtherSubjectsForm
from gui.gui_forms import QuranKareemForm, OtherSubjectsForm

class EntryEditService:
    @staticmethod
    def update_stats(main_window, original_entry, edited_entry, subject, book, session):
        old_pages = original_entry["Total Pages"]
        new_pages = edited_entry["Total Pages"]
        old_time = original_entry["Time Spent"]
        new_time = edited_entry["Time Spent"]
        if old_pages != new_pages:
            details = (subject, book, session)
            values = (old_pages, new_pages)
            main_window.context.stats_manager.updater.update_stats(details, values, "Page")
        if old_time != new_time:
            details = (subject, book, session)
            values = (old_time, new_time)
            main_window.context.stats_manager.updater.update_stats(details, values, "Time Spent")
      
    @classmethod
    def get_date_entry_form(cls, main_window):
        date_dialog = DateDialog("Edit an entry from:", main_window)
        if date_dialog.exec_() != QDialog.Accepted:
            return
        date = date_dialog.calendar_widget.selectedDate().toString("dd-MMM-yyyy")
        entries_date = main_window.context.data_manager.get_entries_from_date(date)
        if not entries_date:
            MsgDialogs.show_warning_msg(main_window, f"No entries recorded for {date}")
            return
        editor_dialog = EditorDialog(date, entries_date, main_window)
        if editor_dialog.exec_() != QDialog.Accepted:
            return
        subject = editor_dialog.qcb_subject.currentText()
        book = editor_dialog.qcb_book.currentText()
        session = editor_dialog.qcb_session.currentText()

        original_entry = entries_date[subject][book][session]

        if subject == "Al-Qur'an (Tafseer)":
            entry_inst = TafseerEntry.from_dict(subject, book, original_entry)
            form = QuranKareemForm(main_window)
        elif subject == "Al-Qur'an (Tilawat)":
            entry_inst = TilawatEntry.from_dict(subject, book, original_entry)
            form = QuranKareemForm(main_window, Tafseer=False)
        else:
            entry_inst = OtherEntry.from_dict(subject, book, original_entry)
            form = OtherSubjectsForm(main_window)

        return (date, session, entries_date, entry_inst, form)

    @staticmethod
    def delete_an_entry(main_window, entries_day, details):
        dict_to_edit = entries_day[details[0]][details[1]][details[2]]
        values = (dict_to_edit["Total Pages"], dict_to_edit["Time Spent"])
        main_window.context.stats_manager.updater.update_stats(details, values, date=details[3])
        entries_day[details[0]][details[1]].pop(details[2])
        ProgressEditor.pop_empty_dicts(entries_day, details[0], details[1])
        main_window.context.data_manager.update_entry_log(details[3], entries_day)

    @staticmethod
    def delete_entries(main_window):
        date_dialog = DateDialog("Delete entries from:", main_window)
        if date_dialog.exec_() != QDialog.Accepted:
            return
        date_selected = date_dialog.calendar_widget.selectedDate().toString("dd-MMM-yyyy")
        if date_selected == main_window.context.data_manager.date_today:
            is_today = True
        else:
            is_today = False
        if not MsgDialogs.get_answer(main_window, f"This will delete all progress record from {date_selected + ' (Today)' if is_today else date_selected}.\nContinue?\n", title="Delete Confirmation"):
            return
        if MsgDialogs.show_operation_result(main_window, DeleteController.delete_day(date_selected, main_window.context), False):
            main_window.main_menu.display_stats_today()
    
    @staticmethod
    def delete_all(main_window):
        if not MsgDialogs.get_answer(main_window, f"This will delete all time progress.\nContinue?\n", title="Delete Confirmation"):
            return
        password, _ = QInputDialog.getText(main_window, main_window.context.app_name, "Enter your password")
        MsgDialogs.show_operation_result(main_window, DeleteController.delete_all_with_password_check(password, main_window.context))
