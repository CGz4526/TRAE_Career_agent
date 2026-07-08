import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { RoleCard } from '@/types/role_card'
import presetCardsData from '@/data/preset_role_cards.json'

/** 岗位画像类型 */
export interface JobProfile {
  position?: string
  tech_stack?: string[]
  experience_years?: string | number
  education?: string
  core_skills?: string[]
  soft_skills?: string[]
  bonus_items?: string[]
  key_responsibilities?: string[]
  [key: string]: any
}

// RoleCard 类型统一从 @/types/role_card 导入，避免字段冲突

/** 面试题类型 */
export interface Question {
  category: string
  difficulty: string
  question: string
  answer: string
  explanation?: string
  tags?: string[]
}

const STORAGE_KEY = 'career-agent-data'
const HISTORY_KEY = 'career-agent-interview-history'
const ACTIVE_CARD_KEY = 'career-agent-active-card'

export interface BackgroundTask {
  id: string
  type: 'interview-report' | 'resume-optimize' | 'question-bank'
  title: string
  status: 'running' | 'completed' | 'failed'
  progress?: number
  createdAt: string
  completedAt?: string
  result?: any
  error?: string
  relatedId?: string
}

export interface InterviewRecord {
  id: string
  jobProfile: JobProfile | null
  startedAt: string
  finishedAt?: string
  status: 'ongoing' | 'completed'
  messages: { role: 'interviewer' | 'user'; content: string }[]
  report?: any
  questionReviews?: any[]
  sessionId?: string
  resumeText?: string
}

interface PersistData {
  jdText: string
  jobProfile: JobProfile | null
  resumeText: string
  optimizedResume: string
  questionBank: Question[] | null
  projectDesc: string
  projectStory: any | null
  activeCard: RoleCard | null
}

function loadFromStorage(): Partial<PersistData> {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return {}
    return JSON.parse(raw)
  } catch {
    return {}
  }
}

function saveToStorage(data: PersistData) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data))
  } catch {
    // ignore quota errors
  }
}

