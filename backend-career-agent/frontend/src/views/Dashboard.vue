<template>
  <div class="page-container">
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-left">
          <div class="hero-badge">
            <span class="badge-dot"></span>
            <span>多 Agent 协同 · 智能求职</span>
          </div>
          <h1 class="hero-title">
            <span class="hero-title-main font-heading">后端职途</span>
            <span class="title-divider"></span>
            <span class="hero-subtitle-inline font-heading">多 Agent 求职辅助系统</span>
          </h1>
          <p class="hero-desc font-heading">
            面向后端工程师的一站式求职辅助平台，融合岗位解析、项目分析、智能题库与模拟面试四大 AI Agent，
            帮助你精准匹配岗位、打磨简历、备战八股与算法，并在真实对话中检验面试能力。
          </p>
          <div class="hero-tags">
            <span class="hero-tag" v-for="(tag, i) in heroTags" :key="i">
              <span class="tag-icon" :style="{ background: tag.color }"></span>
              {{ tag.label }}
            </span>
          </div>
          <div class="hero-stats">
            <div class="hero-stat-item" v-for="(stat, i) in heroStats" :key="i">
              <div class="stat-value font-heading">
                <CountUpNumber :value="stat.value" :suffix="stat.suffix" :duration="1800" />
              </div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </div>
        </div>
        <div class="hero-right">
          <div class="hero-emblem">
            <svg viewBox="0 0 100 100" fill="none" class="emblem-svg">
              <defs>
                <linearGradient id="embGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#ffffff" stop-opacity="0.6" />
                  <stop offset="100%" stop-color="#52525b" stop-opacity="0.3" />
                </linearGradient>
              </defs>
              <circle cx="50" cy="50" r="42" stroke="url(#embGrad)" stroke-width="0.6" opacity="0.3" />
              <circle cx="50" cy="50" r="32" stroke="url(#embGrad)" stroke-width="0.6" opacity="0.4" />
              <circle cx="50" cy="50" r="22" stroke="url(#embGrad)" stroke-width="0.8" opacity="0.5" />
              <circle cx="50" cy="50" r="6" fill="#ffffff" opacity="0.6" />
              <line x1="50" y1="8" x2="50" y2="20" stroke="#ffffff" stroke-width="0.8" opacity="0.4" />
              <line x1="50" y1="80" x2="50" y2="92" stroke="#ffffff" stroke-width="0.8" opacity="0.4" />
              <line x1="8" y1="50" x2="20" y2="50" stroke="#ffffff" stroke-width="0.8" opacity="0.4" />
              <line x1="80" y1="50" x2="92" y2="50" stroke="#ffffff" stroke-width="0.8" opacity="0.4" />
            </svg>
          </div>
        </div>
      </div>
    </section>

    <section class="role-section" v-if="appStore.activeCard">
      <BorderGlowCard
        :glow-color="'270 50% 80%'"
        :background-color="'rgba(255, 255, 255, 0.02)'"
        :border-radius="16"
        :glow-radius="50"
        :glow-intensity="0.6"
        :cone-spread="30"
        :animated="true"
        :colors="['#ffffff', '#c4b5fd', '#a1a1aa']"
        :fill-opacity="0.2"
        class="role-card-wrapper"
      >
        <div class="role-card-panel">
          <div class="panel-header">
            <span class="panel-title font-heading">当前面试方向</span>
            <IridescentBtn text="切换方向" size="sm" @click="router.push('/role-select')" />
          </div>
          <div class="active-card-info">
            <div class="card-icon" :style="{ background: getRoleColor(appStore.activeCard.icon) }">
              {{ getRoleIcon(appStore.activeCard.icon) }}
            </div>
            <div class="card-details">
              <h3 class="font-heading">{{ appStore.activeCard.role_name }}</h3>
              <p>{{ appStore.activeCard.description }}</p>
              <div class="card-tech-tags">
                <el-tag
                  v-for="tech in appStore.activeCard.tech_stack.slice(0, 6)"
                  :key="tech"
                  size="small"
                  effect="plain"
                  class="tech-tag"
                >
                  {{ tech }}
                </el-tag>
                <span class="more-tag" v-if="appStore.activeCard.tech_stack.length > 6">
                  +{{ appStore.activeCard.tech_stack.length - 6 }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </BorderGlowCard>
    </section>

    <section class="role-section" v-else>
      <BorderGlowCard
        :glow-color="'270 40% 75%'"
        :background-color="'rgba(255, 255, 255, 0.02)'"
        :border-radius="16"
        :glow-radius="50"
        :glow-intensity="0.5"
        :cone-spread="30"
        :animated="false"
        :colors="['#ffffff', '#c4b5fd', '#a1a1aa']"
        :fill-opacity="0.15"
        class="no-card-wrapper"
      >
        <div class="no-card-tip">
          <div class="tip-icon-wrap">
            <svg viewBox="0 0 48 48" fill="none" class="tip-svg">
              <circle cx="24" cy="24" r="20" stroke="#ffffff" stroke-width="1.5" stroke-dasharray="3 3" opacity="0.4" />
              <circle cx="24" cy="24" r="8" stroke="#a1a1aa" stroke-width="1.5" fill="none" />
              <circle cx="24" cy="24" r="3" fill="#ffffff" opacity="0.8" />
            </svg>
          </div>
          <div class="tip-text">
            <h3 class="font-heading">选择你的面试方向</h3>
            <p>选择一个预设岗位，我们将为你生成针对性的面试题库和模拟面试</p>
          </div>
          <IridescentBtn text="立即选择" size="lg" @click="router.push('/role-select')" />
        </div>
      </BorderGlowCard>
    </section>

    <section class="features-section">
      <h2 class="section-title font-heading">
        <span class="title-accent"></span>
        功能入口
      </h2>
      <div class="features-bento">
        <div
          class="bento-card bento-card-xl job-card"
          :style="{ '--accent': cards[0].accentColor }"
          @click="router.push(cards[0].path)"
        >
          <div class="bento-content">
            <div class="bento-icon-wrap">
              <component :is="cards[0].icon" class="bento-icon-svg" />
            </div>
            <div class="bento-text">
              <h3 class="bento-title font-heading">{{ cards[0].title }}</h3>
              <p class="bento-desc">{{ cards[0].desc }}</p>
              <div class="bento-tags" v-if="cards[0].badge">
                <span class="bento-badge">{{ cards[0].badge }}</span>
              </div>
            </div>
            <div class="bento-arrow">
              <el-icon><ArrowRight /></el-icon>
            </div>
          </div>
        </div>

        <div
          class="bento-card bento-card-sm resume-card"
          :style="{ '--accent': cards[1].accentColor }"
          @click="router.push(cards[1].path)"
        >
          <div class="bento-content-vertical">
            <div class="bento-icon-wrap-sm">
              <component :is="cards[1].icon" class="bento-icon-svg-sm" />
            </div>
            <h3 class="bento-title-sm font-heading">{{ cards[1].title }}</h3>
            <p class="bento-desc-sm">{{ cards[1].desc }}</p>
            <span v-if="cards[1].badge" class="bento-badge-sm">{{ cards[1].badge }}</span>
          </div>
        </div>

        <div
          class="bento-card bento-card-sm question-card"
          :style="{ '--accent': cards[2].accentColor }"
          @click="router.push(cards[2].path)"
        >
          <div class="bento-content-vertical">
            <div class="bento-icon-wrap-sm">
              <component :is="cards[2].icon" class="bento-icon-svg-sm" />
            </div>
            <h3 class="bento-title-sm font-heading">{{ cards[2].title }}</h3>
            <p class="bento-desc-sm">{{ cards[2].desc }}</p>
            <span v-if="cards[2].badge" class="bento-badge-sm">{{ cards[2].badge }}</span>
          </div>
        </div>

        <div
          class="bento-card bento-card-lg interview-card"
          :style="{ '--accent': cards[3].accentColor }"
          @click="router.push(cards[3].path)"
        >
          <div class="bento-content">
            <div class="bento-icon-wrap">
              <component :is="cards[3].icon" class="bento-icon-svg" />
            </div>
            <div class="bento-text">
              <h3 class="bento-title font-heading">{{ cards[3].title }}</h3>
              <p class="bento-desc">{{ cards[3].desc }}</p>
            </div>
            <div class="bento-arrow">
              <el-icon><ArrowRight /></el-icon>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="progress-section">
      <div class="panel-header">
        <span class="panel-title font-heading">求职准备进度</span>
        <el-button
          text
          type="danger"
          :icon="Delete"
          @click="handleClear"
          v-if="appStore.hasJobProfile || appStore.hasResume || appStore.hasQuestionBank"
        >
          清除数据
        </el-button>
      </div>
      <div class="progress-grid">
        <BorderGlowCard
          v-for="(item, idx) in progressItems"
          :key="idx"
          :glow-color="'270 40% 75%'"
          :background-color="'rgba(255, 255, 255, 0.02)'"
          :border-radius="12"
          :glow-radius="30"
          :glow-intensity="0.4"
          :cone-spread="25"
          :animated="false"
          :colors="['#ffffff', '#c4b5fd', '#a1a1aa']"
          :fill-opacity="0.15"
          class="progress-card"
          @click="router.push(item.path)"
        >
          <div class="progress-item" :class="{ done: item.done }">
            <div class="progress-icon-wrap">
              <el-icon v-if="item.done" class="done-icon"><CircleCheck /></el-icon>
              <el-icon v-else class="todo-icon"><CircleClose /></el-icon>
            </div>
            <div class="progress-info">
              <div class="progress-label font-heading">{{ item.label }}</div>
              <div class="progress-status">{{ item.done ? item.statusText : '未开始' }}</div>
            </div>
            <el-icon class="progress-arrow"><ArrowRight /></el-icon>
          </div>
        </BorderGlowCard>
      </div>
    </section>

    <section class="flow-section">
      <BorderGlowCard
        :colors="['#ffffff', '#c4b5fd', '#a1a1aa']"
        glow-color="270 40% 75%"
        :border-radius="16"
        :glow-radius="40"
        :glow-intensity="0.5"
        class="flow-card"
      >
        <div class="flow">
          <h3 class="flow-title font-heading">推荐使用流程</h3>
          <el-steps :active="appStore.progressStep" align-center finish-status="success">
            <el-step title="解析岗位" description="粘贴 JD，生成岗位需求画像" />
            <el-step title="优化简历" description="按画像定向打磨简历" />
            <el-step title="生成题库" description="针对性刷题备战" />
            <el-step title="模拟面试" description="真实对话 + 雷达图评分" />
          </el-steps>
          <div class="flow-tip" v-if="appStore.progressStep === 0">
            <el-icon><InfoFilled /></el-icon>
            <span>从「岗位匹配」开始，后续模块会自动复用已生成的数据</span>
          </div>
        </div>
      </BorderGlowCard>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Aim,
  Document,
  Reading,
  ChatDotRound,
  ArrowRight,
  CircleCheck,
  CircleClose,
  InfoFilled,
  Delete,
} from '@element-plus/icons-vue'
import { useAppStore } from '@/stores/app'
import { getRoleIcon, getRoleColor } from '@/types/role_card'
import BorderGlowCard from '@/components/effects/BorderGlowCard.vue'
import CountUpNumber from '@/components/effects/CountUpNumber.vue'
import IridescentBtn from '@/components/effects/IridescentBtn.vue'
import JobIcon from '@/components/icons/JobIcon.vue'
import ResumeIcon from '@/components/icons/ResumeIcon.vue'
import QuestionIcon from '@/components/icons/QuestionIcon.vue'
import InterviewIcon from '@/components/icons/InterviewIcon.vue'

