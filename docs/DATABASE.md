# JimFinance Database Schema

## Overview

JimFinance uses PostgreSQL with a normalized schema designed for:
- Financial data integrity
- Efficient querying
- Scalability
- Multi-user support

## Entity Relationship Diagram

```
User (1) ──────────┬───────── (N) Account
                   │
                   ├────────── (N) Transaction
                   │
                   ├────────── (N) Category
                   │
                   ├────────── (N) Subscription
                   │
                   ├────────── (N) FinancialMemory
                   │
                   ├────────── (N) Forecast
                   │
                   └────────── (N) FinancialGoal

Category (1) ────────────────── (N) Transaction
Account (1) ────────────────── (N) Transaction
Account (1) ────────────────── (N) Subscription
```

## Table Schemas

### Users Table

Stores user account information and authentication data.

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    username VARCHAR UNIQUE NOT NULL,
    hashed_password VARCHAR NOT NULL,
    full_name VARCHAR NULL,
    avatar_url VARCHAR NULL,
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

**Fields:**
- `id`: Unique user identifier (PK)
- `email`: User email (unique, indexed)
- `username`: User username (unique, indexed)
- `hashed_password`: Bcrypt hashed password
- `full_name`: User's full name (optional)
- `avatar_url`: Profile picture URL (optional)
- `is_active`: Account activation status
- `is_verified`: Email verification status
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp

### Accounts Table

Stores user financial accounts (checking, savings, credit card, etc.)

```sql
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    name VARCHAR NOT NULL,
    account_type VARCHAR NOT NULL,
    currency VARCHAR DEFAULT 'USD',
    balance DECIMAL(15, 2) DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_accounts_user_id ON accounts(user_id);
CREATE INDEX idx_accounts_name ON accounts(name);
```

**Fields:**
- `id`: Account identifier (PK)
- `user_id`: Foreign key to users (FK)
- `name`: Account name (e.g., "Main Checking")
- `account_type`: Type (checking, savings, credit_card, investment, cash)
- `currency`: Account currency (RUB, USD, EUR, INR, GBP)
- `balance`: Current balance
- `is_active`: Account status
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Categories Table

Transaction categories for organizing expenses.

```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    name VARCHAR NOT NULL,
    description VARCHAR NULL,
    category_type VARCHAR NOT NULL,
    color VARCHAR DEFAULT '#808080',
    icon VARCHAR NULL,
    is_default BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_categories_user_id ON categories(user_id);
CREATE INDEX idx_categories_name ON categories(name);
```

**Fields:**
- `id`: Category identifier (PK)
- `user_id`: Foreign key to users (FK)
- `name`: Category name
- `description`: Category description (optional)
- `category_type`: Type (food, transport, entertainment, utilities, etc.)
- `color`: Hex color code for UI
- `icon`: Icon identifier
- `is_default`: Default category flag
- `created_at`: Creation timestamp

### Transactions Table

Core financial transactions data.

```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    account_id INTEGER NOT NULL REFERENCES accounts(id),
    category_id INTEGER REFERENCES categories(id),
    
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR NOT NULL,
    merchant VARCHAR NOT NULL,
    description VARCHAR NULL,
    transaction_type VARCHAR NOT NULL,
    
    transaction_date TIMESTAMP WITH TIME ZONE NOT NULL,
    is_recurring BOOLEAN DEFAULT false,
    recurring_pattern VARCHAR NULL,
    
    confidence_score FLOAT DEFAULT 1.0,
    is_duplicate BOOLEAN DEFAULT false,
    source_type VARCHAR DEFAULT 'manual',
    raw_input TEXT NULL,
    
    is_anomaly BOOLEAN DEFAULT false,
    anomaly_score FLOAT NULL,
    
    tags JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_account_id ON transactions(account_id);
CREATE INDEX idx_transactions_category_id ON transactions(category_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_merchant ON transactions(merchant);
```

