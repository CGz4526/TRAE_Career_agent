<template>
  <div class="magic-bento" :style="bentoStyle">
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// Props 定义
interface Props {
  /** 列数，默认 4 */
  columns?: number
  /** 间距 px，默认 16 */
  gap?: number
  /** 行数，'auto' 为自动 */
  rows?: 'auto' | number
}

const props = withDefaults(defineProps<Props>(), {
  columns: 4,
  gap: 16,
  rows: 'auto',
})

// Bento 容器样式
const bentoStyle = computed(() => {
  const style: Record<string, string> = {
    '--bento-columns': String(props.columns),
    '--bento-gap': `${props.gap}px`,
  }

  if (props.rows !== 'auto') {
    style['--bento-rows'] = String(props.rows)
    style.gridAutoRows = 'minmax(0, 1fr)'
  }

  return style
})
</script>

<style scoped>
.magic-bento {
  display: grid;
  grid-template-columns: repeat(var(--bento-columns), minmax(0, 1fr));
  gap: var(--bento-gap);
  width: 100%;
}

/* 子元素通过 CSS 变量控制跨度
 * 用法示例：
 * <div style="--col-span: 2; --row-span: 1;">内容</div>
 */
.magic-bento :deep(*) {
  --col-span: 1;
  --row-span: 1;
  grid-column: span var(--col-span);
  grid-row: span var(--row-span);
}

/* 响应式：移动端自动变 2 列 */
@media (max-width: 768px) {
  .magic-bento {
    --bento-columns: 2;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  /* 移动端下，跨列超过 2 的限制为 2 */
  .magic-bento :deep(*) {
    --col-span: min(var(--col-span), 2);
  }
}

@media (max-width: 480px) {
  .magic-bento {
    --bento-columns: 1;
    grid-template-columns: 1fr;
  }

  .magic-bento :deep(*) {
    --col-span: 1;
    grid-column: span 1;
  }
}
</style>
