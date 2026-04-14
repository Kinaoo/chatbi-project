import sys
import os

# 获取项目根目录（当前文件所在目录的上一级）
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
from chatbi_core import ask_question

questions = [
    "上个月华东区销售额最高的三个子品类是什么？",
    "各个地区的总销售额是多少？",
    "2023年利润最高的五个订单是哪些？",
    "科技品类的平均利润和平均利润率是多少？"
]

for q in questions:
    print(f"\n问题: {q}")
    res = ask_question(q)
    print(f"SQL: {res['sql']}")
    if res['error']:
        print(f"❌ 错误: {res['error']}")
    else:
        print(f"✅ 返回 {len(res['data'])} 行")
        if not res['data'].empty:
            print(res['data'].head())
