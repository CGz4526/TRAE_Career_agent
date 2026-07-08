<template>
  <div class="noise-grain-bg" :style="containerStyle">
    <svg class="noise-svg" xmlns="http://www.w3.org/2000/svg">
      <filter id="noise-filter">
        <feTurbulence
          type="fractalNoise"
          :baseFrequency="baseFrequency"
          numOctaves="3"
          stitchTiles="stitch"
        />
      </filter>
      <rect width="100%" height="100%" filter="url(#noise-filter)" />
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

/**
 * 噪点颗粒纹理背景组件
 * 灵感来自高端设计网站的胶片颗粒质感
 * 使用 SVG feTurbulence 生成噪点纹理
 * 极低透明度叠加在背景上，增加质感
 */
interface Props {
  /** 透明度（0-1） */
  opacity?: number
  /** 噪点大小缩放（值越大颗粒越细） */
  scale?: number
  /** 混合模式 */
  blendMode?: string
}

const props = withDefaults(defineProps<Props>(), {
  opacity: 0.04,
  scale: 1,
  blendMode: 'overlay',
})

const baseFrequency = computed(() => {
  return 0.85 / props.scale
})

const containerStyle = computed(() => ({
  opacity: props.opacity,
  mixBlendMode: props.blendMode,
} as Record<string, string>))
</script>

<style scoped>
.noise-grain-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.noise-svg {
  width: 100%;
  height: 100%;
  display: block;
}
</style>
