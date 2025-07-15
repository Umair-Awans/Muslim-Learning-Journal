import sys
from PyQt5.QtGui import QIcon, QPainter, QLinearGradient, QColor
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QTextEdit,
                             QGridLayout, QAction, QFileDialog, QLabel, QCheckBox,
                             QMessageBox, QVBoxLayout, QScrollArea, QStackedWidget,
                             QMenu, QFormLayout, QLineEdit, QStackedLayout, QSpinBox)
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
    def styleWidgets(cls, *widgets):
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

    @staticmethod
    def styleInputFields(*widgets):
        for widget in widgets:
            widget.setStyleSheet("""QLineEdit{
                font-size: 25px;
                padding: 10px;
            }""")


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


class QuranKareemForm(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.form_scroll = QScrollArea()
        self.form_scroll.setWidgetResizable(True)
        self.form_scroll.setWidget(self)
        self.Para_label = QLabel("Para no.")
        self.Para_input = QSpinBox()
        self.Para_input.setRange(1, 30)
        self.Surah_label = QLabel("Surah no.")
        self.Surah_input = QSpinBox()
        self.Surah_input.setRange(1, 114)
        self.Ayah_label = QLabel("Ayah no.")
        self.Ayah_input = QSpinBox()
        self.Ayah_input.setRange(1, 99999)
        self.Ruku_label = QLabel("Ruku no.")
        self.Ruku_input = QSpinBox()
        self.Ruku_input.setRange(1, 99999)
        self.Page_label = QLabel("Page no.")
        self.Page_input = QSpinBox()
        self.Page_input.setRange(1, 99999)
        self.Time_label = QLabel("Time Spent ( in minutes):")
        self.Time_input = QSpinBox()
        self.Time_input.setRange(1, 99999)
        self.Notes_label = QLabel("Notes (optional):")
        self.Notes_input = QTextEdit()
        self.Sequence_label = QLabel("Reading Sequentially?")
        self.Sequence_input = QCheckBox()
        self.Revision_label = QLabel("Did you revise previous content?")
        self.Revision_input = QTextEdit()
        self.submit_label = ClickableLabel("Submit")
        self.submit_label.leftClicked.connect(self.submit_form)
        self.go_back_label = ClickableLabel("Go Back")

        self.form_layout = QGridLayout(self)
        self.form_layout.addWidget(self.Para_label, 0, 0, 1, 1)
        self.form_layout.addWidget(self.Para_input, 0, 1, 1, 2)
        self.form_layout.addWidget(self.Surah_label, 1, 0, 1, 1)
        self.form_layout.addWidget(self.Surah_input, 1, 1, 1, 2)
        self.form_layout.addWidget(self.Ayah_label, 2, 0, 1, 1)
        self.form_layout.addWidget(self.Ayah_input, 2, 1, 1, 2)
        self.form_layout.addWidget(self.Ruku_label, 3, 0, 1, 1)
        self.form_layout.addWidget(self.Ruku_input, 3, 1, 1, 2)
        self.form_layout.addWidget(self.Page_label, 4, 0, 1, 1)
        self.form_layout.addWidget(self.Page_input, 4, 1, 1, 2)
        self.form_layout.addWidget(self.Time_label, 5, 0, 1, 1)
        self.form_layout.addWidget(self.Time_input, 5, 1, 1, 2)
        self.form_layout.addWidget(self.Notes_label, 6, 0, 1, 1)
        self.form_layout.addWidget(self.Notes_input, 6, 1, 1, 2)
        self.form_layout.addWidget(self.Sequence_label, 7, 0, 1, 2)
        self.form_layout.addWidget(self.Sequence_input, 7, 2, 1, 1)
        self.form_layout.addWidget(self.Revision_label, 8, 0, 1, 2)
        self.form_layout.addWidget(self.Revision_input, 8, 1, 1, 2)
        self.form_layout.addWidget(self.submit_label, 9, 0, 1, 3)
        self.form_layout.addWidget(self.go_back_label, 10, 0, 1, 3)

        Utilities.styleWidgets(
            self.Para_label,
            self.Surah_label,
            self.Ayah_label,
            self.Ruku_label,
            self.Page_label,
            self.Time_label,
            self.Notes_label,
            self.Sequence_label,
            self.Revision_label,
            self.submit_label,
            self.go_back_label
        )
        Utilities.styleInputFields(
            self.Para_input,
            self.Surah_input,
            self.Ayah_input,
            self.Ruku_input,
            self.Page_input,
            self.Time_input,
            self.Notes_input,
            self.Sequence_input,
            self.Revision_input,
        )

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
        

class QuranKareem(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.main_window = parent
        self.go_back_label = self.main_window.get_back_label()

        # Widgets
        self.title = QLabel("AL Quran Kareem")

        # **Quran-Screens**
        # Quran-Options-Screen
        self.options_screen = QWidget()

        self.Tafseer_label = ClickableLabel("Al Qur'an (Tafseer) ")
        self.Tafseer_label.leftClicked.connect(self.open_Tafseer_form)

        self.Tilawat_label = ClickableLabel("Al Qur'an (Tilawat) ")
        self.Tilawat_label.leftClicked.connect(self.open_Tilawat_form)

        self.layout_options_screen = QVBoxLayout(self.options_screen)
        self.layout_options_screen.addWidget(self.Tafseer_label)
        self.layout_options_screen.addWidget(self.Tilawat_label)
        self.layout_options_screen.addWidget(self.go_back_label)
        Utilities.styleWidgets(self.Tafseer_label, self.Tilawat_label)

        # Tafseer Form
        self.Tafseer_form = QuranKareemForm(self.main_window)
        self.Tafseer_form.go_back_label.leftClicked.connect(self.back_to_options)
               
        # Tilawat Form
        self.Tilawat_form = QuranKareemForm(self.main_window)
        self.Tilawat_form.go_back_label.leftClicked.connect(self.back_to_options)
        
        # Quran Screens
        self.Quran_screens_widget = QWidget()
        self.Quran_screens_layout = QStackedLayout(self.Quran_screens_widget)
        self.Quran_screens_layout.addWidget(self.options_screen)
        self.Quran_screens_layout.addWidget(self.Tafseer_form.form_scroll)
        self.Quran_screens_layout.addWidget(self.Tilawat_form.form_scroll)

        # Main layout
        self.Quran_main_screen = QVBoxLayout(self)
        self.Quran_main_screen.addWidget(self.title)
        self.Quran_main_screen.addWidget(self.Quran_screens_widget)
        Utilities.styleWidgets(self.title)

    def open_Tafseer_form(self):
        self.Quran_screens_layout.setCurrentWidget(self.Tafseer_form.form_scroll)

    def open_Tilawat_form(self):
        self.Quran_screens_layout.setCurrentWidget(self.Tilawat_form.form_scroll)

    def back_to_options(self):
        self.Quran_screens_layout.setCurrentWidget(self.options_screen)

    def get_back_btn(self) -> ClickableLabel:
        go_back_label = ClickableLabel("Go Back")
        Utilities.styleWidgets(go_back_label)
        go_back_label.leftClicked.connect(self.back_to_options)
        return go_back_label


class OtherSubjectsForm(QWidget):
    def __init__(self, parent):
        super().__init__()

        self.main_window = parent
        self.go_back_label = self.main_window.get_back_label()

        # Main layout
        self.other_subjects_form = QFormLayout(self)
        # OtherEntry()
        self.subject_label = QLabel("Subject:")
        self.subject_input = QLineEdit()
        self.book_label = QLabel("Book:")
        self.book_input = QLineEdit()
        self.pages_label = QLabel("Pages:")
        self.pages_input = QLineEdit()
        self.time_label = QLabel("Time Spent (minutes):")
        self.time_input = QLineEdit()
        self.notes_label = QLabel("Notes:")
        self.notes_input = QLineEdit()
        self.notes_label = QLabel("Reading Sequentially:")
        self.notes_input = QLineEdit()
        Utilities.styleWidgets(self.subject_label)
        Utilities.styleInputFields(self.subject_input)
        # Work in Progress
        self.other_subjects_form.setWidget(0, QFormLayout.LabelRole, self.subject_label)
        self.other_subjects_form.setWidget(0, QFormLayout.FieldRole, self.subject_input)
        self.other_subjects_form.addWidget(self.go_back_label)


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
        self.Quran_Kareem = QuranKareem(self)
        self.other_subjects = OtherSubjectsForm(self)
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
        reply = QMessageBox.question(
            self,
            'Exit Confirmation',
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            QApplication.quit()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.raise_()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
