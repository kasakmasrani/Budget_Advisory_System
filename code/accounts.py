
# ------------------------------
# Accounts Management
# ------------------------------
import traceback
from tabulate import tabulate
from database import Database
from rich.console import Console
from utils import InputUtils

class AccountsManager:
    """Manages account-related CRUD operations."""
    def __init__(self, db: Database):
        self.db = db
        self.accounts = []
        self.account_id_to_name = {}
        self.account_name_to_id = {}
        self.load_accounts()

    def load_accounts(self):
        try:
            self.accounts = self.db.fetch_all("SELECT * FROM accounts")
            self.account_id_to_name = {acc['account_id']: acc['account_name'] for acc in self.accounts}
            self.account_name_to_id = {acc['account_name'].casefold(): acc['account_id'] for acc in self.accounts}
        except Exception:
            traceback.print_exc()

    def add_account(self, account_name, initial_balance, account_type):
        console = Console()
        try:
            if not account_name or initial_balance is None or not account_type or account_type not in ['card', 'cash', 'savings', 'online']:
                console.print("[bold red]❌ Invalid account data.[/bold red]")
                return
            if float(initial_balance) < 0:
                console.print("[bold red]❌ Initial balance cannot be negative.[/bold red]")
                return

            query = """
            INSERT INTO accounts (account_name, initial_balance, account_type)
            VALUES (%s, %s, %s)
            """
            if self.db.execute(query, (account_name, float(initial_balance), account_type)):
                new_id = self.db.fetch_one("SELECT LAST_INSERT_ID()")['LAST_INSERT_ID()']

                self.account_id_to_name[new_id] = account_name
                self.account_name_to_id[account_name] = new_id
                self.accounts.append({
                    'account_id': new_id,
                    'account_name': account_name,
                    'initial_balance': float(initial_balance),
                    'account_type': account_type
                })

                console.print(f"[bold green]✅ Account '{account_name}' added successfully![/bold green]")
            else:
                console.print("[bold red]❌ Failed to add account.[/bold red]")
        except Exception as e:
            console.print(f"[bold red]⚠️ Error adding account: {e}[/bold red]")


    def search_accounts(self, account_name):
        return [account for account in self.accounts if account['account_name'].lower() == account_name.lower()]

    def update_account(self):
        try:
            self.load_accounts()
            account_name = InputUtils.get_string("Enter the account name to update: ").lower()
            if account_name not in [ name.lower() for name in self.account_name_to_id]:
                print("Account not found.")
                return
            matching_accounts = self.search_accounts(account_name)
            if len(matching_accounts)==1:
                account_id = matching_accounts[0]['account_id']
            else:
                print("Multiple accounts found with the specified name. Please select the account to delete.")
                for idx, account in enumerate(matching_accounts, start=1):
                    print(f"[{idx}] Name: {account['account_name']}, Type: {account['account_type']}, "
                        f"Balance: {account['initial_balance']}")
                
                try:
                    choice = int(input("Enter the number of the account you want to delete: "))
                    if choice < 1 or choice > len(matching_accounts):
                        print("Invalid selection.")
                        return
                    selected_account = matching_accounts[choice - 1]
                    account_id = selected_account['account_id']
                except ValueError:
                    print("Invalid input. Please enter a valid number.")
                    return

            new_name = InputUtils.get_string("Enter new account name (leave blank to keep same): ")
            new_balance = InputUtils.get_string("Enter new balance (leave blank to keep same): ")
            new_type = InputUtils.get_account_type("Enter new account type (card/cash/savings/online) (leave blank to keep same): ")

            if new_name:
                query = "UPDATE accounts SET account_name = %s WHERE account_id = %s"
                self.db.execute(query, (new_name, account_id))
            if new_balance:
                try:
                    new_balance = float(new_balance)
                    query = "UPDATE accounts SET initial_balance = %s WHERE account_id = %s"
                    self.db.execute(query, (new_balance, account_id))
                except ValueError:
                    print("Invalid balance entered.")
            if new_type:
                query = "UPDATE accounts SET account_type = %s WHERE account_id = %s"
                self.db.execute(query, (new_type, account_id))
            self.load_accounts()
            print(f"Account with ID {account_id} updated successfully.")
        except Exception as e:
            print(f"Error updating account: {e}")

    def delete_account(self):
        try:
            self.load_accounts()
            account_name = InputUtils.get_string("Enter the account name to delete: ")
            if account_name not in self.account_name_to_id:
                print("Account not found.")
                return
            matching_accounts = self.search_accounts(account_name)
            if not matching_accounts:
                print("No matching accounts found.")
                return
            
            if len(matching_accounts) == 1:
                account_id = matching_accounts[0]['account_id']
            else:
                print("Multiple accounts found with the specified name. Please select the account to delete.")
                for idx, account in enumerate(matching_accounts, start=1):
                    print(f"[{idx}] Name: {account['account_name']}, Type: {account['account_type']}, "
                        f"Balance: {account['initial_balance']}")
                
                try:
                    choice = int(input("Enter the number of the account you want to delete: "))
                    if choice < 1 or choice > len(matching_accounts):
                        print("Invalid selection.")
                        return
                    selected_account = matching_accounts[choice - 1]
                    account_id = selected_account['account_id']
                except ValueError:
                    print("Invalid input. Please enter a valid number.")
                    return
            
            confirm = InputUtils.get_string(f"Are you sure you want to delete '{account_name}'? (yes/no): ").lower()
            if confirm != "yes":
                print("Deletion cancelled.")
                return
            # Delete associated transactions first
            self.db.execute("DELETE FROM transactions WHERE account_id = %s", (account_id,))
            self.db.execute("DELETE FROM accounts WHERE account_id = %s", (account_id,))
            self.load_accounts()
            print(f"Account '{account_name}' deleted successfully.")
        except Exception as e:
            print(f"Error deleting account: {e}")

    def view_accounts(self):
        console = Console()
        try:
            self.load_accounts()
            if not self.accounts:
                console.print("[bold red]❌ No accounts found.[/bold red]")
                return
            
            headers = ["Index", "Name", "Balance", "Type"]
            rows = [[idx + 1, acc["account_name"], acc["initial_balance"], acc["account_type"]] for idx, acc in enumerate(self.accounts)]
            
            console.print("\n[bold cyan]📋 Accounts:[/bold cyan]")
            console.print(tabulate(rows, headers=headers, tablefmt="grid"))
        except Exception as e:
            console.print(f"[bold red]⚠️ Error viewing accounts: {e}[/bold red]")
