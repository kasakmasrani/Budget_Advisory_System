# ------------------------------
# Analysis Management
# ------------------------------
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
from database import Database
from transactions import TransactionsManager



class AnalysisManager:
    """Provides AI-powered financial analysis and insights."""
    def __init__(self, db: Database, transaction_manager: TransactionsManager):
        self.db = db
        self.console = Console()
        self.transaction_manager = transaction_manager

        
    def spending_patterns(self):
        """Analyzes spending behavior and detects overspending trends."""
        try:
            # Fetch transactions from the transaction manager
            df = self.transaction_manager.transactions
            
            # Check if the DataFrame is empty or None
            if df is None or len(df) == 0:
                self.console.print("[bold yellow]No transaction data available for analysis.[/bold yellow]")
                return
            
            # Filter only expenses
            expense_df = [transaction for transaction in df if transaction['transaction_type'].lower() == 'expense']

            if not expense_df:
                self.console.print("[bold yellow]No expense data available for analysis.[/bold yellow]")
                return
            
            # Create DataFrame from the filtered expenses
            expense_df = pd.DataFrame(expense_df)

            # Convert amount to numeric (handling Decimal type)
            expense_df['amount'] = pd.to_numeric(expense_df['amount'], errors='coerce')

            # Drop any rows where 'amount' could not be converted
            expense_df = expense_df.dropna(subset=['amount'])

            # Group by category_name and sum the amounts
            grouped = expense_df.groupby('category_name')['amount'].sum().reset_index()

            # Ensure there are valid expense categories
            if grouped.empty:
                self.console.print("[bold yellow]No valid expense data available for analysis.[/bold yellow]")
                return

            # Get top 5 spending categories
            top_categories = grouped.nlargest(5, 'amount')

            # Display table
            self.console.print(Panel("💰 [bold cyan]Top 5 Spending Categories:[/bold cyan]", style="bold white"))
            table = Table(title="Top Spending Categories")
            table.add_column("Category Name", justify="center", style="cyan")
            table.add_column("Total Spent ($)", justify="right", style="red")

            for _, row in top_categories.iterrows():
                table.add_row(row['category_name'], f"${row['amount']:.2f}")

            self.console.print(table)

            # Plot bar chart
            sns.barplot(x='category_name', y='amount', data=top_categories, hue='category_name', palette='coolwarm', legend=False)

            plt.xlabel("Category Name")
            plt.ylabel("Total Spent ($)")
            plt.title("Top Spending Categories")
            plt.show()
        except Exception as e:
            self.console.print(f"[bold red]⚠️ Error in spending patterns analysis: {e}[/bold red]")

    def income_stability(self):
        """Analyzes fluctuations in income over time and provides a clear conclusion."""
        try:
            # Convert the list of dictionaries to a DataFrame
            df = pd.DataFrame(self.transaction_manager.transactions)

            # Check if DataFrame is empty
            if df.empty:
                self.console.print("[bold yellow]No income data available.[/bold yellow]")
                return

            # Filter for income transactions (create a copy to avoid SettingWithCopyWarning)
            income_df = df[df['transaction_type'] == 'Income'].copy()

            # Convert transaction_date to datetime safely
            income_df['transaction_date'] = pd.to_datetime(income_df['transaction_date'], errors='coerce')

            # Drop rows with invalid dates
            income_df.dropna(subset=['transaction_date'], inplace=True)

            # Convert amount to float safely
            income_df['amount'] = income_df['amount'].astype(float)

            # Group by month-end ('ME' replaces deprecated 'M')
            monthly_income = income_df.groupby(pd.Grouper(key='transaction_date', freq='ME'))['amount'].sum()

            # Calculate mean and standard deviation of income
            mean_income = monthly_income.mean()
            std_income = monthly_income.std()

            # Display results
            self.console.print(f"[bold cyan]📊 Average Monthly Income: ${mean_income:.2f}[/bold cyan]")
            self.console.print(f"[bold red]📉 Income Volatility (Std Dev): ${std_income:.2f}[/bold red]")

            # Determine income stability
            if std_income == 0:
                conclusion = "Your income is completely stable with no fluctuations."
            elif std_income < (0.2 * mean_income):
                conclusion = "Your income is relatively stable with minimal fluctuations."
            elif std_income < (0.5 * mean_income):
                conclusion = "Your income shows moderate fluctuations. Consider setting aside savings to manage variations."
            else:
                conclusion = "Your income is highly unstable. You may need a financial buffer to handle income variations."

            # Print the conclusion
            self.console.print(f"[bold green]🔍 Conclusion: {conclusion}[/bold green]")

            # Plot the income trend
            plt.figure(figsize=(8, 5))
            plt.plot(monthly_income.index, monthly_income.values, marker='o', linestyle='-')
            plt.axhline(mean_income, color='r', linestyle='dashed', label='Avg Income')
            plt.xlabel("Month")
            plt.ylabel("Income ($)")
            plt.title("Income Stability Analysis")
            plt.legend()
            plt.grid(True)
            plt.show()
        except Exception as e:
            self.console.print(f"[bold red]⚠️ Error in income stability analysis: {e}[/bold red]")

    def anomaly_detection(self):
        """Detects unusual spending or income patterns based on the provided transaction data."""
        try:
            # Assuming self.transaction_manager.transactions holds the transaction data
            df = pd.DataFrame(self.transaction_manager.transactions)
            
            if df.empty:
                self.console.print("[bold yellow]No transaction data available.[/bold yellow]")
                return
            
            # Filter for expense transactions
            expense_df = df[df['transaction_type'] == 'Expense'].copy()  # Use .copy() to avoid warning
            if expense_df.empty:
                self.console.print("[bold yellow]No expense data available for analysis.[/bold yellow]")
                return
            
            # Convert 'amount' to float for calculations to avoid issues with Decimal
            expense_df['amount'] = expense_df['amount'].apply(lambda x: float(x))  # Convert Decimal to float
            
            # Calculate the threshold for anomalies: mean + 2 * standard deviation
            threshold = expense_df['amount'].mean() + 2 * expense_df['amount'].std()
            anomalies = expense_df[expense_df['amount'] > threshold]
            
            # Handle the case where no anomalies are found
            if anomalies.empty:
                self.console.print("[bold green]No anomalies detected in spending.[/bold green]")
                return
            
            # Print a panel with the warning for detected anomalies
            self.console.print(Panel("🚨 [bold red]Anomalous Transactions Detected![/bold red]", style="bold white"))
            
            # Display a table with suspicious transactions
            table = Table(title="Suspicious Transactions")
            table.add_column("Date", style="cyan")
            table.add_column("Amount ($)", justify="right", style="red")
            for _, row in anomalies.iterrows():
                table.add_row(str(row['transaction_date']), f"${row['amount']:.2f}")
            self.console.print(table)
            
            # Plot a boxplot to visualize anomalies
            plt.figure(figsize=(8, 5))
            sns.boxplot(y=expense_df['amount'])
            plt.title("Expense Anomaly Detection")
            plt.show()

            # Provide conclusions for user clarity
            self.console.print("[bold magenta]Conclusion:[/bold magenta]")
            self.console.print("[bold green]1. Anomaly Detection Complete – The system analyzed all expense transactions to identify unusual spending patterns.[/bold green]")
            self.console.print("[bold cyan]2. Identified Suspicious Transactions – Transactions exceeding the mean by more than two standard deviations have been flagged as potential anomalies.[/bold cyan]")
            self.console.print("[bold yellow]3. Boxplot Visualization – A boxplot is provided to help you visualize the distribution of expenses and identify outliers more easily.[/bold yellow]")
            self.console.print("[bold blue]4. Financial Review Recommended – If any anomalies are detected, it's recommended to review the flagged transactions for further insights.[/bold blue]")
        except Exception as e:
            self.console.print(f"[bold red]⚠️ Error in anomaly detection: {e}[/bold red]")

    def expense_overview(self):
        """Provides a detailed breakdown of all expenses."""
        try:
            df = pd.DataFrame(self.transaction_manager.transactions)
            
            if df.empty:
                self.console.print("[bold yellow]No expense data available for overview.[/bold yellow]")
                return
            
            expense_df = df[df['transaction_type'] == 'Expense'].copy()
            try:
                # Use .loc to avoid SettingWithCopyWarning
                expense_df.loc[:, 'amount'] = pd.to_numeric(expense_df['amount'], errors='coerce')
                expense_df.dropna(subset=['amount'], inplace=True)
            except Exception as e:
                self.console.print(f"[bold red]⚠️ Error in expense overview: {e}[/bold red]")
            
            # Group by category for detailed breakdown
            expense_category_summary = expense_df.groupby('category_name')['amount'].sum().reset_index()
            
            # Display the breakdown in a table
            self.console.print(Panel("💸 [bold cyan]Expense Overview:[/bold cyan]", style="bold white"))
            table = Table(title="Expense Breakdown")
            table.add_column("Category Name", justify="center", style="cyan")
            table.add_column("Total Spent ($)", justify="right", style="red")

            for _, row in expense_category_summary.iterrows():
                table.add_row(row['category_name'], f"${row['amount']:.2f}")
            
            self.console.print(table)

            # Plot bar chart of expenses by category
            sns.barplot(x='category_name', y='amount', data=expense_category_summary, hue='category_name', palette='coolwarm', legend=False)
            plt.xlabel("Category Name")
            plt.ylabel("Total Spent ($)")
            plt.title("Expense Breakdown")
            plt.show()
        except Exception as e:
            self.console.print(f"[bold red]⚠️ Error in expense overview: {e}[/bold red]")

    def income_overview(self):
        """Provides a detailed breakdown of all income."""
        try:
            df = pd.DataFrame(self.transaction_manager.transactions)
            
            if df.empty:
                self.console.print("[bold yellow]No income data available for overview.[/bold yellow]")
                return
            
            income_df = df[df['transaction_type'] == 'Income'].copy()
            income_df.loc[:, 'amount'] = pd.to_numeric(income_df['amount'], errors='coerce')
            income_df.dropna(subset=['amount'], inplace=True)
            
            # Group by income source or type for detailed breakdown
            income_source_summary = income_df.groupby('category_name')['amount'].sum().reset_index()
            
            # Display the breakdown in a table
            self.console.print(Panel("💰 [bold cyan]Income Overview:[/bold cyan]", style="bold white"))
            table = Table(title="Income Breakdown")
            table.add_column("Source Name", justify="center", style="cyan")
            table.add_column("Total Income ($)", justify="right", style="green")

            for _, row in income_source_summary.iterrows():
                table.add_row(row['category_name'], f"${row['amount']:.2f}")
            
            self.console.print(table)

            # Plot bar chart of income by source
            sns.barplot(x='category_name', y='amount', data=income_source_summary, hue='category_name', palette='viridis', legend=False)
            plt.xlabel("Source Name")
            plt.ylabel("Total Income ($)")
            plt.title("Income Breakdown")
            plt.show()
        except Exception as e:
            self.console.print(f"[bold red]⚠️ Error in income overview: {e}[/bold red]")

    def expense_flow(self):
        """Shows the trend of expenses over time."""
        try:
            df = pd.DataFrame(self.transaction_manager.transactions)
            
            if df.empty:
                self.console.print("[bold yellow]No expense data available for flow analysis.[/bold yellow]")
                return
            
            expense_df = df[df['transaction_type'] == 'Expense'].copy()
            expense_df.loc[:, 'transaction_date'] = pd.to_datetime(expense_df['transaction_date'], errors='coerce')
            expense_df.dropna(subset=['transaction_date'], inplace=True)
            
            # Ensure the dtype is inferred correctly
            expense_df['transaction_date'] = expense_df['transaction_date'].infer_objects()
            
            # Group by month-end ('ME' replaces deprecated 'M')
            monthly_expense_flow = expense_df.groupby(pd.Grouper(key='transaction_date', freq='ME'))['amount'].sum()

            # Plot expense flow trend
            plt.figure(figsize=(8, 5))
            plt.plot(monthly_expense_flow.index, monthly_expense_flow.values, marker='o', linestyle='-', color='red')
            plt.xlabel("Month")
            plt.ylabel("Total Expense ($)")
            plt.title("Monthly Expense Flow")
            plt.grid(True)
            plt.show()
        except Exception as e:
            self.console.print(f"[bold red]⚠️ Error in expense flow analysis: {e}[/bold red]")

    def income_flow(self):
        """Shows the trend of income over time."""
        try:
            df = pd.DataFrame(self.transaction_manager.transactions)
            
            if df.empty:
                self.console.print("[bold yellow]No income data available for flow analysis.[/bold yellow]")
                return
            
            income_df = df[df['transaction_type'] == 'Income'].copy()
            income_df.loc[:, 'transaction_date'] = pd.to_datetime(income_df['transaction_date'], errors='coerce')
            income_df.dropna(subset=['transaction_date'], inplace=True)
            
            # Ensure the dtype is inferred correctly
            income_df['transaction_date'] = income_df['transaction_date'].infer_objects()
            
            # Group by month-end ('ME' replaces deprecated 'M')
            monthly_income_flow = income_df.groupby(pd.Grouper(key='transaction_date', freq='ME'))['amount'].sum()

            # Plot income flow trend
            plt.figure(figsize=(8, 5))
            plt.plot(monthly_income_flow.index, monthly_income_flow.values, marker='o', linestyle='-', color='green')
            plt.xlabel("Month")
            plt.ylabel("Total Income ($)")
            plt.title("Monthly Income Flow")
            plt.grid(True)
            plt.show()
        except Exception as e:
            self.console.print(f"[bold red]⚠️ Error in income flow analysis: {e}[/bold red]")

    def run_full_analysis(self):
        """Executes all analysis functions."""
        try:
            for task in track([self.spending_patterns, self.income_stability, self.anomaly_detection,
                                self.expense_overview, self.income_overview, self.expense_flow, self.income_flow], description="Running full analysis..."):
                task()
            self.console.print("[bold green]✅ Full analysis completed successfully![/bold green]")
        except Exception as e:
            self.console.print(f"[bold red]⚠️ Error during full analysis: {e}[/bold red]")