export const useAppStore = defineStore('app', () => {
  const persisted = loadFromStorage()

  // 页面标题
  const pageTitle = ref<string>('工作台')
  // 全局 loading
  const loading = ref<boolean>(false)

  // ====== 角色卡状态 ======
  /** 预设角色卡列表 */
  const presetCards = ref<RoleCard[]>(presetCardsData as RoleCard[])
  /** 当前活跃角色卡 */
  const activeCard = ref<RoleCard | null>(persisted.activeCard || loadActiveCard())

  function loadActiveCard(): RoleCard | null {
    try {
      const raw = localStorage.getItem(ACTIVE_CARD_KEY)
      if (!raw) return null
      return JSON.parse(raw)
    } catch {
      return null
    }
  }

  function saveActiveCard(card: RoleCard | null) {
    if (card) {
      localStorage.setItem(ACTIVE_CARD_KEY, JSON.stringify(card))
    } else {
      localStorage.removeItem(ACTIVE_CARD_KEY)
    }
  }

  function setActiveCard(card: RoleCard | null) {
    activeCard.value = card
    saveActiveCard(card)
  }

  function clearActiveCard() {
    activeCard.value = null
    saveActiveCard(null)
  }

  // ====== 跨模块共享数据 ======
  /** JD 原始文本 */
  const jdText = ref<string>(persisted.jdText || '')
  /** 岗位需求画像（岗位匹配 Agent 产出） */
  const currentJobProfile = ref<JobProfile | null>(persisted.jobProfile || null)
  /** 原始简历文本 */
  const currentResume = ref<string>(persisted.resumeText || '')
  /** 优化后简历（简历优化 Agent 产出） */
  const optimizedResume = ref<string>(persisted.optimizedResume || '')
  /** 题库（题库生成 Agent 产出） */
  const questionBank = ref<Question[] | null>(persisted.questionBank || null)
  /** 项目描述原文 */
  const projectDesc = ref<string>(persisted.projectDesc || '')
  /** 项目梳理结果（STAR） */
  const projectStory = ref<any | null>(persisted.projectStory || null)

  // ====== 时间戳（用于展示"已生成"状态） ======
  const jobProfileTime = ref<string>(persisted.jobProfile ? '已生成' : '')
  const resumeTime = ref<string>(persisted.optimizedResume ? '已优化' : '')
  const questionBankTime = ref<string>(persisted.questionBank ? '已生成' : '')

  // ====== 计算属性：各模块数据是否就绪 ======
  const hasJobProfile = computed(() => !!currentJobProfile.value)
  const hasResume = computed(() => !!optimizedResume.value || !!currentResume.value)
  const hasQuestionBank = computed(() => !!questionBank.value && questionBank.value.length > 0)

  /** 求职准备完成度（0-4） */
  const progressStep = computed(() => {
    let step = 0
    if (hasJobProfile.value) step++
    if (hasResume.value) step++
    if (hasQuestionBank.value) step++
    // 面试需要手动进行，不计入自动进度
    return step
  })

  // ====== Actions ======
  function setPageTitle(title: string) {
    pageTitle.value = title
  }

  function setLoading(val: boolean) {
    loading.value = val
  }

  function setJdText(text: string) {
    jdText.value = text
    persist()
  }

  function setJobProfile(profile: JobProfile | null) {
    currentJobProfile.value = profile
    jobProfileTime.value = profile ? '已生成' : ''
    persist()
  }

  function setResume(resume: string) {
    currentResume.value = resume
    persist()
  }

  function setOptimizedResume(resume: string) {
    optimizedResume.value = resume
    resumeTime.value = resume ? '已优化' : ''
    persist()
  }

  function setQuestionBank(questions: Question[] | null) {
    questionBank.value = questions
    questionBankTime.value = questions && questions.length ? '已生成' : ''
    persist()
  }

  function setProjectDesc(desc: string) {
    projectDesc.value = desc
    persist()
  }

  function setProjectStory(story: any | null) {
    projectStory.value = story
    persist()
  }

  /** 清除所有数据 */
  function clearAll() {
    jdText.value = ''
    currentJobProfile.value = null
    currentResume.value = ''
    optimizedResume.value = ''
    questionBank.value = null
    projectDesc.value = ''
    projectStory.value = null
    jobProfileTime.value = ''
    resumeTime.value = ''
    questionBankTime.value = ''
    persist()
  }

  // ====== 后台任务管理 ======
  const backgroundTasks = ref<BackgroundTask[]>([])

  const runningTasks = computed(() =>
    backgroundTasks.value.filter(t => t.status === 'running')
  )

  const hasRunningTasks = computed(() => runningTasks.value.length > 0)

  function addBackgroundTask(task: Omit<BackgroundTask, 'createdAt' | 'status'> & { status?: BackgroundTask['status'] }) {
    const newTask: BackgroundTask = {
      createdAt: new Date().toISOString(),
      status: 'running',
      ...task,
    }
    backgroundTasks.value.unshift(newTask)
    return newTask
  }

  function updateBackgroundTask(id: string, updates: Partial<BackgroundTask>) {
    const idx = backgroundTasks.value.findIndex(t => t.id === id)
    if (idx >= 0) {
      backgroundTasks.value[idx] = { ...backgroundTasks.value[idx], ...updates }
    }
  }

  function removeBackgroundTask(id: string) {
    backgroundTasks.value = backgroundTasks.value.filter(t => t.id !== id)
  }

  function clearCompletedTasks() {
    backgroundTasks.value = backgroundTasks.value.filter(t => t.status === 'running')
  }

  function getBackgroundTask(id: string): BackgroundTask | undefined {
    return backgroundTasks.value.find(t => t.id === id)
  }

  // ====== 面试历史记录 ======
  const interviewHistory = ref<InterviewRecord[]>(loadInterviewHistory())

  function loadInterviewHistory(): InterviewRecord[] {
    try {
      const raw = localStorage.getItem(HISTORY_KEY)
      if (!raw) return []
      return JSON.parse(raw)
    } catch {
      return []
    }
  }

  function saveInterviewHistory() {
    try {
      localStorage.setItem(HISTORY_KEY, JSON.stringify(interviewHistory.value))
    } catch {
      // ignore
    }
  }

  function addInterviewRecord(record: InterviewRecord) {
    interviewHistory.value.unshift(record)
    saveInterviewHistory()
  }

  function updateInterviewRecord(id: string, updates: Partial<InterviewRecord>) {
    const idx = interviewHistory.value.findIndex(r => r.id === id)
    if (idx >= 0) {
      interviewHistory.value[idx] = { ...interviewHistory.value[idx], ...updates }
      saveInterviewHistory()
    }
  }

  function getInterviewRecord(id: string): InterviewRecord | undefined {
    return interviewHistory.value.find(r => r.id === id)
  }

  function deleteInterviewRecord(id: string) {
    interviewHistory.value = interviewHistory.value.filter(r => r.id !== id)
    saveInterviewHistory()
  }

  function persist() {
    saveToStorage({
      jdText: jdText.value,
      jobProfile: currentJobProfile.value,
      resumeText: currentResume.value,
      optimizedResume: optimizedResume.value,
      questionBank: questionBank.value,
      projectDesc: projectDesc.value,
      projectStory: projectStory.value,
    })
  }

  return {
    // state
    pageTitle,
    loading,
    jdText,
    currentJobProfile,
    currentResume,
    optimizedResume,
    questionBank,
    projectDesc,
    projectStory,
    jobProfileTime,
    resumeTime,
    questionBankTime,
    interviewHistory,
    backgroundTasks,
    // 角色卡
    presetCards,
    activeCard,
    // computed
    hasJobProfile,
    hasResume,
    hasQuestionBank,
    progressStep,
    runningTasks,
    hasRunningTasks,
    // actions
    setPageTitle,
    setLoading,
    setJdText,
    setJobProfile,
    setResume,
    setOptimizedResume,
    setQuestionBank,
    setProjectDesc,
    setProjectStory,
    setActiveCard,
    clearActiveCard,
    clearAll,
    addInterviewRecord,
    updateInterviewRecord,
    getInterviewRecord,
    deleteInterviewRecord,
    addBackgroundTask,
    updateBackgroundTask,
    removeBackgroundTask,
    clearCompletedTasks,
    getBackgroundTask,
  }
})
