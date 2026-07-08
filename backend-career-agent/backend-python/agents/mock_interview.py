"""模拟面试 Agent —— 扮演后端面试官，进行实时模拟面试并生成评分报告"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from typing import List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from models.schemas import InterviewReport, InterviewScore, JobProfile, QuestionBank
from agents.job_matcher import get_llm


# ==================== 面试官系统 Prompt ====================
INTERVIEWER_SYSTEM_PROMPT = """你是一位资深的后端技术面试官，正在对候选人进行模拟面试。

## 面试规则
1. 每次只问一个问题，等候选人回答后再追问或换下一个问题
2. 面试流程：自我介绍 → 项目深挖(4-5题) → 技术深挖(3-4题) → 综合考察(1题)
3. 总共约 8-10 个问题，确保覆盖全面
4. 根据候选人回答的深度，适当追问细节
5. 如果候选人回答偏离方向，温和引导回正题
6. 态度专业友好，不要打击候选人

## 【核心原则：基于简历提问】
这是最重要的原则，请严格遵守：
1. 所有问题必须基于候选人简历中已有的经历和技能
2. 优先围绕简历中的项目经历进行深入挖掘和追问
3. 对于简历中提到的技术栈，可以深入问原理和实践
4. 对于简历中没有提到的技术，不要主动提问！
5. 项目深挖阶段，选择简历中最相关、最有深度的1-2个项目，进行多轮追问
6. 可以追问项目中的技术难点、解决方案、性能优化、踩坑经历等

## 候选人简历
{resume_text}

## 岗位信息
{job_info}

## 题库参考（仅作知识点范围参考，严禁直接使用原题）
{question_list}

## 重要约束
- 绝对不要直接提问题库中的原题
- 基于题库涉及的知识点，从不同角度、不同深度、不同场景出全新的题目
- 问题表述要与原题有明显区别，可以换场景、换数据、换提问方式
- 【重要】如果简历中没有某项技术，不要问相关问题！

## 当前面试进度
{interview_progress}

请以面试官身份提出下一个问题。只输出你的提问内容，不要加额外说明。"""

# ==================== 评分 Prompt ====================
SCORING_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """你是一位后端技术面试评审专家。请根据以下面试对话记录，对候选人进行多维度评分，并生成逐题回顾。

评分维度（每项 0-10 分）：
1. **技术深度**：后端基础知识、框架原理的掌握程度
2. **代码能力**：算法题、代码实操的表现
3. **表达能力**：回答的逻辑性、条理性
4. **系统设计**：架构设计思维和方案合理性
5. **综合素质**：学习能力、沟通协作、问题解决

逐题回顾要求（question_reviews）：
对面试中每一个面试官的问题，都要给出：
- question: 面试官的问题
- candidate_answer: 候选人的回答
- standard_answer: 参考答案要点（全面、准确的标准回答）
- error_correction: 错误纠正（指出候选人回答中的错误、遗漏或不足；如果回答很好则为空字符串）
- is_correct: 回答是否基本正确（true/false）

注意：自我介绍类的问题也需要回顾，standard_answer 可以给出一个优秀自我介绍应包含的要点。

输出要求：
- scores: 每个维度的得分和评语
- overall_score: 综合得分（加权平均，0-100）
- strengths: 亮点表现（2-3条）
- improvements: 改进建议（2-3条）
- summary: 面试总结（1段话）
- question_reviews: 逐题回顾列表（按面试顺序排列，包含所有问题）"""),
    ("human", """请评估以下面试记录：

## 岗位信息
{job_info}

