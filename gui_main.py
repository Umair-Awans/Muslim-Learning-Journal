import sys
from io import StringIO
from datetime import datetime
from PyQt5.QtGui import QIcon, QIntValidator, QDoubleValidator
from PyQt5.QtCore import Qt, QRect, QTimer, QDate, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QGridLayout, QAction, QHBoxLayout,
                             QCheckBox, QMessageBox, QVBoxLayout,
                             QScrollArea, QMenu, QLabel, QDateEdit,
                             QFormLayout, QLineEdit, QStackedLayout,
                             QComboBox, QTabWidget, QStatusBar,
                             QTextBrowser, QPushButton, QTextEdit,
                             QRadioButton)

from gui_utils import ClickableLabel, GuiDataCollector, GuiUtilities, StyleUtilities
from entries import EntryFactory, DataCarrier
from core_utils import PasswordManager, DateManager, DeleteController
from file_manager import DataManager
from progress_tools import ProgressDisplay

DATA = DataManager()


class EntryFormWidget(QScrollArea):
    """
    ql = QLabel,
    qle = QLineEdit,
    qte = QTextEdit,
    qcb = QComboBox
    qchb = QCheckBox
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.entry_form_widget = QWidget()
        self.entry_form_layout = QVBoxLayout(self.entry_form_widget)
        self.setWidgetResizable(True)
        self.setWidget(self.entry_form_widget)

        self.qlPage, self.qlePage1, self.qlePage2 = self.make_triplet(
            "Page:", 1.0, 9999.0)
        self.qlTime, self.qleTime1, self.qleTime2 = self.make_triplet(
            "Time Spent:", 0.0, 60.0, "Hours", "Minutes")
        self.qleTime1.setValidator(QIntValidator(0, 90))
        self.qleTime2.setValidator(QIntValidator(0, 60))
        self.qlNotes, self.qteNotes = QLabel("\nNotes:"), QTextEdit()
        self.qlRevision, self.qteRevision = QLabel(
            "\nRevision:"), QTextEdit()
        self.qlReadingMode = QLabel("Reading Sequentially?")
        self.qchbReadingMode = QCheckBox()
        self.submit_label = ClickableLabel("Submit")

        StyleUtilities.styleWidgets(self.submit_label)
        StyleUtilities.styleFormElements(self.entry_form_widget)

        self.commons_widget = QWidget()
        self.commons_layout = QGridLayout(self.commons_widget)
        self.commons_layout.addWidget(self.qlPage, 0, 0, 1, 1)
        self.commons_layout.addWidget(self.qlePage1, 0, 1, 1, 1)
        self.commons_layout.addWidget(self.qlePage2, 0, 2, 1, 1)
        self.commons_layout.addWidget(self.qlTime, 1, 0, 1, 1)
        self.commons_layout.addWidget(self.qleTime1, 1, 1, 1, 1)
        self.commons_layout.addWidget(self.qleTime2, 1, 2, 1, 1)
        self.commons_layout.addWidget(self.qlNotes, 2, 0, 3, 1)
        self.commons_layout.addWidget(self.qteNotes, 2, 1, 3, 2)
        self.commons_layout.addWidget(self.qlRevision, 5, 0, 3, 1)
        self.commons_layout.addWidget(self.qteRevision, 5, 1, 3, 2)
        self.commons_layout.addWidget(self.qlReadingMode, 8, 0, 1, 2)
        self.commons_layout.addWidget(self.qchbReadingMode, 8, 2, 1, 1)
        self.commons_layout.addWidget(self.submit_label, 9, 0, 1, 3)

    def make_triplet(self,
                     label_text,
                     min_val,
                     max_val,
                     placeholder1="From",
                     placeholder2="To"):
        label = QLabel(label_text)
        input1 = QLineEdit()
        input1.setValidator(QDoubleValidator(min_val, max_val, 2))
        input1.setPlaceholderText(placeholder1)

        input2 = QLineEdit()
        input2.setValidator(QDoubleValidator(min_val, max_val, 2))
        input2.setPlaceholderText(placeholder2)

        return label, input1, input2

    def collect_common_raw_input(self):
        return {
        "page_from": self.qlePage1.text(), 
        "page_to": self.qlePage2.text(),
        "hours": self.qleTime1.text(),
        "minutes": self.qleTime2.text(),
        "notes": self.qteNotes.toPlainText(),
        "reading_mode": self.qchbReadingMode.isChecked(),
        "revision": self.qteRevision.toPlainText(),
        }

    
class QuranKareemForm(EntryFormWidget):

    def __init__(self, Tafseer=True, parent=None):
        super().__init__(parent)
        self.Tafseer = Tafseer
        self.form_widget = QWidget()
        self.form_layout = QGridLayout(self.form_widget)

        self.entry_form_layout.addWidget(self.form_widget)
        self.entry_form_layout.addWidget(self.commons_widget)

        self.qlPara, self.qlePara1, self.qlePara2 = self.make_triplet(
            "Para:", 1.0, 30.0)
        self.qlRuku, self.qleRuku1, self.qleRuku2 = self.make_triplet(
            "Ruku (Para):", 1.0, 9999.0)

        # Make them the same width so they look visually aligned
        self.qlPage.setMinimumWidth(170)
        self.qlPara.setMinimumWidth(170)

        if self.Tafseer:
            self.qlSurah, self.qleSurah1, self.qleSurah2 = self.make_triplet(
                "Surah:", 1.0, 114.0)
            self.qlAyah, self.qleAyah1, self.qleAyah2 = self.make_triplet(
                "Ayah:", 1.0, 9999.0)

            self.add_to_layout([
                (self.qlPara, self.qlePara1, self.qlePara2),
                (self.qlSurah, self.qleSurah1, self.qleSurah2),
                (self.qlAyah, self.qleAyah1, self.qleAyah2),
                (self.qlRuku, self.qleRuku1, self.qleRuku2)
            ])
        else:
            self.add_to_layout([
                (self.qlPara, self.qlePara1, self.qlePara2),
                (self.qlRuku, self.qleRuku1, self.qleRuku2)
            ])

        self.submit_label.leftClicked.connect(self.submit_form) #type: ignore

    def add_to_layout(self, *widgets):
        """
        Adds widgets in rows: 
        Each row has a label + 'From' field + 'To' field.
        Example:
        [Label] [From-input] [To-input]
        """
        row = 0
        # Iterate through widgets in groups of three: (Label, From, To)
        for tuple_ in widgets:
            for label, from_input, to_input in tuple_:
                self.form_layout.addWidget(label, row, 0)
                self.form_layout.addWidget(from_input, row, 1)
                self.form_layout.addWidget(to_input, row, 2)

                # Apply placeholders for input fields
                if hasattr(from_input, "setPlaceholderText"):
                    from_input.setPlaceholderText("From")
                if hasattr(to_input, "setPlaceholderText"):
                    to_input.setPlaceholderText("To")

                row += 1  # Move to next row


    def collect_raw_input(self):
        if self.Tafseer:
            return {
                "Para_from": self.qlePara1.text(),
                "Para_to": self.qlePara2.text(),
                "Ruku_from": self.qleRuku1.text(),
                "Ruku_to": self.qleRuku2.text(),
                "Surah_from": self.qleSurah1.text(),
                "Surah_to": self.qleSurah2.text(),
                "Ayah_from": self.qleAyah1.text(),
                "Ayah_to": self.qleAyah2.text()
            }
        else:
            return {
                "Para_from": self.qlePara1.text(),
                "Para_to": self.qlePara2.text(),
                "Ruku_from": self.qleRuku1.text(),
                "Ruku_to": self.qleRuku2.text()
            }


    def submit_form(self):
        if self.Tafseer:
            subject = "Al-Qur'an (Tafseer)"
        else:
            subject = "Al-Qur'an (Tilawat)"
        entry, msg = EntryFactory.make_Quran_entry({"form": self, "book": subject}, GuiDataCollector) # type: ignore
        if not entry:
            GuiUtilities.show_warning_msg(self, msg)
            return
        print()
        print(subject)
        print(entry.to_dict())
        DATA.add_entry(subject, entry.book, entry.to_dict())
        UnsavedEntries.unsaved_entries.update({f"{subject}\n{entry.book}": entry})
        GuiUtilities.show_information_msg(self, "Entry successful!")
        

class OtherSubjectsForm(EntryFormWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.form_widget = QWidget()
        self.form_layout = QGridLayout(self.form_widget)
        
        self.entry_form_layout.addWidget(self.form_widget)
        self.entry_form_layout.addWidget(self.commons_widget)

        self.qlSubject, self.qcbSubject = self.get_label_and_comboBox("Subject:")
        
        self.qlBook, self.qcbBook = self.get_label_and_comboBox("Book:")

        self.qlUnit, self.qleUnit1, self.qleUnit2 = self.make_triplet("Unit", 1.0, 9999.0)
        self.qlChapter, self.qleChapter = QLabel(
            "Chapter:"), QLineEdit()

        # Make them the same width so they look visually aligned
        self.qlPage.setMinimumWidth(155)
        self.qlSubject.setMinimumWidth(155)

        self.qcbSubject.currentTextChanged.connect(self.populate_books)
        self.submit_label.leftClicked.connect(self.submit_form) #type: ignore

        self.form_layout.addWidget(self.qlSubject, 0, 0, 1, 1)
        self.form_layout.addWidget(self.qcbSubject, 0, 1, 1, 2)
        self.form_layout.addWidget(self.qlBook, 1, 0, 1, 1)
        self.form_layout.addWidget(self.qcbBook, 1, 1, 1, 2)
        self.form_layout.addWidget(self.qlUnit, 2, 0, 1, 1)
        self.form_layout.addWidget(self.qleUnit1, 2, 1, 1, 1)
        self.form_layout.addWidget(self.qleUnit2, 2, 2, 1, 1)
        self.form_layout.addWidget(self.qlChapter, 3, 0, 1, 1)
        self.form_layout.addWidget(self.qleChapter, 3, 1, 1, 2)
        self.populate_combo_boxes()

    def populate_combo_boxes(self):
        self.subjects = DATA.all_time_subjects
        self.qcbSubject.addItems(self.subjects.keys())
        self.populate_books()
    
    def populate_books(self):
        subject = self.qcbSubject.currentText().strip()
        books_list = self.subjects.get(subject, [])
        self.qcbBook.clear()
        self.qcbBook.addItems(books_list)

    def get_label_and_comboBox(self, label_text: str):
        label = QLabel(label_text)
        combo_box = QComboBox()
        combo_box.setEditable(True)
        combo_box.setInsertPolicy(QComboBox.InsertAlphabetically)

        return label, combo_box

    def collect_raw_input(self):
        return {
            "subject": self.qcbSubject.currentText(),
            "book": self.qcbBook.currentText(),
            "unit_from": self.qleUnit1.text(),
            "unit_to": self.qleUnit2.text(),
            "chapter": self.qleChapter.text()
            }
        
    def submit_form(self):
        subject = self.qcbSubject.currentText()        
        entry, msg = EntryFactory.make_other_entry({"form": self}, GuiDataCollector) # type: ignore
        if not entry:
            GuiUtilities.show_warning_msg(self, msg)
            return
        print("\n",subject , "\n",entry.to_dict())
        DATA.add_entry(subject, entry.book, entry.to_dict())
        UnsavedEntries.unsaved_entries.update({f"{subject}\n{entry.book}": entry})
        GuiUtilities.show_information_msg(self, "Entry successful!")


class MainMenuScreen(QWidget):

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        # Widgets
        self.title = QLabel("Muslim Learning Journal")
        self.Quran_label = ClickableLabel("Al Qur'an Kareem")
        self.other_label = ClickableLabel("Other Subjects")
        self.save_label = ClickableLabel("Save Progress")
        self.view_label = ClickableLabel("View Progress")
        self.delete_label = ClickableLabel("Delete Progress")
        self.exit_label = ClickableLabel("Exit")
        StyleUtilities.styleWidgets(self.title, self.Quran_label, self.other_label,
                               self.save_label, self.view_label,
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
        self.exit_label.leftClicked.connect(self.main_window.quit_program) #type: ignore

        self.menu = QGridLayout(self)
        # self.menu.setVerticalSpacing(15)
        self.menu.setContentsMargins(25, 25, 25, 25)
        self.menu.addWidget(self.title, 0, 0, 1, 3)
        self.menu.addWidget(self.Quran_label, 1, 0, 1, 3)
        self.menu.addWidget(self.other_label, 2, 0, 1, 3)
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

    def __init__(self, go_back_label):

        # **Quran-Forms**
        # Tafseer Form
        self.Tafseer_form = QuranKareemForm()

        # Tilawat Form
        self.Tilawat_form = QuranKareemForm(False)

        # Quran Tabs
        self.tabs_widget = QTabWidget()
        self.tabs_widget.addTab(self.Tafseer_form, QIcon("./images/Quran.jpg"), "Tafseer")
        self.tabs_widget.addTab(self.Tilawat_form, QIcon("./images/Quran.jpg"), "Tilawat")

        super().__init__("AL Quran Kareem", self.tabs_widget, go_back_label)


class EntryDisplay:
    @staticmethod
    def format_entry_html(buffer: StringIO, heading: str, entry: dict):
        buffer.write(f"<h2>{heading}</h2><br>\n<pre align='left'>\n")
        for key, value in entry.items():
            buffer.write(f">>> {key}: {value}<br><br>")
        buffer.write(f"\n</pre><hr><br>")

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


class UnsavedEntries:
    unsaved_entries = {}

    @classmethod
    def clear_all(cls):
        cls.unsaved_entries.clear()

    @classmethod
    def to_html(cls):
        if not cls.unsaved_entries:
            return "<h2>No unsaved entries</h2>"
        buffer = StringIO()
        buffer.write(f"<h2>Unsaved Entries: {len(cls.unsaved_entries)}</h2><br>")

        for i, (key, entry) in enumerate(cls.unsaved_entries.items(), 1):
            buffer.write(f"<h2>Entry no. {i}<h2><br>")
            EntryDisplay.format_entry_html(buffer, key, entry.to_dict())

        return buffer.getvalue()


class OtherSubjectsScreen(BaseScreen):
    def __init__(self, go_back_label):
        super().__init__("Other Subjects", OtherSubjectsForm(), go_back_label)


class SaveScreen(BaseScreen):
    def __init__(self, go_back_label):
        self.content_widget = QWidget()
        super().__init__("Save Progress", self.content_widget, go_back_label)

        self.tb = QTextBrowser()
        self.tb.setStyleSheet("background: rgb(220, 220, 220);")
        self.save = ClickableLabel("Save")
        self.save.leftClicked.connect(self.save_progress) #type: ignore
        layout = QVBoxLayout(self.content_widget)
        layout.addWidget(self.tb)
        layout.addWidget(self.save)

        StyleUtilities.styleWidgets(self.save)

    def showEvent(self, event):
        super().showEvent(event)
        self.show_unsaved_entries()

    def show_unsaved_entries(self):
        self.tb.setHtml(f"<pre align='center'>{UnsavedEntries.to_html()}</pre>")

    def save_progress(self):
        return_code =  DATA.save_progress_to_files()
        if return_code == 0:
            GuiUtilities.show_information_msg(self, "Progress saved successfully!")
            UnsavedEntries.clear_all()
            self.show_unsaved_entries()
        elif return_code == 1:
            GuiUtilities.show_critical_msg(self, "Could not save JSON file.")
        elif return_code == 2:
            GuiUtilities.show_critical_msg(self, "Could not save Markdown file.")


class DateSelector(QWidget):
    dateSelected = pyqtSignal(QDate)
    def __init__(self, label_text: str ,parent=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        self.date_edit = QDateEdit()
        self.submit = ClickableLabel(label_text)
        layout.addWidget(self.submit)
        layout.addWidget(self.date_edit)
        StyleUtilities.styleWidgets(self.submit)
        self.submit.leftClicked.connect(lambda: self.dateSelected.emit(self.date_edit.date())) # type: ignore

    def showEvent(self, event):
        super().showEvent(event)
        self.date_edit.setDate(QDate(datetime.today().year, datetime.today().month, datetime.today().day))


class ViewScreen(BaseScreen):
    def __init__(self, go_back_label):
        self.content_widget = QWidget()
        super().__init__("View Progress", self.content_widget, go_back_label)

        layout = QVBoxLayout(self.content_widget)
        self.date_selector = DateSelector("View Entries from")
        self.display = QTextBrowser()
        self.display.setStyleSheet("background: rgb(220, 220, 220);")
        layout.addWidget(self.date_selector)
        layout.addWidget(self.display)
        self.date_selector.dateSelected.connect(self.get_date) # type: ignore

    def get_date(self, date: QDate):
        formatted = date.toString("dd-MMM-yyyy")
        self.show_progress(formatted)

    def show_progress(self, date: str):
        entries = DATA.get_entries_from_date(date)
        if entries:
            formatted = EntryDisplay.format_day_entries_html(date, entries)
            self.display.setHtml(f"<pre align='center'>{formatted}</pre>")
        else:
            self.display.setHtml(f"<pre align='center'><h2>No entries found for {date}.<br>Please try another date.</h2></pre>")
            

class DeleteScreen(BaseScreen):
    def __init__(self, go_back_label):
        self.content_widget = QWidget()
        super().__init__("Delete Progress", self.content_widget, go_back_label)
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
        date_selector.dateSelected.connect(self.get_date) # type: ignore
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
                deleted, msg = DeleteController.delete_day(today, DATA)
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
            deleted, msg = DeleteController.delete_day(formatted, DATA)
            if deleted:
                GuiUtilities.show_information_msg(self, msg)
            else:
                GuiUtilities.show_critical_msg(self, msg)
        self.stacked_layout.setCurrentWidget(self.menu)

    def delete_all(self):
        if not GuiUtilities.get_answer(self, f"This will delete all time progress.\nContinue?\n", title="Delete Confirmation"):
            return
        password = self.password_edit.text()
        deleted, msg = DeleteController.delete_all(password, DATA)
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
    # def paintEvent(self, event):
    #     painter = QPainter(self)
    #     gradient = QLinearGradient(0, 0, self.width(), self.height())
    #     gradient.setColorAt(0.0, QColor("#34495e"))
    #     gradient.setColorAt(1.0, QColor("#2c3e50"))
    #     painter.fillRect(self.rect(), gradient)

    def __init__(self):
        super().__init__()

        # MainWindow's Setup
        self.setGeometry(150, 100, 900, 600)
        self.setWindowTitle("Muslim Learning Journal")
        self.setWindowIcon(QIcon("./images/Diary.png"))

        # All Screens
        self.main_menu = MainMenuScreen(self)
        self.Quran_Kareem = QuranKareemScreen(self.get_back_label())
        self.other_subjects = OtherSubjectsScreen(self.get_back_label())
        self.save_screen = SaveScreen(self.get_back_label())
        self.view_screen = ViewScreen(self.get_back_label())
        self.delete_screen = DeleteScreen(self.get_back_label())

        # Central Widget
        central_widget = QWidget()
        central_widget.setStyleSheet("background: #F2F2F2;")
        self.setCentralWidget(central_widget)
        self.stacked_layout = QStackedLayout(central_widget)

        self.stacked_layout.addWidget(self.main_menu)
        self.stacked_layout.addWidget(self.Quran_Kareem)
        self.stacked_layout.addWidget(self.other_subjects)
        self.stacked_layout.addWidget(self.save_screen)
        self.stacked_layout.addWidget(self.view_screen)
        self.stacked_layout.addWidget(self.delete_screen)
        self.setStatusBar(QStatusBar())
        self.setup_password_gate()

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

    def quit_program(self):
        if GuiUtilities.get_answer(self, "Any unsaved changes will be lost.\nAre you sure you want to exit?", title="Exit Confirmation"):
            QApplication.quit()


def main():
    app = QApplication(sys.argv)
    StyleUtilities.applyGlobalStyles(app)
    window = MainWindow()
    window.show()
    window.raise_()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
