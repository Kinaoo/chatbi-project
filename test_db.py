import sqlite3

conn = sqlite3.connect('superstore.db')
cur = conn.cursor()

# 检查总行数
cur.execute("SELECT COUNT(*) FROM orders")
count = cur.fetchone()[0]
print(f"总记录数: {count}")

# 查看表结构（列名）
cur.execute("PRAGMA table_info(orders)")
columns = cur.fetchall()
print("\n表结构:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

# 查看前5行数据
print("\n前5行数据:")
cur.execute("SELECT * FROM orders LIMIT 5")
for row in cur.fetchall():
    print(row)

conn.close()
