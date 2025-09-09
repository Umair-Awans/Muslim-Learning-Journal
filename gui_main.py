import sys
from PyQt5.QtGui import QIcon, QPainter, QPixmap, QLinearGradient, QColor, QIntValidator
from PyQt5.QtCore import Qt, QRect, QTimer
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QTextEdit,
                             QGridLayout, QAction, QFileDialog, QLabel, QCheckBox,
                             QMessageBox, QVBoxLayout, QScrollArea, QStackedWidget,
                             QMenu, QFormLayout, QLineEdit, QStackedLayout, QSpinBox,
                             QComboBox, QTabWidget, QStatusBar, )
sys.path.append("../Modules")
from MyQt5 import ClickableLabel
from entries import TafseerEntry, OtherEntry


class Utilities:
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
            FONT = 'Segoe Script' if not isinstance(widget, ClickableLabel) else 'Arial'
            FONT_SIZE = 35 if not isinstance(widget, ClickableLabel) else 25
            # FONT_COLOR = "#19c25f" if not isinstance(widget, ClickableLabel) else "#2077ce"
            FONT_COLOR = "#333333"
            BG_COLOR = cls.get_gradient(False) if isinstance(widget, ClickableLabel) else cls.get_gradient(False, True)
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
            widget.setMinimumHeight(30)
            widget.setStyleSheet("""QLineEdit, QTextEdit, QComboBox, QLabel{
                font-size: 25px;
                font-family: consolas;
                }
                QLineEdit, QTextEdit{
                    background-color: white;
                }""")
            if not isinstance(widget, QCheckBox) and not isinstance(widget, QComboBox) and not isinstance(widget, QTextEdit):
                widget.setAlignment(Qt.AlignCenter)
            if isinstance(widget, QTextEdit):
                widget.setMinimumHeight(100)

            if isinstance(widget, QLabel):
                widget.setAlignment(Qt.AlignCenter)


class EntryForm(QScrollArea):
    def __init__(self):
        super().__init__()
        self.entry_form_widget = QWidget()
        self.entry_form_layout = QVBoxLayout(self.entry_form_widget)
        self.setWidgetResizable(True)
        self.setWidget(self.entry_form_widget)

        self.page_label, self.page_input1, self.page_input2 = self.make_triplet("Page:", 1, 9999)
        self.time_label, self.time_input1, self.time_input2 = self.make_triplet("Time Spent:", 0, 60, "Hours", "Minutes")
        self.notes_label, self.notes_input = QLabel("\nNotes:"), QTextEdit()
        self.revision_label, self.revision_input = QLabel("\nRevision:"), QTextEdit()
        self.sequence_label = QLabel("Reading Sequentially?")
        self.sequence_input = QCheckBox()
        self.submit_label = ClickableLabel("Submit")

        Utilities.styleWidgets(self.submit_label)
        Utilities.styleFormElements(
            self.page_label,
            self.time_label,
            self.notes_label,
            self.sequence_label,
            self.revision_label,
            self.page_input1,
            self.page_input2,
            self.time_input1,
            self.time_input2,
            self.notes_input,
            self.sequence_input,
            self.revision_input
        )

        self.commons_widget = QWidget()
        self.commons_layout = QGridLayout(self.commons_widget)
        self.commons_layout.addWidget(self.page_label, 0, 0, 1, 1)
        self.commons_layout.addWidget(self.page_input1, 0, 1, 1, 1)
        self.commons_layout.addWidget(self.page_input2, 0, 2, 1, 1)
        self.commons_layout.addWidget(self.time_label, 1, 0, 1, 1)
        self.commons_layout.addWidget(self.time_input1, 1, 1, 1, 1)
        self.commons_layout.addWidget(self.time_input2, 1, 2, 1, 1)
        self.commons_layout.addWidget(self.notes_label, 2, 0, 3, 1)
        self.commons_layout.addWidget(self.notes_input, 2, 1, 3, 2)
        self.commons_layout.addWidget(self.revision_label, 5, 0, 3, 1)
        self.commons_layout.addWidget(self.revision_input, 5, 1, 3, 2)
        self.commons_layout.addWidget(self.sequence_label, 8, 0, 1, 2)
        self.commons_layout.addWidget(self.sequence_input, 8, 2, 1, 1)
        self.commons_layout.addWidget(self.submit_label, 9, 0, 1, 3)
    
    def make_triplet(self, label_text, min_val, max_val, placeholder1 = "From", placeholder2 = "To"):
        label = QLabel(label_text)
        input1 = QLineEdit()
        input1.setValidator(QIntValidator(min_val, max_val))
        input1.setPlaceholderText(placeholder1)

        input2 = QLineEdit()
        input2.setValidator(QIntValidator(min_val, max_val))
        input2.setPlaceholderText(placeholder2)

        return label, input1, input2
    
    
