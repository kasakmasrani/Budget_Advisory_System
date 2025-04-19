# ------------------------------
# Utility Class for Input Validations
# ------------------------------
from datetime import datetime
from colorama import Fore, Style, init
init(autoreset=True)

class InputUtils:
    """Provides static methods for common user input validations."""
    @staticmethod
    def get_valid_date(is_time=False, prompt=None, attempts=3):
        if prompt is None:
            prompt = "Enter a time (HH:MM:SS): " if is_time else "Enter a date (YYYY-MM-DD): "
        attempt = 0
        while attempt < attempts:
            date_str = input(Fore.CYAN + prompt).strip()
            if not date_str:
                return None
            try:
                if is_time:
                    return datetime.strptime(date_str, "%H:%M:%S").time()
                else:
                    return datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                print(Fore.RED + "❌ Invalid format. Please try again.")
                attempt += 1
        print(Fore.RED + "❌ Maximum attempts reached.")
        return None

    @staticmethod
    def get_valid_menu_choice(prompt, valid_choices):
        while True:
            choice = input(Fore.CYAN + prompt).strip()
            if choice in valid_choices:
                return int(choice)
            else:
                print(Fore.RED + f"❌ Invalid choice. Please select from {', '.join(valid_choices)}.")

    @staticmethod
    def get_float(prompt, min_value=None):
        """Get a valid float from the user."""
        attempts=3
        attempt = 0
        while attempt < attempts:
            val = input(Fore.CYAN + prompt).strip()
            attempt += 1
            try:
                num = float(val)
                if min_value is not None and num < min_value:
                    raise ValueError(f"Value must be at least {min_value}.")
                return num
            except ValueError as ve:
                print(Fore.RED + f"❌ Invalid Input")

    @staticmethod
    def get_string(prompt):
        return input(Fore.CYAN + prompt).strip()
    
    @staticmethod
    def get_account_type(prompt):
        """Take a valid account type input from the user."""
        attempts=0
        while attempts<3:
            try:
                account_type = input(Fore.CYAN + prompt).strip().lower()
                attempts+=1
                # Check if account name exists
                if account_type=="":
                    return None
                if account_type.lower() not in ['card','cash','savings','online']:
                    raise ValueError(f"Account must be from the following types: 'card', 'cash', 'savings', 'online'")
                return account_type
            except ValueError as e:
                print(Fore.RED + f"❌ Error: {e}")
                continue
        else:
            return None
