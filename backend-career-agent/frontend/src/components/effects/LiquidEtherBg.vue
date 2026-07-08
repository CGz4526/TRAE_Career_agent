<template>
  <div ref="containerRef" class="liquid-ether-container" :style="{ mixBlendMode: 'screen', opacity: '0.85' }"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import * as THREE from 'three'

interface LiquidEtherProps {
  colors?: string[]
  mouseForce?: number
  cursorSize?: number
  resolution?: number
  autoDemo?: boolean
  autoSpeed?: number
  autoIntensity?: number
}

const props = withDefaults(defineProps<LiquidEtherProps>(), {
  colors: () => ['#5227FF', '#FF9FFC', '#B497CF'],
  mouseForce: 20,
  cursorSize: 100,
  resolution: 0.5,
  autoDemo: true,
  autoSpeed: 0.5,
  autoIntensity: 2.2,
})

const containerRef = ref<HTMLDivElement | null>(null)
let rafId: number | null = null
let renderer: THREE.WebGLRenderer | null = null
let scene: THREE.Scene | null = null
let camera: THREE.OrthographicCamera | null = null
let material: THREE.ShaderMaterial | null = null
let geometry: THREE.PlaneGeometry | null = null
let mesh: THREE.Mesh | null = null
let mouse = new THREE.Vector2(0, 0)
let targetMouse = new THREE.Vector2(0, 0)
let time = 0
let resizeObserver: ResizeObserver | null = null
let containerElement: HTMLDivElement | null = null

function makePaletteTexture(stops: string[]) {
  let arr = stops
  if (!Array.isArray(arr) || arr.length === 0) {
    arr = ['#ffffff', '#ffffff']
  }
  if (arr.length === 1) {
    arr = [arr[0], arr[0]]
  }
  const w = arr.length
  const data = new Uint8Array(w * 4)
  for (let i = 0; i < w; i++) {
    const c = new THREE.Color(arr[i])
    data[i * 4 + 0] = Math.round(c.r * 255)
    data[i * 4 + 1] = Math.round(c.g * 255)
    data[i * 4 + 2] = Math.round(c.b * 255)
    data[i * 4 + 3] = 255
  }
  const tex = new THREE.DataTexture(data, w, 1, THREE.RGBAFormat)
  tex.magFilter = THREE.LinearFilter
  tex.minFilter = THREE.LinearFilter
  tex.wrapS = THREE.ClampToEdgeWrapping
  tex.wrapT = THREE.ClampToEdgeWrapping
  tex.generateMipmaps = false
  tex.needsUpdate = true
  return tex
}

