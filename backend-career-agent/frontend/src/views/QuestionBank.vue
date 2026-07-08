<template>
  <div class="page-container">
    <h1 class="page-title">
      <span class="title-bar"></span>
      <span class="fx-gradient-text">题库刷题</span>
    </h1>
    <p class="page-subtitle" v-if="appStore.activeCard">
      已选择「{{ appStore.activeCard.role_name }}」，AI 将按分类生成针对性面试题库（含答案与解析）
    </p>
    <p class="page-subtitle" v-else>
      输入岗位画像，AI 将按分类生成针对性面试题库（含答案与解析）
    </p>

    <div class="section-card config-panel">
      <div class="panel-header">
        <span class="panel-title">
          <span class="title-bar-sm"></span>
          <template v-if="appStore.activeCard">基于角色卡生成</template>
          <template v-else>岗位画像 JSON</template>
        </span>
        <div class="header-actions">
          <el-button text type="primary" :icon="Aim" @click="roleSelectorVisible = true">
            选择岗位方向
          </el-button>
          <el-button text type="primary" :icon="MagicStick" @click="fillFromStore">
            从岗位匹配导入
          </el-button>
          <el-button text @click="loadSample">载入示例</el-button>
        </div>
      </div>
      <el-input
        v-if="!appStore.activeCard"
        v-model="jobProfileText"
        type="textarea"
        :rows="6"
        placeholder='请粘贴岗位画像 JSON，例如 {"position":"后端工程师","tech_stack":["Java","MySQL","Redis"],"core_skills":["高并发","分布式"]}'
        class="mono profile-textarea"
      />
      <div v-else class="card-preview">
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
          <span class="preview-label">面试方向：</span>
          <div class="preview-tags fx-stagger">
            <el-tag
              v-for="dir in appStore.activeCard.interview_directions.slice(0, 4)"
              :key="dir"
              size="small"
              type="warning"
              effect="plain"
              class="preview-tag"
            >
              {{ dir }}
            </el-tag>
          </div>
        </div>
      </div>
      <div class="actions">
        <el-button
          type="primary"
          :loading="loading"
          :icon="Promotion"
          class="fx-shine"
          @click="handleGenerate"
        >
          {{ appStore.activeCard ? '基于角色卡生成题库' : '生成题库' }}
        </el-button>
        <el-button :icon="Delete" @click="resetAll">清空</el-button>
        <span v-if="totalQuestions" class="count">共 {{ totalQuestions }} 题</span>
      </div>
    </div>

    <div v-if="generating" class="section-card progress-card">
      <div class="panel-header">
        <span class="panel-title">
          <span class="title-bar-sm"></span>
          题库生成中
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

    <div v-else-if="hasQuestions" class="section-card result-panel">
      <div class="panel-header">
        <span class="panel-title">
          <span class="title-bar-sm"></span>
          题库结果（共 {{ totalQuestions }} 题）
        </span>
        <el-button text type="danger" :icon="ChatDotRound" @click="router.push('/interview')">
          带题库去模拟面试
        </el-button>
      </div>
      <el-tabs v-model="activeTab" class="q-tabs">
        <el-tab-pane
          v-for="cat in categories"
          :key="cat.key"
          :name="cat.key"
        >
          <template #label>
            <span class="tab-label">
              <el-icon class="cat-icon"><component :is="iconMap[cat.icon]" /></el-icon>
              {{ cat.label }}
              <el-badge
                :value="getCategoryQuestions(cat.key).length"
                :max="99"
                class="tab-badge"
              />
            </span>
          </template>

          <el-empty
            v-if="!getCategoryQuestions(cat.key).length"
            description="该分类暂无题目"
          />

          <el-collapse v-else accordion class="q-collapse">
            <el-collapse-item
              v-for="(q, i) in getCategoryQuestions(cat.key)"
              :key="i"
              :name="i"
              class="q-item"
            >
              <template #title>
                <div class="q-title-row">
                  <el-tag
                    :type="difficultyType(q.difficulty)"
                    effect="dark"
                    size="small"
                    class="q-diff"
                  >
                    {{ q.difficulty || '中等' }}
                  </el-tag>
                  <span class="q-index">{{ i + 1 }}.</span>
                  <span class="q-stem">{{ q.question || q.title || q.stem }}</span>
                </div>
              </template>

              <div class="q-body">
                <div class="q-block">
                  <div class="q-block-title">参考答案</div>
                  <div class="q-block-content answer">{{ q.answer || '—' }}</div>
                </div>
                <div class="q-block">
                  <div class="q-block-title">解析</div>
                  <div class="q-block-content analysis">{{ q.analysis || q.explanation || '—' }}</div>
                </div>
                <div v-if="q.keywords || q.points" class="q-block">
                  <div class="q-block-title">关键点</div>
                  <div class="tag-row fx-stagger">
                    <el-tag
                      v-for="k in asArray(q.keywords || q.points)"
                      :key="k"
                      effect="plain"
                      size="small"
                      class="kw-tag"
                    >
                      {{ k }}
                    </el-tag>
                  </div>
                </div>
              </div>
            </el-collapse-item>
          </el-collapse>
        </el-tab-pane>
      </el-tabs>
    </div>

    <el-empty
      v-else
      description="生成题库后将按分类展示，支持折叠查看答案与解析"
    />

    <RoleSelector v-model="roleSelectorVisible" @select="handleRoleSelect" />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Promotion, Delete, MagicStick, ChatDotRound, Aim, Document, Grid, Connection, Box, CircleCheckFilled } from '@element-plus/icons-vue'
