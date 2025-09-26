# Database Transactions: ACID Properties


## Atomicity

- Transactions are **all or nothing**, preventing partial updates during errors or power failures
- *Example*: Money transfer between 2 accounts
- **Practical Example**: See `atomicity_example.py`

## Consistency

- **Valid state** to **valid state**, ensuring constraints are not violated after transaction
- *Example*: After money transfer, account balance cannot be negative
- **Practical Example**: See `consistency_example.py`
    

## Isolation

- Ensures concurrent transactions don't interfere with each other
- Prevents dirty reads (reading uncommitted data from another transaction)
- **Practical Example**: See `isolation_example.py`

## Durability

- When a transaction is committed, all changes are permanently saved even if system crashes
- *Example*: Successful order placement survives system crash and restart
- **Practical Example**: See `durability_example.py`

# Isolation Levels

## Concurrency Problems

Isolation levels are designed to prevent three main problems:

- **Dirty Read**: A transaction reads data that has been modified by another transaction but has **not yet been committed**.
- **Non-Repeatable Read**: A transaction reads the same row twice but gets different data each time because another transaction **modified or deleted** that row and committed the change in between the reads.
- **Phantom Read**: A transaction runs the same query twice but gets a different set of rows each time because another transaction **inserted** new rows that satisfy the query's `WHERE` clause and committed the change.

## The Four Standard Isolation Levels

| Isolation Level | Dirty Read | Non-Repeatable Read | Phantom Read |
| --- | --- | --- | --- |
| **Read Uncommitted** | Allowed | Allowed | Allowed |
| **Read Committed** | Prevented | Allowed | Allowed |
| **Repeatable Read** | Prevented | Prevented | Allowed |
| **Serializable** | Prevented | Prevented | Prevented |

## When to Use High Isolation Levels?

**Use higher isolation levels when:**
- Financial transactions (banking, payments)
- Inventory management with strict stock control
- Audit trails and compliance requirements
- Critical business logic that cannot tolerate inconsistencies

**Trade-offs:**
- Higher isolation = Better consistency but lower performance
- Lower isolation = Better performance but potential data inconsistencies
- Choose based on your application's consistency vs performance requirements
