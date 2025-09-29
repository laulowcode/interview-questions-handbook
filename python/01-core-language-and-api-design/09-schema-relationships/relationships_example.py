#!/usr/bin/env python3
"""
Database Relationships Example with SQLite
Demonstrates 1:1, 1:N, and M:N relationships
"""

import sqlite3

def create_schema(conn):
    """Create tables for all relationship types"""
    cursor = conn.cursor()
    
    # Users table (base for all relationships)
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE
        )
    """)
    
    # 1:1 Relationship - User to Profile
    cursor.execute("""
        CREATE TABLE profiles (
            id INTEGER PRIMARY KEY,
            user_id INTEGER UNIQUE,
            bio TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # 1:N Relationship - User to Posts
    cursor.execute("""
        CREATE TABLE posts (
            id INTEGER PRIMARY KEY,
            user_id INTEGER,
            title TEXT,
            content TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # M:N Relationship - Users to Roles
    cursor.execute("""
        CREATE TABLE roles (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE user_roles (
            user_id INTEGER,
            role_id INTEGER,
            PRIMARY KEY (user_id, role_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (role_id) REFERENCES roles(id)
        )
    """)
    
    conn.commit()

def insert_sample_data(conn):
    """Insert sample data to demonstrate relationships"""
    cursor = conn.cursor()
    
    # Insert users
    users = [('alice',), ('bob',), ('charlie',)]
    cursor.executemany("INSERT INTO users (username) VALUES (?)", users)
    
    # Insert profiles (1:1)
    profiles = [
        (1, 'Software engineer who loves Python'),
        (2, 'Designer with 5 years experience')
    ]
    cursor.executemany("INSERT INTO profiles (user_id, bio) VALUES (?, ?)", profiles)
    
    # Insert posts (1:N)
    posts = [
        (1, 'Python Tips', 'Here are some Python tips...'),
        (1, 'Database Design', 'Good database design is important...'),
        (2, 'UI/UX Principles', 'Design principles every developer should know...'),
        (3, 'Getting Started', 'My first post!')
    ]
    cursor.executemany("INSERT INTO posts (user_id, title, content) VALUES (?, ?, ?)", posts)
    
    # Insert roles
    roles = [('admin',), ('editor',), ('viewer',)]
    cursor.executemany("INSERT INTO roles (name) VALUES (?)", roles)
    
    # Insert user-role relationships (M:N)
    user_roles = [
        (1, 1),  # alice is admin
        (1, 2),  # alice is also editor
        (2, 2),  # bob is editor
        (3, 3)   # charlie is viewer
    ]
    cursor.executemany("INSERT INTO user_roles (user_id, role_id) VALUES (?, ?)", user_roles)
    
    conn.commit()

def demonstrate_queries(conn):
    """Show different types of queries for each relationship"""
    cursor = conn.cursor()
    
    print("=== 1:1 Relationship Query ===")
    print("Users with their profiles:")
    cursor.execute("""
        SELECT u.username, p.bio
        FROM users u
        LEFT JOIN profiles p ON u.id = p.user_id
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1] or 'No profile'}")
    
    print("\n=== 1:N Relationship Query ===")
    print("Users and their post counts:")
    cursor.execute("""
        SELECT u.username, COUNT(p.id) as post_count
        FROM users u
        LEFT JOIN posts p ON u.id = p.user_id
        GROUP BY u.id, u.username
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]} posts")
    
    print("\n=== M:N Relationship Query ===")
    print("Users and their roles:")
    cursor.execute("""
        SELECT u.username, GROUP_CONCAT(r.name) as roles
        FROM users u
        LEFT JOIN user_roles ur ON u.id = ur.user_id
        LEFT JOIN roles r ON ur.role_id = r.id
        GROUP BY u.id, u.username
    """)
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1] or 'No roles'}")

def main():
    """Main execution"""
    conn = sqlite3.connect(':memory:')
    
    print("🏗️  Creating schema...")
    create_schema(conn)
    
    print("📊 Inserting sample data...")
    insert_sample_data(conn)
    
    print("\n🔍 Running relationship queries:")
    demonstrate_queries(conn)
    
    conn.close()
    print("\n✅ Database relationships demonstration complete!")

if __name__ == "__main__":
    main()
