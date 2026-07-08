<template>
  <div class="bg-decorations">
    <div class="decor-left">
      <svg class="decor-svg" viewBox="0 0 200 700" fill="none" xmlns="http://www.w3.org/2000/svg">
        <g opacity="0.08">
          <circle cx="100" cy="80" r="50" stroke="currentColor" stroke-width="1" stroke-dasharray="4 3" />
          <circle cx="100" cy="80" r="35" stroke="currentColor" stroke-width="0.8" stroke-dasharray="2 2" />
          <circle cx="100" cy="80" r="20" stroke="currentColor" stroke-width="0.6" />
        </g>

        <g opacity="0.06">
          <path d="M40 180 L160 180" stroke="currentColor" stroke-width="1" />
          <path d="M50 195 L150 195" stroke="currentColor" stroke-width="0.8" />
          <path d="M60 210 L140 210" stroke="currentColor" stroke-width="0.6" />
          <path d="M70 225 L130 225" stroke="currentColor" stroke-width="0.5" />
        </g>

        <g opacity="0.07">
          <rect x="60" y="270" width="80" height="80" rx="10" stroke="currentColor" stroke-width="1" />
          <rect x="72" y="282" width="56" height="56" rx="6" stroke="currentColor" stroke-width="0.8" />
          <path d="M80 300 L120 300" stroke="currentColor" stroke-width="0.6" />
          <path d="M80 315 L110 315" stroke="currentColor" stroke-width="0.5" />
          <circle cx="100" cy="325" r="4" fill="currentColor" opacity="0.3" />
        </g>

        <g opacity="0.05">
          <path d="M30 390 Q60 370 90 390 T150 390 T180 390" stroke="currentColor" stroke-width="1" fill="none" />
          <path d="M20 410 Q50 395 80 410 T140 410 T170 410" stroke="currentColor" stroke-width="0.7" fill="none" />
        </g>

        <g opacity="0.06">
          <polygon points="100,480 140,540 60,540" stroke="currentColor" stroke-width="1" fill="none" />
          <polygon points="100,500 125,535 75,535" stroke="currentColor" stroke-width="0.7" fill="none" />
          <circle cx="100" cy="515" r="3" fill="currentColor" opacity="0.4" />
        </g>

        <g opacity="0.07">
          <circle v-for="i in 12" :key="'dot-l-'+i"
            :cx="35 + ((i - 1) % 6) * 26"
            :cy="580 + Math.floor((i - 1) / 6) * 22"
            r="3"
            fill="currentColor"
          />
        </g>

        <g opacity="0.04">
          <path d="M20 640 L40 620 L60 640 L80 620 L100 640 L120 620 L140 640 L160 620 L180 640"
                stroke="currentColor" stroke-width="1" fill="none" />
        </g>
      </svg>
    </div>

    <div class="decor-right">
      <svg class="decor-svg" viewBox="0 0 200 700" fill="none" xmlns="http://www.w3.org/2000/svg">
        <g opacity="0.06">
          <path d="M20 70 Q60 50 100 70 T180 70" stroke="currentColor" stroke-width="1" fill="none" />
          <path d="M30 90 Q70 75 110 90 T170 90" stroke="currentColor" stroke-width="0.8" fill="none" />
          <path d="M40 110 Q80 100 120 110 T160 110" stroke="currentColor" stroke-width="0.6" fill="none" />
        </g>

        <g opacity="0.07">
          <rect x="55" y="160" width="90" height="90" rx="12" stroke="currentColor" stroke-width="1" />
          <rect x="70" y="175" width="60" height="60" rx="8" stroke="currentColor" stroke-width="0.8" />
          <rect x="82" y="187" width="36" height="36" rx="4" stroke="currentColor" stroke-width="0.6" />
          <circle cx="100" cy="205" r="5" fill="currentColor" opacity="0.25" />
        </g>

        <g opacity="0.05">
          <circle cx="100" cy="310" r="45" stroke="currentColor" stroke-width="1" stroke-dasharray="5 3" />
          <circle cx="100" cy="310" r="30" stroke="currentColor" stroke-width="0.8" stroke-dasharray="3 2" />
          <circle cx="100" cy="310" r="15" stroke="currentColor" stroke-width="0.6" />
          <path d="M100 270 L100 290" stroke="currentColor" stroke-width="0.8" />
          <path d="M100 330 L100 350" stroke="currentColor" stroke-width="0.8" />
          <path d="M60 310 L80 310" stroke="currentColor" stroke-width="0.8" />
          <path d="M120 310 L140 310" stroke="currentColor" stroke-width="0.8" />
        </g>

        <g opacity="0.06">
          <path d="M30 400 L170 400" stroke="currentColor" stroke-width="1" />
          <path d="M45 418 L155 418" stroke="currentColor" stroke-width="0.8" />
          <path d="M60 436 L140 436" stroke="currentColor" stroke-width="0.6" />
          <path d="M75 454 L125 454" stroke="currentColor" stroke-width="0.5" />
        </g>

        <g opacity="0.07">
          <polygon points="100,510 135,560 65,560" stroke="currentColor" stroke-width="1" fill="none" />
          <polygon points="100,525 122,555 78,555" stroke="currentColor" stroke-width="0.7" fill="none" />
          <path d="M85 540 L115 540" stroke="currentColor" stroke-width="0.6" />
        </g>

        <g opacity="0.05">
          <path v-for="i in 5" :key="'star-'+i"
            :d="starPath(40 + (i-1) * 30, 620, 6, 3, 5)"
            stroke="currentColor"
            stroke-width="0.6"
            fill="none"
          />
        </g>

        <g opacity="0.06">
          <circle v-for="i in 10" :key="'dot-r-'+i"
            :cx="50 + ((i - 1) % 5) * 25"
            :cy="660 + Math.floor((i - 1) / 5) * 20"
            r="2.5"
            fill="currentColor"
          />
        </g>
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
function starPath(cx: number, cy: number, outerR: number, innerR: number, points: number): string {
  const path: string[] = []
  for (let i = 0; i < points * 2; i++) {
    const r = i % 2 === 0 ? outerR : innerR
    const angle = (Math.PI / points) * i - Math.PI / 2
    const x = cx + Math.cos(angle) * r
    const y = cy + Math.sin(angle) * r
    path.push(`${i === 0 ? 'M' : 'L'}${x.toFixed(1)} ${y.toFixed(1)}`)
  }
  path.push('Z')
  return path.join(' ')
}
</script>

<style scoped>
.bg-decorations {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
  color: #ffffff;
}

.decor-left {
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  width: 180px;
  height: 700px;
}

.decor-right {
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
  width: 180px;
  height: 700px;
}

.decor-svg {
  width: 100%;
  height: 100%;
  animation: float-slow 18s ease-in-out infinite;
}

@keyframes float-slow {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-15px);
  }
}

.decor-right .decor-svg {
  animation-delay: -9s;
}

@media (max-width: 1400px) {
  .decor-left,
  .decor-right {
    opacity: 0.7;
  }
}

@media (max-width: 1200px) {
  .decor-left,
  .decor-right {
    display: none;
  }
}
</style>
