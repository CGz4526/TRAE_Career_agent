<template>
  <div
    ref="blobRef"
    class="blob-cursor"
    :style="blobStyle"
  />
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, onBeforeUnmount } from 'vue'

interface Props {
  size?: number
  color?: string
  blur?: number
  speed?: number
}

const props = withDefaults(defineProps<Props>(), {
  size: 350,
  color: '',
  blur: 120,
  speed: 0.15,
})

const blobRef = ref<HTMLElement | null>(null)
const currentX = ref(-9999)
const currentY = ref(-9999)
const targetX = ref(-9999)
const targetY = ref(-9999)
const isVisible = ref(false)

let rafId: number | null = null
let reducedMotion = false

const blobStyle = computed(() => {
  const bgColor = props.color || `linear-gradient(135deg, var(--bc-aurora-1), var(--bc-aurora-3))`
  return {
    width: `${props.size}px`,
    height: `${props.size}px`,
    background: bgColor,
    filter: `blur(${props.blur}px)`,
    transform: `translate(${currentX.value - props.size / 2}px, ${currentY.value - props.size / 2}px)`,
    opacity: isVisible.value ? 0.4 : 0,
  }
})

const lerp = (start: number, end: number, factor: number): number => {
  return start + (end - start) * factor
}

const animate = () => {
  if (reducedMotion) return

  currentX.value = lerp(currentX.value, targetX.value, props.speed)
  currentY.value = lerp(currentY.value, targetY.value, props.speed)

  rafId = requestAnimationFrame(animate)
}

const handleMouseMove = (e: MouseEvent) => {
  targetX.value = e.clientX
  targetY.value = e.clientY
  if (!isVisible.value) {
    currentX.value = e.clientX
    currentY.value = e.clientY
    isVisible.value = true
  }
}

const handleMouseLeave = () => {
  isVisible.value = false
}

const checkReducedMotion = () => {
  reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

onMounted(() => {
  checkReducedMotion()

  if (reducedMotion) return

  window.addEventListener('mousemove', handleMouseMove)
  window.addEventListener('mouseleave', handleMouseLeave)
  window.addEventListener('mouseout', (e) => {
    if (e.relatedTarget === null) {
      isVisible.value = false
    }
  })

  animate()
})

onBeforeUnmount(() => {
  if (rafId !== null) {
    cancelAnimationFrame(rafId)
  }
  window.removeEventListener('mousemove', handleMouseMove)
  window.removeEventListener('mouseleave', handleMouseLeave)
})
</script>

<style scoped>
.blob-cursor {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 0;
  pointer-events: none;
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.5s ease;
  will-change: transform, opacity;
}

@media (prefers-reduced-motion: reduce) {
  .blob-cursor {
    display: none;
  }
}
</style>
