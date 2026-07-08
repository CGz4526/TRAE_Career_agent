"""
LangGraph 多 Agent 工作流编排
Supervisor 模式：协调 Agent 统筹 5 个专业子 Agent

工作流：
1. 岗位匹配 Agent (必经第一步)
2. 并行执行：简历优化 + 题库生成 + 项目梳理
3. 模拟面试 Agent (最后一步，可选)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from typing import TypedDict, List, Optional, Any
from langgraph.graph import StateGraph, END

from models.schemas import (
    JobProfile, ResumeOptimizeResult, QuestionBank,
    ProjectStory, InterviewReport
)
from agents.job_matcher import match_job
from agents.resume_optimizer import optimize_resume
from agents.question_bank import generate_questions
from agents.project_story import organize_project_story
from agents.mock_interview import InterviewSession


# ==================== 状态定义 ====================
class AgentState(TypedDict):
    """多 Agent 共享状态"""
    # 输入
    jd_text: str
    resume_text: str
    project_desc: str
    # 中间结果
    job_profile: Optional[dict]
    optimized_resume: Optional[dict]
    question_bank: Optional[dict]
    project_story: Optional[dict]
    # 面试（异步，不在此工作流中执行）
    interview_session_id: Optional[str]
    # 元数据
    errors: List[str]
    current_step: str


# ==================== Agent 节点 ====================
async def job_matcher_node(state: AgentState) -> dict:
    """节点 1：岗位匹配 —— 解析 JD"""
    print("  [Agent] 岗位匹配 Agent 启动...")
    try:
        profile = await match_job(state["jd_text"])
        print(f"  [Agent] 岗位匹配完成: {profile.position}")
        return {
            "job_profile": profile.model_dump(),
            "current_step": "job_matched",
        }
    except Exception as e:
        print(f"  [Agent] 岗位匹配失败: {e}")
        return {"errors": state.get("errors", []) + [f"job_matcher: {str(e)}"]}


async def resume_optimizer_node(state: AgentState) -> dict:
    """节点 2a：简历优化"""
    print("  [Agent] 简历优化 Agent 启动...")
    try:
        if not state.get("resume_text"):
            print("  [Agent] 无简历输入，跳过简历优化")
            return {}
        profile = JobProfile(**state["job_profile"])
        result = await optimize_resume(state["resume_text"], profile)
        print(f"  [Agent] 简历优化完成，生成 {len(result.suggestions)} 条建议")
        return {
            "optimized_resume": result.model_dump(),
            "current_step": "resume_optimized",
        }
    except Exception as e:
        print(f"  [Agent] 简历优化失败: {e}")
        return {"errors": state.get("errors", []) + [f"resume_optimizer: {str(e)}"]}


async def question_bank_node(state: AgentState) -> dict:
    """节点 2b：题库生成"""
    print("  [Agent] 题库生成 Agent 启动...")
    try:
        profile = JobProfile(**state["job_profile"])
        result = await generate_questions(profile)
        print(f"  [Agent] 题库生成完成，共 {len(result.questions)} 道题")
        return {
            "question_bank": result.model_dump(),
            "current_step": "questions_generated",
        }
    except Exception as e:
        print(f"  [Agent] 题库生成失败: {e}")
        return {"errors": state.get("errors", []) + [f"question_bank: {str(e)}"]}


async def project_story_node(state: AgentState) -> dict:
    """节点 2c：项目梳理"""
    print("  [Agent] 项目梳理 Agent 启动...")
    try:
        if not state.get("project_desc"):
            print("  [Agent] 无项目描述输入，跳过项目梳理")
            return {}
        result = await organize_project_story(state["project_desc"])
        print("  [Agent] 项目梳理完成")
        return {
            "project_story": result.model_dump(),
            "current_step": "story_organized",
        }
    except Exception as e:
        print(f"  [Agent] 项目梳理失败: {e}")
        return {"errors": state.get("errors", []) + [f"project_story: {str(e)}"]}


# ==================== 路由函数 ====================
def route_after_job_match(state: AgentState) -> str:
    """岗位匹配后的路由：如果有错误直接结束，否则进入并行阶段"""
    if state.get("errors"):
        return "end"
    if not state.get("job_profile"):
        return "end"
    return "parallel"


def should_continue(state: AgentState) -> str:
    """并行阶段完成后，检查是否结束"""
    return "end"


# ==================== 构建工作流图 ====================
def build_workflow():
    """
    构建 LangGraph 多 Agent 工作流

    流程:
        START → job_matcher → [resume_optimizer + question_bank + project_story] → END
    """
    workflow = StateGraph(AgentState)

    # 添加节点（节点名不能与状态键同名）
    workflow.add_node("job_matcher_node", job_matcher_node)
    workflow.add_node("resume_optimizer_node", resume_optimizer_node)
    workflow.add_node("question_bank_node", question_bank_node)
    workflow.add_node("project_story_node", project_story_node)

    # 设置入口
    workflow.set_entry_point("job_matcher_node")

    # 岗位匹配后路由
    workflow.add_conditional_edges(
        "job_matcher_node",
        route_after_job_match,
        {
            "parallel": "resume_optimizer_node",  # 进入串行阶段
            "end": END,
        }
    )

    # 串行执行：简历优化 → 题库生成 → 项目梳理
    workflow.add_edge("resume_optimizer_node", "question_bank_node")
    workflow.add_edge("question_bank_node", "project_story_node")
    workflow.add_edge("project_story_node", END)

    return workflow.compile()


# ==================== 便捷调用函数 ====================
async def run_full_pipeline(jd_text: str, resume_text: str = "", project_desc: str = "") -> dict:
    """
    运行完整多 Agent 管线：JD解析 → 简历优化 + 题库生成 + 项目梳理

    Args:
        jd_text: JD 文本
        resume_text: 简历文本（可选）
        project_desc: 项目描述（可选）

    Returns:
        dict: 所有 Agent 的输出结果
    """
    print("🚀 启动多 Agent 工作流...")

    app = build_workflow()

    initial_state: AgentState = {
        "jd_text": jd_text,
        "resume_text": resume_text,
        "project_desc": project_desc,
        "job_profile": None,
        "optimized_resume": None,
        "question_bank": None,
        "project_story": None,
        "interview_session_id": None,
        "errors": [],
        "current_step": "start",
    }

    result = await app.ainvoke(initial_state)

    print("✅ 多 Agent 工作流完成!")
    if result.get("errors"):
        print(f"⚠️  有 {len(result['errors'])} 个错误: {result['errors']}")

    return result


if __name__ == "__main__":
    import asyncio

    async def test():
        result = await run_full_pipeline(
            jd_text="""岗位：Java后端开发工程师
1. 熟悉Spring Boot、MyBatis
2. 熟悉MySQL、Redis，了解Kafka
3. 3年以上后端开发经验
4. 有高并发经验优先""",
            resume_text="""张三 | Java后端开发
XX大学 计算机本科 2020-2024
技能：Java, Spring Boot, MySQL
项目：电商后台，用Spring Boot开发商品管理模块""",
            project_desc="做过一个电商系统，用Spring Boot+MySQL，解决过并发下单问题"
        )

        print("\n===== 工作流结果汇总 =====\n")

        if result.get("job_profile"):
            print(f"岗位: {result['job_profile']['position']}")
            print(f"技术栈: {result['job_profile']['tech_stack']}")

        if result.get("optimized_resume"):
            print(f"\n简历优化: {len(result['optimized_resume']['suggestions'])} 条建议")

        if result.get("question_bank"):
            print(f"题库: {len(result['question_bank']['questions'])} 道题")

        if result.get("project_story"):
            print(f"项目梳理: {result['project_story']['summary'][:50]}...")

    asyncio.run(test())