const router = useRouter()
const appStore = useAppStore()

const heroTags = [
  { label: '岗位画像解析', color: '#ffffff' },
  { label: '简历智能优化', color: '#e4e4e7' },
  { label: '题库自适应生成', color: '#a1a1aa' },
  { label: 'AI 模拟面试', color: '#71717a' },
]

const hasCompletedInterview = computed(() => {
  return appStore.interviewHistory.some(r => r.status === 'completed')
})

const progressItems = computed(() => [
  {
    label: '岗位画像',
    done: appStore.hasJobProfile,
    statusText: appStore.currentJobProfile?.position || '已生成',
    path: '/job-matcher',
  },
  {
    label: '项目分析',
    done: appStore.hasResume,
    statusText: appStore.optimizedResume ? '已优化' : '已有简历',
    path: '/resume-optimizer',
  },
  {
    label: '面试题库',
    done: appStore.hasQuestionBank,
    statusText: `${appStore.questionBank?.length || 0} 道题已生成`,
    path: '/question-bank',
  },
  {
    label: '模拟面试',
    done: hasCompletedInterview.value,
    statusText: hasCompletedInterview.value
      ? `已完成 ${appStore.interviewHistory.filter(r => r.status === 'completed').length} 次`
      : '待开始',
    path: '/interview',
  },
])

