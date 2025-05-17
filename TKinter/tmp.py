import sqlite3

conn = sqlite3.connect('config1.db')
cursor = conn.cursor()

# Execute query to get one row
cursor.execute("SELECT * FROM params WHERE id = 1")
row = cursor.fetchone()

if row:
    columns = [description[0] for description in cursor.description]
    result = dict(zip(columns, row))
    print(result)
else:
    print("No data found.")


# print(bool(row[0]))
# print(model_path)
# print(type(model_path))