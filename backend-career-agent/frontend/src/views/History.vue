<template>
  <div class="page-container">
    <div class="page-header">
      <h2 class="page-title">历史记录</h2>
      <p class="page-desc">查看你保存的面试记录</p>
    </div>

    <!-- 面试记录列表 -->
    <div v-if="appStore.interviewHistory.length === 0" class="empty-wrap">
      <el-empty description="暂无面试记录，去「模拟面试」开始你的第一场面试吧" />
    </div>

    <div v-else class="record-list">
      <div
        v-for="iv in appStore.interviewHistory"
        :key="iv.id"
        class="record-card"
        @click="viewInterview(iv)"
      >
        <div class="record-header">
          <el-tag :type="iv.status === 'completed' ? 'success' : 'warning'" effect="dark" size="small">
            {{ iv.status === 'completed' ? '已完成' : '进行中' }}
          </el-tag>
          <span class="record-position">
            {{ iv.jobProfile?.position || '后端工程师' }}
          </span>
          <span class="record-time">{{ formatTime(iv.startedAt) }}</span>
        </div>
        <div class="record-body">
          <div class="record-meta">
            <span v-if="iv.status === 'completed'" class="score-tag">
              综合得分：{{ getScore(iv) }} 分
            </span>
            <span class="msg-count">共 {{ countQuestions(iv) }} 道题</span>
          </div>
        </div>
        <div class="record-actions">
          <el-button size="small" type="primary" text @click.stop="viewInterview(iv)">
            查看详情
          </el-button>
          <el-button size="small" type="danger" text @click.stop="deleteRecord(iv.id)">
            删除
          </el-button>
        </div>
      </div>
    </div>

    <!-- 面试详情弹窗 -->
    <el-dialog
      v-model="detailVisible"
      title="面试详情"
      width="820px"
      align-center
      destroy-on-close
    >
      <div v-if="currentDetail" class="detail-body">
        <div class="detail-header">
          <el-tag :type="currentDetail.status === 'completed' ? 'success' : 'warning'" effect="dark">
            {{ currentDetail.status === 'completed' ? '已完成' : '进行中' }}
          </el-tag>
          <span class="detail-position">
            {{ currentDetail.jobProfile?.position || '后端工程师' }}
          </span>
          <span class="detail-time">{{ formatTime(currentDetail.startedAt) }}</span>
        </div>

        <el-tabs v-model="detailTab" class="detail-tabs">
          <!-- 对话记录 -->
          <el-tab-pane label="对话记录" name="messages">
            <div class="chat-export">
              <div
                v-for="(msg, i) in currentDetail.messages"
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
            </div>
          </el-tab-pane>

          <!-- 评分总览 -->
          <el-tab-pane label="评分总览" name="score" v-if="currentDetail.report">
            <div class="score-overview">
              <div class="score-ring">
                <el-progress
                  type="dashboard"
                  :percentage="getOverallScore(currentDetail)"
                  :width="140"
                  :color="scoreColor(getOverallScore(currentDetail))"
                >
                  <template #default>
                    <div class="ring-inner">
                      <div class="ring-num">{{ getOverallScore(currentDetail) }}</div>
                      <div class="ring-label">综合评分</div>
                    </div>
                  </template>
                </el-progress>
              </div>
              <div class="overview-text">
                <div class="overview-title">
                  {{ currentDetail.report.summary || currentDetail.report.overall_comment || '面试评估完成' }}
                </div>
                <div class="overview-sub">
                  {{ currentDetail.report.conclusion || currentDetail.report.recommendation || '' }}
                </div>
              </div>
            </div>

            <el-divider />

            <div class="dim-grid">
              <div v-for="d in getDimensions(currentDetail)" :key="d.name" class="dim-item">
                <div class="dim-head">
                  <span class="dim-name">{{ d.name }}</span>
                  <span class="dim-score" :style="{ color: scoreColor(d.score) }">{{ d.score }}</span>
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
          </el-tab-pane>

          <!-- 逐题回顾 -->
          <el-tab-pane
            :label="`逐题回顾 (${getQuestionReviews(currentDetail).length})`"
            name="reviews"
            v-if="getQuestionReviews(currentDetail).length"
          >
            <div class="reviews-body">
              <div
                v-for="(rev, idx) in getQuestionReviews(currentDetail)"
                :key="idx"
                class="review-card"
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
          </el-tab-pane>
        </el-tabs>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Avatar, User, CircleCheck, Warning } from '@element-plus/icons-vue'
