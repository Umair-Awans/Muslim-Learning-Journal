from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import (QWidget, QGridLayout, QCheckBox, QVBoxLayout,
                             QScrollArea, QLabel, QLineEdit, QPushButton,
                             QComboBox, QTextEdit)
from gui.dialogs import MsgDialogs
from gui.styles import StyleSheets
from gui.gui_workflow import GuiWorkflow


class EntryFormWidget(QScrollArea):
    """
    ql = QLabel,
    qle = QLineEdit,
    qte = QTextEdit,
    qcb = QComboBox
    qchb = QCheckBox
    """
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window

        self.entry_form_widget = QWidget()
        self.entry_form_layout = QVBoxLayout(self.entry_form_widget)
        self.setWidgetResizable(True)
        self.setWidget(self.entry_form_widget)

        self.ql_page, self.qle_page1, self.qle_page2 = self.make_triplet(
            "Page:", 1.0, 9999.0)
        self.ql_time, self.qle_time1, self.qle_time2 = self.make_triplet(
            "Time Spent:", 0.0, 60.0, "Hours", "Minutes")
        self.qle_time1.setValidator(QIntValidator(0, 90))
        self.qle_time2.setValidator(QIntValidator(0, 60))
        self.ql_notes, self.qte_notes = QLabel("\nNotes:"), QTextEdit()
        self.ql_revision, self.qte_revision = QLabel(
            "\nRevision:"), QTextEdit()
        self.ql_reading_mode = QLabel("Reading Sequentially?")
        self.qchb_reading_mode = QCheckBox()
        self.submit_label = QPushButton("Submit")
        self.submit_label.clicked.connect(self.submit_form) #type: ignore

        self.setStyleSheet(StyleSheets.form_style_sheet())

        self.commons_widget = QWidget()
        self.commons_layout = QGridLayout(self.commons_widget)
        self.commons_layout.addWidget(self.ql_page, 0, 0, 1, 1)
        self.commons_layout.addWidget(self.qle_page1, 0, 1, 1, 1)
        self.commons_layout.addWidget(self.qle_page2, 0, 2, 1, 1)
        self.commons_layout.addWidget(self.ql_time, 1, 0, 1, 1)
        self.commons_layout.addWidget(self.qle_time1, 1, 1, 1, 1)
        self.commons_layout.addWidget(self.qle_time2, 1, 2, 1, 1)
        self.commons_layout.addWidget(self.ql_notes, 2, 0, 3, 1)
        self.commons_layout.addWidget(self.qte_notes, 2, 1, 3, 2)
        self.commons_layout.addWidget(self.ql_revision, 5, 0, 3, 1)
        self.commons_layout.addWidget(self.qte_revision, 5, 1, 3, 2)
        self.commons_layout.addWidget(self.ql_reading_mode, 8, 0, 1, 2)
        self.commons_layout.addWidget(self.qchb_reading_mode, 8, 2, 1, 1)
        self.commons_layout.addWidget(self.submit_label, 9, 0, 1, 3)

    def make_triplet(self, label_text, min_val, max_val, placeholder1="From", placeholder2="To"):
        label = QLabel(label_text)
        input1 = QLineEdit()
        input1.setValidator(QDoubleValidator(min_val, max_val, 2))
        input1.setPlaceholderText(placeholder1)

        input2 = QLineEdit()
        input2.setValidator(QDoubleValidator(min_val, max_val, 2))
        input2.setPlaceholderText(placeholder2)

        return label, input1, input2
    
    def set_edit_mode(self, callback):
        self.submit_label.clicked.disconnect(self.submit_form)
        self.submit_label.clicked.connect(callback)

    def load_entry(self, entry: dict):
        self.qle_page1.setText(entry["page_from"])
        if "page_to" in entry:
            self.qle_page2.setText(entry["page_to"])
        self.qle_time1.setText(str(entry["hours"]))
        self.qle_time2.setText(str(entry["minutes"]))
        self.qte_notes.setText(entry["notes"])
        self.qte_revision.setText(entry["revision"])
        self.qchb_reading_mode.setChecked(entry["reading_mode"])

    def collect_common_input(self):
        return {
        "page_from": self.qle_page1.text(),
        "page_to": self.qle_page2.text(),
        "hours": self.qle_time1.text(),
        "minutes": self.qle_time2.text(),
        "notes": self.qte_notes.toPlainText(),
        "reading_mode": self.qchb_reading_mode.isChecked(),
        "revision": self.qte_revision.toPlainText(),
        }
    
    def submit_form(self, add_entry: bool = True):
        specific_input = self.collect_specific_input()
        common_input = self.collect_common_input()
        workflow = GuiWorkflow(self.main_window.context)
        if MsgDialogs.show_operation_result(self.main_window,
            workflow.collect_data_make_entry(specific_input, common_input, add_entry),
            False):
            self.main_window.main_menu.display_stats_today()
            return workflow.entry

    
