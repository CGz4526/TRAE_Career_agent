<template>
  <div ref="containerRef" class="ferrofluid-container"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { Renderer, Program, Mesh, Triangle } from 'ogl'

interface FerrofluidProps {
  colors?: string[]
  speed?: number
  scale?: number
  turbulence?: number
  fluidity?: number
  rimWidth?: number
  sharpness?: number
  shimmer?: number
  glow?: number
  flowDirection?: 'up' | 'down' | 'left' | 'right'
  opacity?: number
  mouseInteraction?: boolean
  mouseStrength?: number
  mouseRadius?: number
  mouseDampening?: number
}

const props = withDefaults(defineProps<FerrofluidProps>(), {
  colors: () => ['#ffffff', '#a1a1aa', '#71717a'],
  speed: 0.5,
  scale: 1.6,
  turbulence: 1,
  fluidity: 0.1,
  rimWidth: 0.2,
  sharpness: 2.5,
  shimmer: 1.5,
  glow: 2,
  flowDirection: 'down',
  opacity: 1,
  mouseInteraction: true,
  mouseStrength: 1,
  mouseRadius: 0.35,
  mouseDampening: 0.15,
})

const containerRef = ref<HTMLDivElement | null>(null)
let rafId: number | null = null
let program: Program | null = null
let geometry: Triangle | null = null
let mesh: Mesh | null = null
let renderer: Renderer | null = null
let mouseTarget: [number, number] = [0, 0]
let lastTime = 0
let resizeObserver: ResizeObserver | null = null
let containerElement: HTMLDivElement | null = null
let pointerHandler: ((e: PointerEvent) => void) | null = null

const MAX_COLORS = 8

function hexToRGB(hex: string): [number, number, number] {
  const c = hex.replace('#', '').padEnd(6, '0')
  const r = parseInt(c.slice(0, 2), 16) / 255
  const g = parseInt(c.slice(2, 4), 16) / 255
  const b = parseInt(c.slice(4, 6), 16) / 255
  return [r, g, b]
}

function prepColors(input: string[]) {
  const base = (input && input.length ? input : ['#ffffff', '#a1a1aa', '#71717a']).slice(0, MAX_COLORS)
  const count = base.length
  const arr: [number, number, number][] = []
  for (let i = 0; i < MAX_COLORS; i++) {
    arr.push(hexToRGB(base[Math.min(i, base.length - 1)]))
  }
  const avg = [0, 0, 0]
  for (let i = 0; i < count; i++) {
    avg[0] += arr[i][0]
    avg[1] += arr[i][1]
    avg[2] += arr[i][2]
  }
  avg[0] /= count
  avg[1] /= count
  avg[2] /= count
  return { arr, count, avg }
}

function flowVec(d: string): [number, number] {
  switch (d) {
    case 'up': return [0, 1]
    case 'down': return [0, -1]
    case 'left': return [-1, 0]
    case 'right': return [1, 0]
    default: return [0, -1]
  }
}

// WebGL 2 / GLSL ES 3.0 语法
const vertex = /* glsl */ `
in vec2 position;
in vec2 uv;
out vec2 vUv;
void main() {
  vUv = uv;
  gl_Position = vec4(position, 0.0, 1.0);
}
`

