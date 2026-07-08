import type { Directive } from 'vue'

/**
 * v-spotlight 指令：自动跟踪鼠标位置写入 --mx / --my CSS 变量
 * 配合 .fx-spotlight 类使用，实现卡片光斑跟随效果
 *
 * 用法：<div class="fx-spotlight" v-spotlight>...</div>
 */
const spotlight: Directive = {
  mounted(el: HTMLElement) {
    el.addEventListener('mousemove', (e: MouseEvent) => {
      const rect = el.getBoundingClientRect()
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top
      el.style.setProperty('--mx', `${x}px`)
      el.style.setProperty('--my', `${y}px`)
    })
  },
}

export default spotlight
