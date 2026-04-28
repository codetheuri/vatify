<template>
  <div class="auth-page">
    <div class="auth-card-wrapper">
      <UiCard class="auth-card" glass>
        <div class="auth-header">
          <div class="logo-box">
            <Zap :size="32" class="text-primary" />
          </div>
          <h1 class="text-2xl font-black text-main mt-4">Join Vatify</h1>
          <p class="text-sm text-muted">Automate your KRA compliance in seconds.</p>
        </div>

        <div v-if="signupSuccess" class="text-center py-8">
          <div class="w-16 h-16 bg-blue-50 text-primary rounded-2xl flex items-center justify-center mx-auto mb-6">
            <Mail :size="32" />
          </div>
          <h2 class="text-2xl font-black text-main">Check Your Email</h2>
          <p class="text-sm text-muted mt-4 leading-relaxed">
            We've sent an activation link to <br/>
            <strong class="text-main">{{ form.email }}</strong>. <br/>
            Please click the link in the email to activate your account.
          </p>
          <UiButton block variant="outline" class="mt-8" @click="signupSuccess = false; router.push('/login')">
            Back to Login
          </UiButton>
        </div>

        <form v-else @submit.prevent="handleSignup" class="mt-8">
          <div class="grid grid-cols-2 gap-4">
            <UiInput v-model="form.full_name" label="Full Name" placeholder="John Doe" required :error="errors.full_name" />
            <UiInput v-model="form.email" type="email" label="Email Address" placeholder="john@company.com" required :error="errors.email" />
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <UiInput v-model="form.phone_number" label="Mobile Number" placeholder="0712345678" required :error="errors.phone_number" />
            <UiInput v-model="form.kra_pin" label="KRA PIN" placeholder="A000000000X" required @input="form.kra_pin = $event.toUpperCase()" :error="errors.kra_pin" />
          </div>

          <UiInput v-model="form.password" type="password" label="Create Password" placeholder="••••••••" required :error="errors.password" />

          <UiButton block variant="primary" size="lg" :loading="loading" class="mt-4 shadow-primary" :disabled="loading">
            Create Account
          </UiButton>
        </form>

        <div v-if="!signupSuccess" class="auth-footer mt-8 text-center">
          <p class="text-sm text-muted">
            Already have an account? 
            <NuxtLink to="/login" class="text-primary font-bold hover:underline">Log In</NuxtLink>
          </p>
        </div>
      </UiCard>
      
      <div v-if="!signupSuccess" class="auth-security-note mt-6 flex items-center justify-center gap-2 text-[10px] text-muted uppercase tracking-widest font-bold">
        <ShieldCheck :size="14" /> Encrypted & KRA Sandbox Verified
      </div>
    </div>
  </div>
</template>

<script setup>
import { Zap, ShieldCheck, Mail } from 'lucide-vue-next'

definePageMeta({
  layout: false
})

const { setUser } = useAuth()
const api = useApi()
const toast = useToast()
const router = useRouter()

const loading = ref(false)
const signupSuccess = ref(false)
const form = ref({
  full_name: '',
  email: '',
  phone_number: '',
  kra_pin: '',
  password: ''
})

const errors = ref({})

const validate = () => {
  errors.value = {}
  if (!form.value.full_name.trim()) errors.value.full_name = 'Name is required'
  if (!form.value.email.trim()) errors.value.email = 'Email is required'
  if (!form.value.kra_pin.trim()) errors.value.kra_pin = 'KRA PIN is required'
  if (form.value.kra_pin.length !== 11) errors.value.kra_pin = 'PIN must be 11 characters'
  if (form.value.password.length < 6) errors.value.password = 'Password too short (min 6 chars)'
  
  return Object.keys(errors.value).length === 0
}

const handleSignup = async () => {
  if (!validate()) {
    toast.error('Please fix the errors before submitting.')
    return
  }

  loading.value = true
  try {
    const res = await api.post('/users/signup', form.value)
    signupSuccess.value = true
    toast.success('Account created! Verification email sent.')
  } catch (err) {
    const data = err.response?.data
    if (data?.detail && Array.isArray(data.detail)) {
      // Pydantic validation errors
      data.detail.forEach(e => {
        const field = e.loc[e.loc.length - 1]
        errors.value[field] = e.msg
      })
      toast.error('Validation failed. Please check the fields.')
    } else {
      const respData = err.data || err.response?._data
      const backendError = respData?.alertifyPayload?.message || respData?.errorPayload?.errors
      toast.error(backendError || 'Signup failed. Please check your details.')
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
  background: radial-gradient(circle at top right, #f8fafc, #e2e8f0);
  padding: 2rem;
}

.auth-card-wrapper {
  width: 100%;
  max-width: 500px;
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
