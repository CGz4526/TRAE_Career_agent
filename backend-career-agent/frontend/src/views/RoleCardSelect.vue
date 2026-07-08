<template>
  <div class="role-card-select">
    <div class="page-header fx-fade-up">
      <div class="header-top">
        <el-button text class="back-btn" :icon="ArrowLeft" @click="goBack">返回</el-button>
        <h2 class="header-title">
          <span class="title-bar"></span>
          <span class="fx-gradient-text">选择面试方向</span>
        </h2>
        <div style="width: 60px"></div>
      </div>
      <p class="subtitle">选择一个预设岗位，我们将为你生成针对性的面试题库和模拟面试</p>
    </div>

    <div class="role-cards-grid fx-stagger">
      <div
        v-for="card in presetCards"
        :key="card.id"
        class="role-card section-card fx-hover-lift fx-spotlight"
        :class="{ active: selectedId === card.id }"
        v-spotlight
        @click="selectCard(card)"
      >
        <div class="card-icon" :style="{ background: getRoleColor(card.icon) }">
          {{ getRoleIcon(card.icon) }}
        </div>
        <div class="card-content">
          <h3>{{ card.role_name }}</h3>
          <p class="card-desc">{{ card.description }}</p>
          <div class="card-tags">
            <el-tag size="small" effect="plain">{{ card.experience_years }}</el-tag>
            <el-tag size="small" type="info" effect="plain">{{ card.education }}</el-tag>
          </div>
          <div class="card-tech">
            <span class="tech-label">技术栈：</span>
            <span class="tech-list">{{ card.tech_stack.slice(0, 4).join('、') }}...</span>
          </div>
        </div>
        <div class="card-action">
          <el-button
            type="primary"
            size="small"
            class="fx-shine"
            :disabled="selectedId === card.id"
          >
            {{ selectedId === card.id ? '已选择' : '选择' }}
          </el-button>
        </div>
      </div>
    </div>

    <transition name="detail-in" mode="out-in">
      <div v-if="selectedCard" key="detail" class="selected-detail section-card">
        <div class="detail-header">
          <div class="detail-title-wrap">
            <div class="detail-icon" :style="{ background: getRoleColor(selectedCard.icon) }">
              {{ getRoleIcon(selectedCard.icon) }}
            </div>
            <h3 class="detail-title">
              <span class="title-bar"></span>
              {{ selectedCard.role_name }}
            </h3>
          </div>
          <el-button type="primary" size="large" class="confirm-btn fx-shine" @click="confirmSelect">
            确认选择，开始面试准备
          </el-button>
        </div>
        
        <el-tabs v-model="activeTab" class="detail-tabs">
          <el-tab-pane label="技术栈" name="tech">
            <div class="skill-tags fx-stagger">
              <el-tag
                v-for="tech in selectedCard.tech_stack"
                :key="tech"
                size="large"
                effect="plain"
                class="skill-tag"
              >
                {{ tech }}
              </el-tag>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="核心技能" name="core">
            <div class="skill-tags fx-stagger">
              <el-tag
                v-for="skill in selectedCard.core_skills"
                :key="skill"
                size="large"
                type="success"
                effect="plain"
                class="skill-tag"
              >
                {{ skill }}
              </el-tag>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="面试方向" name="direction">
            <div class="skill-tags fx-stagger">
              <el-tag
                v-for="dir in selectedCard.interview_directions"
                :key="dir"
                size="large"
                type="warning"
                effect="plain"
                class="skill-tag"
              >
                {{ dir }}
              </el-tag>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="题目分布" name="category">
            <div class="category-chart">
              <div
                v-for="cat in selectedCard.question_categories"
                :key="cat.name"
                class="category-item"
              >
                <div class="cat-name">{{ cat.name }}</div>
                <div class="cat-bar">
                  <div
                    class="cat-fill"
                    :style="{ width: cat.weight + '%', background: getRoleColor(selectedCard.icon) }"
                  ></div>
                </div>
                <div class="cat-weight">{{ cat.weight }}%</div>
              </div>
            </div>
          </el-tab-pane>
          
          <el-tab-pane label="岗位简介" name="summary">
            <div class="jd-summary">
              {{ selectedCard.jd_summary }}
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
      <div v-else key="hint" class="select-hint section-card">
        <el-icon class="hint-icon"><QuestionFilled /></el-icon>
        <span>点击选择一个岗位方向开始准备</span>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { QuestionFilled, ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { RoleCard } from '@/types/role_card'
import { getRoleIcon, getRoleColor } from '@/types/role_card'
import presetCardsData from '@/data/preset_role_cards.json'
import { useAppStore } from '@/stores/app'

const router = useRouter()
const appStore = useAppStore()

const presetCards = ref<RoleCard[]>(presetCardsData as RoleCard[])
const selectedId = ref<string>('')
const activeTab = ref('tech')

const selectedCard = computed(() => {
  if (!selectedId.value) return null
  return presetCards.value.find(c => c.id === selectedId.value) || null
})

function selectCard(card: RoleCard) {
  selectedId.value = card.id
}

function goBack() {
  router.push('/dashboard')
}

function confirmSelect() {
  if (!selectedCard.value) {
    ElMessage.warning('请先选择一个岗位方向')
    return
  }
  
  // 同时更新 store 状态和 localStorage
  appStore.setActiveCard(selectedCard.value)
  
  ElMessage.success(`已选择「${selectedCard.value.role_name}」，正在跳转...`)
  
  // 跳转到工作台
  setTimeout(() => {
    router.push('/dashboard')
  }, 500)
}
</script>

<style scoped>
.role-card-select {
  position: relative;
  overflow: hidden;
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--bc-space-8);
}

.page-header {
  text-align: center;
  margin-bottom: var(--bc-space-10);
}

