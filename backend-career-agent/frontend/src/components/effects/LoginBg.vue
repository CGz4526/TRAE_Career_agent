<template>
  <div class="login-bg">
    <div class="prism-wrap">
      <PrismBg
        :height="3.5"
        :base-width="5.5"
        :animation-type="'rotate'"
        :glow="1"
        :offset="{ x: 0, y: 0 }"
        :noise="0.5"
        :transparent="true"
        :scale="3.5"
        :hue-shift="0"
        :color-frequency="1"
        :bloom="0.9"
        :time-scale="0.4"
      />
    </div>

    <div class="bg-grid"></div>

    <div class="bg-vignette"></div>
  </div>
</template>

<script setup lang="ts">
import PrismBg from './PrismBg.vue'
</script>

<style scoped>
.login-bg {
  position: fixed;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  z-index: 0;
  background: #0a0a0a;
  display: flex;
  align-items: center;
  justify-content: center;
}

.prism-wrap {
  width: 1200px;
  height: 1200px;
  max-width: 100vw;
  max-height: 100vh;
  position: relative;
  border-radius: 50%;
  overflow: hidden;
  filter: blur(60px);
  opacity: 0.75;
}

.prism-wrap :deep(.prism-container) {
  z-index: 0 !important;
}

.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.04) 1px, transparent 1px);
  background-size: 60px 60px;
  mask-image: radial-gradient(ellipse at center, black 30%, transparent 75%);
  -webkit-mask-image: radial-gradient(ellipse at center, black 30%, transparent 75%);
  z-index: 1;
}

.bg-vignette {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse at 50% 50%, transparent 40%, rgba(0, 0, 0, 0.75) 100%);
  z-index: 2;
}
</style>
