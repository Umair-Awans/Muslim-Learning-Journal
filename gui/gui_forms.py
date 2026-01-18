from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import (QWidget, QGridLayout, QCheckBox, QVBoxLayout,
                             QScrollArea, QLabel, QLineEdit,
                             QComboBox, QTextEdit)
from gui.gui_utils import ClickableLabel, GuiWorkflow, GuiUtilities, StyleUtilities

class EntryFormWidget(QScrollArea):
    """
    ql = QLabel,
    qle = QLineEdit,
    qte = QTextEdit,
    qcb = QComboBox
    qchb = QCheckBox
    """
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.gui_workflow = GuiWorkflow(data_manager)

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
        self.submit_label.leftClicked.connect(self.submit_form) #type: ignore

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

    def make_triplet(self, label_text, min_val, max_val, placeholder1="From", placeholder2="To"):
        label = QLabel(label_text)
        input1 = QLineEdit()
        input1.setValidator(QDoubleValidator(min_val, max_val, 2))
        input1.setPlaceholderText(placeholder1)

        input2 = QLineEdit()
        input2.setValidator(QDoubleValidator(min_val, max_val, 2))
        input2.setPlaceholderText(placeholder2)

        return label, input1, input2

    def keyPressEvent(self, event) -> None:
        super().keyPressEvent(event)
        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            self.submit_form()

    def collect_common_input(self):
        return {
        "page_from": self.qlePage1.text(),
        "page_to": self.qlePage2.text(),
        "hours": self.qleTime1.text(),
        "minutes": self.qleTime2.text(),
        "notes": self.qteNotes.toPlainText(),
        "reading_mode": self.qchbReadingMode.isChecked(),
        "revision": self.qteRevision.toPlainText(),
        }
    
    def submit_form(self):
        specific_input = self.collect_specific_input()
        common_input = self.collect_common_input()
        valid, msg = self.gui_workflow.collect_data_make_entry(specific_input, common_input)
        if not valid:
            GuiUtilities.show_warning_msg(self, msg)
        else:
            GuiUtilities.show_information_msg(self, msg)

    
class QuranKareemForm(EntryFormWidget):

    def __init__(self, data_manager, Tafseer=True, parent=None):
        super().__init__(data_manager, parent)
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
            self.subject = "Al-Qur'an (Tafseer)"
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
            self.subject = "Al-Qur'an (Tilawat)"
            self.add_to_layout([
                (self.qlPara, self.qlePara1, self.qlePara2),
                (self.qlRuku, self.qleRuku1, self.qleRuku2)
            ])

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

    def collect_specific_input(self):
        raw_input = {
                "entry_type": "Al Qur'an",
                "subject": self.subject,
                "Para_from": self.qlePara1.text(),
                "Para_to": self.qlePara2.text(),
                "Ruku_from": self.qleRuku1.text(),
                "Ruku_to": self.qleRuku2.text()
            }
        if self.Tafseer:
            raw_input.update({
                "Surah_from": self.qleSurah1.text(),
                "Surah_to": self.qleSurah2.text(),
                "Ayah_from": self.qleAyah1.text(),
                "Ayah_to": self.qleAyah2.text()
            })
        return raw_input
           

class OtherSubjectsForm(EntryFormWidget):
    def __init__(self, data_manager, parent=None):
        super().__init__(data_manager, parent)
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
        self.subjects = self.data_manager.all_time_subjects
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

    def collect_specific_input(self):
        return {
            "entry_type": "Other",
            "subject": self.qcbSubject.currentText(),
            "book": self.qcbBook.currentText(),
            "unit_from": self.qleUnit1.text(),
            "unit_to": self.qleUnit2.text(),
            "chapter": self.qleChapter.text()
        }