function init() {
  const container = containerRef.value
  if (!container) return
  containerElement = container

  const testCanvas = document.createElement('canvas')
  const gl = testCanvas.getContext('webgl') || testCanvas.getContext('experimental-webgl')
  if (!gl) {
    console.warn('[LiquidEther] WebGL not supported')
    return
  }

  const width = container.clientWidth
  const height = container.clientHeight

  scene = new THREE.Scene()
  camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1)

  renderer = new THREE.WebGLRenderer({
    antialias: false,
    alpha: true,
    powerPreference: 'high-performance',
    stencil: false,
    depth: false,
  })

  const dpr = Math.min(window.devicePixelRatio, 2) * props.resolution
  renderer.setSize(width, height)
  renderer.setPixelRatio(dpr)
  renderer.domElement.style.width = '100%'
  renderer.domElement.style.height = '100%'
  renderer.domElement.style.display = 'block'
  container.appendChild(renderer.domElement)

  const paletteTex = makePaletteTexture(props.colors)

  const vertexShader = /* glsl */ `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = vec4(position, 1.0);
    }
  `

  const fragmentShader = /* glsl */ `
    precision highp float;
    uniform float uTime;
    uniform vec2 uResolution;
    uniform vec2 uMouse;
    uniform float uMouseForce;
    uniform float uCursorSize;
    uniform sampler2D uPalette;
    uniform float uAutoDemo;
    uniform float uAutoSpeed;
    uniform float uAutoIntensity;
    varying vec2 vUv;

    float hash(vec2 p) {
      return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
    }

    float noise(vec2 p) {
      vec2 i = floor(p);
      vec2 f = fract(p);
      vec2 u = f * f * (3.0 - 2.0 * f);
      return mix(
        mix(hash(i + vec2(0.0, 0.0)), hash(i + vec2(1.0, 0.0)), u.x),
        mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x),
        u.y
      );
    }

    float fbm(vec2 p) {
      float v = 0.0;
      float a = 0.5;
      vec2 shift = vec2(100.0);
      mat2 rot = mat2(cos(0.5), sin(0.5), -sin(0.5), cos(0.5));
      for (int i = 0; i < 5; i++) {
        v += a * noise(p);
        p = rot * p * 2.0 + shift;
        a *= 0.5;
      }
      return v;
    }

    void main() {
      vec2 uv = vUv;
      vec2 aspect = vec2(uResolution.x / uResolution.y, 1.0);
      vec2 p = (uv - 0.5) * aspect * 3.0;

      float t = uTime * 0.3;

      // Auto demo circular motion
      vec2 autoCenter = vec2(0.0);
      if (uAutoDemo > 0.5) {
        float autoRadius = uAutoIntensity;
        autoCenter = vec2(
          cos(t * uAutoSpeed) * autoRadius,
          sin(t * uAutoSpeed * 0.7) * autoRadius * 0.6
        );
      }

      // Mouse influence
      vec2 mouseInfluence = uMouse * aspect * uMouseForce;
      vec2 center = autoCenter + mouseInfluence;

      // Distance field
      float dist = length(p - center);
      float cursor = 1.0 - smoothstep(0.0, uCursorSize / 100.0, dist);

      // Flow field
      float angle = atan(p.y - center.y, p.x - center.x);
      float flow = fbm(p * 0.5 + t + vec2(cos(angle), sin(angle)) * 0.3);

      // Color from palette
      float colorT = fract(flow + t * 0.1);
      vec4 col = texture2D(uPalette, vec2(colorT, 0.5));

      // Blend
      float brightness = cursor * 0.8 + flow * 0.4;
      brightness *= col.a;
      brightness = clamp(brightness, 0.0, 1.2);

      vec3 finalCol = col.rgb * brightness;
      finalCol = clamp(finalCol, 0.0, 1.0);

      gl_FragColor = vec4(finalCol, col.a);
    }
  `

  material = new THREE.ShaderMaterial({
    vertexShader,
    fragmentShader,
    uniforms: {
      uTime: { value: 0 },
      uResolution: { value: new THREE.Vector2(width, height) },
      uMouse: { value: mouse },
      uMouseForce: { value: props.mouseForce },
      uCursorSize: { value: props.cursorSize },
      uPalette: { value: paletteTex },
      uAutoDemo: { value: props.autoDemo ? 1.0 : 0.0 },
      uAutoSpeed: { value: props.autoSpeed },
      uAutoIntensity: { value: props.autoIntensity },
    },
    transparent: true,
    depthWrite: false,
    depthTest: false,
  })

  geometry = new THREE.PlaneGeometry(2, 2)
  mesh = new THREE.Mesh(geometry, material)
  scene.add(mesh)

  // Mouse handler
  function handleMouseMove(e: MouseEvent) {
    const rect = container!.getBoundingClientRect()
    targetMouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1
    targetMouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1
  }

  container.addEventListener('mousemove', handleMouseMove, { passive: true })

  // Resize
  resizeObserver = new ResizeObserver(() => {
    if (!renderer || !material || !containerElement) return
    const w = containerElement.clientWidth
    const h = containerElement.clientHeight
    renderer.setSize(w, h)
    material.uniforms.uResolution.value.set(w, h)
  })
  resizeObserver.observe(container)

  function animate() {
    rafId = requestAnimationFrame(animate)
    if (!material || !renderer || !scene || !camera) return

    time += 0.016

    // Smooth mouse follow
    mouse.x += (targetMouse.x - mouse.x) * 0.08
    mouse.y += (targetMouse.y - mouse.y) * 0.08

    material.uniforms.uTime.value = time
    material.uniforms.uMouse.value.copy(mouse)

    renderer.render(scene, camera)
  }

  rafId = requestAnimationFrame(animate)
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
  if (containerElement) {
    containerElement.removeEventListener('mousemove', () => {})
    if (renderer && renderer.domElement.parentNode === containerElement) {
      containerElement.removeChild(renderer.domElement)
    }
  }
  if (renderer) {
    renderer.dispose()
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

onMounted(() => {
  requestAnimationFrame(() => init())
})

onUnmounted(() => {
  cleanup()
})
</script>

<style scoped>
.liquid-ether-container {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
  background: transparent;
}
</style>
