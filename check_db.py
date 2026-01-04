import sqlite3

conn = sqlite3.connect('tourism.db')
cursor = conn.cursor()

# Get all tables
tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
print('Tables:', [t[0] for t in tables])

# Get tourism_data schema
print('\ntourism_data schema:')
cursor.execute('PRAGMA table_info(tourism_data)')
for row in cursor.fetchall():
    print(row)

# Get uploaded_files schema
print('\nuploaded_files schema:')
cursor.execute('PRAGMA table_info(uploaded_files)')
for row in cursor.fetchall():
    print(row)

conn.close()
