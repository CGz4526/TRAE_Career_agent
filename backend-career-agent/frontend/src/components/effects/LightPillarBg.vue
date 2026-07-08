<template>
  <div ref="containerRef" class="light-pillar-container" :style="{ mixBlendMode: mixBlendMode }"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as THREE from 'three'

interface LightPillarProps {
  topColor?: string
  bottomColor?: string
  intensity?: number
  rotationSpeed?: number
  interactive?: boolean
  glowAmount?: number
  pillarWidth?: number
  pillarHeight?: number
  noiseIntensity?: number
  mixBlendMode?: string
  pillarRotation?: number
  quality?: 'low' | 'medium' | 'high'
}

const props = withDefaults(defineProps<LightPillarProps>(), {
  topColor: '#ffffff',
  bottomColor: '#a1a1aa',
  intensity: 1.0,
  rotationSpeed: 0.3,
  interactive: false,
  glowAmount: 0.005,
  pillarWidth: 3.0,
  pillarHeight: 0.4,
  noiseIntensity: 0.5,
  mixBlendMode: 'screen',
  pillarRotation: 0,
  quality: 'high',
})

const containerRef = ref<HTMLDivElement | null>(null)
let rafId: number | null = null
let renderer: THREE.WebGLRenderer | null = null
let material: THREE.ShaderMaterial | null = null
let scene: THREE.Scene | null = null
let camera: THREE.OrthographicCamera | null = null
let geometry: THREE.PlaneGeometry | null = null
let mesh: THREE.Mesh | null = null
let mouse = new THREE.Vector2(0, 0)
let time = 0
let rotationSpeed = props.rotationSpeed
let resizeTimeout: number | null = null
let mouseMoveTimeout: number | null = null
let containerElement: HTMLDivElement | null = null
let mouseHandler: ((e: MouseEvent) => void) | null = null
let resizeHandler: (() => void) | null = null

function parseColor(hex: string): THREE.Vector3 {
  const color = new THREE.Color(hex)
  return new THREE.Vector3(color.r, color.g, color.b)
}

