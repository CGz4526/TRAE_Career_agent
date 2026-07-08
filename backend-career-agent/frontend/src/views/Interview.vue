<template>
  <div class="page-container">
    <h1 class="page-title">
      <span class="title-bar"></span>
      <span class="fx-gradient-text">模拟面试</span>
    </h1>
    <p class="page-subtitle" v-if="appStore.activeCard">
      已选择「{{ appStore.activeCard.role_name }}」，AI 面试官将围绕该岗位进行多轮对话追问
    </p>
    <p class="page-subtitle" v-else>
      AI 面试官多轮对话追问，结束后输出多维评分与改进建议
    </p>

    <div v-if="!started" class="section-card setup-panel">
      <div v-if="appStore.activeCard" class="card-tip-banner fx-aurora-border">
        <div class="tip-icon" :style="{ background: getRoleColor(appStore.activeCard.icon) }">
          {{ getRoleIcon(appStore.activeCard.icon) }}
        </div>
        <div class="tip-content">
          <h4>{{ appStore.activeCard.role_name }}</h4>
          <p>{{ appStore.activeCard.description }}</p>
          <div class="tech-preview fx-stagger">
            <el-tag
              v-for="tech in appStore.activeCard.tech_stack.slice(0, 6)"
              :key="tech"
              size="small"
              effect="plain"
            >
              {{ tech }}
            </el-tag>
          </div>
        </div>
        <el-button type="primary" :icon="Aim" @click="roleSelectorVisible = true">
          切换方向
        </el-button>
      </div>

      <div v-else class="no-card-banner">
        <el-icon :size="24" color="#6366f1"><InfoFilled /></el-icon>
        <span>未选择面试方向</span>
        <el-button type="primary" size="small" :icon="Aim" @click="roleSelectorVisible = true">
          选择面试方向
        </el-button>
      </div>

      <div v-if="appStore.hasJobProfile || appStore.hasResume" class="auto-fill-banner">
        <el-icon class="banner-icon"><MagicStick /></el-icon>
        <span class="banner-text">
          已自动填充：
          <el-tag v-if="appStore.hasJobProfile" size="small" type="primary" effect="dark">岗位画像</el-tag>
          <el-tag v-if="appStore.hasResume" size="small" type="success" effect="dark">简历</el-tag>
          <el-tag v-if="appStore.hasQuestionBank" size="small" type="warning" effect="plain">题库已生成</el-tag>
        </span>
      </div>

      <div class="panel-header">
        <span class="panel-title">
          <span class="title-bar-sm"></span>
          <template v-if="appStore.activeCard">基于角色卡面试</template>
          <template v-else>面试配置</template>
        </span>
        <div class="header-actions" v-if="!appStore.activeCard">
          <el-button text type="primary" :icon="MagicStick" @click="fillFromStore">
            从岗位匹配导入
          </el-button>
          <el-button text @click="loadSample">载入示例</el-button>
        </div>
      </div>

      <el-form label-position="top" class="setup-form">
        <el-form-item v-if="!appStore.activeCard" label="岗位画像 JSON">
          <el-input
            v-model="jobProfileText"
            type="textarea"
            :rows="7"
            placeholder='请粘贴岗位画像 JSON，例如 {"position":"后端工程师","tech_stack":["Java","MySQL"],...}'
            class="mono profile-textarea"
          />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="appStore.activeCard ? 24 : 12" :xs="24" :md="appStore.activeCard ? 24 : 12">
            <el-form-item label="简历文本（可选，提升针对性）">
              <el-input
                v-model="resumeText"
                type="textarea"
                :rows="4"
                placeholder="粘贴简历以让面试官围绕你的项目追问（可选）"
                class="resume-textarea"
              />
            </el-form-item>
          </el-col>
          <el-col v-if="!appStore.activeCard" :span="12" :xs="24" :md="12">
            <el-form-item label="已有题库（可选，默认不使用）">
              <div style="position: relative;">
                <el-input
                  v-model="questionBankText"
                  type="textarea"
                  :rows="4"
                  placeholder="留空则面试官动态出题，题目与题库不重复"
                  class="mono bank-textarea"
                />
                <el-button
                  v-if="appStore.hasQuestionBank && !questionBankText"
                  text
                  type="primary"
                  size="small"
                  style="position: absolute; top: 6px; right: 8px;"
                  @click="importQuestionBank"
                >
                  从题库导入
                </el-button>
              </div>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>

      <div class="actions">
        <el-button
          type="primary"
          size="large"
          :loading="starting"
          :icon="VideoPlay"
          class="fx-shine start-btn"
          @click="handleStart"
        >
          启动面试
        </el-button>
      </div>
    </div>

    <div v-else class="chat-wrap section-card">
      <div class="chat-header">
        <div class="chat-info">
          <el-tag type="success" effect="dark" round class="fx-pulse">面试进行中</el-tag>
          <span class="session-id">会话 ID：{{ sessionId || '—' }}</span>
        </div>
        <div class="chat-actions">
          <el-button
            type="danger"
            plain
            :icon="Document"
            :loading="reporting"
            @click="handleReport"
          >
            生成报告
          </el-button>
          <el-button :icon="RefreshLeft" @click="handleReset">重新开始</el-button>
        </div>
      </div>

      <div ref="chatBoxRef" class="chat-box">
        <div
          v-for="(msg, i) in messages"
          :key="i"
          class="msg-row"
          :class="msg.role"
        >
          <div class="avatar">
            <el-icon v-if="msg.role === 'interviewer'"><Avatar /></el-icon>
            <el-icon v-else><User /></el-icon>
          </div>
          <div class="bubble">
            <div class="bubble-role">{{ msg.role === 'interviewer' ? '面试官' : '我' }}</div>
            <div class="bubble-text">{{ msg.content }}</div>
          </div>
        </div>
        <div v-if="chatting" class="msg-row interviewer">
          <div class="avatar"><el-icon><Avatar /></el-icon></div>
          <div class="bubble">
            <div class="bubble-role">面试官</div>
            <div class="bubble-text typing">正在思考下一个问题<span class="dots"><i></i><i></i><i></i></span></div>
          </div>
        </div>
      </div>

      <div class="chat-input">
        <el-input
          v-model="answer"
          type="textarea"
          :rows="2"
          placeholder="输入你的回答，按 Ctrl+Enter 发送..."
          resize="none"
          :disabled="chatting"
          class="input-textarea"
          @keydown.ctrl.enter.prevent="handleSend"
          @keydown.meta.enter.prevent="handleSend"
        />
        <el-button
          type="primary"
          :loading="chatting"
          :icon="Promotion"
          :disabled="!answer.trim()"
          class="fx-shine send-btn"
          @click="handleSend"
        >
          发送
        </el-button>
      </div>
    </div>

    <el-dialog
      v-model="reportVisible"
      title="面试评估报告"
      width="820px"
      align-center
      destroy-on-close
      class="report-dialog"
    >
      <el-tabs v-model="reportTab" class="report-tabs">
        <el-tab-pane label="总览评分" name="overview">
          <div v-if="report" class="report-body">
            <div class="report-overview">
              <div class="score-ring">
                <el-progress
                  type="dashboard"
                  :percentage="overallScore"
                  :width="140"
                  :color="scoreColor(overallScore)"
                >
                  <template #default>
                    <div class="ring-inner">
                      <div class="ring-num fx-gradient-text">{{ overallScore }}</div>
                      <div class="ring-label">综合评分</div>
                    </div>
                  </template>
                </el-progress>
              </div>
              <div class="overview-text">
                <div class="overview-title">{{ report.summary || report.overall_comment || '面试评估完成' }}</div>
                <div class="overview-sub">{{ report.conclusion || report.recommendation || '' }}</div>
                <el-tag v-if="report.level" effect="dark" :type="levelType(report.level)">
                  评级：{{ report.level }}
                </el-tag>
              </div>
            </div>

            <el-divider />

            <div class="dim-section">
              <div class="dim-title">
                <span class="title-bar-sm"></span>
                维度评分
              </div>
              <div class="dim-grid fx-stagger">
                <div v-for="d in dimensions" :key="d.name" class="dim-item section-card fx-glass-soft">
                  <div class="dim-head">
                    <span class="dim-name">{{ d.name }}</span>
                    <span class="dim-score fx-count" :style="{ color: scoreColor(d.score) }">{{ d.score }}</span>
                  </div>
                  <el-progress
                    :percentage="d.score"
                    :color="scoreColor(d.score)"
                    :stroke-width="10"
                    :show-text="false"
                  />
                  <div class="dim-comment">{{ d.comment || '' }}</div>
                </div>
              </div>
            </div>

            <el-divider />

            <div class="dim-section">
              <div class="dim-title">
                <span class="title-bar-sm"></span>
                改进建议
              </div>
              <div v-if="improvements.length" class="improve-list fx-stagger">
                <div v-for="(it, i) in improvements" :key="i" class="improve-item section-card fx-glass-soft">
                  <el-icon class="improve-icon"><WarningFilled /></el-icon>
                  <span>{{ it }}</span>
                </div>
              </div>
              <el-empty v-else description="暂无改进建议" :image-size="80" />
            </div>
          </div>
        </el-tab-pane>

        <el-tab-pane :label="`逐题回顾 (${questionReviews.length})`" name="reviews">
          <div v-if="questionReviews.length" class="reviews-body fx-stagger">
            <div
              v-for="(rev, idx) in questionReviews"
              :key="idx"
              class="review-card section-card"
            >
              <div class="review-header">
                <el-tag size="small" :type="rev.is_correct ? 'success' : 'danger'" effect="dark">
                  {{ rev.is_correct ? '✓ 回答正确' : '✗ 回答有误' }}
                </el-tag>
                <span class="review-q-num">第 {{ idx + 1 }} 题</span>
              </div>
              <div class="review-question">
                <span class="q-label">问题：</span>
                <span class="q-text">{{ rev.question }}</span>
              </div>
              <div class="review-answer">
                <span class="q-label">你的回答：</span>
                <span class="q-text answer-text">{{ rev.candidate_answer }}</span>
              </div>
              <div class="review-standard">
                <div class="review-block-title">
                  <el-icon color="#2ecc71"><CircleCheck /></el-icon>
                  <span>参考答案</span>
                </div>
                <div class="review-block-content standard-text">
                  {{ rev.standard_answer }}
                </div>
              </div>
              <div v-if="rev.error_correction" class="review-correction">
                <div class="review-block-title">
                  <el-icon color="#e74c3c"><Warning /></el-icon>
                  <span>错误纠正</span>
                </div>
                <div class="review-block-content correction-text">
                  {{ rev.error_correction }}
                </div>
              </div>
            </div>
          </div>
          <el-empty v-else description="暂无逐题回顾数据" :image-size="80" />
        </el-tab-pane>
      </el-tabs>
      <template #footer>
        <el-button @click="reportVisible = false">关闭</el-button>
        <el-button type="primary" class="fx-shine" @click="handleReset">再来一次</el-button>
      </template>
    </el-dialog>

    <RoleSelector v-model="roleSelectorVisible" @select="handleRoleSelect" />
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  VideoPlay,
  Promotion,
  Document,
  RefreshLeft,
  MagicStick,
  Avatar,
  User,
  WarningFilled,
  CircleCheck,
  Warning,
  Aim,
  InfoFilled
} from '@element-plus/icons-vue'
import {
  interviewStart,
  interviewChat,
  interviewReport
} from '@/api/agents'
import { useAppStore, type JobProfile } from '@/stores/app'
import { getRoleIcon, getRoleColor } from '@/types/role_card'
import RoleSelector from '@/components/effects/RoleSelector.vue'
import type { RoleCard } from '@/types/role_card'

