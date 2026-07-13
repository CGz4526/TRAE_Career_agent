import { apiClient as request } from './client'

export const historyApi = {
  /** 获取简历列表 */
  getResumes() {
    return request.get('/api/resumes')
  },

  /** 获取岗位列表 */
  getJobs() {
    return request.get('/api/jobs')
  },

  /** 获取面试记录列表 */
  getInterviews() {
    return request.get('/api/interviews')
  },

  /** 保存简历 */
  saveResume(data: { title?: string; content: string; optimizedContent?: string }) {
    return request.post('/api/resumes', data)
  },

  /** 保存岗位 JD */
  saveJob(data: { company?: string; position?: string; rawText: string; jobProfile?: any }) {
    return request.post('/api/jobs', data)
  },
}
