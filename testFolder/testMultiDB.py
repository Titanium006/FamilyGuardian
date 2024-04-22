import sqlite3
import threading

# 在每个线程中创建独立的数据库连接
def connect_to_database():
    return sqlite3.connect("example.db")

# 在每个线程中执行数据库查询
def query_database(connection, thread_name):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM table_name")
    rows = cursor.fetchall()
    print(f"Thread {thread_name}: {rows}")
    connection.close()

# 主函数
def main():
    # 创建线程
    threads = []
    for i in range(5):
        thread_name = f"Thread-{i+1}"
        thread = threading.Thread(target=thread_function, args=(thread_name,))
        threads.append(thread)
        thread.start()

    # 等待所有线程结束
    for thread in threads:
        thread.join()

# 线程函数
def thread_function(thread_name):
    connection = connect_to_database()
    query_database(connection, thread_name)

if __name__ == "__main__":
    main()
