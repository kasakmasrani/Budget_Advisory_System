# ------------------------------
# Category Management
# ------------------------------

from database import Database
from tabulate import tabulate
from rich.console import Console

class CategoryManager:
    """Manages income and expense categories."""
    def __init__(self, db: Database):
        self.db = db
        self.income_categories = {}   # key: category name, value: {category_id, description}
        self.expense_categories = {}
        self.load_categories()
        self.console = Console()

    def get_category_name_by_id(self, category_id):
        """Returns the category name by its ID."""
        try:
            # Check in income categories
            for name, data in self.income_categories.items():
                if data['category_id'] == category_id:
                    return name
            # Check in expense categories
            for name, data in self.expense_categories.items():
                if data['category_id'] == category_id:
                    return name
            return None  # If not found
        except Exception as e:
            print(f"Error getting category name by ID: {e}")
            return None

    def get_category_id_by_name(self, category_name):
        """Returns the category ID by its name (case-insensitive)."""
        try:
            category_name_lower = category_name.lower()  # Normalize input

            # Check in income categories (case-insensitive)
            for name, details in self.income_categories.items():
                if name.lower() == category_name_lower:
                    return details['category_id']

            # Check in expense categories (case-insensitive)
            for name, details in self.expense_categories.items():
                if name.lower() == category_name_lower:
                    return details['category_id']

            return None  # If not found
        except Exception as e:
            print(f"Error getting category ID by name: {e}")
            return None

    def load_categories(self):
        try:
            categories = self.db.fetch_all("SELECT * FROM categories")
            income_rows = self.db.fetch_all(
                """
                SELECT ic.income_category_id, c.category_id, c.category_name, c.description
                FROM income_categories ic
                JOIN categories c ON ic.category_id = c.category_id
                """
            )
            expense_rows = self.db.fetch_all(
                """
                SELECT ec.expense_category_id, c.category_id, c.category_name, c.description
                FROM expense_categories ec
                JOIN categories c ON ec.category_id = c.category_id
                """
            )
            self.income_categories = {row['category_name']: {'category_id': row['category_id'], 'description': row['description']} for row in income_rows}
            self.expense_categories = {row['category_name']: {'category_id': row['category_id'], 'description': row['description']} for row in expense_rows}

            # Create mappings for categories
            self.category_id_to_name = {cat['category_id']: cat['category_name'] for cat in categories}
            self.category_name_to_id = {cat['category_name']: cat['category_id'] for cat in categories}

        except Exception as e:
            print(f"Error loading categories: {e}")

    def add_category(self, category_name, category_type, description=None):
        try:
            self.load_categories()
            category_name_lower = category_name.lower()
            if category_name_lower in [name.lower() for name in self.income_categories] or category_name_lower in [name.lower() for name in self.expense_categories]:
                print("Category already exists.")
                return
            # Insert into categories table
            self.db.execute("INSERT INTO categories (category_name, description) VALUES (%s, %s)",
                            (category_name, description))
            row = self.db.fetch_one("SELECT category_id FROM categories WHERE category_name = %s", (category_name,))
            if not row:
                print("Error retrieving category id.")
                return
            category_id = row['category_id']
            if category_type.lower() == "income":
                self.db.execute("INSERT INTO income_categories (category_id) VALUES (%s)", (category_id,))
                self.income_categories[category_name] = {'category_id': category_id, 'description': description}
            elif category_type.lower() == "expense":
                self.db.execute("INSERT INTO expense_categories (category_id) VALUES (%s)", (category_id,))
                self.expense_categories[category_name] = {'category_id': category_id, 'description': description}
            else:
                print("Invalid category type. Please specify 'income' or 'expense'.")
                return
            self.console.print(f"[bold green]✅ Category '{category_name}' added successfully.[/bold green]")
        except Exception as e:
            self.console.print(f"[bold red]⚠️ Error adding category: {e}[/bold red]")

    def update_category(self, category_name, new_name=None, new_description=None):
        try:
            self.load_categories()
            category_name_lower = category_name.lower()
            cat_data = None

            # Search for the category in a case-insensitive manner
            for name, data in self.income_categories.items():
                if name.lower() == category_name_lower:
                    cat_data = data
                    break
            if not cat_data:
                for name, data in self.expense_categories.items():
                    if name.lower() == category_name_lower:
                        cat_data = data
                        break

            if not cat_data:
                print("Category not found.")
                return

            updates = []
            params = []
            if new_name:
                updates.append("category_name = %s")
                params.append(new_name)
            if new_description:
                updates.append("description = %s")
                params.append(new_description)
            if not updates:
                print("No updates provided.")
                return
            params.append(cat_data["category_id"])
            query = f"UPDATE categories SET {', '.join(updates)} WHERE category_id = %s"
            self.db.execute(query, tuple(params))
            self.load_categories()
            self.console.print(f"[bold green]✅ Category '{category_name}' updated successfully.[/bold green]")
        except Exception as e:
            self.console.print(f"[bold red]⚠️ Error updating category: {e}[/bold red]")

    def delete_category(self, category_name):
        try:
            self.load_categories()
            category_name_lower = category_name.lower()
            cat_data = None
            table = None

            # Search for the category in a case-insensitive manner
            for name, data in self.income_categories.items():
                if name.lower() == category_name_lower:
                    cat_data = data
                    table = "income_categories"
                    break
            if not cat_data:
                for name, data in self.expense_categories.items():
                    if name.lower() == category_name_lower:
                        cat_data = data
                        table = "expense_categories"
                        break

            if not cat_data:
                print("Category not found.")
                return

            if table == "expense_categories":
                self.db.execute("DELETE FROM budgets WHERE category_id = %s", (cat_data["category_id"],))
            self.db.execute(f"DELETE FROM {table} WHERE category_id = %s", (cat_data["category_id"],))
            self.db.execute("DELETE FROM transactions WHERE category_id = %s", (cat_data["category_id"],))
            self.db.execute("DELETE FROM categories WHERE category_id = %s", (cat_data["category_id"],))
            self.load_categories()
            self.console.print(f"[bold green]✅ Category '{category_name}' deleted successfully.[/bold green]")
        except Exception as e:
            self.console.print(f"[bold red]⚠️ Error deleting category: {e}[/bold red]")

    def view_categories(self):
        try:
            self.load_categories()
            
            # Income categories with dynamic index
            self.console.print("[bold green]Income Categories:[/bold green]")
            income_table = [
                [idx, name, data.get('description', 'No description available')]
                for idx, (name, data) in enumerate(self.income_categories.items(), start=1)
            ]
            self.console.print(tabulate(income_table, headers=["Index", "Name", "Description"], tablefmt="fancy_grid", stralign="center"))
            
            # Expense categories with dynamic index
            self.console.print("\n[bold red]Expense Categories:[/bold red]")
            expense_table = [
                [idx, name, data.get('description', 'No description available')]
                for idx, (name, data) in enumerate(self.expense_categories.items(), start=1)
            ]
            self.console.print(tabulate(expense_table, headers=["Index", "Name", "Description"], tablefmt="fancy_grid", stralign="center"))
            
        except Exception as e:
            self.console.print(f"[bold red]⚠️ Error viewing categories: {e}[/bold red]")
