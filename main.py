"""Main entry point for the Learning Journal application."""

from core_utils import PasswordManager, CliInputCollector
from menu_manager import Menus

def main():
    if not PasswordManager.password_file_exists():
        password = CliInputCollector.get_password()
        saved, msg = PasswordManager.store_password(password)
        print(msg)
        if not saved:
            return
    Menus.main_menu()

if __name__ == "__main__":
    main()