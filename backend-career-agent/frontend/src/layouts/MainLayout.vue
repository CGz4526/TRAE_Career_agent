<template>
  <el-container class="layout-root">
    <DarkVeilBg
      :speed="0.8"
      :hue-shift="0"
      :noise-intensity="0.6"
      :scanline-frequency="0.5"
      :scanline-intensity="0.35"
      :warp-amount="0.6"
    />
    <BgDecorations />
    <div class="bg-vignette"></div>
    <el-aside width="240px" class="sidebar fx-glass fx-noise">
      <div class="logo" @click="goTo('/')">
        <div class="logo-icon-wrap">
          <svg class="logo-svg" viewBox="0 0 32 32" fill="none">
            <defs>
              <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#ffffff" />
                <stop offset="50%" stop-color="#a1a1aa" />
                <stop offset="100%" stop-color="#52525b" />
              </linearGradient>
            </defs>
            <path d="M16 2 L28 9 L28 23 L16 30 L4 23 L4 9 Z" stroke="url(#logoGrad)" stroke-width="1.5" fill="rgba(255,255,255,0.03)" />
            <circle cx="16" cy="16" r="5" stroke="url(#logoGrad)" stroke-width="1.5" fill="none" />
            <circle cx="16" cy="16" r="2" fill="#ffffff" />
          </svg>
        </div>
        <div class="logo-text-wrap">
          <span class="logo-text fx-gradient-text font-heading">后端职途</span>
          <span class="logo-sub">CAREER · AGENT</span>
        </div>
      </div>
      
      <el-menu
        :default-active="activeMenu"
        :router="false"
        class="side-menu"
        background-color="transparent"
        text-color="#94a3b8"
        active-text-color="#f1f5f9"
      >
        <el-menu-item
          v-for="item in menuItems"
          :key="item.path"
          :index="item.path"
          @click="goTo(item.path)"
        >
          <el-icon class="menu-icon"><component :is="item.icon" /></el-icon>
          <span class="menu-label">{{ item.title }}</span>
          <span class="menu-active-dot"></span>
        </el-menu-item>
      </el-menu>
      
      <div class="side-footer">
        <span class="status-dot fx-pulse" :class="{ on: backendOnline }"></span>
        <span class="status-text">{{ backendOnline ? 'AI 服务在线' : 'AI 服务离线' }}</span>
      </div>
    </el-aside>

    <el-container>
      <el-header height="64px" class="topbar fx-glass fx-glass-highlight">
        <div class="topbar-title">
          <span class="title-accent"></span>
          <span class="title-text font-heading">{{ appStore.pageTitle }}</span>
        </div>
        <div class="topbar-right">
          <el-dropdown
            v-if="appStore.hasRunningTasks"
            trigger="click"
            :hide-on-click="false"
            class="task-dropdown"
          >
            <div class="task-indicator">
              <el-icon class="task-icon fx-spin"><Loading /></el-icon>
              <span class="task-badge">{{ appStore.runningTasks.length }}</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu class="task-menu">
                <div class="task-menu-header">
                  <span>后台任务</span>
                  <el-button link type="primary" size="small" @click.stop="appStore.clearCompletedTasks">
                    清除已完成
                  </el-button>
                </div>
                <el-dropdown-item
                  v-for="task in appStore.backgroundTasks.slice(0, 5)"
                  :key="task.id"
                  class="task-item"
                  @click.stop
                >
                  <div class="task-item-content">
                    <div class="task-item-title">
                      <el-icon v-if="task.status === 'running'" class="task-status running"><Loading /></el-icon>
                      <el-icon v-else-if="task.status === 'completed'" class="task-status success"><CircleCheckFilled /></el-icon>
                      <el-icon v-else class="task-status failed"><CircleCloseFilled /></el-icon>
                      <span class="task-title-text">{{ task.title }}</span>
                    </div>
                    <div class="task-item-status">
                      <span :class="['task-status-text', task.status]">
                        {{ task.status === 'running' ? '进行中' : task.status === 'completed' ? '已完成' : '失败' }}
                      </span>
                    </div>
                  </div>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
          <div class="topbar-tag">
            <span class="tag-dot"></span>
            <span>多 Agent 求职辅助系统</span>
          </div>
          <el-dropdown @command="handleCommand">
            <div class="user-info cursor-pointer">
              <el-avatar :size="34" class="user-avatar" :src="authStore.avatar || ''">
                {{ authStore.displayName?.charAt(0).toUpperCase() || 'G' }}
              </el-avatar>
              <span class="user-name">{{ authStore.displayName || '未登录' }}</span>
              <el-tag v-if="authStore.isGuest" size="small" type="info" class="guest-tag">游客</el-tag>
              <el-icon class="arrow"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item v-if="!authStore.isGuest" command="profile" :icon="User">
                  <span>个人资料</span>
                </el-dropdown-item>
                <el-dropdown-item command="history" :icon="Clock">
                  <span>历史记录</span>
                </el-dropdown-item>
                <el-dropdown-item v-if="authStore.isGuest" command="login" :icon="User" divided>
                  <span>登录账号</span>
                </el-dropdown-item>
                <el-dropdown-item v-else command="logout" :icon="SwitchButton" divided>
                  <span>退出登录</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <BlobCursor />
        <router-view v-slot="{ Component }">
          <transition name="page" mode="out-in">
            <component :is="Component" :key="route.path" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Odometer,
  Aim,
  Document,
  Reading,
  ChatDotRound,
  Clock,
  ArrowDown,
  SwitchButton,
  Loading,
  CircleCheckFilled,
  CircleCloseFilled,
  User
} from '@element-plus/icons-vue'
import { useAppStore } from '@/stores/app'
import { useAuthStore } from '@/stores/auth'
import request from '@/api/client'
import DarkVeilBg from '@/components/effects/DarkVeilBg.vue'
import BgDecorations from '@/components/effects/BgDecorations.vue'
import BlobCursor from '@/components/effects/BlobCursor.vue'