class QuranKareemForm(EntryFormWidget):

    def __init__(self, main_window, Tafseer=True, parent=None):
        super().__init__(main_window, parent)
        self.Tafseer = Tafseer
        self.form_widget = QWidget()
        self.form_layout = QGridLayout(self.form_widget)

        self.entry_form_layout.addWidget(self.form_widget)
        self.entry_form_layout.addWidget(self.commons_widget)

        self.ql_Para, self.qle_Para1, self.qle_Para2 = self.make_triplet(
            "Para:", 1.0, 30.0)
        self.ql_Ruku, self.qle_Ruku1, self.qle_Ruku2 = self.make_triplet(
            "Ruku (Para):", 1.0, 9999.0)

        # Make them the same width so they look visually aligned
        self.ql_page.setMinimumWidth(170)
        self.ql_Para.setMinimumWidth(170)

        if self.Tafseer:
            self.subject = "Al-Qur'an (Tafseer)"
            self.ql_Surah, self.qle_Surah1, self.qle_Surah2 = self.make_triplet(
                "Surah:", 1.0, 114.0)
            self.ql_Ayah, self.qle_Ayah1, self.qle_Ayah2 = self.make_triplet(
                "Ayah:", 1.0, 9999.0)

            self.add_to_layout([
                (self.ql_Para, self.qle_Para1, self.qle_Para2),
                (self.ql_Surah, self.qle_Surah1, self.qle_Surah2),
                (self.ql_Ayah, self.qle_Ayah1, self.qle_Ayah2),
                (self.ql_Ruku, self.qle_Ruku1, self.qle_Ruku2)
            ])
        else:
            self.subject = "Al-Qur'an (Tilawat)"
            self.add_to_layout([
                (self.ql_Para, self.qle_Para1, self.qle_Para2),
                (self.ql_Ruku, self.qle_Ruku1, self.qle_Ruku2)
            ])

    def add_to_layout(self, rows):
        """
        Adds widgets in rows: 
        Each row has a label + 'From' field + 'To' field.
        Example:
        [Label] [From-input] [To-input]
        """
        row = 0
        # Iterate through widgets in groups of three: (Label, From, To)
        for label, from_input, to_input in rows:
            self.form_layout.addWidget(label, row, 0)
            self.form_layout.addWidget(from_input, row, 1)
            self.form_layout.addWidget(to_input, row, 2)

            # Apply placeholders for input fields
            if hasattr(from_input, "setPlaceholderText"):
                from_input.setPlaceholderText("From")
            if hasattr(to_input, "setPlaceholderText"):
                to_input.setPlaceholderText("To")

            row += 1  # Move to next row

    def load_entry(self, entry: dict):
        self.qle_Para1.setText(entry["Para_from"])
        if "Para_to" in entry:
            self.qle_Para2.setText(entry["Para_to"])
        self.qle_Ruku1.setText(entry["Ruku (Para)_from"])
        if "Ruku (Para)_to" in entry:
            self.qle_Ruku2.setText(entry["Ruku (Para)_to"])
        if self.Tafseer:
            self.qle_Surah1.setText(entry["Surah_from"])
            if "Surah_to" in entry:
                self.qle_Surah2.setText(entry["Surah_to"])
            self.qle_Ayah1.setText(entry["Ayah_from"])
            if "Ayah_to" in entry:
                self.qle_Ayah2.setText(entry["Ayah_to"])
        super().load_entry(entry)

    def collect_specific_input(self):
        raw_input = {
                "entry_type": "Al Qur'an",
                "subject": self.subject,
                "Para_from": self.qle_Para1.text(),
                "Para_to": self.qle_Para2.text(),
                "Ruku_from": self.qle_Ruku1.text(),
                "Ruku_to": self.qle_Ruku2.text()
            }
        if self.Tafseer:
            raw_input.update({
                "Surah_from": self.qle_Surah1.text(),
                "Surah_to": self.qle_Surah2.text(),
                "Ayah_from": self.qle_Ayah1.text(),
                "Ayah_to": self.qle_Ayah2.text()
            })
        return raw_input
           

