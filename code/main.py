# ------------------------------
# Main Menu and Flow
# ------------------------------
from database import Database
from accounts import AccountsManager
from transactions import TransactionsManager
from budget import BudgetManager
from categories import CategoryManager
from analysis import AnalysisManager
from utils import InputUtils
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

class MainMenu:
    """Coordinates the overall application flow and menus."""
    def __init__(self, db: Database):
        self.db = db
        self.accounts_manager = AccountsManager(db)
        self.category_manager = CategoryManager(db)
        self.budget_manager = BudgetManager(db, self.category_manager)
        self.transactions_manager = TransactionsManager(db, self.accounts_manager, self.category_manager, self.budget_manager)
        self.analysis_manager = AnalysisManager(db,self.transactions_manager)
        self.console = Console()

    def show_main_menu(self):
        self.console.print(Panel("[bold cyan] Main Menu [/bold cyan]", style="bold white"))
        self.console.print("[bold yellow]1.[/bold yellow] 🏦 Manage Accounts")
        self.console.print("[bold yellow]2.[/bold yellow] 📂 Manage Categories")
        self.console.print("[bold yellow]3.[/bold yellow] 📊 Manage Budgets")
        self.console.print("[bold yellow]4.[/bold yellow] 💸 Manage Transactions")
        self.console.print("[bold yellow]5.[/bold yellow] 📈 Analysis")
        self.console.print("[bold yellow]6.[/bold yellow] 🚪 Exit")

    def accounts_menu_flow(self):
        while True:
            self.console.print(Panel("[bold cyan]🏦 Accounts Menu[/bold cyan]", style="bold white"))
            self.console.print("[bold yellow]1.[/bold yellow] ➕ Add Account")
            self.console.print("[bold yellow]2.[/bold yellow] ✏️ Update Account")
            self.console.print("[bold yellow]3.[/bold yellow] ❌ Delete Account")
            self.console.print("[bold yellow]4.[/bold yellow] 📄 View Accounts")
            self.console.print("[bold yellow]5.[/bold yellow] 🔙 Go Back")
            choice = InputUtils.get_valid_menu_choice("Choose an option (1-5): ", ['1','2','3','4','5'])
            if choice == 1:
                name = InputUtils.get_string("Enter account name: ")
                balance = InputUtils.get_float("Enter initial balance: ", min_value=0)
                acc_type = InputUtils.get_string("Enter account type (card/cash/savings/online): ")
                self.accounts_manager.add_account(name, balance, acc_type)
            elif choice == 2:
                self.accounts_manager.update_account()
            elif choice == 3:
                self.accounts_manager.delete_account()
            elif choice == 4:
                self.accounts_manager.view_accounts()
            elif choice == 5:
                break

    def transactions_menu_flow(self):
        while True:
            self.console.print(Panel("[bold cyan]💸 Transactions Menu[/bold cyan]", style="bold white"))
            self.console.print("[bold yellow]1.[/bold yellow] ➕ Add Transaction")
            self.console.print("[bold yellow]2.[/bold yellow] 🔄 Transfer Funds")
            self.console.print("[bold yellow]3.[/bold yellow] ✏️ Update Transaction")
            self.console.print("[bold yellow]4.[/bold yellow] ❌ Delete Transaction")
            self.console.print("[bold yellow]5.[/bold yellow] 📄 View Transactions")
            self.console.print("[bold yellow]6.[/bold yellow] 🔙 Go Back")
            choice = InputUtils.get_valid_menu_choice("Choose an option (1-6): ", ['1','2','3','4','5','6'])
            if choice == 1:
                self.transactions_manager.add_transaction()
            elif choice == 2:
                self.transactions_manager.transfer_funds()
            elif choice == 3:
                self.transactions_manager.update_transaction()
            elif choice == 4:
                self.transactions_manager.delete_transaction()
            elif choice == 5:
                self.transactions_manager.view_transactions()
            elif choice == 6:
                break

    def categories_menu_flow(self):
        while True:
            self.console.print(Panel("[bold cyan]📂 Categories Menu[/bold cyan]", style="bold white"))
            self.console.print("[bold yellow]1.[/bold yellow] ➕ Add Category")
            self.console.print("[bold yellow]2.[/bold yellow] ✏️ Update Category")
            self.console.print("[bold yellow]3.[/bold yellow] ❌ Delete Category")
            self.console.print("[bold yellow]4.[/bold yellow] 📄 View Categories")
            self.console.print("[bold yellow]5.[/bold yellow] 🔙 Go Back")
            choice = InputUtils.get_valid_menu_choice("Choose an option (1-5): ", ['1','2','3','4','5'])
            if choice == 1:
                name = InputUtils.get_string("Enter category name: ")
                ctype = InputUtils.get_string("Enter category type (income/expense): ")
                desc = InputUtils.get_string("Enter description (optional): ")
                self.category_manager.add_category(name, ctype, desc)
            elif choice == 2:
                name = InputUtils.get_string("Enter category name to update: ")
                new_name = InputUtils.get_string("Enter new category name (leave blank to keep same): ")
                new_desc = InputUtils.get_string("Enter new description (leave blank to keep same): ")
                self.category_manager.update_category(name, new_name, new_desc)
            elif choice == 3:
                name = InputUtils.get_string("Enter category name to delete: ")
                self.category_manager.delete_category(name)
            elif choice == 4:
                self.category_manager.view_categories()
            elif choice == 5:
                break

    def budgets_menu_flow(self):
        while True:
            self.console.print(Panel("[bold cyan]📊 Budgets Menu[/bold cyan]", style="bold white"))
            self.console.print("[bold yellow]1.[/bold yellow] ➕ Set Budget")
            self.console.print("[bold yellow]2.[/bold yellow] 📄 View Budgets")
            self.console.print("[bold yellow]3.[/bold yellow] ❌ Delete Budget")
            self.console.print("[bold yellow]4.[/bold yellow] 🚨 Check Budget Alerts")
            self.console.print("[bold yellow]5.[/bold yellow] 🔙 Go Back")
            
            # Get user's choice from a valid range (1-6)
            choice = InputUtils.get_valid_menu_choice("Choose an option (1-6): ", ['1', '2', '3', '4', '5', '6'])
            
            # Process each choice
            if choice == 1:
                self.budget_manager.add_budget()
            elif choice == 2:
                self.budget_manager.view_budgets()
            elif choice == 3:
                # Delete a budget
                self.budget_manager.delete_budget()
            elif choice == 4:
                # Handle recurring budgets
                self.budget_manager.check_budget_alerts()
            elif choice == 5:
                # Exit the loop (Go Back)
                break


    def analysis_menu_flow(self):
        """Handles user interaction for analysis features."""
        try:
            while True:
                self.console.print(Panel("[bold cyan]📊 Financial Analysis Menu[/bold cyan]", style="bold white"))
                self.console.print("[bold yellow]1.[/bold yellow] 📉 Spending Patterns Analysis")
                self.console.print("[bold yellow]2.[/bold yellow] 📈 Income Stability Analysis")
                self.console.print("[bold yellow]3.[/bold yellow] 🔍 Anomaly Detection")
                self.console.print("[bold yellow]4.[/bold yellow] 📊 Expense Overview")
                self.console.print("[bold yellow]5.[/bold yellow] 📈 Income Overview")
                self.console.print("[bold yellow]6.[/bold yellow] 🔄 Expense Flow")
                self.console.print("[bold yellow]7.[/bold yellow] 🔄 Income Flow")
                self.console.print("[bold yellow]8.[/bold yellow] 🧩 Run Full Analysis")
                self.console.print("[bold yellow]9.[/bold yellow] 🔙 Go Back")
                

                choice = Prompt.ask("[bold green]Select an option[/bold green]", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9"])

                if choice == "1":
                    self.analysis_manager.spending_patterns()
                elif choice == "2":
                    self.analysis_manager.income_stability()
                elif choice == "3":
                    self.analysis_manager.anomaly_detection()
                elif choice == "4":
                    self.analysis_manager.expense_overview()
                elif choice == "5":
                    self.analysis_manager.income_overview()
                elif choice == "6":
                    self.analysis_manager.expense_flow()
                elif choice == "7":
                    self.analysis_manager.income_flow()
                elif choice == "8":
                    self.analysis_manager.run_full_analysis()
                elif choice == "9":
                    self.console.print("[bold red]Returning to main menu...[/bold red]")
                    break
        except Exception as e:
            self.console.print(f"[bold red]An error occurred: {e}[/bold red]")
            

    def run(self):
        while True:
            self.show_main_menu()
            choice = InputUtils.get_valid_menu_choice("Choose an option (1-6): ", ['1','2','3','4','5','6'])
            if choice == 1:
                self.accounts_menu_flow()
            elif choice == 2:
                self.categories_menu_flow()
            elif choice == 3:
                self.budgets_menu_flow()
            elif choice == 4:
                self.transactions_menu_flow()
            elif choice == 5:
                self.analysis_menu_flow()
            elif choice == 6:
                print("Exiting...")
                break

# ------------------------------
# Application Entry Point
# ------------------------------

if __name__ == "__main__":
    # Set up database connection
    db = Database(
        host="localhost",
        user="kasak",
        password="1234",
        database="bas"
    )
    try:
        app = MainMenu(db)
        app.run()
    finally:
        if db:
            db.close()