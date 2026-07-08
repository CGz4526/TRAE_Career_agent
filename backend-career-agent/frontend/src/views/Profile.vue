<template>
  <div class="profile-page">
    <div class="profile-container">
      <div class="profile-header fx-glass fx-glass-highlight">
        <div class="avatar-section">
          <div class="avatar-wrapper" @click="triggerAvatarUpload">
            <el-avatar :size="96" class="main-avatar" :src="authStore.avatar || ''">
              {{ authStore.displayName?.charAt(0).toUpperCase() || 'U' }}
            </el-avatar>
            <div class="avatar-overlay">
              <el-icon :size="24"><Camera /></el-icon>
              <span>更换头像</span>
            </div>
          </div>
          <input
            ref="avatarInputRef"
            type="file"
            accept="image/*"
            style="display: none"
            @change="handleAvatarChange"
          />
        </div>
        <div class="user-info">
          <h2 class="user-name font-heading">{{ authStore.displayName || '用户' }}</h2>
          <p class="user-account">账号：{{ authStore.username }}</p>
        </div>
      </div>

      <div class="profile-card fx-glass">
        <div class="card-title-row">
          <span class="title-bar"></span>
          <span class="card-title font-heading">基本资料</span>
        </div>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="100px"
          class="profile-form"
        >
          <el-form-item label="昵称" prop="nickname">
            <el-input
              v-model="form.nickname"
              placeholder="不填则默认显示账号名"
              maxlength="20"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="账号">
            <el-input :value="authStore.username" disabled />
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              :loading="saving"
              @click="handleSave"
            >
              保存修改
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <div class="profile-card fx-glass">
        <div class="card-title-row">
          <span class="title-bar"></span>
          <span class="card-title font-heading">账号安全</span>
        </div>
        <div class="security-tip">
          <el-icon class="tip-icon"><InfoFilled /></el-icon>
          <span>当前为本地账号系统，密码等敏感信息暂不支持网页端修改</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Camera, InfoFilled } from '@element-plus/icons-vue'
import { authApi } from '@/api/auth'

const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const avatarInputRef = ref<HTMLInputElement>()
const saving = ref(false)

const form = reactive({
  nickname: ''
})

const rules: FormRules = {
  nickname: [
    { max: 20, message: '昵称最多 20 个字符', trigger: 'blur' },
    {
      validator: async (_rule, value, callback) => {
        if (!value || value.trim() === '') {
          callback()
          return
        }
        try {
          const res: any = await authApi.checkNickname(value.trim())
          const available = res?.data ?? res
          if (available) {
            callback()
          } else {
            callback(new Error('该昵称已被使用'))
          }
        } catch {
          callback(new Error('昵称校验失败，请重试'))
        }
      },
      trigger: 'blur'
    }
  ]
}

function triggerAvatarUpload() {
  avatarInputRef.value?.click()
}

async function handleAvatarChange(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  if (!file.type.startsWith('image/')) {
    ElMessage.error('请选择图片文件')
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过 5MB')
    return
  }

  try {
    saving.value = true
    await authStore.updateAvatar(file)
    ElMessage.success('头像更新成功')
  } catch {
    ElMessage.error('头像上传失败')
  } finally {
    saving.value = false
    input.value = ''
  }
}

async function handleSave() {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  try {
    saving.value = true
    await authStore.updateNickname(form.nickname.trim())
    ElMessage.success('保存成功')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  form.nickname = authStore.nickname
  if (authStore.isLoggedIn && !authStore.nickname) {
    await authStore.fetchProfile()
    form.nickname = authStore.nickname
  }
})
</script>

<style scoped>
.profile-page {
  padding: var(--bc-space-6);
  max-width: 800px;
  margin: 0 auto;
}

.profile-container {
  display: flex;
  flex-direction: column;
  gap: var(--bc-space-5);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: var(--bc-space-6);
  padding: var(--bc-space-8);
  border-radius: var(--bc-radius-lg);
  border: 1px solid var(--bc-border);
  position: relative;
  overflow: hidden;
}

