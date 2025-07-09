"""Main entry point for the Learning Journal application."""

from core_utils import PasswordManager
from menu_manager import Menus


if __name__ == "__main__":
    if not PasswordManager.password_file_exists():
        PasswordManager.get_and_store_password()
    Menus.main_menu()