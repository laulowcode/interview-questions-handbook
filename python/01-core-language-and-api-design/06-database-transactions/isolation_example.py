#!/usr/bin/env python3
"""
ACID - Isolation Example
Demonstrates concurrent transaction isolation
"""

import sqlite3
import os
import tempfile

def main():
    """Main execution scenario"""
    # --- Setup the database ---
    # Use a temporary file so two connections can access the same database
    db_fd, db_file = tempfile.mkstemp(suffix='.db')
    os.close(db_fd)  # Close the file descriptor, we only need the filename
    
    try:
        conn_setup = sqlite3.connect(db_file)
        cursor = conn_setup.cursor()
        cursor.execute("DROP TABLE IF EXISTS accounts")
        cursor.execute("CREATE TABLE accounts (id TEXT PRIMARY KEY, balance REAL)")
        cursor.execute("INSERT INTO accounts (id, balance) VALUES ('A', 1000)")
        conn_setup.commit()
        conn_setup.close()

        # --- Simulate two concurrent transactions ---

        # Open two separate connections, representing two users/processes
        conn1 = sqlite3.connect(db_file, isolation_level='SERIALIZABLE') # TX1
        conn2 = sqlite3.connect(db_file) # TX2

        try:
            cursor1 = conn1.cursor()
            cursor2 = conn2.cursor()

            # Step 1 (TX1): Start transaction and read the initial balance
            # conn1.isolation_level = 'SERIALIZABLE' will start a transaction on SELECT
            cursor1.execute("SELECT balance FROM accounts WHERE id = 'A'")
            balance1_before = cursor1.fetchone()[0]
            print(f"[TX1] First read: Account A balance is {balance1_before}")

            # Step 2 (TX2): Start another transaction and UPDATE the balance, but DO NOT COMMIT yet
            print("\n[TX2] Starting update...")
            cursor2.execute("UPDATE accounts SET balance = balance + 500 WHERE id = 'A'")
            print("[TX2] Updated balance, but NOT COMMITTED yet.")

            # Step 3 (TX1): Read the balance again from transaction 1
            # Due to isolation, TX1 should not see TX2's uncommitted change
            print("\n[TX1] Second read (while TX2 has not committed)...")
            cursor1.execute("SELECT balance FROM accounts WHERE id = 'A'")
            balance1_after = cursor1.fetchone()[0]
            print(f"[TX1] Second read result: Balance is still {balance1_after}")

            # Step 4 (TX2): Now commit transaction 2
            conn2.commit()
            print("\n[TX2] Commit complete.")

            # Step 5 (TX1): Read the balance again after TX2 has committed
            # TX1's transaction is still running and operates on a "snapshot"
            # of the data as of when it started.
            cursor1.execute("SELECT balance FROM accounts WHERE id = 'A'")
            balance1_final = cursor1.fetchone()[0]
            print(f"[TX1] Third read (after TX2 commit): Balance is still {balance1_final} because TX1 is still in the old snapshot.")

            # End transaction 1
            conn1.commit()

            # Step 6: Start a new transaction to see the final state of the database
            cursor1.execute("SELECT balance FROM accounts WHERE id = 'A'")
            final_balance = cursor1.fetchone()[0]
            print(f"\n[New transaction] Final balance of account A is {final_balance}")

        finally:
            conn1.close()
            conn2.close()
    
    finally:
        # Clean up the temporary file
        if os.path.exists(db_file):
            os.remove(db_file)

if __name__ == "__main__":
    main()
