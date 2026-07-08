"""后端职途 · Python AI 服务入口"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel
from typing import Optional

from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("🚀 后端职途 AI 服务启动中...")
    logger.info(f"   LLM 模型: {settings.llm_model}")
    logger.info(f"   API 地址: {settings.llm_base_url}")
    if not settings.llm_api_key:
        logger.warning("⚠️  LLM_API_KEY 未配置，请在 .env 文件中设置")
    logger.info(f"✅ 服务就绪: http://{settings.host}:{settings.port}")
    yield
    logger.info("👋 服务关闭")


app = FastAPI(
    title="后端职途 AI 服务",
    description="多 Agent 求职辅助系统 —— AI 智能层",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== 健康检查 ====================
@app.get("/health")
async def health():
    return {"status": "ok", "service": "backend-career-agent-ai"}


@app.get("/agent/health")
async def agent_health():
    return {"status": "ok", "service": "backend-career-agent-ai"}


@app.get("/")
async def root():
    return {
        "service": "后端职途 AI 服务",
        "version": "0.1.0",
        "docs": "/docs",
        "agents": {
            "job_matcher": "/agent/match-job (POST)",
            "resume_optimizer": "/agent/optimize-resume (POST)",
            "question_bank": "/agent/generate-questions (POST)",
            "project_story": "/agent/project-story (POST)",
            "interview_start": "/agent/interview/start (POST)",
            "interview_chat": "/agent/interview/chat (POST)",
            "interview_report": "/agent/interview/report (GET)",
            "full_pipeline": "/agent/pipeline (POST)",
        },
    }


# ==================== 请求模型 ====================
class JobMatchRequest(BaseModel):
    jd_text: str


class ResumeOptimizeRequest(BaseModel):
    resume_text: str
    job_profile: dict


class ProjectAnalysisRequest(BaseModel):
    """项目分析请求"""
    resume_text: str
    job_profile: dict


class GenerateQuestionsRequest(BaseModel):
    job_profile: dict
    resume: str = ""


class ProjectStoryRequest(BaseModel):
    project_desc: str


class PipelineRequest(BaseModel):
    jd_text: str
    resume_text: str = ""
    project_desc: str = ""


class InterviewStartRequest(BaseModel):
    job_profile: dict
    question_bank: Optional[dict] = None
    resume: str = ""


class InterviewChatRequest(BaseModel):
    session_id: str
    answer: str


# ==================== Agent API ====================

# --- 1. 岗位匹配 Agent ---
@app.post("/agent/match-job")
async def api_match_job(req: JobMatchRequest):
    """岗位匹配 Agent —— 解析 JD，返回结构化岗位需求画像"""
    logger.info(f"收到 JD 解析请求，文本长度: {len(req.jd_text)}")
    from agents.job_matcher import match_job
    result = await match_job(req.jd_text)
    logger.info(f"岗位匹配完成: {result.position}")
    return result


# --- 2. 项目分析 Agent ---
@app.post("/agent/project-analysis")
async def api_project_analysis(req: ProjectAnalysisRequest):
    """项目分析 Agent —— 解析简历项目、提取技术栈、给出建议、推荐新项目"""
    logger.info("收到项目分析请求")
    from agents.project_analyzer import analyze_projects
    from models.schemas import JobProfile
    try:
        profile = JobProfile(**req.job_profile)
    except Exception as e:
        logger.error(f"岗位画像解析失败: {e}")
        raise HTTPException(status_code=422, detail=f"岗位画像字段不合法: {e}")
    try:
        result = await analyze_projects(req.resume_text, profile)
        logger.info(f"项目分析完成，解析出 {result.total_projects} 个项目")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"项目分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"项目分析失败: {e}")


# --- 3. 题库生成 Agent ---
@app.post("/agent/generate-questions")
async def api_generate_questions(req: GenerateQuestionsRequest):
    """题库生成 Agent —— 根据岗位画像生成面试题库"""
    logger.info("收到题库生成请求")
    from agents.question_bank import generate_questions
    from models.schemas import JobProfile
    try:
        profile = JobProfile(**req.job_profile)
    except Exception as e:
        logger.error(f"岗位画像解析失败: {e}")
        raise HTTPException(status_code=422, detail=f"岗位画像字段不合法: {e}")
    try:
        result = await generate_questions(profile, req.resume)
        logger.info(f"题库生成完成，{len(result.questions)} 道题")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"题库生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"题库生成失败: {e}")


# --- 4. 简历文件解析 Agent ---
@app.post("/agent/parse-resume-file")
async def api_parse_resume_file(file: UploadFile = File(...)):
    """简历解析 Agent —— 支持 PDF/图片格式简历的 OCR 文字提取"""
    logger.info(f"收到简历解析请求: {file.filename}")
    try:
        content = await file.read()
        from agents.resume_parser import parse_resume_file
        result = await parse_resume_file(file.filename or "resume", content)
        if result.get("method") == "error":
            raise HTTPException(status_code=400, detail=result.get("error", "解析失败"))
        logger.info(f"简历解析完成，方法: {result['method']}，页数: {result.get('pages', 0)}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"简历解析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- 4.1 JD 图片解析 Agent ---
@app.post("/agent/parse-jd-image")
async def api_parse_jd_image(file: UploadFile = File(...)):
    """岗位 JD 图片解析 Agent —— 支持图片格式 JD 的 OCR 文字提取"""
    logger.info(f"收到 JD 图片解析请求: {file.filename}")
    try:
        content = await file.read()
        filename = file.filename or "jd.png"
        from agents.resume_parser import parse_resume_file
        result = await parse_resume_file(filename, content)
        if result.get("method") == "error":
            raise HTTPException(status_code=400, detail=result.get("error", "解析失败"))
        logger.info(f"JD 图片解析完成，方法: {result['method']}，文字长度: {len(result.get('text', ''))}")
        return {
            "text": result.get("text", ""),
            "method": result.get("method", "ocr"),
            "filename": filename,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"JD 图片解析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- 5. 项目梳理 Agent ---
@app.post("/agent/project-story")
async def api_project_story(req: ProjectStoryRequest):
    """项目梳理 Agent —— 用 STAR 法则梳理项目经历"""
    logger.info("收到项目梳理请求")
    from agents.project_story import organize_project_story
    result = await organize_project_story(req.project_desc)
    logger.info("项目梳理完成")
    return result


# --- 6. 模拟面试 Agent ---
@app.post("/agent/interview/start")
async def api_interview_start(req: InterviewStartRequest):
    """模拟面试 Agent —— 开始面试，返回第一个问题"""
    logger.info("收到模拟面试启动请求")
    from agents.mock_interview import create_session
    from models.schemas import JobProfile, QuestionBank

    profile = JobProfile(**req.job_profile)
    bank = QuestionBank(**req.question_bank) if req.question_bank else None

    session_id = f"interview_{uuid.uuid4().hex[:12]}"
    session = create_session(session_id, profile, bank, req.resume)

    first_question = await session.start()
    logger.info(f"面试会话创建: {session_id}")
    return {
        "session_id": session_id,
        "question": first_question,
        "stage": session.stage_names[session.stage],
    }


@app.post("/agent/interview/chat")
async def api_interview_chat(req: InterviewChatRequest):
    """模拟面试 Agent —— 候选人回答，返回下一个问题"""
    from agents.mock_interview import get_session

    session = get_session(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="面试会话不存在或已过期")

    if session.finished:
        return {
            "question": "面试已结束，请获取评分报告。",
            "stage": "面试结束",
            "finished": True,
        }

    next_question = await session.chat(req.answer)
    return {
        "session_id": req.session_id,
        "question": next_question,
        "stage": session.stage_names[min(session.stage, 6)],
        "finished": session.finished,
    }


@app.get("/agent/interview/{session_id}/report")
async def api_interview_report(session_id: str):
    """模拟面试 Agent —— 生成面试评分报告"""
    from agents.mock_interview import get_session

    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="面试会话不存在或已过期")

    if not session.finished:
        raise HTTPException(status_code=400, detail="面试尚未结束，无法生成报告")

    report = await session.generate_report()
    return {
        "report": report,
        "dialogue": session.get_dialogue(),
    }


# --- 6. 多 Agent 全流程管线 ---
@app.post("/agent/pipeline")
async def api_pipeline(req: PipelineRequest):
    """多 Agent 全流程：JD解析 → 简历优化 + 题库生成 + 项目梳理"""
    logger.info(f"收到全流程请求，JD长度: {len(req.jd_text)}")
    from graph.workflow import run_full_pipeline
    result = await run_full_pipeline(
        jd_text=req.jd_text,
        resume_text=req.resume_text,
        project_desc=req.project_desc,
    )
    logger.info("全流程完成")
    return result


# ==================== 角色卡 API ====================
@app.get("/agent/role-cards")
async def api_role_cards():
    """获取 8 个预设角色卡列表"""
    from agents.role_cards import get_all_role_cards
    return {"role_cards": get_all_role_cards()}


@app.get("/agent/role-cards/{card_id}")
async def api_role_card_detail(card_id: str):
    """获取指定预设角色卡详情"""
    from agents.role_cards import get_role_card_by_id
    card = get_role_card_by_id(card_id)
    if not card:
        raise HTTPException(status_code=404, detail=f"角色卡不存在: {card_id}")
    return card


# ==================== 技能差距分析 Agent ====================
class SkillGapRequest(BaseModel):
    user_skills: list[str]
    job_profile: dict


@app.post("/agent/skill-gap")
async def api_skill_gap(req: SkillGapRequest):
    """技能差距分析 Agent —— 对比用户技能与岗位要求，输出差距报告"""
    logger.info(f"收到技能差距分析请求，用户技能数: {len(req.user_skills)}")
    from agents.skill_gap import analyze_skill_gap
    from models.schemas import JobProfile
    profile = JobProfile(**req.job_profile)
    result = await analyze_skill_gap(req.user_skills, profile)
    logger.info(f"技能差距分析完成，匹配度: {result.match_percentage}%")
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
