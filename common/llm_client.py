# common/llm_client.py
import os
import re
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class LLMClient:
    """封装与智谱 LLM 的交互，返回纯净的 SQL 字符串"""
    def __init__(self, model="glm-4-flash"):
        self.client = OpenAI(
            api_key=os.getenv("ZHIPU_API_KEY"),
            base_url="https://open.bigmodel.cn/api/paas/v4/"
        )
        self.model = model

    def generate_sql(self, system_prompt: str, user_question: str):
        """
        调用 LLM 生成 SQL
        返回: (sql, error) 元组。成功时 sql=str, error=None；失败时 sql=None, error=str
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_question}
                ],
                temperature=0
            )
            raw = response.choices[0].message.content.strip()

            # 提取 SQL（支持 Markdown 代码块）
            sql_match = re.search(r"```(?:sql)?\n*(.*?)\n*```", raw, re.DOTALL)
            if sql_match:
                sql = sql_match.group(1).strip()
            else:
                sql = raw.strip()

            # 简单校验：是否以 SELECT/WITH 等开头
            if not re.match(r'^\s*(SELECT|WITH|INSERT|UPDATE|DELETE)\s', sql, re.IGNORECASE):
                logger.warning(f"LLM 返回非 SQL 内容: {sql[:100]}")
                return None, "生成的内容不是有效的 SQL，请提出数据查询类问题。"

            logger.info(f"Generated SQL: {sql}")
            return sql, None

        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            return None, f"LLM 调用失败: {str(e)}"
