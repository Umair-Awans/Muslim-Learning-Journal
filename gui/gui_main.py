import sys
from PyQt5.QtGui import QIcon, QIntValidator, QDoubleValidator, QKeyEvent
from PyQt5.QtCore import Qt, QRect, QTimer, QDate, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QGridLayout, QAction, QHBoxLayout,
                             QCheckBox, QMessageBox, QVBoxLayout,
                             QScrollArea, QMenuBar, QMenu, QLabel, QDateEdit,
                             QFormLayout, QLineEdit, QStackedLayout,
                             QComboBox, QTabWidget, QStatusBar,
                             QTextBrowser, QPushButton, QTextEdit,
                             QRadioButton)
from core.app_context import AppContext
from core.data_manager import DataManager
from core.stats_manager import StatsManager
from core.core_utils import PasswordManager, DateManager, Utilities, DeleteController
from core.exceptions import DataCorruptionError
from gui.gui_utils import ClickableLabel, GuiUtilities, StyleUtilities, UnsavedEntries, EntryFormatter
from gui.gui_forms import QuranKareemForm, OtherSubjectsForm 


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
        StyleUtilities.styleWidgets(self.title, self.Quran_label, self.other_label,
                               self.stats_label, self.save_label, self.view_label,
                               self.delete_label, self.exit_label)

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
        self.exit_label.leftClicked.connect(self.on_exit_label_clicked) #type: ignore

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
        self.title.setStatusTip("Muslim-learning-Journal")
        self.Quran_label.setStatusTip("Log Qur'an Progress")
        self.other_label.setStatusTip("Log other Progress")
        self.save_label.setStatusTip("Save all changes")
        self.view_label.setStatusTip("View entries from a specific date")
        self.delete_label.setStatusTip("Delete entries")
        self.exit_label.setStatusTip("Exit")
        self.display_stats_today()

    def on_exit_label_clicked(self):
        if self.main_window.quit_program():
            QApplication.quit()
    
    def display_stats_today(self):
        stats_manager = self.main_window.context.stats_manager
        stats_manager.calculate_stats_today()
        self.stats_label.setText(f"Today\n\n{Utilities.format_time(stats_manager.stats_today[0])}\n{stats_manager.stats_today[1]} page(s)")


class BaseScreen(QWidget):

    def __init__(self, title: str, content_widget, back_label, parent=None):
        super().__init__(parent)

        self.title = QLabel(title)
        StyleUtilities.styleWidgets(self.title)

        self.screen_layout = QVBoxLayout(self)
        self.screen_layout.addWidget(self.title)
        self.screen_layout.addWidget(content_widget)
        self.screen_layout.addWidget(back_label)


class QuranKareemScreen(BaseScreen):

    def __init__(self, main_window):

        # **Quran-Forms**
        # Tafseer Form
        self.Tafseer_form = QuranKareemForm(main_window.context.data_manager)

        # Tilawat Form
        self.Tilawat_form = QuranKareemForm(main_window.context.data_manager, False)

        # Quran Tabs
        self.tabs_widget = QTabWidget()
        self.tabs_widget.addTab(self.Tafseer_form, QIcon("./images/Quran.jpg"), "Tafseer")
        self.tabs_widget.addTab(self.Tilawat_form, QIcon("./images/Quran.jpg"), "Tilawat")

        super().__init__("AL Quran Kareem", self.tabs_widget, main_window.get_back_label())


class OtherSubjectsScreen(BaseScreen):
    def __init__(self, main_window):
        super().__init__("Other Subjects", OtherSubjectsForm(main_window.context.data_manager), main_window.get_back_label())


class SaveScreen(BaseScreen):
    def __init__(self, main_window):
        self.content_widget = QWidget()
        self.main_window = main_window
        super().__init__("Save Progress", self.content_widget, self.main_window.get_back_label())

        self.tb = QTextBrowser()
        self.tb.setStyleSheet("background: rgb(220, 220, 220);")
        self.save_label = ClickableLabel("Save")
        self.save_label.leftClicked.connect(self.save_progress) #type: ignore
        self.main_window.signal_save.connect(self.save_progress) #type: ignore
        layout = QVBoxLayout(self.content_widget)
        layout.addWidget(self.tb)
        layout.addWidget(self.save_label)
        
        StyleUtilities.styleWidgets(self.save_label)

    def showEvent(self, event):
        super().showEvent(event)
        self.show_unsaved_entries()

    def show_unsaved_entries(self):
        self.tb.setHtml(f"<div align='center' style='white-space: pre-wrap;'>{UnsavedEntries.to_html()}</div>")

    def save_progress(self):
        return_code =  self.main_window.context.data_manager.save_progress_to_files()
        if return_code == 0:
            GuiUtilities.show_information_msg(self, "Progress saved successfully!")
            UnsavedEntries.clear_all()
            self.show_unsaved_entries()
        elif return_code == 1:
            GuiUtilities.show_critical_msg(self, "Could not save JSON file.")
        elif return_code == 2:
            GuiUtilities.show_critical_msg(self, "Could not save Markdown file.")


