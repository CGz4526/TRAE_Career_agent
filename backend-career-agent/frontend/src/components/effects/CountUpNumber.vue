<template>
  <span ref="elRef" class="count-up-number font-mono">
    {{ formattedValue }}
  </span>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

interface Props {
  value: number
  duration?: number
  suffix?: string
  prefix?: string
  decimals?: number
}

const props = withDefaults(defineProps<Props>(), {
  duration: 2000,
  suffix: '',
  prefix: '',
  decimals: 0,
})

const elRef = ref<HTMLElement | null>(null)
const currentValue = ref(0)
const isAnimating = ref(false)
const hasAnimated = ref(false)

let rafId: number | null = null
let observer: IntersectionObserver | null = null
let startTime: number | null = null
let startValue = 0
let targetValue = 0

const formattedValue = computed(() => {
  const formatted = currentValue.value.toFixed(props.decimals)
  return `${props.prefix}${formatted}${props.suffix}`
})

const easeOutExpo = (t: number): number => {
  return t === 1 ? 1 : 1 - Math.pow(2, -10 * t)
}

const animate = (timestamp: number) => {
  if (startTime === null) {
    startTime = timestamp
  }

  const elapsed = timestamp - startTime
  const progress = Math.min(elapsed / props.duration, 1)
  const easedProgress = easeOutExpo(progress)

  currentValue.value = startValue + (targetValue - startValue) * easedProgress

  if (progress < 1) {
    rafId = requestAnimationFrame(animate)
  } else {
    isAnimating.value = false
    rafId = null
  }
}

const startAnimation = (from: number, to: number) => {
  if (rafId !== null) {
    cancelAnimationFrame(rafId)
  }

  startValue = from
  targetValue = to
  startTime = null
  isAnimating.value = true

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  if (prefersReducedMotion) {
    currentValue.value = to
    isAnimating.value = false
    return
  }

  rafId = requestAnimationFrame(animate)
}

const play = () => {
  startAnimation(0, props.value)
}

const reset = () => {
  if (rafId !== null) {
    cancelAnimationFrame(rafId)
    rafId = null
  }
  currentValue.value = 0
  hasAnimated.value = false
  isAnimating.value = false
}

const pause = () => {
  if (rafId !== null) {
    cancelAnimationFrame(rafId)
    rafId = null
  }
  isAnimating.value = false
}

const resume = () => {
  if (isAnimating.value || currentValue.value >= props.value) return
  startAnimation(currentValue.value, props.value)
}

watch(() => props.value, (newVal, oldVal) => {
  if (hasAnimated.value && !isAnimating.value) {
    startAnimation(oldVal ?? 0, newVal)
  }
})

onMounted(() => {
  if (!elRef.value) return

  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  if (prefersReducedMotion) {
    currentValue.value = props.value
    hasAnimated.value = true
    return
  }

  observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting && !hasAnimated.value) {
          hasAnimated.value = true
          play()
        }
      })
    },
    { threshold: 0.3 }
  )

  observer.observe(elRef.value)
})

onUnmounted(() => {
  if (rafId !== null) {
    cancelAnimationFrame(rafId)
  }
  if (observer !== null) {
    observer.disconnect()
  }
})

defineExpose({
  play,
  reset,
  pause,
  resume,
})
</script>

<style scoped>
.count-up-number {
  display: inline-block;
  font-variant-numeric: tabular-nums;
  font-family: var(--bc-font-mono);
  letter-spacing: -0.02em;
}
</style>
