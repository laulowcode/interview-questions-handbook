#!/usr/bin/env python3
"""
ACID - Durability Example
Demonstrates data persistence after a system crash
"""

import sqlite3
import os
import random
import tempfile

def main():
    """Main execution scenario"""
    # Create a temporary database file
    db_fd, db_file = tempfile.mkstemp(suffix='_order_system.db')
    os.close(db_fd)  # Close file descriptor, only need the filename

    try:
        # --- 1. Set up initial database ---
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        # Create products and orders tables
        cursor.execute("CREATE TABLE products (id TEXT PRIMARY KEY, name TEXT, stock_quantity INT)")
        cursor.execute("CREATE TABLE orders (order_id INT PRIMARY KEY, product_id TEXT, quantity_ordered INT)")
        # Add a product with stock quantity 50
        cursor.execute("INSERT INTO products VALUES ('LP123', 'Laptop Pro', 50)")
        conn.commit()
        print(f"Initial inventory: 'Laptop Pro', stock: 50")
        conn.close()

        # --- 2. Place an order and COMMIT ---
        print("\n--- A customer orders 1 'Laptop Pro' ---")
        new_order_id = random.randint(1000, 9999)

        try:
            conn_order = sqlite3.connect(db_file)
            cursor_order = conn_order.cursor()

            # Step a: Decrease product stock
            cursor_order.execute("UPDATE products SET stock_quantity = stock_quantity - 1 WHERE id = 'LP123'")

            # Step b: Create a new order
            cursor_order.execute("INSERT INTO orders VALUES (?, 'LP123', 1)", (new_order_id,))

            # Step c: COMMIT! This is where Durability comes into play
            # Data is permanently written to the database file
            conn_order.commit()

            print(f"=> Order placed successfully! Order ID: {new_order_id}. Data has been COMMITTED.")

        finally:
            conn_order.close()

        # --- 3. SIMULATE A CRASH ---
        print("\n... (Suppose the server loses power immediately and restarts) ...\n")

        # --- 4. Check data after "system recovery" ---
        print("--- System recovers, reconnecting to the database to check ---")
        try:
            conn_after_crash = sqlite3.connect(db_file)
            cursor_after_crash = conn_after_crash.cursor()

            # Check remaining stock
            cursor_after_crash.execute("SELECT stock_quantity FROM products WHERE id = 'LP123'")
            stock = cursor_after_crash.fetchone()[0]
            print(f"Check inventory: 'Laptop Pro', remaining stock: {stock}")

            # Check if the order still exists
            cursor_after_crash.execute("SELECT product_id FROM orders WHERE order_id = ?", (new_order_id,))
            order_exists = cursor_after_crash.fetchone()

            if order_exists:
                print(f"Check order: Order {new_order_id} STILL EXISTS in the system.")
            else:
                print(f"Check order: Order {new_order_id} is missing! (Durability failure)")

        finally:
            conn_after_crash.close()

    finally:
        # Clean up temporary file
        if os.path.exists(db_file):
            os.remove(db_file)

if __name__ == "__main__":
    main()
