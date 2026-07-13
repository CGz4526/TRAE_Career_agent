import axios from 'axios'
import { ElMessage } from 'element-plus'

const TOKEN_KEY = 'career-agent-token'

/**
 * 后端地址配置：
 * - 本地开发：VITE_API_BASE / VITE_AGENT_BASE 未设置，baseURL 留空，
 *   由 vite dev server 的 proxy 转发：
 *     /agent → http://localhost:8000 (Python AI 服务)
 *     /api   → http://localhost:8080 (Java 后端)
 * - 生产部署（Vercel + Railway）：由构建环境变量注入真实域名
 *     VITE_API_BASE   → Java 后端地址，如 https://java-xxx.railway.app
 *     VITE_AGENT_BASE → Python AI 服务地址，如 https://py-xxx.railway.app
 */
const API_BASE: string = import.meta.env.VITE_API_BASE || ''
const AGENT_BASE: string = import.meta.env.VITE_AGENT_BASE || ''

/**
 * 创建 axios 实例
 * @param baseURL 后端服务基地址，留空则使用相对路径（走 vite proxy）
 */
function createRequest(baseURL: string) {
  const instance = axios.create({
    baseURL,
    timeout: 120000,
    headers: {
      'Content-Type': 'application/json'
    }
  })

  // 请求拦截器：自动携带 JWT Token
  instance.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem(TOKEN_KEY)
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    },
    (error) => {
      return Promise.reject(error)
    }
  )

  // 响应拦截器：直接返回 data，统一处理错误
  instance.interceptors.response.use(
    (response) => {
      return response.data
    },
    (error) => {
      let msg = '请求失败，请稍后重试'
      if (error.response) {
        const status = error.response.status
        const data = error.response.data

        // 401 未授权：清除 token 并跳转登录
        if (status === 401) {
          localStorage.removeItem(TOKEN_KEY)
          localStorage.removeItem('career-agent-user')
          ElMessage.error('登录已过期，请重新登录')
          setTimeout(() => {
            window.location.href = '/login'
          }, 1500)
          return Promise.reject(error)
        }

        msg = data?.detail || data?.message || data?.error || `服务异常(${status})`
      } else if (error.request) {
        msg = '网络连接失败，请确认后端服务已启动'
      } else {
        msg = error.message || msg
      }
      ElMessage.error(msg)
      return Promise.reject(error)
    }
  )

  return instance
}

// Java 后端（/api 业务接口）
export const apiClient = createRequest(API_BASE)
// Python AI 服务（/agent 智能接口）
export const agentClient = createRequest(AGENT_BASE)

// 默认导出保持兼容
export default apiClient