**Fields:**
- `id`: Transaction identifier (PK)
- `user_id`: Foreign key to users (FK)
- `account_id`: Foreign key to accounts (FK)
- `category_id`: Foreign key to categories (FK, nullable)
- `amount`: Transaction amount
- `currency`: Transaction currency
- `merchant`: Merchant name
- `description`: Transaction description
- `transaction_type`: Type (income, expense, transfer)
- `transaction_date`: When transaction occurred
- `is_recurring`: Recurring transaction flag
- `recurring_pattern`: Pattern (daily, weekly, monthly, yearly)
- `confidence_score`: AI confidence in categorization
- `is_duplicate`: Duplicate detection flag
- `source_type`: Source (manual, telegram, ocr, api)
- `raw_input`: Original input
- `is_anomaly`: Anomaly detection flag
- `anomaly_score`: Anomaly score
- `tags`: JSON array of tags
- `metadata`: JSON metadata
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Subscriptions Table

Recurring subscriptions and billing tracking.

```sql
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    account_id INTEGER NOT NULL REFERENCES accounts(id),
    
    name VARCHAR NOT NULL,
    merchant VARCHAR NOT NULL,
    category_id INTEGER REFERENCES categories(id),
    
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR NOT NULL,
    billing_cycle VARCHAR NOT NULL,
    billing_date INTEGER NOT NULL,
    
    is_active BOOLEAN DEFAULT true,
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE NULL,
    
    auto_renew BOOLEAN DEFAULT true,
    cancellation_date TIMESTAMP WITH TIME ZONE NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_is_active ON subscriptions(is_active);
```

**Fields:**
- `id`: Subscription identifier (PK)
- `user_id`: Foreign key to users (FK)
- `account_id`: Foreign key to accounts (FK)
- `name`: Subscription name
- `merchant`: Service provider
- `category_id`: Category reference
- `amount`: Monthly/yearly amount
- `currency`: Currency
- `billing_cycle`: Period (monthly, yearly, weekly)
- `billing_date`: Day of month (1-31)
- `is_active`: Active status
- `start_date`: Subscription start
- `end_date`: Subscription end (if known)
- `auto_renew`: Auto-renewal flag
- `cancellation_date`: When cancelled
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Financial Memory Table

Persistent behavioral insights and patterns.

```sql
CREATE TABLE financial_memory (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    
    memory_type VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    description TEXT NOT NULL,
    data JSONB NOT NULL,
    
    confidence_score FLOAT DEFAULT 0.8,
    is_validated BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_financial_memory_user_id ON financial_memory(user_id);
CREATE INDEX idx_financial_memory_type ON financial_memory(memory_type);
```

**Fields:**
- `id`: Memory identifier (PK)
- `user_id`: Foreign key to users (FK)
- `memory_type`: Type (spending_pattern, behavior, insight, goal)
- `title`: Memory title
- `description`: Detailed description
- `data`: JSON data structure
- `confidence_score`: Confidence level
- `is_validated`: User validation flag
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Forecasts Table

Financial projections and predictions.

```sql
CREATE TABLE forecasts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    
    forecast_type VARCHAR NOT NULL,
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    
    predicted_value DECIMAL(15, 2) NOT NULL,
    confidence_interval_low DECIMAL(15, 2) NULL,
    confidence_interval_high DECIMAL(15, 2) NULL,
    confidence_score FLOAT NOT NULL,
    
    methodology VARCHAR NOT NULL,
    parameters JSONB NOT NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_forecasts_user_id ON forecasts(user_id);
CREATE INDEX idx_forecasts_type ON forecasts(forecast_type);
```

**Fields:**
- `id`: Forecast identifier (PK)
- `user_id`: Foreign key to users (FK)
- `forecast_type`: Type (cashflow, spending, income, runway)
- `period_start`: Forecast period start
- `period_end`: Forecast period end
- `predicted_value`: Predicted value
- `confidence_interval_low`: Lower bound
- `confidence_interval_high`: Upper bound
- `confidence_score`: Confidence level
- `methodology`: Algorithm used (ARIMA, Prophet, etc.)
- `parameters`: JSON algorithm parameters
- `created_at`: Creation timestamp

### Financial Goals Table

User financial goals and targets.

