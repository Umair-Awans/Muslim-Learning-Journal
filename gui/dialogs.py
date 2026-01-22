from PyQt5.QtCore import QDate, pyqtSignal
from PyQt5.QtWidgets import (QMessageBox, QDialog, QDialogButtonBox,
                             QVBoxLayout, QCalendarWidget, QFormLayout, 
                             QLabel, QLineEdit)

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


class DateDialog(QDialog):
    signal_date_selected = pyqtSignal(QDate)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Muslim Learning journal")

        layout = QVBoxLayout(self)
        calendar_widget = QCalendarWidget(self)
        layout.addWidget(calendar_widget)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, # type: ignore
            parent=self
        )

        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        buttons.accepted.connect(
            lambda: self.signal_date_selected.emit(calendar_widget.selectedDate()) # type: ignore
        )

        layout.addWidget(buttons)


class PasswordDialog(QDialog):
    def __init__(self, password_manager, title: str, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Muslim Learning journal")

        self.password_manager = password_manager
        
        layout = QFormLayout(self)
        label = QLabel(title)
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
            return super().accept()

