from typing import List, Union, Tuple
from cli.cli_prompt import CliPrompt


class Menu:
    """A customizable menu system for console applications.
    
    Attributes:
        menu_name (str): The title displayed when menu is shown.
    """
    
    def __init__(self, options: List[str], menu_name: str = "Main Menu") -> None:
        """Initialize the Menu with options and a title.
        
        Args:
            options: List of menu option strings
            menu_name: Title for the menu. Defaults to "Main Menu".
            
        Example:
            >>> menu = Menu(["Start Game", "Settings"], "Game Menu")
        """
        self.__options = options.copy() if options else []
        self.menu_name = menu_name

    def display_menu(
        self, 
        get_user_choice: bool = True, 
        show_menu_name: bool = True, 
        show_exit: bool = True, 
        exit_label: str = "Exit"
    ) -> Union[None, int, Tuple[int, int]]:
        """Display the menu and optionally collect user choice.
        
        Args:
            get_user_choice: If True, returns user selection. Defaults to True.
            show_menu_name: If True, displays the menu name. Defaults to True.
            show_exit: If True, shows exit option. Defaults to True.
            exit_label: Custom text for exit option. Defaults to "Exit".
            
        Returns:
            If get_user_choice is True:
                - Returns choice only if show_exit is False
                - Returns (choice, exit_option_num) if show_exit is True
            Otherwise returns None
            
        Example:
            >>> choice = menu.display_menu(get_user_choice=True)
        """
        if show_menu_name:
            border = "=" * ((54 - len(self.menu_name)) // 2)
            print(f"\n{border} {self.menu_name} {border}\n")
        
        for i, option in enumerate(self.__options, 1):
            print(f"{i}. {option}")
            
        if show_exit:
            print(f"{len(self.__options) + 1}. {exit_label}")
        
        if not get_user_choice:
            return None
    
        choice = self.get_user_choice(show_exit)
        return (choice, len(self.__options)+1) if show_exit else choice
        

    def get_user_choice(self, show_exit: bool) -> int:
        """Get and validate user's menu selection.
        
        Returns:
            Validated integer choice from the user
            
        Raises:
            ValueError: If invalid input is provided
            
        Example:
            >>> choice = menu.get_user_choice()
        """
        last_option = len(self.__options) + 1 if show_exit else len(self.__options)
        return int(CliPrompt.validate_number("\nEnter your choice: ", 1, last_option))

