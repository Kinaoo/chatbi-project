import sys
import os

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from chatbi_core import ask_question

# 测试问题列表
test_cases = [
    ("各个地区的总销售额是多少？画柱状图", True),   # 应生成柱状图
    ("2023年各月销售额趋势，画折线图", True),       # 应生成折线图（需确保查询返回日期列）
    ("科技品类的平均利润是多少？", True),           # 不包含图表关键词，应不生成图表
    ("利润最高的五个订单", False)                  # 即使不要求可视化，也不生成图表
]

for question, visualize in test_cases:
    print(f"\n问题: {question}")
    res = ask_question(question, visualize=visualize)
    if res['error']:
        print(f"❌ 错误: {res['error']}")
    else:
        print(f"✅ 返回 {len(res['data'])} 行数据")
        if res['chart_path']:
            print(f"📊 图表已保存: {res['chart_path']}")
        else:
            print("未生成图表")
