<template>
  <span
    class="shiny-text"
    :class="{ 'is-hover-paused': pauseOnHover }"
    :style="textStyle"
  >
    {{ text }}
  </span>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  text: string
  color?: string
  shineColor?: string
  speed?: number
  spread?: number
  delay?: number
  direction?: 'left' | 'right'
  yoyo?: boolean
  pauseOnHover?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  color: '#ffffff',
  shineColor: '#ffffff',
  speed: 3,
  spread: 0.5,
  delay: 0,
  direction: 'left',
  yoyo: false,
  pauseOnHover: false,
})

const textStyle = computed(() => {
  const spreadPercent = props.spread * 100
  const gradientStart = (100 - spreadPercent) / 2
  const gradientEnd = gradientStart + spreadPercent
  const animationDirection = props.direction === 'right' ? 'reverse' : 'normal'
  const animationIteration = props.yoyo ? 'infinite' : 'infinite'
  const animationDirectionFinal = props.yoyo ? 'alternate' : animationDirection

  return {
    '--shiny-color': props.color,
    '--shine-color': props.shineColor,
    '--gradient-start': `${gradientStart}%`,
    '--gradient-end': `${gradientEnd}%`,
    animationDuration: `${props.speed}s`,
    animationDelay: `${props.delay}s`,
    animationDirection: animationDirectionFinal,
    animationIterationCount: animationIteration,
  }
})
</script>

<style scoped>
.shiny-text {
  background: linear-gradient(
    110deg,
    var(--shiny-color) var(--gradient-start),
    var(--shine-color) 50%,
    var(--shiny-color) var(--gradient-end)
  );
  background-size: 200% 100%;
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  color: transparent;
  animation-name: shiny-shine;
  animation-timing-function: ease-in-out;
  animation-iteration-count: infinite;
  display: inline-block;
}

@keyframes shiny-shine {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.is-hover-paused:hover {
  animation-play-state: paused;
}

@media (prefers-reduced-motion: reduce) {
  .shiny-text {
    animation: none;
    background: var(--shiny-color);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    color: transparent;
  }
}
</style>
