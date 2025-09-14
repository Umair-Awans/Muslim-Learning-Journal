import sys
from PyQt5.QtGui import QIcon, QIntValidator,QDoubleValidator
from PyQt5.QtCore import Qt, QRect, QTimer
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, 
                             QGridLayout, QAction, QFileDialog,
                             QCheckBox, QMessageBox, QVBoxLayout,
                             QScrollArea, QMenu, QLabel,
                             QFormLayout, QLineEdit, QStackedLayout,
                             QComboBox, QTabWidget, QStatusBar,
                             QTextBrowser, QPushButton, QTextEdit)

sys.path.append("../Modules")
from MyQt5 import ClickableLabel
from entries import EntryFactory, DataCarrier
from core_utils import Utilities, ProgressUtils, PasswordManager
from file_manager import DataManager

DATA = DataManager()


class DataProcessor:
    @staticmethod
    def stoi(data: dict):
        for key in data.keys():
            if not "from" in key and not "to" in key:
                continue
            data[key] = float(data[key] or "0")
            if data[key] == int(data[key]):
                data[key] = int(data[key])

    @classmethod
    def validate_pair_fields(cls, pair_fields: list):
        for field_name, field1, field2 in pair_fields:
            ok, msg = FormValidation.verify_range_fields(field_name, field1, field2)
            if not ok:
                return False, msg
        return True, ""

    @staticmethod
    def finalize_common_data(book: str,carrier: DataCarrier):
        page_from = carrier.common_raw_data["page_from"]
        page_to = carrier.common_raw_data["page_to"]
        hours = carrier.common_raw_data["hours"]
        minutes = carrier.common_raw_data["minutes"]
        notes = carrier.common_raw_data["notes"].strip() or "N/A"
        reading_mode = "Sequential" if carrier.common_raw_data["reading_mode"] else "Random"
        revision = carrier.common_raw_data["revision"].strip() or "No"
        pages, total_pages = ProgressUtils.get_str_and_total(page_from, page_to)
        time_spent = Utilities.get_time_str(hours, minutes)
        carrier.common_data = {
                "book": book,
                "pages": pages,
                "total_pages": total_pages,
                "time_spent": time_spent,
                "notes": notes,
                "reading_mode": reading_mode,
                "revision": revision
            }
        return True

    @classmethod
    def process_common_data(cls, carrier: DataCarrier):
        cls.stoi(carrier.common_raw_data)
        valid, msg = cls.validate_pair_fields([("Page", carrier.common_raw_data["page_from"], carrier.common_raw_data["page_to"])])
        if not valid:
            return False, msg
        return FormValidation.both_fields_empty("Time Spent", carrier.common_raw_data["hours"], carrier.common_raw_data["minutes"])

    @classmethod
    def finalize_Quran_data(cls, carrier: DataCarrier):
        Para = ProgressUtils.get_str_and_total(carrier.raw_data["Para_from"], carrier.raw_data["Para_to"])[0]
        Ruku, tota_Ruku = ProgressUtils.get_str_and_total(carrier.raw_data["Ruku_from"], carrier.raw_data["Ruku_to"])
        Para = f"Para no. {Para}"
        carrier.data = {"Ruku": Ruku, "total_Ruku": tota_Ruku}
        if "Surah_from" in carrier.raw_data:
            Surah_from = carrier.raw_data["Surah_from"]
            Surah_to = carrier.raw_data["Surah_to"]
            Ayah_from = carrier.raw_data["Ayah_from"]
            Ayah_to = carrier.raw_data["Ayah_to"]
            carrier.data["Surah_number"] = ProgressUtils.get_str_and_total(Surah_from, Surah_to)[0]
            carrier.data["Ayah"], carrier.data["total_Aayat"] = ProgressUtils.get_str_and_total(Ayah_from, Ayah_to)
        return cls.finalize_common_data(Para, carrier)

    @classmethod
    def process_Quran_data(cls, carrier: DataCarrier):
        cls.stoi(carrier.raw_data)
        pairs = []
        pairs.append(("Para", carrier.raw_data["Para_from"], carrier.raw_data["Para_to"]))
        if "Surah_from" in carrier.raw_data:
            pairs.append(("Surah", carrier.raw_data["Surah_from"], carrier.raw_data["Surah_to"]))
            pairs.append(("Ayah", carrier.raw_data["Ayah_from"], carrier.raw_data["Ayah_to"]))
        pairs.append(("Ruku", carrier.raw_data["Ruku_from"], carrier.raw_data["Ruku_to"]))
        valid, msg = cls.validate_pair_fields(pairs)
        if not valid:
            return False, msg
        valid, msg = cls.process_common_data(carrier)
        if not valid:
            return False, msg
        return cls.finalize_Quran_data(carrier), "Failed to save data"

    @classmethod
    def finalize_other_data(cls, carrier: DataCarrier):
        subject = carrier.raw_data["subject"].strip()
        book = carrier.raw_data["book"].strip()

        if not subject or not book:
            return False, "Can't leave Subject or Book field empty"

        carrier.data["unit"] = ProgressUtils.get_str_and_total(carrier.raw_data["unit_from"], carrier.raw_data["unit_to"])[0]
        carrier.data["chapter"] = carrier.raw_data["chapter"].strip() or "N/A"
        return cls.finalize_common_data(book, carrier)

    @classmethod
    def process_other_data(cls, carrier: DataCarrier):
        cls.stoi(carrier.raw_data)
        pairs = [("Unit", carrier.raw_data["unit_from"], carrier.raw_data["unit_to"])]
        valid, msg = cls.validate_pair_fields(pairs)
        if not valid:
            return False, msg
        valid, msg = cls.process_common_data(carrier)
        if not valid:
            return False, msg
        return cls.finalize_other_data(carrier), "Failed to save data"

        