function init() {
  const container = containerRef.value
  if (!container) {
    console.warn('[LightPillar] container not found')
    return
  }
  containerElement = container

  // WebGL support check
  const testCanvas = document.createElement('canvas')
  const gl = testCanvas.getContext('webgl') || testCanvas.getContext('experimental-webgl')
  if (!gl) {
    console.warn('[LightPillar] WebGL not supported')
    return
  }

  const width = container.clientWidth
  const height = container.clientHeight

  scene = new THREE.Scene()
  camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1)

  // Quality settings
  const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
  const isLowEnd = isMobile || (navigator.hardwareConcurrency && navigator.hardwareConcurrency <= 4)
  let effectiveQuality = props.quality
  if (isLowEnd && props.quality === 'high') effectiveQuality = 'medium'
  if (isMobile && props.quality !== 'low') effectiveQuality = 'low'

  const qualitySettings: Record<string, {
    iterations: number
    waveIterations: number
    pixelRatio: number
    precision: string
    stepMultiplier: number
  }> = {
    low: { iterations: 24, waveIterations: 1, pixelRatio: 0.5, precision: 'mediump', stepMultiplier: 1.5 },
    medium: { iterations: 40, waveIterations: 2, pixelRatio: 0.65, precision: 'mediump', stepMultiplier: 1.2 },
    high: {
      iterations: 80,
      waveIterations: 4,
      pixelRatio: Math.min(window.devicePixelRatio, 2),
      precision: 'highp',
      stepMultiplier: 1.0,
    },
  }

  const settings = qualitySettings[effectiveQuality] || qualitySettings.medium

  try {
    renderer = new THREE.WebGLRenderer({
      antialias: false,
      alpha: true,
      powerPreference: effectiveQuality === 'high' ? 'high-performance' : 'low-power',
      stencil: false,
      depth: false,
    })
  } catch (e) {
    console.error('[LightPillar] WebGLRenderer init failed', e)
    return
  }

  renderer.setSize(width, height)
  renderer.setPixelRatio(settings.pixelRatio)
  renderer.domElement.style.width = '100%'
  renderer.domElement.style.height = '100%'
  renderer.domElement.style.display = 'block'
  container.appendChild(renderer.domElement)

  const vertexShader = /* glsl */ `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = vec4(position, 1.0);
    }
  `

  const pillarRotRad = (props.pillarRotation * Math.PI) / 180
  const waveSin = Math.sin(0.4)
  const waveCos = Math.cos(0.4)

  const fragmentShader = /* glsl */ `
    precision ${settings.precision} float;
    uniform float uTime;
    uniform vec2 uResolution;
    uniform vec2 uMouse;
    uniform vec3 uTopColor;
    uniform vec3 uBottomColor;
    uniform float uIntensity;
    uniform bool uInteractive;
    uniform float uGlowAmount;
    uniform float uPillarWidth;
    uniform float uPillarHeight;
    uniform float uNoiseIntensity;
    uniform float uRotCos;
    uniform float uRotSin;
    uniform float uPillarRotCos;
    uniform float uPillarRotSin;
    uniform float uWaveSin;
    uniform float uWaveCos;
    varying vec2 vUv;
    const float STEP_MULT = ${settings.stepMultiplier.toFixed(1)};
    const int MAX_ITER = ${settings.iterations};
    const int WAVE_ITER = ${settings.waveIterations};
    void main() {
      vec2 uv = (vUv * 2.0 - 1.0) * vec2(uResolution.x / uResolution.y, 1.0);
      uv = vec2(uPillarRotCos * uv.x - uPillarRotSin * uv.y, uPillarRotSin * uv.x + uPillarRotCos * uv.y);
      vec3 ro = vec3(0.0, 0.0, -10.0);
      vec3 rd = normalize(vec3(uv, 1.0));
      float rotC = uRotCos;
      float rotS = uRotSin;
      if(uInteractive && (uMouse.x != 0.0 || uMouse.y != 0.0)) {
        float a = uMouse.x * 6.283185;
        rotC = cos(a);
        rotS = sin(a);
      }
      vec3 col = vec3(0.0);
      float t = 0.1;

      for(int i = 0; i < MAX_ITER; i++) {
        vec3 p = ro + rd * t;
        p.xz = vec2(rotC * p.x - rotS * p.z, rotS * p.x + rotC * p.z);
        vec3 q = p;
        q.y = p.y * uPillarHeight + uTime;

        float freq = 1.0;
        float amp = 1.0;
        for(int j = 0; j < WAVE_ITER; j++) {
          q.xz = vec2(uWaveCos * q.x - uWaveSin * q.z, uWaveSin * q.x + uWaveCos * q.z);
          q += cos(q.zxy * freq - uTime * float(j) * 2.0) * amp;
          freq *= 2.0;
          amp *= 0.5;
        }

        float d = length(cos(q.xz)) - 0.2;
        float bound = length(p.xz) - uPillarWidth;
        float k = 4.0;
        float h = max(k - abs(d - bound), 0.0);
        d = max(d, bound) + h * h * 0.0625 / k;
        d = abs(d) * 0.15 + 0.01;
        float grad = clamp((15.0 - p.y) / 30.0, 0.0, 1.0);
        col += mix(uBottomColor, uTopColor, grad) / d;
        t += d * STEP_MULT;
        if(t > 50.0) break;
      }
      float widthNorm = uPillarWidth / 3.0;
      col = tanh(col * uGlowAmount / widthNorm);

      col -= fract(sin(dot(gl_FragCoord.xy, vec2(12.9898, 78.233))) * 43758.5453) / 15.0 * uNoiseIntensity;

      gl_FragColor = vec4(col * uIntensity, 1.0);
    }
  `

  material = new THREE.ShaderMaterial({
    vertexShader,
    fragmentShader,
    uniforms: {
      uTime: { value: 0 },
      uResolution: { value: new THREE.Vector2(width, height) },
      uMouse: { value: mouse },
      uTopColor: { value: parseColor(props.topColor) },
      uBottomColor: { value: parseColor(props.bottomColor) },
      uIntensity: { value: props.intensity },
      uInteractive: { value: props.interactive },
      uGlowAmount: { value: props.glowAmount },
      uPillarWidth: { value: props.pillarWidth },
      uPillarHeight: { value: props.pillarHeight },
      uNoiseIntensity: { value: props.noiseIntensity },
      uRotCos: { value: 1.0 },
      uRotSin: { value: 0.0 },
      uPillarRotCos: { value: Math.cos(pillarRotRad) },
      uPillarRotSin: { value: Math.sin(pillarRotRad) },
      uWaveSin: { value: waveSin },
      uWaveCos: { value: waveCos },
    },
    transparent: true,
    depthWrite: false,
    depthTest: false,
  })

  geometry = new THREE.PlaneGeometry(2, 2)
  mesh = new THREE.Mesh(geometry, material)
  scene.add(mesh)

  // Mouse handler
  mouseHandler = (event: MouseEvent) => {
    if (!props.interactive) return
    if (mouseMoveTimeout) return
    mouseMoveTimeout = window.setTimeout(() => {
      mouseMoveTimeout = null
    }, 16)
    const rect = container.getBoundingClientRect()
    const x = ((event.clientX - rect.left) / rect.width) * 2 - 1
    const y = -((event.clientY - rect.top) / rect.height) * 2 + 1
    mouse.set(x, y)
  }

  if (props.interactive) {
    container.addEventListener('mousemove', mouseHandler, { passive: true })
  }

  // Resize handler
  resizeHandler = () => {
    if (resizeTimeout) clearTimeout(resizeTimeout)
    resizeTimeout = window.setTimeout(() => {
      if (!renderer || !material || !containerElement) return
      const newWidth = containerElement.clientWidth
      const newHeight = containerElement.clientHeight
      renderer.setSize(newWidth, newHeight)
      material.uniforms.uResolution.value.set(newWidth, newHeight)
    }, 150)
  }

  window.addEventListener('resize', resizeHandler, { passive: true })

  // Animation loop
  const targetFPS = effectiveQuality === 'low' ? 30 : 60
  const frameTime = 1000 / targetFPS
  let lastTime = performance.now()

  function animate(currentTime: number) {
    if (!material || !renderer || !scene || !camera) return

    const deltaTime = currentTime - lastTime
    if (deltaTime >= frameTime) {
      time += 0.016 * rotationSpeed
      const t = time
      material.uniforms.uTime.value = t
      material.uniforms.uRotCos.value = Math.cos(t * 0.3)
      material.uniforms.uRotSin.value = Math.sin(t * 0.3)
      renderer.render(scene, camera)
      lastTime = currentTime - (deltaTime % frameTime)
    }
    rafId = requestAnimationFrame(animate)
  }

  rafId = requestAnimationFrame(animate)
}

