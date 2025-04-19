# 💰 Budget Advisory System

A Python-based console application that helps individuals and small businesses manage their finances through budgeting, transaction tracking, and financial analysis.

## 🎯 Objective

To provide a centralized platform for:
- Tracking income, expenses, and budgets
- Visualizing financial trends
- Offering AI-powered insights and alerts to improve financial decisions

---

## 🧩 Features

### ✅ Core Functionalities
- **Accounts Management**: Add, update, and delete financial accounts (Cash, Card, Savings, Online).
- **Categories Management**: Define and organize expense and income categories.
- **Transactions**: Record income, expenses, and transfers between accounts.
- **Budget Management**: Set monthly limits per category and receive real-time alerts.
- **Financial Analysis**:
  - Spending pattern analysis
  - Income stability evaluation
  - Anomaly detection in spending
  - Visual summaries and breakdowns

### 📊 Visualizations
- Pie charts, bar graphs, and line plots using `Matplotlib` and `Seaborn`.

### ⚠️ Alerts & Insights
- Get notified when you are about to exceed your budget.
- View personalized budget advice and recommendations.

---

## 🛠️ Tech Stack

| Component      | Tool / Library                  |
|----------------|----------------------------------|
| Programming    | Python                          |
| Database       | MySQL                           |
| Visualization  | Matplotlib, Seaborn             |
| Data Handling  | Pandas, NumPy                   |
| CLI Interface  | Rich, Tabulate, Colorama        |
| Development    | VS Code, MySQL Workbench        |

---

## 📁 Modules Overview

| Module          | Description |
|-----------------|-------------|
| `main.py`       | Entry point and menu navigation |
| `accounts.py`   | Manage account-related operations |
| `categories.py` | Create, view, update categories |
| `transactions.py`| Manage all types of transactions |
| `budget.py`     | Set, update, delete budgets and trigger alerts |
| `analysis.py`   | Perform financial analysis and visualization |
| `database.py`   | Database connector and query execution |
| `utils.py`      | Input validation helpers |

---

## 🗃️ Database Schema

The project uses multiple normalized tables such as:
- `accounts`
- `transactions`
- `categories`, `income_categories`, `expense_categories`
- `budgets`

The schema is available in the `bas.sql` file.

---

## 🚀 Future Enhancements

- 📱 **Mobile App** with offline support and push notifications
- 🏦 **Bank Integration** for real-time sync
- 🤖 **AI Insights** for predictive budgeting
- 🔐 **Security Features** like 2FA, encryption
- 🎙️ **Voice-based Commands**
- 📈 **Investment Portfolio Management**

---

## ⚙️ How to Run

1. **Clone the repository**:
   ```bash
   git clone https://github.com/kasakmasrani/Budget_Advisory_System.git
   cd Budget_Advisory_System
   ```

2. **Setup a MySQL database using `bas.sql`**:
   - Open MySQL Workbench or any preferred tool.
   - Create a new database (e.g., `budget_db`).
   - Execute the SQL script from `bas.sql` to create required tables and relationships.

3. **Update database credentials**:
   - Open the `database.py` file.
   - Replace the placeholders with your actual database credentials:
     ```python
     self.connection = mysql.connector.connect(
         host="localhost",
         user="your_mysql_user",
         password="your_mysql_password",
         database="budget_db"
     )
     ```

4. **Install Python dependencies**:
   Make sure you have Python 3.8+ installed.
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**:
   ```bash
   python main.py
   ```

---

## 🗃️ Sample Credentials

Make sure your MySQL user has permissions to create and read from tables.  
Create a user (if needed):

```sql
CREATE USER 'budget_user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON budget_db.* TO 'budget_user'@'localhost';
FLUSH PRIVILEGES;
```

---

## 👩‍💻 Contributors

- **Kasak Masrani**  
  B.E. Computer Engineering Student  
  Developer of the Budget Advisory System  
  Participant, Hackathon 6.0

---

## 📜 License

This project is licensed under the **MIT License**.  
Feel free to use, modify, and distribute it with attribution.

---

## 🌐 Connect

If you like this project or want to collaborate, feel free to connect with me on [GitHub](https://github.com/kasakmasrani).
