<template>
  <div class="page-container">
    <h1 class="page-title">
      <span class="title-bar"></span>
      <span class="fx-gradient-text">项目分析</span>
    </h1>
    <p class="page-subtitle">解析简历项目技术栈，给出针对岗位的技术建议，并推荐可提升竞争力的新项目</p>

    <el-row :gutter="20" class="input-row fx-stagger">
      <el-col :span="12" :xs="24" :md="12">
        <div class="section-card">
          <div class="panel-header">
            <span class="panel-title">
              <span class="title-bar-sm"></span>
              简历文本
            </span>
            <div class="header-actions">
              <el-upload
                :show-file-list="false"
                :before-upload="handleUploadResume"
                accept=".pdf,.png,.jpg,.jpeg,.bmp,.webp"
              >
                <el-button :loading="parsing" :icon="Upload" size="small" text>
                  {{ parsing ? '解析中...' : '上传 PDF/图片' }}
                </el-button>
              </el-upload>
              <el-button text size="small" @click="loadSampleResume">载入示例</el-button>
            </div>
          </div>
          <el-input
            v-model="resumeText"
            type="textarea"
            :rows="14"
            placeholder="请粘贴你的简历全文（包含项目经历）..."
            resize="none"
            class="resume-textarea"
          />
        </div>
      </el-col>
      <el-col :span="12" :xs="24" :md="12">
        <div class="section-card">
          <div class="panel-header">
            <span class="panel-title" v-if="appStore.activeCard">
              <span class="title-bar-sm"></span>
              目标岗位：{{ appStore.activeCard.role_name }}
            </span>
            <span class="panel-title" v-else>
              <span class="title-bar-sm"></span>
              岗位画像 JSON
            </span>
            <div class="header-actions">
              <el-button text type="primary" :icon="Aim" @click="roleSelectorVisible = true">
                选择岗位方向
              </el-button>
              <el-button text type="primary" :icon="MagicStick" @click="fillFromStore" v-if="!appStore.activeCard">
                从岗位匹配导入
              </el-button>
            </div>
          </div>
          <div v-if="appStore.activeCard" class="card-preview">
            <div class="preview-item">
              <span class="preview-label">技术栈：</span>
              <div class="preview-tags fx-stagger">
                <el-tag
                  v-for="tech in appStore.activeCard.tech_stack.slice(0, 8)"
                  :key="tech"
                  size="small"
                  effect="plain"
                  class="preview-tag"
                >
                  {{ tech }}
                </el-tag>
              </div>
            </div>
            <div class="preview-item">
              <span class="preview-label">核心技能：</span>
              <div class="preview-tags fx-stagger">
                <el-tag
                  v-for="skill in appStore.activeCard.core_skills.slice(0, 4)"
                  :key="skill"
                  size="small"
                  type="success"
                  effect="plain"
                  class="preview-tag"
                >
                  {{ skill }}
                </el-tag>
              </div>
            </div>
          </div>
          <el-input
            v-else
            v-model="jobProfileText"
            type="textarea"
            :rows="14"
            placeholder='请粘贴岗位画像 JSON，例如 {"position":"后端工程师","tech_stack":["Go","MySQL"],...}'
            resize="none"
            class="mono job-textarea"
          />
        </div>
      </el-col>
    </el-row>

    <div class="action-bar">
      <el-button
        type="primary"
        size="large"
        :loading="analyzing"
        :icon="MagicStick"
        class="fx-shine"
        @click="handleAnalyze"
      >
        开始分析
      </el-button>
    </div>

    <div v-if="analyzing" class="section-card progress-card">
      <div class="panel-header">
        <span class="panel-title">
          <span class="title-bar-sm"></span>
          项目分析进行中
        </span>
        <span class="progress-percent">{{ progressPercent }}%</span>
      </div>
      <el-progress
        :percentage="progressPercent"
        :status="progressStatus"
        :stroke-width="8"
        class="progress-bar"
      />
      <div class="progress-steps">
        <div
          v-for="(step, i) in progressSteps"
          :key="i"
          class="step-item"
          :class="{
            active: currentStepIndex >= i,
            current: currentStepIndex === i && !step.done
          }"
        >
          <div class="step-dot">
            <el-icon v-if="step.done" class="step-check"><CircleCheckFilled /></el-icon>
            <span v-else class="step-num">{{ i + 1 }}</span>
          </div>
          <div class="step-info">
            <span class="step-name">{{ step.name }}</span>
            <span class="step-desc">{{ step.desc }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 分析结果 -->
    <div v-if="analysisResult || techSuggestions.length || recommendedProject" class="result-card">

      <!-- 项目解析 -->
      <div v-if="projects.length" class="section-card result-section">
        <div class="panel-header">
          <span class="panel-title">
            <span class="title-bar-sm"></span>
            项目解析（共 {{ projects.length }} 个项目）
          </span>
        </div>
        <div class="projects-list fx-stagger">
          <div v-for="(proj, i) in projects" :key="i" class="project-card fx-hover-lift">
            <div class="project-head">
              <span class="project-num">{{ i + 1 }}</span>
              <h4 class="project-name">{{ proj.name }}</h4>
            </div>
            <p class="project-desc">{{ proj.description }}</p>
            <div class="project-tech">
              <span class="section-label">技术栈：</span>
              <el-tag
                v-for="tech in proj.tech_stack"
                :key="tech"
                size="small"
                type="info"
                effect="plain"
                class="tech-tag"
              >
                {{ tech }}
              </el-tag>
            </div>
            <div v-if="proj.highlights && proj.highlights.length" class="project-highlights">
              <span class="section-label">核心亮点：</span>
              <ul class="highlights-list">
                <li v-for="(h, j) in proj.highlights" :key="j">{{ h }}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      <!-- 技术建议 -->
      <div v-if="techSuggestions.length" class="section-card result-section">
        <div class="panel-header">
          <span class="panel-title">
            <span class="title-bar-sm"></span>
            技术补充建议（{{ techSuggestions.length }} 条）
          </span>
        </div>
        <div class="tech-suggestions-list fx-stagger">
          <div
            v-for="(sug, i) in techSuggestions"
            :key="i"
            class="tech-sug-card fx-hover-lift"
          >
            <div class="tech-sug-head">
              <el-tag :type="getPriorityType(sug.priority)" effect="dark" size="small">
                {{ sug.priority }}
              </el-tag>
              <h4 class="tech-name">{{ sug.tech }}</h4>
            </div>
            <div class="tech-sug-body">
              <div class="tech-sug-item">
                <span class="label">为什么学：</span>
                <span class="value">{{ sug.reason }}</span>
              </div>
              <div class="tech-sug-item">
                <span class="label">如何加入：</span>
                <span class="value">{{ sug.how_to_add }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 推荐新项目 -->
      <div v-if="recommendedProject" class="section-card result-section recommended-project-section">
        <div class="panel-header">
          <span class="panel-title">
            <span class="title-bar-sm"></span>
            推荐新项目
          </span>
          <el-tag type="success" effect="dark" size="small">{{ recommendedProject.difficulty }}</el-tag>
        </div>
        <div class="recommended-project">
          <h3 class="rec-project-name">{{ recommendedProject.name }}</h3>
          <p class="rec-project-desc">{{ recommendedProject.description }}</p>

          <div class="rec-project-tech">
            <span class="section-label">技术栈：</span>
            <el-tag
              v-for="tech in recommendedProject.tech_stack"
              :key="tech"
              size="small"
              type="success"
              effect="plain"
              class="tech-tag"
            >
              {{ tech }}
            </el-tag>
          </div>

          <div class="rec-project-value">
            <el-icon color="#67c23a"><Opportunity /></el-icon>
            <span>{{ recommendedProject.value }}</span>
          </div>

          <div class="rec-project-hints">
            <span class="section-label">实现要点：</span>
            <ul class="hints-list">
              <li v-for="(hint, i) in recommendedProject.implementation_hints" :key="i">
                {{ hint }}
              </li>
            </ul>
          </div>

          <div class="rec-project-actions">
            <el-button type="primary" :icon="Reading" @click="router.push('/project-story')">
              深挖这个项目
            </el-button>
            <el-button text type="warning" :icon="ChatDotRound" @click="router.push('/interview')">
              去模拟面试
            </el-button>
          </div>
        </div>
      </div>

      <!-- 整体总结 -->
      <div v-if="analysisSummary" class="section-card result-section summary-section">
        <div class="panel-header">
          <span class="panel-title">
            <span class="title-bar-sm"></span>
            整体分析总结
          </span>
        </div>
        <p class="summary-text">{{ analysisSummary }}</p>
      </div>
    </div>

    <el-empty
      v-if="!analysisResult && !analyzing && !projects.length && !techSuggestions.length && !recommendedProject"
      description="分析结果将展示在此"
    />

    <RoleSelector v-model="roleSelectorVisible" @select="handleRoleSelect" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  MagicStick,
  Upload,
  Aim,
  CircleCheckFilled,
  Reading,
  ChatDotRound,
  Opportunity
} from '@element-plus/icons-vue'
import { projectAnalysis, parseResumeFile } from '@/api/agents'
import { useAppStore, type JobProfile } from '@/stores/app'
import RoleSelector from '@/components/effects/RoleSelector.vue'
import type { RoleCard } from '@/types/role_card'

const router = useRouter()
const appStore = useAppStore()

const resumeText = ref(appStore.currentResume || '')
const jobProfileText = ref('')
const parsing = ref(false)
const analyzing = ref(false)
const roleSelectorVisible = ref(false)

// 结果数据
const projects = ref<any[]>([])
const techSuggestions = ref<any[]>([])
const recommendedProject = ref<any>(null)
const analysisSummary = ref('')
const analysisResult = ref<any>(null)

// 进度相关
const progressPercent = ref(0)
const progressStatus = ref<'success' | 'exception' | ''>('')
const currentStepIndex = ref(-1)
const progressSteps = ref([
  { name: '解析项目', desc: '提取简历中的项目信息', done: false },
  { name: '分析技术栈', desc: '识别已有技术和亮点', done: false },
  { name: '生成建议', desc: '针对岗位给出技术建议', done: false },
  { name: '推荐项目', desc: '推荐可提升竞争力的新项目', done: false },
])

function handleRoleSelect(card: RoleCard) {
  appStore.setActiveCard(card)
  ElMessage.success(`已选择「${card.role_name}」`)
}

// 页面加载时自动填充岗位画像
onMounted(() => {
  if (appStore.currentJobProfile) {
    jobProfileText.value = JSON.stringify(appStore.currentJobProfile, null, 2)
  }

  // 恢复已完成的任务结果
  const task = appStore.backgroundTasks.find(
    t => t.type === 'resume-optimize' && t.status === 'completed' && t.result
  )
  if (task?.result) {
    restoreResult(task.result)
  }
})

function parseProfile(): JobProfile | null {
  if (appStore.activeCard) {
    return {
      position: appStore.activeCard.role_name,
      tech_stack: appStore.activeCard.tech_stack,
      core_skills: appStore.activeCard.core_skills,
      experience_years: appStore.activeCard.experience_years,
      education: appStore.activeCard.education,
      interview_directions: appStore.activeCard.interview_directions,
    }
  }
  if (!jobProfileText.value.trim()) {
    ElMessage.warning('请输入岗位画像 JSON')
    return null
  }
  try {
    return JSON.parse(jobProfileText.value)
  } catch {
    ElMessage.error('岗位画像 JSON 格式不正确')
    return null
  }
}

function fillFromStore() {
  const p = appStore.currentJobProfile
  if (p) {
    jobProfileText.value = JSON.stringify(p, null, 2)
    ElMessage.success('已从岗位匹配导入画像')
  } else {
    ElMessage.warning('尚未解析岗位画像，请先在「岗位匹配」页解析')
  }
}

async function handleUploadResume(file: File) {
  parsing.value = true
  try {
    const res: any = await parseResumeFile(file)
    resumeText.value = res?.text || res?.resume_text || ''
    ElMessage.success('简历解析完成')
  } catch {
    ElMessage.error('简历解析失败，请重试')
  } finally {
    parsing.value = false
  }
  return false
}

function loadSampleResume() {
  resumeText.value = `张三 | Java后端开发 | 3年经验

技能：
- Java、Spring Boot、MySQL、Redis

项目经历：

1. 电商后台管理系统
   使用Spring Boot开发，实现了商品管理和订单管理模块。
   使用Redis做缓存提升接口响应速度。

2. 在线考试系统
   SSM框架，实现了试题管理和自动判分功能。
   数据库设计优化，查询效率提升30%。`
}

function startProgressSimulation() {
  progressPercent.value = 0
  progressStatus.value = ''
  currentStepIndex.value = 0
  progressSteps.value.forEach((s, i) => s.done = false)
}

function finishProgress(success: boolean) {
  progressSteps.value.forEach(s => s.done = true)
  progressPercent.value = 100
  progressStatus.value = success ? 'success' : 'exception'
  currentStepIndex.value = progressSteps.value.length
}

async function handleAnalyze() {
  const profile = parseProfile()
  if (!profile) return

  if (!resumeText.value.trim()) {
    ElMessage.warning('请输入简历文本')
    return
  }

  // 创建后台任务
  const taskId = `project-analysis-${Date.now()}`
  appStore.addBackgroundTask({
    id: taskId,
    type: 'resume-optimize',
    title: '项目分析中...',
    progress: 0,
    result: null,
  })

  analyzing.value = true
  projects.value = []
  techSuggestions.value = []
  recommendedProject.value = null
  analysisSummary.value = ''
  analysisResult.value = null

  startProgressSimulation()

  // 模拟进度更新
  const progressInterval = setInterval(() => {
    if (currentStepIndex.value < progressSteps.value.length) {
      progressSteps.value[currentStepIndex.value].done = true
      currentStepIndex.value++
      progressPercent.value = Math.min(95, currentStepIndex.value * 25)
    }
  }, 800)

  // 后台执行分析
  projectAnalysis(resumeText.value, profile)
    .then((res: any) => {
      clearInterval(progressInterval)
      finishProgress(true)

      // 提取结果
      const result = {
        projects: res?.projects || [],
        techSuggestions: res?.tech_suggestions || res?.techSuggestions || [],
        recommendedProject: res?.recommended_project || res?.recommendedProject || null,
        summary: res?.summary || '',
      }

      projects.value = result.projects
      techSuggestions.value = result.techSuggestions
      recommendedProject.value = result.recommendedProject
      analysisSummary.value = result.summary
      analysisResult.value = result

      // 保存到 store
      appStore.setResume(resumeText.value)

      // 更新任务状态
      appStore.updateBackgroundTask(taskId, {
        status: 'completed',
        title: '项目分析完成',
        progress: 100,
        completedAt: new Date().toISOString(),
        result,
      })

      ElMessage.success('项目分析完成！')
    })
    .catch((err: any) => {
      clearInterval(progressInterval)
      finishProgress(false)

      appStore.updateBackgroundTask(taskId, {
        status: 'failed',
        title: '项目分析失败',
        completedAt: new Date().toISOString(),
        error: err?.message || '分析失败',
      })

      ElMessage.error('项目分析失败，请重试')
    })
    .finally(() => {
      setTimeout(() => {
        analyzing.value = false
      }, 500)
    })
}

function restoreResult(result: any) {
  if (result.projects) projects.value = result.projects
  if (result.techSuggestions) techSuggestions.value = result.techSuggestions
  if (result.recommendedProject) recommendedProject.value = result.recommendedProject
  if (result.summary) analysisSummary.value = result.summary
  if (result) analysisResult.value = result
}

function getPriorityType(priority: string): 'danger' | 'warning' | 'success' | 'info' {
  const map: Record<string, 'danger' | 'warning' | 'success' | 'info'> = {
    '高': 'danger',
    '中': 'warning',
    '低': 'success',
  }
  return map[priority] || 'info'
}
</script>

<style scoped>
.page-title {
  display: flex;
  align-items: center;
  gap: var(--bc-space-3);
}

.title-bar {
  width: 4px;
  height: 32px;
  border-radius: 2px;
  background: linear-gradient(180deg, #ffffff 0%, #c4b5fd 100%);
  flex-shrink: 0;
  box-shadow: 0 0 10px var(--bc-violet-soft);
}

.input-row {
  margin-bottom: 0;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--bc-space-4);
}

.panel-title {
  display: flex;
  align-items: center;
  gap: var(--bc-space-2);
  font-size: var(--bc-font-size-base);
  font-weight: 600;
  color: var(--bc-text);
}

.title-bar-sm {
  width: 3px;
  height: 16px;
  border-radius: 2px;
  background: linear-gradient(180deg, #ffffff 0%, #c4b5fd 100%);
  flex-shrink: 0;
  box-shadow: 0 0 6px var(--bc-violet-soft);
}

.action-bar {
  display: flex;
  justify-content: center;
  margin: var(--bc-space-5) 0;
}

.resume-textarea :deep(.el-textarea__inner) {
  font-family: var(--bc-font-mono);
  font-size: 13px;
  line-height: 1.6;
}

.job-textarea :deep(.el-textarea__inner) {
  font-family: var(--bc-font-mono);
  font-size: 13px;
  line-height: 1.6;
}

.card-preview {
  padding: var(--bc-space-3);
  background: var(--bc-bg-soft);
  border-radius: var(--bc-radius-sm);
}

.preview-item {
  margin-bottom: var(--bc-space-3);
}

.preview-label {
  font-size: var(--bc-font-size-sm);
  color: var(--bc-text-soft);
  margin-bottom: var(--bc-space-2);
  display: block;
}

.preview-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--bc-space-2);
}

