<template>
  <div class="auth-page">
    <div class="auth-card-wrapper">
      <UiCard class="auth-card" glass>
        <div class="auth-header">
          <div class="logo-box">
            <Zap :size="32" class="text-primary" />
          </div>
          <h1 class="text-2xl font-black text-main mt-4">Welcome Back</h1>
          <p class="text-sm text-muted">Sign in to manage your KRA obligations.</p>
        </div>

        <form @submit.prevent="handleLogin" class="mt-8">
          <UiInput v-model="form.email" type="email" label="Email Address" placeholder="john@company.com" required :error="errors.email" />
          <UiInput v-model="form.password" type="password" label="Password" placeholder="••••••••" required :error="errors.password" />

          <div class="flex items-center justify-between mb-6">
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" class="accent-primary" />
              <span class="text-xs text-muted font-medium">Remember me</span>
            </label>
            <NuxtLink to="/forgot-password" class="text-xs text-primary font-bold hover:underline">Forgot Password?</NuxtLink>
          </div>

          <UiButton block variant="primary" size="lg" :loading="loading" class="shadow-primary" :disabled="loading">
            Sign In
          </UiButton>
        </form>

        <div class="auth-footer mt-8 text-center">
          <p class="text-sm text-muted">
            Don't have an account? 
            <NuxtLink to="/signup" class="text-primary font-bold hover:underline">Get Started</NuxtLink>
          </p>
        </div>
      </UiCard>
    </div>
  </div>
</template>

<script setup>
import { Zap } from 'lucide-vue-next'

definePageMeta({
  layout: false
})

const { setUser } = useAuth()
const api = useApi()
const toast = useToast()
const router = useRouter()

const loading = ref(false)
const form = ref({
  email: '',
  password: ''
})

const errors = ref({})

const validate = () => {
  errors.value = {}
  if (!form.value.email.trim()) errors.value.email = 'Email is required'
  if (!form.value.password.trim()) errors.value.password = 'Password is required'
  return Object.keys(errors.value).length === 0
}

const handleLogin = async () => {
  if (!validate()) {
    toast.error('Username and password cannot be blank.')
    return
  }

  loading.value = true
  try {
    const res = await api.post('/users/login', form.value)
    const data = res.dataPayload.data
    
    if (data.mfa_required) {
      const { mfaEmail } = useAuth()
      mfaEmail.value = data.email
      toast.info('Verification code sent to your email.')
      router.push('/verify-mfa')
      return
    }

    const { user, access_token, refresh_token } = data
    setUser(user, access_token, refresh_token)
    toast.success('Welcome back, ' + user.full_name)
    router.push('/')
  } catch (err) {
    const respData = err.data || err.response?._data
    if (err.response?.status === 403) {
      toast.warning(respData?.alertifyPayload?.message || 'Please verify your account first.')
    } else if (respData?.detail && Array.isArray(respData.detail)) {
      respData.detail.forEach(e => {
        const field = e.loc[e.loc.length - 1]
        errors.value[field] = e.msg
      })
      toast.error('Invalid input provided.')
    } else {
      const backendError = respData?.alertifyPayload?.message || respData?.errorPayload?.errors
      toast.error(backendError || 'Invalid email or password')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at bottom left, #f8fafc, #e2e8f0);
  padding: 2rem;
}

.auth-card-wrapper {
  width: 100%;
  max-width: 440px;
}

.auth-card {
  padding: 3rem 2.5rem;
  border-radius: 2rem;
}

.auth-header {
  text-align: center;
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

.shadow-primary {
  box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.2);
}
</style>
