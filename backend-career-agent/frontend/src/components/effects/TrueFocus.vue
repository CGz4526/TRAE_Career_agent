<template>
  <div class="true-focus" :style="{ '--blur-amount': `${blurAmount}px`, '--border-color': borderColor, '--glow-color': glowColor, '--animation-duration': `${animationDuration}s`, '--pause-duration': `${pauseBetweenAnimations}s` }">
    <span
      v-for="(word, index) in words"
      :key="index"
      class="word"
      :class="{ active: activeIndex === index }"
    >
      {{ word }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'

interface TrueFocusProps {
  sentence?: string
  separator?: string
  manualMode?: boolean
  blurAmount?: number
  borderColor?: string
  glowColor?: string
  animationDuration?: number
  pauseBetweenAnimations?: number
}

const props = withDefaults(defineProps<TrueFocusProps>(), {
  sentence: 'Career Agent',
  separator: ' ',
  manualMode: false,
  blurAmount: 5,
  borderColor: '#6366f1',
  glowColor: 'rgba(99, 102, 241, 0.6)',
  animationDuration: 0.5,
  pauseBetweenAnimations: 1,
})

const activeIndex = ref(0)
let intervalId: number | null = null

const words = computed(() => props.sentence.split(props.separator))

function startAnimation() {
  if (props.manualMode) return
  intervalId = window.setInterval(() => {
    activeIndex.value = (activeIndex.value + 1) % words.value.length
  }, (props.animationDuration + props.pauseBetweenAnimations) * 1000)
}

function stopAnimation() {
  if (intervalId !== null) {
    clearInterval(intervalId)
    intervalId = null
  }
}

onMounted(() => {
  startAnimation()
})

onUnmounted(() => {
  stopAnimation()
})
</script>

<style scoped>
.true-focus {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 0;
  line-height: 1.2;
}

.word {
  position: relative;
  padding: 0 8px;
  filter: blur(var(--blur-amount));
  opacity: 0.3;
  transition:
    filter var(--animation-duration) ease,
    opacity var(--animation-duration) ease;
  color: var(--bc-text);
  font-weight: 700;
  letter-spacing: -0.02em;
}

.word.active {
  filter: blur(0);
  opacity: 1;
  color: var(--bc-text);
}

.word.active::before {
  content: '';
  position: absolute;
  inset: 0;
  border: 2px solid var(--border-color);
  border-radius: 4px;
  box-shadow:
    0 0 8px var(--glow-color),
    inset 0 0 8px var(--glow-color);
  animation: glow-pulse var(--animation-duration) ease-out;
}

.word.active::after {
  content: '';
  position: absolute;
  inset: -2px;
  border-radius: 6px;
  background: transparent;
  box-shadow: 0 0 20px var(--glow-color);
  opacity: 0;
  animation: glow-fade var(--animation-duration) ease-out;
}

@keyframes glow-pulse {
  0% {
    box-shadow:
      0 0 4px var(--glow-color),
      inset 0 0 4px var(--glow-color);
  }
  50% {
    box-shadow:
      0 0 12px var(--glow-color),
      inset 0 0 12px var(--glow-color);
  }
  100% {
    box-shadow:
      0 0 8px var(--glow-color),
      inset 0 0 8px var(--glow-color);
  }
}

@keyframes glow-fade {
  0% { opacity: 0.8; }
  100% { opacity: 0.4; }
}
</style>
