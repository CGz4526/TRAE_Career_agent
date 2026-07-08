import axios from 'axios'
import { ElMessage } from 'element-plus'

const TOKEN_KEY = 'career-agent-token'

/**
 * axios 实例
 * - baseURL 留空：通过 vite dev server 的 proxy 转发
 *   /agent → http://localhost:8000 (Python AI 服务)
 *   /api   → http://localhost:8080 (Java 后端)
 * - 超时 120 秒：AI 推理耗时较长
 */
const request = axios.create({
  baseURL: '',
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器：自动携带 JWT Token
request.interceptors.request.use(
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
request.interceptors.response.use(
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

export default request
