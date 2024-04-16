import sqlite3 as sql

conn = sql.connect('test.db')
# print('数据亏打开成功')
c = conn.cursor()
# c.execute('''CREATE TABLE COMPANY
#             (ID INT PRIMARY KEY NOT NULL,
#             NAME    TEXT    NOT NULL,
#             AGE     INT     NOT NULL,
#             ADDRESS     CHAR(50),
#             SALARY      REAL);''')
# print('数据表创建成功')
# c.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
#           VALUES (2, 'Allen', 25, 'Texas', 15000.00)")
# c.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
#           VALUES (3, 'Teddy', 23, 'Norway', 20000.00)")
# c.execute("INSERT INTO COMPANY (ID,NAME,AGE,ADDRESS,SALARY) \
#           VALUES (4, 'Mark', 25, 'Rich-Mond', 65000.00)")
# c.execute("UPDATE COMPANY set SALARY = 25000.00 where ID = 1")
# c.execute("DELETE from COMPANY where ID = 2")
conn.commit()
# print("Total number of rows updated: " + str(conn.total_changes))
c.execute("SELECT * FROM COMPANY")
rows = c.fetchall()
for row in rows:
    print(row)
conn.close()
