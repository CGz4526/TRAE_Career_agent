<template>
  <el-dialog
    v-model="visible"
    title="选择岗位方向"
    width="720px"
    align-center
    destroy-on-close
    class="role-selector-dialog"
  >
    <p class="selector-tip">选择一个预设岗位，将用于当前模块的 AI 处理</p>
    <div class="selector-list fx-stagger">
      <div
        v-for="card in appStore.presetCards"
        :key="card.id"
        class="selector-item fx-hover-lift"
        :class="{ active: selectedId === card.id }"
        @click="selectedId = card.id"
      >
        <div class="selector-icon" :style="{ background: getRoleColor(card.icon) }">
          {{ getRoleIcon(card.icon) }}
        </div>
        <div class="selector-info">
          <div class="selector-name">{{ card.role_name }}</div>
          <div class="selector-tech">{{ card.tech_stack.slice(0, 5).join('、') }}</div>
        </div>
        <el-icon v-if="selectedId === card.id" class="check-icon">
          <CircleCheckFilled />
        </el-icon>
      </div>
    </div>
    <template #footer>
      <el-button @click="handleCancel">取消</el-button>
      <el-button type="primary" :disabled="!selectedId" class="fx-shine" @click="handleConfirm">
        确认选择
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { CircleCheckFilled } from '@element-plus/icons-vue'
import { useAppStore } from '@/stores/app'
import { getRoleIcon, getRoleColor } from '@/types/role_card'
import type { RoleCard } from '@/types/role_card'

const props = defineProps<{
  modelValue: boolean
  currentCardId?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'select': [card: RoleCard]
}>()

const appStore = useAppStore()
const visible = ref(props.modelValue)
const selectedId = ref<string>('')

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    selectedId.value = props.currentCardId || appStore.activeCard?.id || ''
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

function handleCancel() {
  visible.value = false
}

function handleConfirm() {
  const card = appStore.presetCards.find(c => c.id === selectedId.value)
  if (card) {
    emit('select', card)
    visible.value = false
  }
}
</script>

<style scoped>
.role-selector-dialog :deep(.el-dialog) {
  background: var(--bc-bg-elev);
  border: 1px solid var(--bc-border);
  border-radius: var(--bc-radius-lg);
  box-shadow: var(--bc-shadow-xl);
}

.role-selector-dialog :deep(.el-dialog__title) {
  color: var(--bc-text);
  font-weight: 600;
}

.role-selector-dialog :deep(.el-dialog__header) {
  border-bottom: 1px solid var(--bc-border);
  padding-bottom: var(--bc-space-4);
}

.role-selector-dialog :deep(.el-dialog__footer) {
  border-top: 1px solid var(--bc-border);
  padding-top: var(--bc-space-4);
}

.selector-tip {
  margin: 0 0 var(--bc-space-4) 0;
  color: var(--bc-text-soft);
  font-size: var(--bc-font-size-sm);
}

.selector-list {
  display: flex;
  flex-direction: column;
  gap: var(--bc-space-3);
  max-height: 480px;
  overflow-y: auto;
  padding-right: 4px;
}

.selector-item {
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
  min-height: 72px;
}

.selector-item:hover {
  border-color: var(--bc-border-glow);
  box-shadow: var(--bc-shadow-md);
}

.selector-item.active {
  border-color: var(--bc-primary);
  background: rgba(99, 102, 241, 0.08);
  box-shadow: 0 0 0 1px var(--bc-primary-glow);
}

.selector-icon {
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

.selector-info {
  flex: 1;
  min-width: 0;
}

.selector-name {
  font-size: var(--bc-font-size-base);
  font-weight: 600;
  color: var(--bc-text);
  margin-bottom: 4px;
  line-height: 1.5;
}

.selector-tech {
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
  .role-selector-dialog :deep(.el-dialog) {
    width: 95% !important;
    margin: 0 auto;
  }
}
</style>