.preview-tag {
  margin: 0;
}

.preview-text {
  font-size: var(--bc-font-size-sm);
  color: var(--bc-text-muted);
}

/* 进度条 */
.progress-card {
  margin-bottom: var(--bc-space-4);
}

.progress-percent {
  font-size: var(--bc-font-size-sm);
  color: var(--bc-text-soft);
}

.progress-bar {
  margin: var(--bc-space-4) 0;
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  padding: 0 var(--bc-space-4);
}

.step-item {
  display: flex;
  align-items: center;
  gap: var(--bc-space-2);
  opacity: 0.4;
  transition: opacity 0.3s;
}

.step-item.active {
  opacity: 1;
}

.step-item.current {
  opacity: 1;
}

.step-dot {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--bc-bg-soft);
  border: 2px solid var(--bc-border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: var(--bc-text-soft);
}

.step-item.active .step-dot {
  background: var(--bc-primary);
  border-color: var(--bc-primary);
  color: #fff;
}

.step-check {
  color: #fff;
}

.step-num {
  font-weight: 600;
}

.step-info {
  display: flex;
  flex-direction: column;
}

.step-name {
  font-size: var(--bc-font-size-sm);
  font-weight: 500;
}

.step-desc {
  font-size: var(--bc-font-size-xs);
  color: var(--bc-text-soft);
}

