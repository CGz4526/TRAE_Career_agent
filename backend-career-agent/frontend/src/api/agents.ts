import request from './client'
import type { JobProfile } from '@/stores/app'

/**
 * Agent API 封装（对接 Python AI 服务 http://localhost:8000）
 * 所有路径以 /agent 开头，经 vite proxy 转发。
 */

/** 1. 岗位匹配：解析 JD 得到岗位需求画像 */
export function matchJob(jd_text: string) {
  return request.post<any>('/agent/match-job', { jd_text })
}

/** 2. 项目分析：解析简历项目、提取技术栈、给出建议、推荐新项目 */
export function projectAnalysis(resume_text: string, job_profile: JobProfile) {
  return request.post<any>('/agent/project-analysis', { resume_text, job_profile })
}

/** 3. 题库生成：根据岗位画像生成面试题库 */
export function generateQuestions(job_profile: JobProfile, resume: string = '') {
  return request.post<any>('/agent/generate-questions', { job_profile, resume })
}

/** 3.5 简历文件解析：支持 PDF/图片 OCR */
export function parseResumeFile(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post<any>('/agent/parse-resume-file', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000,
  })
}

/** 3.6 JD 图片解析：支持图片格式 JD 的 OCR 文字提取 */
export function parseJDImage(file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return request.post<any>('/agent/parse-jd-image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000,
  })
}

/** 4. 项目深挖：根据项目描述生成讲述与问答 */
export function projectStory(project_desc: string) {
  return request.post<any>('/agent/project-story', { project_desc })
}

/** 5. 启动模拟面试 */
export function interviewStart(
  job_profile: JobProfile,
  question_bank?: any,
  resume?: string
) {
  return request.post<any>('/agent/interview/start', {
    job_profile,
    question_bank,
    resume
  })
}

/** 6. 模拟面试对话 */
export function interviewChat(session_id: string, answer: string) {
  return request.post<any>('/agent/interview/chat', { session_id, answer })
}

/** 7. 生成面试报告 */
export function interviewReport(session_id: string) {
  return request.get<any>(`/agent/interview/${session_id}/report`)
}

/** 8. 一键全流程：JD -> 画像 -> 简历优化 / 项目深挖 */
export function pipeline(
  jd_text: string,
  resume_text?: string,
  project_desc?: string
) {
  return request.post<any>('/agent/pipeline', {
    jd_text,
    resume_text,
    project_desc
  })
}

/** 9. 获取预设角色卡列表（8 个通用技术岗位） */
export function getRoleCards() {
  return request.get<any>('/agent/role-cards')
}

/** 10. 获取指定角色卡详情 */
export function getRoleCardDetail(cardId: string) {
  return request.get<any>(`/agent/role-cards/${cardId}`)
}

/** 11. 技能差距分析：对比用户技能与岗位要求 */
export function skillGapAnalysis(user_skills: string[], job_profile: JobProfile) {
  return request.post<any>('/agent/skill-gap', { user_skills, job_profile })
}
