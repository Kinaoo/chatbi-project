import os
import sqlite3
import logging
from dotenv import load_dotenv
from openai import OpenAI

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='chatbi.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

# 初始化客户端（使用智谱）
client = OpenAI(
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)

# 读取表结构和 Prompt 模板（在模块加载时读取一次）
with open('schema_info.txt', 'r', encoding='utf-8') as f:
    SCHEMA = f.read()

with open('prompt_template.txt', 'r', encoding='utf-8') as f:
    PROMPT_TEMPLATE = f.read()

SYSTEM_PROMPT = PROMPT_TEMPLATE.format(schema=SCHEMA)
CACHE = {}

def ask_question(question, visualize=False):
    """
    输入自然语言问题，返回查询结果字典。
    参数：
        question: 字符串，用户问题
        visualize: 布尔值，是否生成图表（Day 5 实现）
    返回：
        dict 包含以下字段：
            - sql: 生成的 SQL 语句
            - data: 查询结果的 DataFrame（或 None）
            - error: 错误信息（若无错误则为 None）
            - chart_path: 图表路径（预留）
    """
    result = {
        'sql': None,
        'data': None,
        'error': None,
        'chart_path': None
    }
    # 检查缓存
    if question in CACHE:
        logger.info(f"使用缓存结果: {question}")
        return CACHE[question]
    
    try:
        # 调用 LLM 生成 SQL
        logger.info(f"处理问题: {question}")
        response = client.chat.completions.create(
            model="glm-4-flash",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}
            ],
            temperature=0
        )
        raw = response.choices[0].message.content.strip()
        # 移除可能的 Markdown 代码块
        if raw.startswith("```sql") and raw.endswith("```"):
            sql = raw[6:-3].strip()
        elif raw.startswith("```") and raw.endswith("```"):
            sql = raw[3:-3].strip()
        else:
            sql = raw
        result['sql'] = sql
        logger.info(f"生成的SQL: {sql}")

        # 执行 SQL
        conn = sqlite3.connect('superstore.db')
        # 使用 pandas 读取结果，方便后续可视化
        import pandas as pd
        df = pd.read_sql_query(sql, conn)
        conn.close()
        result['data'] = df
        logger.info(f"查询成功，返回 {len(df)} 行")

    except Exception as e:
        result['error'] = str(e)
        logger.error(f"处理失败: {e}")
    
    # 存储到缓存
    CACHE[question] = result
    return result

# 简单测试（可选）
if __name__ == "__main__":
    test_q = "各个地区的总销售额是多少？"
    res = ask_question(test_q)
    print(f"SQL: {res['sql']}")
    if res['error']:
        print(f"错误: {res['error']}")
    else:
        print(res['data'].head())