const router = useRouter()
const appStore = useAppStore()

interface ChatMessage {
  role: 'interviewer' | 'user'
  content: string
}

const jobProfileText = ref('')
const resumeText = ref('')
const questionBankText = ref('')

const started = ref(false)
const starting = ref(false)
const chatting = ref(false)
const reporting = ref(false)

const sessionId = ref('')
const currentRecordId = ref('')
const messages = ref<ChatMessage[]>([])
const answer = ref('')

const chatBoxRef = ref<HTMLElement | null>(null)

const reportVisible = ref(false)
const report = ref<any>(null)
const reportTab = ref('overview')

const roleSelectorVisible = ref(false)

function handleRoleSelect(card: RoleCard) {
  appStore.setActiveCard(card)
  ElMessage.success(`已选择「${card.role_name}」`)
}

// 页面加载时自动填充已有数据
onMounted(() => {
  if (appStore.currentJobProfile) {
    jobProfileText.value = JSON.stringify(appStore.currentJobProfile, null, 2)
  }
  // 自动填充原始简历
  if (appStore.currentResume) {
    resumeText.value = appStore.currentResume
  } else if (appStore.optimizedResume) {
    resumeText.value = appStore.optimizedResume
  }
  // 注意：题库不自动填充，模拟面试使用全新题目以避免与题库刷题重复
  // 如需手动导入题库，可点击下方按钮

  // 恢复进行中的面试
  const ongoingRecord = appStore.interviewHistory.find(r => r.status === 'ongoing')
  if (ongoingRecord) {
    ElMessage.info('检测到进行中的面试，已恢复')
    started.value = true
    currentRecordId.value = ongoingRecord.id
    sessionId.value = ongoingRecord.sessionId || ''
    messages.value = ongoingRecord.messages.map(m => ({
      role: m.role as 'interviewer' | 'user',
      content: m.content,
    }))
    if (ongoingRecord.resumeText) {
      resumeText.value = ongoingRecord.resumeText
    }
    setTimeout(() => scrollToBottom(), 100)
  }
})

