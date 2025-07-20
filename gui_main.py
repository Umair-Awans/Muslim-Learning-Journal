import sys
from PyQt5.QtGui import QIcon, QPainter, QPixmap, QLinearGradient, QColor, QIntValidator
from PyQt5.QtCore import Qt, QRect, QTimer
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QTextEdit,
                             QGridLayout, QAction, QFileDialog, QLabel, QCheckBox,
                             QMessageBox, QVBoxLayout, QScrollArea, QStackedWidget,
                             QMenu, QFormLayout, QLineEdit, QStackedLayout, QSpinBox,
                             QComboBox, QTabWidget, QStatusBar)
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


class EntryForm(QScrollArea):
    def __init__(self):
        super().__init__()
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.setWidgetResizable(True)
        self.setWidget(self.main_widget)

        self.Page_label = QLabel("Page no.")
        self.Page_input = QLineEdit()
        self.Page_input.setValidator(QIntValidator(1, 9999))
        self.Time_label = QLabel("Time Spent (in minutes):")
        self.Time_input = QLineEdit()
        self.Time_input.setValidator(QIntValidator(1, 9999))
        self.Notes_label = QLabel("Notes (optional):")
        self.Notes_input = QTextEdit()
        self.Sequence_label = QLabel("Reading Sequentially?")
        self.Sequence_input = QCheckBox()
        self.Revision_label = QLabel("Revision Notes (optional):")
        self.Revision_input = QTextEdit()
        self.submit_label = ClickableLabel("Submit")
        self.submit_label.setAlignment(Qt.AlignCenter)
        # self.go_back_label = ClickableLabel("Go Back")

        self.commons_widget = QWidget()
        self.commons_layout = QFormLayout(self.commons_widget)
        self.commons_layout.addRow(self.Page_label, self.Page_input)
        self.commons_layout.addRow(self.Time_label, self.Time_input)
        self.commons_layout.addRow(self.Notes_label, self.Notes_input)
        self.commons_layout.addRow(self.Sequence_label, self.Sequence_input)
        self.commons_layout.addRow(self.Revision_label, self.Revision_input)
        self.commons_layout.addRow(self.submit_label)
        # self.commons_layout.addWidget(self.Page_label, 0, 0, 1, 1)
        # self.commons_layout.addWidget(self.Page_input, 0, 1, 1, 1)
        # self.commons_layout.addWidget(self.Time_label, 1, 0, 1, 1)
        # self.commons_layout.addWidget(self.Time_input, 1, 1, 1, 1)
        # self.commons_layout.addWidget(self.Notes_label, 2, 0, 1, 1)
        # self.commons_layout.addWidget(self.Notes_input, 2, 1, 1, 1)
        # self.commons_layout.addWidget(self.Sequence_label, 3, 0, 1, 1)
        # self.commons_layout.addWidget(self.Sequence_input, 3, 2, 1, 1)
        # self.commons_layout.addWidget(self.Revision_label, 4, 0, 1, 1)
        # self.commons_layout.addWidget(self.Revision_input, 4, 1, 1, 1)
        # self.commons_layout.addWidget(self.submit_label, 5, 0, 1, 2)
        # self.commons_layout.addWidget(self.go_back_label, 6, 0, 1, 3)
        
        self.setStyleSheet(
                """
                QLineEdit {border: none;
                           border-bottom: 0.5px solid black;
                           text-align: center;}
                """
            )
        self.styleWidgets(
            self.Page_label,
            self.Time_label,
            self.Notes_label,
            self.Sequence_label,
            self.Revision_label,
        )
        # Utilities.styleWidgets(self.submit_label)
        # Utilities.styleInputFields(
        #     self.Page_input,
        #     self.Time_input,
        #     self.Notes_input,
        #     self.Sequence_input,
        #     self.Revision_input,
        #     form_inputs=True
        # )
    
    def styleWidgets(self, *widgets):
        for widget in widgets:
            
            if isinstance(widget, QLabel):
                widget.setStyleSheet("background-color: red;")
            else:
                widget.setStyleSheet("background-color: green;")


