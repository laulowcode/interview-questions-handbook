#!/usr/bin/env python3
"""
ACID - Atomicity Example
Demonstrates all-or-nothing transaction behavior
"""

import sqlite3

def setup_and_print_initial_state(conn):
    """Setup initial database and print balances."""
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS accounts (id TEXT PRIMARY KEY, balance REAL)")
    cursor.execute("INSERT OR REPLACE INTO accounts (id, balance) VALUES ('A', 1000), ('B', 500)")
    conn.commit()
    print("--- Initial State ---")
    for row in cursor.execute("SELECT id, balance FROM accounts"):
        print(f"  Account {row[0]}: {row[1]}")

def atomic_transfer(conn, from_acc, to_acc, amount, simulate_error=False):
    """
    Perform an atomic money transfer transaction.
    If error occurs, all changes will be rolled back.
    """
    print(f"\n--- Starting transaction (transfer {amount} from {from_acc} to {to_acc}) ---")
    cursor = conn.cursor()
    try:
        # Step 1: Deduct money from source account
        cursor.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (amount, from_acc))
        print(f"  (1) Deducted {amount} from account {from_acc}.")

        # Simulate a system error occurring mid-transaction
        if simulate_error:
            raise ValueError("Sudden system error!")

        # Step 2: Add money to destination account
        cursor.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (amount, to_acc))
        print(f"  (2) Added {amount} to account {to_acc}.")

        # If all steps succeed, commit to save changes
        conn.commit()
        print("=> Transaction SUCCESSFUL. Changes have been saved.")

    except Exception as e:
        # If any error occurs, rollback all changes
        conn.rollback()
        print(f"  (!) Error occurred: {e}")
        print("=> Transaction FAILED. Rolled back to initial state.")

def main():
    """Main execution scenario"""
    conn = sqlite3.connect(":memory:")

    # 1. Success scenario
    setup_and_print_initial_state(conn)
    atomic_transfer(conn, 'A', 'B', 100, simulate_error=False)

    # Print balances after successful transaction
    cursor = conn.cursor()
    print("\n--- State after successful transaction ---")
    for row in cursor.execute("SELECT id, balance FROM accounts"):
        print(f"  Account {row[0]}: {row[1]}")

    # 2. Failure scenario
    # (Current balances: A: 900, B: 600)
    atomic_transfer(conn, 'A', 'B', 200, simulate_error=True)

    # Print balances after failed transaction
    print("\n--- State after failed transaction ---")
    for row in cursor.execute("SELECT id, balance FROM accounts"):
        print(f"  Account {row[0]}: {row[1]}")

    conn.close()

if __name__ == "__main__":
    main()
