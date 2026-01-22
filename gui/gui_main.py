import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt ,QDate, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QDialog,
                             QGridLayout, QVBoxLayout, QLabel, QFormLayout,
                             QLineEdit, QStackedLayout, QTabWidget, 
                             QStatusBar, QTextBrowser, QRadioButton, QInputDialog)
from core.app_context import AppContext
from core.core_services import CoreHelpers, DeleteController, DateManager
from core.exceptions import DataCorruptionError
from gui.dialogs import MsgDialogs, DateDialog, PasswordDialog
from gui.screens import BaseScreen
from gui.widgets import ClickableLabel, DateSelector
from gui.gui_forms import QuranKareemForm, OtherSubjectsForm 
from gui.entries_display import EntryFormatter
from gui.styles import StyleSheets
from gui.menubar import MainMenuBar


class MainMenuScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # Widgets
        self.title = QLabel("Muslim Learning Journal")
        self.Quran_label = ClickableLabel("Al Qur'an Kareem")
        self.other_label = ClickableLabel("Other Subjects")
        self.stats_label = ClickableLabel()
        self.save_label = ClickableLabel("Save Progress")
        self.view_label = ClickableLabel("View Progress")
        self.delete_label = ClickableLabel("Delete Progress")
        self.exit_label = ClickableLabel("Exit")

        # Attaching Functions
        self.Quran_label.leftClicked.connect( #type: ignore
            lambda: self.main_window.switch_screens(self.main_window.Quran_Kareem))
        self.other_label.leftClicked.connect( #type: ignore
            lambda: self.main_window.switch_screens(self.main_window.other_subjects))
        self.save_label.leftClicked.connect( #type: ignore
            lambda: self.main_window.switch_screens(self.main_window.save_screen))
        self.view_label.leftClicked.connect( #type: ignore
            lambda: self.main_window.switch_screens(self.main_window.view_screen))
        self.delete_label.leftClicked.connect( #type: ignore
            lambda: self.main_window.switch_screens(self.main_window.delete_screen))
        self.exit_label.leftClicked.connect(self.main_window.close) #type: ignore

        self.title.setStyleSheet(StyleSheets.label_normal())
        self.title.setStatusTip("Muslim-learning-Journal")
        self.Quran_label.setStatusTip("Log Qur'an Progress")
        self.other_label.setStatusTip("Log other Progress")
        self.save_label.setStatusTip("Save all changes")
        self.view_label.setStatusTip("View entries from a specific date")
        self.delete_label.setStatusTip("Delete entries")
        self.exit_label.setStatusTip("Exit")

        self.menu = QGridLayout(self)
        # self.menu.setVerticalSpacing(15)
        self.menu.setContentsMargins(25, 25, 25, 25)
        self.menu.addWidget(self.title, 0, 0, 1, 3)
        self.menu.addWidget(self.Quran_label, 1, 0, 1, 2)
        self.menu.addWidget(self.other_label, 2, 0, 1, 2)
        self.menu.addWidget(self.stats_label, 1, 2, 2, 1)
        self.menu.addWidget(self.save_label, 3, 0)
        self.menu.addWidget(self.view_label, 3, 1)
        self.menu.addWidget(self.delete_label, 3, 2)
        self.menu.addWidget(self.exit_label, 4, 0, 1, 3)
        self.display_stats_today()
    
    def display_stats_today(self):
        stats_manager = self.main_window.context.stats_manager
        stats_manager.calculate_stats_today()
        entry_count = stats_manager.stats_today[0]
        stats = (
                f"Today\n\n{entry_count} {'entries' if entry_count > 1 else 'entry'}\n"
                f"{stats_manager.stats_today[2]} page(s)\n"
                f"{CoreHelpers.format_time(stats_manager.stats_today[1])}"
            )
        self.stats_label.setText(stats)


class QuranKareemScreen(BaseScreen):

    def __init__(self, main_window):

        # Tafseer Form
        self.Tafseer_form = QuranKareemForm(main_window)

        # Tilawat Form
        self.Tilawat_form = QuranKareemForm(main_window, False)

        # Quran Tabs
        self.tabs_widget = QTabWidget()
        self.tabs_widget.addTab(self.Tafseer_form, QIcon("./images/Quran.jpg"), "Tafseer")
        self.tabs_widget.addTab(self.Tilawat_form, QIcon("./images/Quran.jpg"), "Tilawat")

        super().__init__("AL Quran Kareem", self.tabs_widget, main_window.get_back_label())


class OtherSubjectsScreen(BaseScreen):
    def __init__(self, main_window):
        super().__init__("Other Subjects", OtherSubjectsForm(main_window), main_window.get_back_label())