import { useAppStore, type InterviewRecord } from '@/stores/app'

const appStore = useAppStore()

const detailVisible = ref(false)
const currentDetail = ref<InterviewRecord | null>(null)
const detailTab = ref('messages')

function formatTime(time: string) {
  if (!time) return ''
  try {
    const d = new Date(time)
    return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours()}:${String(d.getMinutes()).padStart(2, '0')}`
  } catch {
    return time
  }
}

function getScore(iv: InterviewRecord): number {
  const report = iv.report
  if (!report) return 0
  return Math.round(report.overall_score || report.total_score || report.score || 0)
}

function countQuestions(iv: InterviewRecord): number {
  return iv.messages.filter(m => m.role === 'interviewer').length
}

function viewInterview(iv: InterviewRecord) {
  currentDetail.value = iv
  detailTab.value = iv.report ? 'score' : 'messages'
  detailVisible.value = true
}

function deleteRecord(id: string) {
  ElMessageBox.confirm('确定要删除这条面试记录吗？', '提示', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消'
  })
    .then(() => {
      appStore.deleteInterviewRecord(id)
      ElMessage.success('已删除')
    })
    .catch(() => {})
}

function getOverallScore(iv: InterviewRecord): number {
  const report = iv.report
  if (!report) return 0
  const score = report.overall_score || report.total_score || report.score || 0
  return Math.round(score)
}

function getDimensions(iv: InterviewRecord): { name: string; score: number; comment: string }[] {
  const report = iv.report
  if (!report) return []
  const raw = report.dimensions || report.scores || report.radar || {}
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
  return result
}

function getQuestionReviews(iv: InterviewRecord): any[] {
  if (iv.questionReviews && Array.isArray(iv.questionReviews)) return iv.questionReviews
  const report = iv.report
  if (!report) return []
  const raw = report.question_reviews || report.questionReviews || []
  if (Array.isArray(raw)) return raw
  return []
}

function scoreColor(score: number) {
  if (score >= 85) return 'var(--bc-success)'
  if (score >= 70) return 'var(--bc-primary)'
  if (score >= 60) return 'var(--bc-warning)'
  return 'var(--bc-danger)'
}
</script>

<style scoped>
.page-container { padding: 24px; max-width: 900px; margin: 0 auto; }

.page-header { margin-bottom: 24px; }
.page-title { font-size: 22px; font-weight: 700; color: var(--bc-text); margin: 0 0 8px 0; }
.page-desc { font-size: 14px; color: var(--bc-text-soft); margin: 0; }

.empty-wrap { padding: 60px 0; }

.record-list { display: flex; flex-direction: column; gap: 12px; }

.record-card {
  background: var(--bc-bg-elev);
  border: 1px solid var(--bc-border);
  border-radius: 10px;
  padding: 16px 20px;
  cursor: pointer;
  transition: border-color 0.2s;
}
.record-card:hover { border-color: var(--bc-primary); }

.record-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.record-position { font-size: 14px; color: var(--bc-text); font-weight: 500; }
.record-time { font-size: 12px; color: var(--bc-text-soft); margin-left: auto; }

.record-body { font-size: 13px; color: var(--bc-text-soft); line-height: 1.6; }

.record-meta {
  display: flex;
  gap: 16px;
  align-items: center;
}

.score-tag {
  color: var(--bc-primary);
  font-weight: 600;
}

.msg-count {
  color: var(--bc-text-soft);
}

.record-actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* 详情弹窗 */
.detail-body { max-height: 65vh; overflow-y: auto; padding-right: 4px; }

.detail-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--bc-border);
}

.detail-position { font-size: 15px; color: var(--bc-text); font-weight: 600; }
.detail-time { font-size: 12px; color: var(--bc-text-soft); margin-left: auto; }

.detail-tabs { margin-bottom: 0; }
.detail-tabs :deep(.el-tabs__item) { font-size: 14px; }

/* 对话记录导出样式 */
.chat-export {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 10px 0;
}

.msg-row {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.msg-row.user { flex-direction: row-reverse; }

.avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: var(--bc-bg-elev);
  border: 1px solid var(--bc-border);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 18px;
  color: var(--bc-text-soft);
}

.msg-row.user .avatar {
  background: rgba(79, 140, 255, 0.15);
  color: var(--bc-primary);
}

.bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 12px;
  background: var(--bc-bg-elev);
  border: 1px solid var(--bc-border);
}

.msg-row.interviewer .bubble { border-top-left-radius: 4px; }
.msg-row.user .bubble {
  border-top-right-radius: 4px;
  background: rgba(79, 140, 255, 0.12);
  border-color: rgba(79, 140, 255, 0.3);
}

.bubble-role { font-size: 12px; color: var(--bc-text-soft); margin-bottom: 4px; }
.bubble-text { line-height: 1.7; color: var(--bc-text); white-space: pre-wrap; word-break: break-word; }

/* 评分总览 */
.score-overview {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 12px;
}

.ring-inner { text-align: center; }
.ring-num { font-size: 30px; font-weight: 700; color: var(--bc-text); }
.ring-label { font-size: 12px; color: var(--bc-text-soft); }

.overview-text { flex: 1; }
.overview-title { font-size: 16px; font-weight: 600; color: var(--bc-text); margin-bottom: 6px; }
.overview-sub { color: var(--bc-text-soft); margin-bottom: 10px; line-height: 1.7; }

.dim-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px 24px;
}

.dim-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
}

.dim-name { color: var(--bc-text); font-size: 13px; }
.dim-score { font-weight: 700; font-size: 14px; }
.dim-comment { font-size: 12px; color: var(--bc-text-soft); margin-top: 4px; line-height: 1.5; }

/* 逐题回顾 — 与 Interview.vue 保持一致 */
.reviews-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 10px 0;
}

.review-card {
  background: var(--bc-bg-soft);
  border: 1px solid var(--bc-border);
  border-radius: 10px;
  padding: 16px;
}

.review-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.review-q-num {
  margin-left: auto;
  font-size: 12px;
  color: var(--bc-text-soft);
}

.review-question,
.review-answer {
  margin-bottom: 10px;
  line-height: 1.7;
  font-size: 14px;
}

.q-label {
  color: var(--bc-text-soft);
  font-weight: 600;
}

.q-text { color: var(--bc-text); }
.answer-text { color: #a0a8b8; }

.review-standard,
.review-correction {
  margin-top: 12px;
  padding: 12px 14px;
  border-radius: 8px;
  border-left: 3px solid;
}

.review-standard {
  background: rgba(46, 204, 113, 0.08);
  border-color: #2ecc71;
}

.review-correction {
  background: rgba(231, 76, 60, 0.08);
  border-color: #e74c3c;
}

.review-block-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 8px;
}

.review-standard .review-block-title { color: #2ecc71; }
.review-correction .review-block-title { color: #e74c3c; }

.review-block-content {
  line-height: 1.8;
  font-size: 13px;
  white-space: pre-wrap;
  word-break: break-word;
}

.standard-text { color: #7cd99a; }
.correction-text { color: #e07c7c; }
</style>