class OtherSubjectsForm(EntryFormWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(main_window, parent)
        self.data_manager = main_window.context.data_manager

        self.form_widget = QWidget()
        self.form_layout = QGridLayout(self.form_widget)
        
        self.entry_form_layout.addWidget(self.form_widget)
        self.entry_form_layout.addWidget(self.commons_widget)

        self.ql_subject, self.qcb_subject = self.get_label_and_comboBox("Subject:")
        
        self.ql_book, self.qcb_book = self.get_label_and_comboBox("book:")

        self.ql_unit, self.qle_unit1, self.qle_unit2 = self.make_triplet("Unit", 1.0, 9999.0)
        self.ql_chapter, self.qle_chapter = QLabel(
            "Chapter:"), QLineEdit()

        # Make them the same width so they look visually aligned
        self.ql_page.setMinimumWidth(155)
        self.ql_subject.setMinimumWidth(155)

        self.qcb_subject.currentTextChanged.connect(self.populate_books)

        self.form_layout.addWidget(self.ql_subject, 0, 0, 1, 1)
        self.form_layout.addWidget(self.qcb_subject, 0, 1, 1, 2)
        self.form_layout.addWidget(self.ql_book, 1, 0, 1, 1)
        self.form_layout.addWidget(self.qcb_book, 1, 1, 1, 2)
        self.form_layout.addWidget(self.ql_unit, 2, 0, 1, 1)
        self.form_layout.addWidget(self.qle_unit1, 2, 1, 1, 1)
        self.form_layout.addWidget(self.qle_unit2, 2, 2, 1, 1)
        self.form_layout.addWidget(self.ql_chapter, 3, 0, 1, 1)
        self.form_layout.addWidget(self.qle_chapter, 3, 1, 1, 2)
        self.populate_combo_boxes()

    def populate_combo_boxes(self):
        self.qcb_subject.addItems(self.data_manager.get_all_subjects())
        self.populate_books()
    
    def populate_books(self):
        subject = self.qcb_subject.currentText().strip()
        books_list = self.data_manager.get_books_list(subject)
        self.qcb_book.clear()
        self.qcb_book.addItems(books_list)

    def get_label_and_comboBox(self, label_text: str):
        label = QLabel(label_text)
        combo_box = QComboBox()
        combo_box.setEditable(True)
        combo_box.setInsertPolicy(QComboBox.InsertAlphabetically)

        return label, combo_box

    def load_entry(self, entry: dict):
        self.qcb_subject.blockSignals(True)
        self.qcb_subject.setEditable(False)
        self.qcb_book.setEditable(False)
        self.qcb_subject.clear()
        self.qcb_book.clear()
        self.qcb_subject.addItem(entry["subject"])
        self.qcb_book.addItem(entry["book"])
        self.qle_chapter.setText(entry["chapter"])
        self.qle_unit1.setText(entry["unit_from"])
        if "unit_to" in entry:
            self.qle_unit2.setText(entry["unit_to"])
        super().load_entry(entry)

    def collect_specific_input(self):
        return {
            "entry_type": "Other",
            "subject": self.qcb_subject.currentText(),
            "book": self.qcb_book.currentText(),
            "unit_from": self.qle_unit1.text(),
            "unit_to": self.qle_unit2.text(),
            "chapter": self.qle_chapter.text()
        }