const heroStats = computed(() => [
  {
    value: appStore.questionBank?.length || 0,
    suffix: '',
    label: '题目储备',
  },
  {
    value: appStore.interviewHistory.filter(r => r.status === 'completed').length,
    suffix: '',
    label: '面试次数',
  },
  {
    value: appStore.hasResume ? 100 : appStore.hasJobProfile ? 25 : 0,
    suffix: '%',
    label: '准备进度',
  },
])

const cards = computed(() => [
  {
    path: '/job-matcher',
    title: '岗位画像解析',
    desc: '粘贴 JD 文本，AI 解析生成岗位需求画像，含技术栈、技能与加分项。',
    icon: JobIcon,
    accentColor: '#ffffff',
    badge: appStore.hasJobProfile ? '已生成' : '',
  },
  {
    path: '/resume-optimizer',
    title: '简历智能优化',
    desc: '基于岗位画像定向优化简历，输出修改建议与优化后全文。',
    icon: ResumeIcon,
    accentColor: '#ffffff',
    badge: appStore.hasResume ? '已优化' : '',
  },
  {
    path: '/question-bank',
    title: '题库自适应生成',
    desc: '按岗位生成八股 / 算法 / 系统设计 / 项目深挖题库，附答案解析。',
    icon: QuestionIcon,
    accentColor: '#ffffff',
    badge: appStore.hasQuestionBank ? `${appStore.questionBank?.length}题` : '',
  },
  {
    path: '/interview',
    title: 'AI 模拟面试',
    desc: 'AI 面试官多轮对话追问，结束后输出多维评分与改进建议。',
    icon: InterviewIcon,
    accentColor: '#ffffff',
    badge: '',
  },
])

