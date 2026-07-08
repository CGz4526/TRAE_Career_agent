import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, type UserProfile } from '@/api/auth'

const TOKEN_KEY = 'career-agent-token'
const USER_KEY = 'career-agent-user'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string>(localStorage.getItem(TOKEN_KEY) || '')
  const username = ref<string>(localStorage.getItem(USER_KEY) || '')
  const nickname = ref<string>('')
  const avatar = ref<string>('')
  const userId = ref<number | null>(null)

  const isLoggedIn = computed(() => !!token.value)
  const isGuest = computed(() => !token.value && localStorage.getItem('career-agent-guest') === 'true')
  const displayName = computed(() => nickname.value || username.value || (isGuest.value ? '游客' : ''))

  async function login(user: string, password: string) {
    const res: any = await authApi.login(user, password)
    const data = res?.data ?? res
    token.value = data.token
    username.value = data.username
    userId.value = data.userId
    localStorage.setItem(TOKEN_KEY, data.token)
    localStorage.setItem(USER_KEY, data.username)
    localStorage.removeItem('career-agent-guest')
    await fetchProfile()
    return data
  }

  async function register(user: string, password: string) {
    const res: any = await authApi.register(user, password)
    return res
  }

  async function fetchProfile() {
    if (!token.value) return
    try {
      const res: any = await authApi.getProfile()
      const data: UserProfile = res?.data ?? res
      if (data) {
        nickname.value = data.nickname || ''
        avatar.value = data.avatar || ''
        userId.value = data.userId
        if (data.username) {
          username.value = data.username
          localStorage.setItem(USER_KEY, data.username)
        }
      }
    } catch (e) {
      console.warn('获取用户资料失败', e)
    }
  }

  async function updateNickname(newNickname: string) {
    const res: any = await authApi.updateProfile({ nickname: newNickname })
    const data: UserProfile = res?.data ?? res
    if (data) {
      nickname.value = data.nickname || ''
    }
    return data
  }

  async function updateAvatar(file: File) {
    const res: any = await authApi.uploadAvatar(file)
    const data: UserProfile = res?.data ?? res
    if (data) {
      avatar.value = data.avatar || ''
      nickname.value = data.nickname || ''
    }
    return data
  }

  function logout() {
    token.value = ''
    username.value = ''
    nickname.value = ''
    avatar.value = ''
    userId.value = null
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
    localStorage.removeItem('career-agent-guest')
  }

  return {
    token,
    username,
    nickname,
    avatar,
    userId,
    isLoggedIn,
    isGuest,
    displayName,
    login,
    register,
    fetchProfile,
    updateNickname,
    updateAvatar,
    logout,
  }
})