const sampleProfile = JSON.stringify(
  {
    position: '后端开发工程师',
    tech_stack: ['Java', 'Spring Boot', 'MySQL', 'Redis', 'Kafka'],
    experience_years: '3-5年',
    core_skills: ['高并发', '分布式', '性能优化']
  },
  null,
  2
)

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

function importQuestionBank() {
  if (appStore.questionBank && appStore.questionBank.length > 0) {
    questionBankText.value = JSON.stringify({ questions: appStore.questionBank }, null, 2)
    ElMessage.success(`已导入 ${appStore.questionBank.length} 道题库题目`)
  } else {
    ElMessage.warning('暂无题库，请先在「题库刷题」页生成')
  }
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

async function scrollToBottom() {
  await nextTick()
  if (chatBoxRef.value) {
    chatBoxRef.value.scrollTop = chatBoxRef.value.scrollHeight
  }
}

async function handleStart() {
  // 如果有选中的角色卡，基于角色卡启动
  if (appStore.activeCard) {
    starting.value = true
    try {
      const card = appStore.activeCard
      // 将角色卡转换为 JobProfile 格式
      const profile = {
        position: card.role_name,
        tech_stack: card.tech_stack,
        core_skills: card.core_skills,
        experience_years: card.experience_years,
        education: card.education,
        interview_directions: card.interview_directions,
      }

      let questionBank: any = undefined
      if (questionBankText.value.trim()) {
        try {
          questionBank = JSON.parse(questionBankText.value)
        } catch {
          ElMessage.warning('题库 JSON 格式不正确，已忽略题库')
        }
      }

      const res: any = await interviewStart(
        profile,
        questionBank,
        resumeText.value.trim() || undefined
      )
      sessionId.value = res?.session_id || ''
      const firstMsg = res?.opening || res?.question || res?.message || `你好，我们开始${card.role_name}的面试吧。请先做个自我介绍。`
      messages.value = [
        {
          role: 'interviewer',
          content: firstMsg
        }
      ]
      started.value = true

      // 创建面试历史记录
      const recordId = 'iv_' + Date.now()
      currentRecordId.value = recordId
      appStore.addInterviewRecord({
        id: recordId,
        jobProfile: profile,
        startedAt: new Date().toISOString(),
        status: 'ongoing',
        messages: messages.value.map(m => ({ role: m.role, content: m.content })),
        sessionId: sessionId.value,
        resumeText: resumeText.value,
      })

      await scrollToBottom()
      ElMessage.success('面试已开始，祝你面试顺利！')
    } catch (e: any) {
      ElMessage.error(e?.message || '启动面试失败，请重试')
    } finally {
      starting.value = false
    }
    return
  }

  // 否则使用岗位画像 JSON
  const profile = parseProfile()
  if (!profile) return

  starting.value = true
  try {
    let questionBank: any = undefined
    if (questionBankText.value.trim()) {
      try {
        questionBank = JSON.parse(questionBankText.value)
      } catch {
        ElMessage.warning('题库 JSON 格式不正确，已忽略题库')
      }
    }
    const res: any = await interviewStart(
      profile,
      questionBank,
      resumeText.value.trim() || undefined
    )
    sessionId.value = res?.session_id || ''
    const firstMsg = res?.opening || res?.question || res?.message || '你好，我们开始面试吧。请先做个自我介绍。'
    messages.value = [
      {
        role: 'interviewer',
        content: firstMsg
      }
    ]
    started.value = true

    // 创建面试历史记录
    const recordId = 'iv_' + Date.now()
    currentRecordId.value = recordId
    appStore.addInterviewRecord({
      id: recordId,
      jobProfile: profile,
      startedAt: new Date().toISOString(),
      status: 'ongoing',
      messages: messages.value.map(m => ({ role: m.role, content: m.content })),
      sessionId: sessionId.value,
      resumeText: resumeText.value,
    })

    await scrollToBottom()
    ElMessage.success('面试已开始，祝你面试顺利！')
  } catch (e: any) {
    ElMessage.error(e?.message || '启动面试失败，请重试')
  } finally {
    starting.value = false
  }
}

async function handleSend() {
  const text = answer.value.trim()
  if (!text || chatting.value) return
  if (!sessionId.value) {
    ElMessage.warning('会话未建立，请重新启动面试')
    return
  }

  messages.value.push({ role: 'user', content: text })
  answer.value = ''
  chatting.value = true
  await scrollToBottom()

  // 更新历史记录
  if (currentRecordId.value) {
    appStore.updateInterviewRecord(currentRecordId.value, {
      messages: messages.value.map(m => ({ role: m.role, content: m.content })),
    })
  }

  try {
    const res: any = await interviewChat(sessionId.value, text)
    messages.value.push({
      role: 'interviewer',
      content: res?.question || res?.reply || res?.message || '（面试官未返回内容）'
    })
    if (res?.finished || res?.is_end) {
      ElMessage.success('面试结束，正在生成评估报告...')
      // 自动生成报告并弹出
      setTimeout(() => handleReport(), 500)
    }
    // 更新历史记录
    if (currentRecordId.value) {
      appStore.updateInterviewRecord(currentRecordId.value, {
        messages: messages.value.map(m => ({ role: m.role, content: m.content })),
      })
    }
  } catch {
    // ignore
  } finally {
    chatting.value = false
    await scrollToBottom()
  }
}

async function handleReport() {
  if (!sessionId.value) {
    ElMessage.warning('会话未建立')
    return
  }

  const taskId = `report-${sessionId.value}-${Date.now()}`
  appStore.addBackgroundTask({
    id: taskId,
    type: 'interview-report',
    title: '面试报告生成中',
    relatedId: currentRecordId.value,
  })

  reporting.value = true

  try {
    const res: any = await interviewReport(sessionId.value)
    report.value = res?.report ?? res
    reportVisible.value = true
    reportTab.value = 'overview'

    if (currentRecordId.value) {
      const questionReviews = report.value?.question_reviews || report.value?.questionReviews || []
      appStore.updateInterviewRecord(currentRecordId.value, {
        status: 'completed',
        finishedAt: new Date().toISOString(),
        report: report.value,
        questionReviews: questionReviews,
        messages: messages.value.map(m => ({ role: m.role, content: m.content })),
      })
    }

    appStore.updateBackgroundTask(taskId, {
      status: 'completed',
      completedAt: new Date().toISOString(),
      result: report.value,
    })

    ElMessage.success('面试报告生成完成')
  } catch (e: any) {
    appStore.updateBackgroundTask(taskId, {
      status: 'failed',
      completedAt: new Date().toISOString(),
      error: e?.message || '生成失败',
    })
  } finally {
    reporting.value = false
    setTimeout(() => {
      appStore.removeBackgroundTask(taskId)
    }, 3000)
  }
}

function handleReset() {
  ElMessageBox.confirm('确定要结束当前面试并重新开始吗？', '提示', {
    type: 'warning',
    confirmButtonText: '重新开始',
    cancelButtonText: '取消'
  })
    .then(() => {
      started.value = false
      sessionId.value = ''
      messages.value = []
      answer.value = ''
      report.value = null
      reportVisible.value = false
    })
    .catch(() => {})
}

/* ============ 报告数据归一化 ============ */
const overallScore = computed(() => {
  return Number(report.value?.overall_score ?? report.value?.total_score ?? report.value?.score ?? 0)
})

const dimensions = computed(() => {
  const raw = report.value?.dimensions || report.value?.scores || report.value?.radar || {}
  const result: { name: string; score: number; comment: string }[] = []
  if (Array.isArray(raw)) {
    for (const d of raw) {
      result.push({
        name: d.name || d.dimension || d.label || '维度',
        score: Number(d.score ?? d.value ?? 0),
        comment: d.comment || d.feedback || d.description || ''
      })
    }
  } else if (raw && typeof raw === 'object') {
    for (const [k, v] of Object.entries(raw)) {
      if (v && typeof v === 'object') {
        result.push({
          name: (v as any).name || k,
          score: Number((v as any).score ?? 0),
          comment: (v as any).comment || ''
        })
      } else {
        result.push({ name: k, score: Number(v), comment: '' })
      }
    }
  }
  // 兜底示例维度
  if (!result.length) {
    result.push(
      { name: '技术深度', score: 0, comment: '' },
      { name: '系统设计', score: 0, comment: '' },
      { name: '表达能力', score: 0, comment: '' },
      { name: '问题解决', score: 0, comment: '' },
      { name: '项目经验', score: 0, comment: '' }
    )
  }
  return result
})

const improvements = computed(() => {
  const raw =
    report.value?.improvements ||
    report.value?.suggestions ||
    report.value?.improvement_suggestions ||
    report.value?.advice
  if (Array.isArray(raw)) return raw.map((s: any) => (typeof s === 'string' ? s : s.suggestion || s.text || JSON.stringify(s)))
  if (typeof raw === 'string') return raw.split(/\n+/).filter(Boolean)
  if (raw && typeof raw === 'object') return Object.values(raw).map((s: any) => String(s))
  return []
})

const questionReviews = computed(() => {
  const raw = report.value?.question_reviews || report.value?.questionReviews || []
  if (Array.isArray(raw)) return raw
  return []
})

function scoreColor(score: number) {
  if (score >= 85) return 'var(--bc-success)'
  if (score >= 70) return 'var(--bc-primary)'
  if (score >= 60) return 'var(--bc-warning)'
  return 'var(--bc-danger)'
}

function levelType(level: string): 'success' | 'warning' | 'danger' | 'info' {
  const v = (level || '').toLowerCase()
  if (v.includes('优') || v.includes('a') || v.includes('pass')) return 'success'
  if (v.includes('良') || v.includes('b') || v.includes('中')) return 'warning'
  if (v.includes('差') || v.includes('c') || v.includes('fail')) return 'danger'
  return 'info'
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

.title-bar-sm {
  width: 3px;
  height: 16px;
  border-radius: 2px;
  background: linear-gradient(180deg, #ffffff 0%, #c4b5fd 100%);
  flex-shrink: 0;
  box-shadow: 0 0 6px var(--bc-violet-soft);
}

.setup-panel {
  margin-bottom: 0;
}

.card-tip-banner {
  display: flex;
  align-items: center;
  gap: var(--bc-space-5);
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(236, 72, 153, 0.04) 100%);
  border: 1px solid var(--bc-border);
  border-radius: var(--bc-radius-md);
  padding: var(--bc-space-5) var(--bc-space-6);
  margin-bottom: var(--bc-space-5);
  position: relative;
}

.card-tip-banner .tip-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #fff;
  flex-shrink: 0;
  box-shadow: var(--bc-shadow-inner);
}

.card-tip-banner .tip-content {
  flex: 1;
  min-width: 0;
}

.card-tip-banner .tip-content h4 {
  margin: 0 0 var(--bc-space-2) 0;
  font-size: var(--bc-font-size-xl);
  color: var(--bc-text);
  font-weight: 600;
}

.card-tip-banner .tip-content p {
  margin: 0 0 var(--bc-space-3) 0;
  font-size: var(--bc-font-size-sm);
  color: var(--bc-text-soft);
  line-height: 1.6;
}

.card-tip-banner .tech-preview {
  display: flex;
  gap: var(--bc-space-2);
  flex-wrap: wrap;
}

.no-card-banner {
  display: flex;
  align-items: center;
  gap: var(--bc-space-3);
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: var(--bc-radius-sm);
  padding: var(--bc-space-3) var(--bc-space-4);
  margin-bottom: var(--bc-space-4);
}

.no-card-banner span {
  flex: 1;
  color: var(--bc-text-soft);
  font-size: var(--bc-font-size-base);
}

.auto-fill-banner {
  display: flex;
  align-items: center;
  gap: var(--bc-space-2);
  background: rgba(99, 102, 241, 0.08);
  border: 1px solid rgba(99, 102, 241, 0.25);
  border-radius: var(--bc-radius-sm);
  padding: var(--bc-space-3) var(--bc-space-4);
  margin-bottom: var(--bc-space-4);
}
.auto-fill-banner .banner-icon {
  color: var(--bc-primary);
  font-size: 16px;
}
.auto-fill-banner .banner-text {
  font-size: var(--bc-font-size-sm);
  color: var(--bc-text-soft);
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
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

.header-actions {
  display: flex;
  gap: var(--bc-space-2);
}

.setup-form {
  margin-bottom: 0;
}

.profile-textarea :deep(.el-textarea__inner),
.resume-textarea :deep(.el-textarea__inner),
.bank-textarea :deep(.el-textarea__inner) {
  background: var(--bc-bg-soft);
  border-color: var(--bc-border);
  color: var(--bc-text);
  border-radius: var(--bc-radius-sm);
  transition: border-color 0.2s var(--bc-ease);
}

.profile-textarea :deep(.el-textarea__inner),
.bank-textarea :deep(.el-textarea__inner) {
  font-family: 'JetBrains Mono', 'Fira Code', Consolas, Monaco, monospace;
  font-size: var(--bc-font-size-sm);
}

.profile-textarea :deep(.el-textarea__inner:focus),
.resume-textarea :deep(.el-textarea__inner:focus),
.bank-textarea :deep(.el-textarea__inner:focus) {
  border-color: rgba(196, 181, 253, 0.5);
  box-shadow: 0 0 0 2px var(--bc-violet-glow), 0 0 20px var(--bc-violet-soft);
}

.profile-textarea :deep(.el-textarea__inner::placeholder),
.resume-textarea :deep(.el-textarea__inner::placeholder),
.bank-textarea :deep(.el-textarea__inner::placeholder) {
  color: var(--bc-text-muted);
}

.actions {
  margin-top: var(--bc-space-4);
}

.start-btn {
  min-width: 160px;
}

/* ============ 聊天界面 ============ */
.chat-wrap {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 200px);
  min-height: 520px;
  padding: 0;
  overflow: hidden;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--bc-space-4) var(--bc-space-6);
  background: var(--bc-bg-elev);
  border-bottom: 1px solid var(--bc-border);
  flex-shrink: 0;
}

