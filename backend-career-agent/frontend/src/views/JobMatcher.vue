<template>
  <div class="page-container">
    <h1 class="page-title">
      <span class="title-bar"></span>
      <span class="fx-gradient-text">岗位匹配</span>
    </h1>
    <p class="page-subtitle">粘贴岗位 JD，AI 将解析生成结构化岗位需求画像</p>

    <el-row :gutter="20" class="content-row fx-stagger">
      <el-col :span="12" :xs="24" :md="12">
        <div class="section-card input-panel">
          <div class="panel-header">
            <span class="panel-title">
              <span class="title-bar-sm"></span>
              岗位 JD
            </span>
            <div class="header-right">
              <el-button text type="primary" :icon="Files" @click="openPresetDialog">
              导入预设岗位
              </el-button>
              <el-upload
                :show-file-list="false"
                :before-upload="handleUploadJD"
                accept=".pdf,.png,.jpg,.jpeg,.bmp,.webp"
              >
                <el-button text :icon="Picture" :loading="ocrLoading">
                  截图识别 JD
                </el-button>
              </el-upload>
              <el-button text @click="loadSample">载入示例</el-button>
            </div>
          </div>
          <el-input
            v-model="jdText"
            type="textarea"
            :rows="18"
            placeholder="请粘贴完整的岗位描述（JD），包括职责、要求、技术栈等..."
            resize="none"
            class="jd-textarea"
          />
          <div class="actions">
            <el-button
              type="primary"
              :loading="loading"
              :icon="Promotion"
              class="fx-shine"
              @click="handleMatch"
            >
              解析岗位
            </el-button>
            <el-button :icon="Delete" @click="jdText = ''">清空</el-button>
            <span class="count">{{ jdText.length }} 字</span>
          </div>
        </div>
      </el-col>

      <el-col :span="12" :xs="24" :md="12">
        <div class="section-card result-panel">
          <div class="panel-header">
            <span class="panel-title">
              <span class="title-bar-sm"></span>
              岗位需求画像
            </span>
            <div v-if="profile" class="header-actions">
              <el-button text type="primary" :icon="Share" @click="router.push('/resume-optimizer')">去优化简历</el-button>
              <el-button text type="warning" :icon="Reading" @click="router.push('/question-bank')">去生成题库</el-button>
              <el-button text type="danger" :icon="ChatDotRound" @click="router.push('/interview')">去模拟面试</el-button>
            </div>
          </div>

          <el-empty v-if="!profile && !loading" description="暂无解析结果，请粘贴 JD 并点击解析" />

          <el-skeleton v-else-if="loading" :rows="8" animated />

          <div v-else class="profile-wrap">
            <el-descriptions :column="1" border class="profile-desc">
              <el-descriptions-item label="岗位名称">
                <span class="bold">{{ profile.position || '-' }}</span>
              </el-descriptions-item>
              <el-descriptions-item label="经验要求">
                {{ profile.experience_years ?? '-' }}
              </el-descriptions-item>
              <el-descriptions-item label="技术栈">
                <div class="tag-row">
                  <el-tag
                    v-for="t in asArray(profile.tech_stack)"
                    :key="t"
                    effect="dark"
                    type="primary"
                    class="tag"
                  >
                    {{ t }}
                  </el-tag>
                  <span v-if="!asArray(profile.tech_stack).length" class="muted">-</span>
                </div>
              </el-descriptions-item>
              <el-descriptions-item label="核心技能">
                <div class="tag-row">
                  <el-tag
                    v-for="t in asArray(profile.core_skills)"
                    :key="t"
                    effect="plain"
                    type="success"
                    class="tag"
                  >
                    {{ t }}
                  </el-tag>
                  <span v-if="!asArray(profile.core_skills).length" class="muted">-</span>
                </div>
              </el-descriptions-item>
              <el-descriptions-item label="软技能">
                <div class="tag-row">
                  <el-tag
                    v-for="t in asArray(profile.soft_skills)"
                    :key="t"
                    effect="plain"
                    type="warning"
                    class="tag"
                  >
                    {{ t }}
                  </el-tag>
                  <span v-if="!asArray(profile.soft_skills).length" class="muted">-</span>
                </div>
              </el-descriptions-item>
              <el-descriptions-item label="加分项">
                <div class="tag-row">
                  <el-tag
                    v-for="t in asArray(profile.bonus_items)"
                    :key="t"
                    effect="plain"
                    type="danger"
                    class="tag"
                  >
                    {{ t }}
                  </el-tag>
                  <span v-if="!asArray(profile.bonus_items).length" class="muted">-</span>
                </div>
              </el-descriptions-item>
            </el-descriptions>

            <div class="json-box">
              <div class="json-head">
                <span>原始 JSON</span>
                <el-button text :icon="CopyDocument" @click="copyJson">复制</el-button>
              </div>
              <pre class="json-pre">{{ JSON.stringify(profile, null, 2) }}</pre>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-dialog
      v-model="presetDialogVisible"
      title="导入预设岗位画像"
      width="720px"
      align-center
      destroy-on-close
      class="preset-dialog"
    >
      <p class="preset-tip">选择一个预设岗位，将直接生成结构化岗位画像，无需解析 JD</p>
      <div class="preset-list fx-stagger">
        <div
          v-for="card in appStore.presetCards"
          :key="card.id"
          class="preset-item fx-hover-lift"
          :class="{ active: selectedPresetId === card.id }"
          @click="selectedPresetId = card.id"
        >
          <div class="preset-icon" :style="{ background: getRoleColor(card.icon) }">
            {{ getRoleIcon(card.icon) }}
          </div>
          <div class="preset-info">
            <div class="preset-name">{{ card.role_name }}</div>
            <div class="preset-tech">{{ card.tech_stack.slice(0, 5).join('、') }}</div>
          </div>
          <el-icon v-if="selectedPresetId === card.id" class="check-icon" color="#6366f1">
            <CircleCheckFilled />
          </el-icon>
        </div>
      </div>
      <template #footer>
        <el-button @click="presetDialogVisible = false">取消</el-button>
        <el-button type="primary" :disabled="!selectedPresetId" class="fx-shine" @click="confirmImportPreset">
          导入画像
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Promotion,
  Delete,
  Share,
  CopyDocument,
  Reading,
  ChatDotRound,
  Picture,
  Files,
  CircleCheckFilled
} from '@element-plus/icons-vue'
import { matchJob, parseResumeFile } from '@/api/agents'
import { useAppStore, type JobProfile } from '@/stores/app'
import { getRoleIcon, getRoleColor } from '@/types/role_card'