class SaveScreen(BaseScreen):

    def showEvent(self, event):
        super().showEvent(event)
        self.show_unsaved_entries()

    def __init__(self, main_window):
        self.content_widget = QWidget()
        self.context = main_window.context
        super().__init__("Save Progress", self.content_widget, main_window.get_back_label())

        self.tb = QTextBrowser()
        self.tb.setStyleSheet("background: rgb(220, 220, 220);")
        self.save_label = ClickableLabel("Save")
        self.save_label.leftClicked.connect(self.save_progress) #type: ignore
        main_window.signal_save.connect(self.save_progress) #type: ignore
        layout = QVBoxLayout(self.content_widget)
        layout.addWidget(self.tb)
        layout.addWidget(self.save_label)
        
    def show_unsaved_entries(self):
        if not self.context.unsaved_entries:
            html = "<div align='center' style='white-space: pre-wrap;'><h2>No unsaved entries</h2></div>"
        else:
            formatted = EntryFormatter.format_dict_entries_html("Unsaved Entries", self.context.unsaved_entries)
            html = f"<div align='center' style='white-space: pre-wrap;'>{formatted}</div>"
        self.tb.setHtml(html)

    def save_progress(self):
        return_code = self.context.save_progress_to_files()
        if return_code == 0:
            MsgDialogs.show_information_msg(self, "Progress saved successfully!")
            self.show_unsaved_entries()
        elif return_code == 1:
            MsgDialogs.show_critical_msg(self, "Could not save JSON file.")
        elif return_code == 2:
            MsgDialogs.show_critical_msg(self, "Could not save Markdown file.")


class ViewScreen(BaseScreen):

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            self.get_date(self.date_selector.get_date_selected())

    def __init__(self, main_window):
        self.content_widget = QWidget()
        self.context = main_window.context
        super().__init__("View Progress", self.content_widget, main_window.get_back_label())

        layout = QVBoxLayout(self.content_widget)
        self.date_selector = DateSelector("View Entries from")
        self.display = QTextBrowser()
        self.display.setStyleSheet("background: rgb(220, 220, 220);")
        layout.addWidget(self.date_selector)
        layout.addWidget(self.display)
        self.date_selector.signal_date_selection.connect(self.get_date) # type: ignore

    def get_date(self, date: QDate):
        formatted = date.toString("dd-MMM-yyyy")
        self.show_progress(formatted)

    def show_progress(self, date: str):
        entries = self.context.data_manager.get_entries_from_date(date)
        if entries:
            formatted = EntryFormatter.format_day_entries_html(date, entries)
            self.display.setHtml(f"<div align='center' style='white-space: pre-wrap;'>{formatted}</div>")
        else:
            self.display.setHtml(f"<div align='center' style='white-space: pre-wrap;'><h2>No entries found for {date}.<br>Please try another date.</h2></div>")
            

class DeleteScreen(BaseScreen):

    def __init__(self, main_window):
        self.content_widget = QWidget()
        self.main_window = main_window
        super().__init__("Delete Progress", self.content_widget, self.main_window.get_back_label())
        layout = QVBoxLayout(self.content_widget)

        self.label = QLabel("Select an option")
        self.today = QRadioButton(text=DeleteController.DEL_OPTIONS[0])
        self.another_day = QRadioButton(text=DeleteController.DEL_OPTIONS[1])
        self.all_progress = QRadioButton(text=DeleteController.DEL_OPTIONS[2])
        self.button = ClickableLabel("Next")
        self.label.setStyleSheet(StyleSheets.label_normal())
        self.button.leftClicked.connect(self.next) # type: ignore
        layout.addWidget(self.label)
        layout.addWidget(self.today)
        layout.addWidget(self.another_day)
        layout.addWidget(self.all_progress)
        layout.addWidget(self.button)

        self.date_dialog = DateDialog(self)
        self.date_dialog.signal_date_selected.connect(self.get_date) # type: ignore
        
    def next(self):
        if self.today.isChecked():
            today = DateManager.get_date_today()
            if MsgDialogs.get_answer(self, "This will delete progress from today.\nContinue?\n", title="Delete Confirmation"):
                deleted, msg = DeleteController.delete_day(today, self.main_window.context)
                if deleted:
                    self.main_window.main_menu.display_stats_today()
                    MsgDialogs.show_information_msg(self, msg)
                else:
                    MsgDialogs.show_warning_msg(self, msg)
        elif self.another_day.isChecked():
            self.date_dialog.exec_()
        elif self.all_progress.isChecked():
            self.delete_all()

    def get_date(self, date: QDate):
        formatted = date.toString("dd-MMM-yyyy")
        if MsgDialogs.get_answer(self, f"This will delete progress from {formatted}.\nContinue?\n", title="Delete Confirmation"):
            deleted, msg = DeleteController.delete_day(formatted, self.main_window.context)
            if deleted:
                MsgDialogs.show_information_msg(self, msg)
            else:
                MsgDialogs.show_warning_msg(self, msg)

    def delete_all(self):
        if not MsgDialogs.get_answer(self, f"This will delete all time progress.\nContinue?\n", title="Delete Confirmation"):
            return
        password, _ = QInputDialog.getText(self, self.main_window.context.app_name, "Enter your password")
        deleted, msg = DeleteController.delete_all_with_password_check(password, self.main_window.context)
        if deleted:
            MsgDialogs.show_information_msg(self, msg)            
        else:
            MsgDialogs.show_critical_msg(self, msg)