.chat-info {
  display: flex;
  align-items: center;
  gap: var(--bc-space-3);
}

.session-id {
  color: var(--bc-text-soft);
  font-size: var(--bc-font-size-sm);
  font-family: 'JetBrains Mono', Consolas, monospace;
}

.chat-actions {
  display: flex;
  gap: var(--bc-space-2);
}

.chat-box {
  flex: 1;
  overflow-y: auto;
  padding: var(--bc-space-6);
  background: var(--bc-bg-soft);
}

.msg-row {
  display: flex;
  gap: var(--bc-space-3);
  margin-bottom: var(--bc-space-5);
  align-items: flex-start;
}

.msg-row.user {
  flex-direction: row-reverse;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--bc-bg-elev);
  border: 1px solid var(--bc-border);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 18px;
  color: var(--bc-text-soft);
  box-shadow: var(--bc-shadow-sm);
}

.msg-row.user .avatar {
  background: rgba(99, 102, 241, 0.15);
  color: var(--bc-primary);
  border-color: rgba(99, 102, 241, 0.3);
}

.bubble {
  max-width: 70%;
  padding: var(--bc-space-3) var(--bc-space-4);
  border-radius: var(--bc-radius-md);
  background: var(--bc-bg-elev);
  border: 1px solid var(--bc-border);
  box-shadow: var(--bc-shadow-sm);
}

