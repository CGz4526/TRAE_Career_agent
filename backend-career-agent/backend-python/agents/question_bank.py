"""题库生成 Agent —— 根据岗位需求画像自动生成分类面试题库"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from models.schemas import QuestionBank, JobProfile
from agents.job_matcher import get_llm


QUESTION_BANK_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一位资深后端技术面试官，精通 Java、Python 后端技术面试。
请根据岗位需求画像和简历信息，生成一套完整的面试题库。

题库分类要求：
1. **八股文** (8题)：Java/Python 基础、集合框架、JVM、并发编程、Spring 框架原理、数据库原理、缓存中间件、消息队列等知识点，覆盖全面
2. **算法** (4题)：中等难度，与后端场景相关（如链表、树、动态规划、字符串、滑动窗口等）
3. **系统设计** (3题)：后端架构设计题（如设计短链系统、秒杀系统、限流降级、分布式事务、消息队列架构等）
4. **项目深挖** (5题)：针对简历中提到的项目经历进行深入追问，如果有简历信息则围绕简历中的项目背景、技术难点、解决方案、性能优化、踩坑经验等角度出题；如果没有简历信息，则给出通用的项目追问方向

每道题包含：
- category: 分类
- difficulty: 简单/中等/困难
- question: 题干
- answer: 标准答案（简洁准确）
- explanation: 解析说明
- tags: 知识点标签

确保题目与岗位技术栈高度相关，不生成无关题目。
项目深挖题务必结合简历中的具体项目来设计，不要泛泛而谈。"""),
    ("human", """请根据以下岗位需求画像和简历信息生成面试题库：

## 岗位需求画像
{job_profile}

## 简历信息（用于项目深挖题参考）
{resume_info}"""),
])


async def generate_questions(job_profile: JobProfile, resume: str = "") -> QuestionBank:
    """
    根据岗位需求画像生成分类面试题库

    Args:
        job_profile: 岗位需求画像
        resume: 简历文本（可选，用于项目深挖题）

    Returns:
        QuestionBank: 分类题库
    """
    llm = get_llm()
    structured_llm = llm.with_structured_output(QuestionBank)
    chain = QUESTION_BANK_PROMPT | structured_llm

    import json
    profile_str = json.dumps(job_profile.model_dump(), ensure_ascii=False, indent=2)
    resume_str = resume.strip() if resume else "（未提供简历，项目深挖题请给出通用方向）"
    result = await chain.ainvoke({"job_profile": profile_str, "resume_info": resume_str})
    return result


if __name__ == "__main__":
    import asyncio
    import json
    from agents.job_matcher import match_job

    test_jd = """岗位：Java 后端开发工程师
1. 熟悉 Spring Boot、MyBatis
2. 熟悉 MySQL、Redis，了解 Kafka
3. 3年以上后端开发经验"""

    async def test():
        profile = await match_job(test_jd)
        print(f"为岗位 [{profile.position}] 生成题库...\n")
        bank = await generate_questions(profile)
        print(f"共生成 {len(bank.questions)} 道题\n")
        for i, q in enumerate(bank.questions, 1):
            print(f"--- 第{i}题 [{q.category}] [{q.difficulty}] ---")
            print(f"题干: {q.question}")
            print(f"答案: {q.answer[:100]}...")
            print(f"标签: {q.tags}")
            print()

    asyncio.run(test())