class StyleUtilities:

    @staticmethod
    def get_gradient(hover: bool, title: bool = False) -> str:
        if title:
            top_color = "#E6E6E6" if not hover else "#F2F2F2"
            bottom_color = "#BFBFBF" if not hover else "#D9D9D9"
        else:
            top_color = "#D9D9D9" if not hover else "#E6E6E6"
            bottom_color = "#BFBFBF" if not hover else "#CCCCCC"

        return f"""qlineargradient(
            spread:pad,
            x1:0, y1:0, x2:0, y2:1,
            stop:0 {top_color},
            stop:1 {bottom_color});"""

    @classmethod
    def styleWidgets(cls, *widgets, form_labels=False):
        for widget in widgets:
            FONT = 'Segoe Script' if not isinstance(
                widget, ClickableLabel) else 'Fira code'
            FONT_SIZE = 35 if not isinstance(widget, ClickableLabel) else 30
            # FONT_COLOR = "#19c25f" if not isinstance(widget, ClickableLabel) else "#2077ce"
            FONT_COLOR = "#333333"
            BG_COLOR = cls.get_gradient(False) if isinstance(
                widget, ClickableLabel) else cls.get_gradient(False, True)
            widget.setAlignment(Qt.AlignCenter)
            normal_style = f"""QLabel{{
            border-radius: 5px;
            font-weight: 500;
            color: {FONT_COLOR};
            background: {BG_COLOR};
            font-size: {FONT_SIZE}px;
            font-family: {FONT}, Tahoma;
            padding: 10px;
            }}
            ClickableLabel:hover{{
            background: {cls.get_gradient(True)};
            }}"""
            pressed_style = f"""
                border-radius: 5px;
                font-weight: 500;
                color: #333333;
                background: {BG_COLOR};
                font-size: {FONT_SIZE}px;
                font-family: {FONT}, Tahoma;
                padding: 10px;
            """
            widget.setStyleSheet(normal_style)
            if isinstance(widget, ClickableLabel):
                widget.setPressedStyle(pressed_style)
            if form_labels:
                widget.setFixedWidth(550)

    @staticmethod
    def styleInputFields(*widgets, form_inputs=False):
        for widget in widgets:
            widget.setStyleSheet("""QLineEdit, QComboBox{
                background-color: none;
                font-size: 25px;
                padding: 10px;
            }""")
            if form_inputs:
                widget.setFixedWidth(250)

    @staticmethod
    def styleFormElements(*widgets):
        for widget in widgets:
            # widget.setMinimumWidth(280)
            widget.setMinimumHeight(40)
            widget.setStyleSheet("""QLineEdit, QTextEdit, QComboBox, QLabel{
                font-size: 25px;
                font-family: consolas;
                }
                QLineEdit, QTextEdit{
                    background-color: white;
                }""")
            if not isinstance(widget, QCheckBox) and not isinstance(
                    widget, QComboBox) and not isinstance(widget, QTextEdit):
                widget.setAlignment(Qt.AlignCenter)
            if isinstance(widget, QTextEdit):
                widget.setMinimumHeight(100)

            if isinstance(widget, QLabel):
                widget.setAlignment(Qt.AlignCenter)


