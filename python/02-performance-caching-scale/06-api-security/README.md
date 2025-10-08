Cross-Site Request Forgery (CSRF), Cross-Site Scripting (XSS), and SQL Injection are common web application vulnerabilities.

* **Cross-Site Request Forgery (CSRF)** forgery is an attack that tricks a user into submitting a malicious request. It leverages the trust a site has in a user's browser, essentially making the user's browser perform an unwanted action on a site where the user is already authenticated (like changing their email or password). 🎭
* **Cross-Site Scripting (XSS)** is an injection attack where an attacker embeds malicious code (usually JavaScript) into a trusted website. When a victim visits the page, the malicious script runs in their browser, allowing the attacker to steal session cookies, deface the site, or redirect the user. 📜
* **SQL Injection (SQLi)** is an attack where malicious SQL code is inserted into an application's input fields, which is then executed by the database. A successful attack can allow an attacker to bypass authentication, view, modify, or delete data. データベース

---

## How to Prevent SQL Injection in Python 🛡️

The **most effective way** to prevent SQL Injection in Python is to **never** build SQL queries using string formatting or concatenation with user-supplied data. Instead, always use **parameterized queries** (also known as prepared statements).

This method separates the SQL query's logic from the data. The database driver is instructed to treat the user-supplied values strictly as data, not as executable code, which completely neutralizes the injection attempt.

### The Wrong Way: String Formatting ❌

Never do this. This example uses an f-string to insert user input directly into the query, which makes it vulnerable.

**Python**

```
# DANGEROUS - DO NOT USE IN PRODUCTION
import sqlite3

# Connect to a database (it will be created if it doesn't exist)
conn = sqlite3.connect('example.db')
cursor = conn.cursor()

# Get some unsafe user input
user_id = "1 OR 1=1" 

# Vulnerable query using string formatting
query = f"SELECT * FROM users WHERE id = {user_id}" 
# The final query becomes: SELECT * FROM users WHERE id = 1 OR 1=1
# This would return ALL users, bypassing the intended logic.

try:
    cursor.execute(query)
    print("Vulnerable query executed.")
except sqlite3.Error as e:
    print(f"An error occurred: {e}")

conn.close()
```

### The Right Way: Parameterized Queries ✅

This is the secure method. Notice how a `?` placeholder is used in the query string, and the actual value is passed as a separate tuple to the `cursor.execute()` method. The database driver safely handles the value.

Different database drivers use different placeholder styles (`?` for `sqlite3`, `%s` for `psycopg2` and `mysql-connector`), but the principle is identical.

#### Example: `sqlite3` (Standard Library)

The `sqlite3` module uses a question mark (`?`) as the placeholder.

**Python**

```
# SAFE - Using parameterized queries
import sqlite3

conn = sqlite3.connect('example.db')
cursor = conn.cursor()

# Assume 'users' table exists with 'id' and 'name' columns

# Get some potentially malicious user input
user_id_input = "1; DROP TABLE users" 

# Secure query using a placeholder
query = "SELECT * FROM users WHERE id = ?"

# The driver safely substitutes the placeholder with the user input.
# The malicious "DROP TABLE" part is treated as part of the string value, not as a SQL command.
cursor.execute(query, (user_id_input,)) # Note: The second argument must be a tuple!

results = cursor.fetchall()
print(f"Found: {results}")

conn.close()
```

#### Example: Using an ORM (SQLAlchemy)

Object-Relational Mappers (ORMs) like SQLAlchemy are highly recommended as they handle parameterization automatically, adding a strong layer of security by design.

**Python**

```
# SAFE - SQLAlchemy handles parameterization automatically
from sqlalchemy import create_engine, text

engine = create_engine('sqlite:///example.db')

# Malicious input
user_id_input = "1 OR 1=1"

# Using a named parameter with the text() construct
query = text("SELECT * FROM users WHERE id = :user_id")

with engine.connect() as connection:
    # The value is passed safely in the execute method
    result = connection.execute(query, {"user_id": user_id_input})
    for row in result:
        print(row)
```

By using parameterized queries, you effectively prevent attackers from manipulating your SQL logic through user input.