.msg-row.interviewer .bubble {
  border-top-left-radius: 4px;
}

.msg-row.user .bubble {
  border-top-right-radius: 4px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(99, 102, 241, 0.08) 100%);
  border-color: rgba(99, 102, 241, 0.25);
}

.bubble-role {
  font-size: var(--bc-font-size-xs);
  color: var(--bc-text-muted);
  margin-bottom: 4px;
  font-weight: 500;
}

.bubble-text {
  line-height: 1.7;
  color: var(--bc-text);
  white-space: pre-wrap;
  word-break: break-word;
  font-size: var(--bc-font-size-base);
}

.typing {
  color: var(--bc-text-soft);
}

.dots {
  display: inline-flex;
  gap: 3px;
  margin-left: 4px;
}

.dots i {
  width: 5px;
  height: 5px;
  background: var(--bc-text-soft);
  border-radius: 50%;
  animation: blink 1.2s infinite both;
}

.dots i:nth-child(2) {
  animation-delay: 0.2s;
}
.dots i:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes blink {
  0%,
  80%,
  100% {
    opacity: 0.2;
  }
  40% {
    opacity: 1;
  }
}

.chat-input {
  display: flex;
  gap: var(--bc-space-3);
  padding: var(--bc-space-4) var(--bc-space-6);
  background: var(--bc-bg-elev);
  border-top: 1px solid var(--bc-border);
  align-items: flex-end;
  flex-shrink: 0;
}

