<template>
  <div
    ref="cardRef"
    @pointermove="handlePointerMove"
    @pointerenter="handlePointerEnter"
    @pointerleave="handlePointerLeave"
    class="tilted-card"
    :class="className"
    :style="cardStyle"
    @click="$emit('click', $event)"
  >
    <div class="tilted-content" :style="contentStyle">
      <slot />
    </div>
    <div class="tilted-shine" :style="shineStyle" />
    <div class="tilted-border" :style="borderStyle" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'

interface TiltedCardProps {
  max?: number
  scale?: number
  speed?: number
  glareOpacity?: number
  className?: string
  glareColor?: string
}

const props = withDefaults(defineProps<TiltedCardProps>(), {
  max: 15,
  scale: 1.02,
  speed: 400,
  glareOpacity: 0.1,
  className: '',
  glareColor: '255, 255, 255'
})

defineEmits<{
  click: [e: MouseEvent]
}>()

const cardRef = ref<HTMLDivElement | null>(null)
const isHovered = ref(false)
const rotation = reactive({ x: 0, y: 0 })
const position = reactive({ x: 50, y: 50 })

const cardStyle = computed(() => ({
  transform: `perspective(1000px) rotateX(${rotation.x}deg) rotateY(${rotation.y}deg) scale(${isHovered.value ? props.scale : 1})`,
  transition: isHovered.value
    ? `transform ${props.speed}ms cubic-bezier(0.03, 0.98, 0.52, 0.99)`
    : 'transform 500ms ease',
}))

const contentStyle = computed(() => ({
  transform: 'translateZ(30px)',
  transformStyle: 'preserve-3d',
}))

const shineStyle = computed(() => ({
  background: `radial-gradient(circle at ${position.x}% ${position.y}%, rgba(${props.glareColor}, 0.35) 0%, transparent 60%)`,
  opacity: isHovered.value ? 1 : 0,
}))

const borderStyle = computed(() => ({
  background: `radial-gradient(circle at ${position.x}% ${position.y}%, rgba(${props.glareColor}, 0.4) 0%, transparent 40%)`,
  opacity: isHovered.value ? 1 : 0,
}))

function handlePointerMove(e: PointerEvent) {
  const card = cardRef.value
  if (!card) return

  const rect = card.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  const centerX = rect.width / 2
  const centerY = rect.height / 2

  const rotateX = ((y - centerY) / centerY) * -props.max
  const rotateY = ((x - centerX) / centerX) * props.max

  rotation.x = rotateX
  rotation.y = rotateY
  position.x = (x / rect.width) * 100
  position.y = (y / rect.height) * 100
}

function handlePointerEnter() {
  isHovered.value = true
}

function handlePointerLeave() {
  isHovered.value = false
  rotation.x = 0
  rotation.y = 0
  position.x = 50
  position.y = 50
}
</script>

<style scoped>
.tilted-card {
  position: relative;
  transform-style: preserve-3d;
  cursor: pointer;
  border-radius: 20px;
  transition: box-shadow 0.4s ease;
}

.tilted-card:hover {
  box-shadow:
    0 25px 50px -12px rgba(0, 0, 0, 0.5),
    0 0 30px rgba(99, 102, 241, 0.1);
}

.tilted-content {
  position: relative;
  z-index: 2;
  transform-style: preserve-3d;
  width: 100%;
  height: 100%;
}

.tilted-shine {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  z-index: 3;
  mix-blend-mode: overlay;
  transition: opacity 0.3s ease;
}

.tilted-border {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
  z-index: 4;
  padding: 1px;
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  transition: opacity 0.3s ease;
}
</style>
