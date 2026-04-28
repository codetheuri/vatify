<template>
  <div class="auth-page">
    <div class="auth-card-wrapper">
      <UiCard class="auth-card" glass>
        <div class="auth-header text-center">
          <div class="logo-box">
            <CheckCircle v-if="success" :size="32" class="text-green-500" />
            <XCircle v-else-if="error" :size="32" class="text-red-500" />
            <Loader2 v-else :size="32" class="text-primary animate-spin" />
          </div>
          
          <h1 class="text-2xl font-black text-main mt-4">
            {{ statusTitle }}
          </h1>
          <p class="text-sm text-muted mt-2">
            {{ statusMessage }}
          </p>
        </div>

        <div class="mt-8 text-center">
          <UiButton v-if="success" block variant="primary" size="lg" to="/login" class="shadow-primary">
            Sign In Now
          </UiButton>
          <UiButton v-else-if="error" block variant="outline" size="lg" to="/signup">
            Try Signing Up Again
          </UiButton>
          <p v-else class="text-xs text-muted font-bold uppercase tracking-widest">
            Verifying your security token...
          </p>
        </div>

        <div class="auth-footer mt-8 text-center">
          <NuxtLink to="/login" class="text-xs text-muted font-bold hover:text-main">
            Back to Home
          </NuxtLink>
        </div>
      </UiCard>
    </div>
  </div>
</template>

<script setup>
import { CheckCircle, XCircle, Loader2 } from 'lucide-vue-next'

definePageMeta({ layout: false })

const route = useRoute()
const api = useApi()
const toast = useToast()

const success = ref(false)
const error = ref(false)
const loading = ref(true)

const statusTitle = computed(() => {
  if (success.value) return 'Account Activated!'
  if (error.value) return 'Verification Failed'
  return 'Verifying Account'
})

const backendMessage = ref('')

const statusMessage = computed(() => {
  if (backendMessage.value) return backendMessage.value
  if (success.value) return 'Your email has been verified. You can now access all Vatify features.'
  if (error.value) return 'The activation link is invalid or has expired. Please try signing up again.'
  return 'Please wait while we confirm your email address.'
})

const verify = async () => {
  const token = route.query.token
  if (!token) {
    error.value = true
    loading.value = false
    return
  }

  try {
    const res = await api.post('/users/verify-account', { token })
    success.value = true
    backendMessage.value = res.alertifyPayload?.message
    toast.success(backendMessage.value || 'Account verified successfully!')
  } catch (err) {
    error.value = true
    const respData = err.data || err.response?._data
    backendMessage.value = respData?.alertifyPayload?.message || respData?.errorPayload?.errors
    toast.error(backendMessage.value || 'Invalid or expired token.')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  verify()
})
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: radial-gradient(circle at center, #f8fafc, #e2e8f0);
}

.auth-card-wrapper {
  width: 100%;
  max-width: 400px;
}

.auth-card {
  padding: 3rem 2rem;
  border-radius: 2rem;
}

.logo-box {
  width: 64px;
  height: 64px;
  background: white;
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  box-shadow: var(--shadow-md);
}
</style>
