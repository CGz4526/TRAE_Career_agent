"""简历优化 Agent —— 基于岗位需求画像，针对性优化简历"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from models.schemas import ResumeOptimizeResult, JobProfile
from agents.job_matcher import get_llm


RESUME_OPTIMIZE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一位专业的技术简历优化顾问。你的核心任务是：基于候选人的真实简历，针对目标岗位需求进行优化润色。

【最高红线：绝对禁止编造任何信息】
这是不可逾越的红线。你的所有优化必须严格基于原始简历中已有的信息，绝对不能添加任何原始简历没有的事实性内容。

以下内容严禁出现在 optimized_resume 中：
1. 教育经历：不得添加课程、GPA、分数、排名、奖学金、学校名称、专业等任何原文没有的信息
2. 奖项荣誉：不得添加任何原文没有的奖项、证书、竞赛
3. 工作/实习经历：不得添加公司名称、职位、时间、团队规模等原文没有的信息
4. 项目经历：
   - 不得添加原文没有的项目名称、技术栈、框架、工具、库
   - 不得编造任何量化数据（QPS、性能提升百分比、用户数、成功率、代码行数等）
   - 不得添加原文没有的项目职责、架构设计、解决方案
   - 不得虚构微服务架构、分布式系统、中间件等原文没有的技术
5. 技能清单：不得添加原文没有的技能，只能调整排序或修改措辞
6. 不得添加"按JD匹配度排序"等任何说明性文字或括号注释
7. 不得添加任何原文没有的自我评价、个人总结内容
8. 【重要】不得新增任何原文没有的板块！比如原文没有"技术博客"、"开源贡献"、"论文发表"、"专利"等板块，优化后也绝对不能有
9. 【重要】不得新增任何原文没有的条目！比如原文项目只有2个，优化后也必须是2个，不能变成3个

【你可以对 optimized_resume 做的优化】
1. 措辞优化：将口语化、平淡的表述改为更专业、更书面、更有冲击力的表达
2. 结构优化：调整段落顺序、使用更清晰的 bullet point 结构、优化排版
3. STAR 重述：将平铺直叙的项目经历用 STAR 结构重新组织语言，但所有事实必须来自原文
4. 关键词强化：将岗位需求中的关键词自然融入已有描述中，但前提是简历确实有相关经历
5. 重点突出：将与目标岗位最相关的经历和技能前置，提高匹配度
6. 模糊量化保留：如果原文有"大幅提升"、"显著改善"等模糊表述，可以改为更专业的表述（如"性能得到明显优化"），但绝对不能添加具体数字
7. 技能排序：按岗位需求的重要性重新排序技能列表，但不添加新技能

【严禁修改的板块】
以下板块如果原文有，只能原样保留或微调措辞，不得增删内容：
- 个人信息（姓名、联系方式等）
- 教育背景（学校、专业、学历、时间）
- 奖项荣誉
- 证书资格

【改进建议 improvement_suggestions】
这是给用户的额外建议，不直接写入简历。你可以在这里大胆提出改进建议：
- 技术栈补充：建议用户学习哪些岗位需要但简历中没有的技术
- 项目优化：建议用户在项目中可以补充哪些内容来提升匹配度
- 技能提升：建议用户提升哪些方面的能力
- 其他建议：其他任何对求职有帮助的建议
每条建议包含 category（分类）、content（内容）、priority（优先级：高/中/低）

【学习建议 learning_suggestions】
针对当前岗位，给用户列出具体的学习路径建议，3-8条。

【修改建议 suggestions 的严格要求】
- original 字段必须是从原始简历中精确摘录的原文片段，一字不差
- optimized 字段必须是基于原文优化后的内容，所有事实性信息必须能在原文中找到对应
- reason 字段说明修改理由，以及与岗位需求的关联
- section 字段标明属于哪个板块（如"项目经历"、"技能"等）
- 如果某个板块不需要修改，可以不出现在 suggestions 中
- suggestions 不能为空！至少要有 3-5 条有实际意义的修改建议

请记住：
1. optimized_resume 是"优化后的简历"，只能润色，不能创作
2. improvement_suggestions 是"建议"，告诉用户可以怎么改进，但不直接改
3. 宁可优化得少，也绝不能编造。简历的真实性是第一位的。
4. 如果你不确定某条信息是否在原文中，就当它不在原文中，不要加进去。"""),
    ("human", """请根据以下岗位需求画像优化我的简历：

## 岗位需求画像
{job_profile}

## 我的原始简历
{resume_text}"""),
])


async def optimize_resume(resume_text: str, job_profile: JobProfile) -> ResumeOptimizeResult:
    """
    基于岗位需求画像优化简历

    Args:
        resume_text: 原始简历文本
        job_profile: 岗位需求画像

    Returns:
        ResumeOptimizeResult: 优化后简历 + 修改建议列表
    """
    llm = get_llm()
    structured_llm = llm.with_structured_output(ResumeOptimizeResult)
    chain = RESUME_OPTIMIZE_PROMPT | structured_llm

    import json
    profile_str = json.dumps(job_profile.model_dump(), ensure_ascii=False, indent=2)
    result = await chain.ainvoke({
        "job_profile": profile_str,
        "resume_text": resume_text,
    })
    return result


if __name__ == "__main__":
    import asyncio
    import json
    from agents.job_matcher import match_job

    test_jd = """岗位：Java 后端开发工程师
1. 熟悉 Spring Boot、MyBatis
2. 熟悉 MySQL、Redis
3. 3年以上后端开发经验"""

    test_resume = """张三 | Java后端开发
手机：138xxxx | 邮箱：zhangsan@email.com

教育背景：
XX大学 计算机科学与技术 本科 2020-2024

技能：
- Java基础，了解Spring
- MySQL基本操作
- 了解Redis

项目经历：
1. 电商后台管理系统
   使用Spring Boot开发，实现了商品管理、订单管理模块。
   负责数据库设计和接口开发。

2. 在线考试系统
   使用SSM框架，实现试题管理和自动判分。"""

    async def test():
        profile = await match_job(test_jd)
        print("岗位画像:", profile.position)
        result = await optimize_resume(test_resume, profile)
        print("\n===== 优化后简历 =====")
        print(result.optimized_resume)
        print("\n===== 修改建议 =====")
        for s in result.suggestions:
            print(f"\n[{s.section}]")
            print(f"  原文: {s.original}")
            print(f"  优化: {s.optimized}")
            print(f"  理由: {s.reason}")

    asyncio.run(test())
