<template>
  <div class="radiant-beams">
    <svg class="beams-svg" viewBox="0 0 1000 1000" preserveAspectRatio="xMidYMid slice">
      <defs>
        <radialGradient id="beam-fade" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stop-color="currentColor" stop-opacity="0.6" />
          <stop offset="100%" stop-color="currentColor" stop-opacity="0" />
        </radialGradient>
        <mask id="beam-mask">
          <rect width="1000" height="1000" fill="black" />
          <g fill="white" class="beams-group" :style="beamsGroupStyle">
            <path
              v-for="(_, i) in beamCount"
              :key="i"
              :d="getBeamPath(i)"
              fill="url(#beam-fade)"
            />
          </g>
        </mask>
      </defs>
      <g :style="beamsGroupStyle" class="beams-rotate">
        <rect
          v-for="(color, i) in colors"
          :key="i"
          x="0"
          y="0"
          width="1000"
          height="1000"
          :fill="color"
          :style="{ opacity: 1 / colors.length }"
          mask="url(#beam-mask)"
        />
      </g>
    </svg>
    <div class="beams-blur" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  colors?: string[]
  speed?: number
  beams?: number
}

const props = withDefaults(defineProps<Props>(), {
  colors: () => [
    'var(--bc-aurora-1)',
    'var(--bc-aurora-2)',
    'var(--bc-aurora-3)',
    'var(--bc-aurora-4)',
  ],
  speed: 1,
  beams: 12,
})

const beamCount = computed(() => Math.max(4, props.beams))

const beamsGroupStyle = computed(() => ({
  animationDuration: `${60 / props.speed}s`,
}))

const getBeamPath = (index: number): string => {
  const angleStep = 360 / beamCount.value
  const angle = index * angleStep
  const centerX = 500
  const centerY = 500
  const beamWidth = angleStep * 0.35
  const outerRadius = 700
  const innerRadius = 50

  const angle1 = angle - beamWidth / 2
  const angle2 = angle + beamWidth / 2

  const x1 = centerX + innerRadius * Math.cos((angle1 * Math.PI) / 180)
  const y1 = centerY + innerRadius * Math.sin((angle1 * Math.PI) / 180)
  const x2 = centerX + outerRadius * Math.cos((angle1 * Math.PI) / 180)
  const y2 = centerY + outerRadius * Math.sin((angle1 * Math.PI) / 180)
  const x3 = centerX + outerRadius * Math.cos((angle2 * Math.PI) / 180)
  const y3 = centerY + outerRadius * Math.sin((angle2 * Math.PI) / 180)
  const x4 = centerX + innerRadius * Math.cos((angle2 * Math.PI) / 180)
  const y4 = centerY + innerRadius * Math.sin((angle2 * Math.PI) / 180)

  return `M ${centerX} ${centerY} L ${x1} ${y1} L ${x2} ${y2} A ${outerRadius} ${outerRadius} 0 0 1 ${x3} ${y3} L ${x4} ${y4} Z`
}
</script>

<style scoped>
.radiant-beams {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  opacity: 0.15;
  z-index: 0;
}

.beams-svg {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
}

.beams-rotate {
  transform-origin: 500px 500px;
  animation: beams-spin linear infinite;
  will-change: transform;
}

.beams-blur {
  position: absolute;
  inset: 0;
  backdrop-filter: blur(40px);
  -webkit-backdrop-filter: blur(40px);
  pointer-events: none;
}

@keyframes beams-spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .beams-rotate {
    animation: none;
  }
}
</style>
