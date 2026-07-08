<template>
  <div
    ref="containerRef"
    class="carousel-container"
    :class="{ round: round }"
    :style="containerStyle"
    @mouseenter="onMouseEnter"
    @mouseleave="onMouseLeave"
  >
    <div
      ref="trackRef"
      class="carousel-track"
      :style="trackStyle"
      @pointerdown="onPointerDown"
      @pointermove="onPointerMove"
      @pointerup="onPointerUp"
      @pointercancel="onPointerUp"
    >
      <div
        v-for="(item, index) in itemsForRender"
        :key="`${item.id ?? index}-${index}`"
        class="carousel-item"
        :class="{ round: round }"
        :style="itemStyle(index)"
        @click="onItemClick(item, index)"
      >
        <div class="carousel-item-header" :class="{ round: round }">
          <span class="carousel-icon-container">
            <component :is="item.icon" v-if="item.icon" class="carousel-icon" />
          </span>
        </div>
        <div class="carousel-item-content">
          <div class="carousel-item-title">{{ item.title }}</div>
          <p class="carousel-item-description">{{ item.description }}</p>
        </div>
      </div>
    </div>

    <div class="carousel-indicators-container" :class="{ round: round }">
      <div class="carousel-indicators">
        <button
          v-for="(_, index) in items"
          :key="index"
          type="button"
          class="carousel-indicator"
          :class="activeIndex === index ? 'active' : 'inactive'"
          :aria-label="`Go to slide ${index + 1}`"
          :aria-current="activeIndex === index"
          @click="goTo(index)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted, onMounted, watch } from 'vue'

export interface CarouselItem {
  id?: number | string
  title: string
  description: string
  icon?: any
}

interface Props {
  items?: CarouselItem[]
  baseWidth?: number
  autoplay?: boolean
  autoplayDelay?: number
  pauseOnHover?: boolean
  loop?: boolean
  round?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  items: () => [],
  baseWidth: 1100,
  autoplay: false,
  autoplayDelay: 3000,
  pauseOnHover: false,
  loop: false,
  round: false,
})

const GAP = 16
const DRAG_BUFFER = 0
const VELOCITY_THRESHOLD = 500
const SPRING = { type: 'spring', stiffness: 300, damping: 30 }

const containerPadding = 16
const itemWidth = computed(() => props.baseWidth - containerPadding * 2)
const trackItemOffset = computed(() => itemWidth.value + GAP)

const itemsForRender = computed(() => {
  if (!props.loop) return props.items
  if (props.items.length === 0) return []
  return [props.items[props.items.length - 1], ...props.items, props.items[0]]
})

const position = ref(props.loop ? 1 : 0)
const x = ref(0)
const isHovered = ref(false)
const isJumping = ref(false)
const isAnimating = ref(false)
const isDragging = ref(false)
const dragStartX = ref(0)
const dragStartPosition = ref(0)
const lastDragX = ref(0)
const lastDragTime = ref(0)
const dragVelocity = ref(0)
const effectiveTransition = ref<any>(SPRING)

const containerRef = ref<HTMLDivElement | null>(null)
const trackRef = ref<HTMLDivElement | null>(null)

const containerStyle = computed(() => {
  const style: Record<string, string> = {
    width: `${props.baseWidth}px`,
  }
  if (props.round) {
    style.height = `${props.baseWidth}px`
    style.borderRadius = '50%'
  }
  return style
})

const trackStyle = computed(() => {
  const cur = x.value
  const offset = -(position.value * trackItemOffset.value)
  return {
    width: `${itemWidth.value}px`,
    gap: `${GAP}px`,
    transform: `translate3d(${cur + offset}px, 0, 0)`,
    transition: isJumping.value || isDragging.value ? 'none' : 'transform 0.4s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
    perspective: '1000px',
    perspectiveOrigin: `${position.value * trackItemOffset.value + itemWidth.value / 2}px 50%`,
  }
})