/* 结果区域 */
.result-card {
  margin-top: var(--bc-space-4);
}

.result-section {
  margin-bottom: var(--bc-space-4);
}

/* 项目列表 */
.projects-list {
  display: flex;
  flex-direction: column;
  gap: var(--bc-space-3);
}

.project-card {
  background: var(--bc-bg-soft);
  border: 1px solid var(--bc-border);
  border-radius: var(--bc-radius-sm);
  padding: var(--bc-space-4);
  transition: all 0.2s var(--bc-ease);
}

.project-card:hover {
  border-color: var(--bc-border-glow);
  box-shadow: var(--bc-shadow-md);
}

.project-head {
  display: flex;
  align-items: center;
  gap: var(--bc-space-3);
  margin-bottom: var(--bc-space-3);
}

.project-num {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--bc-primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.project-name {
  font-size: var(--bc-font-size-base);
  font-weight: 600;
  margin: 0;
}

.project-desc {
  font-size: var(--bc-font-size-sm);
  color: var(--bc-text-soft);
  margin-bottom: var(--bc-space-3);
  line-height: 1.6;
}

.project-tech,
.project-highlights {
  margin-bottom: var(--bc-space-2);
}

.section-label {
  font-size: var(--bc-font-size-sm);
  color: var(--bc-text-soft);
  margin-right: var(--bc-space-2);
}

.tech-tag {
  margin: 0 4px 4px 0;
}

.highlights-list {
  margin: var(--bc-space-2) 0 0;
  padding-left: var(--bc-space-4);
  font-size: var(--bc-font-size-sm);
  color: var(--bc-text);
  line-height: 1.8;
}

/* 技术建议 */
.tech-suggestions-list {
  display: flex;
  flex-direction: column;
  gap: var(--bc-space-3);
}

.tech-sug-card {
  background: var(--bc-bg-soft);
  border: 1px solid var(--bc-border);
  border-radius: var(--bc-radius-sm);
  padding: var(--bc-space-4);
  transition: all 0.2s var(--bc-ease);
}

.tech-sug-card:hover {
  border-color: var(--bc-border-glow);
  box-shadow: var(--bc-shadow-md);
}

.tech-sug-head {
  display: flex;
  align-items: center;
  gap: var(--bc-space-3);
  margin-bottom: var(--bc-space-3);
}

.tech-name {
  font-size: var(--bc-font-size-base);
  font-weight: 600;
  margin: 0;
}

.tech-sug-body {
  display: flex;
  flex-direction: column;
  gap: var(--bc-space-2);
}

.tech-sug-item {
  display: flex;
  align-items: flex-start;
  gap: var(--bc-space-2);
  font-size: var(--bc-font-size-sm);
  line-height: 1.6;
}

.tech-sug-item .label {
  color: var(--bc-text-soft);
  flex-shrink: 0;
}

.tech-sug-item .value {
  color: var(--bc-text);
}

/* 推荐项目 */
.recommended-project-section {
  border: 2px solid var(--bc-primary);
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(0, 0, 0, 0) 100%);
}

