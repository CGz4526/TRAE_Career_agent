<template>
  <div class="login-page">
    <LoginBg />
    
    <!-- 装饰性光效元素 -->
    <div class="ambient-orbs">
      <div class="orb orb-1"></div>
      <div class="orb orb-2"></div>
      <div class="orb orb-3"></div>
      <div class="orb orb-4"></div>
    </div>
    
    <!-- 顶部装饰线 -->
    <div class="top-line"></div>
    <div class="top-line top-line-2"></div>
    
    <div class="login-card fx-glass fx-noise">
      <!-- Logo 区 -->
      <div class="logo-area">
        <div class="logo-icon-wrap">
          <!-- 使用与 Dashboard MainLayout 完全一致的六边形图标 -->
          <svg class="logo-svg" viewBox="0 0 32 32" fill="none">
            <defs>
              <linearGradient id="loginLogoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#ffffff" />
                <stop offset="50%" stop-color="#a1a1aa" />
                <stop offset="100%" stop-color="#52525b" />
              </linearGradient>
            </defs>
            <path d="M16 2 L28 9 L28 23 L16 30 L4 23 L4 9 Z" stroke="url(#loginLogoGrad)" stroke-width="1.5" fill="rgba(255,255,255,0.03)" />
            <circle cx="16" cy="16" r="5" stroke="url(#loginLogoGrad)" stroke-width="1.5" fill="none" />
            <circle cx="16" cy="16" r="2" fill="#ffffff" />
          </svg>
          <!-- 光晕效果 -->
          <div class="logo-glow"></div>
          <div class="logo-ring"></div>
        </div>
        <h1 class="logo-title">后端职途</h1>
        <p class="logo-subtitle">多 Agent 求职辅助系统</p>
      </div>

      <!-- 表单切换 -->
      <el-tabs v-model="activeTab" class="login-tabs" stretch>
        <el-tab-pane label="登录" name="login">
          <el-form ref="loginFormRef" :model="loginForm" :rules="loginRules" @submit.prevent="handleLogin">
            <el-form-item prop="username">
              <el-input
                v-model="loginForm.username"
                placeholder="用户名"
                size="large"
                :prefix-icon="User"
              />
            </el-form-item>
            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="密码"
                size="large"
                :prefix-icon="Lock"
                show-password
                @keyup.enter="handleLogin"
              />
            </el-form-item>
            <el-button
              type="primary"
              size="large"
              class="submit-btn"
              :loading="loading"
              @click="handleLogin"
            >
              登 录
            </el-button>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="注册" name="register">
          <el-form ref="regFormRef" :model="regForm" :rules="regRules" @submit.prevent="handleRegister">
            <el-form-item prop="username">
              <el-input
                v-model="regForm.username"
                placeholder="设置用户名（3-20位）"
                size="large"
                :prefix-icon="User"
              />
            </el-form-item>
            <el-form-item prop="password">
              <el-input
                v-model="regForm.password"
                type="password"
                placeholder="设置密码（6-20位）"
                size="large"
                :prefix-icon="Lock"
                show-password
              />
            </el-form-item>
            <el-form-item prop="confirmPassword">
              <el-input
                v-model="regForm.confirmPassword"
                type="password"
                placeholder="确认密码"
                size="large"
                :prefix-icon="Lock"
                show-password
                @keyup.enter="handleRegister"
              />
            </el-form-item>
            <el-button
              type="primary"
              size="large"
              class="submit-btn"
              :loading="loading"
              @click="handleRegister"
            >
              注 册
            </el-button>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <!-- 游客访问 -->
      <div class="guest-entry">
        <el-divider>或</el-divider>
        <el-button text type="primary" class="guest-btn" @click="goGuest">游客模式体验 →</el-button>
      </div>
    </div>

    <!-- 底部装饰 -->
    <div class="bottom-glow"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import LoginBg from '@/components/effects/LoginBg.vue'

