<template>
  <div class="auth-page">
    <div class="auth-card-wrapper">
      <UiCard class="auth-card" glass>
        <div class="auth-header">
          <div class="logo-box">
            <LockKeyhole :size="32" class="text-primary" />
          </div>
          <h1 class="text-2xl font-black text-main mt-4">Reset Password</h1>
          <p class="text-sm text-muted">Almost there. Set your new password below.</p>
        </div>

        <form @submit.prevent="handleReset" class="mt-8">
          <UiInput v-model="form.password" type="password" label="New Password" placeholder="••••••••" required />
          <UiInput v-model="confirm_password" type="password" label="Confirm Password" placeholder="••••••••" required />

          <UiButton block variant="primary" size="lg" :loading="loading" class="mt-4 shadow-primary">
            Update Password
          </UiButton>
        </form>

        <div class="auth-footer mt-8 text-center" v-if="!loading">
          <p class="text-xs text-muted">
            Changed your mind? <NuxtLink to="/login" class="text-primary font-bold hover:underline">Cancel</NuxtLink>
          </p>
        </div>
      </UiCard>
    </div>
  </div>
</template>

<script setup>
import { LockKeyhole } from 'lucide-vue-next'

definePageMeta({
  layout: false
})

const route = useRoute()
const router = useRouter()
const api = useApi()
const toast = useToast()

const loading = ref(false)
const token = computed(() => route.query.token)

const form = ref({
  password: '',
  token: ''
})
const confirm_password = ref('')

onMounted(() => {
  if (!token.value) {
    toast.error('Invalid password reset link.')
    router.push('/login')
  } else {
    form.value.token = token.value
  }
})

const handleReset = async () => {
  if (form.value.password !== confirm_password.value) {
    return toast.error('Passwords do not match')
  }
  
  loading.value = true
  try {
    await api.post('/users/reset-password', form.value)
    toast.success('Password updated! Please login.')
    router.push('/login')
  } catch (err) {
    toast.error(err.response?.data?.alertifyPayload?.message || 'Failed to reset password.')
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
  background: radial-gradient(circle at bottom center, #f8fafc, #e2e8f0);
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
