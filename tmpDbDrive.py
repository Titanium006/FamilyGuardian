# 用来给数据库写入文件作测试用的驱动程序
import sqlite3 as sql
import random

# random.seed(42)

conn = sql.connect('myDB.db')
c = conn.cursor()
# i = 31
# for j in range(5, 11):
#     for t in range(1, 31):
#         c.execute("INSERT INTO alarmRecord (id, startTime, endTime, alarmType, camNo) \
#                   VALUES ({}, '2024-{}-{} 09:{}:00', '2024-{}-{} 12:{}:00', {}, 0)".format(i, j, t, random.randint(10, 59),
#                                                                                          j, t + 1,
#                                                                                          random.randint(10, 59),
#                                                                                          random.randint(0, 2)))
#         i += 1
# conn.commit()
# c.execute("SELECT * FROM alarmRecord")
# rows = c.fetchall()
# for row in rows:
#     print(row)

# c.execute("SELECT COUNT(*) FROM alarmRecord")
# row_count = c.fetchone()[0]
# print("Table row count:", row_count)

# c.execute("SELECT startTime, endTime, alarmType, camNo FROM alarmRecord ORDER BY id DESC LIMIT 10;")

# c.execute("SELECT * FROM alarmRecord ORDER BY id DESC LIMIT 15 OFFSET 220")   # 这里OFFSET超出表格数据限制只是会读不到数据而已, 不会报错!
c.execute("SELECT * FROM alarmRecord ORDER BY id DESC LIMIT 15 OFFSET 100")     # 注意这里的OFFSET 后面的数字是从倒序最后一位开始数的第几个"开始"(数组下标)
c.execute("SELECT * FROM alarmRecord ORDER BY id DESC LIMIT ? OFFSET ?", (15, 0))
results = c.fetchall()         # 查询结果返回的是元组的列表
processed_results = []
for i, row in enumerate(results, 1):
    processed_results.append((i,) + row)  # 在每行的前面添加序号

for row in processed_results:
    print(row)

conn.close()
