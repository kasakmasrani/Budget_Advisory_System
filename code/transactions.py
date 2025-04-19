# ------------------------------
# Transactions Management
# ------------------------------
from tabulate import tabulate
from database import Database
from utils import InputUtils
from accounts import AccountsManager
from categories import CategoryManager
from budget import BudgetManager
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt

class TransactionsManager:
    """Manages transactions, including transfers."""
    def __init__(self, db: Database, accounts_manager: AccountsManager, 
                 category_manager: CategoryManager, budget_manager: BudgetManager):
        self.db = db
        self.accounts_manager = accounts_manager
        self.category_manager = category_manager
        self.budget_manager = budget_manager
        self.transactions = []
        self.load_transactions()
        self.console = Console()

    def load_transactions(self):
        try:
            query = """
            SELECT t.transaction_id, a.account_name, c.category_name, t.transaction_type, 
                   t.amount, t.notes, t.transaction_date, t.transaction_time, t.account_id, t.category_id
            FROM transactions t
            LEFT JOIN accounts a ON t.account_id = a.account_id
            LEFT JOIN categories c ON t.category_id = c.category_id
            """
            self.transactions = self.db.fetch_all(query)
        except Exception as e:
            print(f"Error loading transactions: {e}")

    def add_transaction(self):
        try:
            # Step 1: Get transaction type
            transaction_type = InputUtils.get_string("Enter transaction type (income/expense/transfer): ").lower()
            if transaction_type not in ['income', 'expense', 'transfer']:
                self.console.print("[bold red]Invalid transaction type.[/bold red]")
                return

            if transaction_type == "transfer":
                self.transfer_funds()
                return

            # Step 2: Get account name
            account_name = InputUtils.get_string("Enter account name: ").casefold()
            if account_name not in [name.lower() for name in self.accounts_manager.account_name_to_id]:
                self.console.print("[bold red]Account not found.[/bold red]")
                return
            matching_accounts = self.accounts_manager.search_accounts(account_name)
            if len(matching_accounts) == 1:
                account_id = matching_accounts[0]['account_id']
                old_amount = matching_accounts[0]['initial_balance']
                if matching_accounts[0]['initial_balance'] <= 0 and transaction_type == "expense":
                    self.console.print("[bold red]Account balance is zero or negative. Please deposit funds first.[/bold red]")
                    return
            else:
                self.console.print("[bold yellow]Multiple accounts found with the specified name. Please select the account.[/bold yellow]")
                for idx, account in enumerate(matching_accounts, start=1):
                    self.console.print(f"[{idx}] Name: {account['account_name']}, Type: {account['account_type']}, "
                                       f"Balance: {account['initial_balance']}")
                try:
                    choice = int(input("Enter the number of the account you want to use: "))
                    if choice < 1 or choice > len(matching_accounts):
                        self.console.print("[bold red]Invalid selection.[/bold red]")
                        return
                    selected_account = matching_accounts[choice - 1]
                    account_id = selected_account['account_id']
                    old_amount = selected_account['initial_balance']
                    print(old_amount)
                except ValueError:
                    self.console.print("[bold red]Invalid input. Please enter a valid number.[/bold red]")
                    return

                if selected_account['initial_balance'] <= 0 and transaction_type == "expense":
                    self.console.print("[bold red]Account balance is zero or negative. Please deposit funds first.[/bold red]")
                    return

            # Step 3: Get category name and ensure it's valid
            category_name = InputUtils.get_string("Enter category name: ").casefold()
            if transaction_type == "income":
                matching_categories = {
                    name.casefold(): category
                    for name, category in self.category_manager.income_categories.items()
                }
                if category_name not in matching_categories:
                    self.console.print(f"[bold red]Income category '{category_name}' does not exist.[/bold red]")
                    return
                category_id = matching_categories[category_name]['category_id']

            elif transaction_type == "expense":
                matching_categories = {
                    name.casefold(): category
                    for name, category in self.category_manager.expense_categories.items()
                }
                if category_name not in matching_categories:
                    self.console.print(f"[bold red]Expense category '{category_name}' does not exist.[/bold red]")
                    return
                category_id = matching_categories[category_name]['category_id']

            # Step 4: Get transaction details
            amount = InputUtils.get_float("Enter amount: ", min_value=0.01)
            print(old_amount)
            if old_amount < amount and transaction_type == "expense":
                self.console.print("[bold red]Insufficient funds in account. Please deposit funds first.[/bold red]")
                return
            now = datetime.now()
            t_date = InputUtils.get_valid_date() or now.date()
            t_time = InputUtils.get_valid_date(is_time=True) or now.time()
            notes = InputUtils.get_string("Enter notes (optional): ")

            # Step 5: Insert transaction into the database
            query = """
            INSERT INTO transactions (account_id, category_id, transaction_type, amount, notes, transaction_date, transaction_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            if self.db.execute(query, (account_id, category_id, transaction_type.capitalize(), amount, notes, t_date, t_time)):
                self.load_transactions()

                # Step 6: Update the account balance after the transaction
                if transaction_type == "income":
                    self.db.execute("UPDATE accounts SET initial_balance = initial_balance + %s WHERE account_id = %s", (amount, account_id))
                elif transaction_type == "expense":
                    self.db.execute("UPDATE accounts SET initial_balance = initial_balance - %s WHERE account_id = %s", (amount, account_id))

                    self.budget_manager.load_budgets()
                    # Step 7: Update budget for the expense category (by calling the new method)
                    self.budget_manager.update_budget_after_transaction(category_name, amount)

                self.console.print("[bold green]✅ Transaction added successfully.[/bold green]")
            else:
                self.console.print("[bold red]❌ Failed to add transaction.[/bold red]")
        except Exception as e:
            self.console.print(f"[bold red]⚠️ Error adding transaction: {e}[/bold red]")

    def update_transaction(self):
        try:
            self.load_transactions()
            self.accounts_manager.load_accounts()
            self.category_manager.load_categories()
            if not self.transactions:
                print("No transactions to update.")
                return

            # Display transactions with index
            self.view_transactions()

            choice = InputUtils.get_float("Enter the index of the transaction to update: ")
            index = int(choice) - 1
            if index < 0 or index >= len(self.transactions):
                print("Invalid selection.")
                return
            transaction = self.transactions[index]
            
            if transaction["transaction_type"] != "Transfer":
                old_amount = transaction["amount"]
                old_category_id = transaction["category_id"]
                new_amount = input(f"Enter new amount (current: {transaction['amount']}): ").strip() or transaction["amount"]
                
                if isinstance(new_amount, str):
                    print("[bold red]Invalid amount.[/bold red]")
                    return
                    
                new_category = input(f"Enter new category (current: {transaction['category_name']}): ").strip() or transaction["category_name"]
                new_notes = input(f"Enter new notes (current: {transaction['notes']}): ").strip() or transaction["notes"]
                new_date = InputUtils.get_valid_date() or transaction["transaction_date"]
                new_time = InputUtils.get_valid_date(is_time=True) or transaction["transaction_time"]

                # Get new category id from category_manager
                new_category_lower = new_category.lower()
                new_category_id = None
                for name, details in self.category_manager.income_categories.items():
                    if name.lower() == new_category_lower:
                        new_category_id = details['category_id']
                        break
                if not new_category_id:
                    for name, details in self.category_manager.expense_categories.items():
                        if name.lower() == new_category_lower:
                            new_category_id = details['category_id']
                            break

                if not new_category_id:
                    print(f"Category '{new_category}' does not exist.")
                    return

                query = """
                UPDATE transactions
                SET category_id = %s, amount = %s, notes = %s, transaction_date = %s, transaction_time = %s
                WHERE transaction_id = %s
                """
                self.db.execute(query, (new_category_id, new_amount, new_notes, new_date, new_time, transaction["transaction_id"]))
                self.load_transactions()

                if transaction["transaction_type"].lower() == "expense":
                    query = """
                    UPDATE accounts
                    SET initial_balance = initial_balance + %s - %s
                    WHERE account_id = %s
                    """
                    self.db.execute(query, (old_amount, new_amount, transaction["account_id"]))
                    self.accounts_manager.load_accounts()

                    if old_category_id != new_category_id:
                        # Roll back spent amount from old category
                        query = """
                        UPDATE budgets
                        SET spent = spent - %s
                        WHERE category_id = %s
                        """
                        self.db.execute(query, (old_amount, old_category_id))

                        # Add spent amount to new category
                        query = """
                        UPDATE budgets
                        SET spent = spent + %s
                        WHERE category_id = %s
                        """
                        self.db.execute(query, (new_amount, new_category_id))
                    else:
                        query = """
                        UPDATE budgets
                        SET spent = spent - %s + %s
                        WHERE category_id = %s
                        """
                        self.db.execute(query, (old_amount, new_amount, new_category_id))

                    self.budget_manager.budgets = self.budget_manager.load_budgets()
                else:
                    query = """
                    UPDATE accounts
                    SET initial_balance = initial_balance - %s + %s
                    WHERE account_id = %s
                    """
                    self.db.execute(query, (old_amount, new_amount, transaction["account_id"]))
                    self.accounts_manager.load_accounts()

                self.category_manager.load_categories()
                self.console.print("[bold green]✅ Transaction updated successfully.[/bold green]")
            else:
                self.update_transfer_funds(transaction)
        except Exception as e:
            self.console.print(f"[bold red]⚠️ Error updating transaction: {e}[/bold red]")

    def delete_transaction(self):
        try:
            self.load_transactions()
            if not self.transactions:
                print("No transactions to delete.")
                return

            # Display transactions with index
            self.view_transactions()

            choice = InputUtils.get_float("Enter the index of the transaction to delete: ")
            index = int(choice) - 1
            if index < 0 or index >= len(self.transactions):
                print("Invalid selection.")
                return
            transaction = self.transactions[index]
            confirm = InputUtils.get_string("Are you sure you want to delete this transaction? (yes/no): ").lower()
            if confirm != "yes":
                print("Deletion cancelled.")
                return

            # Update account balance before deleting the transaction
            if transaction["transaction_type"].lower() == "income":
                account_balances = {acc['account_id']: acc['initial_balance'] for acc in self.accounts_manager.accounts}
                current_balance = account_balances.get(transaction["account_id"])  
                if current_balance <= 0 or current_balance < transaction["amount"]:
                    print("Account has insufficient funds for the transfer. Deletion will lead to negative balance")
                    confirm = InputUtils.get_string("Are you sure you want to delete this transaction? (yes/no): ").lower()
                    if confirm != "yes":
                        print("Deletion cancelled.")
                        return
                self.db.execute("UPDATE accounts SET initial_balance = initial_balance - %s WHERE account_id = %s", (transaction["amount"], transaction["account_id"]))
            elif transaction["transaction_type"].lower() == "expense":
                self.db.execute("UPDATE accounts SET initial_balance = initial_balance + %s WHERE account_id = %s", (transaction["amount"], transaction["account_id"]))
                self.budget_manager.update_budget_after_transaction(transaction["category_name"], -transaction["amount"])
            elif transaction["transaction_type"].lower() == "transfer":
                # Handle transfer deletion
                note_parts = transaction["notes"].split(":")
                if "Transfer to" in note_parts[0]:
                    source_id = transaction["account_id"]
                    dest_name = note_parts[0].replace("Transfer to ", "").strip()
                    dest_id = self.accounts_manager.account_name_to_id.get(dest_name.casefold())
                else:
                    dest_id = transaction["account_id"]
                    dest_name = self.accounts_manager.account_id_to_name.get(dest_id)
                    source_name = note_parts[0].replace("Transfer from ", "").strip()
                    source_id = self.accounts_manager.account_name_to_id.get(source_name.casefold())
                    

                if not dest_id or not source_id:
                    print("Error identifying transfer accounts.")
                    return
                
                
                account_balances = {acc['account_id']: acc['initial_balance'] for acc in self.accounts_manager.accounts}
                dest_current_balance = account_balances.get(dest_id)  
                print(dest_current_balance, transaction["amount"])
                if dest_current_balance <= 0 or dest_current_balance < transaction["amount"]:
                    print("Destination account has insufficient funds for the transfer. Deletion will lead to negative balance")
                    confirm = InputUtils.get_string("Are you sure you want to delete this transaction? (yes/no): ").lower()
                    if confirm != "yes":
                        print("Deletion cancelled.")
                        return
                    
                # Update balances
                self.db.execute("UPDATE accounts SET initial_balance = initial_balance - %s WHERE account_id = %s", (transaction["amount"], source_id))
                self.db.execute("UPDATE accounts SET initial_balance = initial_balance + %s WHERE account_id = %s", (transaction["amount"], dest_id))

                # Delete both transfer transactions (debit & credit)
                self.db.execute("DELETE FROM transactions WHERE account_id = %s AND notes LIKE %s", (source_id, f"Transfer to {dest_name}%"))
                self.db.execute("DELETE FROM transactions WHERE account_id = %s AND notes LIKE %s", (dest_id, f"Transfer from {transaction['account_name']}%"))

            self.accounts_manager.load_accounts()
            self.budget_manager.load_budgets()

            self.db.execute("DELETE FROM transactions WHERE transaction_id = %s", (transaction["transaction_id"],))
            self.load_transactions()
            self.console.print("[bold green]✅ Transaction deleted successfully.[/bold green]")
        except Exception as e:
            self.console.print(f"[bold red]⚠️ Error deleting transaction: {e}[/bold red]")

    def view_transactions(self):
        try:
            self.load_transactions()
            if not self.transactions:
                self.console.print("[bold yellow]No transactions found.[/bold yellow]")
                return
            
            table = Table(title="Transactions")
            table.add_column("Index", justify="center", style="cyan")
            table.add_column("Account", justify="center", style="cyan")
            table.add_column("Category", justify="center", style="cyan")
            table.add_column("Type", justify="center", style="cyan")
            table.add_column("Amount", justify="right", style="green")
            table.add_column("Notes", justify="center", style="cyan")
            table.add_column("Date", justify="center", style="cyan")
            table.add_column("Time", justify="center", style="cyan")

            for idx, t in enumerate(self.transactions, start=1):
                table.add_row(str(idx), t["account_name"], t["category_name"], t["transaction_type"],
                              f"${t['amount']:.2f}", t["notes"], str(t["transaction_date"]), str(t["transaction_time"]))
                table.add_row("", "", "", "", "", "", "", "")  # Add an empty row for spacing
            
            self.console.print(table)
        
        except Exception as e:
            self.console.print(f"[bold red]⚠️ Error viewing transactions: {e}[/bold red]")

    def transfer_funds(self):
        try:
            print("Transfer Funds")
            source = InputUtils.get_string("Enter source account name: ").casefold()
            dest = InputUtils.get_string("Enter destination account name: ").casefold()

            if source not in [name.lower() for name in self.accounts_manager.account_name_to_id]:
                self.console.print("[bold red]Source account not found.[/bold red]")
                return
            if dest not in [name.lower() for name in self.accounts_manager.account_name_to_id]:
                self.console.print("[bold red]Destination account not found.[/bold red]")
                return

            # Handle multiple source accounts with the same name
            matching_source_accounts = self.accounts_manager.search_accounts(source)
            if len(matching_source_accounts) == 1:
                source_id = matching_source_accounts[0]['account_id']
            else:
                self.console.print("[bold yellow]Multiple source accounts found with the specified name. Please select the account.[/bold yellow]")
                for idx, account in enumerate(matching_source_accounts, start=1):
                    self.console.print(f"[{idx}] Name: {account['account_name']}, Type: {account['account_type']}, "
                          f"Balance: {account['initial_balance']}")
                try:
                    choice = int(input("Enter the number of the source account you want to use: "))
                    if choice < 1 or choice > len(matching_source_accounts):
                        self.console.print("[bold red]Invalid selection.[/bold red]")
                        return
                    selected_account = matching_source_accounts[choice - 1]
                    source_id = selected_account['account_id']
                    if selected_account['initial_balance'] <= 0:
                        self.console.print("[bold red]Source account has insufficient funds.[/bold red]")
                        return
                    
                except ValueError:
                    self.console.print("[bold red]Invalid input. Please enter a valid number.[/bold red]")
                    return

            
            # Handle multiple destination accounts with the same name
            matching_dest_accounts = self.accounts_manager.search_accounts(dest)
            if len(matching_dest_accounts) == 1:
                dest_id = matching_dest_accounts[0]['account_id']
            else:
                self.console.print("\n[bold yellow]Multiple destination accounts found with the specified name. Please select the account.[/bold yellow]")
                for idx, account in enumerate(matching_dest_accounts, start=1):
                    self.console.print(f"[{idx}] Name: {account['account_name']}, Type: {account['account_type']}, "
                          f"Balance: {account['initial_balance']}")
                try:
                    choice = int(input("Enter the number of the destination account you want to use: "))
                    if choice < 1 or choice > len(matching_dest_accounts):
                        self.console.print("[bold red]Invalid selection.[/bold red]")
                        return
                    selected_account = matching_dest_accounts[choice - 1]
                    dest_id = selected_account['account_id']
                except ValueError:
                    self.console.print("[bold red]Invalid input. Please enter a valid number.[/bold red]")
                    return

            if source_id == dest_id:
                self.console.print("[bold red]Source and destination accounts cannot be the same.[/bold red]")
                return

            amount = InputUtils.get_float("Enter transfer amount: ") 
            if not amount:
                self.console.print("[bold red]Invalid input. Please enter a valid amount.[/bold red]")
                return
            amount = float(amount)
            now = datetime.now()
            t_date = InputUtils.get_valid_date() or now.date()
            t_time = InputUtils.get_valid_date(is_time=True) or now.time()
            notes = InputUtils.get_string("Enter transfer notes (optional): ")

            # Check sufficient balance
            src_balance = self.db.fetch_one("SELECT initial_balance FROM accounts WHERE account_id = %s", (source_id,))
            if src_balance is None or src_balance["initial_balance"] < amount:
                print(f"Insufficient funds in account '{source}'.")
                return

            # Record debit from source and credit to destination
            query = """
            INSERT INTO transactions (account_id, category_id, transaction_type, amount, notes, transaction_date, transaction_time)
            VALUES (%s, NULL, 'Transfer', %s, %s, %s, %s)
            """
            # Debit entry: negative amount
            self.db.execute(query, (source_id, -amount, f"Transfer to {dest}: {notes}", t_date, t_time))
            # Credit entry: positive amount
            self.db.execute(query, (dest_id, amount, f"Transfer from {source}: {notes}", t_date, t_time))
            # Update balances
            self.db.execute("UPDATE accounts SET initial_balance = initial_balance - %s WHERE account_id = %s", (amount, source_id))
            self.db.execute("UPDATE accounts SET initial_balance = initial_balance + %s WHERE account_id = %s", (amount, dest_id))
            self.load_transactions()
            self.console.print("[bold green]✅ Funds transferred successfully.[/bold green]")
        except Exception as e:
            self.console.print(f"[bold red]⚠️ Error during funds transfer: {e}[/bold red]")

    def update_transfer_funds(self, transaction):
        try:
            self.load_transactions()
            self.accounts_manager.load_accounts()

            old_amount = abs(transaction["amount"])

            # Get destination account ID
            note_parts = transaction["notes"].split(":")
            if "Transfer to" in note_parts[0]:
                source_id = transaction["account_id"]
                dest_name = note_parts[0].replace("Transfer to ", "").strip()
                dest_id = self.accounts_manager.account_name_to_id.get(dest_name.casefold())
            else:
                dest_id = transaction["account_id"]
                dest_name = self.accounts_manager.account_id_to_name.get(dest_id)
                source_name = note_parts[0].replace("Transfer from ", "").strip()
                source_id = self.accounts_manager.account_name_to_id.get(source_name.casefold())
            
            if not dest_id:
                print("Destination account not found.")
                return
            if not source_id:
                print("Source account not found.")
                return

            # Get new transaction details
            new_amount = InputUtils.get_string(f"Enter new amount (current: {transaction['amount']}): ") or old_amount
            if isinstance(new_amount, str):
                    print("[bold red]Invalid amount.[/bold red]")
                    return
            new_date = InputUtils.get_valid_date() or transaction["transaction_date"]
            new_time = InputUtils.get_valid_date(is_time=True) or transaction["transaction_time"]
            new_notes = InputUtils.get_string(f"Enter new notes (current: {transaction['notes']}): ").strip() 
            old_notes = transaction["notes"]

            # Ensure sufficient funds for the new transfer amount
            src_balance = self.db.fetch_one("SELECT initial_balance FROM accounts WHERE account_id = %s", (source_id,))
            if src_balance is None or (src_balance["initial_balance"] + abs(old_amount)) < new_amount:
                print(f"Insufficient funds in account '{transaction['account_name']}' after update.")
                return

            

            if new_notes != old_notes:
                # Update transfer transactions (debit & credit)
                query = """
                UPDATE transactions
                SET amount = %s, notes = %s, transaction_date = %s, transaction_time = %s
                WHERE account_id = %s AND notes LIKE %s
                """
                self.db.execute(query, (-new_amount, f"Transfer to {dest_name}: {new_notes}", new_date, new_time, source_id, f"Transfer to {dest_name}%"))
                self.db.execute(query, (new_amount, f"Transfer from {transaction['account_name']}: {new_notes}", new_date, new_time, dest_id, f"Transfer from {transaction['account_name']}%"))
            else:
                # Update transfer transactions (debit & credit)
                query = """
                UPDATE transactions
                SET amount = %s, transaction_date = %s, transaction_time = %s
                WHERE account_id = %s AND notes LIKE %s
                """
                self.db.execute(query, (-new_amount, new_date, new_time, source_id, f"Transfer to {dest_name}%"))
                self.db.execute(query, (new_amount, new_date, new_time, dest_id, f"Transfer from {transaction['account_name']}%"))

            # Adjust balances
            self.db.execute("UPDATE accounts SET initial_balance = initial_balance + %s - %s WHERE account_id = %s", (old_amount, new_amount, source_id))
            self.db.execute("UPDATE accounts SET initial_balance = initial_balance - %s + %s WHERE account_id = %s", (old_amount, new_amount, dest_id))

            self.load_transactions()
            self.console.print("[bold green]✅ Transfer transaction updated successfully.[/bold green]")

        except Exception as e:
            self.console.print(f"[bold red]⚠️ Error updating transfer transaction: {e}[/bold red]")
