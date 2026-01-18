"""Main entry point for the Learning Journal application."""

from core.core_utils import PasswordManager
from cli.menu_manager import Menus
from cli.cli_prompt import CliPrompt

def main():
    if not PasswordManager.password_file_exists():
        password = CliPrompt.get_password()
        saved, msg = PasswordManager.store_password(password)
        print(msg)
        if not saved:
            return
    Menus.main_menu()

if __name__ == "__main__":
    main()