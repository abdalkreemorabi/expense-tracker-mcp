# server.py
import sqlite3
import os
from mcp.server.fastmcp import FastMCP
from datetime import datetime, timedelta

# Create an MCP server
mcp = FastMCP(name="Expense Tracker")

def get_db_path():
    return os.path.join(os.path.dirname(__file__), 'transactions.db')

def check_category_limit(category: str, amount: float, currency: str = "USD") -> tuple[bool, str]:
    """Check if adding this expense would exceed the category limit."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get the category limit
    cursor.execute(
        "SELECT limit_amount, limit_type FROM category_limits WHERE category = ? AND currency = ?",
        (category, currency)
    )
    limit_result = cursor.fetchone()
    
    if not limit_result:
        conn.close()
        return True, "No limit set for this category"
    
    limit_amount, limit_type = limit_result
    
    # Calculate the current period's total spending
    now = datetime.now()
    if limit_type == 'daily':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
    elif limit_type == 'weekly':
        start_date = now - timedelta(days=now.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=7)
    elif limit_type == 'monthly':
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now.month == 12:
            end_date = now.replace(year=now.year + 1, month=1, day=1)
        else:
            end_date = now.replace(month=now.month + 1, day=1)
    
    cursor.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE category = ? AND currency = ? AND created_at >= ? AND created_at < ?",
        (category, currency, start_date.isoformat(), end_date.isoformat())
    )
    current_total = cursor.fetchone()[0]
    conn.close()
    
    if current_total + amount > limit_amount:
        return False, f"WARNING: Adding {amount} would exceed the {limit_type} limit of {limit_amount} for {category}. Current total: {current_total}"
    
    return True, f"OK: Current {limit_type} total for {category}: {current_total + amount}/{limit_amount}"

@mcp.tool()
def add_expense(category: str, amount: float, notes: str = "", currency: str = "USD") -> str:
    """Add a new expense to the expenses table with limit checking."""
    # Check category limit first
    within_limit, limit_message = check_category_limit(category, amount, currency)
    
    db_path = get_db_path()
    now = datetime.now().isoformat(sep=' ', timespec='seconds')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (category, amount, notes, currency, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
        (category, amount, notes, currency, now, now)
    )
    conn.commit()
    conn.close()
    
    result = f"Expense added: {category} - {amount} {currency} ({notes})"
    if not within_limit:
        result += f"\n⚠️ {limit_message}"
    else:
        result += f"\n✅ {limit_message}"
    
    return result

@mcp.tool()
def set_category_limit(category: str, limit_amount: float, limit_type: str, currency: str = "USD") -> str:
    """Set a spending limit for a category (daily, weekly, or monthly)."""
    if limit_type not in ['daily', 'weekly', 'monthly']:
        return "Error: limit_type must be 'daily', 'weekly', or 'monthly'"
    
    db_path = get_db_path()
    now = datetime.now().isoformat(sep=' ', timespec='seconds')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO category_limits (category, limit_amount, limit_type, currency, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (category, limit_amount, limit_type, currency, now, now))
        conn.commit()
        conn.close()
        return f"Limit set for {category}: {limit_amount} {currency} ({limit_type})"
    except Exception as e:
        conn.close()
        return f"Error setting limit: {str(e)}"

@mcp.tool()
def add_table_column(table_name: str, column_name: str, column_type: str, default_value: str | None = None, is_required: bool = False) -> str:
    """Add a new column to an existing table."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            conn.close()
            return f"Error: Table '{table_name}' does not exist"
        
        # Check if column already exists
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        if column_name in columns:
            conn.close()
            return f"Column '{column_name}' already exists in table '{table_name}'"
        
        # Build ALTER TABLE statement
        alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
        if default_value is not None:
            alter_sql += f" DEFAULT '{default_value}'"
        if is_required:
            alter_sql += " NOT NULL"
        
        cursor.execute(alter_sql)
        conn.commit()
        conn.close()
        return f"Column '{column_name}' added to table '{table_name}' successfully"
    except Exception as e:
        conn.close()
        return f"Error adding column: {str(e)}"

@mcp.tool()
def list_category_limits():
    """List all category limits."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT category, limit_amount, limit_type, currency FROM category_limits ORDER BY category")
    results = cursor.fetchall()
    conn.close()
    return [
        {
            "category": row[0],
            "limit_amount": row[1],
            "limit_type": row[2],
            "currency": row[3]
        }
        for row in results
    ]

@mcp.tool()
def total_expenses(start_date: str, end_date: str) -> float:
    """Calculate the total expenses between two dates (inclusive). Dates must be in YYYY-MM-DD format."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT SUM(amount) FROM expenses WHERE date(created_at) BETWEEN ? AND ?",
        (start_date, end_date)
    )
    result = cursor.fetchone()[0]
    conn.close()
    return result if result is not None else 0.0

@mcp.tool()
def average_transaction() -> float:
    """Get the average amount of all expenses."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT AVG(amount) FROM expenses")
    result = cursor.fetchone()[0]
    conn.close()
    return result if result is not None else 0.0

@mcp.tool()
def top_categories(n: int = 3):
    """Get the top N categories by total spending."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT category, SUM(amount) as total FROM expenses GROUP BY category ORDER BY total DESC LIMIT ?",
        (n,)
    )
    results = cursor.fetchall()
    conn.close()
    return [{"category": cat, "total": total} for cat, total in results]

@mcp.tool()
def list_expenses():
    """List all expenses in the expenses table."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, category, amount, notes, currency, created_at, updated_at FROM expenses ORDER BY created_at DESC")
    results = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "category": row[1],
            "amount": row[2],
            "notes": row[3],
            "currency": row[4],
            "created_at": row[5],
            "updated_at": row[6]
        }
        for row in results
    ]

# Run the server
if __name__ == "__main__":
    mcp.run()