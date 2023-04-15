!pip install mysql-connector-python
import mysql.connector
import streamlit as st

def connect_to_database():
    
    mydb = mysql.connector.connect(
    host = "db4free.net",
    user = "monasr",
    password = "monasr1658",
    database = "olxxdatabase",
    )
    
    return mydb

# print(mydb)
# mycursor = mydb.cursor()
# sql = """
# select * from user;
# """
# mycursor.execute(sql)

# result = mycursor.fetchall()
# for r in result:
#     print(r)

mydb = connect_to_database()

st.write ('''
# Welcome to OLX Database
''')

