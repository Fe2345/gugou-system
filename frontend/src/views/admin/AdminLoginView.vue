<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

defineOptions({ name: 'AdminLoginView' })

const router = useRouter()
const adminId = ref('')
const adminPassword = ref('')
const showError = ref(false)

function handleLogin() {
  if (adminId.value === 'admin' && adminPassword.value === '123456') {
    router.push('/admin')
  } else {
    showError.value = true
    setTimeout(() => { showError.value = false }, 2000)
  }
}
</script>

<template>
  <div class="login-page">
    <div class="bg-glow glow-1"></div>
    <div class="bg-glow glow-2"></div>

    <div class="particles">
      <span v-for="i in 5" :key="i" class="particle" :style="{ '--i': i }"></span>
    </div>

    <div class="login-card">
      <div class="logo-wrapper">
        <svg class="logo-svg" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#00f2fe" />
              <stop offset="100%" stop-color="#7d73e6" />
            </linearGradient>
            <linearGradient id="g2" x1="100%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stop-color="#7d73e6" stop-opacity="0.8" />
              <stop offset="100%" stop-color="#00f2fe" />
            </linearGradient>
            <linearGradient id="g3" x1="50%" y1="0%" x2="50%" y2="100%">
              <stop offset="0%" stop-color="#fff" stop-opacity="0.2" />
              <stop offset="100%" stop-color="#00f2fe" stop-opacity="0.8" />
            </linearGradient>
          </defs>
          <path class="neon-path stroke1" d="M 50,10 L 85,28 L 85,72 L 50,90 L 15,72 L 15,28 Z" />
          <path class="neon-path stroke2" d="M 50,30 L 65,45 L 35,45 Z M 40,55 L 60,55 M 30,65 L 70,65 M 50,65 L 50,80 L 35,85 M 50,80 L 65,85" />
          <path class="inner-path" d="M 50,30 L 65,45 L 35,45 Z M 40,55 L 60,55 M 30,65 L 70,65" opacity="0.3" />
        </svg>
        <div class="login-title">谷购后台管理</div>
        <div class="login-subtitle">GUGOU Goods Asset</div>
      </div>

      <div v-if="showError" class="error-msg">身份验证失败，请重新检查凭据</div>

      <form @submit.prevent="handleLogin">
        <div class="input-group">
          <input v-model="adminId" type="text" placeholder="管理员工号 / UID" required />
        </div>
        <div class="input-group">
          <input v-model="adminPassword" type="password" placeholder="访问秘钥" required />
        </div>
        <button type="submit">进入系统</button>
      </form>

      <div class="links">
        <a href="#">申请权限</a>
        <a href="#">丢失秘钥?</a>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  position: fixed;
  inset: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  background: radial-gradient(circle at top left, #1e293b, #0f172a);
  overflow: hidden;
}

.bg-glow {
  position: absolute;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.15;
}

.glow-1 { top: 20%; left: 20%; background: #7d73e6; }
.glow-2 { bottom: 20%; right: 20%; background: #00f2fe; }

.particles {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

.particle {
  position: absolute;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  animation: rise linear infinite;
}

.particle:nth-child(1) { width: 2px; height: 2px; top: 10%; left: 15%; animation-duration: 6s; animation-delay: 0s; }
.particle:nth-child(2) { width: 3px; height: 3px; top: 30%; left: 70%; animation-duration: 8s; animation-delay: 1s; }
.particle:nth-child(3) { width: 1.5px; height: 1.5px; top: 50%; left: 80%; animation-duration: 5s; animation-delay: 2.5s; }
.particle:nth-child(4) { width: 2.5px; height: 2.5px; top: 70%; left: 30%; animation-duration: 7s; animation-delay: 4s; }
.particle:nth-child(5) { width: 2px; height: 2px; top: 90%; left: 95%; animation-duration: 6.5s; animation-delay: 0.5s; }

@keyframes rise {
  0% { transform: translateY(100%) rotate(0deg); opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { transform: translateY(-100vh) rotate(360deg); opacity: 0; }
}

.login-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 40px 40px 50px;
  width: 400px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 10;
}

.logo-wrapper {
  margin-bottom: 30px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.logo-svg {
  width: 90px;
  height: 90px;
  margin-bottom: 10px;
  filter: drop-shadow(0 0 10px rgba(125, 115, 230, 0.5));
  animation: pulse 5s ease-in-out infinite;
}

.neon-path {
  fill: none;
  stroke-width: 1.5;
  stroke-linecap: round;
  stroke-linejoin: round;
  filter: drop-shadow(0 0 3px #00f2fe);
}

.stroke1 { stroke: url(#g1); }
.stroke2 { stroke: url(#g2); }
.inner-path { fill: url(#g3); }

@keyframes pulse {
  0%, 100% { transform: scale(1); filter: drop-shadow(0 0 10px rgba(125, 115, 230, 0.5)); }
  50% { transform: scale(1.05); filter: drop-shadow(0 0 20px rgba(0, 242, 254, 0.8)); }
}

.login-title {
  font-weight: 700;
  font-size: 24px;
  margin-bottom: 5px;
  background: linear-gradient(to right, #fff, #00f2fe);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  color: #fff;
}

.login-subtitle {
  font-size: 12px;
  color: #94a3b8;
  letter-spacing: 2px;
  text-transform: uppercase;
}

.input-group {
  position: relative;
  margin-bottom: 20px;
  width: 100%;
}

input {
  width: 100%;
  padding: 14px 16px;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: #fff;
  font-size: 14px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font: inherit;
}

input:focus {
  outline: none;
  border-color: #7d73e6;
  background: rgba(0, 0, 0, 0.3);
  box-shadow: 0 0 15px rgba(125, 115, 230, 0.3);
  transform: translateY(-1px);
}

button[type="submit"] {
  width: 100%;
  background: linear-gradient(135deg, #7d73e6, #6366f1);
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  border: none;
  border-radius: 12px;
  padding: 14px;
  cursor: pointer;
  margin-top: 10px;
  transition: all 0.3s ease;
  box-shadow: 0 10px 15px -3px rgba(125, 115, 230, 0.3);
  font: inherit;
}

button[type="submit"]:hover {
  filter: brightness(1.1);
  transform: translateY(-2px);
  box-shadow: 0 15px 20px -3px rgba(125, 115, 230, 0.4);
}

.links {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
  width: 100%;
}

.links a {
  color: #94a3b8;
  text-decoration: none;
  font-size: 13px;
  transition: color 0.3s;
}

.links a:hover {
  color: #00f2fe;
}

.error-msg {
  color: #fb7185;
  font-size: 13px;
  background: rgba(251, 113, 133, 0.1);
  padding: 10px;
  border-radius: 8px;
  margin-bottom: 20px;
  width: 100%;
  border-left: 3px solid #fb7185;
  animation: shake 0.4s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}
</style>
