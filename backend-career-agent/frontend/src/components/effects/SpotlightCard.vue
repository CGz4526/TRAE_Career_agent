<template>
  <div
    ref="divRef"
    @mousemove="handleMouseMove"
    @focus="handleFocus"
    @blur="handleBlur"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
    class="spotlight-card"
    :class="className"
  >
    <div
      class="spotlight-glow"
      :style="{
        opacity: glowOpacity,
        background: `radial-gradient(circle at ${position.x}px ${position.y}px, ${spotlightColor}, transparent 80%)`,
      }"
    />

    <div class="card-content">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Position {
  x: number
  y: number
}

interface SpotlightCardProps {
  className?: string
  spotlightColor?: string
}

const props = withDefaults(defineProps<SpotlightCardProps>(), {
  className: '',
  spotlightColor: 'rgba(255, 255, 255, 0.15)',
})

const divRef = ref<HTMLDivElement | null>(null)
const isFocused = ref<boolean>(false)
const position = ref<Position>({ x: 0, y: 0 })
const glowOpacity = ref<number>(0)

const handleMouseMove = (e: MouseEvent) => {
  if (!divRef.value || isFocused.value) return

  const rect = divRef.value.getBoundingClientRect()
  position.value = { x: e.clientX - rect.left, y: e.clientY - rect.top }
}

const handleFocus = () => {
  isFocused.value = true
  glowOpacity.value = 0.6
}

const handleBlur = () => {
  isFocused.value = false
  glowOpacity.value = 0
}

const handleMouseEnter = () => {
  glowOpacity.value = 0.6
}

const handleMouseLeave = () => {
  glowOpacity.value = 0
}
</script>

<style scoped>
.spotlight-card {
  position: relative;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.3s var(--bc-ease-out);
}

.spotlight-card:hover {
  transform: translateY(-2px);
}

.spotlight-glow {
  position: absolute;
  inset: 0;
  pointer-events: none;
  transition: opacity 0.5s ease-in-out;
  z-index: 1;
}

.card-content {
  position: relative;
  z-index: 2;
}

@media (prefers-reduced-motion: reduce) {
  .spotlight-card {
    transition: none;
  }

  .spotlight-card:hover {
    transform: none;
  }

  .spotlight-glow {
    display: none;
  }
}
</style>
