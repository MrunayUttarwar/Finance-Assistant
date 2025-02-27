import sqlite3

conn = sqlite3.connect("users.db")
c = conn.cursor()

c.execute("SELECT * FROM users3")
users = c.fetchall()

if users:
    print("Stored Users:")
    for user in users:
        print(f"Username: {user[0]}, Password: {user[1]}")
else:
    print("No users found in the database.")

conn.close()