.input-textarea {
  flex: 1;
}

.input-textarea :deep(.el-textarea__inner) {
  background: var(--bc-bg-soft);
  border-color: var(--bc-border);
  color: var(--bc-text);
  border-radius: var(--bc-radius-sm);
  transition: border-color 0.2s var(--bc-ease);
}

.input-textarea :deep(.el-textarea__inner:focus) {
  border-color: var(--bc-primary);
  box-shadow: 0 0 0 2px var(--bc-primary-glow);
}

.input-textarea :deep(.el-textarea__inner::placeholder) {
  color: var(--bc-text-muted);
}

.send-btn {
  height: auto;
  min-height: 40px;
}

/* ============ 报告弹窗 ============ */
.report-dialog :deep(.el-dialog) {
  background: var(--bc-bg-elev);
  border: 1px solid var(--bc-border);
  border-radius: var(--bc-radius-lg);
  box-shadow: var(--bc-shadow-xl);
}

.report-dialog :deep(.el-dialog__title) {
  color: var(--bc-text);
  font-weight: 600;
  font-size: var(--bc-font-size-xl);
}

.report-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid var(--bc-border);
  padding-bottom: var(--bc-space-4);
}

.report-dialog :deep(.el-dialog__footer) {
  border-top: 1px solid var(--bc-border);
  padding-top: var(--bc-space-4);
}

