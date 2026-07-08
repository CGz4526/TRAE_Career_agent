<template>
  <div
    class="mega-bg-text"
    :class="[
      `position-${position}`,
      `size-${size}`,
      { 'is-stroke': stroke, 'has-blur': blur > 0 }
    ]"
    :style="containerStyle"
  >
    <span class="mega-text" :style="textStyle">
      <slot>{{ text }}</slot>
    </span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

/**
 * 超大号背景装饰文字组件
 * 灵感来自 Godly / Recent 网站 hero 区的巨大装饰文字
 * 低透明度，有渐变和描边效果，作为背景装饰使用
 */
interface Props {
  /** 显示的文字（英文大写效果最好） */
  text: string
  /** 文字位置 */
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'center'
  /** 文字大小 */
  size?: 'sm' | 'md' | 'lg' | 'xl'
  /** 透明度（0-1） */
  opacity?: number
  /** 旋转角度（deg） */
  rotate?: number
  /** 主颜色（支持 CSS 变量） */
  color?: string
  /** 是否只有描边（空心字） */
  stroke?: boolean
  /** 模糊值 px（加了有发光感） */
  blur?: number
  /** 字体（默认 heading 字体） */
  fontFamily?: string
  /** 字重（默认 900 超粗） */
  fontWeight?: number | string
}

const props = withDefaults(defineProps<Props>(), {
  position: 'center',
  size: 'lg',
  opacity: 0.06,
  rotate: -2,
  color: 'var(--bc-primary)',
  stroke: false,
  blur: 0,
  fontFamily: 'var(--bc-font-heading)',
  fontWeight: 900,
})

const containerStyle = computed(() => ({
  '--text-opacity': props.opacity,
  '--rotate-deg': `${props.rotate}deg`,
} as Record<string, string>))

const textStyle = computed(() => {
  const styles: Record<string, string> = {
    fontFamily: props.fontFamily,
    fontWeight: String(props.fontWeight),
    color: props.stroke ? 'transparent' : props.color,
  }

  if (props.stroke) {
    styles['-webkit-text-stroke'] = `2px ${props.color}`
    styles['text-stroke'] = `2px ${props.color}`
  }

  if (props.blur > 0) {
    styles.filter = `blur(${props.blur}px)`
  }

  return styles
})
</script>

<style scoped>
.mega-bg-text {
  position: absolute;
  pointer-events: none;
  z-index: 0;
  user-select: none;
  overflow: hidden;
  opacity: var(--text-opacity, 0.06);
  transform: rotate(var(--rotate-deg, -2deg));
  will-change: opacity;
}

.mega-text {
  display: block;
  white-space: nowrap;
  line-height: 1;
  letter-spacing: -0.02em;
  text-transform: uppercase;
  background: linear-gradient(
    135deg,
    currentColor 0%,
    rgba(255, 255, 255, 0.8) 50%,
    currentColor 100%
  );
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  animation: mega-float 8s ease-in-out infinite;
  will-change: transform, opacity;
}

.is-stroke .mega-text {
  background: none;
  -webkit-background-clip: initial;
  background-clip: initial;
  -webkit-text-fill-color: initial;
}

/* 位置 */
.position-top-left {
  top: -2%;
  left: -2%;
}
.position-top-right {
  top: -2%;
  right: -2%;
}
.position-bottom-left {
  bottom: -2%;
  left: -2%;
}
.position-bottom-right {
  bottom: -2%;
  right: -2%;
}
.position-center {
  top: 50%;
  left: 50%;
  translate: -50% -50%;
}

/* 大小 */
.size-sm .mega-text {
  font-size: 80px;
}
.size-md .mega-text {
  font-size: 120px;
}
.size-lg .mega-text {
  font-size: 180px;
}
.size-xl .mega-text {
  font-size: 260px;
}

/* 漂浮动画 */
@keyframes mega-float {
  0%,
  100% {
    transform: translateY(0);
    opacity: 1;
  }
  50% {
    transform: translateY(-12px);
    opacity: 0.7;
  }
}

/* 响应式 */
@media (max-width: 1024px) {
  .size-sm .mega-text {
    font-size: 56px;
  }
  .size-md .mega-text {
    font-size: 80px;
  }
  .size-lg .mega-text {
    font-size: 120px;
  }
  .size-xl .mega-text {
    font-size: 160px;
  }
}

@media (max-width: 640px) {
  .size-sm .mega-text {
    font-size: 36px;
  }
  .size-md .mega-text {
    font-size: 52px;
  }
  .size-lg .mega-text {
    font-size: 72px;
  }
  .size-xl .mega-text {
    font-size: 96px;
  }
}

/* 无障碍：减少动画 */
@media (prefers-reduced-motion: reduce) {
  .mega-bg-text {
    animation: none;
  }
}
</style>
