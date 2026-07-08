<template>
  <div class="landing-page">
    <div class="bg-black"></div>
    <LiquidEtherBg
      :colors="['#2a1a6b', '#8b5cf6', '#c4b5fd', '#f0abfc']"
      :mouse-force="15"
      :cursor-size="80"
      :resolution="0.5"
      :auto-demo="true"
      :auto-speed="0.3"
      :auto-intensity="1.5"
    />
    <div class="bg-vignette"></div>
    <div class="bg-noise"></div>

    <div class="landing-content">
      <div class="hero-section">
        <div class="hero-badge">
          <span class="badge-dot"></span>
          <span>AI-Powered Career Assistant</span>
        </div>

        <h1 class="hero-title">
          <TrueFocus
            sentence="CAREER AGENT"
            :blur-amount="4"
            border-color="#ffffff"
            glow-color="rgba(255, 255, 255, 0.7)"
            :animation-duration="0.6"
            :pause-between-animations="1.2"
          />
        </h1>

        <p class="hero-subtitle">
          面向后端工程师的一站式 AI 求职辅助平台
        </p>

        <p class="hero-desc">
          岗位解析 · 项目分析 · 智能题库 · 模拟面试
        </p>
      </div>

      <div class="cta-section">
        <button class="cta-btn primary" @click="handleLogin">
          <span>开始探索</span>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
        </button>

        <button class="cta-btn secondary" @click="handleGuest">
          <span>游客模式</span>
        </button>
      </div>

      <div class="features-preview">
        <div class="feature-item" v-for="(feature, i) in features" :key="i">
          <div class="feature-icon">
            <component :is="feature.icon" class="feature-svg" />
          </div>
          <span class="feature-label">{{ feature.label }}</span>
        </div>
      </div>
    </div>

    <div class="scroll-indicator">
      <span>Scroll</span>
      <div class="scroll-line"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import LiquidEtherBg from '@/components/effects/LiquidEtherBg.vue'
import TrueFocus from '@/components/effects/TrueFocus.vue'
import JobIcon from '@/components/icons/JobIcon.vue'
import ResumeIcon from '@/components/icons/ResumeIcon.vue'
import QuestionIcon from '@/components/icons/QuestionIcon.vue'
import InterviewIcon from '@/components/icons/InterviewIcon.vue'

const router = useRouter()

const features = [
  { label: '岗位画像解析', icon: JobIcon },
  { label: '简历智能优化', icon: ResumeIcon },
  { label: '题库自适应生成', icon: QuestionIcon },
  { label: 'AI 模拟面试', icon: InterviewIcon },
]

function handleLogin() {
  localStorage.removeItem('career-agent-guest')
  router.push('/login')
}

function handleGuest() {
  localStorage.removeItem('career-agent-token')
  localStorage.removeItem('career-agent-user')
  localStorage.setItem('career-agent-guest', 'true')
  router.push('/dashboard')
}
</script>

<style scoped>
.landing-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.bg-black {
  position: absolute;
  inset: 0;
  background: #000000;
  z-index: -2;
}

.bg-vignette {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: -1;
  background:
    radial-gradient(ellipse at 50% 30%, transparent 0%, rgba(0,0,0,0.5) 60%, rgba(0,0,0,0.85) 100%),
    radial-gradient(ellipse at 0% 50%, transparent 0%, rgba(0,0,0,0.3) 50%),
    radial-gradient(ellipse at 100% 50%, transparent 0%, rgba(0,0,0,0.3) 50%);
}

.bg-noise {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: -1;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  opacity: 0.035;
  mix-blend-mode: overlay;
}

.landing-content {
  position: relative;
  z-index: 10;
  text-align: center;
  padding: 40px 20px;
  max-width: 900px;
}

.hero-section {
  margin-bottom: 60px;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 100px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  letter-spacing: 0.5px;
  margin-bottom: 32px;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.badge-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #ffffff;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.6);
  animation: pulse-dot 2s ease-in-out infinite;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.2); }
}

.hero-title {
  font-size: clamp(48px, 12vw, 120px);
  font-weight: 800;
  letter-spacing: -0.04em;
  margin: 0 0 24px 0;
  line-height: 1;
}

.hero-subtitle {
  font-size: clamp(18px, 3vw, 28px);
  color: #fafafa;
  margin: 0 0 12px 0;
  font-weight: 500;
  letter-spacing: -0.01em;
}

.hero-desc {
  font-size: clamp(14px, 2vw, 18px);
  color: #71717a;
  margin: 0;
  letter-spacing: 0.5px;
}

.cta-section {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-bottom: 80px;
}

.cta-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 28px;
  font-size: 15px;
  font-weight: 600;
  border-radius: 12px;
  border: none;
  cursor: pointer;
  transition: all 0.3s ease;
  letter-spacing: 0.3px;
  font-family: inherit;
}

.cta-btn.primary {
  background: #fafafa;
  color: #09090b;
  box-shadow: 0 0 30px rgba(250, 250, 250, 0.2);
}

.cta-btn.primary:hover {
  background: #ffffff;
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(250, 250, 250, 0.3);
}

.cta-btn.secondary {
  background: rgba(255, 255, 255, 0.05);
  color: #fafafa;
  border: 1px solid rgba(255, 255, 255, 0.12);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.cta-btn.secondary:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.22);
}

.features-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 48px;
  flex-wrap: wrap;
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  transition: transform 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-4px);
}

.feature-icon {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  color: #ffffff;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.feature-item:hover .feature-icon {
  background: rgba(6, 182, 212, 0.12);
  border-color: rgba(6, 182, 212, 0.3);
  box-shadow: 0 0 25px rgba(6, 182, 212, 0.2);
}

.feature-svg {
  width: 32px;
  height: 32px;
  color: #ffffff;
  filter: drop-shadow(0 0 6px rgba(255, 255, 255, 0.3));
}

.feature-item:hover .feature-svg {
  filter: drop-shadow(0 0 8px rgba(6, 182, 212, 0.5));
}

.feature-label {
  font-size: 13px;
  color: #a1a1aa;
  letter-spacing: 0.3px;
  font-weight: 500;
}

.scroll-indicator {
  position: absolute;
  bottom: 40px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #52525b;
  font-size: 10px;
  letter-spacing: 2px;
  text-transform: uppercase;
  z-index: 10;
}

.scroll-line {
  width: 1px;
  height: 40px;
  background: linear-gradient(to bottom, #52525b, transparent);
  animation: scroll-bounce 2s ease-in-out infinite;
}

@keyframes scroll-bounce {
  0%, 100% { transform: translateY(0); opacity: 1; }
  50% { transform: translateY(10px); opacity: 0.5; }
}

@media (max-width: 640px) {
  .cta-section {
    flex-direction: column;
  }

  .features-preview {
    gap: 28px;
  }

  .scroll-indicator {
    display: none;
  }

  .feature-icon {
    width: 52px;
    height: 52px;
    border-radius: 14px;
  }

  .feature-svg {
    width: 28px;
    height: 28px;
  }

  .feature-label {
    font-size: 11px;
  }
}
</style>
