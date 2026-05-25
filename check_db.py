import sqlite3
from pathlib import Path

DB_NAME = "movieflix_users.db"

if not Path(DB_NAME).exists():
    print("Database file nahi mili. Pehle app run karo aur signup karo.")
    exit()

conn = sqlite3.connect(DB_NAME)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("\nAvailable Tables:")
tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()

for table in tables:
    print("-", table["name"])

print("\nRegistered Users:")
try:
    users = cur.execute("""
        SELECT id, username, email, created_at, updated_at
        FROM users
        ORDER BY id DESC
    """).fetchall()

    if not users:
        print("Abhi koi user database me add nahi hua.")
    else:
        for user in users:
            print(
                f"ID: {user['id']} | "
                f"Username: {user['username']} | "
                f"Email: {user['email']} | "
                f"Created: {user['created_at']}"
            )

except Exception as e:
    print("Users table read nahi hui:", e)

conn.close()