.profile-header::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -20%;
  width: 400px;
  height: 400px;
  background: radial-gradient(
    circle,
    var(--bc-violet-soft) 0%,
    transparent 60%
  );
  filter: blur(30px);
  pointer-events: none;
  opacity: 0.6;
}

.avatar-section {
  position: relative;
  z-index: 1;
}

.avatar-wrapper {
  position: relative;
  cursor: pointer;
  border-radius: 50%;
}

.main-avatar {
  border: 3px solid rgba(196, 181, 253, 0.3);
  box-shadow: 0 0 20px var(--bc-violet-soft);
  font-size: 36px;
  font-weight: 600;
  background: linear-gradient(135deg, #1a1a2e, #16213e);
  color: #e0e7ff;
}

.avatar-overlay {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  opacity: 0;
  transition: opacity 250ms var(--bc-ease);
  color: #fff;
  font-size: 11px;
}

.avatar-wrapper:hover .avatar-overlay {
  opacity: 1;
}

.user-info {
  flex: 1;
  z-index: 1;
}

.user-name {
  font-size: 28px;
  font-weight: 700;
  color: var(--bc-text);
  margin: 0 0 8px 0;
  letter-spacing: 0.5px;
}

.user-account {
  color: var(--bc-text-soft);
  font-size: var(--bc-font-size-sm);
  margin: 0;
}

.profile-card {
  padding: var(--bc-space-6);
  border-radius: var(--bc-radius-lg);
  border: 1px solid var(--bc-border);
}

.card-title-row {
  display: flex;
  align-items: center;
  gap: var(--bc-space-3);
  margin-bottom: var(--bc-space-6);
}

.title-bar {
  width: 4px;
  height: 28px;
  border-radius: 2px;
  background: linear-gradient(180deg, #ffffff 0%, #c4b5fd 100%);
  flex-shrink: 0;
  box-shadow: 0 0 10px var(--bc-violet-soft);
}

.card-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--bc-text);
}

.profile-form {
  max-width: 500px;
}

.security-tip {
  display: flex;
  align-items: flex-start;
  gap: var(--bc-space-3);
  padding: var(--bc-space-4);
  background: rgba(255, 255, 255, 0.03);
  border-radius: var(--bc-radius-md);
  border: 1px solid var(--bc-border-soft);
  color: var(--bc-text-soft);
  font-size: var(--bc-font-size-sm);
  line-height: 1.6;
}

.tip-icon {
  color: #c4b5fd;
  flex-shrink: 0;
  margin-top: 2px;
}

:deep(.el-input__wrapper) {
  background: var(--bc-bg-soft);
  box-shadow: 0 0 0 1px var(--bc-border) inset;
  border-radius: var(--bc-radius-sm);
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px rgba(196, 181, 253, 0.5) inset,
    0 0 15px var(--bc-violet-soft);
}

:deep(.el-input__inner) {
  color: var(--bc-text);
}

.profile-form :deep(.el-input.is-disabled .el-input__wrapper) {
  background: var(--bc-bg-elev);
  opacity: 0.9;
}

.profile-form :deep(.el-input.is-disabled .el-input__inner) {
  color: var(--bc-text-soft) !important;
  -webkit-text-fill-color: var(--bc-text-soft) !important;
}

.profile-form :deep(.el-button--primary) {
  background: linear-gradient(135deg, #ffffff 0%, #c4b5fd 100%) !important;
  color: #18181b !important;
  border: none !important;
  font-weight: 600 !important;
}

.profile-form :deep(.el-button--primary:hover) {
  background: linear-gradient(135deg, #ffffff 0%, #a78bfa 100%) !important;
  box-shadow: 0 4px 20px var(--bc-violet-glow);
  color: #18181b !important;
}
</style>