class QuranKareemForm(EntryForm):
    def __init__(self, Tafseer=True):
        super().__init__()
        if Tafseer:
            self.Surah_label = QLabel("Surah no.")
            self.Surah_input = QLineEdit()
            self.Surah_input.setValidator(QIntValidator(1, 114))
            self.Ayah_label = QLabel("Ayah no.")
            self.Ayah_input = QLineEdit()
            self.Ayah_input.setValidator(QIntValidator(1, 9999))
        self.Para_label = QLabel("Para no.")
        self.Para_input = QLineEdit()
        self.Para_input.setValidator(QIntValidator(1, 30))
        self.Ruku_label = QLabel("Ruku no.")
        self.Ruku_input = QLineEdit()
        self.Ruku_input.setValidator(QIntValidator(1, 9999))
        self.form_widget = QWidget()
        self.form_layout = QFormLayout(self.form_widget)
        self.main_layout.addWidget(self.form_widget)
        self.main_layout.addWidget(self.commons_widget)

        if Tafseer:
            self.form_layout.addRow(self.Para_label, self.Para_input)
            self.form_layout.addRow(self.Surah_label, self.Surah_input)
            self.form_layout.addRow(self.Ayah_label, self.Ayah_input)
            self.form_layout.addRow(self.Ruku_label, self.Ruku_input)
        #     self.add_to_layout(self.Para_label, self.Para_input, self.Surah_label, self.Surah_input, self.Ayah_label, self.Ayah_input, self.Ruku_label, self.Ruku_input)
        else:
            self.form_layout.addRow(self.Para_label, self.Para_input)
            self.form_layout.addRow(self.Ruku_label, self.Ruku_input)
        #     self.add_to_layout(self.Para_label, self.Para_input, self.Ruku_label, self.Ruku_input)
        

        # if Tafseer:
        #     Utilities.styleWidgets(
        #         self.Para_label,
        #         self.Surah_label,
        #         self.Ayah_label,
        #         self.Ruku_label,
        #         form_labels=True
        #     )
        #     Utilities.styleInputFields(
        #         self.Para_input,
        #         self.Surah_input,
        #         self.Ayah_input,
        #         self.Ruku_input,
        #         form_inputs=True
        #     )
        # else:            
        #     Utilities.styleWidgets(self.Para_label, self.Ruku_label, form_labels=True)
        #     Utilities.styleInputFields(self.Para_input, self.Ruku_input, form_inputs=True)

        

        # self.form_layout.addLayout(self.commons_layout, 1, 0)
        # self.form_layout.addWidget(self.commons_widget)
        # self.main_layout.addWidget(self.form_widget)
        # self.main_layout.addWidget(self.commons_widget)


    # def add_to_layout(self, *widgets):
    #     row = 0
    #     x = 0
    #     col = 0
    #     col_span = 1
    #     for widget in widgets:
    #         self.form_layout.addWidget(widget, row, col, 1, 1)
    #         x += 0.5
    #         row = int(x)
    #         col = 0 if col == 1 else 1
    #         col_span = 2 if col_span == 1 else 1
    #         if isinstance(widget, QLabel):
    #             widget.setStyleSheet("background-color: red;")
    #         else:
    #             widget.setStyleSheet("background-color: green;")

    def submit_form(self):
        # dummy function
        TafseerEntry(
            self.Para_input.text(),
            self.Surah_input.text(),
            int(self.Ayah_input.text()),
            self.Ruku_input.text(),
            self.Page_input.text(),
            self.Time_input.text(),
            self.Notes_input.text(),
            self.Sequence_input.text(),
            int(self.Revision_input.text()),
            self.Revision_input.text(),
            self.Revision_input.text(),
            int(self.Revision_input.text()),
            )