function itemStyle(index: number) {
  // 3D rotate based on position offset
  const offset = (index - position.value) * trackItemOffset.value
  let rotateY = 0
  if (offset > 0) {
    rotateY = Math.min(20, (offset / itemWidth.value) * 25)
  } else if (offset < 0) {
    rotateY = Math.max(-20, (offset / itemWidth.value) * 25)
  }

  const style: Record<string, string> = {
    width: `${itemWidth.value}px`,
    height: props.round ? `${itemWidth.value}px` : '100%',
    transform: `rotateY(${rotateY}deg)`,
  }
  if (props.round) {
    style.borderRadius = '50%'
  }
  return style
}

const activeIndex = computed(() => {
  if (props.items.length === 0) return 0
  if (props.loop) return (position.value - 1 + props.items.length) % props.items.length
  return Math.min(position.value, props.items.length - 1)
})

function goTo(idx: number) {
  const target = props.loop ? idx + 1 : idx
  position.value = target
}

function clamp(v: number, min: number, max: number) {
  return Math.max(min, Math.min(max, v))
}

function handleAnimationComplete() {
  if (!props.loop || itemsForRender.value.length <= 1) {
    isAnimating.value = false
    return
  }
  const lastCloneIndex = itemsForRender.value.length - 1
  if (position.value === lastCloneIndex) {
    isJumping.value = true
    position.value = 1
    x.value = 0
    requestAnimationFrame(() => {
      isJumping.value = false
      isAnimating.value = false
    })
    return
  }
  if (position.value === 0) {
    isJumping.value = true
    position.value = props.items.length
    x.value = 0
    requestAnimationFrame(() => {
      isJumping.value = false
      isAnimating.value = false
    })
    return
  }
  isAnimating.value = false
}

const emit = defineEmits<{
  (e: 'item-click', item: CarouselItem): void
}>()

function onItemClick(item: CarouselItem, index: number) {
  if (isDragging.value) return
  // 忽略 clone 的首尾项
  if (props.loop) {
    if (index === 0 || index === itemsForRender.value.length - 1) {
      goTo(props.items.length === 0 ? 0 : Math.max(0, props.items.length - 1))
      return
    }
  }
  emit('item-click', item)
}

function onMouseEnter() {
  isHovered.value = true
}

function onMouseLeave() {
  isHovered.value = false
  if (isDragging.value) {
    isDragging.value = false
    onPointerUp()
  }
}

function onPointerDown(e: PointerEvent) {
  if (isAnimating.value) return
  isDragging.value = true
  dragStartX.value = e.clientX
  dragStartPosition.value = x.value
  lastDragX.value = e.clientX
  lastDragTime.value = Date.now()
  dragVelocity.value = 0
  ;(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId)
}

function onPointerMove(e: PointerEvent) {
  if (!isDragging.value) return
  const dx = e.clientX - dragStartX.value
  x.value = dragStartPosition.value + dx

  const now = Date.now()
  const dt = now - lastDragTime.value
  if (dt > 0) {
    dragVelocity.value = (e.clientX - lastDragX.value) / dt * 1000
  }
  lastDragX.value = e.clientX
  lastDragTime.value = now
}

function onPointerUp(e?: PointerEvent) {
  if (!isDragging.value) return
  isDragging.value = false
  if (e) {
    try { (e.currentTarget as HTMLElement).releasePointerCapture(e.pointerId) } catch {}
  }

  const dx = x.value - dragStartPosition.value
  const velocity = dragVelocity.value

  let direction = 0
  if (dx < -DRAG_BUFFER || velocity < -VELOCITY_THRESHOLD) direction = 1
  else if (dx > DRAG_BUFFER || velocity > VELOCITY_THRESHOLD) direction = -1

  if (direction === 0) {
    x.value = 0
    return
  }

  const next = clamp(position.value + direction, 0, itemsForRender.value.length - 1)
  position.value = next
  x.value = 0
}

// Reset on items length change
watch(() => props.items.length, (newLen) => {
  if (newLen === 0) {
    position.value = 0
    return
  }
  const start = props.loop ? 1 : 0
  position.value = start
  x.value = 0
})

let autoplayTimer: number | null = null

