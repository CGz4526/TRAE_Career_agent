"""技能差距分析 Agent —— 对比用户技能与岗位要求，输出差距报告与学习建议"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from typing import List
from langchain_core.prompts import ChatPromptTemplate
from models.schemas import SkillGapReport, JobProfile
from agents.job_matcher import get_llm


SKILL_GAP_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一位资深的技术导师与职业规划专家，精通后端技术栈体系。
请对比用户已掌握的技能与目标岗位的要求，输出结构化的技能差距分析报告。

分析要求：
1. **mastered**：用户已掌握且岗位要求的技能（模糊匹配，如用户"Spring"匹配岗位"Spring Boot"）
2. **missing**：岗位要求但用户未掌握的技能，按重要度（高/中/低）排序，每项给出具体学习建议
3. **extra**：用户掌握但岗位未明确要求的技能（潜在加分项）
4. **match_percentage**：匹配度 = 已掌握的核心技能数 / 岗位核心技能数 × 100，保留 1 位小数
5. **recommendations**：针对核心差距给出 3-5 条整体学习路径建议，按优先级排序
6. **summary**：一段话总结差距情况与改进方向

重要度判定标准：
- 高：岗位核心技能（core_skills 中的项），缺失会直接影响通过率
- 中：岗位技术栈（tech_stack）中的项，缺失需补足
- 低：加分项（bonus_items），缺失不致命

学习建议要具体可执行，包含学习方向、推荐资源类型、预计周期。"""),
    ("human", """请分析以下技能差距：

## 用户已掌握技能
{user_skills}

## 目标岗位画像
{job_profile}"""),
])


async def analyze_skill_gap(user_skills: List[str], job_profile: JobProfile) -> SkillGapReport:
    """
    对比用户技能与岗位要求，生成差距分析报告

    Args:
        user_skills: 用户已掌握的技能列表
        job_profile: 目标岗位画像

    Returns:
        SkillGapReport: 技能差距分析报告
    """
    llm = get_llm()
    structured_llm = llm.with_structured_output(SkillGapReport)
    chain = SKILL_GAP_PROMPT | structured_llm

    # LLM 偶尔会在 JSON 字符串值中输出未转义换行符导致解析失败，最多重试 2 次
    last_err = None
    for attempt in range(3):
        try:
            result = await chain.ainvoke({
                "user_skills": json.dumps(user_skills, ensure_ascii=False),
                "job_profile": json.dumps(job_profile.model_dump(), ensure_ascii=False, indent=2),
            })
            return result
        except Exception as e:
            last_err = e
            # 重试时在 prompt 末尾强调 JSON 规范，避免未转义字符
            if attempt < 2:
                continue
    raise last_err


if __name__ == "__main__":
    import asyncio

    async def test():
        from agents.job_matcher import match_job

        jd = """岗位：Java后端开发
1. 熟悉Spring Boot、MyBatis
2. 熟悉MySQL、Redis，了解Kafka
3. 3年经验"""
        profile = await match_job(jd)
        print(f"岗位: {profile.position}\n")

        user_skills = ["Java", "Spring Boot", "MySQL", "Git", "Docker", "Linux"]
        print(f"用户技能: {user_skills}\n")

        report = await analyze_skill_gap(user_skills, profile)
        print(f"匹配度: {report.match_percentage}%")
        print(f"已掌握: {report.mastered}")
        print(f"未掌握: {[m.skill for m in report.missing]}")
        print(f"超出: {report.extra}")
        print(f"\n建议: {report.recommendations}")

    asyncio.run(test())
