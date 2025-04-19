-- Create the database
CREATE DATABASE bas;
USE bas;

-- Main Categories Table
CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY, -- Unique ID for the category
    category_name VARCHAR(50) NOT NULL,        -- Name of the category
    description TEXT,                          -- Description of the category
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Timestamp for creation
);

-- Income Categories Table
CREATE TABLE income_categories (
    income_category_id INT AUTO_INCREMENT PRIMARY KEY, -- Unique ID for the income category
    category_id INT NOT NULL,                         -- Foreign key referencing categories
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
    ON DELETE CASCADE                                  -- Cascade delete for related rows
);

-- Expense Categories Table
CREATE TABLE expense_categories (
    expense_category_id INT AUTO_INCREMENT PRIMARY KEY, -- Unique ID for the expense category
    category_id INT NOT NULL,                          -- Foreign key referencing categories
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
    ON DELETE CASCADE                                   -- Cascade delete for related rows
);

-- Accounts Table
CREATE TABLE accounts (
    account_id INT AUTO_INCREMENT PRIMARY KEY,          -- Unique ID for the account
    account_name VARCHAR(50) NOT NULL,                 -- Name of the account
    account_type ENUM('Card', 'Cash', 'Savings', 'Online') NOT NULL, -- Type of account
    initial_balance DECIMAL(10, 2) NOT NULL,           -- Initial balance in the account
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP     -- Timestamp for account creation
);

-- Transactions Table
CREATE TABLE transactions (
    transaction_id INT AUTO_INCREMENT PRIMARY KEY,      -- Unique ID for the transaction
    account_id INT NOT NULL,                            -- Foreign key referencing accounts
    category_id INT,                                    -- Foreign key referencing categories
    transaction_type ENUM('Income', 'Expense', 'Transfer') NOT NULL, -- Type of transaction
    amount DECIMAL(10, 2) NOT NULL,                    -- Amount of transaction
    notes TEXT,                                        -- Notes for the transaction
    transaction_date DATE NOT NULL,                   -- Date of the transaction
    transaction_time TIME NOT NULL,                   -- Time of the transaction
    FOREIGN KEY (account_id) REFERENCES accounts(account_id), -- FK constraint on accounts
    FOREIGN KEY (category_id) REFERENCES categories(category_id) -- FK constraint on categories
);

-- Budgets Table
CREATE TABLE budgets (
    budget_id INT AUTO_INCREMENT PRIMARY KEY,          -- Unique ID for the budget
    category_id INT NOT NULL,                          -- Foreign key referencing categories
    monthly_limit DECIMAL(10, 2) NOT NULL,            -- Monthly limit for the budget
    spent DECIMAL(10, 2) DEFAULT 0,                   -- Amount spent
    remaining DECIMAL(10, 2) AS (monthly_limit - spent) STORED, -- Calculated remaining amount
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,   -- Timestamp for creation
    FOREIGN KEY (category_id) REFERENCES expense_categories(expense_category_id)
    ON DELETE CASCADE                                  -- Cascade delete for related rows
);





select * from accounts;
select * from transactions;
select * from income_categories;
select * from expense_categories;
select * from categories;
select * from budgets;


INSERT INTO categories (category_name, description) VALUES
('Salary', 'Monthly salary from employer'),
('Freelance', 'Income from freelance work'),
('Groceries', 'Expenses for groceries'),
('Rent', 'Monthly rent payment'),
('Utilities', 'Expenses for utilities like electricity, water, etc.'),
('Entertainment', 'Expenses for entertainment activities'),
('Dining', 'Expenses for dining out'),
('Travel', 'Expenses for travel and vacations'),
('Healthcare', 'Expenses for healthcare and medical needs'),
('Education', 'Expenses for education and learning');

INSERT INTO income_categories (category_id) VALUES
(1), (2);

INSERT INTO expense_categories (category_id) VALUES
(3), (4), (5), (6), (7), (8), (9), (10);

INSERT INTO accounts (account_name, account_type, initial_balance) VALUES
('Checking Account', 'Card', 1500.00),
('Savings Account', 'Savings', 5000.00),
('Cash Wallet', 'Cash', 200.00),
('Online Wallet', 'Online', 300.00),
('Credit Card', 'Card', 1000.00),
('Business Account', 'Card', 2500.00),
('Emergency Fund', 'Savings', 10000.00),
('Travel Fund', 'Savings', 1500.00),
('Investment Account', 'Online', 7000.00),
('Petty Cash', 'Cash', 100.00);

INSERT INTO transactions (account_id, category_id, transaction_type, amount, notes, transaction_date, transaction_time) VALUES
(1, 1, 'Income', 3000.00, 'Monthly salary', '2023-01-01', '09:00:00'),
(2, 2, 'Income', 1500.00, 'Freelance project', '2023-01-05', '10:00:00'),
(1, 3, 'Expense', 200.00, 'Grocery shopping', '2023-01-10', '11:00:00'),
(1, 4, 'Expense', 800.00, 'Monthly rent', '2023-01-15', '12:00:00'),
(1, 5, 'Expense', 100.00, 'Electricity bill', '2023-01-20', '13:00:00'),
(1, 6, 'Expense', 50.00, 'Movie tickets', '2023-01-25', '14:00:00'),
(1, 7, 'Expense', 75.00, 'Dinner at restaurant', '2023-01-30', '15:00:00'),
(1, 8, 'Expense', 500.00, 'Vacation trip', '2023-02-01', '16:00:00'),
(1, 9, 'Expense', 150.00, 'Doctor visit', '2023-02-05', '17:00:00'),
(1, 10, 'Expense', 200.00, 'Online course', '2023-02-10', '18:00:00');


INSERT INTO budgets (category_id, monthly_limit, spent) VALUES
(3, 500.00, 200.00),
(4, 1000.00, 800.00),
(5, 150.00, 100.00),
(6, 100.00, 50.00),
(7, 200.00, 75.00),
(8, 1000.00, 500.00),
(9, 300.00, 150.00),
(10, 400.00, 200.00);