class DateSelector(QWidget):
    signal_date_selection = pyqtSignal(QDate)
    def __init__(self, label_text: str, parent=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        self.date_edit = QDateEdit()
        self.submit = ClickableLabel(label_text)
        layout.addWidget(self.submit)
        layout.addWidget(self.date_edit)
        StyleUtilities.styleWidgets(self.submit)
        self.submit.leftClicked.connect(lambda: self.signal_date_selection.emit(self.date_edit.date())) # type: ignore

    def get_date_selected(self):
        return self.date_edit.date()

    def showEvent(self, event):
        super().showEvent(event)
        self.date_edit.setDate(QDate.currentDate())


class ViewScreen(BaseScreen):
    def __init__(self, main_window):
        self.content_widget = QWidget()
        self.main_window = main_window
        super().__init__("View Progress", self.content_widget, self.main_window.get_back_label())

        layout = QVBoxLayout(self.content_widget)
        self.date_selector = DateSelector("View Entries from")
        self.display = QTextBrowser()
        self.display.setStyleSheet("background: rgb(220, 220, 220);")
        layout.addWidget(self.date_selector)
        layout.addWidget(self.display)
        self.date_selector.signal_date_selection.connect(self.get_date) # type: ignore

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            self.get_date(self.date_selector.get_date_selected())

    def get_date(self, date: QDate):
        formatted = date.toString("dd-MMM-yyyy")
        self.show_progress(formatted)

    def show_progress(self, date: str):
        entries = self.main_window.context.data_manager.get_entries_from_date(date)
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
        self.stacked_layout = QStackedLayout(self.content_widget)

        self.menu = QWidget()
        menu_layout = QVBoxLayout(self.menu)
        self.label = QLabel("Select an option")
        self.today = QRadioButton(text=DeleteController.DEL_OPTIONS[0])
        self.another_day = QRadioButton(text=DeleteController.DEL_OPTIONS[1])
        self.all_progress = QRadioButton(text=DeleteController.DEL_OPTIONS[2])
        self.button = ClickableLabel("Next")
        self.button.leftClicked.connect(self.next) # type: ignore
        menu_layout.addWidget(self.label)
        menu_layout.addWidget(self.today)
        menu_layout.addWidget(self.another_day)
        menu_layout.addWidget(self.all_progress)
        menu_layout.addWidget(self.button)
        StyleUtilities.styleWidgets(self.label, self.button)

        self.another_date = QWidget()
        another_layout = QVBoxLayout(self.another_date)
        another_label = QLabel("Select the Date")
        date_selector = DateSelector("Delete Entries from")
        date_selector.signal_date_selection.connect(self.get_date) # type: ignore
        another_layout.addWidget(another_label)
        another_layout.addWidget(date_selector)

        self.password_screen = QWidget()
        password_layout = QVBoxLayout(self.password_screen)
        password_label = QLabel("Enter your password")
        self.password_edit = QLineEdit()
        password_submit = ClickableLabel("Submit")
        password_submit.leftClicked.connect(self.delete_all) # type: ignore
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_edit)
        password_layout.addWidget(password_submit)
        StyleUtilities.styleWidgets(password_label, password_submit, another_label)
        
        self.stacked_layout.addWidget(self.menu)
        self.stacked_layout.addWidget(self.another_date)
        self.stacked_layout.addWidget(self.password_screen)

    def next(self):
        if self.today.isChecked():
            today = DateManager.get_date_today()
            if GuiUtilities.get_answer(self, "This will delete progress from today.\nContinue?\n", title="Delete Confirmation"):
                deleted, msg = DeleteController.delete_day(today, self.main_window.context.data_manager)
                if deleted:
                    GuiUtilities.show_information_msg(self, msg)
                else:
                    GuiUtilities.show_critical_msg(self, msg)
        elif self.another_day.isChecked():
            self.stacked_layout.setCurrentWidget(self.another_date)
        elif self.all_progress.isChecked():
            self.stacked_layout.setCurrentWidget(self.password_screen)

    def get_date(self, date: QDate):
        formatted = date.toString("dd-MMM-yyyy")
        if GuiUtilities.get_answer(self, f"This will delete progress from {formatted}.\nContinue?\n", title="Delete Confirmation"):
            deleted, msg = DeleteController.delete_day(formatted, self.main_window.context.data_manager)
            if deleted:
                GuiUtilities.show_information_msg(self, msg)
            else:
                GuiUtilities.show_critical_msg(self, msg)
        self.stacked_layout.setCurrentWidget(self.menu)

    def delete_all(self):
        if not GuiUtilities.get_answer(self, f"This will delete all time progress.\nContinue?\n", title="Delete Confirmation"):
            return
        password = self.password_edit.text()
        deleted, msg = DeleteController.delete_all(password, self.main_window.context.data_manager)
        if deleted:
            GuiUtilities.show_information_msg(self, msg)            
        else:
            GuiUtilities.show_critical_msg(self, msg)
        self.stacked_layout.setCurrentWidget(self.menu)


