from io import StringIO
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import (QMessageBox, QDialog, QDialogButtonBox, QPushButton,
                             QVBoxLayout, QCalendarWidget, QFormLayout, 
                             QLabel, QLineEdit, QTextBrowser, QComboBox)
from core.progress_editor import ProgressEditor
from gui.entries_display import EntryFormatter



class MsgDialogs:
    @staticmethod
    def show_information_msg(parent_widget, message: str, title: str = "Muslim Learning Journal"):
        QMessageBox.information(parent_widget, title,
                                    message,
                                    QMessageBox.Ok, QMessageBox.Ok)

    @staticmethod
    def show_warning_msg(parent_widget, message: str, title: str = "Muslim Learning Journal"):
        QMessageBox.warning(parent_widget, title,
                                    message,
                                    QMessageBox.Ok, QMessageBox.Ok)
        
    @staticmethod
    def show_critical_msg(parent_widget, message: str, title: str = "Muslim Learning Journal"):
        QMessageBox.critical(parent_widget, title,
                                    message,
                                    QMessageBox.Ok, QMessageBox.Ok)

    @staticmethod
    def get_answer(parent_widget, question: str, title: str = "Muslim Learning Journal") -> bool:
        return QMessageBox.question(parent_widget, title,
                                    question,
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes # type: ignore

    @classmethod
    def show_operation_result(cls, parent, result, critical: bool = True):
        success, msg = result
        if success:
            cls.show_information_msg(parent, msg)
        else:
            if critical:
                cls.show_critical_msg(parent, msg)
            else:
                cls.show_warning_msg(parent, msg)
        return success

class DateDialog(QDialog):

    def showEvent(self, a0) -> None:
        self.calendar_widget.setSelectedDate(QDate.currentDate())
        return super().showEvent(a0)

    def __init__(self, label_text: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Muslim Learning journal")

        layout = QVBoxLayout(self)
        label = QLabel(label_text)
        label.setStyleSheet("qproperty-alignment: 'AlignCenter'")
        self.calendar_widget = QCalendarWidget(self)
        layout.addWidget(label)
        layout.addWidget(self.calendar_widget)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, # type: ignore
            parent=self
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)


class EditorDialog(QDialog):
    def __init__(self, date: str, entries: dict, parent=None) -> None:
        super().__init__(parent)
        self.entries = entries

        self.setWindowTitle("Muslim Learning Journal")
        self.setMinimumWidth(550)

        # ---------- Widgets ----------
        title_label = QLabel(date)
        title_label.setAlignment(Qt.AlignCenter)
     
        self.qcb_subject = QComboBox()
        self.qcb_book = QComboBox()
        self.qcb_session = QComboBox()
        self.text_browser = QTextBrowser()

        # ---------- Layout ----------
        layout = QFormLayout(self)
        layout.addRow(title_label)
        layout.addRow("Subject:", self.qcb_subject)
        layout.addRow("Book:", self.qcb_book)
        layout.addRow("Entry:", self.qcb_session)
        layout.addRow(self.text_browser)

        
        buttons = QDialogButtonBox(self)
        buttons.addButton("Edit", QDialogButtonBox.AcceptRole)
        buttons.addButton("Cancel", QDialogButtonBox.RejectRole)

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addRow(buttons)

        # ---------- Populate initial data ----------
        self.populate_subjects()

        # ---------- Signals ----------
        self.qcb_subject.currentTextChanged.connect(self.populate_books)
        self.qcb_book.currentTextChanged.connect(self.populate_entries)
        self.qcb_session.currentTextChanged.connect(self.refresh_view)

        # Initial display
        self.refresh_view()

    # ============================================================
    # Population methods
    # ============================================================

    def populate_subjects(self) -> None:
        self.qcb_subject.blockSignals(True)

        self.qcb_subject.clear()
        self.qcb_subject.addItems(self.entries.keys())

        self.qcb_subject.blockSignals(False)

        self.populate_books()

    def populate_books(self) -> None:
        subject = self.qcb_subject.currentText()
        if not subject:
            return

        self.qcb_book.blockSignals(True)
        self.qcb_session.blockSignals(True)

        self.qcb_book.clear()
        self.qcb_book.addItems(self.entries[subject].keys())

        self.qcb_session.clear()

        self.qcb_book.blockSignals(False)
        self.qcb_session.blockSignals(False)

        self.populate_entries()

    def populate_entries(self) -> None:
        subject = self.qcb_subject.currentText()
        book = self.qcb_book.currentText()

        if not subject or not book:
            return

        self.qcb_session.blockSignals(True)

        self.qcb_session.clear()
        self.qcb_session.addItems(self.entries[subject][book].keys())

        self.qcb_session.blockSignals(False)

        self.refresh_view()

    # ============================================================
    # View refresh
    # ============================================================
    def refresh(self):
        self.subject = self.qcb_subject.currentText()
        self.book = self.qcb_book.currentText()
        self.session = self.qcb_session.currentText()

    def refresh_view(self) -> None:
        self.refresh()

        if not all((self.subject, self.book, self.session)):
            self.text_browser.clear()
            return

        try:
            data = self.entries[self.subject][self.book][self.session]
        except KeyError:
            self.text_browser.clear()
            return

        buffer = StringIO()
        EntryFormatter.format_entry_html(
            buffer,
            f"{self.book} ({self.session})",
            data,
        )
        self.text_browser.setHtml(buffer.getvalue())
             

class PasswordDialog(QDialog):
    def __init__(self, password_manager, label_text: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Muslim Learning journal")

        self.password_manager = password_manager
        
        label = QLabel(label_text)
        label.setStyleSheet("qproperty-alignment: 'AlignCenter'")
        self.info_label = QLabel()
        self.info_label.setStyleSheet("""QLabel{
                                    color: red;
                                    qproperty-alignment: 'AlignCenter'
                                    }""")

        self.password = QLineEdit()
        self.confirm = QLineEdit()
        self.password.setFixedWidth(250)
        self.confirm.setFixedWidth(250)

        layout = QFormLayout(self)
        layout.addRow(label)
        layout.addRow("Password: ", self.password)
        layout.addRow("Confirm Password: ", self.confirm)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, # type: ignore
            parent=self
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addRow(self.info_label)
        layout.addRow(buttons)

    def accept(self) -> None:
        saved, msg = self.password_manager.set_password(self.password.text().strip(), self.confirm.text().strip())
        self.info_label.setText(msg)
        if saved:
            MsgDialogs.show_information_msg(self, msg)
            return super().accept()

