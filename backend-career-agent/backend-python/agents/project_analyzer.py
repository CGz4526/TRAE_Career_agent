"""项目分析 Agent —— 解析简历项目、提取技术栈、给出建议、推荐新项目"""
import sys
import os
import re
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from models.schemas import ProjectAnalysisResult, ProjectInfo, TechSuggestion, RecommendedProject, JobProfile
from agents.job_matcher import get_llm


PROJECT_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一位专业的技术简历分析师。请分析候选人的简历项目，针对目标岗位给出技术建议和新项目推荐。

请直接输出 JSON 格式结果，不要有任何额外的解释文字、Markdown 标记或前后缀。

JSON 结构如下：
{{
  "projects": [
    {{
      "name": "项目名称",
      "description": "项目描述（原文摘录）",
      "tech_stack": ["技术1", "技术2"],
      "highlights": ["亮点1", "亮点2"]
    }}
  ],
  "total_projects": 项目数量,
  "tech_suggestions": [
    {{
      "tech": "技术名称",
      "reason": "为什么建议学",
      "how_to_add": "如何在现有项目中加入",
      "priority": "高/中/低"
    }}
  ],
  "recommended_project": {{
    "name": "项目名称",
    "description": "项目简介",
    "tech_stack": ["技术1", "技术2"],
    "difficulty": "入门/进阶/高级",
    "value": "项目价值",
    "implementation_hints": ["要点1", "要点2"]
  }},
  "summary": "整体分析总结"
}}

【重要规则】
1. projects 中的所有信息必须从简历原文提取，不得编造
2. tech_suggestions 是建议，不是简历已有内容
3. recommended_project 是推荐的新项目，不是简历已有项目
4. 只输出 JSON，不要输出任何其他内容"""),
    ("human", """目标岗位画像：
{job_profile}

候选人简历：
{resume_text}"""),
])


async def analyze_projects(resume_text: str, job_profile: JobProfile) -> ProjectAnalysisResult:
    """
    分析简历项目，给出技术建议和新项目推荐

    Args:
        resume_text: 原始简历文本
        job_profile: 岗位需求画像

    Returns:
        ProjectAnalysisResult: 项目分析结果
    """
    llm = get_llm()

    import json
    profile_str = json.dumps(job_profile.model_dump(), ensure_ascii=False, indent=2)

    # 先尝试用结构化输出
    try:
        structured_llm = llm.with_structured_output(ProjectAnalysisResult)
        chain = PROJECT_ANALYSIS_PROMPT | structured_llm
        result = await chain.ainvoke({
            "job_profile": profile_str,
            "resume_text": resume_text,
        })
        return result
    except Exception as e:
        print(f"结构化输出解析失败，尝试手动解析: {e}")

    # 降级：直接调用 LLM，手动提取 JSON
    chain = PROJECT_ANALYSIS_PROMPT | llm
    response = await chain.ainvoke({
        "job_profile": profile_str,
        "resume_text": resume_text,
    })
    content = response.content if hasattr(response, 'content') else str(response)

    # 提取第一个完整的 JSON 对象
    first_brace = content.find('{')
    last_brace = content.rfind('}')
    if first_brace == -1 or last_brace == -1:
        raise ValueError("无法从 LLM 响应中提取 JSON")

    json_str = content[first_brace:last_brace + 1]

    try:
        data = json.loads(json_str)
        return ProjectAnalysisResult(**data)
    except Exception as e:
        # 尝试修复：从左到右找到最大的有效 JSON
        for i in range(len(json_str), 0, -1):
            try:
                data = json.loads(json_str[:i])
                return ProjectAnalysisResult(**data)
            except:
                continue
        raise ValueError(f"JSON 解析失败: {e}")


if __name__ == "__main__":
    import asyncio
    from agents.job_matcher import match_job

    test_jd = """岗位：Java 后端开发工程师
1. 熟悉 Spring Boot、MySQL、Redis
2. 有高并发系统设计经验
3. 3年以上经验"""

    test_resume = """张三 | Java后端开发

技能：
- Java、Spring Boot、MySQL、Redis

项目经历：
1. 电商后台管理系统
   使用Spring Boot开发，实现了商品管理和订单管理模块。
   使用Redis做缓存，MySQL存储数据。

2. 在线考试系统
   SSM框架，实现了试题管理和自动判分功能。"""

    async def test():
        profile = await match_job(test_jd)
        print("岗位画像:", profile.position)
        result = await analyze_projects(test_resume, profile)
        print("\n===== 项目分析结果 =====")
        print(f"项目数量: {result.total_projects}")
        for p in result.projects:
            print(f"\n【{p.name}】")
            print(f"  技术栈: {', '.join(p.tech_stack)}")
            print(f"  亮点: {p.highlights}")
        print(f"\n===== 技术建议 =====")
        for s in result.tech_suggestions:
            print(f"\n[{s.priority}] {s.tech}")
            print(f"  原因: {s.reason}")
            print(f"  如何加入: {s.how_to_add}")
        print(f"\n===== 推荐项目 =====")
        print(f"项目名: {result.recommended_project.name}")
        print(f"描述: {result.recommended_project.description}")
        print(f"技术栈: {', '.join(result.recommended_project.tech_stack)}")
        print(f"难度: {result.recommended_project.difficulty}")
        print(f"\n总结: {result.summary}")

    asyncio.run(test())
