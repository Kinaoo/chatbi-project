import os
import sqlite3
import logging
from dotenv import load_dotenv
from openai import OpenAI
import matplotlib.pyplot as plt
import seaborn as sns

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

def auto_plot(df, question, output_dir='charts', filename=None):
    """
    根据 DataFrame 和用户问题自动生成图表并保存。
    """
    # 1. 检查数据有效性
    if df is None or df.empty:
        return None

    # 2. 判断是否需要生成图表（关键词匹配）
    chart_keywords = ['画图', '图表', '可视化', '趋势', '对比', '柱状图', '折线图', '饼图']
    if not any(kw in question for kw in chart_keywords):
        return None

    # 3. 创建保存目录
    os.makedirs(output_dir, exist_ok=True)

    # 4. 生成唯一文件名
    if filename is None:
        import time
        filename = f"chart_{int(time.time())}.png"
    save_path = os.path.join(output_dir, filename)

    # ========== 优先处理饼图（用户明确要求） ==========
    if '饼图' in question:
        # 情况1：数据有两列，且第二列为数值 → 直接用第一列作标签，第二列作数值
        if df.shape[1] == 2 and df.dtypes.iloc[1] in ['int64', 'float64']:
            plt.figure(figsize=(8, 8))
            plt.pie(df.iloc[:, 1], labels=df.iloc[:, 0], autopct='%1.1f%%')
            plt.title(question[:50])
            plt.tight_layout()
            plt.savefig(save_path)
            plt.close()
            return save_path
        # 情况2：数据包含百分比列（列名含"percent"或"比例"）
        percent_col = None
        for col in df.columns:
            if 'percent' in col.lower() or '比例' in col:
                percent_col = col
                break
        if percent_col:
            # 取第一列作为标签
            label_col = df.columns[0]
            plt.figure(figsize=(8, 8))
            plt.pie(df[percent_col], labels=df[label_col], autopct='%1.1f%%')
            plt.title(question[:50])
            plt.tight_layout()
            plt.savefig(save_path)
            plt.close()
            return save_path
        # 其他情况无法绘制饼图，继续尝试其他图表

    # ========== 柱状图 ==========
    if df.shape[1] == 2 and df.dtypes.iloc[1] in ['int64', 'float64']:
        plt.figure(figsize=(10, 6))
        sns.barplot(x=df.columns[0], y=df.columns[1], data=df)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
        return save_path

    # ========== 折线图（含日期列） ==========
    date_cols = df.select_dtypes(include=['datetime64']).columns
    if len(date_cols) > 0:
        plt.figure(figsize=(12, 6))
        for col in df.columns:
            if col != date_cols[0] and df[col].dtype in ['int64', 'float64']:
                plt.plot(df[date_cols[0]], df[col], marker='o', label=col)
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
        return save_path

    # 未匹配任何规则，不生成图表
    return None

def ask_question(question, visualize=False):
    """
    输入自然语言问题，返回查询结果字典。
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
        if raw.startswith("```sql") and raw.endswith("```"):
            sql = raw[6:-3].strip()
        elif raw.startswith("```") and raw.endswith("```"):
            sql = raw[3:-3].strip()
        else:
            sql = raw
        result['sql'] = sql
        logger.info(f"生成的SQL: {sql}")

        conn = sqlite3.connect('superstore.db')
        import pandas as pd
        df = pd.read_sql_query(sql, conn)
        conn.close()
        result['data'] = df
        logger.info(f"查询成功，返回 {len(df)} 行")

        if visualize:
            chart_path = auto_plot(df, question)
            result['chart_path'] = chart_path

    except Exception as e:
        result['error'] = str(e)
        logger.error(f"处理失败: {e}")

    CACHE[question] = result
    return result

if __name__ == "__main__":
    test_q = "各个地区的总销售额是多少？"
    res = ask_question(test_q)
    print(f"SQL: {res['sql']}")
    if res['error']:
        print(f"错误: {res['error']}")
    else:
        print(res['data'].head())
