import sys

import mysql.connector
from werkzeug.security import generate_password_hash

mydb = mysql.connector.connect(
    host="localhost",
    user=sys.argv[2],
    passwd=str(sys.argv[3]),
    database=sys.argv[1]
)

mycursor = mydb.cursor()

hashed_password = generate_password_hash(sys.argv[5], method='sha256')

sql = "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)"
val = (sys.argv[4], hashed_password, 'admin')
mycursor.execute(sql, val)

mydb.commit()

print(mycursor.rowcount, "User created successfully!")
