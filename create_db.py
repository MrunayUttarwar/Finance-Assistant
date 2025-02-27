import sqlite3

conn = sqlite3.connect("users.db")
c = conn.cursor()

# Create users table
c.execute('''CREATE TABLE IF NOT EXISTS users3 (username TEXT PRIMARY KEY, password TEXT)''')

conn.commit()
conn.close()

print("Database created successfully!")




def get_table_columns(table_name):
    conn = sqlite3.connect("users.db")  # Update with your database name
    cursor = conn.cursor()

    # Fetch column names
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    conn.close()
    
    # Extract column names from the query result
    return [col[1] for col in columns]

# Example usage
table_name = "users3"  # Change this to the table you want to check
columns = get_table_columns(table_name)
print(f"Columns in '{table_name}' table: {columns}")