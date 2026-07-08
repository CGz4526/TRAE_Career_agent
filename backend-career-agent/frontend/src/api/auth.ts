import request from './client'

export interface UserProfile {
  userId: number
  username: string
  nickname: string
  avatar?: string
  email?: string
  techStack?: string
  createdAt: string
}

export const authApi = {
  register(username: string, password: string) {
    return request.post('/api/auth/register', { username, password })
  },

  login(username: string, password: string) {
    return request.post('/api/auth/login', { username, password })
  },

  getProfile() {
    return request.get<UserProfile>('/api/user/profile')
  },

  updateProfile(data: { nickname?: string }) {
    return request.put<UserProfile>('/api/user/profile', data)
  },

  checkNickname(nickname: string) {
    return request.get<boolean>('/api/user/check-nickname', { params: { nickname } })
  },

  uploadAvatar(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    return request.post<UserProfile>('/api/user/avatar', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
}
