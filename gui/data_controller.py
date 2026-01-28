import pathlib
from PyQt5.QtWidgets import QFileDialog
from gui.dialogs import MsgDialogs, PasswordDialog

class DataController:
    @staticmethod
    def open_journal(main_window):
        try:
            main_window.context.open_journal()
        except (Exception, FileNotFoundError) as e:
            MsgDialogs.show_critical_msg(main_window, str(e))

    @staticmethod
    def save_md_as(main_window):
        options = QFileDialog.Options()
        new_path_md, _ = QFileDialog.getSaveFileName(main_window, "Save As...", str(pathlib.Path(".", "data", "Journal.md")), "Markdown (*.md)", options=options)
        if not new_path_md:
            return
        MsgDialogs.show_operation_result(main_window, main_window.context.change_path_md(new_path_md))

    @staticmethod
    def on_backup_triggered(main_window):
        options = QFileDialog.Options()
        backup_dir = QFileDialog.getExistingDirectory(main_window, "Backup Data", "", options)
        if not backup_dir:
            return
        MsgDialogs.show_operation_result(main_window, main_window.context.data_manager.backup_data(backup_dir))

    @staticmethod
    def on_restore_triggered(main_window):
        if not MsgDialogs.get_answer(main_window, "This action will permanently replace your\ncurrent data with the selected backup.\nContinue?"):
            return
        options = QFileDialog.Options()
        zip_file, _ = QFileDialog.getOpenFileName(main_window, "Restore Data", "", "Zip files (*.zip)", options=options)
        if not zip_file:
            return
        MsgDialogs.show_operation_result(main_window, main_window.context.data_manager.restore_data(zip_file))

    
    @staticmethod
    def show_weekly_report(main_window):
        MsgDialogs.show_information_msg(main_window, main_window.context.stats_manager.get_weekly_summary(), "Weekly Report")

    @staticmethod
    def reset_password(main_window):
        PasswordDialog(main_window.context.password_manager, "Set a new password").exec_()