"""岗位匹配 Agent —— 解析 JD，提取结构化岗位需求画像"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from models.schemas import JobProfile
from config import settings


def get_llm() -> ChatOpenAI:
    """获取 LLM 实例"""
    return ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        temperature=0.3,
    )


# Prompt 模板
JOB_MATCH_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一位资深后端技术招聘专家，精通 Java、Python 后端技术栈。
请分析用户提供的 JD（岗位描述）文本，提取结构化的岗位需求画像。

要求：
1. 技术栈要精确到具体框架和工具（如 Spring Boot 而非仅 Spring）
2. 核心技能按重要性排序
3. 如果 JD 中未明确某项，使用合理默认值（如经验年数默认 1）
4. 软技能和加分项如果没有提到，返回空列表"""),
    ("human", "请分析以下 JD 文本：\n\n{jd_text}"),
])


async def match_job(jd_text: str) -> JobProfile:
    """
    解析 JD 文本，返回结构化岗位需求画像

    Args:
        jd_text: JD 原始文本

    Returns:
        JobProfile: 结构化岗位需求画像
    """
    llm = get_llm()
    structured_llm = llm.with_structured_output(JobProfile)
    chain = JOB_MATCH_PROMPT | structured_llm
    result = await chain.ainvoke({"jd_text": jd_text})
    return result


if __name__ == "__main__":
    # 本地测试
    import asyncio
    import json

    test_jd = """岗位：Java 后端开发工程师
1. 熟悉 Java 编程，深入理解 Spring Boot、MyBatis
2. 熟悉 MySQL、Redis，了解消息队列 Kafka
3. 3年以上后端开发经验，本科及以上学历
4. 良好的沟通能力和团队协作精神
5. 有高并发系统设计经验者优先"""

    if not settings.llm_api_key:
        print("⚠️  请先在 .env 文件中配置 LLM_API_KEY")
        print("   复制 .env.example 为 .env，填入你的 API Key")
    else:
        result = asyncio.run(match_job(test_jd))
        print(json.dumps(result.model_dump(), ensure_ascii=False, indent=2))