class GuiUtilities:
    @staticmethod
    def show_information_msg(message: str):
        QMessageBox.information(QWidget(), 'Muslim Learning Journal',
                                    message,
                                    QMessageBox.Ok, QMessageBox.Ok)

    @staticmethod
    def show_warning_msg(message: str):
        QMessageBox.warning(QWidget(), 'Muslim Learning Journal',
                                    message,
                                    QMessageBox.Ok, QMessageBox.Ok)

    @staticmethod
    def show_critical_msg(message: str):
        QMessageBox.critical(QWidget(), 'Muslim Learning Journal',
                                    message,
                                    QMessageBox.Ok, QMessageBox.Ok)

class FormValidation:
    @staticmethod
    def both_fields_empty(field_name: str, field1, field2):
        if not field1 and not field2:
            return False, f"Can't leave {field_name} fields empty."
        return True, ""

    @staticmethod
    def are_fields_in_order(field_name: str, field1, field2):
        if field1 and field2 and not field1 <= field2:
            return False, f"{field_name}: 'From' field must be smaller than 'To' field"
        return True, ""

    @classmethod
    def verify_range_fields(cls, field_name: str, field1, field2):
        valid, msg = cls.both_fields_empty(field_name, field1, field2)
        if not valid:
            return False, msg
        return cls.are_fields_in_order(field_name, field1, field2)

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
        StyleUtilities.styleFormElements(self.qlPage, self.qlTime,
                                    self.qlNotes, self.qlReadingMode,
                                    self.qlRevision, self.qlePage1,
                                    self.qlePage2, self.qleTime1,
                                    self.qleTime2, self.qteNotes,
                                    self.qchbReadingMode, self.qteRevision)

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

        if Tafseer:
            self.qlSurah, self.qleSurah1, self.qleSurah2 = self.make_triplet(
                "Surah:", 1.0, 114.0)
            self.qlAyah, self.qleAyah1, self.qleAyah2 = self.make_triplet(
                "Ayah:", 1.0, 9999.0)

            StyleUtilities.styleFormElements(self.qlPara, self.qlePara1,
                                        self.qlePara2, self.qlSurah,
                                        self.qleSurah1, self.qleSurah2,
                                        self.qlAyah, self.qleAyah1,
                                        self.qleAyah2, self.qlRuku,
                                        self.qleRuku1, self.qleRuku2)
            self.add_to_layout([
                (self.qlPara, self.qlePara1, self.qlePara2),
                (self.qlSurah, self.qleSurah1, self.qleSurah2),
                (self.qlAyah, self.qleAyah1, self.qleAyah2),
                (self.qlRuku, self.qleRuku1, self.qleRuku2)
            ])
        else:
            StyleUtilities.styleFormElements(self.qlPara, self.qlePara1,
                                        self.qlePara2, self.qlRuku,
                                        self.qleRuku1, self.qleRuku2)
            self.add_to_layout([
                (self.qlPara, self.qlePara1, self.qlePara2),
                (self.qlRuku, self.qleRuku1, self.qleRuku2)
            ])

        self.submit_label.leftClicked.connect(self.submit_form)

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
        if hasattr(self, "qlSurah"):
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
        if hasattr(self, "qlSurah"):
            subject = "Al-Qur'an (Tafseer)"
        else:
            subject = "Al-Qur'an (Tilawat)"
        entry, msg = EntryFactory.make_Quran_entry({"form": self, "book": subject}, GuiDataCollector)
        if not entry:
            GuiUtilities.show_warning_msg(msg)
            return
        print()
        print(subject)
        print(entry.to_dict())
        DATA.add_entry(subject, entry.book, entry.to_dict())
        UnsavedEntries.unsaved_entries.append(entry)
        GuiUtilities.show_information_msg("Entry successful!")
        

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
        self.submit_label.leftClicked.connect(self.submit_form)

        StyleUtilities.styleFormElements(self.qlSubject, self.qcbSubject,
                                    self.qlBook, self.qcbBook,
                                    self.qlUnit, self.qleUnit1, self.qleUnit2,
                                    self.qlChapter, self.qleChapter)

        self.setStyleSheet("QComboBox{background-color: white;}")
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
        entry, msg = EntryFactory.make_other_entry({"form": self}, GuiDataCollector)
        if not entry:
            GuiUtilities.show_warning_msg(msg)
            return
        print("\n",subject , "\n",entry.to_dict())
        DATA.add_entry(subject, entry.book, entry.to_dict())
        UnsavedEntries.unsaved_entries.append(entry)
        GuiUtilities.show_information_msg("Entry successful!")


