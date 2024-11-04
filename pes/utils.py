#  utils.py

# For Database
# import pyodbc
# from django.db import connection
# from django.contrib.auth.hashers import make_password

# def  read_data_from_database():
#     with connection.cursor() as cursor:
#         cursor.execute("SELECT FSPID, password FROM FSPs")  # Select FSPID and password columns
#         rows = cursor.fetchall()  # Fetch all rows
     
#         for row in rows:
#             fspid, password = row  # Unpack the FSPID and password from the row
#             if password:
#                 hashed_password = make_password(password) 
#                 # print(password) # Hash password using PBKDF2
#                 #print(len(rows)) # Hash password using PBKDF2
#                 # Update the database with the hashed password based on FSPID
#                 #print(hashed_password, fspid)
#                 cursor.execute("UPDATE FSPs SET pwd = %s WHERE FSPID = %s", (hashed_password, fspid))
         
#         return len(rows)  # Return the number of ro updated