class QuranKareemForm(EntryForm):
    def __init__(self, Tafseer=True):
        super().__init__()
        self.form_widget = QWidget()
        self.form_layout = QGridLayout(self.form_widget)

        self.entry_form_layout.addWidget(self.form_widget)
        self.entry_form_layout.addWidget(self.commons_widget)

        self.Para_label, self.Para_input1, self.Para_input2 = self.make_triplet("Para:", 1, 30)
        self.Ruku_label, self.Ruku_input1, self.Ruku_input2 = self.make_triplet("Ruku:", 1, 9999)

        # Same Width so they look symmetrical
        self.page_label.setMinimumWidth(155)
        self.Para_label.setMinimumWidth(155)

        if Tafseer:
            self.Surah_label, self.Surah_input1, self.Surah_input2 = self.make_triplet("Surah:", 1, 114)
            self.Ayah_label, self.Ayah_input1, self.Ayah_input2 = self.make_triplet("Ayah:", 1, 9999)

            Utilities.styleFormElements(self.Para_label, self.Para_input1, self.Para_input2, self.Surah_label, self.Surah_input1, self.Surah_input2, self.Ayah_label, self.Ayah_input1, self.Ayah_input2, self.Ruku_label, self.Ruku_input1, self.Ruku_input2)
            self.add_to_layout([(self.Para_label, self.Para_input1, self.Para_input2), (self.Surah_label, self.Surah_input1, self.Surah_input2), (self.Ayah_label, self.Ayah_input1, self.Ayah_input2), (self.Ruku_label, self.Ruku_input1, self.Ruku_input2)])
        else:
            Utilities.styleFormElements(self.Para_label, self.Para_input1, self.Para_input2, self.Ruku_label, self.Ruku_input1, self.Ruku_input2)
            self.add_to_layout([(self.Para_label, self.Para_input1, self.Para_input2), (self.Ruku_label, self.Ruku_input1, self.Ruku_input2)])

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

    def submit_form(self):
        """WARNING! Not Implemented."""
        print("Al Qur'an")


class OtherSubjectsForm(EntryForm):
    """TODO: Add Subjects and books lists"""
    def __init__(self):
        super().__init__()
        self.form_widget = QWidget()
        self.form_layout = QGridLayout(self.form_widget)

        self.entry_form_layout.addWidget(self.form_widget)
        self.entry_form_layout.addWidget(self.commons_widget)

        self.subject_label, self.subject_input = self.get_label_combo("Subject:", ["Subject1", "Subject2"])
        self.book_label, self.book_input = self.get_label_combo("Book:", ["Book1", "Book2"])
        self.unit_label, self.unit_input = QLabel("Unit:"), QLineEdit()
        self.unit_input.setValidator(QIntValidator(1, 1000))
        self.unit_input.setFixedWidth(150)
        self.chapter_label, self.chapter_input = QLabel("Chapter:"), QLineEdit()

        # Same Width so they look symmetrical
        self.page_label.setMinimumWidth(155)
        self.subject_label.setMinimumWidth(155)

        self.submit_label.leftClicked.connect(self.submit_form)

        Utilities.styleFormElements(
            self.subject_label,
            self.subject_input,
            self.book_label,
            self.book_input,
            self.unit_label,
            self.unit_input,
            self.chapter_label,
            self.chapter_input
        )

        self.setStyleSheet("QComboBox{background-color: white;}")
        self.form_layout.addWidget(self.subject_label, 0, 0, 1, 1)
        self.form_layout.addWidget(self.subject_input, 0, 1, 1, 1)
        self.form_layout.addWidget(self.book_label, 0, 2, 1, 1)
        self.form_layout.addWidget(self.book_input, 0, 3, 1, 1)
        self.form_layout.addWidget(self.unit_label, 1, 0, 1, 1)
        self.form_layout.addWidget(self.unit_input, 1, 1, 1, 1)
        self.form_layout.addWidget(self.chapter_label, 1, 2, 1, 1)
        self.form_layout.addWidget(self.chapter_input, 1, 3, 1, 1)
        
    def get_label_combo(self, label_text: str, items: list):
        label = QLabel(label_text)
        combo_box = QComboBox()
        combo_box.setEditable(True)
        combo_box.setInsertPolicy(QComboBox.InsertAlphabetically)
        combo_box.addItems(items)

        return label, combo_box

        
    def submit_form(self):
        """WARNING! Not Implemented."""
        print("Others")

