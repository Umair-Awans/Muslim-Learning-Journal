from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QGridLayout, QVBoxLayout, QTextBrowser, QTabWidget
from core.core_services import CoreHelpers
from gui.styles import StyleSheets
from gui.widgets import ClickableLabel, DateSelector
from gui.dialogs import MsgDialogs
from gui.gui_forms import QuranKareemForm, OtherSubjectsForm 
from gui.gui_editor import EntryEditService
from gui.entries_display import EntryFormatter


class BaseScreen(QWidget):

    def __init__(self, title: str, content_widget, back_label, parent=None):
        super().__init__(parent)

        self.screen_layout = QVBoxLayout(self)
        if title:
            self.title = QLabel(title)
            self.title.setStyleSheet(StyleSheets.label_normal())
            self.screen_layout.addWidget(self.title)

        self.screen_layout.addWidget(content_widget)
        self.screen_layout.addWidget(back_label)


class MainMenuScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # Widgets
        self.title = QLabel("Muslim Learning Journal")
        self.Quran_label = ClickableLabel("Al Qur'an Kareem")
        self.other_label = ClickableLabel("Other Subjects")
        self.stats_label = QLabel()
        self.save_label = ClickableLabel("Save Progress")
        self.view_label = ClickableLabel("View Progress")
        self.edit_label = ClickableLabel("Edit Progress")
        self.exit_label = ClickableLabel("Exit")

        # Attaching Functions
        self.Quran_label.leftClicked.connect( #type: ignore
            lambda: self.main_window.switch_screen(self.main_window.Quran_Kareem))
        self.other_label.leftClicked.connect( #type: ignore
            lambda: self.main_window.switch_screen(self.main_window.other_subjects))
        self.save_label.leftClicked.connect( #type: ignore
            lambda: self.main_window.switch_screen(self.main_window.save_screen))
        self.view_label.leftClicked.connect( #type: ignore
            lambda: self.main_window.switch_screen(self.main_window.view_screen))
        self.edit_label.leftClicked.connect( #type: ignore
            lambda: self.main_window.switch_screen(self.main_window.edit_screen))
        self.exit_label.leftClicked.connect(self.main_window.close) #type: ignore

        self.title.setStyleSheet(StyleSheets.label_normal())
        self.stats_label.setStyleSheet(StyleSheets.label_normal())
        self.title.setStatusTip("Muslim-learning-Journal")
        self.Quran_label.setStatusTip("Log Qur'an Progress")
        self.other_label.setStatusTip("Log other Progress")
        self.save_label.setStatusTip("Save all changes")
        self.view_label.setStatusTip("View entries from a specific date")
        self.exit_label.setStatusTip("Exit")

        self.menu = QGridLayout(self)
        # self.menu.setVerticalSpacing(15)
        self.menu.setContentsMargins(25, 25, 25, 25)
        self.menu.addWidget(self.title, 0, 0, 1, 3)
        self.menu.addWidget(self.Quran_label, 1, 0, 1, 2)
        self.menu.addWidget(self.other_label, 2, 0, 1, 2)
        self.menu.addWidget(self.stats_label, 1, 2, 2, 1)
        self.menu.addWidget(self.save_label, 3, 0, 1, 1)
        self.menu.addWidget(self.view_label, 3, 1, 1, 1)
        self.menu.addWidget(self.edit_label, 3, 2, 1, 1)
        self.menu.addWidget(self.exit_label, 4, 0, 1, 3)
        self.display_stats_today()
    
    def display_stats_today(self):
        stats_manager = self.main_window.context.stats_manager
        stats_manager.aggregator.calculate_stats_today()
        entry_count = stats_manager.aggregator.stats_today[0]
        stats = (
                f"Today\n\n{entry_count} {'entries' if entry_count > 1 else 'entry'}\n"
                f"{stats_manager.aggregator.stats_today[2]} page(s)\n"
                f"{CoreHelpers.format_time(stats_manager.aggregator.stats_today[1])}"
            )
        self.stats_label.setText(stats)