const router = useRouter()
const authStore = useAuthStore()

const activeTab = ref('login')
const loading = ref(false)

const loginFormRef = ref<FormInstance>()
const regFormRef = ref<FormInstance>()

const loginForm = reactive({
  username: '',
  password: '',
})

const regForm = reactive({
  username: '',
  password: '',
  confirmPassword: '',
})

const loginRules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const regRules: FormRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '长度 3-20 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 20, message: '长度 6-20 个字符', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value !== regForm.password) callback(new Error('两次密码不一致'))
        else callback()
      },
      trigger: 'blur',
    },
  ],
}

async function handleLogin() {
  const valid = await loginFormRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await authStore.login(loginForm.username, loginForm.password)
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } catch {
    // 错误已在拦截器中提示
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  const valid = await regFormRef.value?.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await authStore.register(regForm.username, regForm.password)
    ElMessage.success('注册成功，正在自动登录...')
    // 注册成功后自动登录
    await authStore.login(regForm.username, regForm.password)
    router.push('/dashboard')
  } catch {
    // 错误已在拦截器中提示
  } finally {
    loading.value = false
  }
}

function goGuest() {
  localStorage.removeItem('career-agent-token')
  localStorage.removeItem('career-agent-user')
  localStorage.setItem('career-agent-guest', 'true')
  router.push('/dashboard')
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #000000;
  position: relative;
  overflow: hidden;
}

/* ===================== 环境光球 ===================== */
.ambient-orbs {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 1;
  overflow: hidden;
}

.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
  animation: orbFloat 25s ease-in-out infinite;
}

.orb-1 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%);
  top: -150px;
  left: -100px;
  animation-delay: 0s;
}

.orb-2 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(200,200,220,0.12) 0%, transparent 70%);
  bottom: -100px;
  right: -100px;
  animation-delay: -7s;
}

.orb-3 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
  top: 40%;
  right: 15%;
  animation-delay: -14s;
}

.orb-4 {
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(180,180,200,0.08) 0%, transparent 70%);
  top: 20%;
  left: 20%;
  animation-delay: -21s;
}

@keyframes orbFloat {
  0%, 100% { transform: translate(0, 0) scale(1); }
  20% { transform: translate(40px, -30px) scale(1.08); }
  40% { transform: translate(-20px, 20px) scale(0.95); }
  60% { transform: translate(30px, 40px) scale(1.05); }
  80% { transform: translate(-30px, -20px) scale(1.02); }
}

/* ===================== 顶部装饰线 ===================== */
.top-line {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255,255,255,0.3) 20%,
    rgba(255,255,255,0.5) 50%,
    rgba(255,255,255,0.3) 80%,
    transparent 100%
  );
  z-index: 5;
  animation: lineShimmer 4s ease-in-out infinite;
}

.top-line-2 {
  top: auto;
  bottom: 0;
  animation-delay: -2s;
}

@keyframes lineShimmer {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.7; }
}

/* ===================== 登录卡片 - 高级毛玻璃 ===================== */
.login-card {
  width: 440px;
  max-width: 92vw;
  background: rgba(8, 8, 10, 0.75);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 28px;
  padding: 52px 48px;
  z-index: 10;
  position: relative;
  box-shadow:
    0 30px 80px -12px rgba(0, 0, 0, 0.7),
    0 0 0 1px rgba(255, 255, 255, 0.05) inset,
    0 0 150px rgba(255, 255, 255, 0.03);
}

/* 卡片外层发光边框 */
.login-card::before {
  content: '';
  position: absolute;
  inset: -1px;
  border-radius: 29px;
  background: linear-gradient(
    135deg,
    rgba(255, 255, 255, 0.2) 0%,
    transparent 30%,
    transparent 70%,
    rgba(255, 255, 255, 0.1) 100%
  );
  pointer-events: none;
  z-index: -1;
}