const route = useRoute()
const router = useRouter()
const appStore = useAppStore()
const authStore = useAuthStore()

const menuItems = [
  { path: '/dashboard', title: '工作台', icon: Odometer },
  { path: '/job-matcher', title: '岗位匹配', icon: Aim },
  { path: '/resume-optimizer', title: '项目分析', icon: Document },
  { path: '/question-bank', title: '题库刷题', icon: Reading },
  { path: '/interview', title: '模拟面试', icon: ChatDotRound },
  { path: '/history', title: '历史记录', icon: Clock }
]

const activeMenu = computed(() => route.path)
const backendOnline = ref(false)

function goTo(path: string) {
  router.push(path)
}

function handleCommand(command: string) {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'history') {
    router.push('/history')
  } else if (command === 'login') {
    authStore.logout()
    router.push('/login')
  } else if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '退出登录', {
      confirmButtonText: '退出',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      authStore.logout()
      ElMessage.success('已退出登录')
      router.push('/login')
    }).catch(() => {})
  }
}

function syncTitle() {
  appStore.setPageTitle((route.meta?.title as string) || '工作台')
}

async function checkBackend() {
  try {
    await request.get('/agent/health', { timeout: 5000 })
    backendOnline.value = true
  } catch {
    backendOnline.value = false
  }
}

onMounted(() => {
  syncTitle()
  checkBackend()
  setInterval(checkBackend, 30000)
  if (authStore.isLoggedIn) {
    authStore.fetchProfile()
  }
})

watch(() => route.path, syncTitle)
</script>

<style scoped>
.layout-root {
  height: 100vh;
  background: #000000;
  position: relative;
  overflow: hidden;
}

.layout-root :deep(.ferrofluid-container) {
  z-index: 0 !important;
}

.layout-root :deep(.el-aside),
.layout-root :deep(.el-header),
.layout-root :deep(.el-main) {
  position: relative;
  z-index: 2;
  background: transparent !important;
}

.bg-vignette {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 1;
  background: 
    radial-gradient(ellipse at 50% 0%, transparent 0%, rgba(0,0,0,0.3) 70%),
    radial-gradient(ellipse at 0% 50%, transparent 0%, rgba(0,0,0,0.2) 50%),
    radial-gradient(ellipse at 100% 50%, transparent 0%, rgba(0,0,0,0.2) 50%);
}