const fragment = /* glsl */ `
precision highp float;
uniform vec3  iResolution;
uniform vec2  iMouse;
uniform float iTime;
uniform vec3  uColor0;
uniform vec3  uColor1;
uniform vec3  uColor2;
uniform vec3  uColor3;
uniform vec3  uColor4;
uniform vec3  uColor5;
uniform vec3  uColor6;
uniform vec3  uColor7;
uniform int   uColorCount;
uniform vec3  uMouseColor;
uniform vec2  uFlow;
uniform float uSpeed;
uniform float uScale;
uniform float uTurbulence;
uniform float uFluidity;
uniform float uRimWidth;
uniform float uSharpness;
uniform float uShimmer;
uniform float uGlow;
uniform float uOpacity;
uniform float uMouseEnabled;
uniform float uMouseStrength;
uniform float uMouseRadius;
in vec2 vUv;
out vec4 fragColor;
#define PI 3.14159265
vec3 palette(float h) {
  int count = uColorCount;
  if (count < 1) count = 1;
  int idx = int(floor(clamp(h, 0.0, 0.999999) * float(count)));
  if (idx <= 0) return uColor0;
  if (idx == 1) return uColor1;
  if (idx == 2) return uColor2;
  if (idx == 3) return uColor3;
  if (idx == 4) return uColor4;
  if (idx == 5) return uColor5;
  if (idx == 6) return uColor6;
  return uColor7;
}
float hash(vec3 p3) {
  p3 = fract(p3 * 0.1031);
  p3 += dot(p3, p3.zyx + 33.33);
  return fract((p3.x + p3.y) * p3.z);
}
float smin(float a, float b, float k) {
  float r = exp2(-a / k) + exp2(-b / k);
  return -k * log2(r);
}
float sinlerp(float a, float b, float w) {
  return mix(a, b, (sin(w * PI - PI / 2.0) + 1.0) / 2.0);
}
float vn(vec2 p, float s, float seed) {
  vec2 cellp = floor(p / s);
  vec2 relp = mod(p, s);
  float g1 = hash(vec3(cellp, seed));
  float g2 = hash(vec3(cellp.x + 1.0, cellp.y, seed));
  float g3 = hash(vec3(cellp.x + 1.0, cellp.y + 1.0, seed));
  float g4 = hash(vec3(cellp.x, cellp.y + 1.0, seed));
  float bx = sinlerp(g1, g2, relp.x / s);
  float tx = sinlerp(g4, g3, relp.x / s);
  return sinlerp(bx, tx, relp.y / s);
}
float dbn(vec2 p, float s, float seed) {
  float o = s / 2.0;
  float n0 = vn(p, s, seed);
  float n1 = vn(p + vec2(o, o), s, seed + 0.1);
  float n2 = vn(p + vec2(-o, o), s, seed + 0.2);
  float n3 = vn(p + vec2(o, -o), s, seed + 0.3);
  float n4 = vn(p + vec2(-o, -o), s, seed + 0.4);
  return (2.0 * n0 + 1.5 * n1 + 1.25 * n2 + 1.125 * n3 + n4) / 7.0;
}
void mainImage(out vec4 fc, in vec2 fragCoord) {
  float ref = 700.0 / max(uScale, 0.05);
  vec2 p = fragCoord / iResolution.y * ref;
  float spd = 200.0 * uSpeed;
  float t = iTime;
  vec2 dir = uFlow;
  vec2 perp = vec2(-dir.y, dir.x);
  float distort1 = vn(p + perp * (t * spd), 60.0, 10.0) * 50.0 * uTurbulence;
  float distort2 = vn(p - perp * (t * spd), 120.0, 15.0) * 100.0 * uTurbulence;
  float peaks = dbn(p + distort1 + dir * (t * spd * 0.5), 40.0, 1.0);
  float peaks2 = dbn(p + distort2 - dir * (t * spd * 0.5), 40.0, 0.0);
  float mapeaks = smin(peaks, peaks2, max(uFluidity, 0.001));
  float mGlow = 0.0;
  if (uMouseEnabled > 0.5) {
    vec2 mp = iMouse / iResolution.y * ref;
    float md = length(p - mp) / ref;
    float rr = max(uMouseRadius, 0.02);
    mGlow = exp(-md * md / (rr * rr)) * uMouseStrength;
  }
  float band = (uRimWidth - abs((mapeaks - 0.4) * 2.0)) * 5.0;
  float ltn = clamp(band - vn(p + dir * (t * spd * 0.5), 60.0, 12.0) * uShimmer, 0.0, 1.0);
  ltn = pow(ltn, uSharpness) * uGlow;
  ltn *= clamp(1.0 - mGlow, 0.0, 1.0);
  float h = clamp(0.5 + (peaks - peaks2) * 0.8, 0.0, 1.0);
  vec3 col = palette(h);
  vec3 outc = col * ltn;
  float a = clamp(max(outc.r, max(outc.g, outc.b)), 0.0, 1.0);
  fc = vec4(outc, a * uOpacity);
}
void main() {
  vec4 color;
  mainImage(color, vUv * iResolution.xy);
  fragColor = color;
}
`

