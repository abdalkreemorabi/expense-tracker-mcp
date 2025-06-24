# MCP Expense Tracker

## Overview
A Model Context Protocol (MCP) server implementation that provides comprehensive expense tracking
and budget management capabilities through SQLite. This server enables 
adding expenses, setting spending limits, analyzing spending patterns,
and automatically checking budget compliance with multi-currency support.

## Components

### Tools
The server offers eight core tools for expense management:

#### Expense Management Tools
- `add_expense`
  - Add new expenses with automatic limit checking
  - Input:
    - `category` (string): Expense category
    - `amount` (float): Expense amount
    - `notes` (string, optional): Additional notes
    - `currency` (string, optional): Currency code (default: USD)
  - Returns: Confirmation with limit status

- `list_expenses`
  - Retrieve all expenses with full details
  - No input required
  - Returns: Array of expense objects with id, category, amount, notes, currency, timestamps

#### Budget Management Tools
- `set_category_limit`
  - Set spending limits for categories with time periods
  - Input:
    - `category` (string): Category name
    - `limit_amount` (float): Spending limit amount
    - `limit_type` (string): Time period (daily, weekly, monthly)
    - `currency` (string, optional): Currency code (default: USD)
  - Returns: Confirmation of limit setting

- `list_category_limits`
  - View all configured category limits
  - No input required
  - Returns: Array of limit objects with category, amount, type, currency

#### Analysis Tools
- `total_expenses`
  - Calculate total expenses between two dates
  - Input:
    - `start_date` (string): Start date in YYYY-MM-DD format
    - `end_date` (string): End date in YYYY-MM-DD format
  - Returns: Total amount as float

- `average_transaction`
  - Calculate average expense amount across all transactions
  - No input required
  - Returns: Average amount as float

- `top_categories`
  - Get top spending categories by total amount
  - Input:
    - `n` (integer, optional): Number of categories to return (default: 3)
  - Returns: Array of category objects with name and total spending

#### Database Management Tools
- `add_table_column`
  - Add new columns to existing tables dynamically
  - Input:
    - `table_name` (string): Target table name
    - `column_name` (string): New column name
    - `column_type` (string): SQLite data type
    - `default_value` (string, optional): Default value for the column
    - `is_required` (boolean, optional): Whether column is NOT NULL
  - Returns: Confirmation of column addition

## Database Schema

### Expenses Table
- `id`: Primary key (auto-increment)
- `category`: Expense category (required)
- `amount`: Expense amount (required)
- `notes`: Optional description
- `currency`: Currency code (default: USD)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Category Limits Table
- `id`: Primary key (auto-increment)
- `category`: Category name (unique, required)
- `limit_amount`: Spending limit amount (required)
- `limit_type`: Time period (daily, weekly, monthly, required)
- `currency`: Currency code (default: USD)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Usage with Claude Desktop

### Local Development

```bash
# Clone and setup
git clone <your-repo-url>
cd expense-tracker-mcp
uv venv .venv --python=python3.12
source .venv/bin/activate
uv sync

# Initialize database
python init_transactions_db.py

# Run server
mcp dev server.py
```

### Configuration

Add the server to your `claude_desktop_config.json`:

```json
"mcpServers": {
  "expense-tracker": {
    "command": "python",
    "args": [
      "/path/to/expense-tracker-mcp/server.py"
    ]
  }
}
```

## Usage with VS Code

For quick installation, add the following configuration to your VS Code settings:

```json
{
  "mcp": {
    "servers": {
      "expense-tracker": {
        "command": "python",
        "args": [
          "${workspaceFolder}/server.py"
        ]
      }
    }
  }
}
```

## Features

### Budget Enforcement
- Automatic limit checking when adding expenses
- Support for daily, weekly, and monthly limits
- Real-time warnings when limits are exceeded
- Multi-currency support for international users

### Data Analysis
- Spending pattern analysis by category
- Time-based expense tracking
- Average transaction calculations
- Top spending category identification

### Database Flexibility
- Dynamic schema modification
- Extensible table structure
- Clean initialization without test data
- Professional data management

## Requirements
- Python 3.12
- uv package manager
- MCP (mcp[cli])
- SQLite (included with Python)

## License

This MCP server is licensed under the MIT License. This means you are free to use, modify, and distribute the software, subject to the terms and conditions of the MIT License.