.report-body {
  max-height: 60vh;
  overflow-y: auto;
  padding-right: 4px;
}

.report-overview {
  display: flex;
  align-items: center;
  gap: var(--bc-space-8);
}

.score-ring {
  flex-shrink: 0;
}

.ring-inner {
  text-align: center;
}

.ring-num {
  font-size: 32px;
  font-weight: 700;
  line-height: 1.2;
}

.ring-label {
  font-size: var(--bc-font-size-xs);
  color: var(--bc-text-soft);
  margin-top: 2px;
}

.overview-text {
  flex: 1;
  min-width: 0;
}

.overview-title {
  font-size: var(--bc-font-size-lg);
  font-weight: 600;
  color: var(--bc-text);
  margin-bottom: var(--bc-space-2);
  line-height: 1.4;
}

.overview-sub {
  color: var(--bc-text-soft);
  margin-bottom: var(--bc-space-3);
  line-height: 1.7;
  font-size: var(--bc-font-size-sm);
}

.dim-section {
  margin-top: 0;
}

.dim-title {
  font-size: var(--bc-font-size-base);
  font-weight: 600;
  color: var(--bc-text);
  margin-bottom: var(--bc-space-4);
  display: flex;
  align-items: center;
  gap: var(--bc-space-2);
}

.dim-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--bc-space-4) var(--bc-space-6);
}

