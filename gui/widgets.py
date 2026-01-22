from PyQt5.QtWidgets import QWidget, QHBoxLayout, QDateEdit, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QDate
from gui.styles import StyleSheets

class ClickableLabel(QLabel):
    leftClicked = pyqtSignal()
    rightClicked = pyqtSignal()

    def __init__(self, text=""):
        super().__init__(text)
        self.setCursor(Qt.PointingHandCursor)

        self.normal_style = StyleSheets.label_normal()
        self.pressed_style = StyleSheets.label_pressed()

        self.setStyleSheet(self.normal_style)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.leftClicked.emit() # type: ignore
            if self.pressed_style:
                self.setStyleSheet(self.pressed_style)
                QTimer.singleShot(1000, self.resetStyle)
        elif event.button() == Qt.RightButton:
            self.rightClicked.emit() # type: ignore

    def resetStyle(self):
        if self.normal_style:
            self.setStyleSheet(self.normal_style)


class DateSelector(QWidget):
    signal_date_selection = pyqtSignal(QDate)
    def __init__(self, label_text: str, parent=None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        self.date_edit = QDateEdit()
        self.submit = ClickableLabel(label_text)
        layout.addWidget(self.submit)
        layout.addWidget(self.date_edit)
        self.submit.leftClicked.connect(lambda: self.signal_date_selection.emit(self.date_edit.date())) # type: ignore

    def get_date_selected(self):
        return self.date_edit.date()

    def showEvent(self, event):
        super().showEvent(event)
        self.date_edit.setDate(QDate.currentDate())