import pandas as pd
import sqlite3

#1.读取csv
df = pd.read_csv('superstore.csv')

# 2. 查看原始列名（调试用）
print("原始列名:", df.columns.tolist())

# 3. 统一列名：转小写，空格替换为下划线
df.columns = [col.lower().replace(' ', '_') for col in df.columns]

#4.将订单日期转换为日期类型（如果存在）
if 'order_date' in df.columns:df['order_date'] = pd.to_datetime(df['order_date'])
#如果有ship_date 也转换
if 'ship_date' in df.columns:df['ship_date'] = pd.to_datetime(df['ship_date'])

# 5. 检查缺失值
print("缺失值统计:\n", df.isnull().sum())

# 6. 连接 SQLite 数据库（如果文件不存在会自动创建）
conn = sqlite3.connect('superstore.db')

# 7. 将数据写入表 orders（如果表已存在则替换）
df.to_sql('orders', conn, if_exists='replace', index=False)
print(f"成功写入 {len(df)} 条记录到 orders 表")

# 8. 关闭连接
conn.close()

