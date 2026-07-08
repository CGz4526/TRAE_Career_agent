"""Pydantic 数据模型 —— Agent 间传递的结构化数据"""
from pydantic import BaseModel, Field
from typing import List, Optional


class JobProfile(BaseModel):
    """岗位需求画像 —— 岗位匹配 Agent 的输出"""

    position: str = Field(description="岗位名称")
    tech_stack: List[str] = Field(description="技术栈列表，如 ['Java', 'Spring Boot', 'MySQL']")
    experience_years: str = Field(default="", description="经验要求，如 '3-5年' / '3' / '不限'")
    education: str = Field(default="", description="学历要求")
    core_skills: List[str] = Field(default_factory=list, description="核心技能要求")
    soft_skills: List[str] = Field(default_factory=list, description="软技能要求")
    bonus_items: List[str] = Field(default_factory=list, description="加分项")
    key_responsibilities: List[str] = Field(default_factory=list, description="核心职责")
    interview_directions: List[str] = Field(default_factory=list, description="面试重点方向")

    model_config = {"extra": "allow"}


class ResumeSuggestion(BaseModel):
    """单条简历修改建议"""
    section: str = Field(description="修改的简历板块")
    original: str = Field(description="原文内容（必须从原始简历精确摘录）")
    optimized: str = Field(description="优化后内容（必须基于原文，不得添加新事实）")
    reason: str = Field(description="修改理由")


class ImprovementSuggestion(BaseModel):
    """单条改进建议（不直接修改简历，仅供用户参考）"""
    category: str = Field(description="建议分类：技术栈补充/项目优化/技能提升/其他")
    content: str = Field(description="建议内容")
    priority: str = Field(description="优先级：高/中/低")


class ResumeOptimizeResult(BaseModel):
    """简历优化 Agent 的输出"""
    optimized_resume: str = Field(description="优化后的完整简历文本（仅对已有内容润色重组，不得添加任何新事实）")
    suggestions: List[ResumeSuggestion] = Field(description="逐条修改建议（所有修改必须能在原文中找到对应内容）")
    improvement_suggestions: List[ImprovementSuggestion] = Field(description="改进建议列表（给用户的建议，不直接写入简历）")
    learning_suggestions: List[str] = Field(description="学习建议列表（针对当前岗位的学习路径建议）")


class Question(BaseModel):
    """单道面试题"""
    category: str = Field(description="题目分类：八股文/算法/系统设计/项目深挖")
    difficulty: str = Field(description="难度：简单/中等/困难")
    question: str = Field(description="题干")
    answer: str = Field(description="标准答案")
    explanation: str = Field(default="", description="解析说明")
    tags: List[str] = Field(default_factory=list, description="知识点标签")


class QuestionBank(BaseModel):
    """题库生成 Agent 的输出"""
    questions: List[Question] = Field(description="面试题列表")


class ProjectStory(BaseModel):
    """项目梳理 Agent 的输出（STAR 法则）"""
    situation: str = Field(description="项目背景")
    task: str = Field(description="承担的任务")
    action: str = Field(description="采取的行动")
    result: str = Field(description="取得的成果")
    summary: str = Field(description="一段式项目描述（可直接用于简历）")


class InterviewScore(BaseModel):
    """面试评分单项"""
    dimension: str = Field(description="评分维度")
    score: float = Field(description="得分 (0-10)")
    comment: str = Field(description="评语")


class QuestionReview(BaseModel):
    """单题回顾 —— 标准答案与纠错"""
    question: str = Field(description="面试官提出的问题")
    candidate_answer: str = Field(description="候选人的回答")
    standard_answer: str = Field(description="参考答案（绿色展示）")
    error_correction: str = Field(default="", description="错误纠正（红色展示，回答正确则为空）")
    is_correct: bool = Field(default=False, description="回答是否基本正确")


class InterviewReport(BaseModel):
    """模拟面试 Agent 的输出"""
    scores: List[InterviewScore] = Field(description="多维评分")
    overall_score: float = Field(description="综合得分")
    strengths: List[str] = Field(description="亮点表现")
    improvements: List[str] = Field(description="改进建议")
    summary: str = Field(description="面试总结")
    question_reviews: List[QuestionReview] = Field(description="逐题回顾：标准答案与纠错")


class SkillGapItem(BaseModel):
    """单项技能差距"""
    skill: str = Field(description="技能名称")
    importance: str = Field(description="重要度：高/中/低")
    status: str = Field(description="掌握状态：mastered/missing/extra")
    recommendation: str = Field(default="", description="学习建议（仅 missing 项有）")


class SkillGapReport(BaseModel):
    """技能差距分析 Agent 的输出"""
    mastered: List[str] = Field(description="已掌握的岗位要求技能")
    missing: List[SkillGapItem] = Field(description="未掌握的岗位要求技能，按重要度排序")
    extra: List[str] = Field(description="用户掌握但岗位未要求的技能")
    match_percentage: float = Field(description="技能匹配度百分比 (0-100)")
    recommendations: List[str] = Field(description="整体学习路径建议")
    summary: str = Field(description="差距分析总结")


# ==================== 项目分析相关模型 ====================

class ProjectInfo(BaseModel):
    """简历中的单个项目"""
    name: str = Field(description="项目名称")
    description: str = Field(description="项目描述（原文摘录）")
    tech_stack: List[str] = Field(description="使用的技术栈列表")
    highlights: List[str] = Field(description="项目核心亮点/职责（原文摘录）")


class TechSuggestion(BaseModel):
    """技术补充建议"""
    tech: str = Field(description="建议学习/加入的技术")
    reason: str = Field(description="为什么建议学习这项技术")
    how_to_add: str = Field(description="如何在现有项目中融入这项技术（具体建议）")
    priority: str = Field(description="优先级：高/中/低")


class RecommendedProject(BaseModel):
    """推荐的新项目"""
    name: str = Field(description="项目名称")
    description: str = Field(description="项目简介")
    tech_stack: List[str] = Field(description="需要掌握的技术栈")
    difficulty: str = Field(description="难度：入门/进阶/高级")
    value: str = Field(description="这个项目对目标岗位的价值说明")
    implementation_hints: List[str] = Field(description="实现要点提示（3-5条）")


class ProjectAnalysisResult(BaseModel):
    """项目分析 Agent 的输出"""
    projects: List[ProjectInfo] = Field(description="简历中解析出的项目列表")
    total_projects: int = Field(description="项目总数")
    tech_suggestions: List[TechSuggestion] = Field(description="技术补充建议列表")
    recommended_project: RecommendedProject = Field(description="针对目标岗位推荐的新项目")
    summary: str = Field(description="整体分析总结")