/* 卡片顶部高光 */
.login-card::after {
  content: '';
  position: absolute;
  top: 0;
  left: 15%;
  right: 15%;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.5),
    rgba(255, 255, 255, 0.8),
    rgba(255, 255, 255, 0.5),
    transparent
  );
  filter: blur(1px);
  pointer-events: none;
}

/* ===================== Logo 区域 ===================== */
.logo-area {
  text-align: center;
  margin-bottom: 44px;
}

.logo-icon-wrap {
  width: 96px;
  height: 96px;
  margin: 0 auto 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 26px;
  position: relative;
  box-shadow:
    0 0 60px rgba(255, 255, 255, 0.08),
    inset 0 0 30px rgba(255, 255, 255, 0.02);
}

.logo-svg {
  width: 52px;
  height: 52px;
  position: relative;
  z-index: 2;
}

/* Logo 光晕 */
.logo-glow {
  position: absolute;
  inset: -10px;
  background: radial-gradient(
    circle at center,
    rgba(255, 255, 255, 0.15) 0%,
    transparent 60%
  );
  border-radius: 26px;
  animation: pulse 4s ease-in-out infinite;
  z-index: 1;
}

/* Logo 外环 */
.logo-ring {
  position: absolute;
  inset: -6px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 32px;
  animation: ringPulse 4s ease-in-out infinite;
  animation-delay: -2s;
}

@keyframes pulse {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.08); }
}

@keyframes ringPulse {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.05); }
}

.logo-title {
  font-size: 36px;
  font-weight: 700;
  margin: 0 0 10px 0;
  letter-spacing: 3px;
  color: #ffffff;
  text-shadow: 0 0 30px rgba(255, 255, 255, 0.3);
}

.logo-subtitle {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.45);
  margin: 0;
  letter-spacing: 2px;
  font-weight: 400;
}

/* ===================== Tab 样式 ===================== */
.login-tabs :deep(.el-tabs__header) {
  margin-bottom: 36px;
}

.login-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.login-tabs :deep(.el-tabs__item) {
  color: rgba(255, 255, 255, 0.35);
  font-size: 16px;
  font-weight: 500;
  transition: all 0.3s ease;
  padding: 0 24px;
  letter-spacing: 1px;
}

.login-tabs :deep(.el-tabs__item:hover) {
  color: rgba(255, 255, 255, 0.6);
}

.login-tabs :deep(.el-tabs__item.is-active) {
  color: #ffffff;
  font-weight: 600;
}

.login-tabs :deep(.el-tabs__active-bar) {
  background: linear-gradient(90deg, #ffffff, rgba(255,255,255,0.7));
  height: 2px;
  border-radius: 1px;
  box-shadow: 0 0 12px rgba(255, 255, 255, 0.5);
}

/* ===================== 输入框 - 更圆润 ===================== */
.login-tabs :deep(.el-input__wrapper) {
  background: rgba(15, 15, 18, 0.8) !important;
  backdrop-filter: blur(16px);
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.06) inset !important;
  border-radius: 16px !important;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
  padding: 5px 18px;
}

.login-tabs :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.12) inset !important;
  background: rgba(20, 20, 24, 0.85) !important;
}

.login-tabs :deep(.el-input__wrapper.is-focus) {
  box-shadow:
    0 0 0 1px rgba(255, 255, 255, 0.25) inset,
    0 0 25px rgba(255, 255, 255, 0.08) !important;
  background: rgba(25, 25, 30, 0.9) !important;
}

.login-tabs :deep(.el-input__inner) {
  color: #fafafa !important;
  font-size: 15px;
  letter-spacing: 0.5px;
}

.login-tabs :deep(.el-input__inner::placeholder) {
  color: rgba(255, 255, 255, 0.25) !important;
}

.login-tabs :deep(.el-input__prefix .el-icon) {
  color: rgba(255, 255, 255, 0.35) !important;
  transition: color 0.3s ease;
  font-size: 18px;
}