/* ===================== 侧边栏 ===================== */
.sidebar {
  border-right: 1px solid var(--bc-border);
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  z-index: 1;
}

.logo {
  height: 72px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 20px;
  border-bottom: 1px solid var(--bc-border-soft);
  position: relative;
  z-index: 1;
  cursor: pointer;
  transition: background-color 0.2s var(--bc-ease);
}

.logo:hover {
  background: rgba(255, 255, 255, 0.02);
}

.logo-icon-wrap {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--bc-border-strong);
  border-radius: var(--bc-radius-md);
  box-shadow: var(--bc-shadow-inner);
  transition: var(--bc-transition);
  position: relative;
  overflow: hidden;
}

.logo-icon-wrap::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(
    circle at center,
    var(--bc-violet-soft) 0%,
    transparent 60%
  );
  opacity: 0;
  transition: opacity 0.3s ease;
}

.logo-icon-wrap:hover {
  border-color: rgba(196, 181, 253, 0.4);
  box-shadow: 0 0 25px var(--bc-violet-glow), var(--bc-shadow-inner);
}

.logo-icon-wrap:hover::before {
  opacity: 1;
}

.logo-svg {
  width: 26px;
  height: 26px;
}

.logo-text-wrap {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.logo-text {
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.5px;
  line-height: 1;
}

.logo-sub {
  font-size: 9px;
  color: var(--bc-text-muted);
  letter-spacing: 2.5px;
  font-weight: 500;
  text-transform: uppercase;
}

.side-menu {
  border-right: none;
  flex: 1;
  padding: 12px 10px;
  position: relative;
  z-index: 1;
}

.side-menu :deep(.el-menu-item) {
  margin: 2px 0;
  border-radius: var(--bc-radius-sm);
  height: 44px;
  line-height: 44px;
  position: relative;
  transition: all 250ms var(--bc-ease);
  color: var(--bc-text-soft);
  cursor: pointer;
}

.side-menu :deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.04);
  color: var(--bc-text) !important;
  transform: translateX(3px);
}

.side-menu :deep(.el-menu-item:hover) .menu-icon {
  color: rgba(196, 181, 253, 0.8);
  filter: drop-shadow(0 0 4px var(--bc-violet-glow));
}

.side-menu :deep(.el-menu-item.is-active) {
  background: rgba(255, 255, 255, 0.06);
  color: var(--bc-text) !important;
  box-shadow: var(--bc-shadow-inner);
}

.side-menu :deep(.el-menu-item.is-active) .menu-icon {
  color: #c4b5fd;
  filter: drop-shadow(0 0 4px var(--bc-violet-glow));
}

.side-menu :deep(.el-menu-item.is-active)::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: linear-gradient(180deg, #c4b5fd, #8b5cf6);
  border-radius: 0 3px 3px 0;
  box-shadow: 0 0 10px var(--bc-violet-glow);
}

.menu-icon {
  font-size: 17px;
  transition: all 250ms var(--bc-ease);
}

.menu-label {
  font-size: 13.5px;
  font-weight: 500;
  margin-left: 4px;
  letter-spacing: 0.01em;
}

.menu-active-dot {
  position: absolute;
  right: 14px;
  top: 50%;
  transform: translateY(-50%) scale(0);
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #c4b5fd;
  box-shadow: 0 0 8px var(--bc-violet-glow);
  transition: transform 250ms var(--bc-ease-spring);
}

.side-menu :deep(.el-menu-item.is-active) .menu-active-dot {
  transform: translateY(-50%) scale(1);
}

.side-footer {
  padding: 14px 20px;
  border-top: 1px solid var(--bc-border-soft);
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
  z-index: 1;
}

.status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--bc-text-muted);
  transition: all 250ms var(--bc-ease);
  position: relative;
}

.status-dot.on {
  background: #10b981;
  color: #10b981;
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.6), 0 0 16px rgba(16, 185, 129, 0.3);
}

.status-text {
  font-size: 11.5px;
  color: var(--bc-text-muted);
  letter-spacing: 0.3px;
}

/* ===================== 顶部栏 ===================== */
.topbar {
  height: 64px;
  border-bottom: 1px solid var(--bc-border-soft);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  position: relative;
  border-radius: 0;
  border-left: none;
  border-right: none;
  border-top: none;
  z-index: 2;
}