function handleClear() {
  ElMessageBox.confirm('确定清除所有已生成的数据（岗位画像、简历、题库）？此操作不可撤销。', '清除数据', {
    confirmButtonText: '确定清除',
    cancelButtonText: '取消',
    type: 'warning',
  })
    .then(() => {
      appStore.clearAll()
      ElMessage.success('数据已清除')
    })
    .catch(() => {})
}
</script>

<style scoped>
.hero-section {
  position: relative;
  overflow: hidden;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  padding: 32px 36px;
  margin-bottom: 32px;
}

/* Hero 紫色光晕背景 */
.hero-section::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -10%;
  width: 500px;
  height: 500px;
  background: radial-gradient(
    circle,
    var(--bc-violet-soft) 0%,
    transparent 60%
  );
  filter: blur(40px);
  pointer-events: none;
  z-index: 0;
}

.hero-section::after {
  content: '';
  position: absolute;
  bottom: -30%;
  left: -5%;
  width: 400px;
  height: 400px;
  background: radial-gradient(
    circle,
    var(--bc-violet-light) 0%,
    transparent 55%
  );
  filter: blur(50px);
  pointer-events: none;
  z-index: 0;
  opacity: 0.5;
}

.hero-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 30px;
}

.hero-left {
  flex: 1;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 5px 12px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: var(--bc-radius-pill);
  font-size: var(--bc-font-size-xs);
  color: var(--bc-primary-light);
  letter-spacing: 0.3px;
  margin-bottom: 16px;
  box-shadow: 0 0 20px var(--bc-violet-soft);
}

.badge-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--bc-primary);
  box-shadow: 0 0 8px rgba(196, 181, 253, 0.6);
  animation: badgePulse 2s ease-in-out infinite;
}

@keyframes badgePulse {
  0%, 100% { box-shadow: 0 0 6px var(--bc-violet-light); }
  50% { box-shadow: 0 0 12px var(--bc-violet-glow); }
}