.login-tabs :deep(.el-input__wrapper.is-focus .el-input__prefix .el-icon) {
  color: rgba(255, 255, 255, 0.7) !important;
}

/* ===================== 表单项 ===================== */
.login-tabs :deep(.el-form-item) {
  margin-bottom: 22px;
}

/* 修复浏览器自动填充背景色 */
.login-tabs :deep(.el-input__inner:-webkit-autofill) {
  -webkit-box-shadow: 0 0 0 1000px rgba(15, 15, 18, 0.95) inset !important;
  -webkit-text-fill-color: #fafafa !important;
  caret-color: #fafafa;
  transition: background-color 5000s ease-in-out 0s;
}

/* ===================== 提交按钮 - 圆润高级 ===================== */
.submit-btn {
  width: 100%;
  margin-top: 16px;
  background: linear-gradient(
    135deg,
    #ffffff 0%,
    #f0f0f0 50%,
    #e8e8e8 100%
  ) !important;
  color: #0a0a0c !important;
  border: none;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 5px;
  border-radius: 18px;
  height: 54px;
  box-shadow:
    0 6px 25px rgba(255, 255, 255, 0.25),
    0 0 0 1px rgba(255, 255, 255, 0.15) inset,
    0 2px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

/* 按钮光泽扫过效果 */
.submit-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(255, 255, 255, 0.4) 50%,
    transparent 100%
  );
  transition: left 0.6s ease;
}

.submit-btn:hover::before {
  left: 100%;
}

.submit-btn:hover {
  background: linear-gradient(
    135deg,
    #ffffff 0%,
    #fafafa 50%,
    #f5f5f5 100%
  ) !important;
  box-shadow:
    0 10px 40px rgba(255, 255, 255, 0.35),
    0 0 0 1px rgba(255, 255, 255, 0.2) inset,
    0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-3px);
}

.submit-btn:active {
  transform: translateY(-1px);
  box-shadow:
    0 4px 15px rgba(255, 255, 255, 0.2),
    0 0 0 1px rgba(255, 255, 255, 0.15) inset;
}

.submit-btn :deep(.el-icon) {
  color: #0a0a0c !important;
}

/* ===================== 游客入口 ===================== */
.guest-entry {
  margin-top: 28px;
  text-align: center;
}

.guest-entry :deep(.el-divider) {
  margin: 0 0 18px 0;
  border-color: rgba(255, 255, 255, 0.08);
}

.guest-entry :deep(.el-divider__text) {
  background: transparent;
  color: rgba(255, 255, 255, 0.3);
  font-size: 12px;
  letter-spacing: 1px;
}

.guest-btn {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  transition: all 0.3s ease;
  padding: 10px 20px;
  border-radius: 12px;
  letter-spacing: 0.5px;
}

.guest-btn:hover {
  color: #ffffff;
  background: rgba(255, 255, 255, 0.08);
  text-shadow: 0 0 20px rgba(255, 255, 255, 0.3);
}

/* ===================== 底部装饰 ===================== */
.bottom-glow {
  position: fixed;
  bottom: -200px;
  left: 50%;
  transform: translateX(-50%);
  width: 800px;
  height: 400px;
  background: radial-gradient(
    ellipse at center,
    rgba(255, 255, 255, 0.06) 0%,
    transparent 60%
  );
  pointer-events: none;
  z-index: 1;
  filter: blur(60px);
}

/* ===================== 响应式 ===================== */
@media (max-width: 480px) {
  .login-card {
    padding: 40px 32px;
    border-radius: 24px;
  }

  .logo-icon-wrap {
    width: 80px;
    height: 80px;
  }

  .logo-svg {
    width: 44px;
    height: 44px;
  }

  .logo-title {
    font-size: 28px;
  }
  
  .submit-btn {
    border-radius: 16px;
    height: 50px;
  }
}
</style>
