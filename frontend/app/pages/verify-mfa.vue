<template>
  <div class="auth-page">
    <div class="auth-card-wrapper">
      <UiCard class="auth-card" glass>
        <div class="auth-header text-center">
          <div class="logo-box">
            <ShieldCheck :size="32" class="text-primary" />
          </div>
          <h1 class="text-2xl font-black text-main mt-4">Security Verification</h1>
          <p class="text-sm text-muted">
            We've sent a 6-digit code to <br/>
            <strong class="text-main">{{ mfaEmail || 'your email' }}</strong>
          </p>
        </div>

        <form @submit.prevent="handleVerify" class="mt-8">
          <div class="otp-group flex justify-between gap-2 mb-8">
            <input 
              v-for="i in 6" :key="i"
              :id="'otp-' + i"
              v-model="otpDigits[i-1]"
              type="text" 
              maxlength="1" 
              class="otp-input"
              @input="handleInput($event, i-1)"
              @keydown.backspace="handleBackspace($event, i-1)"
              autocomplete="one-time-code"
            />
          </div>

          <UiButton block variant="primary" size="lg" :loading="loading" :disabled="!isComplete" class="shadow-primary">
            Verify & Continue
          </UiButton>
        </form>

        <div class="auth-footer mt-8 text-center">
          <p class="text-sm text-muted">
            Didn't receive the code? 
            <button @click="handleResend" :disabled="resendLocked" class="text-primary font-bold hover:underline disabled:opacity-50">
              {{ resendLocked ? `Resend in ${timer}s` : 'Resend Now' }}
            </button>
          </p>
          <NuxtLink to="/login" class="inline-block mt-4 text-xs text-muted font-bold hover:text-main">
            Back to Sign In
          </NuxtLink>
        </div>
      </UiCard>
    </div>
  </div>
</template>

<script setup>
import { ShieldCheck } from 'lucide-vue-next'

definePageMeta({ layout: false })

const { mfaEmail, setUser } = useAuth()
const api = useApi()
const toast = useToast()
const router = useRouter()

const loading = ref(false)
const otpDigits = ref(['', '', '', '', '', ''])
const resendLocked = ref(false)
const timer = ref(60)

const isComplete = computed(() => otpDigits.value.every(d => d !== ''))

onMounted(() => {
  if (!mfaEmail.value) {
    router.push('/login')
    return
  }
  // Focus first input
  document.getElementById('otp-1')?.focus()
})

const handleInput = (e, index) => {
  const val = e.target.value
  if (val && index < 5) {
    document.getElementById(`otp-${index + 2}`)?.focus()
  }
}

const handleBackspace = (e, index) => {
  if (!otpDigits.value[index] && index > 0) {
    document.getElementById(`otp-${index}`)?.focus()
  }
}

const handleVerify = async () => {
  loading.value = true
  const code = otpDigits.value.join('')
  try {
    const res = await api.post('/users/verify-mfa', {
      email: mfaEmail.value,
      code: code
    })
    const { user, access_token, refresh_token } = res.dataPayload.data
    setUser(user, access_token, refresh_token)
    toast.success('MFA Verified. Welcome back!')
    router.push('/')
  } catch (err) {
    toast.error('Invalid or expired code.')
    otpDigits.value = ['', '', '', '', '', '']
    document.getElementById('otp-1')?.focus()
  } finally {
    loading.value = false
  }
}

const handleResend = async () => {
  resendLocked.value = true
  try {
    toast.info('Requesting new code...')
    await api.post('/users/resend-mfa', { email: mfaEmail.value })
    toast.success('New code sent!')
    startTimer()
  } catch (err) {
    const msg = err.response?.data?.errorPayload?.errors || 'Failed to resend code'
    toast.error(msg)
    resendLocked.value = false
  }
}

const startTimer = () => {
  timer.value = 60
  const interval = setInterval(() => {
    timer.value--
    if (timer.value <= 0) {
      clearInterval(interval)
      resendLocked.value = false
    }
  }, 1000)
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at top right, #f1f5f9, #e2e8f0);
}

.auth-card-wrapper {
  width: 100%;
  max-width: 440px;
}

.auth-card {
  padding: 3rem 2.5rem;
  border-radius: 2rem;
}

.otp-input {
  width: 45px;
  height: 55px;
  text-align: center;
  font-size: 1.5rem;
  font-weight: 900;
  border: 2px solid var(--border-color);
  border-radius: 12px;
  background: white;
  transition: all 0.2s;
}

.otp-input:focus {
  border-color: var(--primary);
  outline: none;
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1);
  transform: translateY(-2px);
}

.logo-box {
  width: 60px;
  height: 60px;
  background: white;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-color);
}
</style>