class MainMenu(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.main_window = parent

        # Widgets
        self.title = QLabel("Muslim Learning Journal")
        self.Quran_label = ClickableLabel("Al Qur'an Kareem")
        self.other_label = ClickableLabel("Other Subjects")
        self.save_label = ClickableLabel("Save Progress")
        self.view_label = ClickableLabel("View Progress")
        self.delete_label = ClickableLabel("Delete Progress")
        self.exit_label = ClickableLabel("Exit")
        Utilities.styleWidgets(self.title, self.Quran_label, self.other_label, self.save_label, self.view_label, self.delete_label, self.exit_label)

        # Attaching Functions
        self.Quran_label.leftClicked.connect(lambda: self.main_window.switch_screens(self.main_window.Quran_Kareem))
        self.other_label.leftClicked.connect(lambda: self.main_window.switch_screens(self.main_window.other_subjects))
        self.save_label.leftClicked.connect(lambda: self.main_window.switch_screens(self.main_window.save_screen))
        self.view_label.leftClicked.connect(lambda: self.main_window.switch_screens(self.main_window.view_screen))
        self.delete_label.leftClicked.connect(lambda: self.main_window.switch_screens(self.main_window.delete_screen))
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
    def __init__(self, title: str, content_widget, back_label):
        super().__init__()

        self.title = QLabel(title)
        Utilities.styleWidgets(self.title)

        self.screen_layout = QVBoxLayout(self)
        self.screen_layout.addWidget(self.title)
        self.screen_layout.addWidget(content_widget)
        self.screen_layout.addWidget(back_label)


class QuranKareem(BaseScreen):
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
        self.tabs_widget.setStyleSheet("QTabBar{font-size: 12pt; font-family: Consolas, Seoge Script;}")

        super().__init__("AL Quran Kareem", self.tabs_widget, go_back_label)



class OtherSubjects(BaseScreen):
    def __init__(self, go_back_label):
        super().__init__("Other Subjects", OtherSubjectsForm(), go_back_label)


class SaveProgress(BaseScreen):
    def __init__(self, go_back_label):

        self.content_widget = QWidget()

        super().__init__("Save Progress", self.content_widget, go_back_label)


class ViewProgress(BaseScreen):
    def __init__(self, go_back_label):

        self.content_widget = QWidget()

        super().__init__("View Progress", self.content_widget, go_back_label)



class DeleteProgress(BaseScreen):
    def __init__(self, go_back_label):

        self.content_widget = QWidget()

        super().__init__("Delete Progress", self.content_widget, go_back_label)


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
        self.main_menu = MainMenu(self)
        self.Quran_Kareem = QuranKareem(self.get_back_label())
        self.other_subjects = OtherSubjects(self.get_back_label())
        self.save_screen = SaveProgress(self.get_back_label())
        self.view_screen = ViewProgress(self.get_back_label())
        self.delete_screen = DeleteProgress(self.get_back_label())

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
        # self.setStatusBar(QStatusBar())

    def switch_screens(self, screen):
        self.stacked_layout.setCurrentWidget(screen)

    def go_back(self):
        self.switch_screens(self.main_menu)

    def get_back_label(self, label_text="Go Back") -> ClickableLabel:
        go_back_label = ClickableLabel(label_text)
        go_back_label.leftClicked.connect(self.go_back)
        Utilities.styleWidgets(go_back_label)
        return go_back_label

    # Functions
    def quit_program(self):
        button = QMessageBox.question(
            self,
            'Exit Confirmation',
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
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
