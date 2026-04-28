<template>
  <div class="auth-page">
    <div class="auth-card-wrapper">
      <UiCard class="auth-card" glass>
        <div class="auth-header">
          <div class="logo-box">
            <KeyRound :size="32" class="text-primary" />
          </div>
          <h1 class="text-2xl font-black text-main mt-4">Forgot Password?</h1>
          <p class="text-sm text-muted">No worries, we'll send you reset instructions.</p>
        </div>

        <form @submit.prevent="handleForgot" class="mt-8" v-if="!submitted">
          <UiInput v-model="email" type="email" label="Email Address" placeholder="john@company.com" required />

          <UiButton block variant="primary" size="lg" :loading="loading" class="mt-4 shadow-primary">
            Send Reset Link
          </UiButton>
        </form>

        <div v-else class="mt-8 text-center animate-in fade-in slide-in-from-bottom-4 duration-700">
          <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-50 text-green-600 mb-4">
            <MailCheck :size="32" />
          </div>
          <h2 class="text-xl font-bold text-main">Check your email</h2>
          <p class="text-sm text-muted mt-2">
            We've sent a password reset link to <br/>
            <strong class="text-main">{{ email }}</strong>
          </p>
          <UiButton block variant="secondary" size="lg" class="mt-8" @click="submitted = false">
            Try another email
          </UiButton>
        </div>

        <div class="auth-footer mt-8 text-center">
          <p class="text-sm text-muted">
            Remembered your password? 
            <NuxtLink to="/login" class="text-primary font-bold hover:underline">Back to Sign In</NuxtLink>
          </p>
        </div>
      </UiCard>
    </div>
  </div>
</template>

<script setup>
import { KeyRound, MailCheck } from 'lucide-vue-next'

definePageMeta({
  layout: false
})

const api = useApi()
const toast = useToast()

const loading = ref(false)
const submitted = ref(false)
const email = ref('')

const handleForgot = async () => {
  loading.value = true
  try {
    await api.post('/users/forgot-password', { email: email.value })
    submitted.value = true
    toast.success('Reset link sent!')
  } catch (err) {
    toast.error('Something went wrong. Please try again.')
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
  background: radial-gradient(circle at center, #f8fafc, #e2e8f0);
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
