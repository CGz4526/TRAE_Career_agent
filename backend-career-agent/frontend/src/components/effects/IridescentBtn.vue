<template>
  <button
    class="iridescent-btn"
    :class="[`size-${size}`, `variant-${variant}`]"
    @click="handleClick"
  >
    <span class="btn-inner">
      <slot>{{ text }}</slot>
    </span>
  </button>
</template>

<script setup lang="ts">
interface Props {
  text?: string
  size?: 'sm' | 'md' | 'lg'
  variant?: 'primary' | 'outline'
}

const props = withDefaults(defineProps<Props>(), {
  text: '',
  size: 'md',
  variant: 'primary',
})

const emit = defineEmits<{
  click: [e: MouseEvent]
}>()

const handleClick = (e: MouseEvent) => {
  emit('click', e)
}
</script>

<style scoped>
.iridescent-btn {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  cursor: pointer;
  font-family: var(--bc-font-heading);
  font-weight: var(--bc-font-weight-medium);
  letter-spacing: var(--bc-letter-tight);
  color: var(--bc-text);
  overflow: hidden;
  transition: transform 0.3s var(--bc-ease-out),
    box-shadow 0.3s var(--bc-ease-out);
  will-change: transform;
}

.iridescent-btn::before {
  content: '';
  position: absolute;
  inset: -2px;
  border-radius: inherit;
  background: conic-gradient(
    from 0deg,
    var(--bc-aurora-1),
    var(--bc-aurora-2),
    var(--bc-aurora-3),
    var(--bc-aurora-4),
    var(--bc-aurora-1)
  );
  animation: iridescent-rotate 4s linear infinite;
  z-index: 0;
  opacity: 0.8;
}

.iridescent-btn::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  z-index: 1;
  pointer-events: none;
}

.btn-inner {
  position: relative;
  z-index: 2;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  border-radius: inherit;
  transition: background 0.3s var(--bc-ease),
    box-shadow 0.3s var(--bc-ease);
}

.variant-primary .btn-inner {
  background: var(--bc-bg-glass);
  backdrop-filter: blur(var(--bc-glass-blur)) saturate(var(--bc-glass-saturate));
  -webkit-backdrop-filter: blur(var(--bc-glass-blur)) saturate(var(--bc-glass-saturate));
}

.variant-outline .btn-inner {
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(var(--bc-glass-blur)) saturate(var(--bc-glass-saturate));
  -webkit-backdrop-filter: blur(var(--bc-glass-blur)) saturate(var(--bc-glass-saturate));
}

.size-sm {
  padding: 2px;
  border-radius: var(--bc-radius-sm);
  font-size: var(--bc-font-size-sm);
}

.size-sm .btn-inner {
  padding: 6px 14px;
}

.size-md {
  padding: 2px;
  border-radius: var(--bc-radius-md);
  font-size: var(--bc-font-size-base);
}

.size-md .btn-inner {
  padding: 10px 22px;
}

.size-lg {
  padding: 2px;
  border-radius: var(--bc-radius-lg);
  font-size: var(--bc-font-size-lg);
}

.size-lg .btn-inner {
  padding: 14px 30px;
}

.iridescent-btn:hover {
  transform: translateY(-2px) scale(1.02);
  box-shadow: var(--bc-shadow-glow), 0 8px 32px rgba(255, 255, 255, 0.1);
}

.iridescent-btn:hover::before {
  animation-duration: 1.5s linear infinite;
  opacity: 1;
}

.variant-primary:hover .btn-inner {
  background: rgba(255, 255, 255, 0.08);
}

.variant-outline:hover .btn-inner {
  background: rgba(255, 255, 255, 0.05);
}

.iridescent-btn:active {
  transform: translateY(0) scale(0.98);
}

.iridescent-btn:active .btn-inner {
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.4);
}

@keyframes iridescent-rotate {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@media (prefers-reduced-motion: reduce) {
  .iridescent-btn::before {
    animation: none;
  }

  .iridescent-btn,
  .btn-inner {
    transition: none;
  }

  .iridescent-btn:hover {
    transform: none;
  }
}
</style>