.rec-project-name {
  font-size: var(--bc-font-size-lg);
  font-weight: 700;
  margin: 0 0 var(--bc-space-2);
  color: var(--bc-primary);
}

.rec-project-desc {
  font-size: var(--bc-font-size-base);
  color: var(--bc-text);
  line-height: 1.6;
  margin-bottom: var(--bc-space-3);
}

.rec-project-tech {
  margin-bottom: var(--bc-space-3);
}

.rec-project-value {
  display: flex;
  align-items: flex-start;
  gap: var(--bc-space-2);
  padding: var(--bc-space-3);
  background: rgba(103, 194, 58, 0.1);
  border-radius: var(--bc-radius-sm);
  margin-bottom: var(--bc-space-3);
  font-size: var(--bc-font-size-sm);
  color: var(--bc-text);
  line-height: 1.6;
}

.rec-project-hints {
  margin-bottom: var(--bc-space-4);
}

.hints-list {
  margin: var(--bc-space-2) 0 0;
  padding-left: var(--bc-space-5);
  font-size: var(--bc-font-size-sm);
  color: var(--bc-text);
  line-height: 1.8;
}

.rec-project-actions {
  display: flex;
  gap: var(--bc-space-3);
}

/* 总结 */
.summary-section {
  background: var(--bc-bg-soft);
}

.summary-text {
  font-size: var(--bc-font-size-base);
  color: var(--bc-text);
  line-height: 1.8;
  margin: 0;
}

@media (max-width: 768px) {
  .input-row .el-col {
    margin-bottom: var(--bc-space-3);
  }

  .progress-steps {
    flex-direction: column;
    gap: var(--bc-space-2);
    padding: 0;
  }
}
</style>