.topbar-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-accent {
  width: 3px;
  height: 18px;
  border-radius: 2px;
  background: linear-gradient(180deg, #c4b5fd, #8b5cf6);
  box-shadow: 0 0 8px var(--bc-violet-glow);
}

.title-text {
  font-size: 16px;
  font-weight: 600;
  color: var(--bc-text);
  letter-spacing: -0.01em;
}

.topbar-right {
  display: flex;
  align-items: center;
  gap: 18px;
}

.task-dropdown :deep(.el-dropdown-menu) {
  padding: 0;
  min-width: 280px;
  background: var(--bc-bg-elev);
  border: 1px solid var(--bc-border);
  border-radius: var(--bc-radius-md);
  box-shadow: var(--bc-shadow-xl);
}

.task-indicator {
  position: relative;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--bc-border-soft);
  cursor: pointer;
  transition: all 0.2s var(--bc-ease);
}

.task-indicator:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: var(--bc-border-glow);
}

.task-icon {
  font-size: 16px;
  color: var(--bc-text-soft);
}

.task-badge {
  position: absolute;
  top: -2px;
  right: -2px;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  background: var(--bc-primary);
  color: #fff;
  font-size: 10px;
  font-weight: 600;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 0 2px var(--bc-bg);
}

.task-menu {
  padding: 0 !important;
}

.task-menu-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--bc-border);
  font-size: 13px;
  font-weight: 600;
  color: var(--bc-text);
}

.task-menu :deep(.el-dropdown-menu__item) {
  padding: 0;
  border-bottom: 1px solid var(--bc-border-soft);
}

.task-menu :deep(.el-dropdown-menu__item:last-child) {
  border-bottom: none;
}

.task-menu :deep(.el-dropdown-menu__item:hover) {
  background: var(--bc-bg-soft);
}

.task-item-content {
  padding: 10px 16px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.task-item-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--bc-text);
  font-weight: 500;
}

.task-status {
  font-size: 14px;
}

.task-status.running {
  color: var(--bc-primary);
}

.task-status.success {
  color: #22c55e;
}

.task-status.failed {
  color: #ef4444;
}

.task-status-text {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
}

.task-status-text.running {
  background: rgba(99, 102, 241, 0.1);
  color: var(--bc-primary);
}

.task-status-text.completed {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.task-status-text.failed {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.fx-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.topbar-tag {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 5px 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--bc-border-soft);
  border-radius: var(--bc-radius-pill);
  font-size: 11.5px;
  color: var(--bc-text-soft);
  letter-spacing: 0.3px;
}

.tag-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #c4b5fd;
  box-shadow: 0 0 8px var(--bc-violet-glow);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 12px 4px 4px;
  border-radius: var(--bc-radius-pill);
  border: 1px solid transparent;
  transition: var(--bc-transition);
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: var(--bc-border-soft);
}

.user-avatar {
  background: linear-gradient(135deg, var(--bc-primary), var(--bc-primary-dark));
  color: #000;
  font-weight: 600;
  font-size: 13px;
  box-shadow: 0 0 0 2px var(--bc-bg-elev), 0 0 0 3px rgba(255, 255, 255, 0.2);
}

.user-name {
  color: var(--bc-text);
  font-size: 13px;
  font-weight: 500;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.guest-tag {
  margin-left: 4px;
  flex-shrink: 0;
}

.arrow {
  color: var(--bc-text-muted);
  font-size: 11px;
  transition: transform 250ms var(--bc-ease);
}

.user-info:hover .arrow {
  transform: rotate(180deg);
  color: var(--bc-text-soft);
}

/* ===================== 主内容区 ===================== */
.main-content {
  background: transparent;
  padding: 0;
  overflow-y: auto;
  position: relative;
  z-index: 1;
}

.page-enter-active,
.page-leave-active {
  transition: opacity 350ms var(--bc-ease-out), transform 350ms var(--bc-ease-out);
}
.page-enter-from {
  opacity: 0;
  transform: translateY(14px);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.cursor-pointer {
  cursor: pointer;
}
</style>
