import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QDialog,
                             QPushButton, QStackedLayout, QStatusBar)
from core.app_context import AppContext
from core.core_services import CoreHelpers
from core.exceptions import DataCorruptionError
from gui.screens import (MainMenuScreen, QuranKareemScreen, OtherSubjectsScreen, 
                         EditorScreen, SaveScreen, ViewScreen)
from gui.gui_editor import EntryEditService
from gui.data_controller import DataController
from gui.widgets import ClickableLabel
from gui.dialogs import MsgDialogs, PasswordDialog
from gui.menubar import MainMenuBar
from gui.styles import StyleSheets



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
        self.edit_screen = EditorScreen(self)

        self.stacked_layout.addWidget(self.main_menu)
        self.stacked_layout.addWidget(self.Quran_Kareem)
        self.stacked_layout.addWidget(self.other_subjects)
        self.stacked_layout.addWidget(self.save_screen)
        self.stacked_layout.addWidget(self.view_screen)
        self.stacked_layout.addWidget(self.edit_screen)

        self.menu_bar = MainMenuBar(self)
        self.setMenuBar(self.menu_bar)
        
        self.menu_bar.action_Quran_entry.triggered.connect(lambda: self.switch_screens(self.Quran_Kareem))
        self.menu_bar.action_other_entry.triggered.connect(lambda: self.switch_screens(self.other_subjects))
        self.menu_bar.action_open.triggered.connect(lambda: DataController.open_journal(self))
        self.menu_bar.action_save.triggered.connect(self.signal_save.emit) # type: ignore
        self.menu_bar.action_save_as.triggered.connect(lambda: DataController.save_md_as(self)) # type: ignore
        self.menu_bar.action_exit.triggered.connect(self.close) 

        self.menu_bar.action_edit.triggered.connect(lambda: self.switch_screen(self.edit_screen))
        self.menu_bar.action_delete_entries.triggered.connect(lambda: EntryEditService.delete_entries(self))
        self.menu_bar.action_delete_all.triggered.connect(lambda: EntryEditService.delete_all(self))

        self.menu_bar.action_show_report.triggered.connect(lambda: DataController.show_weekly_report(self))
        self.menu_bar.action_backup.triggered.connect(lambda: DataController.on_backup_triggered(self))
        self.menu_bar.action_restore.triggered.connect(lambda: DataController.on_restore_triggered(self))
        self.menu_bar.action_reset_password.triggered.connect(lambda: DataController.reset_password(self))
        self.menu_bar.action_about.triggered.connect(self.show_about)

    def show_about(self):
        MsgDialogs.show_information_msg(self, f"{self.context.about()}\n\nDeveloped with PyQt5.")

    def switch_screen(self, screen):
        self.stacked_layout.setCurrentWidget(screen)

    def go_back(self):
        self.switch_screen(self.main_menu)

    def get_back_label(self, label_text="Back") -> ClickableLabel:
        # go_back_label = ClickableLabel(label_text)
        # go_back_label.leftClicked.connect(self.go_back) #type: ignore
        go_back_label = QPushButton(label_text)
        go_back_label.clicked.connect(self.go_back)
        return go_back_label

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