const router = useRouter()
const appStore = useAppStore()

const jdText = ref(appStore.jdText || '')
const loading = ref(false)
const ocrLoading = ref(false)
const profile = ref<JobProfile | null>(appStore.currentJobProfile)

// 预设岗位对话框
const presetDialogVisible = ref(false)
const selectedPresetId = ref<string>('')

function openPresetDialog() {
  selectedPresetId.value = appStore.activeCard?.id || ''
  presetDialogVisible.value = true
}

function confirmImportPreset() {
  const card = appStore.presetCards.find(c => c.id === selectedPresetId.value)
  if (!card) {
    ElMessage.warning('请选择一个预设岗位')
    return
  }
  // 将角色卡转换为 JobProfile
  const jobProfile: JobProfile = {
    position: card.role_name,
    tech_stack: card.tech_stack,
    core_skills: card.core_skills,
    soft_skills: card.soft_skills,
    experience_years: card.experience_years,
    education: card.education,
    bonus_items: card.interview_directions,
    key_responsibilities: card.jd_summary ? [card.jd_summary] : [],
  }
  profile.value = jobProfile
  appStore.setJobProfile(jobProfile)
  // 同步设置为活跃角色卡，便于其他模块复用
  appStore.setActiveCard(card)
  jdText.value = card.jd_summary || `[预设岗位] ${card.role_name}`
  appStore.setJdText(jdText.value)
  presetDialogVisible.value = false
  ElMessage.success(`已导入「${card.role_name}」岗位画像`)
}

