<template>
  <div class="glass-toggle-wrapper">
    <button
      class="glass-toggle"
      :class="{ 'is-on': modelValue, 'is-off': !modelValue }"
      role="switch"
      :aria-checked="modelValue"
      @click="toggle"
    >
      <span class="toggle-track">
        <span class="track-highlight" />
        <span class="toggle-thumb">
          <span class="thumb-highlight" />
          <span class="thumb-shadow" />
        </span>
      </span>
    </button>
    <span v-if="label" class="toggle-label">{{ label }}</span>
  </div>
</template>

<script setup lang="ts">
interface Props {
  modelValue: boolean
  label?: string
}

const props = withDefaults(defineProps<Props>(), {
  label: '',
})

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const toggle = () => {
  emit('update:modelValue', !props.modelValue)
}
</script>

<style scoped>
.glass-toggle-wrapper {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  user-select: none;
}

.glass-toggle {
  position: relative;
  width: 52px;
  height: 28px;
  border: none;
  padding: 0;
  background: transparent;
  cursor: pointer;
  flex-shrink: 0;
}

.toggle-track {
  position: absolute;
  inset: 0;
  border-radius: 9999px;
  background: var(--bc-bg-glass);
  backdrop-filter: blur(var(--bc-glass-blur)) saturate(var(--bc-glass-saturate));
  -webkit-backdrop-filter: blur(var(--bc-glass-blur)) saturate(var(--bc-glass-saturate));
  border: 1px solid var(--bc-border);
  transition: background 0.3s var(--bc-ease),
    border-color 0.3s var(--bc-ease),
    box-shadow 0.3s var(--bc-ease);
  overflow: hidden;
}

.track-highlight {
  position: absolute;
  top: 0;
  left: 8px;
  right: 8px;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(255, 255, 255, 0.15),
    transparent
  );
  pointer-events: none;
}

.is-on .toggle-track {
  background: rgba(234, 179, 8, 0.15);
  border-color: rgba(234, 179, 8, 0.4);
  box-shadow: 0 0 20px rgba(234, 179, 8, 0.15),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.is-off .toggle-track {
  background: var(--bc-bg-glass);
  border-color: var(--bc-border);
}

.toggle-thumb {
  position: absolute;
  top: 3px;
  left: 3px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: linear-gradient(180deg, #ffffff 0%, #e2e8f0 100%);
  transition: transform 0.35s var(--bc-ease-spring),
    background 0.3s var(--bc-ease),
    box-shadow 0.3s var(--bc-ease);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.1);
}

.is-on .toggle-thumb {
  transform: translateX(24px);
  background: linear-gradient(180deg, #fde047 0%, #ca8a04 100%);
  box-shadow: 0 2px 12px rgba(234, 179, 8, 0.4),
    0 0 0 1px rgba(234, 179, 8, 0.3);
}

.thumb-highlight {
  position: absolute;
  top: 3px;
  left: 5px;
  right: 5px;
  height: 6px;
  border-radius: 50%;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.6) 0%, rgba(255, 255, 255, 0) 100%);
  pointer-events: none;
}

.is-on .thumb-highlight {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.5) 0%, rgba(255, 255, 255, 0) 100%);
}

.thumb-shadow {
  position: absolute;
  bottom: 2px;
  left: 4px;
  right: 4px;
  height: 4px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.15);
  filter: blur(2px);
  pointer-events: none;
}

.toggle-label {
  font-family: var(--bc-font-body);
  font-size: var(--bc-font-size-base);
  color: var(--bc-text);
  cursor: pointer;
}

.glass-toggle:hover .toggle-thumb {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4),
    0 0 0 1px rgba(255, 255, 255, 0.15);
}

.is-on.glass-toggle:hover .toggle-thumb {
  box-shadow: 0 4px 16px rgba(234, 179, 8, 0.5),
    0 0 0 1px rgba(234, 179, 8, 0.4);
}

.glass-toggle:active .toggle-thumb {
  transform: scale(0.95);
}

.is-on.glass-toggle:active .toggle-thumb {
  transform: translateX(24px) scale(0.95);
}

@media (prefers-reduced-motion: reduce) {
  .toggle-track,
  .toggle-thumb {
    transition: none;
  }
}
</style>