function initWebGL() {
  const container = containerRef.value
  if (!container) {
    console.warn('[FerrofluidBg] container not found')
    return
  }
  containerElement = container

  try {
    renderer = new Renderer({
      dpr: window.devicePixelRatio || 1,
      alpha: true,
      antialias: true,
    })
  } catch (e) {
    console.error('[FerrofluidBg] Renderer init failed', e)
    return
  }

  const gl = renderer.gl
  gl.clearColor(0, 0, 0, 0)

  const canvas = gl.canvas
  canvas.style.width = '100%'
  canvas.style.height = '100%'
  canvas.style.display = 'block'
  canvas.style.position = 'absolute'
  canvas.style.inset = '0'
  container.appendChild(canvas)

  const { arr, count, avg } = prepColors(props.colors)

  const uniforms = {
    iResolution: { value: [gl.drawingBufferWidth, gl.drawingBufferHeight, 1] },
    iMouse: { value: [0, 0] },
    iTime: { value: 0 },
    uColor0: { value: arr[0] },
    uColor1: { value: arr[1] },
    uColor2: { value: arr[2] },
    uColor3: { value: arr[3] },
    uColor4: { value: arr[4] },
    uColor5: { value: arr[5] },
    uColor6: { value: arr[6] },
    uColor7: { value: arr[7] },
    uColorCount: { value: count },
    uMouseColor: { value: avg },
    uFlow: { value: flowVec(props.flowDirection) },
    uSpeed: { value: props.speed },
    uScale: { value: props.scale },
    uTurbulence: { value: props.turbulence },
    uFluidity: { value: props.fluidity },
    uRimWidth: { value: props.rimWidth },
    uSharpness: { value: props.sharpness },
    uShimmer: { value: props.shimmer },
    uGlow: { value: props.glow },
    uOpacity: { value: props.opacity },
    uMouseEnabled: { value: props.mouseInteraction ? 1 : 0 },
    uMouseStrength: { value: props.mouseStrength },
    uMouseRadius: { value: props.mouseRadius },
  }

  try {
    program = new Program(gl, { vertex, fragment, uniforms })
    geometry = new Triangle(gl)
    mesh = new Mesh(gl, { geometry, program })
  } catch (e) {
    console.error('[FerrofluidBg] Program/Mesh init failed', e)
    return
  }

  function resize() {
    if (!container || !renderer || !program) return
    const rect = container.getBoundingClientRect()
    if (rect.width === 0 || rect.height === 0) return
    renderer.setSize(rect.width, rect.height)
    program.uniforms.iResolution.value = [gl.drawingBufferWidth, gl.drawingBufferHeight, 1]
  }

  // 立即调用一次 resize
  resize()

  resizeObserver = new ResizeObserver(resize)
  resizeObserver.observe(container)

  pointerHandler = (e: PointerEvent) => {
    if (!renderer || !program) return
    const rect = (renderer.gl.canvas as HTMLCanvasElement).getBoundingClientRect()
    const sc = renderer.dpr || 1
    const x = (e.clientX - rect.left) * sc
    const y = (rect.height - (e.clientY - rect.top)) * sc
    mouseTarget = [x, y]
    if (props.mouseDampening <= 0) {
      ;(program.uniforms.iMouse.value as [number, number])[0] = x
      ;(program.uniforms.iMouse.value as [number, number])[1] = y
    }
  }

  if (props.mouseInteraction) {
    window.addEventListener('pointermove', pointerHandler)
  }

  function loop(t: number) {
    rafId = requestAnimationFrame(loop)
    if (!program || !mesh || !renderer) return

    program.uniforms.iTime.value = t * 0.001

    if (props.mouseDampening > 0) {
      if (!lastTime) lastTime = t
      const dt = (t - lastTime) / 1000
      lastTime = t
      const tau = Math.max(1e-4, props.mouseDampening)
      const factor = Math.min(1, 1 - Math.exp(-dt / tau))
      const cur = program.uniforms.iMouse.value as [number, number]
      cur[0] += (mouseTarget[0] - cur[0]) * factor
      cur[1] += (mouseTarget[1] - cur[1]) * factor
    }

    try {
      renderer.render({ scene: mesh })
    } catch (e) {
      console.error('[FerrofluidBg] render error', e)
    }
  }

  rafId = requestAnimationFrame(loop)
}

function cleanup() {
  if (rafId !== null) {
    cancelAnimationFrame(rafId)
    rafId = null
  }
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
  if (pointerHandler) {
    window.removeEventListener('pointermove', pointerHandler)
    pointerHandler = null
  }

  if (containerElement && renderer?.gl.canvas.parentElement === containerElement) {
    containerElement.removeChild(renderer.gl.canvas)
  }

  if (program) {
    ;(program as any).remove?.()
    program = null
  }
  if (geometry) {
    ;(geometry as any).remove?.()
    geometry = null
  }
  if (mesh) {
    ;(mesh as any).remove?.()
    mesh = null
  }
  if (renderer) {
    ;(renderer as any).destroy?.()
    renderer = null
  }
}

onMounted(() => {
  // 延迟一帧确保 DOM 已渲染
  requestAnimationFrame(() => {
    initWebGL()
  })
})

onUnmounted(() => {
  cleanup()
})
</script>

<style scoped>
.ferrofluid-container {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
  background: #000000;
}
</style>
