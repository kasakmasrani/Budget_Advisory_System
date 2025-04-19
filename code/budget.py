from decimal import Decimal
from database import Database
from categories import CategoryManager
from tabulate import tabulate
from utils import InputUtils
from datetime import datetime
from decimal import Decimal
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

class BudgetManager:
    """Manages user budgets, including adding, updating, tracking categories, and recurring budgets."""

    def __init__(self, db: Database, category_manager: CategoryManager):
        self.db = db
        self.category_manager = category_manager
        self.budgets = self.load_budgets()
        self.console = Console()

    def load_budgets(self):
        """Loads all budget data from the database."""
        try:
            query = """
            SELECT budget_id, category_id, monthly_limit, spent
            FROM budgets
            """
            budgets_data = self.db.fetch_all(query)
            budgets = {}
            for budget in budgets_data:
                budgets[budget["category_id"]] = budget
            return budgets
        except Exception as e:
            print(f"Error loading budgets: {e}")
            return {}

    def view_budgets(self):
        """Displays current budget allocations for each category."""
        try:
            self.budgets = self.load_budgets()
            if not self.budgets:
                self.console.print("[bold yellow]No budgets found.[/bold yellow]")
                return

            table = Table(title="Budgets")
            table.add_column("Category", justify="center", style="cyan")
            table.add_column("Monthly Limit", justify="right", style="green")
            table.add_column("Spent", justify="right", style="red")
            table.add_column("Remaining", justify="right", style="yellow")

            for category_id, budget in self.budgets.items():
                category_name = self.category_manager.get_category_name_by_id(category_id)
                remaining = budget["monthly_limit"] - budget["spent"]
                table.add_row(category_name, f"${budget['monthly_limit']:.2f}", f"${budget['spent']:.2f}", f"${remaining:.2f}")

            self.console.print(table)
        except Exception as e:
            self.console.print(f"[bold red]⚠️ Error viewing budgets: {e}[/bold red]")

    def add_budget(self):
        """Adds a new budget for a category and retroactively accounts for past transactions in the current month."""
        try:
            category_name = InputUtils.get_string("Enter category name for the budget: ")
            if category_name.lower() not in ( c.lower() for c in self.category_manager.expense_categories):
                print(f"Category '{category_name}' does not exist.")
                return
            category_id = self.category_manager.get_category_id_by_name(category_name)
            monthly_limit = InputUtils.get_float("Enter monthly limit: ", min_value=0.01)

            # Get current year and month
            now = datetime.now()
            current_year = now.year
            current_month = now.month

            # Calculate total spent for this category in the current month
            query = """
            SELECT COALESCE(SUM(amount), 0) AS total_spent
            FROM transactions
            WHERE category_id = %s 
            AND transaction_type = 'Expense'
            AND EXTRACT(YEAR FROM transaction_date) = %s
            AND EXTRACT(MONTH FROM transaction_date) = %s
            """
            result = self.db.fetch_one(query, (category_id, current_year, current_month))
            spent = result["total_spent"] if result else 0

            # Insert budget into database
            query = """
            INSERT INTO budgets (category_id, monthly_limit, spent)
            VALUES (%s, %s, %s)
            """
            success = self.db.execute(query, (category_id, Decimal(monthly_limit), spent))
            if success:
                self.budgets = self.load_budgets()
                self.console.print(f"[bold green]✅ Budget for '{category_name}' added successfully with {spent} already spent this month.[/bold green]")
            else:
                self.console.print("[bold red]❌ Failed to add budget.[/bold red]")

        except Exception as e:
            self.console.print(f"[bold red]⚠️ Error adding budget: {e}[/bold red]")

    def update_budget(self):
        """Updates the budget for an existing category."""
        try:
            self.view_budgets()
            category_name = InputUtils.get_string("Enter the category name to update the budget: ").capitalize()

            category_id = self.category_manager.get_category_id_by_name(category_name)
            if category_id not in self.budgets:
                print(f"No budget found for '{category_name}'.")
                return

            budget = self.budgets[category_id]
            new_monthly_limit = InputUtils.get_float(f"Enter new monthly limit (current: {budget['monthly_limit']}): ", min_value=0.01)

            query = """
            UPDATE budgets
            SET monthly_limit = %s
            WHERE budget_id = %s
            """
            success = self.db.execute(query, (Decimal(new_monthly_limit), budget["budget_id"]))
            if success:
                self.budgets = self.load_budgets()
                self.console.print(f"[bold green]✅ Budget for '{category_name}' updated successfully.[/bold green]")
            else:
                self.console.print("[bold red]❌ Failed to update budget.[/bold red]")
        except Exception as e:
            self.console.print(f"[bold red]⚠️ Error updating budget: {e}[/bold red]")

    def delete_budget(self):
        """Deletes a budget for a category."""
        try:
            self.view_budgets()
            category_name = InputUtils.get_string("Enter the category name to delete the budget: ")

            category_id = self.category_manager.get_category_id_by_name(category_name)
            if category_id not in self.budgets:
                print(f"No budget found for '{category_name}'.")
                return

            confirm = InputUtils.get_string(f"Are you sure you want to delete the budget for '{category_name}'? (yes/no): ").lower()
            if confirm != "yes":
                print("Deletion cancelled.")
                return

            query = "DELETE FROM budgets WHERE budget_id = %s"
            success = self.db.execute(query, (self.budgets[category_id]["budget_id"],))
            if success:
                self.budgets = self.load_budgets()
                self.console.print(f"[bold green]✅ Budget for '{category_name}' deleted successfully.[/bold green]")
            else:
                self.console.print("[bold red]❌ Failed to delete budget.[/bold red]")
        except Exception as e:
            self.console.print(f"[bold red]⚠️ Error deleting budget: {e}[/bold red]")

    def update_budget_after_transaction(self, category_name, amount):
        """Updates the budget for a category after a transaction."""
        try:
            category_id = self.category_manager.get_category_id_by_name(category_name)
            if category_id not in self.budgets:
                print(f"No budget found for '{category_name}'.")
                return

            budget = self.budgets[category_id]
            updated_spent = budget["spent"] + Decimal(amount)

            query = """
            UPDATE budgets
            SET spent = %s
            WHERE budget_id = %s
            """
            success = self.db.execute(query, (updated_spent, budget["budget_id"]))
            if success:
                self.budgets = self.load_budgets()
                self.console.print(f"[bold green]✅ Budget for '{category_name}' updated successfully after the transaction.[/bold green]")
            else:
                self.console.print("[bold red]❌ Failed to update budget after transaction.[/bold red]")

            # Budget Alerting
            self.check_budget_alerts(category_id, updated_spent)
            self.load_budgets()
        except Exception as e:
            self.console.print(f"[bold red]⚠️ Error updating budget after transaction: {e}[/bold red]")

    def check_budget_alerts(self, category_id=None, updated_spent=None):
        """Checks if the user has exceeded or is near exceeding their budget."""
        try:
            if category_id is None:
                category_name = InputUtils.get_string("Enter Category name: ")
                category_id = self.category_manager.get_category_id_by_name(category_name)
            if updated_spent is None:
                updated_spent = self.budgets[category_id]["spent"]
            budget = self.budgets.get(category_id)
            if budget:
                category_name = self.category_manager.get_category_name_by_id(category_id)
                monthly_limit = float(budget["monthly_limit"])
                remaining = monthly_limit - float(updated_spent)
                spent_percentage = (float(updated_spent) / monthly_limit) * 100
                alert_threshold = monthly_limit * 0.9  # Set alert threshold to 90% of budget
                if float(updated_spent) >= alert_threshold:
                    self.console.print(f"[bold yellow]⚠️ Alert: You are nearing the budget for '{category_name}'! Remaining balance: {remaining:.2f} / {monthly_limit:.2f} ({spent_percentage:.2f}% spent)[/bold yellow]")
                elif float(updated_spent) > monthly_limit:
                    self.console.print(f"[bold red]🚨 Warning: You have exceeded the budget for '{category_name}'! Current balance: {updated_spent:.2f} / {monthly_limit:.2f} ({spent_percentage:.2f}% spent)[/bold red]")
                else:
                    self.console.print(f"[bold green]✅ No budget alert for '{category_name}' as you are within the budget. ({spent_percentage:.2f}% spent)[/bold green]")
                print()

                # Ask user if they want to see suggestions
                choice = InputUtils.get_valid_menu_choice("Would you like to see suggestions on managing your budget? (1 for Yes, 2 for No): ", ['1', '2'])
                if choice == 1:
                    self.provide_budget_advice(category_name)
        except:
            self.console.print("[bold red]⚠️ Error checking budget alerts.[/bold red]")

    def provide_budget_advice(self, category_name):
        """Provides dynamic advice on managing expenses and budget based on user-specific expenditures."""
        try:
            category_id = self.category_manager.get_category_id_by_name(category_name)
            if category_id not in self.budgets:
                self.console.print(f"[bold red]No budget found for '{category_name}'.[/bold red]")
                return

            budget = self.budgets[category_id]
            monthly_limit = float(budget["monthly_limit"])
            spent = float(budget["spent"])
            remaining = monthly_limit - spent

            print()
            self.console.print(f"[bold cyan]💡 Budget Advice for '{category_name}':[/bold cyan]")
            self.console.print(f"[bold yellow]You have spent {spent:.2f} out of {monthly_limit:.2f} ({(spent / monthly_limit) * 100:.2f}%).[/bold yellow]")
            self.console.print(f"[bold green]Remaining budget: {remaining:.2f}[/bold green]")
            print()

            # Analyze where the most expense is done
            query = """
            SELECT c.category_name, SUM(t.amount) as total_spent
            FROM transactions t
            JOIN categories c ON t.category_id = c.category_id
            WHERE t.transaction_type = 'Expense'
            GROUP BY c.category_name
            ORDER BY total_spent DESC
            LIMIT 5
            """
            results = self.db.fetch_all(query)
            if results:
                self.console.print("[bold red]Top spending categories:[/bold red]")
                for result in results:
                    category = result["category_name"]
                    total_spent = result["total_spent"]
                    self.console.print(f"[bold red]{category}: {total_spent:.2f}[/bold red]")

            print()
            # Provide dynamic advice based on user-specific expenses
            self.console.print("[bold green]Specific Advice:[/bold green]")
            for result in results:
                category = result["category_name"]
                total_spent = result["total_spent"]
                if category.lower() in ["dining", "entertainment", "luxurious items"]:
                    self.console.print(f"[bold green]{category}: You have spent {total_spent:.2f} on {category}. Consider reducing spending in this area by opting for home-cooked meals, free or low-cost entertainment options, and limiting non-essential luxury purchases.[/bold green]")
                elif category.lower() == "travel":
                    self.console.print(f"[bold green]{category}: You have spent {total_spent:.2f} on travel. Consider using public transportation, carpooling, or planning trips during off-peak times to save money.[/bold green]")
                elif category.lower() == "groceries":
                    self.console.print(f"[bold green]{category}: You have spent {total_spent:.2f} on groceries. Plan your meals, make a shopping list, and avoid impulse buys to reduce grocery expenses.[/bold green]")
                elif category.lower() == "healthcare":
                    self.console.print(f"[bold green]{category}: You have spent {total_spent:.2f} on healthcare. Review your healthcare plan and consider preventive care to reduce costs.[/bold green]")
                elif category.lower() == "education":
                    self.console.print(f"[bold green]{category}: You have spent {total_spent:.2f} on education. Look for scholarships, grants, or free courses to reduce education expenses.[/bold green]")
                else:
                    self.console.print(f"[bold green]{category}: You have spent {total_spent:.2f} on {category}. Review your spending in this category and identify areas where you can cut back.[/bold green]")

            # Provide general advice
            self.console.print("\n[bold green]General Advice:[/bold green]")
            self.console.print("[bold green]1. Review your expenses and identify areas where you can cut back.[/bold green]")
            self.console.print("[bold green]2. Set a realistic budget based on your income and savings goals.[/bold green]")
            self.console.print("[bold green]3. Track your spending regularly to stay within your budget.[/bold green]")
            self.console.print("[bold green]4. Consider setting aside a portion of your income for savings and emergencies.[/bold green]")
        except Exception as e:
            self.console.print(f"[bold red]⚠️ Error providing budget advice: {e}[/bold red]")
