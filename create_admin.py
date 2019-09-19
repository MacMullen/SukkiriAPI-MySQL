from getpass import getpass
from uuid import uuid4

import mysql.connector
from werkzeug.security import generate_password_hash

mydb = mysql.connector.connect(
    host=input('DB host: '),
    user=input('DB user: '),
    passwd=input('DB password: '),
    database=input('DB name: ')
)

mycursor = mydb.cursor()

hashed_password = generate_password_hash(input('admin password: '), method='sha256')

sql = "INSERT INTO users (username, password_hash, role, email, first_name, last_name, public_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
val = (input('admin username: '), hashed_password, 'admin', input('admin email: '), input('admin first name: '),
       input('admin last name: '), str(uuid4()))
mycursor.execute(sql, val)

mydb.commit()

print("User created successfully!")