class GuiDataCollector:
    @staticmethod
    def collect_common_raw_data(form: EntryFormWidget, carrier: DataCarrier):
        carrier.common_raw_data = form.collect_common_raw_input()

    @classmethod
    def collect_raw_data(cls, form: EntryFormWidget, carrier: DataCarrier):
        cls.collect_common_raw_data(form, carrier)
        carrier.raw_data = form.collect_raw_input()

    @classmethod
    def collect_Quran_data(cls, carrier: DataCarrier, args: dict):
        form = args["form"]
        cls.collect_raw_data(form, carrier)
        return DataProcessor.process_Quran_data(carrier)

    @classmethod
    def collect_other_data(cls, carrier: DataCarrier, args: dict):
        form = args["form"]
        cls.collect_raw_data(form, carrier)
        return DataProcessor.process_other_data(carrier)
        

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
        self.Quran_label.leftClicked.connect(
            lambda: self.main_window.switch_screens(self.main_window.
                                                    Quran_Kareem))
        self.other_label.leftClicked.connect(
            lambda: self.main_window.switch_screens(self.main_window.
                                                    other_subjects))
        self.save_label.leftClicked.connect(
            lambda: self.main_window.switch_screens(self.main_window.
                                                    save_screen))
        self.view_label.leftClicked.connect(
            lambda: self.main_window.switch_screens(self.main_window.
                                                    view_screen))
        self.delete_label.leftClicked.connect(
            lambda: self.main_window.switch_screens(self.main_window.
                                                    delete_screen))
        self.exit_label.leftClicked.connect(self.main_window.quit_program)

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
        self.tabs_widget.addTab(self.Tafseer_form, "Tafseer")
        self.tabs_widget.addTab(self.Tilawat_form, "Tilawat")
        self.tabs_widget.setStyleSheet(
            "QTabBar{font-size: 12pt; font-family: Fira code;}")

        super().__init__("AL Quran Kareem", self.tabs_widget, go_back_label)

class UnsavedEntries:
    unsaved_entries = []

    @classmethod
    def clear_all(cls):
        cls.unsaved_entries.clear()

    @classmethod
    def to_text(cls):
        if cls.unsaved_entries:
            lines = [f"Unsaved Entries: {len(cls.unsaved_entries)}\n"]

            for i, entry in enumerate(cls.unsaved_entries, 1):
                lines.append(f"Entry no. {i}\n")
                for key, value in entry.to_dict().items():
                    lines.append(f"{key}: {value}")
                lines.append("")  # blank line between entries

            return "\n".join(lines)
        else:
            return "No unsaved entries"


class OtherSubjectsScreen(BaseScreen):
    def __init__(self, go_back_label):
        super().__init__("Other Subjects", OtherSubjectsForm(), go_back_label)


class SaveScreen(BaseScreen):
    def __init__(self, go_back_label):
        self.content_widget = QWidget()
        super().__init__("Save Progress", self.content_widget, go_back_label)

        self.tb = QTextBrowser()
        self.save = ClickableLabel("Save")
        StyleUtilities.styleWidgets(self.save)
        self.save.leftClicked.connect(self.save_progress)
        self.layout_ = QVBoxLayout(self.content_widget)
        self.layout_.addWidget(self.tb)
        self.layout_.addWidget(self.save)

        self.tb.setStyleSheet("""
        QTextBrowser{
            font-size: 25px;
            font-family: consolas;
        }
        """)
        self.tb.setAlignment(Qt.AlignCenter)

    def showEvent(self, event):
        super().showEvent(event)
        self.show_unsaved_entries()

    def show_unsaved_entries(self):
        self.tb.setText(UnsavedEntries.to_text())

    def save_progress(self):
        return_code =  DATA.save_progress_to_files()
        if return_code == 0:
            GuiUtilities.show_information_msg("Progress saved successfully!")
            UnsavedEntries.clear_all()
            self.show_unsaved_entries()
        elif return_code == 1:
            GuiUtilities.show_critical_msg("Could not save JSON file.")
        elif return_code == 2:
            GuiUtilities.show_critical_msg("Could not save Markdown file.")