```sql
CREATE TABLE financial_goals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    
    name VARCHAR NOT NULL,
    description VARCHAR NULL,
    goal_type VARCHAR NOT NULL,
    
    target_amount DECIMAL(15, 2) NOT NULL,
    current_progress DECIMAL(15, 2) DEFAULT 0,
    currency VARCHAR NOT NULL,
    
    target_date TIMESTAMP WITH TIME ZONE NOT NULL,
    priority INTEGER DEFAULT 1,
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_financial_goals_user_id ON financial_goals(user_id);
CREATE INDEX idx_financial_goals_is_active ON financial_goals(is_active);
```

**Fields:**
- `id`: Goal identifier (PK)
- `user_id`: Foreign key to users (FK)
- `name`: Goal name
- `description`: Goal description
- `goal_type`: Type (savings, investment, debt_payoff)
- `target_amount`: Target amount
- `current_progress`: Current progress
- `currency`: Currency
- `target_date`: Target completion date
- `priority`: Priority level (1-5)
- `is_active`: Active status
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Indexes

### Performance-Critical Indexes

```sql
-- User lookups
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- Account queries
CREATE INDEX idx_accounts_user_id ON accounts(user_id);

-- Transaction filtering
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_account_id ON transactions(account_id);
CREATE INDEX idx_transactions_category_id ON transactions(category_id);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_transactions_merchant ON transactions(merchant);

-- Category queries
CREATE INDEX idx_categories_user_id ON categories(user_id);

-- Subscription filtering
CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_is_active ON subscriptions(is_active);

-- Financial memory
CREATE INDEX idx_financial_memory_user_id ON financial_memory(user_id);
CREATE INDEX idx_financial_memory_type ON financial_memory(memory_type);

-- Forecasts
CREATE INDEX idx_forecasts_user_id ON forecasts(user_id);

-- Goals
CREATE INDEX idx_financial_goals_user_id ON financial_goals(user_id);
```

## Data Types

### Custom Enums
```sql
-- Currency
CREATE TYPE currency_enum AS ENUM ('RUB', 'USD', 'EUR', 'INR', 'GBP');

-- Account Type
CREATE TYPE account_type_enum AS ENUM (
    'checking', 'savings', 'credit_card', 'investment', 'cash'
);

-- Transaction Type
CREATE TYPE transaction_type_enum AS ENUM ('income', 'expense', 'transfer');

-- Transaction Category
CREATE TYPE category_enum AS ENUM (
    'food', 'transport', 'entertainment', 'utilities', 'healthcare',
    'shopping', 'subscriptions', 'salary', 'investment', 'transfer', 'other'
);
```

## Query Examples

### Monthly Spending Summary
```sql
SELECT
    category_id,
    SUM(amount) as total,
    COUNT(*) as transaction_count
FROM transactions
WHERE user_id = 1
  AND transaction_type = 'expense'
  AND DATE_TRUNC('month', transaction_date) = DATE_TRUNC('month', CURRENT_DATE)
GROUP BY category_id
ORDER BY total DESC;
```

### Active Subscriptions
```sql
SELECT
    name,
    amount,
    billing_cycle,
    (amount / CASE
        WHEN billing_cycle = 'monthly' THEN 1
        WHEN billing_cycle = 'yearly' THEN 12
        WHEN billing_cycle = 'weekly' THEN 4.33
    END) as monthly_cost
FROM subscriptions
WHERE user_id = 1 AND is_active = true;
```

### Financial Runway
```sql
SELECT
    SUM(balance) as total_balance,
    AVG(amount) as avg_daily_expense,
    SUM(balance) / AVG(amount) as runway_days
FROM accounts a
LEFT JOIN transactions t ON a.id = t.account_id
WHERE a.user_id = 1
  AND t.transaction_type = 'expense'
  AND t.transaction_date >= CURRENT_DATE - INTERVAL '30 days';
```

## Future Enhancements

1. **Audit Logging** - Track data changes
2. **Multi-Tenancy** - Support multiple organizations
3. **Time Series Data** - Optimized for time-based queries
4. **Data Archiving** - Archive old transactions
5. **Full-Text Search** - Search transactions and descriptions
