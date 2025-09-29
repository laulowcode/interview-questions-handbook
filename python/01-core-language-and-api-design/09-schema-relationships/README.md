# Database Relationships: OneToOne vs OneToMany vs ManyToMany

## OneToOne (1:1)

**Use Case**: Each record in Table A relates to exactly one record in Table B
**Example**: User ↔ Profile

**Pros**: Simple, enforces uniqueness
**Cons**: Could be merged into single table, adds JOIN overhead

```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE
);

-- Profiles table (1:1 with users)
CREATE TABLE profiles (
    id INTEGER PRIMARY KEY,
    user_id INTEGER UNIQUE,  -- UNIQUE enforces 1:1
    bio TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## OneToMany (1:N)

**Use Case**: One record in Table A relates to multiple records in Table B
**Example**: User → Posts (one user has many posts)

**Pros**: Most common relationship, efficient queries
**Cons**: Can't represent reverse many-to-one easily

```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT
);

-- Posts table (N:1 with users)
CREATE TABLE posts (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,  -- Foreign key to users
    title TEXT,
    content TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## ManyToMany (M:N)

**Use Case**: Records in Table A can relate to multiple records in Table B, and vice versa
**Example**: Users ↔ Roles (users can have multiple roles, roles can have multiple users)

**Pros**: Maximum flexibility, models complex relationships
**Cons**: Requires junction table, more complex queries

```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT
);

-- Roles table
CREATE TABLE roles (
    id INTEGER PRIMARY KEY,
    name TEXT
);

-- Junction table for M:N relationship
CREATE TABLE user_roles (
    user_id INTEGER,
    role_id INTEGER,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (role_id) REFERENCES roles(id)
);
```

## Decision Guide

| Relationship | When to Use | Example |
|--------------|-------------|----------|
| **1:1** | Separate concerns, optional data | User ↔ Profile |
| **1:N** | Hierarchical data, ownership | User → Posts |
| **M:N** | Complex associations | Users ↔ Roles |

## Performance Considerations

- **1:1**: Consider merging tables if always queried together
- **1:N**: Index the foreign key column for fast lookups
- **M:N**: Index both columns in junction table, consider denormalization for read-heavy workloads