class QuranKareemScreen(BaseScreen):

    def __init__(self, main_window):

        # Tafseer Form
        self.Tafseer_form = QuranKareemForm(main_window)

        # Tilawat Form
        self.Tilawat_form = QuranKareemForm(main_window, Tafseer=False)

        # Quran Tabs
        self.tabs_widget = QTabWidget()
        self.tabs_widget.addTab(self.Tafseer_form, QIcon("./images/Quran.jpg"), "Tafseer")
        self.tabs_widget.addTab(self.Tilawat_form, QIcon("./images/Quran.jpg"), "Tilawat")
        super().__init__("AL Quran Kareem", self.tabs_widget, main_window.get_back_label())

    def keyPressEvent(self, event) -> None:
        super().keyPressEvent(event)
        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            if self.tabs_widget.currentIndex() == 0:
                self.Tafseer_form.submit_form()
            elif self.tabs_widget.currentIndex() == 1:
                self.Tilawat_form.submit_form()


class OtherSubjectsScreen(BaseScreen):
    def __init__(self, main_window, title="Other Subjects"):
        self.other_subjects_form = OtherSubjectsForm(main_window)
        super().__init__(title, self.other_subjects_form, main_window.get_back_label())
        
    def keyPressEvent(self, event) -> None:
        super().keyPressEvent(event)
        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            self.other_subjects_form.submit_form()

class EditorScreen(BaseScreen):
    def __init__(self, main_window):
        self.main_window = main_window
        self.main_widget = QWidget(main_window)
        main_label = ClickableLabel("Select an Entry")
        self.del_btn = QPushButton("Delete this Entry")
        self.main_layout = QVBoxLayout(self.main_widget)
        
        self.pic_label = QLabel('<img src="./images/diary.png" width="300" height="300">')
        self.pic_label.setMinimumSize(main_window.width() - 20, main_window.height() - 200)
        self.pic_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(main_label)
        self.main_layout.addWidget(self.pic_label)
        self.main_layout.addWidget(self.del_btn)
        self.del_btn.hide()
        
        main_label.leftClicked.connect(self.get_details) # type: ignore
        self.del_btn.clicked.connect(self.del_entry)
        super().__init__("", self.main_widget, main_window.get_back_label())

    def keyPressEvent(self, event) -> None:
        super().keyPressEvent(event)
        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            if hasattr(self, "form"):
                self.complete_editing()
            else:
                self.get_details()

    def remove_form(self):
        if not hasattr(self, "form"):
            return
        if self.form is None:
            return
        self.main_layout.removeWidget(self.form)
        self.form.deleteLater()
        self.form = None
        self.del_btn.hide()

    def get_details(self):
        details = EntryEditService.get_date_entry_form(self.main_window)
        if not details:
            return
        self.date_entry, self.session, self.entries_day, self.original_entry, form = details
        self.setup_form(form)

    def setup_form(self, form):
        self.main_layout.removeWidget(self.pic_label)
        self.remove_form()

        self.form = form
        form_dict = self.original_entry.to_form_dict()
        self.form.load_entry(form_dict)
        self.form.set_edit_mode(self.complete_editing)

        self.del_btn.show()
        self.main_layout.insertWidget(1, self.form)

    def complete_editing(self) -> None:
        if not MsgDialogs.get_answer(self.main_window, "Are you sure?"):
            return
        edited_entry = self.form.submit_form(add_entry=False) # type: ignore
        if not edited_entry:
            return
        original_storage = self.original_entry.to_dict()
        edited_entry_dict = edited_entry.to_dict()
        EntryEditService.update_stats(self.main_window, original_storage, edited_entry_dict, edited_entry.subject, edited_entry.book, self.session)
        self.entries_day[edited_entry.subject][edited_entry.book][self.session] = edited_entry_dict
        self.original_entry = edited_entry
        self.main_window.context.data_manager.update_entry_log(self.date_entry, self.entries_day)
        self.main_window.main_menu.display_stats_today()

    def del_entry(self):
        if not MsgDialogs.get_answer(self.main_window, "Are you sure you want to delete?"):
            return
        self.remove_form()
        self.main_layout.addWidget(self.pic_label)
        details = (self.original_entry.subject, self.original_entry.book, self.session, self.date_entry)
        EntryEditService.delete_an_entry(self.main_window, self.entries_day, details)
        self.main_window.main_menu.display_stats_today()
        msg = f"\n\nDetails:\n\nSubject: {self.original_entry.subject}\nBook: {self.original_entry.book}\nEntry: {self.session}"
        MsgDialogs.show_information_msg(self.main_window, "Entry deleted successfully!" + msg)


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
        self.date_selector = DateSelector("View Entries from", self)
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