function cleanup() {
  if (rafId !== null) {
    cancelAnimationFrame(rafId)
    rafId = null
  }
  if (resizeTimeout !== null) {
    clearTimeout(resizeTimeout)
    resizeTimeout = null
  }
  if (mouseMoveTimeout !== null) {
    clearTimeout(mouseMoveTimeout)
    mouseMoveTimeout = null
  }
  if (mouseHandler && containerElement && props.interactive) {
    containerElement.removeEventListener('mousemove', mouseHandler)
    mouseHandler = null
  }
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler)
    resizeHandler = null
  }

  if (renderer) {
    renderer.dispose()
    renderer.forceContextLoss()
    if (containerElement && renderer.domElement.parentNode === containerElement) {
      containerElement.removeChild(renderer.domElement)
    }
    renderer = null
  }
  if (material) {
    material.dispose()
    material = null
  }
  if (geometry) {
    geometry.dispose()
    geometry = null
  }
  scene = null
  camera = null
  mesh = null
  containerElement = null
}

// Watch prop changes
watch(() => props.rotationSpeed, (v) => { rotationSpeed = v })
watch(() => props.topColor, (v) => {
  if (material) material.uniforms.uTopColor.value = parseColor(v)
})
watch(() => props.bottomColor, (v) => {
  if (material) material.uniforms.uBottomColor.value = parseColor(v)
})
watch(() => props.intensity, (v) => {
  if (material) material.uniforms.uIntensity.value = v
})
watch(() => props.interactive, (v) => {
  if (material) material.uniforms.uInteractive.value = v
})
watch(() => props.glowAmount, (v) => {
  if (material) material.uniforms.uGlowAmount.value = v
})
watch(() => props.pillarWidth, (v) => {
  if (material) material.uniforms.uPillarWidth.value = v
})
watch(() => props.pillarHeight, (v) => {
  if (material) material.uniforms.uPillarHeight.value = v
})
watch(() => props.noiseIntensity, (v) => {
  if (material) material.uniforms.uNoiseIntensity.value = v
})
watch(() => props.pillarRotation, (v) => {
  if (!material) return
  const rad = (v * Math.PI) / 180
  material.uniforms.uPillarRotCos.value = Math.cos(rad)
  material.uniforms.uPillarRotSin.value = Math.sin(rad)
})

onMounted(() => {
  requestAnimationFrame(() => init())
})

onUnmounted(() => {
  cleanup()
})
</script>

<style scoped>
.light-pillar-container {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  background: transparent;
}
</style>
