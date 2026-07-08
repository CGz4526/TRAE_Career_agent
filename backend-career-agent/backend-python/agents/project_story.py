"""项目梳理 Agent —— 用 STAR 法则引导用户梳理项目经历"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from models.schemas import ProjectStory
from agents.job_matcher import get_llm


PROJECT_STORY_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一位后端技术面试辅导专家。
用户会提供一段粗略的项目描述，请你用 STAR 法则（Situation-Task-Action-Result）帮助梳理成结构化的项目故事。

要求：
1. **Situation（背景）**：项目背景、业务场景、团队规模
2. **Task（任务）**：用户承担的具体职责和目标
3. **Action（行动）**：采取的技术方案、关键决策、解决的具体问题
4. **Result（成果）**：量化结果（性能提升、bug 率降低、用户增长等）
5. **summary**：一段 2-3 句话的精炼描述，可直接用于简历

注意：
- 从用户描述中提取信息，不要编造虚假数据
- 如果信息不足，在对应字段标注 "(请补充)"
- 技术细节要准确，符合后端开发实际"""),
    ("human", """请帮我梳理以下项目经历：

{project_desc}"""),
])


async def organize_project_story(project_desc: str) -> ProjectStory:
    """
    用 STAR 法则梳理项目经历

    Args:
        project_desc: 用户粗略的项目描述

    Returns:
        ProjectStory: STAR 结构化项目描述
    """
    llm = get_llm()
    structured_llm = llm.with_structured_output(ProjectStory)
    chain = PROJECT_STORY_PROMPT | structured_llm
    result = await chain.ainvoke({"project_desc": project_desc})
    return result


if __name__ == "__main__":
    import asyncio

    test_desc = """我做过一个电商后台系统，用Spring Boot写的。
    主要做了商品管理和订单管理，数据库用的MySQL。
    遇到过并发下单的问题，后来加了Redis分布式锁解决了。
    还做了接口优化，用了缓存。"""

    async def test():
        result = await organize_project_story(test_desc)
        print("===== STAR 项目故事 =====\n")
        print(f"【Situation 背景】\n{result.situation}\n")
        print(f"【Task 任务】\n{result.task}\n")
        print(f"【Action 行动】\n{result.action}\n")
        print(f"【Result 成果】\n{result.result}\n")
        print(f"【简历摘要】\n{result.summary}")

    asyncio.run(test())