class ViewScreen(BaseScreen):
    def __init__(self, go_back_label):

        self.content_widget = QWidget()

        super().__init__("View Progress", self.content_widget, go_back_label)


class DeleteScreen(BaseScreen):

    def __init__(self, go_back_label):

        self.content_widget = QWidget()

        super().__init__("Delete Progress", self.content_widget, go_back_label)


class PasswordScreen(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.layout = QFormLayout(self)
        self.qlStatus = QLabel("No password has been set. Please set one to continue.")
        self.qlPassword = QLabel("Enter Password:")
        self.qlConfirm = QLabel("Confirm Password:")
        self.qlePassword = QLineEdit()
        self.qleConfirm = QLineEdit()
        self.qpbSubmit = QPushButton("Submit")
        self.qpbSubmit.clicked.connect(self.set_password)

        self.layout.addRow(self.qlStatus)
        self.layout.addRow(self.qlPassword, self.qlePassword)
        self.layout.addRow(self.qlConfirm, self.qleConfirm)
        self.layout.addRow(self.qpbSubmit)

    def set_password(self):
        if self.qlePassword.text().strip() == self.qleConfirm.text().strip():
            saved, msg = PasswordManager.store_password(self.qlePassword.text().strip())
            if saved:
                GuiUtilities.show_information_msg(msg)
            else:
                GuiUtilities.show_critical_msg(msg)
                return
            self.main_window.go_back()
            self.main_window.stacked_layout.removeWidget(self)
            self.deleteLater()
        else:
            GuiUtilities.show_critical_msg("Passwords do not match.\nEnter again.")



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
        self.setStyleSheet("QMainWindow { background-color: #F2F2F2;}")
        # self.showMaximized()

        # All Screens
        self.main_menu = MainMenuScreen(self)
        self.Quran_Kareem = QuranKareemScreen(self.get_back_label())
        self.other_subjects = OtherSubjectsScreen(self.get_back_label())
        self.save_screen = SaveScreen(self.get_back_label())
        self.view_screen = ViewScreen(self.get_back_label())
        self.delete_screen = DeleteScreen(self.get_back_label())

        # Central Widget
        central_widget = QWidget()
        central_widget.setStyleSheet("background: transparent;")
        self.setCentralWidget(central_widget)
        self.stacked_layout = QStackedLayout(central_widget)


        self.stacked_layout.addWidget(self.main_menu)
        self.stacked_layout.addWidget(self.Quran_Kareem)
        self.stacked_layout.addWidget(self.other_subjects)
        self.stacked_layout.addWidget(self.save_screen)
        self.stacked_layout.addWidget(self.view_screen)
        self.stacked_layout.addWidget(self.delete_screen)
        self.setup_password_gate()
        # self.setStatusBar(QStatusBar())

    def switch_screens(self, screen):
        self.stacked_layout.setCurrentWidget(screen)

    def go_back(self):
        self.switch_screens(self.main_menu)

    def get_back_label(self, label_text="Go Back") -> ClickableLabel:
        go_back_label = ClickableLabel(label_text)
        go_back_label.leftClicked.connect(self.go_back)
        StyleUtilities.styleWidgets(go_back_label)
        return go_back_label

    def setup_password_gate(self):
        if not PasswordManager.password_file_exists():
            screen = PasswordScreen(self)
            self.stacked_layout.addWidget(screen)
            self.switch_screens(screen)

    # Functions
    def quit_program(self):
        button = QMessageBox.question(self, 'Exit Confirmation',
                                      "Any unsaved changes will be lost.\nAre you sure you want to exit?",
                                      QMessageBox.Yes | QMessageBox.No,
                                      QMessageBox.No)
        if button == QMessageBox.Yes:
            QApplication.quit()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.raise_()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
