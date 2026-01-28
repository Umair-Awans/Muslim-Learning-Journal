from PyQt5.QtWidgets import QAction, QMenuBar, QMenu
from PyQt5.QtGui import QIcon


class MainMenuBar(QMenuBar):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
    
        # File
        self.menu_file = QMenu("File", self)
        self.menu_entry = QMenu("New Entry", self)

        self.action_Quran_entry = QAction("Al Qur'an Kareem", self)
        self.action_other_entry = QAction("Other Subjects", self)
        self.action_Quran_entry.setShortcut("Ctrl+A")
        self.action_other_entry.setShortcut("Ctrl+D")     

        self.action_open = QAction(QIcon("./images/folder.png"), "Open Journal", self)
        self.action_save = QAction(QIcon("./images/disk.png"), "Save Journal", self)
        self.action_save_as = QAction(QIcon("./images/disk.png"), "Save As...", self)
        self.action_exit = QAction("Exit", self)
        self.action_open.setShortcut("Ctrl+O")
        self.action_save.setShortcut("Ctrl+S")
        self.action_save_as.setShortcut("Ctrl+Shift+S")
        self.action_exit.setShortcut("Ctrl+Shift+Q")

        self.menu_entry.addAction(self.action_Quran_entry)
        self.menu_entry.addAction(self.action_other_entry)

        self.menu_file.addMenu(self.menu_entry)
        self.menu_file.addAction(self.action_open)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_save)
        self.menu_file.addAction(self.action_save_as)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_exit)

        self.addMenu(self.menu_file)

        # Edit
        self.menu_edit = QMenu("Edit", self)
        self.action_edit = QAction("Edit Progress", self)
        self.action_delete_entries = QAction("Delete Entries", self)
        self.action_delete_all = QAction("Delete All Entries", self)
        self.action_edit.setShortcut("Ctrl+E")

        self.menu_edit.addAction(self.action_edit)
        self.menu_edit.addSeparator()
        self.menu_edit.addAction(self.action_delete_entries)
        self.menu_edit.addAction(self.action_delete_all)
        self.addMenu(self.menu_edit)

        # View
        self.menu_view = QMenu("View", self)
        self.action_show_stats = QAction("Show Stats", self)
        self.action_show_report = QAction("Weekly Report", self)

        self.menu_view.addAction(self.action_show_stats)
        self.menu_view.addAction(self.action_show_report)
        self.addMenu(self.menu_view)

        # Tools
        self.menu_tools = QMenu("Tools", self)
        self.action_backup = QAction("Backup Data", self)
        self.action_restore = QAction("Restore Data", self)
        self.action_reset_password = QAction("Reset Password", self)

        self.menu_tools.addAction(self.action_backup)
        self.menu_tools.addAction(self.action_restore)
        self.menu_tools.addAction(self.action_reset_password)
        self.addMenu(self.menu_tools)

        # Help
        self.menu_help = QMenu("Help", self)
        self.action_about = QAction(QIcon("./images/info.png"), "About", self)
        
        self.menu_help.addAction(self.action_about)
        self.addMenu(self.menu_help)

