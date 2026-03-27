import os
import sqlite3
from dotenv import load_dotenv
from openai import OpenAI

# 加载环境变量
load_dotenv()

# 初始化客户端（使用智谱 GLM-4-Flash）
client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)

# 读取表结构描述
with open('schema_info.txt', 'r', encoding='utf-8') as f:
    schema = f.read()

# 读取 Prompt 模板
with open('prompt_template.txt', 'r', encoding='utf-8') as f:
    prompt_template = f.read()

system_prompt = prompt_template.format(schema=schema)

# 测试问题列表
test_questions = [
    "上个月华东区销售额最高的三个子品类是什么？",
    "各个地区的总销售额是多少？",
    "2023年利润最高的五个订单是哪些？",
    "科技品类的平均利润和平均利润率是多少？"
]

def validate_sql(sql):
    """
    执行 SQL 并返回 (success, message, data_preview)
    success: 布尔值，表示执行是否成功（语法正确且无运行时错误）
    message: 描述信息
    data_preview: 如果成功且有数据，返回前5行；否则为 None
    """
    try:
        conn = sqlite3.connect('superstore.db')
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        conn.close()
        if rows:
            return True, f"执行成功，返回 {len(rows)} 行", rows[:5]
        else:
            return True, "执行成功，但返回空结果", None
    except Exception as e:
        return False, f"执行失败: {e}", None

for question in test_questions:
    print(f"\n问题: {question}")
    try:
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            temperature=0
        )
        raw = response.choices[0].message.content.strip()
        # 移除可能的 Markdown 代码块标记
        if raw.startswith("```sql") and raw.endswith("```"):
            sql = raw[6:-3].strip()
        elif raw.startswith("```") and raw.endswith("```"):
            sql = raw[3:-3].strip()
        else:
            sql = raw
        print("生成的SQL:")
        print(sql)

        # 执行并验证
        success, msg, data = validate_sql(sql)
        if success:
            print(f"✅ {msg}")
            if data:
                print("前5行数据预览:")
                for row in data:
                    print(row)
        else:
            print(f"❌ {msg}")

    except Exception as e:
        print(f"调用API失败: {e}")