.header-top {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.header-title {
  font-size: var(--bc-font-size-3xl);
  font-weight: 700;
  letter-spacing: -0.01em;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--bc-space-3);
  margin: 0;
}

.title-bar {
  width: 4px;
  height: 28px;
  border-radius: 2px;
  background: linear-gradient(180deg, var(--bc-primary) 0%, var(--bc-accent) 100%);
  flex-shrink: 0;
}

.back-btn {
  position: absolute;
  left: 0;
  color: var(--bc-text-soft) !important;
  font-size: var(--bc-font-size-base);
  cursor: pointer;
}

.back-btn:hover {
  color: var(--bc-primary-light) !important;
}

.subtitle {
  color: var(--bc-text-soft);
  font-size: var(--bc-font-size-base);
  margin-top: var(--bc-space-3);
}

.role-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--bc-space-5);
  margin-bottom: var(--bc-space-8);
}

.role-card {
  padding: var(--bc-space-6);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
  margin-bottom: 0;
}

.role-card.active {
  border-color: var(--bc-border-glow);
  box-shadow: var(--bc-shadow-lg), var(--bc-shadow-inner), var(--bc-shadow-glow);
}

.role-card.active::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1px;
  background: linear-gradient(135deg, var(--bc-primary), var(--bc-accent));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
  opacity: 0.8;
}

.card-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #fff;
  margin-bottom: var(--bc-space-4);
  box-shadow: var(--bc-shadow-inner);
}

.card-content {
  flex: 1;
}

.card-content h3 {
  font-size: var(--bc-font-size-xl);
  color: var(--bc-text);
  margin-bottom: var(--bc-space-2);
  font-weight: 600;
}

.card-desc {
  color: var(--bc-text-soft);
  font-size: var(--bc-font-size-sm);
  margin-bottom: var(--bc-space-3);
  line-height: 1.6;
}

.card-tags {
  display: flex;
  gap: var(--bc-space-2);
  margin-bottom: var(--bc-space-3);
}

.card-tech {
  font-size: var(--bc-font-size-sm);
  color: var(--bc-text-muted);
}

.tech-label {
  font-weight: 500;
  color: var(--bc-text-soft);
}

.tech-list {
  color: var(--bc-text-muted);
}

.card-action {
  margin-top: var(--bc-space-4);
  display: flex;
  justify-content: flex-end;
}

.selected-detail {
  padding: var(--bc-space-8);
  position: relative;
  overflow: hidden;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--bc-space-6);
  padding-bottom: var(--bc-space-5);
  border-bottom: 1px solid var(--bc-border);
}

.detail-title-wrap {
  display: flex;
  align-items: center;
  gap: var(--bc-space-4);
}

.detail-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #fff;
}

.detail-title {
  font-size: var(--bc-font-size-2xl);
  color: var(--bc-text);
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: var(--bc-space-3);
  margin: 0;
}

.confirm-btn {
  background: var(--bc-gradient-primary, linear-gradient(135deg, var(--bc-primary) 0%, var(--bc-primary-dark) 100%));
  border: none;
  border-radius: 10px;
  font-weight: 600;
  box-shadow: 0 4px 16px var(--bc-primary-glow);
}

.confirm-btn:hover {
  box-shadow: 0 6px 24px var(--bc-primary-glow);
}

.detail-tabs :deep(.el-tabs__item) {
  color: var(--bc-text-muted);
  font-weight: 500;
}

.detail-tabs :deep(.el-tabs__item.is-active) {
  color: var(--bc-primary-light);
}

.detail-tabs :deep(.el-tabs__active-bar) {
  background: linear-gradient(90deg, var(--bc-primary), var(--bc-accent));
}

.skill-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--bc-space-3);
}

.skill-tag {
  margin: 0;
  border-radius: var(--bc-radius-sm);
}

.category-chart {
  display: flex;
  flex-direction: column;
  gap: var(--bc-space-4);
}

.category-item {
  display: flex;
  align-items: center;
  gap: var(--bc-space-3);
}

.cat-name {
  width: 80px;
  font-weight: 500;
  color: var(--bc-text-soft);
  font-size: var(--bc-font-size-sm);
}

.cat-bar {
  flex: 1;
  height: 22px;
  background: var(--bc-bg-soft);
  border-radius: 11px;
  overflow: hidden;
  border: 1px solid var(--bc-border-soft);
}

.cat-fill {
  height: 100%;
  border-radius: 11px;
  transition: width 0.6s var(--bc-ease-out);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.cat-weight {
  width: 40px;
  text-align: right;
  color: var(--bc-text-muted);
  font-size: var(--bc-font-size-sm);
  font-weight: 500;
}

.jd-summary {
  color: var(--bc-text-soft);
  line-height: 1.8;
  font-size: var(--bc-font-size-base);
}

.select-hint {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--bc-space-3);
  color: var(--bc-text-muted);
  padding: var(--bc-space-10);
  font-size: var(--bc-font-size-lg);
}

.hint-icon {
  font-size: 20px;
  color: var(--bc-text-muted);
}

.detail-in-enter-active {
  transition: all 0.45s var(--bc-ease-out);
}
.detail-in-leave-active {
  transition: all 0.3s var(--bc-ease);
}
.detail-in-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.98);
}
.detail-in-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

@media (max-width: 768px) {
  .role-card-select {
    padding: var(--bc-space-4);
  }

  .header-title {
    font-size: var(--bc-font-size-2xl);
  }

  .role-cards-grid {
    grid-template-columns: 1fr;
  }

  .detail-header {
    flex-direction: column;
    gap: var(--bc-space-4);
    align-items: flex-start;
  }

  .confirm-btn {
    width: 100%;
  }
}
</style>