.dim-item {
  padding: var(--bc-space-4);
  margin-bottom: 0;
  cursor: default;
}

.dim-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--bc-space-2);
}

.dim-name {
  color: var(--bc-text);
  font-size: var(--bc-font-size-sm);
  font-weight: 500;
}

.dim-score {
  font-weight: 700;
  font-size: var(--bc-font-size-base);
}

.dim-comment {
  font-size: var(--bc-font-size-xs);
  color: var(--bc-text-soft);
  margin-top: var(--bc-space-2);
  line-height: 1.5;
}

.improve-list {
  display: flex;
  flex-direction: column;
  gap: var(--bc-space-3);
}

.improve-item {
  display: flex;
  gap: var(--bc-space-2);
  align-items: flex-start;
  padding: var(--bc-space-3) var(--bc-space-4);
  margin-bottom: 0;
  color: var(--bc-text);
  line-height: 1.6;
  font-size: var(--bc-font-size-sm);
  cursor: default;
}

.improve-icon {
  color: var(--bc-warning);
  flex-shrink: 0;
  margin-top: 2px;
  font-size: 16px;
}

/* ============ 报告标签页 ============ */
.report-tabs {
  margin-bottom: 0;
}
.report-tabs :deep(.el-tabs__item) {
  font-size: var(--bc-font-size-base);
  color: var(--bc-text-soft);
}
.report-tabs :deep(.el-tabs__item.is-active) {
  color: var(--bc-primary);
}
.report-tabs :deep(.el-tabs__active-bar) {
  background: linear-gradient(90deg, var(--bc-primary), var(--bc-accent));
}

/* ============ 逐题回顾 ============ */
.reviews-body {
  max-height: 60vh;
  overflow-y: auto;
  padding-right: 4px;
  display: flex;
  flex-direction: column;
  gap: var(--bc-space-4);
}

.review-card {
  padding: var(--bc-space-5);
  margin-bottom: 0;
}

.review-header {
  display: flex;
  align-items: center;
  gap: var(--bc-space-2);
  margin-bottom: var(--bc-space-3);
}

.review-q-num {
  margin-left: auto;
  font-size: var(--bc-font-size-sm);
  color: var(--bc-text-muted);
  font-weight: 500;
}

.review-question,
.review-answer {
  margin-bottom: var(--bc-space-3);
  line-height: 1.7;
  font-size: var(--bc-font-size-sm);
}

.q-label {
  color: var(--bc-text-soft);
  font-weight: 600;
  flex-shrink: 0;
}

.q-text {
  color: var(--bc-text);
}

.answer-text {
  color: var(--bc-text-soft);
}

.review-standard,
.review-correction {
  margin-top: var(--bc-space-3);
  padding: var(--bc-space-3) var(--bc-space-4);
  border-radius: var(--bc-radius-sm);
  border-left: 3px solid;
}

.review-standard {
  background: rgba(16, 185, 129, 0.08);
  border-color: var(--bc-success);
}

.review-correction {
  background: rgba(239, 68, 68, 0.08);
  border-color: var(--bc-danger);
}

.review-block-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: var(--bc-font-size-sm);
  font-weight: 600;
  margin-bottom: var(--bc-space-2);
}

.review-standard .review-block-title {
  color: var(--bc-success);
}

.review-correction .review-block-title {
  color: var(--bc-danger);
}

.review-block-content {
  line-height: 1.8;
  font-size: var(--bc-font-size-sm);
  white-space: pre-wrap;
  word-break: break-word;
}

.standard-text {
  color: #6ee7b7;
}

.correction-text {
  color: #fca5a5;
}

@media (max-width: 768px) {
  .card-tip-banner {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--bc-space-3);
  }

  .chat-wrap {
    height: calc(100vh - 180px);
    min-height: 480px;
  }

  .bubble {
    max-width: 85%;
  }

  .chat-header {
    flex-direction: column;
    gap: var(--bc-space-2);
    align-items: flex-start;
  }

  .chat-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .report-overview {
    flex-direction: column;
    gap: var(--bc-space-5);
    text-align: center;
  }

  .dim-grid {
    grid-template-columns: 1fr;
  }

  .report-dialog :deep(.el-dialog) {
    width: 95% !important;
    margin: 0 auto;
  }

  .header-actions {
    flex-wrap: wrap;
  }
}
</style>