class OtherSubjectsForm(EntryForm):
    """"TODO: Add Subjects and books lists"""
    def __init__(self):
        super().__init__()
        self.form_widget = QWidget()
        self.form_layout = QGridLayout(self.main_widget)
        self.subject_label = QLabel("Subject:")
        self.subject_input = QComboBox()
        self.subject_input.setEditable(True)
        # self.subject_input.setFixedHeight(60)
        self.subject_input.addItems(["Subject1", "Subject2"])
        self.subject_input.setInsertPolicy(QComboBox.InsertAlphabetically)
        self.book_label = QLabel("Book:")
        self.book_input = QComboBox()
        self.book_input.setEditable(True)
        # self.book_input.setFixedHeight(60)
        self.book_input.addItems(["Book1", "Book2"])
        self.book_input.setInsertPolicy(QComboBox.InsertAlphabetically)
        self.setStyleSheet("QComboBox{background-color: white;}")
        self.unit_label = QLabel("Unit:")
        self.unit_input = QLineEdit()
        self.unit_input.setValidator(QIntValidator(1, 1000))
        self.chapter_label = QLabel("Chapter:")
        self.chapter_input = QLineEdit()

        # Utilities.styleWidgets(self.subject_label, self.book_label, self.unit_label, self.chapter_label, form_labels=True)
        # Utilities.styleInputFields(self.subject_input, self.book_input, self.unit_input, self.chapter_input, form_inputs=True)

        self.form_layout.addWidget(self.subject_label, 0, 0, 1, 1)
        self.form_layout.addWidget(self.subject_input, 0, 1, 1, 1)
        self.form_layout.addWidget(self.book_label, 1, 0, 1, 1)
        self.form_layout.addWidget(self.book_input, 1, 1, 1, 1)
        self.form_layout.addWidget(self.unit_label, 2, 0, 1, 1)
        self.form_layout.addWidget(self.unit_input, 2, 1, 1, 1)
        self.form_layout.addWidget(self.chapter_label, 3, 0, 1, 1)
        self.form_layout.addWidget(self.chapter_input, 3, 1, 1, 1)

        # self.main_layout.addWidget(self.form_widget)
        self.form_layout.addLayout(self.commons_layout, 8, 0)
        

class MainMenu(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.main_window = parent

        # Widgets
        pixmap = QPixmap("./images/Quran.jpg")
        self.title = QLabel("Muslim Learning Journal")
        # self.Quran_label = ClickableLabel("Al Qur'an Kareem")
        self.Quran_label = ClickableLabel("Al Qur'an Kareem")
        pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.Quran_label.setPixmap(pixmap)
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
        

class QuranKareem(QWidget):
    def __init__(self, go_back_label):
        super().__init__()
        self.go_back_label = go_back_label

        # Widgets
        self.title = QLabel("AL Quran Kareem")
        Utilities.styleWidgets(self.title)

        # **Quran-Screens**
        # Tafseer Form
        self.Tafseer_form = QuranKareemForm()
        # self.Tafseer_form.go_back_label.leftClicked.connect(self.back_to_options)
                       
        # Tilawat Form
        self.Tilawat_form = QuranKareemForm(False)
        # self.Tilawat_form.go_back_label.leftClicked.connect(self.back_to_options)
                
        # Quran Screens
        self.tabs_widget = QTabWidget()
        self.tabs_widget.addTab(self.Tafseer_form, "Tafseer")
        self.tabs_widget.addTab(self.Tilawat_form, "Tilawat")
        self.tabs_widget.setStyleSheet("QTabBar{font-size: 12pt; font-family: Seoge Script;}")

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.addWidget(self.title)
        self.main_layout.addWidget(self.tabs_widget)
        self.main_layout.addWidget(self.go_back_label)


class OtherSubjects(QWidget):
    def __init__(self, go_back_label):
        super().__init__()

        self.title = QLabel("Other Subjects")
        self.go_back_label = go_back_label
        Utilities.styleWidgets(self.title)
        self.other_subjects_form = OtherSubjectsForm()
        self.screen_layout = QVBoxLayout(self)
        self.screen_layout.addWidget(self.title)
        self.screen_layout.addWidget(self.other_subjects_form)
        self.screen_layout.addWidget(self.go_back_label)


class SaveProgress(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.main_window = parent
        self.go_back_label = self.main_window.get_back_label()
        

        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.go_back_label)
        # Work in Progress


class ViewProgress(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.main_window = parent
        self.go_back_label = self.main_window.get_back_label()

        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.go_back_label)
        # Work in Progress


class DeleteProgress(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.main_window = parent
        self.go_back_label = self.main_window.get_back_label()

        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.go_back_label)
        # Work in Progress


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
        self.save_screen = SaveProgress(self)
        self.view_screen = ViewProgress(self)
        self.delete_screen = DeleteProgress(self)

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

    def get_back_label(self) -> ClickableLabel:
        go_back_label = ClickableLabel("Go Back")
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