import { generateQuestions } from '@/api/agents'
import { useAppStore, type JobProfile, type Question } from '@/stores/app'
import RoleSelector from '@/components/effects/RoleSelector.vue'
import type { RoleCard } from '@/types/role_card'

const router = useRouter()
const appStore = useAppStore()

const jobProfileText = ref('')
const loading = ref(false)
const generating = ref(false)
const progressPercent = ref(0)
const progressStatus = ref<'success' | 'exception' | ''>('')
const currentStepIndex = ref(-1)
const progressSteps = ref([
  { name: '分析岗位', desc: '解析岗位技术栈和要求', done: false },
  { name: '生成八股', desc: '生成基础知识面试题', done: false },
  { name: '生成算法', desc: '生成算法面试题', done: false },
  { name: '生成系统设计', desc: '生成系统设计面试题', done: false },
  { name: '生成项目题', desc: '生成项目深挖面试题', done: false },
])
const activeTab = ref('basic')
const questionBank = ref<Record<string, any[]>>({})

const roleSelectorVisible = ref(false)

function handleRoleSelect(card: RoleCard) {
  appStore.setActiveCard(card)
  ElMessage.success(`已选择「${card.role_name}」`)
}

// 页面加载时自动填充岗位画像和已生成的题库
onMounted(() => {
  if (appStore.currentJobProfile) {
    jobProfileText.value = JSON.stringify(appStore.currentJobProfile, null, 2)
  }
  if (appStore.questionBank && appStore.questionBank.length > 0) {
    questionBank.value = questionsToBank(appStore.questionBank)
  }

  // 恢复已完成的后台任务结果（题库生成）
  const task = appStore.backgroundTasks.find(
    t => t.type === 'question-bank' && t.status === 'completed' && t.result
  )
  if (task?.result) {
    questionBank.value = normalize(task.result)
    const allQuestions: Question[] = categories.flatMap(c =>
      getCategoryQuestions(c.key).map((q: any) => ({
        category: q.category || c.key,
        difficulty: q.difficulty || '中等',
        question: q.question || q.title || '',
        answer: q.answer || '',
        explanation: q.explanation || q.analysis || '',
        tags: q.tags || q.keywords || [],
      }))
    )
    appStore.setQuestionBank(allQuestions)
    const first = categories.find((c) => getCategoryQuestions(c.key).length)
    if (first) activeTab.value = first.key
  }
})

const iconMap: Record<string, any> = {
  document: Document,
  grid: Grid,
  connection: Connection,
  box: Box
}

const categories = [
  { key: 'basic', label: '八股文', icon: 'document' },
  { key: 'algorithm', label: '算法', icon: 'grid' },
  { key: 'system_design', label: '系统设计', icon: 'connection' },
  { key: 'project', label: '项目深挖', icon: 'box' }
]

function questionsToBank(questions: any[] | null | undefined): Record<string, any[]> {
  const result: Record<string, any[]> = {
    basic: [],
    algorithm: [],
    system_design: [],
    project: []
  }
  if (!questions || !questions.length) return result
  const keyMap: Record<string, string> = {
    八股文: 'basic',
    八股: 'basic',
    basic: 'basic',
    算法: 'algorithm',
    algorithm: 'algorithm',
    系统设计: 'system_design',
    system_design: 'system_design',
    项目深挖: 'project',
    project: 'project',
    项目: 'project'
  }
  for (const q of questions) {
    const cat = keyMap[String(q.category || '').toLowerCase()] || 'basic'
    result[cat].push(q)
  }
  return result
}