class MainWindow(QMainWindow):
    signal_save = pyqtSignal()
    
    # def paintEvent(self, event):
    #     painter = QPainter(self)
    #     gradient = QLinearGradient(0, 0, self.width(), self.height())
    #     gradient.setColorAt(0.0, QColor("#34495e"))
    #     gradient.setColorAt(1.0, QColor("#2c3e50"))
    #     painter.fillRect(self.rect(), gradient)

    def closeEvent(self, a0) -> None:
        if self.confirm_exit():
            a0.accept()            
        else:
            a0.ignore()

    def __init__(self, app_context: AppContext):
        super().__init__()
        self.context = app_context
        

        # MainWindow's Setup
        self.setGeometry(150, 100, 900, 600)
        self.setWindowTitle("Muslim Learning Journal")
        self.setWindowIcon(QIcon("./images/Diary.png"))
        
        # Central Widget
        central_widget = QWidget()
        central_widget.setStyleSheet("background: #ebeae2;")
        self.setCentralWidget(central_widget)
        self.stacked_layout = QStackedLayout(central_widget)
        self.setStatusBar(QStatusBar(self))

        # All Screens
        self.main_menu = MainMenuScreen(self)
        self.Quran_Kareem = QuranKareemScreen(self)
        self.other_subjects = OtherSubjectsScreen(self)
        self.save_screen = SaveScreen(self)
        self.view_screen = ViewScreen(self)
        self.delete_screen = DeleteScreen(self)

        self.stacked_layout.addWidget(self.main_menu)
        self.stacked_layout.addWidget(self.Quran_Kareem)
        self.stacked_layout.addWidget(self.other_subjects)
        self.stacked_layout.addWidget(self.save_screen)
        self.stacked_layout.addWidget(self.view_screen)
        self.stacked_layout.addWidget(self.delete_screen)

        self.menu_bar = MainMenuBar(self)
        self.setMenuBar(self.menu_bar)
        self.menu_bar.action_Quran_entry.triggered.connect(lambda: self.switch_screens(self.Quran_Kareem)) # type: ignore
        self.menu_bar.action_other_entry.triggered.connect(lambda: self.switch_screens(self.other_subjects)) # type: ignore
        self.menu_bar.action_open.triggered.connect(self.open_journal)
        self.menu_bar.action_save.triggered.connect(self.signal_save.emit) # type: ignore
        self.menu_bar.action_exit.triggered.connect(self.close) 
        self.menu_bar.action_about.triggered.connect(self.about)
        self.menu_bar.action_show_report.triggered.connect(self.show_weekly_report)
        self.menu_bar.action_reset_password.triggered.connect(self.reset_password)

    def reset_password(self):
        PasswordDialog(self.context.password_manager, "Set a new password").exec_()

    def switch_screens(self, screen):
        self.stacked_layout.setCurrentWidget(screen)

    def go_back(self):
        self.switch_screens(self.main_menu)

    def open_journal(self):
        try:
            self.context.open_journal()
        except (Exception, FileNotFoundError) as e:
            MsgDialogs.show_critical_msg(self, str(e))

    def show_weekly_report(self):
        MsgDialogs.show_information_msg(self, self.context.stats_manager.get_weekly_summary(), "Weekly Report")

    def get_back_label(self, label_text="Back") -> ClickableLabel:
        go_back_label = ClickableLabel(label_text)
        go_back_label.leftClicked.connect(self.go_back) #type: ignore
        return go_back_label

    def about(self):
        MsgDialogs.show_information_msg(self, f"{self.context.about()}\n\nDeveloped with PyQt5.")

    def confirm_exit(self) -> bool:
            msg = "Any unsaved changes will be lost.\nAre you sure you want to exit?"
            if not "Al-Qur'an (Tafseer)" in self.context.data_manager.progress_today:
                msg = f"{CoreHelpers.get_motivational_quote()}\n\n\n{msg}"       
            return MsgDialogs.get_answer(self, msg, title="Exit Confirmation")
            
            
def main():
    app = QApplication(sys.argv)
    
    try:
        app_context = AppContext()
    except DataCorruptionError as e:
        MsgDialogs.show_critical_msg(None, f"{e}\n\nDetails:\n{e.__cause__}")
        sys.exit(1)

    if not app_context.password_manager.is_password_set():
        dlg = PasswordDialog(
            app_context.password_manager,
            "No password has been set. Please set one to continue."
        )
        if dlg.exec_() != QDialog.Accepted:
            sys.exit(0)

    app.setStyleSheet(StyleSheets.global_style_sheet())
    app.setStyle("Fusion")
    window = MainWindow(app_context)
    window.show()
    window.raise_()
    sys.exit(app.exec_())