function startAutoplay() {
  if (!props.autoplay || itemsForRender.value.length <= 1) return
  if (props.pauseOnHover && isHovered.value) return
  autoplayTimer = window.setInterval(() => {
    position.value = Math.min(position.value + 1, itemsForRender.value.length - 1)
  }, props.autoplayDelay)
}

function stopAutoplay() {
  if (autoplayTimer !== null) {
    clearInterval(autoplayTimer)
    autoplayTimer = null
  }
}

watch(() => [props.autoplay, props.autoplayDelay, isHovered.value, itemsForRender.value.length], () => {
  stopAutoplay()
  startAutoplay()
}, { immediate: false })

onMounted(() => {
  if (props.autoplay) startAutoplay()
})

onUnmounted(() => {
  stopAutoplay()
})

defineExpose({ goTo, handleAnimationComplete })
</script>

<style scoped>
.carousel-container {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 16px;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  --outer-r: 24px;
  --p-distance: 12px;
}

.carousel-container.round {
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.carousel-track {
  display: flex;
  cursor: grab;
  user-select: none;
  -webkit-user-select: none;
  touch-action: pan-y;
}

.carousel-track:active {
  cursor: grabbing;
}

.carousel-item {
  position: relative;
  display: flex;
  flex-shrink: 0;
  flex-direction: column;
  align-items: flex-start;
  justify-content: space-between;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: calc(var(--outer-r) - var(--p-distance));
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.01));
  overflow: hidden;
  cursor: grab;
  transition: border-color 0.3s ease, background 0.3s ease;
  transform-style: preserve-3d;
  will-change: transform;
}

.carousel-item:hover {
  border-color: rgba(6, 182, 212, 0.3);
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.06), rgba(6, 182, 212, 0.02));
}

.carousel-item.round {
  position: relative;
  bottom: 0.1em;
  border: 1px solid rgba(255, 255, 255, 0.12);
  justify-content: center;
  align-items: center;
  text-align: center;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.01));
}

.carousel-item-header.round {
  padding: 0;
  margin: 0;
}

.carousel-item-header {
  margin-bottom: 16px;
  padding: 20px;
  padding-top: 20px;
}

.carousel-icon-container {
  display: flex;
  height: 48px;
  width: 48px;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.2), rgba(6, 182, 212, 0.08));
  border: 1px solid rgba(6, 182, 212, 0.3);
  box-shadow: 0 0 20px rgba(6, 182, 212, 0.2);
}

.carousel-icon {
  height: 26px;
  width: 26px;
  color: #ffffff;
  filter: drop-shadow(0 0 4px rgba(6, 182, 212, 0.5));
}

.carousel-item-content {
  padding: 20px;
  padding-bottom: 20px;
}

.carousel-item-title {
  margin-bottom: 6px;
  font-weight: 700;
  font-size: 18px;
  color: #ffffff;
  letter-spacing: -0.01em;
}

.carousel-item-description {
  font-size: 13px;
  color: #a1a1aa;
  line-height: 1.6;
  margin: 0;
}

.carousel-indicators-container {
  display: flex;
  width: 100%;
  justify-content: center;
  margin-top: 12px;
}

.carousel-indicators-container.round {
  position: absolute;
  z-index: 2;
  bottom: 3em;
  left: 50%;
  transform: translateX(-50%);
}

.carousel-indicators {
  display: flex;
  gap: 8px;
  padding: 0 32px;
}

.carousel-indicator {
  height: 8px;
  width: 8px;
  border: none;
  padding: 0;
  appearance: none;
  border-radius: 50%;
  cursor: pointer;
  transition: all 250ms cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.carousel-indicator.active {
  background-color: #ffffff;
  transform: scale(1.3);
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.5);
}

.carousel-indicator.inactive {
  background-color: rgba(255, 255, 255, 0.25);
}

.carousel-indicator:hover {
  background-color: rgba(255, 255, 255, 0.6);
}

.carousel-indicator:focus-visible {
  outline: 2px solid #ffffff;
  outline-offset: 2px;
}
</style>