const sampleJD = `高级后端开发工程师（Java/Go）
岗位职责：
1. 负责核心业务系统的设计与开发，保障高并发场景下的稳定性；
2. 参与微服务架构演进，优化系统性能与可用性；
3. 主导技术方案评审，指导初中级工程师。
任职要求：
1. 本科及以上学历，计算机相关专业，3-5年后端开发经验；
2. 精通 Java 或 Go，熟悉 Spring Boot / Gin 框架；
3. 熟练使用 MySQL、Redis、Kafka，具备性能调优经验；
4. 熟悉 Docker、Kubernetes，有云原生实践经验者优先；
5. 具备良好的沟通能力与团队协作精神，有分布式系统设计经验加分。`

function loadSample() {
  jdText.value = sampleJD
}

async function handleUploadJD(file: File): Promise<boolean> {
  const maxSize = 20 * 1024 * 1024 // 20MB
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过 20MB')
    return false
  }
  ocrLoading.value = true
  try {
    const res: any = await parseResumeFile(file)
    const text = res?.text || ''
    if (!text) {
      ElMessage.error('未能识别出 JD 内容，请检查文件是否清晰')
      return false
    }
    jdText.value = text
    const methodMap: Record<string, string> = {
      pdf_text: 'PDF 文字提取',
      ocr: '图片识别 (OCR)'
    }
    const method = methodMap[res.method] || res.method
    ElMessage.success(`JD 解析成功！方法：${method}，共 ${res.pages || 1} 页`)
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || e?.message || '解析失败，请重试')
  } finally {
    ocrLoading.value = false
  }
  return false // 阻止自动上传
}

function asArray(val: any): string[] {
  if (!val) return []
  if (Array.isArray(val)) return val
  if (typeof val === 'string') return val.split(/[,，、\n]/).map((s) => s.trim()).filter(Boolean)
  return [String(val)]
}

async function handleMatch() {
  if (!jdText.value.trim()) {
    ElMessage.warning('请先粘贴岗位 JD')
    return
  }
  loading.value = true
  profile.value = null
  try {
    const res: any = await matchJob(jdText.value)
    profile.value = (res?.job_profile ?? res) as JobProfile
    appStore.setJobProfile(profile.value)
    appStore.setJdText(jdText.value)
    ElMessage.success('岗位解析完成，可快捷跳转到项目分析/题库/面试')
  } catch (e) {
    // 错误已在拦截器中提示
  } finally {
    loading.value = false
  }
}

function copyJson() {
  if (!profile.value) return
  navigator.clipboard.writeText(JSON.stringify(profile.value, null, 2))
  ElMessage.success('已复制到剪贴板')
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

.content-row {
  margin-bottom: 0;
}

.input-panel,
.result-panel {
  height: 100%;
  min-height: 560px;
  display: flex;
  flex-direction: column;
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
  background: linear-gradient(180deg, #ffffff 0%, #c4b5fd 100%);
  flex-shrink: 0;
  box-shadow: 0 0 6px var(--bc-violet-soft);
}

.header-right {
  display: flex;
  align-items: center;
  gap: var(--bc-space-2);
}

.header-actions {
  display: flex;
  gap: var(--bc-space-1);
}

.jd-textarea :deep(.el-textarea__inner) {
  background: var(--bc-bg-soft);
  border-color: var(--bc-border);
  color: var(--bc-text);
  border-radius: var(--bc-radius-sm);
  transition: border-color 0.2s var(--bc-ease);
}

.jd-textarea :deep(.el-textarea__inner:focus) {
  border-color: var(--bc-primary);
  box-shadow: 0 0 0 2px var(--bc-primary-glow);
}

.jd-textarea :deep(.el-textarea__inner::placeholder) {
  color: var(--bc-text-muted);
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

.profile-wrap {
  flex: 1;
}

.profile-desc :deep(.el-descriptions__label) {
  width: 110px;
  color: var(--bc-text-soft);
  background: var(--bc-bg-soft);
  border-color: var(--bc-border);
}

.profile-desc :deep(.el-descriptions__content) {
  color: var(--bc-text);
  background: transparent;
  border-color: var(--bc-border);
}

.profile-desc :deep(.el-descriptions__body) {
  background: transparent;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--bc-space-2);
}

.tag {
  margin: 0;
  cursor: default;
}

.bold {
  font-weight: 600;
  color: var(--bc-primary);
}

.muted {
  color: var(--bc-text-soft);
}

.json-box {
  margin-top: var(--bc-space-5);
  background: var(--bc-bg-soft);
  border: 1px solid var(--bc-border);
  border-radius: var(--bc-radius-sm);
  overflow: hidden;
}

.json-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--bc-space-2) var(--bc-space-3);
  border-bottom: 1px solid var(--bc-border);
  color: var(--bc-text-soft);
  font-size: var(--bc-font-size-sm);
}