class PasswordScreen(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        layout = QFormLayout(self)
        self.qlStatus = QLabel("No password has been set. Please set one to continue.")
        self.qlPassword = QLabel("Enter Password:")
        self.qlConfirm = QLabel("Confirm Password:")
        self.qlePassword = QLineEdit()
        self.qleConfirm = QLineEdit()
        self.clSubmit = ClickableLabel("Submit")
        self.clSubmit.leftClicked.connect(self.set_password) # type: ignore

        layout.addRow(self.qlStatus)
        layout.addRow(self.qlPassword, self.qlePassword)
        layout.addRow(self.qlConfirm, self.qleConfirm)
        layout.addRow(self.clSubmit)
        StyleUtilities.styleWidgets(self.qlStatus, self.qlPassword, self.qlConfirm, self.clSubmit)

    def set_password(self):
        if not self.qlePassword.text().strip() == self.qleConfirm.text().strip():
            GuiUtilities.show_critical_msg(self, "Passwords do not match. Enter again.")
            return
        saved, msg = PasswordManager.store_password(self.qlePassword.text().strip())
        if not saved:
            GuiUtilities.show_critical_msg(self, msg)
            return
        GuiUtilities.show_information_msg(self, msg)
        self.main_window.go_back()
        self.main_window.stacked_layout.removeWidget(self)
        self.deleteLater()


class MainWindow(QMainWindow):
    signal_save = pyqtSignal()
    
    # def paintEvent(self, event):
    #     painter = QPainter(self)
    #     gradient = QLinearGradient(0, 0, self.width(), self.height())
    #     gradient.setColorAt(0.0, QColor("#34495e"))
    #     gradient.setColorAt(1.0, QColor("#2c3e50"))
    #     painter.fillRect(self.rect(), gradient)

    def closeEvent(self, a0) -> None:
        if self.quit_program():
            a0.accept()            
        else:
            a0.ignore()

    def __init__(self, context: AppContext):
        super().__init__()

        self.context = context

        # MainWindow's Setup
        self.setGeometry(150, 100, 900, 600)
        self.setWindowTitle("Muslim Learning Journal")
        self.setWindowIcon(QIcon("./images/Diary.png"))
        

        # All Screens
        self.main_menu = MainMenuScreen(self)
        self.Quran_Kareem = QuranKareemScreen(self)
        self.other_subjects = OtherSubjectsScreen(self)
        self.save_screen = SaveScreen(self)
        self.view_screen = ViewScreen(self)
        self.delete_screen = DeleteScreen(self)

        # Central Widget
        central_widget = QWidget()
        central_widget.setStyleSheet("background: #ebeae2;")
        self.setCentralWidget(central_widget)
        self.stacked_layout = QStackedLayout(central_widget)

        self.stacked_layout.addWidget(self.main_menu)
        self.stacked_layout.addWidget(self.Quran_Kareem)
        self.stacked_layout.addWidget(self.other_subjects)
        self.stacked_layout.addWidget(self.save_screen)
        self.stacked_layout.addWidget(self.view_screen)
        self.stacked_layout.addWidget(self.delete_screen)
        self.setStatusBar(QStatusBar(self))
        self.setup_password_gate()

        # MenuBar Setup
        self.menu_bar = QMenuBar(self)
        self.menu_file = QMenu("File")
        self.action_save = QAction("Save", self)
        self.action_save.setShortcut("Ctrl+S")
        self.action_save.triggered.connect(self.signal_save.emit)
        
        self.menu_file.addAction(self.action_save)

        self.menu_bar.addMenu(self.menu_file)
        self.setMenuBar(self.menu_bar)

    def switch_screens(self, screen):
        self.stacked_layout.setCurrentWidget(screen)

    def go_back(self):
        self.switch_screens(self.main_menu)

    def get_back_label(self, label_text="Go Back") -> ClickableLabel:
        go_back_label = ClickableLabel(label_text)
        go_back_label.leftClicked.connect(self.go_back) #type: ignore
        StyleUtilities.styleWidgets(go_back_label)
        return go_back_label

    def setup_password_gate(self):
        if not PasswordManager.password_file_exists():
            screen = PasswordScreen(self)
            self.stacked_layout.addWidget(screen)
            self.switch_screens(screen)

    def quit_program(self) -> bool:
            msg = "Any unsaved changes will be lost.\nAre you sure you want to exit?"
            if not "Al-Qur'an (Tafseer)" in self.context.data_manager.progress_today:
                msg = f"{Utilities.get_motivational_quote()}\n\n\n{msg}"       
            return GuiUtilities.get_answer(self, msg, title="Exit Confirmation")
            
            
def main():
    app = QApplication(sys.argv)
    try:
        context = AppContext()
    except DataCorruptionError as e:
        GuiUtilities.show_critical_msg(None,
            (
                "Your learning journal data file appears to be corrupted.\n\n"
                "The application will now exit to prevent data loss.\n\n"
                f"Details:\n{e}"
            )
        )
        sys.exit(1)
    StyleUtilities.applyGlobalStyles(app)
    app.setStyle("Fusion")
    window = MainWindow(context)
    window.show()
    window.raise_()
    sys.exit(app.exec_())