const sampleProfile = JSON.stringify(
  {
    position: '后端开发工程师',
    tech_stack: ['Java', 'Spring Boot', 'MySQL', 'Redis', 'Kafka'],
    experience_years: '3-5年',
    core_skills: ['高并发', '分布式', '性能优化'],
    soft_skills: ['沟通协作', '责任心'],
    bonus_items: ['云原生', 'K8s']
  },
  null,
  2
)

const totalQuestions = computed(() =>
  categories.reduce((sum, c) => sum + (questionBank.value[c.key]?.length || 0), 0)
)

const hasQuestions = computed(() => totalQuestions.value > 0)

function loadSample() {
  jobProfileText.value = sampleProfile
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

function getCategoryQuestions(key: string): any[] {
  return questionBank.value[key] || []
}

function asArray(val: any): string[] {
  if (!val) return []
  if (Array.isArray(val)) return val
  if (typeof val === 'string') return val.split(/[,，、]/).map((s) => s.trim()).filter(Boolean)
  return [String(val)]
}

function difficultyType(d?: string): 'success' | 'warning' | 'danger' | 'info' {
  const v = (d || '').toLowerCase()
  if (v.includes('简') || v.includes('easy') || v.includes('初')) return 'success'
  if (v.includes('中') || v.includes('medium') || v.includes('mid')) return 'warning'
  if (v.includes('难') || v.includes('hard') || v.includes('高')) return 'danger'
  return 'info'
}

function parseProfile(): JobProfile | null {
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

// 将后端返回的题库结构归一化到 categories
function normalize(raw: any): Record<string, any[]> {
  const result: Record<string, any[]> = {
    basic: [],
    algorithm: [],
    system_design: [],
    project: []
  }
  if (!raw) return result

  // 情况1：直接是 { basic: [...], algorithm: [...] }
  for (const c of categories) {
    if (Array.isArray(raw[c.key])) {
      result[c.key] = raw[c.key]
    }
  }
  if (Object.values(result).some((arr) => arr.length)) return result

  // 情况2：{ questions: [...] } 每条带 category 字段
  const list = Array.isArray(raw) ? raw : raw.questions || raw.items || []
  const keyMap: Record<string, string> = {
    八股文: 'basic',
    八股: 'basic',
    basic: 'basic',
    算法: 'algorithm',
    algorithm: 'algorithm',
    系统设计: 'system_design',
    system_design: 'system_design',
    项目深挖: 'project',
    project: 'project',
    项目: 'project'
  }
  for (const q of list) {
    const cat = keyMap[String(q.category || q.type || '').toLowerCase()] || 'basic'
    result[cat].push(q)
  }
  return result
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

function processResult(res: any) {
  questionBank.value = normalize(res?.question_bank ?? res)
  const allQuestions: Question[] = categories.flatMap(c =>
    getCategoryQuestions(c.key).map((q: any) => ({
      category: q.category || c.key,
      difficulty: q.difficulty || '中等',
      question: q.question || q.title || '',
      answer: q.answer || '',
      explanation: q.explanation || q.analysis || '',
      tags: q.tags || q.keywords || [],
    }))
  )
  appStore.setQuestionBank(allQuestions)
  const first = categories.find((c) => getCategoryQuestions(c.key).length)
  if (first) activeTab.value = first.key
  return allQuestions
}

async function handleGenerate() {
  let profile: any
  let cardName = ''

  // 如果有选中的角色卡，基于角色卡生成
  if (appStore.activeCard) {
    const card = appStore.activeCard
    profile = {
      position: card.role_name,
      tech_stack: card.tech_stack,
      core_skills: card.core_skills,
      experience_years: card.experience_years,
      education: card.education,
      interview_directions: card.interview_directions,
    }
    cardName = card.role_name
  } else {
    profile = parseProfile()
    if (!profile) return
  }

  if (!resumeTextFromStore()) {
    ElMessage.warning('请先上传或输入简历')
    return
  }

  // 创建后台任务
  const taskId = `question-bank-${Date.now()}`
  appStore.addBackgroundTask({
    id: taskId,
    type: 'question-bank',
    title: '题库生成中...',
    progress: 0,
    result: null,
  })

  generating.value = true
  questionBank.value = {}
  startProgressSimulation()

  // 模拟进度更新
  const progressInterval = setInterval(() => {
    if (currentStepIndex.value < progressSteps.value.length) {
      progressSteps.value[currentStepIndex.value].done = true
      currentStepIndex.value++
      progressPercent.value = Math.min(95, currentStepIndex.value * 20)
    }
  }, 1500)

  // 使用原始简历
  const resumeText = resumeTextFromStore()

  // 后台执行生成
  generateQuestions(profile, resumeText)
    .then((res: any) => {
      clearInterval(progressInterval)
      finishProgress(true)

      const allQuestions = processResult(res)

      // 更新任务状态
      appStore.updateBackgroundTask(taskId, {
        status: 'completed',
        title: '题库生成完成',
        progress: 100,
        completedAt: new Date().toISOString(),
        result: res?.question_bank ?? res,
      })

      const msg = cardName
        ? `基于「${cardName}」生成题库完成，共 ${totalQuestions.value} 题`
        : `题库生成完成，共 ${totalQuestions.value} 题，可直接去模拟面试使用`
      ElMessage.success(msg)
    })
    .catch((err: any) => {
      clearInterval(progressInterval)
      finishProgress(false)

      appStore.updateBackgroundTask(taskId, {
        status: 'failed',
        title: '题库生成失败',
        completedAt: new Date().toISOString(),
        error: err?.message || '生成失败',
      })

      ElMessage.error('题库生成失败，请重试')
    })
    .finally(() => {
      setTimeout(() => {
        generating.value = false
      }, 500)
    })
}

function resumeTextFromStore(): string {
  return appStore.currentResume || ''
}

function resetAll() {
  jobProfileText.value = ''
  questionBank.value = {}
  appStore.setQuestionBank(null)
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
  background: linear-gradient(180deg, #c4b5fd, #8b5cf6);
  flex-shrink: 0;
  box-shadow: 0 0 10px var(--bc-violet-glow);
}

.config-panel {
  margin-bottom: var(--bc-space-5);
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--bc-space-4);
}

.panel-title {
  font-size: var(--bc-font-size-lg);
  font-weight: 600;
  color: var(--bc-text);
  display: flex;
  align-items: center;
  gap: var(--bc-space-2);
}

.title-bar-sm {
  width: 3px;
  height: 16px;
  border-radius: 2px;
  background: linear-gradient(180deg, #c4b5fd, #8b5cf6);
  flex-shrink: 0;
  box-shadow: 0 0 6px var(--bc-violet-glow);
}

.header-actions {
  display: flex;
  gap: var(--bc-space-2);
  align-items: center;
}

.profile-textarea :deep(.el-textarea__inner) {
  background: var(--bc-bg-soft);
  border-color: var(--bc-border);
  color: var(--bc-text);
  border-radius: var(--bc-radius-sm);
  transition: border-color 0.2s var(--bc-ease);
  font-family: 'JetBrains Mono', 'Fira Code', Consolas, Monaco, monospace;
  font-size: var(--bc-font-size-sm);
}

.profile-textarea :deep(.el-textarea__inner:focus) {
  border-color: var(--bc-primary);
  box-shadow: 0 0 0 2px var(--bc-primary-glow);
}

.profile-textarea :deep(.el-textarea__inner::placeholder) {
  color: var(--bc-text-muted);
}

.card-preview {
  background: var(--bc-bg-soft);
  border-radius: var(--bc-radius-sm);
  padding: var(--bc-space-4);
  margin-bottom: var(--bc-space-4);
  border: 1px solid var(--bc-border-soft);
}

.preview-item {
  display: flex;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: var(--bc-space-2);
  margin-bottom: var(--bc-space-3);
}

.preview-item:last-child {
  margin-bottom: 0;
}

.preview-label {
  font-weight: 500;
  color: var(--bc-text-soft);
  font-size: var(--bc-font-size-base);
  flex-shrink: 0;
}

.preview-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--bc-space-2);
}

.preview-tag {
  margin: 0;
  cursor: default;
}

.actions {
  margin-top: var(--bc-space-4);
  display: flex;
  align-items: center;
  gap: var(--bc-space-3);
}

.count {
  margin-left: auto;
  color: var(--bc-text-soft);
  font-size: var(--bc-font-size-sm);
}

.result-panel {
  margin-bottom: var(--bc-space-5);
}

.q-tabs :deep(.el-tabs__item) {
  color: var(--bc-text-soft);
  font-size: var(--bc-font-size-base);
}
.q-tabs :deep(.el-tabs__item.is-active) {
  color: var(--bc-primary);
}
.q-tabs :deep(.el-tabs__active-bar) {
  background: linear-gradient(90deg, var(--bc-primary), var(--bc-accent));
}

.tab-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.cat-icon {
  font-size: 14px;
  color: #a1a1aa;
}

.tab-badge :deep(.el-badge__content) {
  background: var(--bc-primary);
}

.q-collapse {
  border: none;
  background: transparent;
}

.q-collapse :deep(.el-collapse-item) {
  border: 1px solid var(--bc-border);
  border-radius: var(--bc-radius-sm);
  margin-bottom: var(--bc-space-3);
  background: var(--bc-bg-soft);
  overflow: hidden;
}

.q-collapse :deep(.el-collapse-item__header) {
  background: transparent;
  border-bottom: 1px solid var(--bc-border);
  color: var(--bc-text);
  padding: 0 var(--bc-space-4);
  height: 52px;
  line-height: 52px;
}

.q-collapse :deep(.el-collapse-item__wrap) {
  background: transparent;
  border-bottom: none;
}

.q-collapse :deep(.el-collapse-item__content) {
  padding: var(--bc-space-3) var(--bc-space-4);
  color: var(--bc-text);
}

.q-title-row {
  display: flex;
  align-items: center;
  gap: var(--bc-space-2);
  width: 100%;
  padding-right: var(--bc-space-3);
}

.q-diff {
  flex-shrink: 0;
}

/* 难度标签颜色 - 绿橙红区分 */
.q-diff.el-tag--success {
  background-color: rgba(34, 197, 94, 0.15) !important;
  border-color: rgba(34, 197, 94, 0.4) !important;
  color: #4ade80 !important;
}

.q-diff.el-tag--warning {
  background-color: rgba(249, 115, 22, 0.15) !important;
  border-color: rgba(249, 115, 22, 0.4) !important;
  color: #fb923c !important;
}

.q-diff.el-tag--danger {
  background-color: rgba(239, 68, 68, 0.15) !important;
  border-color: rgba(239, 68, 68, 0.4) !important;
  color: #f87171 !important;
}

.q-diff.el-tag--info {
  background-color: rgba(161, 161, 170, 0.15) !important;
  border-color: rgba(161, 161, 170, 0.4) !important;
  color: #a1a1aa !important;
}

/* Tab badge 数字颜色修复 */
.tab-badge :deep(.el-badge__content) {
  background: rgba(255, 255, 255, 0.15) !important;
  color: #ffffff !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  text-shadow: none !important;
}

.q-index {
  color: var(--bc-text-soft);
  flex-shrink: 0;
  font-weight: 500;
}

.q-stem {
  color: var(--bc-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}

.q-body {
  padding: 4px 8px 8px;
}

.q-block {
  margin-bottom: var(--bc-space-4);
}

.q-block:last-child {
  margin-bottom: 0;
}

.q-block-title {
  font-size: var(--bc-font-size-sm);
  font-weight: 600;
  color: var(--bc-primary);
  margin-bottom: var(--bc-space-2);
  display: flex;
  align-items: center;
  gap: var(--bc-space-2);
}

.q-block-title::before {
  content: '';
  width: 3px;
  height: 14px;
  border-radius: 2px;
  background: linear-gradient(180deg, var(--bc-primary), var(--bc-accent));
}

.q-block-content {
  line-height: 1.8;
  color: var(--bc-text);
  white-space: pre-wrap;
  word-break: break-word;
  font-size: var(--bc-font-size-sm);
  padding-left: var(--bc-space-3);
}

.q-block-content.answer {
  color: #9dd6ff;
}

.q-block-content.analysis {
  color: var(--bc-text-soft);
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--bc-space-2);
  padding-left: var(--bc-space-3);
}

.kw-tag {
  margin: 0;
  cursor: default;
}

@media (max-width: 768px) {
  .header-actions {
    flex-wrap: wrap;
  }

  .actions {
    flex-direction: column;
    align-items: stretch;
  }

  .actions .el-button {
    width: 100%;
  }

  .count {
    margin-left: 0;
    text-align: center;
  }
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
  flex-wrap: wrap;
  gap: var(--bc-space-2);
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
  flex-shrink: 0;
}

.step-item.active .step-dot {
  background: linear-gradient(135deg, #c4b5fd, #8b5cf6);
  border-color: #c4b5fd;
  color: #fff;
  box-shadow: 0 0 10px var(--bc-violet-glow);
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

@media (max-width: 768px) {
  .progress-steps {
    flex-direction: column;
    gap: var(--bc-space-2);
    padding: 0;
  }
}
</style>
