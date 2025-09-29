
## When to Create an Index

You create an index to avoid slow, full-table scans. An index acts like the index at the back of a book, allowing the database to quickly locate specific rows instead of reading the entire table. The trade-off is that indexes consume storage space and slightly slow down write operations (`INSERT`, `UPDATE`, `DELETE`) because the index must also be updated.

**Create an index on columns that are:**

  * **Frequently used in `WHERE` clauses:** This is the most common reason. If you often filter by `user_id` or `email`, those columns are prime candidates.
      * `SELECT * FROM orders WHERE customer_id = 123;` ➡️ Index `customer_id`.
  * **Used in `JOIN` conditions:** Indexing foreign key columns (and the primary keys they reference) is crucial for performance. Most database systems do this automatically for primary and unique keys, but you should always index your foreign key columns.
      * `SELECT * FROM users u JOIN posts p ON u.id = p.user_id;` ➡️ Index `p.user_id`.
  * **Used in `ORDER BY` or `GROUP BY` clauses:** An index can store data in a pre-sorted order, making sorting operations nearly instantaneous.
      * `SELECT * FROM products ORDER BY price DESC;` ➡️ Index `price`.

**When *NOT* to create an index:**

  * **On small tables:** The database can scan the whole table faster than using an index.
  * **On columns with low cardinality** (very few unique values), like a `gender` column. The index won't be selective enough to help.
  * **On tables with heavy write and low read activity:** The overhead of updating the index on every write will hurt performance more than the reads will benefit.

-----

## Choosing the Right Index Type

### B-Tree (Balanced Tree)

This is the **default and most common** index type. If you're unsure which to use, start with a B-Tree.

  * **How it works:** It keeps data sorted and allows for efficient searching, insertions, and deletions. Think of it like a dictionary or a phone book.
  * **Best for:** A wide variety of queries. It excels at handling comparison operators.
  * **Use when your queries involve:**
      * Equality: `=`
      * Ranges: `<`, `<=`, `>`, `>=`
      * `BETWEEN`, `IN`, `IS NULL`, `IS NOT NULL`
      * Pattern matching with `LIKE 'prefix%'` (but not `LIKE '%suffix'`)
  * **Example:** To speed up lookups and sorting by username.
    ```sql
    CREATE INDEX idx_users_username ON users (username);
    ```

### Hash

A Hash index is specialized for one thing only: simple equality checks.

  * **How it works:** It creates a hash value (a unique fingerprint) for each row's indexed column value, which allows for incredibly fast direct lookups.
  * **Best for:** Only equality comparisons. It's often faster than B-Tree for this specific task but less flexible.
  * **Use when your queries involve:**
      * Only the equality operator: `=`
  * **Example:** If you are only ever looking up users by their exact email address.
    ```sql
    CREATE INDEX idx_users_email_hash ON users USING HASH (email);
    ```

### Full-Text Search (FTS)

This isn't a standalone index type but rather a feature that uses specialized index types (like GIN or GiST) to search for natural language within large text documents.

  * **How it works:** It parses text into lexemes (words), stems them (e.g., "running" becomes "run"), and discards common "stop words" ('a', 'the', etc.). It then builds an index to quickly find documents containing specific words or phrases.
  * **Best for:** Searching for words inside `TEXT` or `VARCHAR` columns.
  * **Use when your queries involve:** Finding articles, products, or documents based on their content.
  * **Example:** To create a searchable index on an `articles` table's content.
    ```sql
    -- Note: FTS is implemented using another index type, typically GIN.
    CREATE INDEX idx_articles_content_fts ON articles USING GIN (to_tsvector('english', content));

    -- You would query it like this:
    SELECT title FROM articles WHERE to_tsvector('english', content) @@ to_tsquery('english', 'database & performance');
    ```

### GIN (Generalized Inverted Index)

GIN is designed for indexing **composite values**, where a single column entry can contain multiple items (e.g., an array of tags, a JSON document).

  * **How it works:** It creates an index entry for each individual item within the composite value, pointing back to the rows that contain it. Think of the index in a book: the term "Photosynthesis" might list pages 5, 12, and 45.
  * **Best for:**
      * Arrays (`integer[]`, `text[]`, etc.)
      * `jsonb` documents (finding rows where a JSON key exists or has a certain value)
      * Full-Text Search (it's often the preferred type for FTS)
  * **Use when your queries involve:** Checking for containment or existence within a composite type. Operators include `@>` (contains), `<@` (is contained by), `?` (exists).
  * **Example:** Find all products that have the 'electronics' tag in a `text[]` tags column.
    ```sql
    CREATE INDEX idx_products_tags_gin ON products USING GIN (tags);

    -- This query becomes very fast:
    SELECT product_name FROM products WHERE tags @> ARRAY['electronics'];
    ```

-----

## Quick Summary Table

| Index Type | Best For                                                       | Common Operators                                 | Analogy                                   |
| :----------- | :------------------------------------------------------------- | :----------------------------------------------- | :---------------------------------------- |
| **B-Tree** | General purpose, sorting, range queries, equality              | `=`, `>`, `<`, `>=`, `<=`, `BETWEEN`, `LIKE 'prefix%'` | A dictionary or phone book (sorted)       |
| **Hash** | Simple equality checks only                                    | `=`                                              | A computer hash map (key-value lookup)    |
| **GIN** | Composite types: arrays, `jsonb`, full-text search          | `@>`, `<@`, `?`, `@@` (for FTS)                  | Index at the back of a book (word → pages) |