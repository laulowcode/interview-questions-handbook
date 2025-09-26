#!/usr/bin/env python3
"""
ACID - Consistency Example
Demonstrates database constraints preventing invalid states
"""

import sqlite3

def setup_database_with_constraints(conn):
    """
    Setup database with CHECK constraint to ensure balance is not negative.
    """
    cursor = conn.cursor()
    # CHECK(balance >= 0) constraint is the key to consistency here
    cursor.execute("""
        CREATE TABLE accounts (
            id TEXT PRIMARY KEY,
            balance REAL NOT NULL CHECK(balance >= 0)
        )
    """)
    cursor.execute("INSERT INTO accounts (id, balance) VALUES ('A', 1000)")
    conn.commit()
    print("--- Initial State ---")
    print_balance(conn, 'A')

def print_balance(conn, account_id):
    """Print balance of an account."""
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM accounts WHERE id = ?", (account_id,))
    balance = cursor.fetchone()[0]
    print(f"  Account {account_id}: {balance}")

def attempt_withdrawal(conn, account_id, amount):
    """Attempt to withdraw money from an account."""
    print(f"\n--- Attempting to withdraw {amount} from account {account_id} ---")
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, account_id))
        conn.commit()
        print("=> Transaction SUCCESSFUL.")
    except sqlite3.IntegrityError as e:
        # This error occurs when CHECK constraint is violated
        print(f"  (!) Error: {e}")
        print("=> Transaction FAILED. Consistency constraint prevented the change.")
        conn.rollback()

def main():
    """Main execution scenario"""
    # Use in-memory database
    conn = sqlite3.connect(":memory:")
    
    # 1. Setup database and constraints
    setup_database_with_constraints(conn)
    
    # 2. Scenario 1: Invalid transaction (constraint violation)
    #    Attempt to withdraw 1200 while balance is only 1000, would create negative balance.
    attempt_withdrawal(conn, 'A', 1200)
    print("\n--- State after invalid transaction ---")
    print_balance(conn, 'A')  # Balance unchanged
    
    # 3. Scenario 2: Valid transaction
    #    Withdraw 300, remaining balance 700 (still >= 0), complies with constraint.
    attempt_withdrawal(conn, 'A', 300)
    print("\n--- State after valid transaction ---")
    print_balance(conn, 'A')  # Balance has been updated
    
    conn.close()

if __name__ == "__main__":
    main()