## 面试对话记录
{dialogue}"""),
])


# ==================== 面试会话管理 ====================
class InterviewSession:
    """模拟面试会话"""

    def __init__(self, job_profile: JobProfile, question_bank: Optional[QuestionBank] = None, resume: str = ""):
        self.job_profile = job_profile
        self.question_bank = question_bank
        self.resume = resume
        self.messages: List[dict] = []  # {"role": "interviewer/candidate", "content": "..."}
        self.stage = 0  # 面试阶段: 0=开始, 1=自我介绍, 2=项目深挖, 3=技术深挖, 4=综合考察, 5=结束
        self.stage_names = ["开场", "自我介绍", "项目深挖", "技术深挖", "综合考察", "面试结束"]
        self.finished = False

    def _build_job_info(self) -> str:
        return json.dumps(self.job_profile.model_dump(), ensure_ascii=False, indent=2)

    def _build_question_list(self) -> str:
        if not self.question_bank or not self.question_bank.questions:
            return "（无预设题库，请根据岗位要求和候选人简历自由动态出题，确保题目多样化、有深度）"
        lines = []
        for i, q in enumerate(self.question_bank.questions, 1):
            lines.append(f"{i}. [{q.category}][{q.difficulty}] {q.question}")
        return "\n".join(lines)

    def _build_resume_text(self) -> str:
        if not self.resume or not self.resume.strip():
            return "（候选人未提供简历，请基于岗位要求和通用后端技术知识进行面试，但请注意不要问过于具体的项目经历问题）"
        return self.resume

    def _build_progress(self) -> str:
        asked = len([m for m in self.messages if m["role"] == "interviewer"])
        return f"当前阶段: {self.stage_names[min(self.stage, 5)]}，已提问 {asked} 个问题，总共约 8-10 个问题"

    def _build_dialogue(self) -> str:
        lines = []
        for m in self.messages:
            role = "面试官" if m["role"] == "interviewer" else "候选人"
            lines.append(f"【{role}】{m['content']}")
        return "\n\n".join(lines)

    async def start(self) -> str:
        """开始面试，返回面试官的第一个问题"""
        llm = get_llm()
        self.stage = 1

        prompt = INTERVIEWER_SYSTEM_PROMPT.format(
            job_info=self._build_job_info(),
            question_list=self._build_question_list(),
            resume_text=self._build_resume_text(),
            interview_progress=self._build_progress(),
        )

        response = await llm.ainvoke([
            SystemMessage(content=prompt),
            HumanMessage(content="请开始面试，先让候选人做自我介绍。"),
        ])

        question = response.content
        self.messages.append({"role": "interviewer", "content": question})
        return question

    async def chat(self, candidate_answer: str) -> str:
        """
        候选人回答后，返回面试官的下一个问题

        Args:
            candidate_answer: 候选人的回答

        Returns:
            面试官的下一个问题或结束语
        """
        self.messages.append({"role": "candidate", "content": candidate_answer})
        self.stage = min(self.stage + 1, 5)

        llm = get_llm()

        # 判断是否该结束（面试官问了 10 个问题后结束）
        interviewer_count = len([m for m in self.messages if m["role"] == "interviewer"])
        if interviewer_count >= 10:
            self.finished = True
            return "面试结束，感谢你的时间！请稍等，我正在生成你的面试评估报告。"

        prompt = INTERVIEWER_SYSTEM_PROMPT.format(
            job_info=self._build_job_info(),
            question_list=self._build_question_list(),
            resume_text=self._build_resume_text(),
            interview_progress=self._build_progress(),
        )

        # 构建对话历史
        chat_messages = [SystemMessage(content=prompt)]
        for m in self.messages:
            if m["role"] == "interviewer":
                chat_messages.append(HumanMessage(content=f"(面试官之前的提问: {m['content']})"))
            else:
                chat_messages.append(HumanMessage(content=f"(候选人的回答: {m['content']})"))

        chat_messages.append(HumanMessage(content="请根据候选人的回答，追问或提出下一个问题。"))

        response = await llm.ainvoke(chat_messages)
        question = response.content
        self.messages.append({"role": "interviewer", "content": question})
        return question

    async def generate_report(self) -> InterviewReport:
        """生成面试评分报告"""
        llm = get_llm()
        structured_llm = llm.with_structured_output(InterviewReport)
        chain = SCORING_PROMPT | structured_llm

        result = await chain.ainvoke({
            "job_info": self._build_job_info(),
            "dialogue": self._build_dialogue(),
        })
        return result

    def get_dialogue(self) -> List[dict]:
        """获取完整对话记录"""
        return self.messages


# ==================== 全局会话管理（Demo 用，生产环境应放 Redis） ====================
_sessions: dict[str, InterviewSession] = {}


def create_session(session_id: str, job_profile: JobProfile, question_bank: Optional[QuestionBank] = None, resume: str = "") -> InterviewSession:
    """创建面试会话"""
    session = InterviewSession(job_profile, question_bank, resume)
    _sessions[session_id] = session
    return session


def get_session(session_id: str) -> Optional[InterviewSession]:
    """获取面试会话"""
    return _sessions.get(session_id)


if __name__ == "__main__":
    import asyncio

    async def test():
        from agents.job_matcher import match_job
        from agents.question_bank import generate_questions

        jd = """岗位：Java后端开发
1. 熟悉Spring Boot、MyBatis
2. 熟悉MySQL、Redis
3. 3年经验"""

        print("1. 解析JD...")
        profile = await match_job(jd)
        print(f"   岗位: {profile.position}")

        print("2. 生成题库...")
        bank = await generate_questions(profile)
        print(f"   题目数: {len(bank.questions)}")

        print("3. 开始模拟面试...")
        session_id = "test_001"
        session = create_session(session_id, profile, bank)

        q = await session.start()
        print(f"\n面试官: {q}\n")

        # 模拟回答
        answers = [
            "面试官好，我叫张三，XX大学计算机专业毕业，有3年Java后端开发经验，主要技术栈是Spring Boot + MySQL + Redis。",
            "HashMap底层是数组+链表+红黑树。put时先计算hash值定位数组下标，冲突时用链表存储，链表长度超过8转红黑树。扩容时容量翻倍，rehash。",
            "两数之和可以用哈希表一次遍历解决，时间复杂度O(n)。",
            "短链系统可以用发号器生成唯一ID，转成62进制短码存储，用Redis缓存热点短链，数据库用MySQL分库分表。",
            "电商项目中我负责订单模块，用Redis分布式锁解决并发下单问题，用RocketMQ做异步削峰。",
        ]

        for ans in answers:
            print(f"候选人: {ans}\n")
            q = await session.chat(ans)
            print(f"面试官: {q}\n")
            if session.finished:
                break

        if session.finished:
            print("4. 生成评分报告...")
            report = await session.generate_report()
            print(f"\n综合得分: {report.overall_score}")
            for s in report.scores:
                print(f"  {s.dimension}: {s.score}分 - {s.comment}")
            print(f"\n亮点: {report.strengths}")
            print(f"建议: {report.improvements}")
            print(f"\n总结: {report.summary}")

    asyncio.run(test())