.hero-title {
  font-size: var(--bc-font-size-3xl);
  font-weight: 700;
  margin: 0 0 14px 0;
  line-height: 1.2;
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.title-divider {
  width: 1px;
  height: 22px;
  background: var(--bc-border-strong);
}

.hero-subtitle-inline {
  font-size: var(--bc-font-size-lg);
  font-weight: 500;
  color: var(--bc-text-soft);
  letter-spacing: 0.5px;
}

.hero-desc {
  color: var(--bc-text-soft);
  line-height: 1.8;
  margin: 0 0 20px 0;
  max-width: 720px;
  font-size: var(--bc-font-size-sm);
}

.hero-tags {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.hero-tag {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--bc-border-soft);
  border-radius: var(--bc-radius-pill);
  font-size: 12px;
  color: var(--bc-text-soft);
  transition: var(--bc-transition);
  cursor: pointer;
}

.hero-tag:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: var(--bc-border-strong);
  transform: translateY(-2px);
}

.tag-icon {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  transition: box-shadow 0.3s ease;
}

.hero-tag:hover .tag-icon {
  box-shadow: 0 0 8px currentColor;
}

.hero-stats {
  display: flex;
  gap: 24px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--bc-border-soft);
}

.hero-stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-value {
  font-size: var(--bc-font-size-2xl);
  font-weight: 700;
  color: var(--bc-primary-light);
  font-variant-numeric: tabular-nums;
  background: linear-gradient(135deg, #ffffff 0%, #c4b5fd 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: var(--bc-font-size-xs);
  color: var(--bc-text-muted);
  letter-spacing: 0.3px;
}

.hero-right {
  flex-shrink: 0;
}

.hero-emblem {
  width: 130px;
  height: 130px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.emblem-svg {
  width: 100%;
  height: 100%;
  animation: emblem-rotate 25s linear infinite;
}

@keyframes emblem-rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.role-section {
  margin-bottom: var(--bc-space-6);
}

.role-card-wrapper {
  border-radius: var(--bc-radius-md);
}

.role-card-panel {
  border-radius: var(--bc-radius-md);
  padding: var(--bc-space-5);
  background: var(--bc-bg-glass);
  backdrop-filter: blur(var(--bc-glass-blur)) saturate(var(--bc-glass-saturate));
  -webkit-backdrop-filter: blur(var(--bc-glass-blur)) saturate(var(--bc-glass-saturate));
  border: 1px solid var(--bc-border);
}

.no-card-wrapper {
  border-radius: var(--bc-radius-md);
}

.no-card-tip {
  display: flex;
  align-items: center;
  gap: 22px;
  padding: var(--bc-space-5);
}

.tip-icon-wrap {
  width: 56px;
  height: 56px;
  flex-shrink: 0;
}

.tip-svg {
  width: 100%;
  height: 100%;
}

.tip-text {
  flex: 1;
}

.tip-text h3 {
  margin: 0 0 6px 0;
  font-size: var(--bc-font-size-lg);
  font-weight: 600;
  color: var(--bc-text);
}

.tip-text p {
  margin: 0;
  color: var(--bc-text-soft);
  font-size: var(--bc-font-size-sm);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}

.panel-title {
  font-size: var(--bc-font-size-base);
  font-weight: 600;
  color: var(--bc-text);
  letter-spacing: 0.3px;
  position: relative;
  padding-left: 12px;
}

.panel-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 14px;
  background: linear-gradient(180deg, #c4b5fd, #8b5cf6);
  border-radius: 2px;
  box-shadow: 0 0 8px var(--bc-violet-glow);
}

.action-btn {
  color: var(--bc-text-soft) !important;
  font-size: 12px;
}

.action-btn :deep(span) {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.active-card-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.card-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--bc-radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #fff;
  flex-shrink: 0;
  box-shadow: var(--bc-shadow-md), var(--bc-shadow-inner);
}

.card-details h3 {
  margin: 0 0 6px 0;
  font-size: var(--bc-font-size-xl);
  font-weight: 600;
  color: var(--bc-text);
}

.card-details p {
  margin: 0 0 12px 0;
  color: var(--bc-text-soft);
  font-size: var(--bc-font-size-sm);
}

.card-tech-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  align-items: center;
}

.tech-tag {
  background: rgba(255, 255, 255, 0.04) !important;
  border-color: var(--bc-border-soft) !important;
  color: var(--bc-text-soft) !important;
}

.more-tag {
  font-size: 11px;
  color: var(--bc-text-muted);
  padding: 2px 6px;
}

.section-title {
  font-size: var(--bc-font-size-base);
  font-weight: 600;
  color: var(--bc-text);
  margin: 0 0 16px 0;
  letter-spacing: 0.3px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.title-accent {
  width: 3px;
  height: 14px;
  background: linear-gradient(180deg, #c4b5fd, #8b5cf6);
  border-radius: 2px;
  box-shadow: 0 0 8px var(--bc-violet-glow);
}

.features-section {
  margin-bottom: var(--bc-space-6);
}

.features-section {
  margin-bottom: 32px;
}

.features-bento {
  display: grid;
  grid-template-columns: 1.6fr 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 16px;
  height: 420px;
}

.bento-card {
  position: relative;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
}

/* bento卡片紫色光晕 */
.bento-card::before {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 100%;
  height: 100%;
  background: radial-gradient(
    circle,
    var(--bc-violet-soft) 0%,
    transparent 60%
  );
  filter: blur(30px);
  pointer-events: none;
  z-index: 0;
  opacity: 0;
  transition: opacity 0.4s ease;
}

.bento-card:hover::before {
  opacity: 1;
}

.bento-card:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(196, 181, 253, 0.2);
  transform: translateY(-3px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), 0 0 40px var(--bc-violet-soft);
}

.bento-card-xl {
  grid-column: span 2;
  grid-row: span 1;
  min-height: 140px;
}

.bento-card-lg {
  grid-column: span 2;
  grid-row: span 1;
  min-height: 120px;
}

.bento-card-sm {
  grid-column: span 1;
  grid-row: span 1;
  min-height: 140px;
}

.bento-content {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px 28px;
  height: 100%;
  position: relative;
  z-index: 2;
}

.bento-content-vertical {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 20px 22px;
  height: 100%;
  position: relative;
  z-index: 2;
}

.bento-icon-wrap {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.15);
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.bento-icon-svg {
  width: 32px;
  height: 32px;
  color: #ffffff;
  filter: drop-shadow(0 0 6px rgba(196, 181, 253, 0.4));
  transition: filter 0.3s ease;
}

.bento-card:hover .bento-icon-wrap {
  background: rgba(196, 181, 253, 0.1);
  border-color: rgba(196, 181, 253, 0.3);
  transform: scale(1.05);
  box-shadow: 0 0 30px var(--bc-violet-glow);
}

.bento-card:hover .bento-icon-svg {
  filter: drop-shadow(0 0 10px rgba(196, 181, 253, 0.6));
}

.bento-icon-wrap-sm {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.12);
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.bento-icon-svg-sm {
  width: 26px;
  height: 26px;
  color: #ffffff;
  filter: drop-shadow(0 0 4px rgba(196, 181, 253, 0.35));
  transition: filter 0.3s ease;
}

.bento-card:hover .bento-icon-wrap-sm {
  background: rgba(196, 181, 253, 0.08);
  border-color: rgba(196, 181, 253, 0.25);
  transform: scale(1.05);
  box-shadow: 0 0 20px var(--bc-violet-soft);
}

.bento-card:hover .bento-icon-svg-sm {
  filter: drop-shadow(0 0 8px rgba(196, 181, 253, 0.5));
}

.bento-text {
  flex: 1;
  min-width: 0;
}

.bento-title {
  font-size: 18px;
  font-weight: 600;
  color: #fafafa;
  margin: 0 0 6px 0;
  letter-spacing: -0.01em;
}

.bento-title-sm {
  font-size: 15px;
  font-weight: 600;
  color: #fafafa;
  margin: 0;
  letter-spacing: -0.01em;
}

.bento-desc {
  font-size: 13px;
  color: #71717a;
  line-height: 1.6;
  margin: 0;
}

.bento-desc-sm {
  font-size: 12px;
  color: #71717a;
  line-height: 1.5;
  margin: 0;
  flex: 1;
}

.bento-badge {
  display: inline-block;
  margin-top: 8px;
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 100px;
  font-size: 11px;
  font-weight: 600;
  color: #e4e4e7;
  letter-spacing: 0.3px;
}

.bento-badge-sm {
  display: inline-block;
  margin-top: auto;
  padding: 3px 8px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 100px;
  font-size: 10px;
  font-weight: 600;
  color: #d4d4d8;
  letter-spacing: 0.3px;
  align-self: flex-start;
}

.bento-arrow {
  color: #52525b;
  font-size: 14px;
  flex-shrink: 0;
  transition: all 0.3s ease;
  opacity: 0;
  transform: translateX(-4px);
}

.bento-card:hover .bento-arrow {
  opacity: 1;
  transform: translateX(0);
  color: #a1a1aa;
}

.progress-section {
  margin-bottom: var(--bc-space-6);
}

.progress-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.progress-card {
  border-radius: var(--bc-radius-md);
  background: var(--bc-bg-glass);
  backdrop-filter: blur(var(--bc-glass-blur)) saturate(var(--bc-glass-saturate));
  -webkit-backdrop-filter: blur(var(--bc-glass-blur)) saturate(var(--bc-glass-saturate));
  border: 1px solid var(--bc-border);
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.progress-card::before {
  content: '';
  position: absolute;
  inset: 0;
  background: radial-gradient(
    circle at 80% 50%,
    var(--bc-violet-soft) 0%,
    transparent 50%
  );
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.progress-card:hover {
  border-color: rgba(196, 181, 253, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3), 0 0 25px var(--bc-violet-soft);
}

.progress-card:hover::before {
  opacity: 1;
}

.progress-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  min-height: 70px;
}

.progress-icon-wrap {
  flex-shrink: 0;
  font-size: 20px;
}

.done-icon {
  color: #ffffff !important;
  filter: drop-shadow(0 0 6px rgba(196, 181, 253, 0.5));
}

.todo-icon {
  color: var(--bc-text-muted) !important;
}

.progress-info {
  flex: 1;
  min-width: 0;
}

.progress-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--bc-text);
  margin-bottom: 2px;
}

.progress-status {
  font-size: var(--bc-font-size-xs);
  color: var(--bc-text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.progress-item.done .progress-status {
  color: #ffffff;
}

.progress-arrow {
  color: var(--bc-text-muted);
  font-size: 12px;
  transition: transform 250ms var(--bc-ease);
}

.progress-card:hover .progress-arrow {
  transform: translateX(4px);
  color: var(--bc-text-soft);
}

.flow-section {
  margin-bottom: var(--bc-space-6);
}

.flow-card {
  width: 100%;
}

.flow {
  padding: var(--bc-space-5);
}

.flow-title {
  margin: 0 0 22px 0;
  color: var(--bc-text);
  font-size: var(--bc-font-size-base);
  font-weight: 600;
  letter-spacing: 0.3px;
  position: relative;
  padding-left: 12px;
}

.flow-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 14px;
  background: var(--bc-accent-cyan);
  border-radius: 2px;
  box-shadow: 0 0 6px var(--bc-accent-cyan-glow);
}

.flow :deep(.el-step__title.is-finish),
.flow :deep(.el-step__title.is-process),
.flow :deep(.el-step__title.is-wait) {
  color: var(--bc-text);
}

.flow :deep(.el-step__title.is-finish) {
  color: #ffffff;
}

.flow :deep(.el-step__description) {
  color: var(--bc-text-soft);
}

.flow-tip {
  display: flex;
  align-items: center;
  gap: 7px;
  margin-top: 18px;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--bc-radius-sm);
  font-size: var(--bc-font-size-sm);
  color: var(--bc-text-soft);
}

.flow-tip .el-icon {
  color: #c4b5fd;
  filter: drop-shadow(0 0 4px var(--bc-violet-glow));
}

@media (max-width: 768px) {
  .features-bento {
    grid-template-columns: 1fr;
    grid-template-rows: auto;
  }

  .bento-card-xl,
  .bento-card-lg,
  .bento-card-sm {
    grid-column: span 1;
    grid-row: span 1;
  }

  .progress-grid {
    grid-template-columns: 1fr;
  }

  .hero-content {
    flex-direction: column;
  }

  .hero-right {
    display: none;
  }
}
</style>
