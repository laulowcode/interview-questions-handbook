# How do you implement pagination for APIs when dealing with very large datasets (hundreds of millions of records)?

For very large datasets, use **keyset pagination** (also known as cursor-based or seek-based pagination). It's highly performant because it avoids the slow database table scans that plague traditional offset-based pagination (`LIMIT`/`OFFSET`).

Keyset pagination works by using a "cursor"—a unique, sequential value from the last item of the previous page—to fetch the next set of results. This allows the database to use an index to jump directly to the starting point of the next page.

---

## Keyset (Cursor-Based) Pagination

The core principle is to filter records based on a unique, indexed, and sequentially ordered column (like an auto-incrementing `id` or a `created_at` timestamp).

Instead of asking for "page 5" (which requires the database to scan and skip pages 1-4), you ask for records "after" the last item you saw.

* **Query:** `SELECT * FROM records WHERE id > [last_seen_id] ORDER BY id ASC LIMIT [page_size]`
* **Requirement:** The column used for the cursor (**`id`** in this case)  **must be indexed** .
