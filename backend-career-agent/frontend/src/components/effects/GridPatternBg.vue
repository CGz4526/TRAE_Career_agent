<template>
  <div class="grid-pattern-bg" :style="containerStyle">
    <svg class="grid-svg" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <pattern
          v-if="!dot"
          id="grid-pattern"
          :width="size"
          :height="size"
          patternUnits="userSpaceOnUse"
        >
          <path
            :d="`M ${size} 0 L 0 0 0 ${size}`"
            fill="none"
            :stroke="color"
            stroke-width="1"
          />
        </pattern>
        <pattern
          v-else
          id="grid-pattern"
          :width="size"
          :height="size"
          patternUnits="userSpaceOnUse"
        >
          <circle cx="1" cy="1" r="1" :fill="color" />
        </pattern>
        <radialGradient
          v-if="gradient"
          id="grid-mask-gradient"
          cx="50%"
          cy="50%"
          r="70%"
        >
          <stop offset="0%" stop-color="white" stop-opacity="1" />
          <stop offset="100%" stop-color="white" stop-opacity="0" />
        </radialGradient>
        <mask v-if="gradient" id="grid-mask">
          <rect width="100%" height="100%" fill="url(#grid-mask-gradient)" />
        </mask>
      </defs>
      <rect
        width="100%"
        height="100%"
        fill="url(#grid-pattern)"
        :mask="gradient ? 'url(#grid-mask)' : undefined"
      />
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

/**
 * 网格图案背景组件
 * 灵感来自现代 SaaS 网站的网格背景 + 渐变叠加
 * SVG 网格线背景，带径向渐变遮罩
 */
interface Props {
  /** 网格大小 px */
  size?: number
  /** 网格线颜色 */
  color?: string
  /** 透明度（0-1） */
  opacity?: number
  /** 是否有径向渐变遮罩 */
  gradient?: boolean
  /** 是否是点阵网格而非线条 */
  dot?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 40,
  color: '#ffffff',
  opacity: 0.03,
  gradient: true,
  dot: false,
})

const containerStyle = computed(() => ({
  opacity: props.opacity,
}))
</script>

<style scoped>
.grid-pattern-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.grid-svg {
  width: 100%;
  height: 100%;
  display: block;
}
</style>