.json-pre {
  margin: 0;
  padding: var(--bc-space-3);
  max-height: 220px;
  overflow: auto;
  font-size: var(--bc-font-size-sm);
  color: #9dd6ff;
  font-family: 'JetBrains Mono', Consolas, monospace;
  line-height: 1.6;
}

.result-panel :deep(.el-descriptions__label) {
  width: 110px;
  color: var(--bc-text-soft);
}

.result-panel :deep(.el-descriptions__content) {
  color: var(--bc-text);
}

.preset-dialog :deep(.el-dialog) {
  background: var(--bc-bg-elev);
  border: 1px solid var(--bc-border);
  border-radius: var(--bc-radius-lg);
  box-shadow: var(--bc-shadow-xl);
}

.preset-dialog :deep(.el-dialog__title) {
  color: var(--bc-text);
  font-weight: 600;
}

.preset-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid var(--bc-border);
  padding-bottom: var(--bc-space-4);
}

.preset-dialog :deep(.el-dialog__footer) {
  border-top: 1px solid var(--bc-border);
  padding-top: var(--bc-space-4);
}

.preset-tip {
  margin: 0 0 var(--bc-space-4) 0;
  color: var(--bc-text-soft);
  font-size: var(--bc-font-size-sm);
}

.preset-list {
  display: flex;
  flex-direction: column;
  gap: var(--bc-space-3);
  max-height: 480px;
  overflow-y: auto;
  padding-right: 4px;
}

.preset-item {
  display: flex;
  align-items: flex-start;
  gap: var(--bc-space-4);
  padding: var(--bc-space-4);
  background: var(--bc-bg-soft);
  border: 1px solid var(--bc-border);
  border-radius: var(--bc-radius-sm);
  cursor: pointer;
  transition: all 0.2s var(--bc-ease);
  position: relative;
  overflow: visible;
  min-height: 72px;
}

.preset-item:hover {
  border-color: var(--bc-border-glow);
  box-shadow: var(--bc-shadow-md);
}

.preset-item.active {
  border-color: var(--bc-primary);
  background: rgba(99, 102, 241, 0.08);
  box-shadow: 0 0 0 1px var(--bc-primary-glow);
}

.preset-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  color: #fff;
  flex-shrink: 0;
}

.preset-info {
  flex: 1;
  min-width: 0;
}

.preset-name {
  font-size: var(--bc-font-size-base);
  font-weight: 600;
  color: var(--bc-text);
  margin-bottom: 4px;
  line-height: 1.5;
}

.preset-tech {
  font-size: var(--bc-font-size-sm);
  color: var(--bc-text-soft);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.check-icon {
  font-size: 22px;
  flex-shrink: 0;
  color: var(--bc-primary) !important;
}

@media (max-width: 768px) {
  .content-row {
    flex-direction: column;
  }

  .input-panel,
  .result-panel {
    min-height: auto;
  }

  .header-actions {
    flex-wrap: wrap;
  }

  .preset-dialog :deep(.el-dialog) {
    width: 95% !important;
    margin: 0 auto;
  }
}
</style>
