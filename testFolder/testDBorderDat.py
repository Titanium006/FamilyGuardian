import sqlite3

# 连接到 SQLite 数据库
conn = sqlite3.connect('example.db')
cursor = conn.cursor()

# 创建一个带有自增长主键的表
cursor.execute('''CREATE TABLE IF NOT EXISTS data
                (id INTEGER PRIMARY KEY AUTOINCREMENT,
                value TEXT)''')

# 检查数据行数是否超过上限，并删除旧数据
def check_and_reset_primary_key():
    # 获取当前数据行数
    cursor.execute("SELECT COUNT(*) FROM data")
    row_count = cursor.fetchone()[0]

    # 设置数据上限
    max_rows = 5  # 这里设置为5，你可以根据需求修改

    # 如果数据行数超过上限，删除旧数据，重新开始从1开始插入新数据
    if row_count >= max_rows:
        cursor.execute("DELETE FROM data WHERE id = (SELECT MIN(id) FROM data)")

# 插入数据
for i in range(1, 10):
    check_and_reset_primary_key()  # 检查并重置主键
    cursor.execute("INSERT INTO data (value) VALUES (?)", ('Data {}'.format(i),))

# 提交事务
conn.commit()

# 读取数据
cursor.execute("SELECT * FROM data ORDER BY id")
rows = cursor.fetchall()
for row in rows:
    print(row)

# 关闭连接
conn.close()
