import sqlite3

#  from app import db

conn = sqlite3.connect('crm.db.naosei.bckup')
# db.create_all()

conn.execute('''
CREATE TABLE properties (
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT NOT NULL,
address TEXT NOT NULL,
city TEXT NOT NULL,
state TEXT NOT NULL,
value INTEGER NOT NULL,
property_type TEXT NOT NULL,
price INTEGER NOT NULL,
bedrooms INTEGER NOT NULL,
bathrooms INTEGER NOT NULL,
area INTEGER NOT NULL,
garage TEXT NOT NULL,
description TEXT NOT NULL,
photo TEXT NOT NULL,
client_id INTEGER NOT NULL,
FOREIGN KEY (client_id) REFERENCES client (id)
)
''')
conn.commit()

conn.close()
