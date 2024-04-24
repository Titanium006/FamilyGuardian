import sqlite3 as sql
conn = sql.connect("D:\大三下\软工课设\HomeSurface\myDB.db")
c = conn.cursor()
c.execute('SELECT userID FROM userInfo')
rows = c.fetchall()
print(rows)
for row in rows:
    print(row)
c.close()
conn.close()
